"""Pydantic models for the reliability lens — escaped-defect reporting (RAISE-11490).

Core types:
- Denominator: three ways to express escaped-defect rate
- Target: change target classification (product-wins rule)
- DenominatorValue: one denominator entry; reason MANDATORY when value is None
- ConfidenceSummary: SZZ confidence accounting
- ReliabilityReport: the full 3-denominator report with to_markdown()
"""

from __future__ import annotations

from datetime import date
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, model_validator

from raise_cli.quality.models import CrossCell
from raise_cli.reliability.recommendations import Recommendation

__all__ = [
    "ChangeFailureRate",
    "Cohort",
    "CohortBreakdown",
    "CohortMaturity",
    "ConfidenceSummary",
    "Denominator",
    "DenominatorValue",
    "GateEscapeBreakdown",
    "GateStage",
    "ReliabilityReport",
    "Target",
    "TargetTally",
]


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class Denominator(StrEnum):
    """Three ways to express the escaped-defect rate."""

    PER_CHANGE = "per_change"
    """Escaped fixes / total commits — the commit-stream denominator."""

    PER_DEPLOYMENT = "per_deployment"
    """Escaped product fixes / production-deploy count — grounded on deploy events
    (S11487.5); a proxy, not the DORA per-deployment CFR."""

    PER_DEFECT = "per_defect"
    """Escaped fixes / total defects (fix+bug) — the traditional DR metric."""


class Target(StrEnum):
    """Change target classification — product-wins rule applied in targets.py."""

    PRODUCT = "product"
    TEST = "test"
    CONFIG = "config"
    DOCS = "docs"
    OTHER = "other"
    UNKNOWN = "unknown"
    """Low-confidence or no-signal classification — not counted in product metrics."""


# Convenience alias — makes call-sites self-documenting
TargetTally = dict[Target, int]
"""Count of commits landing in each Target bucket."""


# ---------------------------------------------------------------------------
# DenominatorValue
# ---------------------------------------------------------------------------


class DenominatorValue(BaseModel):
    """One denominator entry for the escaped-defect rate.

    ``reason`` is MANDATORY when ``value`` is ``None`` (structural slot or
    insufficient data). When ``value`` is populated, ``reason`` is optional
    context.
    """

    value: float | None = None
    """Computed rate, or None if this denominator is unavailable."""

    numerator: int | None = None
    """Raw count of escaped defects (numerator)."""

    denominator: int | None = None
    """Denominator count (total commits / deployments / defects)."""

    reason: str | None = None
    """MANDATORY when value is None: explains why the slot is empty."""

    @model_validator(mode="after")
    def _reason_required_when_none(self) -> DenominatorValue:
        if self.value is None and not self.reason:
            msg = "reason is required when value is None — provide a non-empty explanation"
            raise ValueError(msg)
        return self


# ---------------------------------------------------------------------------
# ConfidenceSummary
# ---------------------------------------------------------------------------


class ConfidenceSummary(BaseModel):
    """SZZ confidence accounting — tracks the filtering that happened."""

    threshold: float = Field(ge=0.0, le=1.0)
    """Minimum confidence score to include an attribution in the report."""

    kept: int = 0
    """Attributions whose confidence >= threshold (included in numerators)."""

    excluded: int = 0
    """Attributions whose confidence < threshold (excluded from numerators)."""

    net_new_skipped: int = 0
    """Fix commits where SZZ returned [] (net-new code); counted separately,
    not dropped — they contribute to the denominator but not the numerator."""

    bands: dict[str, int] = Field(default_factory=dict)
    """Distribution by confidence band: high/medium/low counts."""


# ---------------------------------------------------------------------------
# Cohort analysis (vintage / right-censoring) — S11487.4
# ---------------------------------------------------------------------------


class CohortMaturity(StrEnum):
    """Whether a cohort has had enough time for its defects to surface."""

    MATURE = "mature"
    """Discovery window elapsed — escape count is trustworthy."""

    IN_FLIGHT = "in_flight"
    """Right-censored — defects may still surface; excluded from headline."""


