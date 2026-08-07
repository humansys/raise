"""Prescriptive recommendation engine — deterministic rules (RAISE-11494).

The reliability lens describes; this engine prescribes. It reads a finished
``ReliabilityReport`` and emits prioritised, TRACEABLE recommendations using
deterministic rules (decision b — no learned model). Every recommendation cites
the exact datum that triggered it (``evidence``).

Honesty discipline: a rule that depends on a KPI which is ``None+reason`` does
NOT fire — the engine never prescribes over a number that does not exist. A
single ``confidence-low`` rule surfaces when attributions are too uncertain to
trust the headline numbers.

Pure module: takes a report + config, returns recommendations; no IO.
"""

from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING

from pydantic import BaseModel

from raise_cli.quality.models import CrossCell

if TYPE_CHECKING:
    from raise_cli.reliability.models import ReliabilityReport

__all__ = [
    "RankedHotspot",
    "Recommendation",
    "RecommendationEngine",
    "RuleConfig",
    "Severity",
    "band_hotspots",
]


class Severity(StrEnum):
    """Recommendation severity, ordered critical → warn → info for sorting."""

    INFO = "info"
    WARN = "warn"
    CRITICAL = "critical"


_SEVERITY_ORDER = {Severity.CRITICAL: 0, Severity.WARN: 1, Severity.INFO: 2}


class Recommendation(BaseModel):
    """One prescriptive recommendation, traceable to the datum that triggered it."""

    rule_id: str
    severity: Severity
    message: str
    evidence: str
    """The exact datum that fired this rule (audit trail)."""

    category: str


class RuleConfig(BaseModel):
    """Tunable thresholds for the deterministic rules.

    Defaults are grounded in DORA bands (Elite CFR ≤5%, High ≤10%); the proxies
    here use 15% as a warn floor. All overridable.
    """

    hotspot_share: float = 0.30
    hotspot_min_count: int = 5
    """Minimum absolute defects in the dominant cell before it earns a recommendation —
    prevents prescribing off thin data (a 2/3 'dominance' is noise, not signal)."""
    escape_prod_warn: float = 0.15
    escape_prod_critical: float = 0.30
    mr_leak_warn: float = 0.50
    cfr_warn: float = 0.15
    low_conf_pct: float = 0.40


class RankedHotspot(BaseModel):
    """An Origin×Type cell annotated with its share and a confidence band."""

    cell: CrossCell
    share: float
    band: str  # high | medium | low


def band_hotspots(hotspots: list[CrossCell], *, total: int) -> list[RankedHotspot]:
    """Annotate hotspots with share-of-total and a confidence band.

    Band reflects how much we should trust the cell: a cell built from few
    attributions gets a low band so it is not over-interpreted.
    - high:   count >= 5 and share >= 0.15
    - medium: count >= 2
    - low:    otherwise

    ``total`` is the attribution total used for share; total == 0 → all shares 0.
    Returned in descending share order.
    """
    # NOTE: these band thresholds are DISPLAY-TRUST gates and are intentionally
    # separate from RuleConfig's PRESCRIPTION gates (hotspot_min_count/hotspot_share).
    # A cell may render "high" (display) without earning a recommendation (action):
    # the band says "trust this number", the rule says "act on it". Kept literal so
    # tuning the prescription thresholds never silently shifts the display banding.
    ranked: list[RankedHotspot] = []
    for cell in hotspots:
        share = cell.fix_bug_count / total if total > 0 else 0.0
        if cell.fix_bug_count >= 5 and share >= 0.15:
            band = "high"
        elif cell.fix_bug_count >= 2:
            band = "medium"
        else:
            band = "low"
        ranked.append(RankedHotspot(cell=cell, share=share, band=band))
    ranked.sort(key=lambda r: r.share, reverse=True)
    return ranked


