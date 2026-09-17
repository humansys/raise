"""Tactical escalation panel — 3-model majority vote for low-confidence symbols.

Implements RAISE-16917 (D1, D2):
  - Collects low-confidence D-layer symbols from a ddd-type artifact.
  - Runs each symbol through a 3-model panel using the tactical classification
    prompt (`build_tactical_classification_prompt`).
  - Aggregates results by majority vote; three-way tie resolved by primary model.
  - Returns TacticalEscalationVerdict list for HITL HTML rendering.

Panel models (K3 + Sol + Fable — higher-capability than BC-discovery panel):
  - moonshotai/kimi-k3  (primary; tiebreaker)
  - openai/gpt-5.6-sol
  - anthropic/claude-fable-5

NOTE: If a model is unavailable on OpenRouter at deployment time, substitute
with the nearest available tier (e.g. openai/gpt-5.5 or anthropic/claude-opus-5)
and document the substitution in the TACTICAL_PANEL_MODELS list.

Architecture references: D1, D2, D6 (design.md, RAISE-16917).
"""

from __future__ import annotations

import logging
import os
from collections import Counter
from dataclasses import dataclass, field
from typing import Any

from raise_cli.ddd.tactical import TacticalClassification, TacticalType
from raise_cli.ddd.tactical_prompts import build_tactical_classification_prompt
from raise_cli.ddd.type_cmd import (
    _parse_tactical_response,  # type: ignore[attr-defined]
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

TACTICAL_ESCALATION_THRESHOLD: float = 0.75

TACTICAL_PANEL_MODELS: list[str] = [
    "moonshotai/kimi-k3",  # primary / tiebreaker
    "openai/gpt-5.6-sol",
    "anthropic/claude-fable-5",
]

# ---------------------------------------------------------------------------
# Public data model
# ---------------------------------------------------------------------------


@dataclass
class TacticalEscalationVerdict:
    """Result of a 3-model panel vote for a single symbol.

    Attributes:
        symbol_id: Symbol identifier (matches artifact classification key).
        tactical_type: Majority-vote winner (primary model as tiebreaker).
        confidence: Arithmetic mean of per-model confidences for the symbol.
        agreement: Number of models that voted for the winning type.
        vote_count: Total models that returned a usable result.
        per_model: Per-model TacticalClassification keyed by model identifier.
    """

    symbol_id: str
    tactical_type: TacticalType
    confidence: float
    agreement: int
    vote_count: int
    per_model: dict[str, TacticalClassification] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _classify_tactical_batch(
    symbols: list[dict[str, Any]],
    model: str,
    client: Any,
) -> list[TacticalClassification]:
    """Classify a batch of symbols via one LLM call (single attempt, no retry).

    This function is intentionally thin so it can be monkey-patched in tests.

    Args:
        symbols: Symbol dicts in prompt-builder format.
        model: OpenRouter model identifier.
        client: OpenAI-compatible client instance.

    Returns:
        List of TacticalClassification objects. Empty on failure or empty input.
    """
    if not symbols:
        return []

    prompt = build_tactical_classification_prompt(symbols)
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a DDD tactical classification expert. "
                        "Follow the heuristics exactly and return only the "
                        "JSON array — no markdown, no explanation."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=32768,
        )
        text: str = response.choices[0].message.content or ""
        return _parse_tactical_response(text)
    except Exception:  # noqa: BLE001
        logger.warning(
            "Model %s returned an error for tactical escalation batch", model
        )
        return []


def _build_verdict(
    symbol_id: str,
    per_model: dict[str, TacticalClassification],
    primary_model: str,
) -> TacticalEscalationVerdict:
    """Aggregate per-model results into a single verdict via majority vote.

    Three-way tie rule (anti-abstention): when all models disagree, the primary
    model's classification wins (not "?" — tactical types require a concrete answer).

    Args:
        symbol_id: Symbol identifier.
        per_model: Dict of model → TacticalClassification for this symbol.
        primary_model: Model identifier used as tiebreaker (index 0 in panel list).

    Returns:
        TacticalEscalationVerdict with majority winner and averaged confidence.
    """
    if not per_model:
        # No models returned a result — produce a fallback verdict
        return TacticalEscalationVerdict(
            symbol_id=symbol_id,
            tactical_type=TacticalType.entity,
            confidence=0.0,
            agreement=0,
            vote_count=0,
            per_model={},
        )

    vote_count = len(per_model)
    counts: Counter[TacticalType] = Counter(
        cls.tactical_type for cls in per_model.values()
    )
    winner_type, winner_count = counts.most_common(1)[0]

    # Three-way tie: every model voted differently (winner_count == 1, len(counts) == vote_count)
    # Use primary model's result as tiebreaker (anti-abstention: no "?" for tactical types)
    if (
        winner_count == 1
        and len(counts) == vote_count
        and vote_count > 1
        and primary_model in per_model
    ):
        winner_type = per_model[primary_model].tactical_type
        # winner_count stays 1

    avg_confidence = sum(cls.confidence for cls in per_model.values()) / vote_count

    return TacticalEscalationVerdict(
        symbol_id=symbol_id,
        tactical_type=winner_type,
        confidence=avg_confidence,
        agreement=winner_count,
        vote_count=vote_count,
        per_model=per_model,
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def escalate_tactical_symbols(
    symbols: list[dict[str, Any]],
    *,
    models: list[str] = TACTICAL_PANEL_MODELS,
    api_key: str | None = None,
) -> list[TacticalEscalationVerdict]:
    """Run a 3-model panel escalation on contested tactical symbols.

    Each symbol is classified by all models in *models*. Per-model results are
    aggregated by majority vote; ties are broken by the first model in the list
    (primary model, typically kimi-k3).

    Empty *symbols* returns [] immediately without making any LLM calls.

    Args:
        symbols: List of symbol dicts (id, kind, signature, module, file, line).
                 Expected to already be filtered to ``confidence < threshold``
                 by the CLI handler (D6 — threshold lives at CLI level only).
        models: Panel model identifiers (default: TACTICAL_PANEL_MODELS).
                Must have at least one entry; first entry is primary/tiebreaker.
        api_key: OpenRouter API key. Falls back to OPENROUTER_API_KEY env var.

    Returns:
        List of TacticalEscalationVerdict (one per input symbol, in input order).
        Symbols for which every model fails are returned with vote_count=0 and
        the primary model's type as a fallback.
    """
    if not symbols:
        return []

    resolved_key = api_key or os.environ.get("OPENROUTER_API_KEY", "")
    primary_model = models[0] if models else ""

    # Build client (lazy import to avoid circular / heavy import at module load)
    import openai  # noqa: PLC0415

    client = openai.OpenAI(
        api_key=resolved_key,
        base_url="https://openrouter.ai/api/v1",
    )

    # Run each model and collect per-symbol results
    # Structure: per_symbol[symbol_id][model_id] = TacticalClassification
    per_symbol: dict[str, dict[str, TacticalClassification]] = {
        sym["id"]: {}
        for sym in symbols  # type: ignore[index]
    }

    for model in models:
        results = _classify_tactical_batch(symbols, model, client)
        for cls in results:
            if cls.symbol_id in per_symbol:
                per_symbol[cls.symbol_id][model] = cls

    # Build verdicts preserving input order
    verdicts: list[TacticalEscalationVerdict] = []
    for sym in symbols:
        sym_id: str = sym["id"]  # type: ignore[assignment]
        verdict = _build_verdict(sym_id, per_symbol[sym_id], primary_model)
        verdicts.append(verdict)

    return verdicts
