"""Test package metadata."""

from __future__ import annotations

import rai_cli


def test_version() -> None:
    """Test that version is defined and follows semver format."""
    assert rai_cli.__version__ is not None
    parts = rai_cli.__version__.split(".")
    assert len(parts) >= 2, f"Version '{rai_cli.__version__}' does not look like semver"


def test_author() -> None:
    """Test that author is defined."""
    assert rai_cli.__author__ == "Emilio Osorio"


def test_license() -> None:
    """Test that license is defined."""
    assert rai_cli.__license__ == "MIT"
