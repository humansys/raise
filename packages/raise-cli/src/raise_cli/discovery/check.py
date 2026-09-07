"""DriftCheck orchestrator — composes I2–I5 into a unified per-module report (S2162.6).

Sequential fan-in: structural metrics (I2) + temporal slope (I3) +
clone detection (I4) + SAST (I5). No LLM required. Budget: <5s warm.
"""

from __future__ import annotations

import contextlib
import json
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

from raise_cli.discovery.clone import CloneConfig, CloneReport, detect_clones
from raise_cli.discovery.sast import SASTConfig, SASTResult, run_sast
from raise_cli.discovery.temporal import TemporalConfig, TemporalReport, snapshot
from raise_cli.graph.backends import get_active_backend
from raise_core.discovery.symbols import (
    _module_id_from_file as _canonical_module_id_from_file,  # pyright: ignore[reportPrivateUsage]
)
from raise_core.graph.metrics import MetricsComputer, MetricsReport

_INDEX_FILE = "index.json"


# ---------------------------------------------------------------------------
# Public models
# ---------------------------------------------------------------------------


class DriftSignal(BaseModel):
    """A single drift signal with status and detail."""

    name: str
    status: Literal["ok", "warn", "unavailable"]
    detail: str


class DriftCheckConfig(BaseModel):
    """Configurable thresholds and paths for the drift check orchestrator."""

    wmc_warn: int = Field(default=20, description="WMC threshold for WARN")
    fan_out_warn: int = Field(default=15, description="fan_out threshold for WARN")
    clone_warn: int = Field(
        default=5,
        description="clone cluster count for WARN (interim; density-based threshold deferred to E2161)",
    )
    sast_warn: int = Field(default=1, description="SAST finding count for WARN")
    sast_ruleset: str = Field(
        default="p/bandit",
        description="Semgrep ruleset for SAST (p/bandit ~3s; auto ~40s)",
    )
    loc_slope_warn: float = Field(
        default=5.0,
        description="LOC slope threshold for WARN (lines/commit; 5.0 ≈ Fowler long-method boundary applied to growth rate)",
    )
    hist_support_warn: int = Field(
        default=5,
        description="Palomba HIST support threshold for WARN (co-change count ≥ N; DR-003 §5.1)",
    )
    cache_dir: Path = Field(
        default=Path(".raise/drift/check"),
        description="Directory for snapshot JSON files",
    )


