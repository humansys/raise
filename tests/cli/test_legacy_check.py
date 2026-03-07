"""Tests for RAISE-482: detect co-installed legacy packages.

Verifies that check_legacy_packages() detects old rai-cli/rai-core
packages and returns actionable warning messages.
"""

from __future__ import annotations

from unittest.mock import patch

from raise_cli.compat import check_legacy_packages


def _mock_version(name: str) -> str:
    """Simulate old packages being installed."""
    if name in ("rai-cli", "rai-core"):
        return "2.1.0"
    raise PackageNotFoundError(name)


class PackageNotFoundError(Exception):
    """Stand-in for importlib.metadata.PackageNotFoundError."""


def test_returns_none_when_no_legacy_packages() -> None:
    """No warning when legacy packages are not installed."""
    from importlib.metadata import PackageNotFoundError as RealError

    def _no_legacy(name: str) -> str:
        raise RealError(name)

    with patch("raise_cli.compat.version", side_effect=_no_legacy):
        result = check_legacy_packages()
    assert result is None


def test_detects_rai_cli_legacy() -> None:
    """Warning when rai-cli (old name) is co-installed."""
    from importlib.metadata import PackageNotFoundError as RealError

    def _only_cli(name: str) -> str:
        if name == "rai-cli":
            return "2.1.0"
        raise RealError(name)

    with patch("raise_cli.compat.version", side_effect=_only_cli):
        result = check_legacy_packages()
    assert result is not None
    assert "rai-cli" in result
    assert "pip uninstall" in result


def test_detects_rai_core_legacy() -> None:
    """Warning when rai-core (old name) is co-installed."""
    from importlib.metadata import PackageNotFoundError as RealError

    def _only_core(name: str) -> str:
        if name == "rai-core":
            return "2.1.0"
        raise RealError(name)

    with patch("raise_cli.compat.version", side_effect=_only_core):
        result = check_legacy_packages()
    assert result is not None
    assert "rai-core" in result


def test_detects_both_legacy() -> None:
    """Warning includes both packages when both are co-installed."""
    from importlib.metadata import PackageNotFoundError as RealError

    def _both(name: str) -> str:
        if name == "rai-cli":
            return "2.1.0"
        if name == "rai-core":
            return "2.1.0"
        raise RealError(name)

    with patch("raise_cli.compat.version", side_effect=_both):
        result = check_legacy_packages()
    assert result is not None
    assert "rai-cli" in result
    assert "rai-core" in result
    assert "pip uninstall" in result
