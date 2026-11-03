"""DDD escalation panel — 3-model majority vote for contested symbols."""

from __future__ import annotations

import logging
from collections import Counter
from dataclasses import dataclass

from raise_cli.ddd.classifier import ClassificationResult, classify_symbols

logger = logging.getLogger(__name__)

PANEL_MODELS = [
    "moonshotai/kimi-k2",
    "deepseek/deepseek-r1",
    "anthropic/claude-sonnet-4",
]


@dataclass
class EscalationVerdict:
    """Result of a 3-model panel vote for a single symbol."""

    id: str
    ddd_layer: str
    confidence: float
    agreement: int
    vote_count: int

    @classmethod
    def from_votes(
        cls, sym_id: str, votes: list[ClassificationResult]
    ) -> EscalationVerdict:
        """Compute majority vote from multiple model classifications."""
        if not votes:
            return cls(
                id=sym_id, ddd_layer="?", confidence=0.0, agreement=0, vote_count=0
            )

        layers = [v.ddd_layer for v in votes]
        counts = Counter(layers)
        winner, winner_count = counts.most_common(1)[0]

        if winner_count == 1 and len(counts) > 1:
            winner = "?"
            winner_count = 1

        avg_confidence = sum(v.confidence for v in votes) / len(votes)

        return cls(
            id=sym_id,
            ddd_layer=winner,
            confidence=avg_confidence,
            agreement=winner_count,
            vote_count=len(votes),
        )


def escalate_symbols(
    symbols: list[dict[str, object]],
) -> list[EscalationVerdict]:
    """Run contested symbols through a 3-model panel and return majority verdicts."""
    if not symbols:
        return []

    all_votes: dict[str, list[ClassificationResult]] = {}
    for sym in symbols:
        all_votes[str(sym["id"])] = []

    for model in PANEL_MODELS:
        results = classify_symbols(symbols, model=model)
        for r in results:
            if r.id in all_votes:
                all_votes[r.id].append(r)

    return [
        EscalationVerdict.from_votes(sym_id, votes)
        for sym_id, votes in all_votes.items()
    ]