class DriftCheckReport(BaseModel):
    """Unified drift health report for a single module."""

    module_id: str
    module_path: Path
    metrics_report: MetricsReport | None = None
    temporal_report: TemporalReport | None = None
    clone_report: CloneReport | None = None
    sast_result: SASTResult | None = None
    signals: list[DriftSignal]
    duration_s: float = 0.0
    checked_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))

    model_config = {"arbitrary_types_allowed": True}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def run_drift_check(
    module_path: Path,
    cfg: DriftCheckConfig | None = None,
    *,
    index_path: Path | None = None,
) -> DriftCheckReport:
    """Compose I2–I5 detectors and return a unified DriftCheckReport.

    Args:
        module_path:  Path to the module directory or file (repo-root-relative).
        cfg:          Thresholds and cache dir (uses defaults if None).
        index_path:   Override graph index path (default: .raise/rai/memory/index.json).

    Returns:
        DriftCheckReport with all available signals and duration.

    Raises:
        FileNotFoundError: If the graph index is absent (caller should exit 4).
    """
    if cfg is None:
        cfg = DriftCheckConfig()

    t0 = time.perf_counter()

    # I2: load graph — propagate FileNotFoundError so CLI can handle exit 4
    from raise_cli.config.paths import get_memory_dir

    resolved_index = index_path or (get_memory_dir() / _INDEX_FILE)
    graph = get_active_backend(resolved_index).load()

    module_id = _module_id_from_path(module_path)

    # I2: structural metrics
    metrics_report: MetricsReport | None = None
    with contextlib.suppress(ModuleNotFoundError):
        metrics_report = MetricsComputer(graph).compute(module_id)

    # I3: temporal slope + HIST co-change
    temporal_report: TemporalReport | None = None
    with contextlib.suppress(Exception):  # any git/IO failure → partial report
        temporal_report = snapshot(
            module_path=module_path,
            repo_root=Path("."),
            cfg=TemporalConfig(),
        )

    # I4: clone detection (always returns, backend_status carries degradation)
    clone_report: CloneReport = detect_clones(module_path, CloneConfig())

    # I5: SAST (always returns, backend_status carries degradation)
    sast_result: SASTResult = run_sast(
        paths=[module_path],
        cfg=SASTConfig(ruleset=cfg.sast_ruleset),
    )

    signals = _compute_signals(
        metrics_report=metrics_report,
        temporal_report=temporal_report,
        clone_report=clone_report,
        sast_result=sast_result,
        cfg=cfg,
    )

    duration_s = time.perf_counter() - t0

    report = DriftCheckReport(
        module_id=module_id,
        module_path=module_path,
        metrics_report=metrics_report,
        temporal_report=temporal_report,
        clone_report=clone_report,
        sast_result=sast_result,
        signals=signals,
        duration_s=duration_s,
    )

    _write_snapshot(report, cfg)
    return report


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _module_id_from_path(path: Path) -> str:
    """Derive a ``mod-*`` id from a path.

    Delegates to ``raise_core.discovery.symbols._module_id_from_file`` — the
    graph loader's single id-minting choke point (RAISE-16033) — instead of
    maintaining a second, independently-drifting heuristic. Before this fix,
    this function used its own approximation (find a ``raise_*`` segment,
    take the next one) that neither package-qualified its output nor agreed
    with the TS/JS flat-layout handling added in RAISE-16027, so a drift
    check against a TS module or a colliding module name (``mod-api`` in
    both ``raise-server`` and ``raise-partners``) could silently resolve to
    the wrong graph node — or one that no longer existed post-qualification.

    Unlike the graph loader (which legitimately omits unattributable
    top-level files by returning ``None``), every ``run_drift_check`` caller
    needs *some* id, so a ``None`` from the canonical derivation falls back
    to a filesystem slug of the last path segment — matching this
    function's pre-existing fallback shape.

    ``run_drift_check`` callers legitimately pass bare module *directories*
    (no filename) — the canonical derivation branches TS/JS vs. Python by
    file *extension*, which a bare directory string never has. Python's
    nested ``src/<pkg>/<module>/`` layout still resolves without I/O (the
    module segment sits below an extra package segment either way), but a
    TS/JS flat ``src/<module>/`` directory is indistinguishable from an
    incomplete Python path from the string alone. When the plain string
    delegation comes back empty and ``path`` is a real directory, probe one
    real file inside it and re-derive from that — the only reliable way to
    recover the missing extension.
    """
    module_id = _canonical_module_id_from_file(str(path))
    if module_id is None and path.is_dir():
        # Any traversal failure (permission, broken symlink) degrades to the
        # filesystem-slug fallback below rather than crashing the whole
        # drift check over one unreadable entry.
        with contextlib.suppress(OSError):
            for probe_file in sorted(path.rglob("*")):
                if not probe_file.is_file():
                    continue
                module_id = _canonical_module_id_from_file(str(probe_file))
                if module_id is not None:
                    break
    if module_id is not None:
        return module_id
    last = path.name or (path.parts[-1] if path.parts else "unknown")
    return f"mod-{last.rstrip('/').replace('_', '-')}"


