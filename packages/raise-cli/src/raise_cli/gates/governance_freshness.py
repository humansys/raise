"""GovernanceFreshnessGate — advisory staleness check for governance docs (RAISE-16251).

Read-only, LLM-free, no network. For each of ``governance/prd.md``,
``governance/vision.md``, and ``governance/guardrails.md`` present in the
repo, resolves the doc's last-modified timestamp (Git history first, file
mtime as fallback) and compares its age against a configurable threshold.

**This gate never blocks.** ``passed`` is always ``True`` — staleness
surfaces only via ``advisory=True`` plus per-doc detail lines (mirrors the
advisory shape already established by
``gates.governance.workflow_transition_ownership_gate`` and
``gates.drift._base``). A story or epic close must not be bricked by a
governance doc nobody has touched in a while; the point is visibility, not
enforcement.

Threshold resolution order: ``RAISE_GOVERNANCE_FRESHNESS_DAYS`` env var (if
set and a valid integer) -> ``governance.freshness_days`` in
``.raise/manifest.yaml`` (if present and readable) -> default of 90 days.
Any failure at a given step (invalid env value, missing/malformed manifest)
falls through to the next step rather than raising — the gate is fail-open
at every layer, per-doc and per-config-source alike.

Architecture: ADR-039 (WorkflowGate Protocol).
"""

from __future__ import annotations

import logging
import os
import subprocess
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import ClassVar

import yaml

from raise_cli.gates.models import GateContext, GateResult

logger = logging.getLogger(__name__)

_GOVERNANCE_DOCS: tuple[Path, ...] = (
    Path("governance") / "prd.md",
    Path("governance") / "vision.md",
    Path("governance") / "guardrails.md",
)
_ENV_KEY = "RAISE_GOVERNANCE_FRESHNESS_DAYS"
_DEFAULT_THRESHOLD_DAYS = 90
_MANIFEST_RELPATH = Path(".raise") / "manifest.yaml"
_SECONDS_PER_DAY = 86400.0


def _now() -> float:
    """Wall-clock time — a test seam so tests can pin the clock."""
    return time.time()


def _threshold_days(working_dir: Path) -> int:
    """Resolve the freshness threshold: env -> manifest -> default.

    An invalid env value (not parseable as int) is ignored, not fatal — the
    resolution simply falls through to the manifest, then the default.
    """
    env_val = os.environ.get(_ENV_KEY)
    if env_val is not None:
        try:
            return int(env_val)
        except ValueError:
            logger.debug(
                "governance-freshness: invalid %s=%r — ignoring", _ENV_KEY, env_val
            )

    manifest_path = working_dir / _MANIFEST_RELPATH
    if manifest_path.is_file():
        try:
            data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
        except (OSError, yaml.YAMLError) as exc:
            logger.debug("governance-freshness: manifest unreadable — %s", exc)
            data = None
        if isinstance(data, dict):
            governance = data.get("governance")
            if isinstance(governance, dict):
                value = governance.get("freshness_days")
                if isinstance(value, int) and not isinstance(value, bool):
                    return value

    return _DEFAULT_THRESHOLD_DAYS


def _last_modified_ts(working_dir: Path, rel: Path) -> float | None:
    """Resolve a doc's last-modified epoch timestamp.

    Tries ``git log -1 --format=%ct`` first (the true last-commit time,
    robust to checkouts/clones that reset mtime), falling back to the file's
    mtime when Git has no history for the path (or the working dir is not a
    repo at all). Returns ``None`` only when the file itself is absent.
    """
    abs_path = working_dir / rel
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%ct", "--", str(rel)],
            cwd=working_dir,
            capture_output=True,
            check=False,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        logger.debug("governance-freshness: git log failed for %s — %s", rel, exc)
        result = None

    if result is not None and result.returncode == 0:
        output = result.stdout.strip()
        if output:
            try:
                return float(int(output))
            except ValueError:
                logger.debug(
                    "governance-freshness: unparseable git log output for %s: %r",
                    rel,
                    output,
                )

    try:
        return abs_path.stat().st_mtime
    except OSError:
        return None


class GovernanceFreshnessGate:
    """Advisory gate: governance docs were revised within a freshness threshold.

    Registered via the ``rai.gates`` entry point. Never returns
    ``passed=False`` — staleness is surfaced via ``advisory=True``.
    """

    gate_id: ClassVar[str] = "gate-governance-freshness"
    description: ClassVar[str] = "Governance docs revised within freshness threshold"
    workflow_point: ClassVar[str] = "before:story:close"

    def evaluate(self, context: GateContext) -> GateResult:
        """Check each governance doc's age against the resolved threshold."""
        working_dir = context.working_dir
        threshold = _threshold_days(working_dir)
        now = _now()

        checked: list[tuple[Path, float, float]] = []
        for rel in _GOVERNANCE_DOCS:
            abs_path = working_dir / rel
            if not abs_path.is_file():
                continue
            ts = _last_modified_ts(working_dir, rel)
            if ts is None:
                continue
            age_days = (now - ts) / _SECONDS_PER_DAY
            checked.append((rel, ts, age_days))

        if not checked:
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message="no governance docs found — skipped",
                skipped=True,
            )

        stale = [entry for entry in checked if entry[2] > threshold]

        if not stale:
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message=f"{len(checked)} governance doc(s) fresh (threshold {threshold}d)",
            )

        details: list[str] = []
        for rel, ts, age_days in stale:
            last_modified = datetime.fromtimestamp(ts, tz=UTC).strftime("%Y-%m-%d")
            line = (
                f"{rel.as_posix()} — last modified {last_modified} "
                f"({int(age_days)}d ago, threshold {threshold}d)"
            )
            details.append(line)
            logger.warning("governance-freshness: %s", line)

        details.append(
            "Review and refresh stale governance docs, or adjust "
            f"{_ENV_KEY} if the threshold no longer fits."
        )

        return GateResult(
            passed=True,
            gate_id=self.gate_id,
            message=(
                f"{len(stale)} governance doc(s) stale (advisory, "
                f"threshold {threshold}d)"
            ),
            details=tuple(details),
            advisory=True,
        )


class EpicGovernanceFreshnessGate(GovernanceFreshnessGate):
    """Epic-close variant of ``GovernanceFreshnessGate``.

    Same evaluation logic (inherited), different workflow point and
    identifier so it can be registered and reported independently.
    """

    gate_id: ClassVar[str] = "gate-epic-governance-freshness"
    workflow_point: ClassVar[str] = "before:epic:close"
