"""Test package metadata."""

from __future__ import annotations

import raise_cli


def test_version() -> None:
    """Test that version is defined and follows semver format."""
    assert raise_cli.__version__ is not None
    parts = raise_cli.__version__.split(".")
    assert len(parts) >= 2, (
        f"Version '{raise_cli.__version__}' does not look like semver"
    )


def test_author() -> None:
    """Test that author is defined."""
    assert raise_cli.__author__ == "Emilio Osorio"


def test_license() -> None:
    """Test that license is defined."""
    assert raise_cli.__license__ == "MIT"
