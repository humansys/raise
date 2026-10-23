"""EpicCloseGate — advisory P90 drift gate for before:epic:close.

Compares current module metrics against the P90 baseline from MetricStore
(S2100.3). Modules exceeding any P90 threshold (WMC, LCOM, fan_out) that
are not whitelisted in governance/drift-whitelist.json are reported.

Advisory: always returns passed=True (PAT-E-1121).
Architecture: S2100.4, ADR-039 §1 (WorkflowGate Protocol)
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import ClassVar

from raise_cli.discovery.metric import DriftReportRecord, MetricStore, ModuleMetricEntry
from raise_cli.gates.drift._base import DriftGate, advisory
from raise_cli.gates.models import GateContext, GateResult

logger = logging.getLogger(__name__)

_METRIC_STORE_PATH = Path(".raise") / "rai" / "memory" / "drift-metric.jsonl"
_WHITELIST_PATH = Path("governance") / "drift-whitelist.json"


def _load_whitelist(working_dir: Path) -> frozenset[str]:
    """Load whitelisted module IDs from governance/drift-whitelist.json.

    Returns empty frozenset if file absent or malformed.
    """
    path = working_dir / _WHITELIST_PATH
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return frozenset(e["module_id"] for e in data.get("entries", []))
    except (OSError, KeyError, json.JSONDecodeError):
        return frozenset()


def _hotspot_lines(
    modules: list[ModuleMetricEntry],
    p90_wmc: float,
    p90_lcom: float,
    p90_fan_out: float,
    whitelist: frozenset[str],
) -> list[str]:
    """Return advisory lines for modules exceeding any P90 threshold."""
    lines: list[str] = []
    for m in modules:
        if m.module_id in whitelist:
            continue
        flags: list[str] = []
        if m.wmc > p90_wmc:
            flags.append(f"wmc={m.wmc} > p90={p90_wmc:.0f}")
        if m.lcom > p90_lcom:
            flags.append(f"lcom={m.lcom} > p90={p90_lcom:.0f}")
        if m.fan_out > p90_fan_out:
            flags.append(f"fan_out={m.fan_out} > p90={p90_fan_out:.0f}")
        if flags:
            lines.append(f"{m.module_id}: {', '.join(flags)}")
    return lines


class EpicCloseGate(DriftGate):
    """Advisory gate checking structural drift against P90 baseline at epic close.

    Uses MetricStore (S2100.3) for P90 thresholds. Modules in
    governance/drift-whitelist.json are excluded from reporting.
    Advisory until FP calibration completes (PAT-E-1121).
    """

    gate_id: ClassVar[str] = "gate-epic-close-drift"
    description: ClassVar[str] = (
        "Drift within P90 baseline before epic close (advisory)"
    )
    workflow_point: ClassVar[str] = "before:epic:close"
    is_blocker: ClassVar[bool] = False

    def evaluate(self, context: GateContext) -> GateResult:
        """Check structural drift against P90 baseline."""
        store_path = context.working_dir / _METRIC_STORE_PATH
        records = MetricStore.load(store_path)
        baseline = MetricStore.latest_baseline(records)

        if baseline is None:
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message="No baseline found — run 'rai drift baseline' first",
            )

        # Use most recent report modules if available; fall back to baseline
        reports = [r for r in records if isinstance(r, DriftReportRecord)]
        current_modules = reports[-1].modules if reports else baseline.modules

        whitelist = _load_whitelist(context.working_dir)
        p90 = baseline.p90
        hotspots = _hotspot_lines(
            current_modules, p90.wmc, p90.lcom, p90.fan_out, whitelist
        )

        if not hotspots and whitelist:
            wl_count = len(whitelist)
            return GateResult(
                passed=True,
                gate_id=self.gate_id,
                message=f"No hotspot modules above P90 threshold ({wl_count} whitelisted)",
            )

        return advisory(
            self.gate_id, hotspots, clean_msg="No hotspot modules above P90 threshold"
        )
