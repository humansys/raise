"""DDD BC naming — one batched LLM micro-call for semantic BC names.

RAISE-16790. OpenRouter plumbing mirrors classifier.py. All parsing and
prompt-building functions are pure; the LLM caller is injectable so tests
never touch the network.
"""

from __future__ import annotations

import json
import logging
import os
import re
import time
from collections.abc import Callable

from pydantic import BaseModel

from raise_cli.ddd.discover import BCSuggestion

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_NAMING_MODEL: str = "google/gemini-3.7-flash"
_MAX_ATTEMPTS: int = 2
_RETRY_DELAY_S: float = 2.0
_MAX_TOKENS: int = 2000
_MAX_SYMBOL_DISPLAY: int = 8
_MAX_DESCRIPTION_LEN: int = 120
_MAX_NAME_WORDS: int = 3

# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------

LlmCaller = Callable[[str], str]


# ---------------------------------------------------------------------------
# Pydantic model for one LLM response entry
# ---------------------------------------------------------------------------


class BCNameProposal(BaseModel):
    """One entry of the LLM's JSON-array response."""

    index: int
    name: str
    description: str = ""


# ---------------------------------------------------------------------------
# Pure helpers
# ---------------------------------------------------------------------------


def _symbol_display_name(symbol_id: str) -> str:
    """'sym-raise_cli.ddd.discover.discover_bcs' -> 'discover_bcs'.

    Strips the 'sym-' prefix and takes the last dot-delimited segment.
    """
    without_prefix = symbol_id.removeprefix("sym-")
    return without_prefix.rsplit(".", 1)[-1]


def _normalize_name(raw: str) -> str:
    """Lowercase and replace spaces (and underscores) with hyphens."""
    return raw.strip().lower().replace(" ", "-").replace("_", "-")


def _name_word_count(name: str) -> int:
    """Count words in a (possibly already normalized) name.

    We split on hyphens and spaces after stripping, so 'session-lifecycle'
    and 'Session Lifecycle' both count as 2.
    """
    return len(re.split(r"[-\s]+", name.strip()))


def build_naming_prompt(suggestions: list[BCSuggestion]) -> str:
    """Pure. Render all BC clusters into a single numbered prompt for the LLM."""
    n = len(suggestions)
    lines: list[str] = [
        f"Below are {n} Bounded Context candidates discovered by static analysis of a codebase.",
        "For EACH candidate, propose:",
        '- "name": 1-3 words of ubiquitous business language, lowercase, hyphen-joined',
        '  (e.g. "session-lifecycle", "backlog-sync"). Name the business capability,',
        "  not the file layout. Names must be unique across candidates.",
        '- "description": one line, at most 12 words.',
        "",
        "Respond ONLY with a JSON array, no prose:",
        '[{"index": 0, "name": "...", "description": "..."}, ...]',
        "",
    ]

    for i, s in enumerate(suggestions):
        # Module stems: split the static name on "+"
        stems = s.name.split("+") if "+" in s.name else [s.name]
        stems_str = ", ".join(stems)

        # Representative symbols: first _MAX_SYMBOL_DISPLAY display names
        display_syms = [
            _symbol_display_name(sid) for sid in s.symbols[:_MAX_SYMBOL_DISPLAY]
        ]
        syms_str = ", ".join(display_syms) if display_syms else "(none)"

        lines.append(f"Candidate {i}:")
        lines.append(f"  current static name: {s.name}")
        lines.append(f"  modules: {stems_str}")
        lines.append(
            f"  symbol count: {len(s.symbols)}  confidence: {s.confidence:.2f}"
        )
        lines.append(f"  representative symbols: {syms_str}")
        lines.append(f"  evidence: {s.rationale}")
        lines.append("")

    return "\n".join(lines)


def _strip_markdown_fences(text: str) -> str:
    """Remove ```json ... ``` fences if present (mirrors classifier.py)."""
    return re.sub(r"```(?:json)?\s*\n?", "", text).strip()


def _parse_naming_response(text: str) -> list[BCNameProposal]:
    """Pure. Strip markdown fences, parse JSON array, skip malformed entries.

    Returns [] on unparseable input (mirrors classifier._parse_*).
    """
    cleaned = _strip_markdown_fences(text)
    try:
        items = json.loads(cleaned)
    except (json.JSONDecodeError, ValueError):
        logger.warning("Failed to parse naming response as JSON")
        return []

    if not isinstance(items, list):
        logger.warning("Naming response is not a list: %s", type(items))
        return []

    results: list[BCNameProposal] = []
    for item in items:
        try:
            results.append(BCNameProposal.model_validate(item))
        except Exception:  # noqa: BLE001
            logger.debug("Skipping malformed naming entry: %s", item)
    return results


