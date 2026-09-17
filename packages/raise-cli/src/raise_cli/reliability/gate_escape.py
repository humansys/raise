"""Gate-stratified escape analysis (RAISE-11493).

A defect caught in MR review is far cheaper than one that reaches production.
Reporting a single "escape rate" blends cheap and expensive leaks (measurement
trap 8). ``GateEscapeTracker`` stratifies each escaped defect by the DEEPEST gate
it slipped past — using the available signal and never inventing a stage.

Backfill signal (git + deploy events only) can place a defect at PROD (a prod
deploy fell inside the introduce→discover window) or RELEASE (a release tag did),
else UNKNOWN. Finer stages (AR/QR, MR review, CI) require an MR/CI provider
(RAISE-11144), passed in optionally.

Pure module: takes dates and an optional provider callable; no git/IO.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable
from datetime import date

from pydantic import BaseModel

from raise_cli.reliability.models import (
    DenominatorValue,
    GateEscapeBreakdown,
    GateStage,
)

__all__ = ["DefectWindow", "GateEscapeTracker", "MrProvider"]

# Stages that mean "the defect got past MR review" (MR did not catch it).
_PAST_MR: frozenset[GateStage] = frozenset(
    {GateStage.CI, GateStage.RELEASE, GateStage.PROD}
)

# Proxy disclaimer carried on the POPULATED KPIs — the stage is inferred from a
# temporal window match (a deploy/tag fell between introduce and fix), NOT from
# matching the deploy's ref to the introducer. So it over-counts when deploys ship
# non-HEAD refs, and depends on the deploy log being reasonably complete.
_ESCAPE_TO_PROD_PROXY = (
    "proxy: temporal-window match — a production deploy fell between the defect's "
    "introduction and its fix; the deploy ref is NOT matched to the introducer, so "
    "this over-counts when deploys ship non-HEAD refs and assumes a complete deploy log"
)
_EXPENSIVE_GATE_PROXY = (
    "proxy: MR/CI stage attested by the gate-signal provider — accuracy depends on "
    "that provider's coverage"
)

# A provider maps a bug key → the deepest finer-grained stage it can attest, or None.
MrProvider = Callable[[str], GateStage | None]


class DefectWindow(BaseModel):
    """One attributed defect and the window in which it could have been caught."""

    bug_key: str
    introduced: date
    """Vintage — when the buggy code was written (SZZ introducer author date)."""

    discovered: date
    """When the fix landed (discovery proxy)."""


class GateEscapeTracker:
    """Stratify escaped defects by the deepest gate they crossed."""

    def stratify(
        self,
        defects: list[DefectWindow],
        prod_deploy_dates: list[date],
        release_dates: list[date],
        *,
        mr_provider: MrProvider | None = None,
        prod_environment: str = "prod",
    ) -> GateEscapeBreakdown:
        """Assign each defect a deepest stage and compute the two KPIs.

        Args:
            defects: Attributed defects with introduce→discover windows.
            prod_deploy_dates: Dates of deploys to the production boundary.
            release_dates: Dates of release tags.
            mr_provider: Optional callable giving a finer stage per bug key.
            prod_environment: Environment name treated as the production boundary.

        Returns:
            GateEscapeBreakdown with honest None+reason KPIs when signal is absent.
        """
        prod_sorted = sorted(prod_deploy_dates)
        rel_sorted = sorted(release_dates)
        counts: dict[GateStage, int] = defaultdict(int)
        past_mr = 0

        for d in defects:
            stage = self._stage_for(d, prod_sorted, rel_sorted, mr_provider)
            counts[stage] += 1
            if stage in _PAST_MR:
                past_mr += 1

        total = len(defects)
        unknown = counts.get(GateStage.UNKNOWN, 0)
        prod = counts.get(GateStage.PROD, 0)

        escape_to_prod = self._escape_to_prod(
            prod, total, has_deploys=bool(prod_deploy_dates)
        )
        expensive = self._expensive_gate_leakage(
            past_mr, total, has_provider=mr_provider is not None
        )

        return GateEscapeBreakdown(
            stage_counts=dict(counts),
            escape_to_prod=escape_to_prod,
            expensive_gate_leakage=expensive,
            unknown_count=unknown,
            prod_environment=prod_environment,
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _stage_for(
        defect: DefectWindow,
        prod_sorted: list[date],
        rel_sorted: list[date],
        mr_provider: MrProvider | None,
    ) -> GateStage:
        """Deepest gate the defect crossed before being caught.

        PROD and RELEASE come from temporal signal (deploy/tag inside the window).
        PROD is checked first because it is deeper. Only when neither fires do we
        consult the MR provider for a finer stage; absent that, UNKNOWN.
        """
        lo, hi = defect.introduced, defect.discovered
        if _any_in_range(prod_sorted, lo, hi):
            return GateStage.PROD
        if _any_in_range(rel_sorted, lo, hi):
            return GateStage.RELEASE
        if mr_provider is not None:
            finer = mr_provider(defect.bug_key)
            if finer is not None:
                return finer
        return GateStage.UNKNOWN

    @staticmethod
    def _escape_to_prod(
        prod: int, total: int, *, has_deploys: bool
    ) -> DenominatorValue:
        if not has_deploys:
            return DenominatorValue(
                value=None,
                numerator=prod,
                denominator=total,
                reason=(
                    "insufficient: no deployment events — the production boundary "
                    "is unknown; register deploys with `rai reliability deploy register`"
                ),
            )
        if total == 0:
            return DenominatorValue(
                value=None,
                numerator=0,
                denominator=0,
                reason="insufficient: no defects",
            )
        return DenominatorValue(
            value=prod / total,
            numerator=prod,
            denominator=total,
            reason=_ESCAPE_TO_PROD_PROXY,
        )

    @staticmethod
    def _expensive_gate_leakage(
        past_mr: int, total: int, *, has_provider: bool
    ) -> DenominatorValue:
        if not has_provider:
            return DenominatorValue(
                value=None,
                numerator=past_mr,
                denominator=total,
                reason=(
                    "insufficient: requires an MR/CI gate-signal provider "
                    "(RAISE-11144) — git alone cannot place the MR-review gate"
                ),
            )
        if total == 0:
            return DenominatorValue(
                value=None,
                numerator=0,
                denominator=0,
                reason="insufficient: no defects",
            )
        return DenominatorValue(
            value=past_mr / total,
            numerator=past_mr,
            denominator=total,
            reason=_EXPENSIVE_GATE_PROXY,
        )


def _any_in_range(sorted_dates: list[date], lo: date, hi: date) -> bool:
    """True if any date falls in the closed window [lo, hi]."""
    return any(lo <= d <= hi for d in sorted_dates)