class Cohort(BaseModel):
    """One vintage cohort: changes made in a period and their escaped defects.

    The cohort is keyed by *introduction* date (when the buggy code was written),
    not fix date. ``rate`` is None+reason when the cohort had zero changes.
    """

    period: str
    """Human label, e.g. '2025-03' (month) or '2025-Q1' (quarter)."""

    period_start: date
    """Inclusive start of the cohort window."""

    period_end: date
    """Exclusive end of the cohort window."""

    total_changes: int
    """Denominator: commits whose date falls in this period."""

    escaped_defects: int
    """Numerator: escaped-defect introducers whose date falls in this period."""

    rate: DenominatorValue
    """escaped_defects / total_changes, or None+reason when total_changes == 0."""

    maturity: CohortMaturity
    """MATURE or IN_FLIGHT (right-censored)."""


class CohortBreakdown(BaseModel):
    """Vintage cohort breakdown with right-censoring discipline.

    ``aggregate_mature`` averages ONLY mature cohorts — in-flight cohorts are
    reported (transparency) but excluded from the headline to avoid undercounting
    their not-yet-discovered defects.
    """

    period_kind: str
    """'month' or 'quarter'."""

    maturity_window_days: int
    """Days a cohort must age before it is considered MATURE."""

    as_of: date
    """Reference date used to compute maturity (typically 'today')."""

    cohorts: list[Cohort] = Field(default_factory=list)
    """Cohorts in chronological order."""

    aggregate_mature: DenominatorValue
    """Pooled escaped/changes over MATURE cohorts only; None+reason if none mature."""

    in_flight_excluded: int = 0
    """Count of IN_FLIGHT cohorts excluded from the aggregate."""


# ---------------------------------------------------------------------------
# Change Failure Rate (release-boundary proxy) — S11487.4
# ---------------------------------------------------------------------------


class ChangeFailureRate(BaseModel):
    """Release-boundary CFR proxy. ``is_proxy`` is ALWAYS True in this story.

    NOT the per-deployment DORA Change Failure Rate — that requires a real
    deployment-event boundary (DeploymentEventStore, S11487.5). This counts
    releases that were followed by an escaped product fix before the next release.
    """

    rate: DenominatorValue
    """releases_failed / releases_considered, or None+reason if no releases."""

    is_proxy: bool = True
    """ALWAYS True here — guards against misreading this as DORA CFR."""

    proxy_basis: str
    """Mandatory disclaimer explaining the proxy and its limitation."""

    releases_considered: int = 0
    """Mature releases used to compute the rate (in-flight ones are excluded)."""

    releases_failed: int = 0
    """Mature releases followed by ≥1 escaped product fix before the next release."""

    releases_in_flight: int = 0
    """Recent releases excluded from the rate — right-censored (not enough time
    has elapsed since the release for a hotfix to surface). Reported for
    transparency, never counted, mirroring the cohort maturity rule."""

    window_start: date | None = None
    """Date of the earliest release considered (None if no releases)."""

    window_end: date | None = None
    """End of the analysis window (typically as_of)."""


# ---------------------------------------------------------------------------
# Gate-stratified escape (trap 8) — S11487.5
# ---------------------------------------------------------------------------


class GateStage(StrEnum):
    """Gates a change passes through, shallowest → deepest.

    A defect's stage is the DEEPEST gate it slipped past before being caught.
    PROD is the most expensive escape; UNKNOWN means no signal placed it (never
    inferred — git alone cannot distinguish AR/QR vs MR vs CI without an MR/CI
    provider, RAISE-11144).
    """

    AR_QR = "ar_qr"
    MR_REVIEW = "mr_review"
    CI = "ci"
    RELEASE = "release"
    PROD = "prod"
    UNKNOWN = "unknown"


