"""Fleet cost summary — CostSummary dataclass and format_cost_summary().

Pure module — no I/O, no external deps. All arithmetic is local.
"""

from __future__ import annotations

from dataclasses import dataclass

# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CostSummary:
    """Aggregated cost data for a fleet run."""

    model: str
    n_stories: int
    estimated_usd: float
    actual_usd: float | None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def format_cost_summary(summary: CostSummary) -> str:
    """Format a CostSummary as a human-readable multi-line string.

    Output format::

        💰 Fleet run cost — N stories (model)
           estimated: $X.XXXX
           actual:    $Y.YYYY  (Δ ±Z.ZZZZ, ±P.P%)   # if actual is set
           actual:    n/a                              # if actual is None

    Args:
        summary: CostSummary to render.

    Returns:
        3-line string.
    """
    lines = [
        f"💰 Fleet run cost — {summary.n_stories} stories ({summary.model})",
        f"   estimated: ${summary.estimated_usd:.4f}",
    ]

    if summary.actual_usd is None:
        lines.append("   actual:    n/a")
    else:
        delta = summary.actual_usd - summary.estimated_usd
        if summary.estimated_usd != 0:
            pct = f"{delta / summary.estimated_usd * 100:+.1f}%"
        else:
            pct = "—"
        lines.append(
            f"   actual:    ${summary.actual_usd:.4f}  (Δ {delta:+.4f}, {pct})"
        )

    return "\n".join(lines)
