"""Drift metric time-series store — baseline, report, and dashboard data (S2100.3).

Append-only JSONL store at .raise/rai/memory/drift-metric.jsonl.
Two record types: DriftBaselineRecord (P75/P90 thresholds) and
DriftReportRecord (per-story delta snapshot).
"""

from __future__ import annotations

import contextlib
import json
import statistics
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Annotated, Literal

from pydantic import BaseModel, Field

from raise_cli.discovery.check import DriftCheckConfig, run_drift_check
from raise_core.discovery.symbols import qualified_module_id

if TYPE_CHECKING:
    from raise_cli.discovery.corpus import ModuleRef

__all__ = [
    "DriftBaselineRecord",
    "DriftMetricRecord",
    "DriftReportRecord",
    "MetricStore",
    "ModuleMetricEntry",
    "PercentileThresholds",
    "take_baseline",
    "take_report",
]


# ---------------------------------------------------------------------------
# Public models
# ---------------------------------------------------------------------------


class PercentileThresholds(BaseModel):
    """P75 or P90 thresholds for WMC, LCOM, and fan_out."""

    wmc: float
    lcom: float
    fan_out: float


class ModuleMetricEntry(BaseModel):
    """Per-module structural metrics snapshot."""

    module_id: str
    wmc: int
    lcom: int
    fan_in: int
    fan_out: int
    violation_score: int
    delta_wmc: int | None = None
    delta_lcom: int | None = None
    delta_fan_out: int | None = None


class DriftBaselineRecord(BaseModel):
    """Full-repo baseline snapshot with calibrated percentile thresholds."""

    record_type: Literal["baseline"] = "baseline"
    taken_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    module_count: int
    p75: PercentileThresholds
    p90: PercentileThresholds
    modules: list[ModuleMetricEntry]


class DriftReportRecord(BaseModel):
    """Per-story drift delta snapshot appended after story close."""

    record_type: Literal["report"] = "report"
    taken_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))
    story_id: str | None = None
    modules: list[ModuleMetricEntry]


DriftMetricRecord = Annotated[
    DriftBaselineRecord | DriftReportRecord,
    Field(discriminator="record_type"),
]


# ---------------------------------------------------------------------------
# MetricStore
# ---------------------------------------------------------------------------


class MetricStore:
    """Append-only JSONL store for drift metric records."""

    @staticmethod
    def append(path: Path, record: DriftBaselineRecord | DriftReportRecord) -> None:
        """Append a record as a JSONL line. Creates parent dirs if needed."""
        path.parent.mkdir(parents=True, exist_ok=True)
        existing = path.read_text(encoding="utf-8") if path.exists() else ""
        line = record.model_dump_json()
        path.write_text(existing + line + "\n", encoding="utf-8")

    @staticmethod
    def load(path: Path) -> list[DriftBaselineRecord | DriftReportRecord]:
        """Load all records from a JSONL store. Returns [] if missing or empty."""
        if not path.exists():
            return []
        records: list[DriftBaselineRecord | DriftReportRecord] = []
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            raw = json.loads(line)
            if raw.get("record_type") == "baseline":
                records.append(DriftBaselineRecord.model_validate(raw))
            elif raw.get("record_type") == "report":
                records.append(DriftReportRecord.model_validate(raw))
        return records

    @staticmethod
    def latest_baseline(
        records: list[DriftBaselineRecord | DriftReportRecord],
    ) -> DriftBaselineRecord | None:
        """Return the most recent baseline record, or None if none exist."""
        baselines = [r for r in records if isinstance(r, DriftBaselineRecord)]
        if not baselines:
            return None
        return max(baselines, key=lambda r: r.taken_at)


# ---------------------------------------------------------------------------
# Public functions
# ---------------------------------------------------------------------------


def take_baseline(
    store_path: Path,
    *,
    modules: list[ModuleRef] | None = None,
    index_path: Path | None = None,
) -> DriftBaselineRecord:
    """Scan modules, compute P75/P90 thresholds, and append a baseline record.

    Args:
        store_path:  Path to JSONL store (created if absent).
        modules:     Module list to scan. Scans packages/ tree if None.
        index_path:  Override graph index path (passed to run_drift_check).
    """
    resolved = modules if modules is not None else _discover_modules()
    cfg = DriftCheckConfig()
    entries: list[ModuleMetricEntry] = []

    for mod in resolved:
        if not mod.path.exists():
            continue
        with contextlib.suppress(Exception):
            report = run_drift_check(mod.path, cfg, index_path=index_path)
            entries.append(_entry_from_report(report))

    p75, p90 = _compute_percentiles(entries)
    rec = DriftBaselineRecord(
        module_count=len(entries),
        p75=p75,
        p90=p90,
        modules=entries,
    )
    MetricStore.append(store_path, rec)
    return rec


