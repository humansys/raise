"""Text processing utilities.

Shared functions for text manipulation used across the codebase.
"""

from __future__ import annotations

import re

# Common English stopwords for keyword extraction
STOPWORDS: frozenset[str] = frozenset(
    {
        # Articles and conjunctions
        "the",
        "a",
        "an",
        "and",
        "or",
        "but",
        # Prepositions
        "in",
        "on",
        "at",
        "to",
        "for",
        "of",
        "with",
        "from",
        "by",
        # Demonstratives
        "this",
        "that",
        "these",
        "those",
        # Be verbs
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "being",
        # Modal verbs (governance keywords)
        "must",
        "should",
        "will",
        "can",
        "may",
    }
)


def extract_keywords(text: str) -> set[str]:
    """Extract meaningful keywords from text.

    Filters out stopwords and keeps only words longer than 3 characters.

    Args:
        text: Text to extract keywords from.

    Returns:
        Set of lowercase keywords.

    Examples:
        >>> keywords = extract_keywords("The system MUST validate inputs")
        >>> "system" in keywords
        True
        >>> "the" in keywords
        False
    """
    words = re.findall(r"\b\w+\b", text.lower())
    return {w for w in words if len(w) > 3 and w not in STOPWORDS}


def sanitize_id(name: str) -> str:
    """Sanitize a name for use as an ID.

    Converts a human-readable name to a lowercase, hyphen-separated
    identifier suitable for use in IDs and keys.

    Args:
        name: Human-readable name to sanitize.

    Returns:
        Sanitized ID string (lowercase, hyphens, alphanumeric only).

    Examples:
        >>> sanitize_id("Context Generation (MVC)")
        'context-generation-mvc'
        >>> sanitize_id("Governance as Code")
        'governance-as-code'
        >>> sanitize_id("Hello, World!")
        'hello-world'
    """
    # Convert to lowercase
    sanitized = name.lower()
    # Replace spaces with hyphens
    sanitized = sanitized.replace(" ", "-")
    # Remove all non-alphanumeric characters except hyphens
    sanitized = re.sub(r"[^a-z0-9-]", "", sanitized)
    # Collapse multiple hyphens into one
    sanitized = re.sub(r"-+", "-", sanitized)
    # Remove leading/trailing hyphens
    sanitized = sanitized.strip("-")

    return sanitized
