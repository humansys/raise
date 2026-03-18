"""Regression tests for RAISE-554 — Unicode symbols crash on CP1252 terminals."""

from __future__ import annotations

from raise_cli.output.symbols import CHECK, CROSS, WARN, get_symbols


def test_unicode_symbols_on_utf8_terminal() -> None:
    check, cross, warn = get_symbols("utf-8")
    assert check == "✓"
    assert cross == "✗"
    assert warn == "⚠"


def test_ascii_fallbacks_on_cp1252_terminal() -> None:
    check, cross, warn = get_symbols("cp1252")
    assert check != "✓"
    assert cross != "✗"
    assert warn != "⚠"


def test_ascii_fallbacks_are_encodable_in_cp1252() -> None:
    """Symbols returned for CP1252 must not raise UnicodeEncodeError."""
    check, cross, warn = get_symbols("cp1252")
    for sym in (check, cross, warn):
        sym.encode("cp1252")  # must not raise


def test_ascii_fallbacks_on_ascii_terminal() -> None:
    check, cross, warn = get_symbols("ascii")
    for sym in (check, cross, warn):
        sym.encode("ascii")  # must not raise


def test_module_constants_are_strings() -> None:
    """Module-level constants must be importable strings."""
    assert isinstance(CHECK, str)
    assert isinstance(CROSS, str)
    assert isinstance(WARN, str)
