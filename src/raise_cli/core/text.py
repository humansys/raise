"""Text processing utilities.

Shared functions for text manipulation used across the codebase.
"""

from __future__ import annotations

import re


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