class RecommendationEngine:
    """Run the deterministic rule set over a ReliabilityReport."""

    def recommend(
        self, report: ReliabilityReport, config: RuleConfig | None = None
    ) -> list[Recommendation]:
        """Return recommendations ordered by severity (critical first).

        Rules whose driving KPI is None+reason are skipped — no prescription over
        absent data.
        """
        cfg = config or RuleConfig()
        recs: list[Recommendation] = []
        for rule in (
            self._rule_hotspot_dominant,
            self._rule_escape_to_prod,
            self._rule_expensive_gate,
            self._rule_cfr_high,
            self._rule_cohort_rising,
            self._rule_confidence_low,
        ):
            rec = rule(report, cfg)
            if rec is not None:
                recs.append(rec)
        recs.sort(key=lambda r: _SEVERITY_ORDER[r.severity])
        return recs

    # ------------------------------------------------------------------
    # Rules — each pure: (report, cfg) -> Recommendation | None
    # ------------------------------------------------------------------

    @staticmethod
    def _rule_hotspot_dominant(
        report: ReliabilityReport, cfg: RuleConfig
    ) -> Recommendation | None:
        total = sum(c.fix_bug_count for c in report.hotspots)
        if total == 0:
            return None
        top = max(report.hotspots, key=lambda c: c.fix_bug_count)
        share = top.fix_bug_count / total
        # Require BOTH a dominant share AND enough absolute defects — a high share
        # over a handful of defects is noise, not a signal worth prescribing on.
        if share < cfg.hotspot_share or top.fix_bug_count < cfg.hotspot_min_count:
            return None
        guidance = (
            "reinforce design review at AR"
            if top.origin.lower().startswith("design")
            else "add targeted unit tests"
        )
        return Recommendation(
            rule_id="hotspot-dominant",
            severity=Severity.WARN,
            message=(
                f"{top.origin}/{top.type} dominates escaped defects "
                f"({top.fix_bug_count}/{total}, {share:.0%}) — {guidance}."
            ),
            evidence=f"{top.origin}/{top.type}={top.fix_bug_count}/{total}",
            category="hotspot",
        )

    @staticmethod
    def _rule_escape_to_prod(
        report: ReliabilityReport, cfg: RuleConfig
    ) -> Recommendation | None:
        ge = report.gate_escape
        if ge is None or ge.escape_to_prod.value is None:
            return None
        v = ge.escape_to_prod.value
        if v < cfg.escape_prod_warn:
            return None
        sev = Severity.CRITICAL if v >= cfg.escape_prod_critical else Severity.WARN
        return Recommendation(
            rule_id="escape-to-prod-high",
            severity=sev,
            message=(
                f"{v:.0%} of attributed defects reached production — strengthen the "
                "staging/prod gate (proxy; see escape disclaimer)."
            ),
            evidence=f"escape_to_prod={v:.4f}",
            category="gate",
        )

    @staticmethod
    def _rule_expensive_gate(
        report: ReliabilityReport, cfg: RuleConfig
    ) -> Recommendation | None:
        ge = report.gate_escape
        if ge is None or ge.expensive_gate_leakage.value is None:
            return None
        v = ge.expensive_gate_leakage.value
        if v < cfg.mr_leak_warn:
            return None
        return Recommendation(
            rule_id="expensive-gate-leak",
            severity=Severity.WARN,
            message=(
                f"{v:.0%} of defects slipped past MR review (proxy) — add a review "
                "checklist for the dominant failure mode."
            ),
            evidence=f"expensive_gate_leakage={v:.4f}",
            category="gate",
        )

    @staticmethod
    def _rule_cfr_high(
        report: ReliabilityReport, cfg: RuleConfig
    ) -> Recommendation | None:
        cfr = report.cfr
        if cfr is None or cfr.rate.value is None:
            return None
        v = cfr.rate.value
        if v < cfg.cfr_warn:
            return None
        return Recommendation(
            rule_id="cfr-high",
            severity=Severity.WARN,
            message=(
                f"{v:.0%} of releases needed a follow-up fix (proxy) — reinforce "
                "pre-release verification."
            ),
            evidence=f"cfr_proxy={v:.4f}",
            category="release",
        )

    @staticmethod
    def _rule_cohort_rising(
        report: ReliabilityReport, _cfg: RuleConfig
    ) -> Recommendation | None:
        cohorts = report.cohorts
        if cohorts is None or not cohorts.cohorts:
            return None
        agg = cohorts.aggregate_mature.value
        if agg is None:
            return None
        in_flight = [
            c
            for c in cohorts.cohorts
            if c.maturity == "in_flight" and c.rate.value is not None
        ]
        if not in_flight:
            return None
        latest = in_flight[-1]
        if latest.rate.value is None or latest.rate.value <= agg:
            return None
        return Recommendation(
            rule_id="cohort-rising",
            severity=Severity.INFO,
            message=(
                f"In-flight cohort {latest.period} rate ({latest.rate.value:.0%}) "
                f"exceeds the mature baseline ({agg:.0%}) — watch; defects still surfacing."
            ),
            evidence=f"{latest.period}={latest.rate.value:.4f} vs mature={agg:.4f}",
            category="cohort",
        )

    @staticmethod
    def _rule_confidence_low(
        report: ReliabilityReport, cfg: RuleConfig
    ) -> Recommendation | None:
        cs = report.confidence
        attempts = cs.kept + cs.excluded
        if attempts == 0:
            return None
        excl_pct = cs.excluded / attempts
        if excl_pct < cfg.low_conf_pct:
            return None
        return Recommendation(
            rule_id="confidence-low",
            severity=Severity.INFO,
            message=(
                f"{excl_pct:.0%} of SZZ attributions were low-confidence — treat the "
                "headline numbers as directional, not precise."
            ),
            evidence=f"excluded={cs.excluded}/{attempts}",
            category="confidence",
        )
