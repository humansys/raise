"""Self-hosted threshold calibration from a healthy module subset (S2161.1 · T2).

Derives per-signal P95 thresholds by running the drift-check orchestrator in a
never-warn configuration over each healthy module and taking the 95th percentile
of each metric. The resulting :class:`DriftCheckConfig` is used to score the full
corpus in Pass 1 (DR-003 §9 — thresholds self-hosted from healthy subset, not
library defaults).

Scales O(N · detector_cost): the internal pass runs the full I2–I5 stack once
per healthy reference.
"""

from __future__ import annotations

import statistics
from pathlib import Path
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

from raise_cli.discovery.check import DriftCheckConfig, run_drift_check

if TYPE_CHECKING:
    from raise_cli.discovery.check import DriftCheckReport

__all__ = [
    "CalibrationReport",
    "HealthyModuleRef",
    "calibrate_thresholds",
]


# ---------------------------------------------------------------------------
# Public models
# ---------------------------------------------------------------------------


class HealthyModuleRef(BaseModel):
    """Reference to a module rated healthy in the ground-truth corpus (E2099)."""

    module_id: str
    path: Path


class CalibrationReport(BaseModel):
    """Trace of a calibration run — n, quantile, per-metric thresholds, excluded modules.

    ``excluded_metrics`` names signals whose healthy-subset distribution is too
    degenerate (e.g. all values near zero) to support a meaningful threshold.
    Consumers should treat these signals as ``unavailable`` rather than apply
    the neutralized threshold (which is forced to a sentinel).
    """

    healthy_n: int
    quantile: float
    thresholds: dict[str, float] = Field(default_factory=lambda: {})
    excluded: list[str] = Field(default_factory=lambda: [])
    excluded_metrics: list[str] = Field(default_factory=lambda: [])


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def calibrate_thresholds(
    healthy_refs: list[HealthyModuleRef],
    repo_root: Path,
    quantile: float = 0.95,
) -> tuple[DriftCheckConfig, CalibrationReport]:
    """Run the drift detectors over each healthy module and derive P-quantile thresholds.

    Args:
        healthy_refs: Modules rated healthy in the ground-truth corpus.
        repo_root:    Repo root for downstream resolution (reserved — currently unused).
        quantile:     Target quantile (default 0.95 = P95 per DR-003 §9).

    Returns:
        Tuple of (calibrated :class:`DriftCheckConfig`, :class:`CalibrationReport`).

    Notes:
        Comparison-operator semantics matter. Strict ``>`` signals (wmc, fan_out,
        loc_slope) use the raw quantile value. Inclusive ``>=`` signals (clones,
        sast, hist) use ``quantile_value + 1`` to preserve "first problematic
        count" semantics — otherwise a healthy module that defined the P95 would
        trip a WARN when re-checked against its own calibration.
    """
    _ = repo_root  # reserved for future resolution

    if not healthy_refs:
        return DriftCheckConfig(), CalibrationReport(
            healthy_n=0, quantile=quantile, thresholds={}, excluded=[]
        )

    never_warn = _never_warn_config()
    reports: list[DriftCheckReport] = []
    excluded: list[str] = []

    for ref in healthy_refs:
        if not ref.path.exists():
            excluded.append(ref.module_id)
            continue
        try:
            reports.append(run_drift_check(ref.path, never_warn))
        except (FileNotFoundError, OSError):
            excluded.append(ref.module_id)

    wmc_values = [
        float(r.metrics_report.wmc) for r in reports if r.metrics_report is not None
    ]
    fan_out_values = [
        float(r.metrics_report.fan_out) for r in reports if r.metrics_report is not None
    ]
    loc_slope_values = [
        float(r.temporal_report.loc_slope)
        for r in reports
        if r.temporal_report is not None
    ]
    hist_max_values = [
        float(max((c for _, c in r.temporal_report.co_change_partners), default=0))
        for r in reports
        if r.temporal_report is not None
    ]
    clone_values = [
        float(len(r.clone_report.clones)) for r in reports if r.clone_report is not None
    ]
    sast_values = [
        float(len(r.sast_result.findings))
        for r in reports
        if r.sast_result is not None and r.sast_result.backend_status == "ok"
    ]

    defaults = DriftCheckConfig()
    thresholds: dict[str, float] = {}

    wmc_warn = _resolve_int(
        wmc_values, quantile, defaults.wmc_warn, thresholds, "wmc_warn"
    )
    fan_out_warn = _resolve_int(
        fan_out_values, quantile, defaults.fan_out_warn, thresholds, "fan_out_warn"
    )
    loc_slope_warn = _resolve_float(
        loc_slope_values,
        quantile,
        defaults.loc_slope_warn,
        thresholds,
        "loc_slope_warn",
    )
    clone_warn = _resolve_int(
        clone_values,
        quantile,
        defaults.clone_warn,
        thresholds,
        "clone_warn",
        inclusive_offset=1,
    )
    sast_warn = _resolve_int(
        sast_values,
        quantile,
        defaults.sast_warn,
        thresholds,
        "sast_warn",
        inclusive_offset=1,
    )
    hist_support_warn = _resolve_int(
        hist_max_values,
        quantile,
        defaults.hist_support_warn,
        thresholds,
        "hist_support_warn",
        inclusive_offset=1,
    )

    # Degenerate-variance guard (DR-003 §9 — self-hosted must also recognize
    # when healthy data is too quiescent to define a meaningful threshold).
    # loc_slope on a subset of static modules collapses to ~zero, which would
    # warn on any movement. Neutralize the threshold and flag the metric so
    # downstream consumers render it as ``unavailable``.
    excluded_metrics: list[str] = []
    if loc_slope_values and max(loc_slope_values) < _DEGENERATE_SLOPE:
        excluded_metrics.append("loc_slope")
        loc_slope_warn = float(_CEIL)
        thresholds["loc_slope_warn"] = loc_slope_warn

    cfg = DriftCheckConfig(
        wmc_warn=wmc_warn,
        fan_out_warn=fan_out_warn,
        loc_slope_warn=loc_slope_warn,
        clone_warn=clone_warn,
        sast_warn=sast_warn,
        hist_support_warn=hist_support_warn,
    )
    report = CalibrationReport(
        healthy_n=len(reports),
        quantile=quantile,
        thresholds=thresholds,
        excluded=excluded,
        excluded_metrics=excluded_metrics,
    )
    return cfg, report


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