def take_report(
    store_path: Path,
    *,
    modules: list[ModuleRef] | None = None,
    story_id: str | None = None,
    index_path: Path | None = None,
) -> DriftReportRecord:
    """Scan modules, compute deltas vs latest baseline, and append a report record.

    Args:
        store_path:  Path to JSONL store.
        modules:     Module list to scan. Scans packages/ tree if None.
        story_id:    Optional story identifier for traceability.
        index_path:  Override graph index path.

    Raises:
        ValueError: If no baseline record exists in the store.
    """
    records = MetricStore.load(store_path)
    baseline = MetricStore.latest_baseline(records)
    if baseline is None:
        raise ValueError(
            f"No baseline found in {store_path}. Run 'rai drift baseline' first."
        )

    resolved = modules if modules is not None else _discover_modules()
    cfg = DriftCheckConfig()
    baseline_map = {e.module_id: e for e in baseline.modules}
    entries: list[ModuleMetricEntry] = []

    for mod in resolved:
        if not mod.path.exists():
            continue
        with contextlib.suppress(Exception):
            report = run_drift_check(mod.path, cfg, index_path=index_path)
            entry = _entry_from_report(report)
            prev = baseline_map.get(entry.module_id)
            if prev is not None:
                entry.delta_wmc = entry.wmc - prev.wmc
                entry.delta_lcom = entry.lcom - prev.lcom
                entry.delta_fan_out = entry.fan_out - prev.fan_out
            entries.append(entry)

    rec = DriftReportRecord(story_id=story_id, modules=entries)
    MetricStore.append(store_path, rec)
    return rec


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _entry_from_report(report: object) -> ModuleMetricEntry:
    """Extract a ModuleMetricEntry from a DriftCheckReport."""
    from raise_cli.discovery.check import DriftCheckReport

    if not isinstance(report, DriftCheckReport):
        raise TypeError(f"Expected DriftCheckReport, got {type(report)}")
    mr = report.metrics_report
    wmc = mr.wmc if mr is not None else 0
    lcom = mr.lcom if mr is not None else 0
    fan_in = mr.fan_in if mr is not None else 0
    fan_out = mr.fan_out if mr is not None else 0
    violation_score = sum(1 for s in report.signals if s.status == "warn")
    return ModuleMetricEntry(
        module_id=report.module_id,
        wmc=wmc,
        lcom=lcom,
        fan_in=fan_in,
        fan_out=fan_out,
        violation_score=violation_score,
    )


def _compute_percentiles(
    entries: list[ModuleMetricEntry],
) -> tuple[PercentileThresholds, PercentileThresholds]:
    """Compute P75 and P90 from a list of module metric entries."""
    if not entries:
        return (
            PercentileThresholds(wmc=0, lcom=0, fan_out=0),
            PercentileThresholds(wmc=0, lcom=0, fan_out=0),
        )

    def _pct(values: list[float], q: float) -> float:
        if len(values) == 1:
            return values[0]
        idx = max(0, min(98, int(round(q * 100)) - 1))
        return statistics.quantiles(values, n=100, method="inclusive")[idx]

    wmcs = [float(e.wmc) for e in entries]
    lcoms = [float(e.lcom) for e in entries]
    fan_outs = [float(e.fan_out) for e in entries]

    p75 = PercentileThresholds(
        wmc=_pct(wmcs, 0.75),
        lcom=_pct(lcoms, 0.75),
        fan_out=_pct(fan_outs, 0.75),
    )
    p90 = PercentileThresholds(
        wmc=_pct(wmcs, 0.90),
        lcom=_pct(lcoms, 0.90),
        fan_out=_pct(fan_outs, 0.90),
    )
    return p75, p90


def _discover_modules() -> list[ModuleRef]:
    """Discover Python sub-packages from the packages/*/src/ tree.

    Scans any top-level Python package under packages/<pkg>/src/<top>/<sub>/
    regardless of naming convention. Only covers Python (__init__.py marker).

    Package-qualified (RAISE-16033 R1): the id is minted the same way
    discovery does (``mod-<package>--<sub>``), keyed by the owning
    ``packages/<pkg>`` directory name. Before this fix, two different
    packages defining a same-named subpackage (e.g. both
    ``raise-server`` and ``raise-partners`` having an ``api/``) minted
    the same bare ``mod-api`` id, and the dedup guard below silently
    DROPPED the second one — real data loss, not just a cosmetic id
    mismatch: that module's WMC/LCOM/fan_out metrics never entered the
    baseline/report at all.
    """
    from raise_cli.discovery.corpus import ModuleRef as _ModuleRef

    modules: list[_ModuleRef] = []
    packages_root = Path("packages")
    if not packages_root.exists():
        return modules

    for src_dir in sorted(packages_root.glob("*/src")):
        package_name = src_dir.parent.name
        for top_pkg in sorted(src_dir.iterdir()):
            if not top_pkg.is_dir() or not (top_pkg / "__init__.py").exists():
                continue
            for sub_pkg in sorted(top_pkg.iterdir()):
                if not sub_pkg.is_dir() or not (sub_pkg / "__init__.py").exists():
                    continue
                module_id = qualified_module_id(
                    sub_pkg.name.replace("_", "-"), package_name
                )
                if not any(m.module_id == module_id for m in modules):
                    modules.append(_ModuleRef(module_id=module_id, path=sub_pkg))
    return modules