class GateEscapeBreakdown(BaseModel):
    """Escape counts stratified by the deepest gate each defect crossed.

    Both KPIs follow None+reason discipline: ``escape_to_prod`` is None when there
    are no deployment events (production boundary unknown — trap 4);
    ``expensive_gate_leakage`` is None without an MR/CI gate-signal provider.
    ``unknown_count`` is reported separately and never inflates a KPI.
    """

    stage_counts: dict[GateStage, int] = Field(default_factory=dict)
    """Count of defects whose deepest crossed gate is each stage."""

    escape_to_prod: DenominatorValue
    """Defects that reached production / total attributed; None+reason if no deploys."""

    expensive_gate_leakage: DenominatorValue
    """Defects that slipped past MR review / total; None+reason without MR provider."""

    unknown_count: int = 0
    """Defects with no gate signal (counted, never folded into a KPI numerator)."""

    prod_environment: str = "prod"
    """Which environment was treated as the production boundary."""


# ---------------------------------------------------------------------------
# ReliabilityReport
# ---------------------------------------------------------------------------


class ReliabilityReport(BaseModel):
    """Full 3-denominator escaped-defect report.

    Design constraints:
    - ``escaped_rate`` ALWAYS has exactly 3 keys (Denominator enum).
    - ``per_deployment`` slot is always DenominatorValue(value=None, reason=...).
    - ``cohorts`` and ``cfr`` are populated by S11487.4 (None when uncomputable).
    - ``to_markdown()`` renders all 3 denominators + confidence caveat.
    """

    escaped_rate: dict[Denominator, DenominatorValue]
    """3-key dict: PER_CHANGE, PER_DEPLOYMENT, PER_DEFECT."""

    product_escaped_rate: DenominatorValue
    """per_change rate filtered to product-target commits only (product-wins)."""

    target_tally: TargetTally
    """Commit counts per Target bucket."""

    hotspots: list[CrossCell] = Field(default_factory=list)
    """Origin×Type cross-cells with highest escaped counts (S11487.4)."""

    cohorts: CohortBreakdown | None = None
    """Vintage cohort breakdown (S11487.4); None when the lens could not compute it."""

    cfr: ChangeFailureRate | None = None
    """Release-boundary CFR proxy (S11487.4); None when no releases in window."""

    gate_escape: GateEscapeBreakdown | None = None
    """Gate-stratified escape (S11487.5); None when the lens could not compute it."""

    recommendations: list[str] = Field(default_factory=list)
    """Rendered recommendation messages (strings) for human/markdown output."""

    recommendation_details: list[Recommendation] = Field(default_factory=list)
    """Structured recommendations (rule_id + severity + evidence) for JSON consumers."""

    confidence: ConfidenceSummary
    """SZZ confidence accounting."""

    confidence_note: str
    """Human-readable caveat about confidence filtering.

    The note reports the *actual* SZZ-exclusion percentage computed dynamically
    at run time (e.g. '~30%', '~0%') — not a fixed '~25%' baseline.  The only
    stable token is 'not a DORA', which is always present.  Hand-built test
    fixtures may use any valid percentage string; the to_markdown() contract
    only checks for 'not a DORA'.
    """

    repo: str
    """Repository name (for the report header)."""

    branch: str
    """Branch analysed (for the report header)."""

    since: date
    """Start date of the analysis window."""

    @model_validator(mode="after")
    def _escaped_rate_has_all_three_keys(self) -> ReliabilityReport:
        required = {
            Denominator.PER_CHANGE,
            Denominator.PER_DEPLOYMENT,
            Denominator.PER_DEFECT,
        }
        actual = set(self.escaped_rate.keys())
        if actual != required:
            missing = required - actual
            extra = actual - required
            parts: list[str] = []
            if missing:
                parts.append(f"missing={missing}")
            if extra:
                parts.append(f"extra={extra}")
            msg = (
                f"escaped_rate must have exactly 3 Denominator keys; {', '.join(parts)}"
            )
            raise ValueError(msg)
        return self

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def to_markdown(self) -> str:
        """Render the report as a Markdown string.

        Contract (enforced by tests):
        - Contains 'per-change', 'per-deployment', 'per-defect'
        - Contains the confidence_note (which must include 'not a DORA')
        - Contains repo name and branch
        """
        lines: list[str] = [
            f"# Reliability Baseline — {self.repo} ({self.branch})",
            "",
            f"**Since:** {self.since}  ",
            "",
            "## Escaped-Defect Rate",
            "",
            "| Denominator | Rate | Numerator | Denominator | Note |",
            "|-------------|------|-----------|-------------|------|",
        ]

        def _fmt_row(label: str, dv: DenominatorValue) -> str:
            rate = f"{dv.value:.4f}" if dv.value is not None else "—"
            num = str(dv.numerator) if dv.numerator is not None else "—"
            den = str(dv.denominator) if dv.denominator is not None else "—"
            note = dv.reason or ""
            return f"| {label} | {rate} | {num} | {den} | {note} |"

        pc = self.escaped_rate[Denominator.PER_CHANGE]
        pd_slot = self.escaped_rate[Denominator.PER_DEPLOYMENT]
        pdef = self.escaped_rate[Denominator.PER_DEFECT]

        lines.append(_fmt_row("per-change", pc))
        lines.append(_fmt_row("per-deployment", pd_slot))
        lines.append(_fmt_row("per-defect", pdef))
        lines.append("")

        # product-only row
        prod = self.product_escaped_rate
        prod_rate = f"{prod.value:.4f}" if prod.value is not None else "—"
        lines.append(f"**Product-only per-change:** {prod_rate}  ")
        lines.append("")

        # Target tally
        lines.append("## Target Tally")
        lines.append("")
        lines.append("| Target | Commits |")
        lines.append("|--------|---------|")
        for target, count in self.target_tally.items():
            lines.append(f"| {target} | {count} |")
        lines.append("")

        # Confidence
        cs = self.confidence
        lines.append("## Confidence")
        lines.append("")
        lines.append(
            f"Threshold={cs.threshold:.2f}  kept={cs.kept}  "
            f"excluded={cs.excluded}  net-new-skipped={cs.net_new_skipped}"
        )
        lines.append("")

        # Confidence note (contains dynamic exclusion % and 'not a DORA' per contract)
        lines.append(f"> {self.confidence_note}")
        lines.append("")

        # Cohorts (vintage / right-censoring)
        if self.cohorts is not None:
            lines.extend(_render_cohorts(self.cohorts))

        # Change Failure Rate (release-boundary proxy)
        if self.cfr is not None:
            lines.extend(_render_cfr(self.cfr))

        # Gate-stratified escape
        if self.gate_escape is not None:
            lines.extend(_render_gate_escape(self.gate_escape))

        # Hotspots (Origin×Type) with confidence band
        if self.hotspots:
            lines.extend(_render_hotspots(self.hotspots))

        # Recommendations
        if self.recommendations:
            lines.append("## Recommendations")
            lines.append("")
            for rec in self.recommendations:
                lines.append(f"- {rec}")
            lines.append("")

        return "\n".join(lines)

    def model_dump(self, **kwargs: Any) -> dict[str, Any]:
        """Override to serialize Denominator keys as strings."""
        d = super().model_dump(**kwargs)
        # Convert Denominator enum keys to str for JSON serialisation
        if "escaped_rate" in d and isinstance(d["escaped_rate"], dict):
            d["escaped_rate"] = {str(k): v for k, v in d["escaped_rate"].items()}
        if "target_tally" in d and isinstance(d["target_tally"], dict):
            d["target_tally"] = {str(k): v for k, v in d["target_tally"].items()}
        return d


