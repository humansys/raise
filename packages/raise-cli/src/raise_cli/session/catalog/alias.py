"""Alias generation for runtime sessions — adjective-noun, collision-checked.

Aliases are unique across active (provisioning + live) rows. Exited rows do
not block reuse — the partial unique index enforces this at the DB layer.
"""

from __future__ import annotations

import random
import sqlite3

_ADJECTIVES = [
    "bright",
    "calm",
    "clear",
    "cool",
    "crisp",
    "deep",
    "fair",
    "fast",
    "firm",
    "free",
    "full",
    "glad",
    "gold",
    "good",
    "gray",
    "keen",
    "kind",
    "lean",
    "mild",
    "neat",
    "pale",
    "pure",
    "rich",
    "safe",
    "slim",
    "soft",
    "sure",
    "tall",
    "true",
    "warm",
    "wide",
    "wise",
]

_NOUNS = [
    "bear",
    "bird",
    "boar",
    "buck",
    "bull",
    "carp",
    "colt",
    "crab",
    "crow",
    "dart",
    "deer",
    "dove",
    "duck",
    "eagle",
    "elk",
    "fawn",
    "finch",
    "fish",
    "frog",
    "gull",
    "hare",
    "hawk",
    "ibis",
    "kite",
    "lark",
    "lion",
    "lynx",
    "mink",
    "mole",
    "moth",
    "newt",
    "orca",
    "owl",
    "puma",
    "rook",
    "seal",
    "slug",
    "snipe",
    "stag",
    "swan",
    "teal",
    "vole",
    "wolf",
    "wren",
]

_MAX_RETRIES = 16


class AliasExhaustedError(Exception):
    """Raised when alias generation fails after _MAX_RETRIES attempts."""


def _random_alias() -> str:
    return f"{random.choice(_ADJECTIVES)}-{random.choice(_NOUNS)}"  # noqa: S311


def _alias_is_taken(conn: sqlite3.Connection, alias: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM runtime_sessions WHERE alias = ? AND state IN ('provisioning', 'live')",
        (alias,),
    ).fetchone()
    return row is not None


def generate_alias(conn: sqlite3.Connection) -> str:
    """Return a unique alias not in use by any active runtime session.

    Retries up to _MAX_RETRIES times. Raises AliasExhaustedError if all
    attempts collide (practically impossible with current word list).
    """
    for _ in range(_MAX_RETRIES):
        alias = _random_alias()
        if not _alias_is_taken(conn, alias):
            return alias
    raise AliasExhaustedError(
        f"Could not generate a unique alias after {_MAX_RETRIES} attempts"
    )
