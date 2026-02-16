"""Test package metadata."""

from __future__ import annotations

import rai_cli


def test_version() -> None:
    """Test that version is defined."""
    assert rai_cli.__version__ == "2.0.0a8"


def test_author() -> None:
    """Test that author is defined."""
    assert rai_cli.__author__ == "Emilio Osorio"


def test_license() -> None:
    """Test that license is defined."""
    assert rai_cli.__license__ == "MIT"
