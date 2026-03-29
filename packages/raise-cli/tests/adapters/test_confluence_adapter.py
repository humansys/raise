"""Tests for PythonApiConfluenceAdapter.

S1051.2 (RAISE-1055)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from raise_cli.adapters.confluence_adapter import PythonApiConfluenceAdapter
from raise_cli.adapters.confluence_config import (
    ArtifactRouting,
    ConfluenceConfig,
    ConfluenceInstanceConfig,
)
from raise_cli.adapters.models.docs import PageContent, PageSummary, PublishResult
from raise_cli.adapters.models.health import AdapterHealth
from raise_cli.adapters.protocols import DocumentationTarget


def _make_config(**routing_overrides: Any) -> ConfluenceConfig:
    """Helper: create a ConfluenceConfig with optional routing."""
    routing = routing_overrides.get("routing", {})
    return ConfluenceConfig(
        default_instance="default",
        instances={
            "default": ConfluenceInstanceConfig(
                url="https://test.atlassian.net/wiki",
                username="test@test.com",
                space_key="TEST",
                instance_name="default",
                routing=routing,
            ),
        },
    )


_CONFIG_MOD = "raise_cli.adapters.confluence_adapter"


# ── T1: Constructor + protocol conformance ───────────────────────────────


class TestConstructorAndProtocol:
    """Adapter construction and protocol conformance."""

    @patch(f"{_CONFIG_MOD}.ConfluenceClient")
    @patch(f"{_CONFIG_MOD}.load_confluence_config")
    def test_satisfies_documentation_target(
        self, mock_load: MagicMock, mock_client_cls: MagicMock
    ) -> None:
        mock_load.return_value = _make_config()
        adapter = PythonApiConfluenceAdapter(project_root=Path("/fake"))
        assert isinstance(adapter, DocumentationTarget)

    @patch(f"{_CONFIG_MOD}.ConfluenceClient")
    @patch(f"{_CONFIG_MOD}.load_confluence_config")
    def test_loads_config_and_creates_client(
        self, mock_load: MagicMock, mock_client_cls: MagicMock
    ) -> None:
        config = _make_config()
        mock_load.return_value = config
        adapter = PythonApiConfluenceAdapter(project_root=Path("/fake"))
        mock_load.assert_called_once_with(Path("/fake"))
        mock_client_cls.assert_called_once_with(config.get_instance())

    @patch(f"{_CONFIG_MOD}.ConfluenceClient")
    @patch(f"{_CONFIG_MOD}.load_confluence_config")
    def test_default_project_root_is_cwd(
        self, mock_load: MagicMock, mock_client_cls: MagicMock, tmp_path: Path
    ) -> None:
        mock_load.return_value = _make_config()
        with patch(f"{_CONFIG_MOD}.Path") as mock_path:
            mock_path.cwd.return_value = tmp_path
            PythonApiConfluenceAdapter()
            mock_load.assert_called_once_with(tmp_path)


# ── T2: Delegation methods ──────────────────────────────────────────────


def _make_adapter(
    routing: dict[str, ArtifactRouting] | None = None,
) -> tuple[PythonApiConfluenceAdapter, MagicMock]:
    """Helper: create adapter with mocked client. Returns (adapter, mock_client)."""
    config = _make_config(routing=routing or {})
    with (
        patch(f"{_CONFIG_MOD}.load_confluence_config", return_value=config),
        patch(f"{_CONFIG_MOD}.ConfluenceClient") as mock_cls,
    ):
        mock_client = MagicMock()
        mock_cls.return_value = mock_client
        adapter = PythonApiConfluenceAdapter(project_root=Path("/fake"))
    return adapter, mock_client


class TestCanPublish:
    """can_publish based on routing config."""

    def test_true_for_routed_type(self) -> None:
        adapter, _ = _make_adapter(
            routing={"adr": ArtifactRouting(parent_title="ADRs", labels=["adr"])}
        )
        assert adapter.can_publish("adr", {}) is True

    def test_false_for_unrouted_type(self) -> None:
        adapter, _ = _make_adapter(
            routing={"adr": ArtifactRouting(parent_title="ADRs")}
        )
        assert adapter.can_publish("unknown", {}) is False

    def test_true_when_no_routing_configured(self) -> None:
        adapter, _ = _make_adapter()
        assert adapter.can_publish("anything", {}) is True


class TestHealth:
    """health delegates to client."""

    def test_delegates_to_client(self) -> None:
        adapter, mock_client = _make_adapter()
        expected = AdapterHealth(name="confluence", healthy=True)
        mock_client.health.return_value = expected
        assert adapter.health() == expected
        mock_client.health.assert_called_once()


class TestGetPage:
    """get_page delegates to client."""

    def test_delegates_to_client(self) -> None:
        adapter, mock_client = _make_adapter()
        expected = PageContent(
            id="123", title="Test", content="<p>hi</p>",
            url="https://x/123", space_key="TEST", version=1,
        )
        mock_client.get_page_by_id.return_value = expected
        assert adapter.get_page("123") == expected
        mock_client.get_page_by_id.assert_called_once_with("123")


class TestSearch:
    """search delegates to client."""

    def test_delegates_to_client(self) -> None:
        adapter, mock_client = _make_adapter()
        expected = [
            PageSummary(id="1", title="Result", url="https://x/1", space_key="TEST"),
        ]
        mock_client.search.return_value = expected
        assert adapter.search("my query", limit=5) == expected
        mock_client.search.assert_called_once_with("my query", limit=5)
