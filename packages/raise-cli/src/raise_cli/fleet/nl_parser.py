"""Bilingual natural-language command parser for FleetDirectorChat.

Pure module — no MCP imports, no state changes, no subprocess calls.
Recognizes approve / pause / relaunch commands in Spanish and English.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------

Action = Literal["approve", "pause", "relaunch"]


@dataclass(frozen=True)
class ParsedIntent:
    """Parsed result of a fleet chat command."""

    action: Action
    story_key: str
    model: str | None


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Valid short model names (mirrors VALID_MODELS in subagent_dispatcher / frontmatter)
VALID_MODELS: frozenset[str] = frozenset({"haiku", "sonnet", "opus", "fable"})

# Verb lexicon: ES+EN verbs mapped to canonical action.
# Each entry is (regex_fragment, canonical_action).  Order within a family
# does not matter — we compile one pattern per action family.
_VERB_LEXICON: dict[Action, tuple[str, ...]] = {
    "approve": ("aprueba", "aprobar", "approve"),
    "pause": ("pausa", "pausar", "pause"),
    "relaunch": ("relanza", "relanzar", "relaunch"),
}

# Story key pattern: one or more uppercase letters/digits/underscores, dash, digits.
_KEY_FRAGMENT = r"([A-Z][A-Z0-9_]*-\d+)"

# Optional model suffix: "con <model>" (ES) or "with <model>" (EN).
_MODEL_FRAGMENT = r"(?:(?:con|with)\s+(\w+))?"

# Compile one pattern per action:
#   verb ... KEY ... optional_model_suffix
_PATTERNS: list[tuple[Action, re.Pattern[str]]] = [
    (
        action,
        re.compile(
            rf"\b(?:{'|'.join(re.escape(v) for v in verbs)})\s+{_KEY_FRAGMENT}\s*{_MODEL_FRAGMENT}",
            re.IGNORECASE,
        ),
    )
    for action, verbs in _VERB_LEXICON.items()
]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def parse_command(text: str) -> ParsedIntent | None:
    """Parse a fleet chat command into a ParsedIntent.

    Args:
        text: Raw user input string (Spanish or English).

    Returns:
        ParsedIntent if a known command is recognised, None otherwise.
    """
    stripped = text.strip()
    if not stripped:
        return None

    for action, pattern in _PATTERNS:
        m = pattern.search(stripped)
        if m is None:
            continue

        story_key = m.group(1).upper()
        raw_model = m.group(2) if m.lastindex and m.lastindex >= 2 else None
        model: str | None = (
            raw_model.lower()
            if raw_model and raw_model.lower() in VALID_MODELS
            else None
        )

        return ParsedIntent(action=action, story_key=story_key, model=model)

    return None
