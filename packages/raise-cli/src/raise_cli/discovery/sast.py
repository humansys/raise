"""SAST wrapper for drift detection infrastructure (S2162.5).

Wraps the Semgrep CLI as a subprocess. Parses its --json output into typed
Pydantic models. Applies an agentic-author prior via `git log` on each finding's
source file. Persists results as a JSON snapshot under .raise/drift/sast/.

ADR-E2162-3: Wrap, don't embed — Semgrep CLI invoked as subprocess, JSON output
parsed into Pydantic models. No Semgrep Python API, no LLM, no numpy.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import time
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal, cast

from pydantic import BaseModel, Field

from raise_cli.discovery.temporal import module_id_to_slug

# ---------------------------------------------------------------------------
# Severity ordering
# ---------------------------------------------------------------------------

Severity = Literal["INFO", "WARNING", "ERROR"]
BackendStatus = Literal["ok", "semgrep_not_found", "semgrep_error"]

_SEVERITY_ORDER: dict[str, int] = {
    "INFO": 0,
    "WARNING": 1,
    "ERROR": 2,
}

# ---------------------------------------------------------------------------
# Config + Result models
# ---------------------------------------------------------------------------


class SASTConfig(BaseModel):
    """Configuration for Semgrep SAST scan."""

    ruleset: str = "auto"
    min_severity: str = "WARNING"
    agentic_prior_multiplier: float = Field(default=2.0, ge=0.0)
    agentic_author_patterns: list[str] = Field(
        default_factory=lambda: ["claude", "rai", "bot"]
    )
    cache_dir: Path = Path(".raise/drift/sast")


class SASTFinding(BaseModel):
    """One SAST finding from Semgrep output."""

    cwe: str | None  # e.g. "CWE-089" or None
    severity: Severity  # "INFO" | "WARNING" | "ERROR"
    file: str  # repo-relative path string
    line: int
    rule_id: str  # e.g. "python.lang.security.audit.sqli"
    agent_authored_prior: float = Field(default=0.2, ge=0.0, le=1.0)


class SASTResult(BaseModel):
    """Result of a SAST scan run. Schema v1 additive-only."""

    schema_version: int = Field(default=1)
    paths: list[Path]
    findings: list[SASTFinding]
    scan_time_s: float
    backend_status: BackendStatus  # "ok" | "semgrep_not_found" | "semgrep_error"
    ruleset: str
    computed_at: str


# ---------------------------------------------------------------------------
# Semgrep helpers
# ---------------------------------------------------------------------------

_DEFAULT_PRIOR: float = 0.2


def _extract_cwe(metadata: dict[str, Any]) -> str | None:
    """Extract CWE identifier from Semgrep metadata dict.

    Handles:
    - list: ["CWE-089: SQL Injection"] → "CWE-089"
    - bare string: "CWE-078: OS Command Injection" → "CWE-078"
    - absent or empty → None
    """
    cwe_raw = metadata.get("cwe")
    if not cwe_raw:
        return None

    # Normalise list to first element
    if isinstance(cwe_raw, list):
        cwe_str = str(cast("object", cwe_raw[0]))
    else:
        cwe_str = str(cast("object", cwe_raw))

    # Extract identifier before ":"
    return cwe_str.split(":")[0].strip() or None


def _parse_semgrep_output(raw: dict[str, Any], min_severity: str) -> list[SASTFinding]:
    """Parse Semgrep JSON output into a filtered list of SASTFinding.

    Findings with severity below min_severity are excluded.
    Unknown severity values are treated as ERROR (highest) to avoid silent drops.
    """
    min_level = _SEVERITY_ORDER.get(min_severity, 0)
    findings: list[SASTFinding] = []

    for item in raw.get("results", []):
        extra = item.get("extra", {})
        severity_str: str = str(extra.get("severity", "INFO")).upper()

        # Normalise unknown severities to ERROR (conservative: don't drop)
        if severity_str not in _SEVERITY_ORDER:
            severity_str = "ERROR"

        # severity_str is now guaranteed to be a valid Severity literal
        severity: Severity = cast("Severity", severity_str)

        if _SEVERITY_ORDER[severity] < min_level:
            continue

        metadata: dict[str, Any] = extra.get("metadata", {})
        cwe = _extract_cwe(metadata)

        findings.append(
            SASTFinding(
                cwe=cwe,
                severity=severity,
                file=item.get("path", ""),
                line=item.get("start", {}).get("line", 0),
                rule_id=item.get("check_id", ""),
                agent_authored_prior=_DEFAULT_PRIOR,
            )
        )

    return findings


# ---------------------------------------------------------------------------
# Agentic prior helpers (PAT-E-709: named helper for clean patching)
# ---------------------------------------------------------------------------


def _get_last_author_email(file_path: str) -> str | None:
    """Return the author email of the last commit touching file_path.

    Returns None on any git error (new file, not in repo, git not found, etc.).
    PAT-E-709: isolated method so tests can patch at the call site.
    """
    try:
        result = subprocess.run(
            ["git", "log", "--follow", "-1", "--format=%ae", "--", file_path],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip() or None
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        return None


def _apply_agentic_prior(
    email: str | None,
    cfg: SASTConfig,
) -> float:
    """Compute agent_authored_prior given a commit author email.

    Pure function — no I/O. I/O (git log) belongs in run_sast.

    Returns elevated prior if email matches any agentic pattern, else baseline.
    """
    if email is None:
        return _DEFAULT_PRIOR

    email_lower = email.lower()
    for pattern in cfg.agentic_author_patterns:
        if pattern.lower() in email_lower:
            return min(_DEFAULT_PRIOR * cfg.agentic_prior_multiplier, 1.0)

    return _DEFAULT_PRIOR


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def run_sast(paths: Sequence[Path], cfg: SASTConfig) -> SASTResult:
    """Run Semgrep on the given paths and return a SASTResult.

    Gracefully degrades when semgrep is not on PATH (backend_status="semgrep_not_found").
    Handles semgrep subprocess failure (backend_status="semgrep_error").

    Network note: cfg.ruleset="auto" requires network access. For air-gapped
    environments set cfg.ruleset to a local config path (e.g. "p/python" bundled
    or a local .semgrep.yaml).

    Writes a snapshot JSON to cfg.cache_dir / <slug>.json after every run,
    including degraded runs.

    Args:
        paths: Directories or files to scan.
        cfg:   SASTConfig (ruleset, severity filter, agentic prior, cache dir).
    """
    cfg.cache_dir.mkdir(parents=True, exist_ok=True)
    start = time.monotonic()
    computed_at = datetime.now(UTC).isoformat()

    # Derive snapshot slug from first path (consistent with clone.py pattern)
    primary_path = paths[0] if paths else Path(".")
    slug = module_id_to_slug(str(primary_path.resolve()))
    snapshot_path = cfg.cache_dir / f"{slug}.json"

    def _write_snapshot(result: SASTResult) -> None:
        snapshot_path.write_text(result.model_dump_json(), encoding="utf-8")

    # Graceful degradation: semgrep not on PATH
    if not shutil.which("semgrep"):
        elapsed = time.monotonic() - start
        result = SASTResult(
            paths=list(paths),
            findings=[],
            scan_time_s=elapsed,
            backend_status="semgrep_not_found",
            ruleset=cfg.ruleset,
            computed_at=computed_at,
        )
        _write_snapshot(result)
        return result

    # Build semgrep command
    cmd = ["semgrep", "--config", cfg.ruleset, "--json"] + [str(p) for p in paths]

    proc = subprocess.run(cmd, capture_output=True, text=True)

    elapsed = time.monotonic() - start

    # Non-zero exit → semgrep error (network failure, invalid config, etc.)
    if proc.returncode != 0:
        result = SASTResult(
            paths=list(paths),
            findings=[],
            scan_time_s=elapsed,
            backend_status="semgrep_error",
            ruleset=cfg.ruleset,
            computed_at=computed_at,
        )
        _write_snapshot(result)
        return result

    # Parse output
    try:
        raw: dict[str, Any] = json.loads(proc.stdout)
    except (json.JSONDecodeError, ValueError):
        result = SASTResult(
            paths=list(paths),
            findings=[],
            scan_time_s=elapsed,
            backend_status="semgrep_error",
            ruleset=cfg.ruleset,
            computed_at=computed_at,
        )
        _write_snapshot(result)
        return result

    findings = _parse_semgrep_output(raw, cfg.min_severity)

    # Apply agentic prior: one git log call per unique file (PAT-E-709)
    unique_files = {f.file for f in findings}
    author_cache: dict[str, str | None] = {
        file_path: _get_last_author_email(file_path) for file_path in unique_files
    }

    findings = [
        f.model_copy(
            update={
                "agent_authored_prior": _apply_agentic_prior(
                    author_cache.get(f.file), cfg
                )
            }
        )
        for f in findings
    ]

    # Deterministic order: file + line
    findings.sort(key=lambda f: (f.file, f.line))

    result = SASTResult(
        paths=list(paths),
        findings=findings,
        scan_time_s=elapsed,
        backend_status="ok",
        ruleset=cfg.ruleset,
        computed_at=computed_at,
    )
    _write_snapshot(result)
    return result
