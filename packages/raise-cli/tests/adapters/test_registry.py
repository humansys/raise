"""Tests for adapter entry point registry."""

from __future__ import annotations

import logging
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from raise_cli.adapters.registry import (
    EP_GOVERNANCE_PARSERS,
    EP_PM_ADAPTERS,
    _discover,
    get_governance_parsers,
    get_graph_backends,
    get_pm_adapters,
)

# --- Helpers ---


def _make_entry_point(name: str, load_result: Any) -> MagicMock:
    """Create a mock entry point that returns load_result on load()."""
    ep = MagicMock()
    ep.name = name
    ep.load.return_value = load_result
    return ep


def _make_broken_entry_point(name: str, error: Exception) -> MagicMock:
    """Create a mock entry point that raises on load()."""
    ep = MagicMock()
    ep.name = name
    ep.load.side_effect = error
    return ep


# --- _discover behavior ---


class TestDiscover:
    def test_returns_empty_dict_for_unknown_group(self) -> None:
        result = _discover("rai.nonexistent.group")
        assert result == {}

    def test_loads_single_entry_point(self) -> None:
        fake_cls = type("FakeAdapter", (), {})
        mock_ep = _make_entry_point("test_adapter", fake_cls)

        with patch("raise_cli.adapters.registry.entry_points", return_value=[mock_ep]):
            result = _discover("rai.adapters.pm")

        assert result == {"test_adapter": fake_cls}

    def test_loads_multiple_entry_points(self) -> None:
        cls_a = type("AdapterA", (), {})
        cls_b = type("AdapterB", (), {})
        eps = [_make_entry_point("a", cls_a), _make_entry_point("b", cls_b)]

        with patch("raise_cli.adapters.registry.entry_points", return_value=eps):
            result = _discover("rai.adapters.pm")

        assert result == {"a": cls_a, "b": cls_b}

    def test_skips_broken_entry_point_with_warning(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        good_cls = type("Good", (), {})
        good_ep = _make_entry_point("good", good_cls)
        bad_ep = _make_broken_entry_point("bad", ImportError("missing dep"))

        with (
            patch(
                "raise_cli.adapters.registry.entry_points",
                return_value=[good_ep, bad_ep],
            ),
            caplog.at_level(logging.WARNING),
        ):
            result = _discover("rai.adapters.pm")

        assert result == {"good": good_cls}
        assert "bad" in caplog.text
        assert "missing dep" in caplog.text

    def test_skips_broken_and_keeps_all_valid(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        cls_a = type("A", (), {})
        cls_c = type("C", (), {})
        eps = [
            _make_entry_point("a", cls_a),
            _make_broken_entry_point("b", Exception("boom")),
            _make_entry_point("c", cls_c),
        ]

        with (
            patch("raise_cli.adapters.registry.entry_points", return_value=eps),
            caplog.at_level(logging.WARNING),
        ):
            result = _discover("rai.test.group")

        assert result == {"a": cls_a, "c": cls_c}
        assert "b" in caplog.text

    def test_skips_non_class_entry_point_with_warning(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Entry points must resolve to classes, not functions or instances."""
        a_function = lambda: None  # noqa: E731
        mock_ep = _make_entry_point("not_a_class", a_function)

        with (
            patch("raise_cli.adapters.registry.entry_points", return_value=[mock_ep]),
            caplog.at_level(logging.WARNING),
        ):
            result = _discover("rai.adapters.pm")

        assert result == {}
        assert "not_a_class" in caplog.text
        assert "expected a class" in caplog.text


# --- Public functions: behavior-based tests ---


class TestPublicFunctions:
    """Each public function discovers from its designated group.

    Tests use real _discover (not mocked) to verify end-to-end behavior.
    """

    @patch("raise_cli.adapters.registry.entry_points", return_value=[])
    def test_get_pm_adapters_returns_empty_when_none_registered(
        self, _mock: MagicMock
    ) -> None:
        assert get_pm_adapters() == {}

    @patch("raise_cli.adapters.registry.entry_points", return_value=[])
    def test_get_graph_backends_returns_empty_when_none_registered(
        self, _mock: MagicMock
    ) -> None:
        assert get_graph_backends() == {}

    def test_get_pm_adapters_discovers_from_correct_group(self) -> None:
        fake_cls = type("JiraAdapter", (), {})
        mock_ep = _make_entry_point("jira", fake_cls)

        with patch(
            "raise_cli.adapters.registry.entry_points", return_value=[mock_ep]
        ) as mock_eps:
            result = get_pm_adapters()

        mock_eps.assert_called_once_with(group=EP_PM_ADAPTERS)
        assert result == {"jira": fake_cls}

    def test_get_governance_parsers_discovers_from_correct_group(self) -> None:
        fake_cls = type("BacklogParser", (), {})
        mock_ep = _make_entry_point("backlog", fake_cls)

        with patch(
            "raise_cli.adapters.registry.entry_points", return_value=[mock_ep]
        ) as mock_eps:
            result = get_governance_parsers()

        mock_eps.assert_called_once_with(group=EP_GOVERNANCE_PARSERS)
        assert result == {"backlog": fake_cls}


class TestGovernanceParsersDiscovery:
    """Integration test: real entry point discovery (requires pip install -e .)."""

    def test_governance_parsers_discovered(self) -> None:
        """All 9 built-in parsers are discoverable via entry points."""
        parsers = get_governance_parsers()
        expected = {
            "prd",
            "vision",
            "constitution",
            "roadmap",
            "backlog",
            "epic_scope",
            "adr",
            "guardrails",
            "glossary",
        }
        assert expected.issubset(parsers.keys())
