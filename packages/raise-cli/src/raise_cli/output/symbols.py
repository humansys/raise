"""Terminal-safe output symbols with ASCII fallbacks for non-Unicode terminals.

On Windows with legacy CP1252 codepage, Unicode symbols like ✓, ✗, ⚠ raise
UnicodeEncodeError. This module detects terminal encoding and provides ASCII
fallbacks automatically.

Example:
    >>> from raise_cli.output.symbols import CHECK, CROSS, WARN, ARROW, BULLET
    >>> print(f"{CHECK} Done")
    ✓ Done   # or [ok] Done on CP1252 terminals
"""

from __future__ import annotations

import sys


def _is_utf8(encoding: str | None = None) -> bool:
    enc = encoding or getattr(sys.stdout, "encoding", None) or "utf-8"
    return "utf" in enc.lower()


def get_symbols(encoding: str | None = None) -> tuple[str, str, str]:
    """Return (CHECK, CROSS, WARN) symbols appropriate for the given encoding.

    Args:
        encoding: Terminal encoding to check. Defaults to sys.stdout.encoding.

    Returns:
        Tuple of (check, cross, warn) symbols — Unicode or ASCII fallbacks.

    Example:
        >>> get_symbols("utf-8")
        ('✓', '✗', '⚠')
        >>> get_symbols("cp1252")
        ('[ok]', '[x]', '[!]')
    """
    if _is_utf8(encoding):
        return ("✓", "✗", "⚠")
    return ("[ok]", "[x]", "[!]")


CHECK, CROSS, WARN = get_symbols()
ARROW = "→" if _is_utf8() else "->"
BULLET = "•" if _is_utf8() else "*"
PLAY = "▶" if _is_utf8() else ">"
PAUSE = "⏸" if _is_utf8() else "||"
BIDIR = "↔" if _is_utf8() else "<->"

__all__ = [
    "CHECK",
    "CROSS",
    "WARN",
    "ARROW",
    "BULLET",
    "PLAY",
    "PAUSE",
    "BIDIR",
    "get_symbols",
]