def _compute_signals(
    *,
    metrics_report: MetricsReport | None,
    temporal_report: TemporalReport | None,
    clone_report: CloneReport | None,
    sast_result: SASTResult | None,
    cfg: DriftCheckConfig,
) -> list[DriftSignal]:
    """Derive DriftSignal list from sub-reports and thresholds."""
    signals: list[DriftSignal] = []

    # WMC
    if metrics_report is None:
        signals.append(
            DriftSignal(name="wmc", status="unavailable", detail="metrics unavailable")
        )
        signals.append(
            DriftSignal(
                name="fan_out", status="unavailable", detail="metrics unavailable"
            )
        )
    else:
        wmc_status: Literal["ok", "warn", "unavailable"] = (
            "warn" if metrics_report.wmc > cfg.wmc_warn else "ok"
        )
        signals.append(
            DriftSignal(
                name="wmc",
                status=wmc_status,
                detail=f"{metrics_report.wmc} (threshold: {cfg.wmc_warn})",
            )
        )
        fan_status: Literal["ok", "warn", "unavailable"] = (
            "warn" if metrics_report.fan_out > cfg.fan_out_warn else "ok"
        )
        signals.append(
            DriftSignal(
                name="fan_out",
                status=fan_status,
                detail=f"{metrics_report.fan_out} (threshold: {cfg.fan_out_warn})",
            )
        )

    # LOC slope
    if temporal_report is None:
        signals.append(
            DriftSignal(
                name="loc_slope", status="unavailable", detail="temporal unavailable"
            )
        )
    else:
        slope_status: Literal["ok", "warn", "unavailable"] = (
            "warn" if temporal_report.loc_slope > cfg.loc_slope_warn else "ok"
        )
        signals.append(
            DriftSignal(
                name="loc_slope",
                status=slope_status,
                detail=f"slope={temporal_report.loc_slope:.2f} (threshold: {cfg.loc_slope_warn})",
            )
        )

    # HIST (Palomba change-coupling): count partners with support >= threshold
    if temporal_report is None:
        signals.append(
            DriftSignal(
                name="hist", status="unavailable", detail="temporal unavailable"
            )
        )
    else:
        high_support = sum(
            1
            for _, count in temporal_report.co_change_partners
            if count >= cfg.hist_support_warn
        )
        hist_status: Literal["ok", "warn", "unavailable"] = (
            "warn" if high_support > 0 else "ok"
        )
        signals.append(
            DriftSignal(
                name="hist",
                status=hist_status,
                detail=f"{high_support} partners ≥ support {cfg.hist_support_warn}",
            )
        )

    # Clones
    if clone_report is None:
        signals.append(
            DriftSignal(
                name="clones",
                status="unavailable",
                detail="clone detection unavailable",
            )
        )
    else:
        clone_count = len(clone_report.clones)
        # >= because threshold is the first problematic count, not an upper bound
        clone_status: Literal["ok", "warn", "unavailable"] = (
            "warn" if clone_count >= cfg.clone_warn else "ok"
        )
        signals.append(
            DriftSignal(
                name="clones",
                status=clone_status,
                detail=f"{clone_count} clusters",
            )
        )

    # SAST
    if sast_result is None:
        signals.append(
            DriftSignal(name="sast", status="unavailable", detail="SAST unavailable")
        )
    elif sast_result.backend_status != "ok":
        signals.append(
            DriftSignal(
                name="sast",
                status="unavailable",
                detail=sast_result.backend_status,
            )
        )
    else:
        finding_count = len(sast_result.findings)
        # >= because threshold is the first problematic count, not an upper bound
        sast_status_val: Literal["ok", "warn", "unavailable"] = (
            "warn" if finding_count >= cfg.sast_warn else "ok"
        )
        signals.append(
            DriftSignal(
                name="sast",
                status=sast_status_val,
                detail=f"{finding_count} findings",
            )
        )

    return signals


def _write_snapshot(report: DriftCheckReport, cfg: DriftCheckConfig) -> None:
    """Persist report as JSON to cfg.cache_dir/<module_id>.json."""
    cfg.cache_dir.mkdir(parents=True, exist_ok=True)
    slug = report.module_id.replace("mod-", "")
    out = cfg.cache_dir / f"{slug}.json"
    out.write_text(
        json.dumps(json.loads(report.model_dump_json()), indent=2),
        encoding="utf-8",
    )
