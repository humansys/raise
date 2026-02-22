"""Tests for adapter entry point registry."""

from __future__ import annotations

import logging
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from rai_cli.adapters.registry import (
    EP_DOC_TARGETS,
    EP_GOVERNANCE_PARSERS,
    EP_GOVERNANCE_SCHEMAS,
    EP_GRAPH_BACKENDS,
    EP_PM_ADAPTERS,
    _discover,
    get_doc_targets,
    get_governance_parsers,
    get_governance_schemas,
    get_graph_backends,
    get_pm_adapters,
)


# --- Constants ---


class TestConstants:
    def test_pm_adapters_group(self) -> None:
        assert EP_PM_ADAPTERS == "rai.adapters.pm"

    def test_governance_schemas_group(self) -> None:
        assert EP_GOVERNANCE_SCHEMAS == "rai.governance.schemas"

    def test_governance_parsers_group(self) -> None:
        assert EP_GOVERNANCE_PARSERS == "rai.governance.parsers"

    def test_doc_targets_group(self) -> None:
        assert EP_DOC_TARGETS == "rai.docs.targets"

    def test_graph_backends_group(self) -> None:
        assert EP_GRAPH_BACKENDS == "rai.graph.backends"


# --- _discover ---


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


class TestDiscover:
    def test_returns_empty_dict_for_unknown_group(self) -> None:
        result = _discover("rai.nonexistent.group")
        assert result == {}

    def test_loads_single_entry_point(self) -> None:
        fake_cls = type("FakeAdapter", (), {})
        mock_ep = _make_entry_point("test_adapter", fake_cls)

        with patch(
            "rai_cli.adapters.registry.entry_points", return_value=[mock_ep]
        ):
            result = _discover("rai.adapters.pm")

        assert result == {"test_adapter": fake_cls}

    def test_loads_multiple_entry_points(self) -> None:
        cls_a = type("AdapterA", (), {})
        cls_b = type("AdapterB", (), {})
        eps = [_make_entry_point("a", cls_a), _make_entry_point("b", cls_b)]

        with patch(
            "rai_cli.adapters.registry.entry_points", return_value=eps
        ):
            result = _discover("rai.adapters.pm")

        assert result == {"a": cls_a, "b": cls_b}

    def test_skips_broken_entry_point_with_warning(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        good_cls = type("Good", (), {})
        good_ep = _make_entry_point("good", good_cls)
        bad_ep = _make_broken_entry_point("bad", ImportError("missing dep"))

        with patch(
            "rai_cli.adapters.registry.entry_points",
            return_value=[good_ep, bad_ep],
        ):
            with caplog.at_level(logging.WARNING):
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

        with patch(
            "rai_cli.adapters.registry.entry_points", return_value=eps
        ):
            with caplog.at_level(logging.WARNING):
                result = _discover("rai.test.group")

        assert result == {"a": cls_a, "c": cls_c}
        assert "b" in caplog.text


# --- Public functions delegate to _discover ---


class TestPublicFunctions:
    @patch("rai_cli.adapters.registry._discover", return_value={})
    def test_get_pm_adapters(self, mock_discover: MagicMock) -> None:
        result = get_pm_adapters()
        mock_discover.assert_called_once_with(EP_PM_ADAPTERS)
        assert result == {}

    @patch("rai_cli.adapters.registry._discover", return_value={})
    def test_get_governance_schemas(self, mock_discover: MagicMock) -> None:
        result = get_governance_schemas()
        mock_discover.assert_called_once_with(EP_GOVERNANCE_SCHEMAS)
        assert result == {}

    @patch("rai_cli.adapters.registry._discover", return_value={})
    def test_get_governance_parsers(self, mock_discover: MagicMock) -> None:
        result = get_governance_parsers()
        mock_discover.assert_called_once_with(EP_GOVERNANCE_PARSERS)
        assert result == {}

    @patch("rai_cli.adapters.registry._discover", return_value={})
    def test_get_doc_targets(self, mock_discover: MagicMock) -> None:
        result = get_doc_targets()
        mock_discover.assert_called_once_with(EP_DOC_TARGETS)
        assert result == {}

    @patch("rai_cli.adapters.registry._discover", return_value={})
    def test_get_graph_backends(self, mock_discover: MagicMock) -> None:
        result = get_graph_backends()
        mock_discover.assert_called_once_with(EP_GRAPH_BACKENDS)
        assert result == {}
