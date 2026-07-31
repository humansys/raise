"""Vintage cohort analysis with right-censoring discipline (RAISE-11492).

A *vintage cohort* groups changes by the period in which they were introduced
(when the buggy code was written — the SZZ introducer date), not when they were
fixed. For each period:

- denominator = commits made in that period (change volume)
- numerator   = escaped-defect introducers dated in that period

Right-censoring (measurement trap 2): a recent cohort looks clean only because
its defects have not surfaced yet. Cohorts younger than ``maturity_window_days``
are marked IN_FLIGHT and excluded from the headline aggregate — reported for
transparency, never averaged in.

Pure module: takes lists of dates, performs no git/subprocess work. The lens
(``reliability/lens.py``) resolves the dates and calls in here.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta
from typing import Literal

from raise_cli.reliability.models import (
    Cohort,
    CohortBreakdown,
    CohortMaturity,
    DenominatorValue,
)

__all__ = ["build_cohorts"]

PeriodKind = Literal["month", "quarter"]


def build_cohorts(
    change_dates: list[date],
    escaped_introducer_dates: list[date],
    *,
    period_kind: PeriodKind = "month",
    as_of: date,
    maturity_window_days: int = 90,
) -> CohortBreakdown:
    """Build a vintage cohort breakdown.

    Args:
        change_dates: Commit dates for the whole change stream (denominators).
        escaped_introducer_dates: Introducer dates of escaped defects (numerators).
            May fall outside the change window (a defect introduced before the
            analysis ``since`` but fixed within it) — such periods get a None+reason
            rate and are excluded from the aggregate.
        period_kind: Bin width — 'month' or 'quarter'.
        as_of: Reference date for maturity (typically today).
        maturity_window_days: A cohort is MATURE only if its whole period ended at
            least this many days before ``as_of``.

    Returns:
        CohortBreakdown with cohorts in chronological order and an aggregate over
        mature cohorts only.
    """
    change_buckets: dict[str, int] = defaultdict(int)
    escaped_buckets: dict[str, int] = defaultdict(int)
    bounds: dict[str, tuple[date, date]] = {}

    for d in change_dates:
        key, start, end = _period_of(d, period_kind)
        change_buckets[key] += 1
        bounds[key] = (start, end)

    for d in escaped_introducer_dates:
        key, start, end = _period_of(d, period_kind)
        escaped_buckets[key] += 1
        bounds.setdefault(key, (start, end))

    cohorts: list[Cohort] = []
    for key in sorted(bounds):
        start, end = bounds[key]
        total = change_buckets.get(key, 0)
        escaped = escaped_buckets.get(key, 0)
        rate = _cohort_rate(escaped, total)
        maturity = _maturity(end, as_of, maturity_window_days)
        cohorts.append(
            Cohort(
                period=key,
                period_start=start,
                period_end=end,
                total_changes=total,
                escaped_defects=escaped,
                rate=rate,
                maturity=maturity,
            )
        )

    aggregate, in_flight_excluded = _aggregate_mature(cohorts)

    return CohortBreakdown(
        period_kind=period_kind,
        maturity_window_days=maturity_window_days,
        as_of=as_of,
        cohorts=cohorts,
        aggregate_mature=aggregate,
        in_flight_excluded=in_flight_excluded,
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _cohort_rate(escaped: int, total: int) -> DenominatorValue:
    """escaped/total, or None+reason when there are no in-window changes."""
    if total == 0:
        return DenominatorValue(
            value=None,
            numerator=escaped,
            denominator=0,
            reason=(
                "insufficient: no in-window changes for this period — "
                "escaped defects were introduced before the analysis window"
            ),
        )
    return DenominatorValue(
        value=escaped / total,
        numerator=escaped,
        denominator=total,
    )


def _maturity(period_end: date, as_of: date, window_days: int) -> CohortMaturity:
    """MATURE iff the whole period ended at least ``window_days`` before ``as_of``."""
    cutoff = as_of - timedelta(days=window_days)
    return CohortMaturity.MATURE if period_end <= cutoff else CohortMaturity.IN_FLIGHT


def _aggregate_mature(cohorts: list[Cohort]) -> tuple[DenominatorValue, int]:
    """Pool escaped/changes over MATURE cohorts with >0 changes.

    Zero-change cohorts are skipped even when mature — they have no denominator
    to contribute and would otherwise inflate the numerator (orphan introducers).
    """
    num = 0
    den = 0
    in_flight = 0
    for c in cohorts:
        if c.maturity is CohortMaturity.IN_FLIGHT:
            in_flight += 1
            continue
        if c.total_changes == 0:
            continue
        num += c.escaped_defects
        den += c.total_changes

    if den == 0:
        return (
            DenominatorValue(
                value=None,
                numerator=num,
                denominator=0,
                reason="insufficient: no mature cohorts with in-window changes",
            ),
            in_flight,
        )
    return (
        DenominatorValue(value=num / den, numerator=num, denominator=den),
        in_flight,
    )


def _period_of(d: date, kind: PeriodKind) -> tuple[str, date, date]:
    """Return (label, start, end-exclusive) for the period containing ``d``."""
    if kind == "quarter":
        q = (d.month - 1) // 3  # 0..3
        start_month = q * 3 + 1
        start = date(d.year, start_month, 1)
        end_year = d.year + (1 if q == 3 else 0)
        end_month = 1 if q == 3 else start_month + 3
        end = date(end_year, end_month, 1)
        return (f"{d.year}-Q{q + 1}", start, end)

    # month
    start = date(d.year, d.month, 1)
    end_year = d.year + (1 if d.month == 12 else 0)
    end_month = 1 if d.month == 12 else d.month + 1
    end = date(end_year, end_month, 1)
    return (f"{d.year}-{d.month:02d}", start, end)
