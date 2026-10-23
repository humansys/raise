"""Clone detection wrapper for drift detection infrastructure (S2162.4).

Detects Type-1 (exact) code clones across Python source files using a
SHA-256 sliding-window hash over normalised lines. No external dependencies;
NiCad is supported as a gracefully-degraded optional backend.

ADR-E2162-2 compliant: no LLM, no numpy, stdlib-only algorithm.
"""

from __future__ import annotations

import hashlib
import shutil
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

from raise_cli.discovery.temporal import module_id_to_slug

# ---------------------------------------------------------------------------
# Type aliases (Literals)
# ---------------------------------------------------------------------------

CloneAuthorship = Literal["agent", "human", "mixed"]
BackendStatus = Literal["ok", "nicad_not_found", "error"]

# ---------------------------------------------------------------------------
# Config + Report models
# ---------------------------------------------------------------------------


class CloneConfig(BaseModel):
    """Configuration for clone detection."""

    min_lines: int = Field(default=4, ge=1)
    min_occurrences: int = Field(default=2, ge=1)
    backend: Literal["python-hash", "nicad"] = "python-hash"
    cache_dir: Path = Path(".raise/drift/clones")


class CloneFragment(BaseModel):
    """One occurrence of a cloned block."""

    file_path: str
    start_line: int
    end_line: int


class CloneCluster(BaseModel):
    """A set of identical code fragments (one logical clone)."""

    window_hash: str
    line_count: int
    fragments: list[CloneFragment]
    occurrences: int
    authorship: CloneAuthorship | None = None


class CloneReport(BaseModel):
    """Result of a clone detection run. Schema v1 additive-only."""

    schema_version: int = Field(default=1)
    source_path: str
    min_lines: int
    min_occurrences: int
    clones: list[CloneCluster]
    detection_time_s: float
    backend_used: str
    backend_status: BackendStatus
    computed_at: str


# ---------------------------------------------------------------------------
# Normalisation
# ---------------------------------------------------------------------------


def _normalise_lines(raw_lines: list[str]) -> list[tuple[int, str]]:
    """Return [(raw_1indexed_line_no, normalised_line)] skipping blanks and comments.

    Preserves leading indent. Strips trailing whitespace only.
    """
    result: list[tuple[int, str]] = []
    for i, line in enumerate(raw_lines, start=1):
        stripped = line.rstrip()
        if not stripped:
            continue
        if stripped.lstrip().startswith("#"):
            continue
        result.append((i, stripped))
    return result


# ---------------------------------------------------------------------------
# Hash backend
# ---------------------------------------------------------------------------


class _HashBackend:
    """SHA-256 sliding-window clone detector."""

    def detect(self, path: Path, cfg: CloneConfig) -> CloneReport:
        start = time.monotonic()
        py_files = sorted(path.rglob("*.py"))

        # hash → list[(file_path_str, window_start_raw, window_end_raw)]
        hash_map: dict[str, list[tuple[str, int, int]]] = {}

        for file_path in py_files:
            try:
                raw_lines = file_path.read_text(encoding="utf-8").splitlines()
            except (OSError, UnicodeDecodeError):
                continue

            normalised = _normalise_lines(raw_lines)
            n = len(normalised)

            # Store repo-relative path so segment_by_authorship prefix matching works
            relative_path = str(file_path.relative_to(path))

            for i in range(n - cfg.min_lines + 1):
                window = normalised[i : i + cfg.min_lines]
                window_text = "\n".join(line for _, line in window)
                digest = hashlib.sha256(window_text.encode()).hexdigest()

                raw_start = window[0][0]
                raw_end = window[-1][0]
                hash_map.setdefault(digest, []).append(
                    (relative_path, raw_start, raw_end)
                )

        clones: list[CloneCluster] = []
        for digest, occurrences in hash_map.items():
            if len(occurrences) < cfg.min_occurrences:
                continue

            fragments = [
                CloneFragment(file_path=fp, start_line=sl, end_line=el)
                for fp, sl, el in sorted(occurrences, key=lambda t: (t[0], t[1]))
            ]
            clones.append(
                CloneCluster(
                    window_hash=digest,
                    line_count=cfg.min_lines,
                    fragments=fragments,
                    occurrences=len(fragments),
                )
            )

        # Deterministic order: (window_hash, first_fragment_path, first_fragment_start_line)
        clones.sort(
            key=lambda c: (
                c.window_hash,
                c.fragments[0].file_path if c.fragments else "",
                c.fragments[0].start_line if c.fragments else 0,
            )
        )

        elapsed = time.monotonic() - start
        return CloneReport(
            schema_version=1,
            source_path=str(path),
            min_lines=cfg.min_lines,
            min_occurrences=cfg.min_occurrences,
            clones=clones,
            detection_time_s=elapsed,
            backend_used="python-hash",
            backend_status="ok",
            computed_at=datetime.now(UTC).isoformat(),
        )