_CEIL = 10**9

# LOC slope below this magnitude (lines/commit) indicates a healthy subset too
# quiescent to define a meaningful P95 threshold for temporal growth.
_DEGENERATE_SLOPE = 0.01


def _never_warn_config() -> DriftCheckConfig:
    """Return a config whose thresholds are far above any plausible metric.

    Used during calibration so the internal per-module ``run_drift_check`` invocations
    never emit WARN (we only need the numeric sub-reports, not the signals).
    """
    return DriftCheckConfig(
        wmc_warn=_CEIL,
        fan_out_warn=_CEIL,
        clone_warn=_CEIL,
        sast_warn=_CEIL,
        loc_slope_warn=float(_CEIL),
        hist_support_warn=_CEIL,
    )


def _p_quantile(values: list[float], quantile: float) -> float:
    """Compute the P-quantile using ``statistics.quantiles`` (inclusive method).

    Edge cases:
      - ``len(values) == 0`` → raises ``ValueError`` (caller handles).
      - ``len(values) == 1`` → returns the single value.
    """
    if len(values) == 1:
        return values[0]
    idx = max(0, min(98, int(round(quantile * 100)) - 1))
    return statistics.quantiles(values, n=100, method="inclusive")[idx]


def _resolve_int(
    values: list[float],
    quantile: float,
    default: int,
    thresholds: dict[str, float],
    key: str,
    *,
    inclusive_offset: int = 0,
) -> int:
    if not values:
        return default
    raw = _p_quantile(values, quantile)
    result = int(round(raw)) + inclusive_offset
    thresholds[key] = float(result)
    return result


def _resolve_float(
    values: list[float],
    quantile: float,
    default: float,
    thresholds: dict[str, float],
    key: str,
) -> float:
    if not values:
        return default
    result = _p_quantile(values, quantile)
    thresholds[key] = result
    return result
