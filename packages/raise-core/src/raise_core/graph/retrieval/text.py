"""Shared lexical helpers for retrieval scoring.

Single source of truth for stop words, keyword extraction, and domain expansion.
Used by both the engine (attribute_match, retrieve) and cartridges (GenericCartridgeAdapter).
"""

from __future__ import annotations

# Function words excluded from scoring — they inflate match counts without semantic signal.
# Callers that need a fallback-to-raw (e.g. adapter seeding) must implement it themselves.
STOP_WORDS: frozenset[str] = frozenset(
    {
        "a",
        "an",
        "and",
        "are",
        "as",
        "at",
        "be",
        "by",
        "do",
        "does",
        "for",
        "from",
        "how",
        "in",
        "is",
        "it",
        "of",
        "on",
        "or",
        "that",
        "the",
        "this",
        "to",
        "what",
        "when",
        "where",
        "which",
        "who",
        "why",
        "with",
        "you",
        "your",
    }
)

_PUNCT = "?!.,;:\"'()"


_MAX_EXPANSIONS_PER_TERM: int = 3


def _stem_simple(token: str) -> str:
    """Minimal English stemming: plural → singular only."""
    if len(token) > 3 and token.endswith("ies"):
        return token[:-3] + "y"
    if len(token) > 4 and (
        token.endswith("ses") or token.endswith("xes") or token.endswith("zes")
    ):
        return token[:-2]
    if len(token) > 5 and (token.endswith("shes") or token.endswith("ches")):
        return token[:-2]
    if len(token) > 3 and token.endswith("s") and not token.endswith("ss"):
        return token[:-1]
    return token


def extract_keywords(query: str) -> list[str]:
    """Lowercase, strip edge punctuation, drop stop words.

    Returns content-bearing tokens only. Returns empty list when all tokens
    are stop words — callers decide whether to fallback to raw (adapter seeding
    does; engine scoring does not).
    """
    if not query:
        return []
    tokens = [t.strip(_PUNCT) for t in query.lower().split() if t.strip(_PUNCT)]
    return [t for t in tokens if t and t not in STOP_WORDS]


def expand_keywords(
    keywords: list[str],
    synonyms: dict[str, frozenset[str]] | None = None,
) -> tuple[list[str], set[str]]:
    """Expand keywords with stemming and optional domain synonyms.

    Returns (all_keywords, expanded_set) where expanded_set contains only the
    added terms (not originals). Callers can weight expanded terms lower.
    When synonyms is None, only stemming is applied.
    """
    originals = set(keywords)
    expanded: set[str] = set()
    syn_map = synonyms or {}

    for kw in keywords:
        stemmed = _stem_simple(kw)
        if stemmed != kw and stemmed not in originals:
            expanded.add(stemmed)

        lookup = stemmed if stemmed in syn_map else kw
        if lookup in syn_map:
            for syn in list(syn_map[lookup])[:_MAX_EXPANSIONS_PER_TERM]:
                if syn not in originals:
                    expanded.add(syn)

    return keywords + sorted(expanded), expanded
