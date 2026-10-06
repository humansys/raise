"""Token measurement harness for session context (S2674.4).

Measures token counts per bundle section using the estimate_tokens heuristic.
Zero modifications to bundle assembly — reads assembled output as a consumer.
"""

from __future__ import annotations

from pydantic import BaseModel

from raise_core.graph.query import estimate_tokens

WINDOW_SIZE = 200_000


class MeasurementResult(BaseModel):
    """Per-section token measurement of session context."""

    bundle: dict[str, int]
    bundle_total: int
    agents_md: int | None = None
    combined_total: int
    window_size: int = WINDOW_SIZE
    window_pct: float

    @property
    def claude_md(self) -> int | None:
        """Backward compat alias — use agents_md instead."""
        return self.agents_md


def measure_bundle(
    orientation_text: str,
    section_texts: dict[str, str],
    agents_md_text: str | None = None,
    *,
    claude_md_text: str | None = None,
) -> MeasurementResult:
    """Measure token counts for assembled bundle sections.

    Args:
        orientation_text: The always-on orientation section text.
        section_texts: Map of section_name → assembled text for each priming section.
        agents_md_text: Optional AGENTS.md content to measure separately.
        claude_md_text: Deprecated alias for agents_md_text.

    Returns:
        MeasurementResult with per-section breakdown and totals.
    """
    effective_md_text = agents_md_text or claude_md_text

    bundle: dict[str, int] = {}

    bundle["orientation"] = estimate_tokens(orientation_text)
    for name, text in section_texts.items():
        bundle[name] = estimate_tokens(text)

    bundle_total = sum(bundle.values())

    agents_md_tokens: int | None = None
    if effective_md_text is not None:
        agents_md_tokens = estimate_tokens(effective_md_text)

    combined = bundle_total + (agents_md_tokens if agents_md_tokens is not None else 0)
    pct = (combined / WINDOW_SIZE * 100) if WINDOW_SIZE > 0 else 0.0

    return MeasurementResult(
        bundle=bundle,
        bundle_total=bundle_total,
        agents_md=agents_md_tokens,
        combined_total=combined,
        window_size=WINDOW_SIZE,
        window_pct=pct,
    )