# ---------------------------------------------------------------------------
# Markdown rendering helpers for S11487.4 sections
# ---------------------------------------------------------------------------


def _render_cohorts(cohorts: CohortBreakdown) -> list[str]:
    """Render the vintage-cohort section with maturity flags and the censored aggregate."""
    lines = [
        f"## Cohorts (vintage, by {cohorts.period_kind})",
        "",
        "| Period | Changes | Escaped | Rate | Maturity |",
        "|--------|---------|---------|------|----------|",
    ]
    for c in cohorts.cohorts:
        rate = f"{c.rate.value:.4f}" if c.rate.value is not None else "—"
        lines.append(
            f"| {c.period} | {c.total_changes} | {c.escaped_defects} | "
            f"{rate} | {c.maturity} |"
        )
    lines.append("")

    agg = cohorts.aggregate_mature
    if agg.value is not None:
        agg_n = f" ({agg.numerator}/{agg.denominator})" if agg.denominator else ""
        agg_rate = f"{agg.value:.4f}{agg_n}"
    else:
        agg_rate = f"— ({agg.reason})"
    lines.append(f"**Mature-cohort aggregate:** {agg_rate}  ")
    lines.append(
        f"> {cohorts.in_flight_excluded} in-flight cohort(s) excluded from the "
        f"aggregate (right-censored — defects may not have surfaced yet)."
    )
    lines.append("")
    return lines


