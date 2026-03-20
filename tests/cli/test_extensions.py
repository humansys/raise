"""Tests for CLI extension discovery via entry points."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any
from unittest.mock import patch

import typer

from raise_cli.cli.extensions import discover_cli_extensions


def _make_entry_point(name: str, load_result: Any, dist_name: str = "test-pkg") -> Any:
    """Create a mock entry point with the given name and load result."""
    ep = SimpleNamespace(name=name, load=lambda: load_result)
    ep.dist = SimpleNamespace(name=dist_name)
    return ep


def _make_broken_entry_point(
    name: str, error: Exception, dist_name: str = "bad-pkg"
) -> Any:
    """Create a mock entry point that raises on load."""

    def _raise() -> None:
        raise error

    ep = SimpleNamespace(name=name, load=_raise)
    ep.dist = SimpleNamespace(name=dist_name)
    return ep


class TestDiscoverSuccess:
    """Tests for successful extension loading."""

    def test_valid_typer_app_is_registered(self) -> None:
        """A valid Typer app entry point should be added to the app."""
        ext_app = typer.Typer()
        ep = _make_entry_point("knowledge", ext_app)
        app = typer.Typer()

        with patch("raise_cli.cli.extensions.entry_points", return_value=[ep]):
            results = discover_cli_extensions(app)

        assert len(results) == 1
        assert results[0].name == "knowledge"
        assert results[0].dist == "test-pkg"
        assert results[0].status == "loaded"
        assert results[0].reason is None

    def test_multiple_extensions_registered(self) -> None:
        """Multiple valid extensions should all be registered."""
        ep1 = _make_entry_point("knowledge", typer.Typer(), "pkg-a")
        ep2 = _make_entry_point("deploy", typer.Typer(), "pkg-b")
        app = typer.Typer()

        with patch("raise_cli.cli.extensions.entry_points", return_value=[ep1, ep2]):
            results = discover_cli_extensions(app)

        loaded = [r for r in results if r.status == "loaded"]
        assert len(loaded) == 2


class TestDiscoverErrors:
    """Tests for error handling during extension loading."""

    def test_broken_extension_is_skipped(self) -> None:
        """An entry point that raises on load should be skipped."""
        ep = _make_broken_entry_point("broken", ImportError("No module named 'foo'"))
        app = typer.Typer()

        with patch("raise_cli.cli.extensions.entry_points", return_value=[ep]):
            results = discover_cli_extensions(app)

        assert len(results) == 1
        assert results[0].name == "broken"
        assert results[0].status == "error"
        assert "No module named" in (results[0].reason or "")

    def test_non_typer_object_is_skipped(self) -> None:
        """An entry point that loads a non-Typer object should be skipped."""
        ep = _make_entry_point("not-typer", "a string, not a Typer app")
        app = typer.Typer()

        with patch("raise_cli.cli.extensions.entry_points", return_value=[ep]):
            results = discover_cli_extensions(app)

        assert len(results) == 1
        assert results[0].status == "skipped"
        assert "expected Typer" in (results[0].reason or "")


class TestNoExtensions:
    """Tests for when no extensions are installed."""

    def test_no_entry_points_returns_empty(self) -> None:
        """No entry points should return empty list."""
        app = typer.Typer()

        with patch("raise_cli.cli.extensions.entry_points", return_value=[]):
            results = discover_cli_extensions(app)

        assert results == []
