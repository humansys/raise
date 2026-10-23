"""DDD classification engine — OpenRouter invocation + response parsing."""

from __future__ import annotations

import json
import logging
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Literal

from pydantic import BaseModel, field_validator

from raise_cli.ddd.heuristics import build_classification_prompt

logger = logging.getLogger(__name__)

DddLayer = Literal["D", "I", "?"]


class ClassificationResult(BaseModel):
    """Structured output from the DDD classifier."""

    id: str
    ddd_layer: DddLayer
    confidence: float
    reasoning: str
    heuristics: dict[str, str] | list[str]

    @field_validator("heuristics", mode="before")
    @classmethod
    def _coerce_heuristics(cls, v: object) -> dict[str, str] | list[str]:
        if isinstance(v, list):
            return {str(item): "" for item in v}
        return v  # type: ignore[return-value]

    @field_validator("confidence")
    @classmethod
    def _clamp_confidence(cls, v: float) -> float:
        return max(0.0, min(1.0, v))


def _strip_markdown_fences(text: str) -> str:
    """Remove ```json ... ``` fences if present."""
    return re.sub(r"```(?:json)?\s*\n?", "", text).strip()


def _extract_json_payload(text: str) -> Any:
    """Extract JSON array or object with 'classifications' key from LLM output."""
    cleaned = _strip_markdown_fences(text)
    parsed = json.loads(cleaned)
    if isinstance(parsed, list):
        return parsed
    if isinstance(parsed, dict) and "classifications" in parsed:
        return parsed["classifications"]
    return parsed


def _parse_classification_response(text: str) -> list[ClassificationResult]:
    """Parse LLM response text into ClassificationResult list.

    Handles: valid JSON array, JSON object with 'classifications' key,
    markdown-fenced JSON, malformed JSON (returns []), and partial results
    (keeps valid entries, skips malformed).
    """
    try:
        items = _extract_json_payload(text)
    except (json.JSONDecodeError, ValueError):
        logger.warning("Failed to parse classification response as JSON")
        return []

    if not isinstance(items, list):
        logger.warning("Classification response is not a list: %s", type(items))
        return []

    results: list[ClassificationResult] = []
    for item in items:
        try:
            results.append(ClassificationResult.model_validate(item))
        except Exception:  # noqa: BLE001
            logger.debug("Skipping malformed classification entry: %s", item)
    return results


BATCH_SIZE = 200
MAX_WORKERS = 4

# RAISE-16610 model eval, production run 2026-08-26: 5/21 batches (24%)
# returned zero results with no retry, silently dropping 1,012 symbols.
# Diagnostic testing ruled out max_tokens/reasoning-budget as the cause
# (identical content succeeded on direct retest) -- treated as transient
# failure under parallel load, not a prompt or parameter problem.
_MAX_ATTEMPTS = 3
_RETRY_DELAY_S = 2.0


def _classify_batch(
    symbols: list[dict[str, object]],
    client: Any,
    model: str,
    *,
    domain_context: str | None = None,
) -> list[ClassificationResult]:
    """Classify a single batch of symbols via one LLM call.

    Retries up to _MAX_ATTEMPTS times on exception or on a parsed-empty
    result for a non-empty batch (RAISE-16610 follow-up: production runs
    showed ~24% of batches failing transiently with no retry).
    """
    if not symbols:
        return []

    prompt = build_classification_prompt(symbols, domain_context=domain_context)
    last_exc: Exception | None = None

    for attempt in range(1, _MAX_ATTEMPTS + 1):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a DDD classification expert.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=32768,
            )
            text = response.choices[0].message.content or ""
            results = _parse_classification_response(text)
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
            results = []

        if results:
            return results

        if attempt < _MAX_ATTEMPTS:
            logger.warning(
                "DDD classifier (%s) batch attempt %d/%d returned no results%s "
                "-- retrying",
                model,
                attempt,
                _MAX_ATTEMPTS,
                f" ({last_exc})" if last_exc else "",
            )
            time.sleep(_RETRY_DELAY_S)

    logger.warning(
        "DDD classifier (%s) failed after %d attempts%s",
        model,
        _MAX_ATTEMPTS,
        f": {last_exc}" if last_exc else "",
    )
    return []


def classify_symbols(
    symbols: list[dict[str, object]],
    *,
    model: str = "google/gemini-3.7-flash",
    batch_size: int = BATCH_SIZE,
    domain_context: str | None = None,
) -> list[ClassificationResult]:
    """Classify symbols via OpenRouter, batching to fit context limits.

    Default model (2026-08-26): Gemini 3.7 Flash, promoted from
    moonshotai/kimi-k2 after a 200-symbol ground-truth eval showed 92.5% vs
    84.0% accuracy at 5.3x the speed. Cost at eval time looked comparable but
    was running on a launch promo (~50% off list per OpenRouter's own UI,
    not visible via the pricing API) — post-promo it's plausibly *more*
    expensive than K2. Justify this default by accuracy + speed, not cost.
    See work/epics/e16503-ddd-brownfield-analyzer/evidence/model-eval-2026-08-26.md.
    """
    if not symbols:
        return []

    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        logger.warning("OPENROUTER_API_KEY not set — DDD classifier unavailable")
        return []

    import openai

    client = openai.OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
    )

    batches = [symbols[i : i + batch_size] for i in range(0, len(symbols), batch_size)]
    total_batches = len(batches)
    workers = min(MAX_WORKERS, total_batches)
    print(
        f"  Classifying {len(symbols)} symbols in {total_batches} batches"
        f" ({workers} parallel workers)",
        file=sys.stderr,
        flush=True,
    )

    indexed_results: list[tuple[int, list[ClassificationResult]]] = []

    def _run(
        idx: int, batch: list[dict[str, object]]
    ) -> tuple[int, list[ClassificationResult]]:
        results = _classify_batch(batch, client, model, domain_context=domain_context)
        print(
            f"  Batch {idx + 1}/{total_batches} → {len(results)}/{len(batch)} classified",
            file=sys.stderr,
            flush=True,
        )
        return idx, results

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {
            pool.submit(_run, idx, batch): idx for idx, batch in enumerate(batches)
        }
        for future in as_completed(futures):
            indexed_results.append(future.result())

    indexed_results.sort(key=lambda t: t[0])
    all_results: list[ClassificationResult] = []
    for _, results in indexed_results:
        all_results.extend(results)

    return all_results