# ---------------------------------------------------------------------------
# NiCad backend (graceful degradation)
# ---------------------------------------------------------------------------


class _NiCadBackend:
    """Thin NiCad subprocess wrapper — degrades gracefully when absent."""

    def detect(self, path: Path, cfg: CloneConfig) -> CloneReport:
        if not shutil.which("nicad"):
            return CloneReport(
                schema_version=1,
                source_path=str(path),
                min_lines=cfg.min_lines,
                min_occurrences=cfg.min_occurrences,
                clones=[],
                detection_time_s=0.0,
                backend_used="nicad",
                backend_status="nicad_not_found",
                computed_at=datetime.now(UTC).isoformat(),
            )
        raise NotImplementedError("NiCad subprocess not yet implemented")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def detect_clones(path: Path, cfg: CloneConfig) -> CloneReport:
    """Detect Type-1 clones under path and write a snapshot JSON.

    Selects backend via cfg.backend. Always creates cfg.cache_dir (safe for
    fresh repos). Snapshot path is derived from the resolved scan path.
    """
    cfg.cache_dir.mkdir(parents=True, exist_ok=True)

    backend: _HashBackend | _NiCadBackend = (
        _NiCadBackend() if cfg.backend == "nicad" else _HashBackend()
    )

    report = backend.detect(path.resolve(), cfg)

    slug = module_id_to_slug(str(path.resolve()))
    snapshot_path = cfg.cache_dir / f"{slug}.json"
    snapshot_path.write_text(report.model_dump_json(), encoding="utf-8")

    return report


def segment_by_authorship(
    report: CloneReport,
    agent_paths: list[Path],
    human_paths: list[Path],
) -> CloneReport:
    """Return a new CloneReport with authorship set on each cluster.

    Pure function — does not mutate the input report.

    Matching rule per fragment:
    - agent bucket: Path(fragment.file_path).is_relative_to(prefix) for any agent_paths prefix
    - human bucket: same for human_paths OR no match (default "human")
    - Cluster authorship: "agent" if all agent-bucket, "human" if all human-bucket, "mixed" otherwise
    """
    tagged_clusters: list[CloneCluster] = []

    for cluster in report.clones:
        buckets: list[str] = []
        for fragment in cluster.fragments:
            fpath = Path(fragment.file_path)
            if any(fpath.is_relative_to(prefix) for prefix in agent_paths):
                buckets.append("agent")
            elif any(fpath.is_relative_to(prefix) for prefix in human_paths):
                buckets.append("human")
            else:
                buckets.append("human")

        if all(b == "agent" for b in buckets):
            authorship: CloneAuthorship = "agent"
        elif all(b == "human" for b in buckets):
            authorship = "human"
        else:
            authorship = "mixed"

        tagged_clusters.append(
            CloneCluster(
                window_hash=cluster.window_hash,
                line_count=cluster.line_count,
                fragments=cluster.fragments,
                occurrences=cluster.occurrences,
                authorship=authorship,
            )
        )

    return CloneReport(
        schema_version=report.schema_version,
        source_path=report.source_path,
        min_lines=report.min_lines,
        min_occurrences=report.min_occurrences,
        clones=tagged_clusters,
        detection_time_s=report.detection_time_s,
        backend_used=report.backend_used,
        backend_status=report.backend_status,
        computed_at=report.computed_at,
    )
