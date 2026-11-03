"""Incremental rollup of reliability snapshots (RAISE-11494).

Each full backfill is expensive. In steady state (Phase B) we want to accumulate
results over time and surface a TREND without re-mining the whole history every
time. ``ReliabilityRollup`` persists one compact snapshot of the headline metrics
per backfill (append-only JSONL under ``.raise/``) and computes the delta vs the
previous snapshot.

v1 is snapshot-based (it accumulates backfill results); a true event-sourced
per-commit incremental miner is a deliberate follow-up.

Honesty discipline: ``trend()`` with fewer than 2 snapshots returns None+reason —
no invented trend. A metric that is None in either snapshot yields an 'unknown'
direction, never a fabricated delta. The snapshot stores headline metrics as bare
floats, dropping the report's ``DenominatorValue.reason``; ``escape_to_prod`` and
``cfr_proxy`` are PROXIES (see ``PROXY_DISCLAIMER``) and MUST be re-disclaimed
wherever a trend is rendered, so a directional claim never reads as authoritative.
"""

from __future__ import annotations

import logging
from datetime import date, datetime
from pathlib import Path
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

from raise_cli.reliability.models import Denominator

if TYPE_CHECKING:
    from raise_cli.reliability.models import ReliabilityReport

__all__ = [
    "MetricDelta",
    "ReliabilityRollup",
    "ReliabilitySnapshot",
    "RollupTrend",
]

_log = logging.getLogger(__name__)

_STORE_RELPATH = Path(".raise") / "reliability" / "rollup.jsonl"

# Metrics tracked in the trend, in display order.
_TRACKED = (
    "per_change",
    "product_escaped",
    "escape_to_prod",
    "cfr_proxy",
    "aggregate_mature",
)

# Metrics that are PROXIES (the snapshot stores a bare float and drops the
# report's DenominatorValue.reason — so the proxy caveat must be re-attached at
# render time, never letting a trend read as authoritative). See S11487.5.
PROXY_METRICS: frozenset[str] = frozenset({"escape_to_prod", "cfr_proxy"})

PROXY_DISCLAIMER = (
    "escape_to_prod and cfr_proxy are PROXIES (temporal-window / release-boundary "
    "matches that over-count); treat their trend as directional, not exact."
)


class ReliabilitySnapshot(BaseModel):
    """Compact headline-metric snapshot of one backfill (lower is better)."""

    taken_on: date
    repo: str
    branch: str
    per_change: float | None = None
    product_escaped: float | None = None
    escape_to_prod: float | None = None
    cfr_proxy: float | None = None
    aggregate_mature: float | None = None

    @classmethod
    def from_report(
        cls, report: ReliabilityReport, *, taken_on: date
    ) -> ReliabilitySnapshot:
        """Extract the headline metrics from a finished report."""
        ge = report.gate_escape
        cohorts = report.cohorts
        cfr = report.cfr
        return cls(
            taken_on=taken_on,
            repo=report.repo,
            branch=report.branch,
            per_change=report.escaped_rate[Denominator.PER_CHANGE].value,
            product_escaped=report.product_escaped_rate.value,
            escape_to_prod=(ge.escape_to_prod.value if ge is not None else None),
            cfr_proxy=(cfr.rate.value if cfr is not None else None),
            aggregate_mature=(
                cohorts.aggregate_mature.value if cohorts is not None else None
            ),
        )


class MetricDelta(BaseModel):
    """Change in one metric between the previous and current snapshot."""

    previous: float | None = None
    current: float | None = None
    delta: float | None = None
    direction: str = "unknown"  # improving | regressing | flat | unknown


class RollupTrend(BaseModel):
    """Per-metric trend vs the previous snapshot; ``reason`` set when unavailable."""

    metrics: dict[str, MetricDelta] = Field(default_factory=dict)
    reason: str | None = None


class ReliabilityRollup:
    """Append-only JSONL store of reliability snapshots + trend computation."""

    def __init__(self, repo_path: Path) -> None:
        self._path = repo_path / _STORE_RELPATH

    @property
    def path(self) -> Path:
        """Absolute path to the JSONL rollup store."""
        return self._path

    def append_snapshot(
        self, report: ReliabilityReport, *, taken_on: date | None = None
    ) -> ReliabilitySnapshot:
        """Append a snapshot of ``report``'s headline metrics; returns it."""
        when = taken_on or datetime.now().date()
        snap = ReliabilitySnapshot.from_report(report, taken_on=when)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._path.open("a", encoding="utf-8") as fh:
            fh.write(snap.model_dump_json() + "\n")
        return snap

    def snapshots(self) -> list[ReliabilitySnapshot]:
        """Read all stored snapshots; malformed lines are skipped."""
        if not self._path.exists():
            return []
        out: list[ReliabilitySnapshot] = []
        for raw in self._path.read_text(encoding="utf-8").splitlines():
            raw = raw.strip()
            if not raw:
                continue
            try:
                out.append(ReliabilitySnapshot.model_validate_json(raw))
            except ValueError:
                _log.debug("skipping malformed rollup line: %s", raw[:80])
        return out

    def trend(self) -> RollupTrend:
        """Compute the delta of each headline metric vs the previous snapshot.

        Fewer than 2 snapshots → None+reason (no invented trend).
        """
        snaps = self.snapshots()
        if len(snaps) < 2:
            return RollupTrend(
                reason=(
                    "insufficient: need at least 2 snapshots to compute a trend — "
                    "run `rai reliability rollup append` over time"
                )
            )
        prev, cur = snaps[-2], snaps[-1]
        metrics: dict[str, MetricDelta] = {}
        for name in _TRACKED:
            p = getattr(prev, name)
            c = getattr(cur, name)
            metrics[name] = _delta(p, c)
        return RollupTrend(metrics=metrics)


def _delta(previous: float | None, current: float | None) -> MetricDelta:
    """Build a MetricDelta; lower is better, so a drop is 'improving'."""
    if previous is None or current is None:
        return MetricDelta(previous=previous, current=current, direction="unknown")
    diff = current - previous
    if diff < 0:
        direction = "improving"
    elif diff > 0:
        direction = "regressing"
    else:
        direction = "flat"
    return MetricDelta(
        previous=previous, current=current, delta=diff, direction=direction
    )
