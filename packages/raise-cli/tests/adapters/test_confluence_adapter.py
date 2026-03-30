"""Tests for PythonApiConfluenceAdapter.

S1051.2 (RAISE-1055)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

from raise_cli.adapters.confluence_adapter import PythonApiConfluenceAdapter
from raise_cli.adapters.confluence_config import (
    ArtifactRouting,
    ConfluenceConfig,
    ConfluenceInstanceConfig,
)
from raise_cli.adapters.models.docs import PageContent, PageSummary
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
        _adapter = PythonApiConfluenceAdapter(project_root=Path("/fake"))
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

    def test_false_when_no_routing_configured(self) -> None:
        adapter, _ = _make_adapter()
        assert adapter.can_publish("anything", {}) is False


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


# ── T3: publish ─────────────────────────────────────────────────────────


def _page(
    page_id: str = "100", title: str = "Test", url: str = "https://x/100"
) -> PageContent:
    return PageContent(
        id=page_id, title=title, content="<p>body</p>",
        url=url, space_key="TEST", version=1,
    )


class TestPublish:
    """publish: create/update with routing."""

    def test_creates_new_page_when_not_found(self) -> None:
        routing = {"doc": ArtifactRouting(parent_title="Docs", labels=["doc"])}
        adapter, mock_client = _make_adapter(routing=routing)
        mock_client.get_page_by_title.side_effect = [
            _page(page_id="5", title="Docs"),  # parent lookup
            None,  # title lookup (new page)
        ]
        mock_client.create_page.return_value = _page()

        result = adapter.publish("doc", "<p>hi</p>", {"title": "My Page"})

        assert result.success is True
        assert result.url == "https://x/100"
        mock_client.create_page.assert_called_once_with(
            "My Page", "<p>hi</p>", parent_id="5",
        )

    def test_updates_existing_page(self) -> None:
        routing = {"doc": ArtifactRouting(parent_title="Docs")}
        adapter, mock_client = _make_adapter(routing=routing)
        existing = _page(page_id="200", title="My Page")
        mock_client.get_page_by_title.side_effect = [
            _page(page_id="5", title="Docs"),  # parent lookup
            existing,  # title lookup (existing page)
        ]
        mock_client.update_page.return_value = _page(page_id="200", url="https://x/200")

        result = adapter.publish("doc", "<p>updated</p>", {"title": "My Page"})

        assert result.success is True
        mock_client.update_page.assert_called_once_with("200", "My Page", "<p>updated</p>")

    def test_applies_labels_from_routing(self) -> None:
        routing = {"adr": ArtifactRouting(parent_title="ADRs", labels=["adr", "arch"])}
        adapter, mock_client = _make_adapter(routing=routing)
        # Parent page found
        mock_client.get_page_by_title.side_effect = [
            _page(page_id="10", title="ADRs"),  # parent lookup
            None,  # title lookup (new page)
        ]
        mock_client.create_page.return_value = _page(page_id="50")

        result = adapter.publish("adr", "<p>adr</p>", {"title": "ADR-015"})

        assert result.success is True
        mock_client.create_page.assert_called_once_with(
            "ADR-015", "<p>adr</p>", parent_id="10",
        )
        mock_client.set_labels.assert_called_once_with("50", ["adr", "arch"])

    def test_rejects_unrouted_doc_type(self) -> None:
        adapter, mock_client = _make_adapter()

        result = adapter.publish("anything", "<p>hi</p>", {"title": "Page"})

        assert result.success is False
        assert "No routing configured" in result.message
        mock_client.create_page.assert_not_called()

    def test_requires_title_in_metadata(self) -> None:
        adapter, mock_client = _make_adapter()

        result = adapter.publish("doc", "<p>hi</p>", {})

        assert result.success is False
        assert "title" in result.message
        mock_client.create_page.assert_not_called()

    def test_parent_not_found_fails(self) -> None:
        routing = {"adr": ArtifactRouting(parent_title="ADRs", labels=["adr"])}
        adapter, mock_client = _make_adapter(routing=routing)
        mock_client.get_page_by_title.return_value = None  # parent not found

        result = adapter.publish("adr", "<p>adr</p>", {"title": "ADR-015"})

        assert result.success is False
        assert "Parent page 'ADRs' not found" in result.message
        mock_client.create_page.assert_not_called()


# ── T4: Entry point registration ────────────────────────────────────────


class TestEntryPoint:
    """Entry point discoverable via registry."""

    def test_confluence_in_doc_targets(self) -> None:
        from raise_cli.adapters.registry import get_doc_targets

        targets = get_doc_targets()
        assert "confluence" in targets
        # May resolve to PythonApiConfluenceAdapter or McpConfluenceAdapter
        # depending on which packages are installed. Both are valid.
        assert targets["confluence"] is not None