# ---------------------------------------------------------------------------
# Real OpenRouter caller builder
# ---------------------------------------------------------------------------


def _default_llm_caller(model: str) -> LlmCaller | None:
    """Build the real OpenRouter caller, or None when OPENROUTER_API_KEY is absent.

    openai is imported lazily inside (classifier.py pattern).
    """
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        return None

    import openai

    client = openai.OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
    )

    def _call(prompt: str) -> str:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a domain-driven design expert who names bounded contexts in ubiquitous language.",
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=_MAX_TOKENS,
        )
        return response.choices[0].message.content or ""

    return _call


# ---------------------------------------------------------------------------
# Internal: retry helper and proposal application
# ---------------------------------------------------------------------------


def _invoke_with_retry(
    caller: LlmCaller,
    prompt: str,
) -> list[BCNameProposal]:
    """Call the LLM caller up to _MAX_ATTEMPTS times, returning parsed proposals.

    Returns [] if all attempts fail or return unparseable/empty responses.
    """
    proposals: list[BCNameProposal] = []
    last_exc: Exception | None = None

    for attempt in range(1, _MAX_ATTEMPTS + 1):
        try:
            raw = caller(prompt)
            proposals = _parse_naming_response(raw)
            if proposals:
                return proposals
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
            proposals = []

        if attempt < _MAX_ATTEMPTS:
            logger.warning(
                "BC naming attempt %d/%d returned no results%s — retrying",
                attempt,
                _MAX_ATTEMPTS,
                f" ({last_exc})" if last_exc else "",
            )
            time.sleep(_RETRY_DELAY_S)

    logger.warning(
        "BC naming failed after %d attempt(s)%s — keeping static names",
        _MAX_ATTEMPTS,
        f": {last_exc}" if last_exc else "",
    )
    return []


def _apply_proposals(
    suggestions: list[BCSuggestion],
    proposals: list[BCNameProposal],
) -> list[BCSuggestion]:
    """Apply validated proposals to a copy of suggestions.

    Per-entry rules: index bounds, non-empty name, ≤ _MAX_NAME_WORDS,
    and cross-BC uniqueness (first wins on duplicate).
    """
    result = list(suggestions)
    # Pre-seed with existing static names so LLM proposals can't collide with them.
    accepted_names: set[str] = {_normalize_name(s.name) for s in suggestions}

    for proposal in proposals:
        idx = proposal.index
        if idx < 0 or idx >= len(suggestions):
            logger.debug("Ignoring out-of-range naming proposal index %d", idx)
            continue

        raw_name = proposal.name.strip()
        if not raw_name:
            logger.debug("Ignoring empty name for index %d", idx)
            continue

        normalized = _normalize_name(raw_name)
        # Word-count and slug check on the normalized form (catches snake_case proposals).
        if _name_word_count(normalized) > _MAX_NAME_WORDS:
            logger.debug("Ignoring overlong name %r for index %d", raw_name, idx)
            continue
        if not re.fullmatch(r"[a-z][a-z0-9-]*", normalized):
            logger.debug("Ignoring non-slug name %r for index %d", normalized, idx)
            continue

        if normalized in accepted_names:
            logger.debug("Ignoring duplicate name %r for index %d", normalized, idx)
            continue

        accepted_names.add(normalized)
        description = (
            proposal.description[:_MAX_DESCRIPTION_LEN]
            if proposal.description
            else None
        )
        result[idx] = suggestions[idx].model_copy(
            update={
                "name": normalized,
                "description": description,
                "name_source": "llm_suggested",
            }
        )

    return result


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def name_bcs_with_llm(
    suggestions: list[BCSuggestion],
    *,
    model: str = DEFAULT_NAMING_MODEL,
    call_llm: LlmCaller | None = None,
) -> list[BCSuggestion]:
    """Return a NEW list of BCSuggestion with LLM names applied.

    - Exactly one LLM call for all suggestions (retried once on failure).
    - Never raises: any failure path returns the input suggestions
      unchanged (name_source stays "static") after logging a warning.
    - Input list/objects are not mutated; replaced entries are built with
      model_copy(update={...}).
    """
    if not suggestions:
        return suggestions

    caller = call_llm if call_llm is not None else _default_llm_caller(model)
    if caller is None:
        logger.warning("OPENROUTER_API_KEY not set — keeping static BC names")
        return suggestions

    prompt = build_naming_prompt(suggestions)
    proposals = _invoke_with_retry(caller, prompt)
    if not proposals:
        return suggestions

    return _apply_proposals(suggestions, proposals)