def _render_cfr(cfr: ChangeFailureRate) -> list[str]:
    """Render the CFR section, always carrying the proxy disclaimer."""
    rate = (
        f"{cfr.rate.value:.4f}"
        if cfr.rate.value is not None
        else f"— ({cfr.rate.reason})"
    )
    lines = [
        "## Change Failure Rate (release-boundary proxy)",
        "",
        f"**Rate:** {rate}  ",
        f"**Releases:** {cfr.releases_failed} failed / {cfr.releases_considered} considered "
        f"({cfr.releases_in_flight} in-flight, right-censored)  ",
        "",
        f"> ⚠️ PROXY — {cfr.proxy_basis}",
        "",
    ]
    return lines


def _render_hotspots(hotspots: list[CrossCell]) -> list[str]:
    """Render Origin×Type hotspots ranked with a confidence band (share-weighted)."""
    from raise_cli.reliability.recommendations import band_hotspots

    total = sum(c.fix_bug_count for c in hotspots)
    ranked = band_hotspots(hotspots, total=total)
    lines = [
        "## Hotspots (Origin×Type)",
        "",
        "| Origin | Type | Count | Share | Confidence |",
        "|--------|------|-------|-------|------------|",
    ]
    for r in ranked:
        lines.append(
            f"| {r.cell.origin} | {r.cell.type} | {r.cell.fix_bug_count} | "
            f"{r.share:.0%} | {r.band} |"
        )
    lines.append("")
    return lines


def _render_gate_escape(ge: GateEscapeBreakdown) -> list[str]:
    """Render the gate-stratified escape section with honest KPI caveats."""

    def _kpi(label: str, dv: DenominatorValue) -> str:
        if dv.value is not None:
            n = f" ({dv.numerator}/{dv.denominator})" if dv.denominator else ""
            # Always surface the proxy caveat, even when populated (the value
            # rests on a temporal-window match that over-counts — never hide it).
            caveat = f" — {dv.reason}" if dv.reason else ""
            return f"**{label}:** {dv.value:.4f}{n}{caveat}  "
        reason = dv.reason or "no data"
        return f"**{label}:** — ({reason})  "

    lines = [
        "## Gate-Stratified Escape",
        "",
        f"Production boundary: `{ge.prod_environment}`",
        "",
        "| Gate stage | Defects |",
        "|------------|---------|",
    ]
    for stage, count in ge.stage_counts.items():
        lines.append(f"| {stage} | {count} |")
    lines.append("")
    lines.append(_kpi("Escape-to-prod", ge.escape_to_prod))
    lines.append(_kpi("Expensive-gate (MR) leakage", ge.expensive_gate_leakage))
    lines.append(
        f"**Unknown stage:** {ge.unknown_count} (no gate signal — not in any KPI)  "
    )
    lines.append("")
    return lines
