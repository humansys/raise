"""Tests for McpConfluenceAdapter — Confluence adapter via MCP bridge.

Mocks at McpBridge.call() level. Does NOT require mcp-atlassian installed.
Uses asyncio.run() for async tests (no pytest-asyncio dependency).
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock

import pytest

from raise_cli.adapters.mcp_bridge import McpBridgeError, McpToolResult
from raise_cli.adapters.models import (
    AdapterHealth,
    PageContent,
    PageSummary,
    PublishResult,
)
from raise_cli.adapters.protocols import AsyncDocumentationTarget, DocumentationTarget
from raise_cli.adapters.registry import get_doc_targets
from raise_cli.adapters.sync import SyncDocsAdapter

# --- Helpers ---


def _run(coro: Any) -> Any:
    """Run async test coroutine synchronously."""
    return asyncio.run(coro)


def _ok(data: dict[str, Any]) -> McpToolResult:
    """Create a successful McpToolResult with JSON data."""
    return McpToolResult(text=json.dumps(data), data=data)


def _ok_items(items: list[dict[str, Any]]) -> McpToolResult:
    """Create a successful McpToolResult with array data (bridge-wrapped)."""
    return McpToolResult(text=json.dumps(items), data={"items": items})


# Sample confluence.yaml content
CONFLUENCE_YAML = """\
space_key: rAIse
"""

CONFLUENCE_YAML_NO_SPACE = """\
some_other_key: value
"""


# =============================================================================
# McpConfluenceAdapter.__init__ + config
# =============================================================================


class TestMcpConfluenceAdapterInit:
    def test_init_reads_confluence_yaml(self, tmp_path: Path) -> None:
        """__init__ reads confluence.yaml and extracts space_key."""
        (tmp_path / ".raise").mkdir()
        (tmp_path / ".raise" / "confluence.yaml").write_text(CONFLUENCE_YAML)

        from rai_pro.adapters.mcp_confluence import McpConfluenceAdapter

        adapter = McpConfluenceAdapter(project_root=tmp_path)
        assert adapter._space_key == "rAIse"

    def test_init_raises_on_missing_config(self, tmp_path: Path) -> None:
        """__init__ raises FileNotFoundError when confluence.yaml doesn't exist."""
        from rai_pro.adapters.mcp_confluence import McpConfluenceAdapter

        with pytest.raises(FileNotFoundError, match="confluence.yaml"):
            McpConfluenceAdapter(project_root=tmp_path)

    def test_init_raises_on_missing_space_key(self, tmp_path: Path) -> None:
        """__init__ raises ValueError when space_key is missing from config."""
        (tmp_path / ".raise").mkdir()
        (tmp_path / ".raise" / "confluence.yaml").write_text(CONFLUENCE_YAML_NO_SPACE)

        from rai_pro.adapters.mcp_confluence import McpConfluenceAdapter

        with pytest.raises(ValueError, match="space_key"):
            McpConfluenceAdapter(project_root=tmp_path)

    def test_init_space_key_from_env(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """__init__ falls back to CONFLUENCE_SPACE_KEY env var."""
        (tmp_path / ".raise").mkdir()
        (tmp_path / ".raise" / "confluence.yaml").write_text(CONFLUENCE_YAML_NO_SPACE)
        monkeypatch.setenv("CONFLUENCE_SPACE_KEY", "ENV_SPACE")

        from rai_pro.adapters.mcp_confluence import McpConfluenceAdapter

        adapter = McpConfluenceAdapter(project_root=tmp_path)
        assert adapter._space_key == "ENV_SPACE"


# =============================================================================
# Helper to create adapter with mocked bridge
# =============================================================================


def _make_adapter(tmp_path: Path) -> Any:
    """Create McpConfluenceAdapter with valid config and mocked bridge."""
    (tmp_path / ".raise").mkdir(exist_ok=True)
    (tmp_path / ".raise" / "confluence.yaml").write_text(CONFLUENCE_YAML)

    from rai_pro.adapters.mcp_confluence import McpConfluenceAdapter

    adapter = McpConfluenceAdapter(project_root=tmp_path)
    adapter._bridge = AsyncMock()
    return adapter


# =============================================================================
# can_publish
# =============================================================================


class TestCanPublish:
    def test_can_publish_returns_true(self, tmp_path: Path) -> None:
        """can_publish returns True for any doc type — no MCP call."""
        adapter = _make_adapter(tmp_path)

        async def run() -> bool:
            return await adapter.can_publish("roadmap", {})

        assert _run(run()) is True
        adapter._bridge.call.assert_not_called()

    def test_can_publish_any_type(self, tmp_path: Path) -> None:
        """can_publish accepts arbitrary doc types."""
        adapter = _make_adapter(tmp_path)

        async def run() -> bool:
            return await adapter.can_publish("custom_type", {"extra": "meta"})

        assert _run(run()) is True


# =============================================================================
# publish — create, update, auto-heal
# =============================================================================


class TestPublish:
    def test_publish_creates_new_page(self, tmp_path: Path) -> None:
        """Publish calls confluence_create_page when no page_id cached."""
        adapter = _make_adapter(tmp_path)
        adapter._bridge.call.return_value = _ok(
            {
                "message": "Page created successfully",
                "page": {
                    "id": "3087892481",
                    "title": "Roadmap",
                    "url": "https://example.atlassian.net/wiki/spaces/rAIse/pages/3087892481",
                    "space": {"key": "rAIse", "name": "rAIse"},
                    "version": 1,
                    "content": {"value": "# Roadmap", "format": "markdown"},
                },
            }
        )

        async def run() -> PublishResult:
            return await adapter.publish(
                "roadmap", "# Roadmap\n\nContent", {"title": "Roadmap"}
            )

        result = _run(run())
        assert result.success is True
        assert "3087892481" in result.url
        # Verify correct MCP tool called
        call_args = adapter._bridge.call.call_args
        assert call_args[0][0] == "confluence_create_page"
        args = call_args[0][1]
        assert args["space_key"] == "rAIse"
        assert args["title"] == "Roadmap"
        # Verify page_id saved to yaml
        pages_yaml = tmp_path / ".raise" / "confluence-pages.yaml"
        assert pages_yaml.exists()
        import yaml

        pages = yaml.safe_load(pages_yaml.read_text())
        assert pages["roadmap"] == "3087892481"

    def test_publish_updates_existing_page(self, tmp_path: Path) -> None:
        """Publish calls confluence_update_page when page_id is cached."""
        adapter = _make_adapter(tmp_path)
        # Pre-populate pages yaml
        import yaml

        pages_path = tmp_path / ".raise" / "confluence-pages.yaml"
        pages_path.write_text(yaml.dump({"roadmap": "3087892481"}))

        adapter._bridge.call.return_value = _ok(
            {
                "message": "Page updated successfully",
                "page": {
                    "id": "3087892481",
                    "title": "Roadmap",
                    "url": "https://example.atlassian.net/wiki/spaces/rAIse/pages/3087892481",
                    "space": {"key": "rAIse", "name": "rAIse"},
                    "version": 2,
                    "content": {"value": "# Roadmap v2", "format": "markdown"},
                },
            }
        )

        async def run() -> PublishResult:
            return await adapter.publish(
                "roadmap", "# Roadmap v2", {"title": "Roadmap"}
            )

        result = _run(run())
        assert result.success is True
        call_args = adapter._bridge.call.call_args
        assert call_args[0][0] == "confluence_update_page"
        args = call_args[0][1]
        assert args["page_id"] == "3087892481"

    def test_publish_reraises_non_notfound_errors(self, tmp_path: Path) -> None:
        """Publish re-raises errors that are not page-not-found (QR-1)."""
        adapter = _make_adapter(tmp_path)
        import yaml

        pages_path = tmp_path / ".raise" / "confluence-pages.yaml"
        pages_path.write_text(yaml.dump({"roadmap": "SOME_ID"}))

        adapter._bridge.call.side_effect = McpBridgeError("401 Unauthorized")

        async def run() -> PublishResult:
            return await adapter.publish("roadmap", "content", {"title": "Roadmap"})

        with pytest.raises(McpBridgeError, match="401 Unauthorized"):
            _run(run())
        # Verify yaml NOT cleared (page_id preserved)
        pages = yaml.safe_load(pages_path.read_text())
        assert pages["roadmap"] == "SOME_ID"

    def test_publish_auto_heals_on_deleted_page(self, tmp_path: Path) -> None:
        """Publish auto-heals when cached page was deleted — removes entry, creates new."""
        adapter = _make_adapter(tmp_path)
        import yaml

        pages_path = tmp_path / ".raise" / "confluence-pages.yaml"
        pages_path.write_text(yaml.dump({"roadmap": "OLD_DELETED_ID"}))

        # First call (update) fails with not-found, second call (create) succeeds
        adapter._bridge.call.side_effect = [
            McpBridgeError("Page not found"),
            _ok(
                {
                    "message": "Page created successfully",
                    "page": {
                        "id": "NEW_PAGE_ID",
                        "title": "Roadmap",
                        "url": "https://example.atlassian.net/wiki/spaces/rAIse/pages/NEW_PAGE_ID",
                        "space": {"key": "rAIse"},
                        "version": 1,
                        "content": {"value": "# Roadmap", "format": "markdown"},
                    },
                }
            ),
        ]

        async def run() -> PublishResult:
            return await adapter.publish("roadmap", "# Roadmap", {"title": "Roadmap"})

        result = _run(run())
        assert result.success is True
        assert "NEW_PAGE_ID" in result.url
        # Verify yaml updated with new ID
        pages = yaml.safe_load(pages_path.read_text())
        assert pages["roadmap"] == "NEW_PAGE_ID"

    def test_publish_returns_failure_on_is_error(self, tmp_path: Path) -> None:
        """Publish returns success=False when bridge result has is_error (QR-3)."""
        adapter = _make_adapter(tmp_path)
        adapter._bridge.call.return_value = McpToolResult(
            is_error=True, error_message="Permission denied"
        )

        async def run() -> PublishResult:
            return await adapter.publish("roadmap", "content", {"title": "Roadmap"})

        result = _run(run())
        assert result.success is False
        assert "Permission denied" in result.message


# =============================================================================
# get_page
# =============================================================================


class TestGetPage:
    def test_get_page_parses_metadata_format(self, tmp_path: Path) -> None:
        """get_page parses mcp-atlassian metadata-wrapped response."""
        adapter = _make_adapter(tmp_path)
        adapter._bridge.call.return_value = _ok(
            {
                "metadata": {
                    "id": "9240577",
                    "title": "Guardrails",
                    "url": "https://example.atlassian.net/wiki/spaces/LA/pages/9240577",
                    "space": {"key": "LA", "name": "Lean-Agile"},
                    "version": 3,
                    "content": {
                        "value": "# Guardrails\n\nContent here.",
                        "format": "markdown",
                    },
                },
            }
        )

        async def run() -> PageContent:
            return await adapter.get_page("9240577")

        result = _run(run())
        assert result.id == "9240577"
        assert result.title == "Guardrails"
        assert result.content == "# Guardrails\n\nContent here."
        assert result.space_key == "LA"
        assert result.version == 3
        assert "9240577" in result.url
        # Verify correct MCP tool called
        call_args = adapter._bridge.call.call_args
        assert call_args[0][0] == "confluence_get_page"
        assert call_args[0][1]["page_id"] == "9240577"


# =============================================================================
# search
# =============================================================================


class TestSearch:
    def test_search_parses_array_results(self, tmp_path: Path) -> None:
        """Search parses bridge-wrapped array into list[PageSummary]."""
        adapter = _make_adapter(tmp_path)
        adapter._bridge.call.return_value = _ok_items(
            [
                {
                    "id": "3087892481",
                    "title": "Roadmap",
                    "url": "https://example.atlassian.net/wiki/spaces/rAIse/pages/3087892481",
                    "space": {"key": "rAIse", "name": "rAIse"},
                    "updated": "",
                },
                {
                    "id": "9240577",
                    "title": "Guardrails",
                    "url": "https://example.atlassian.net/wiki/spaces/LA/pages/9240577",
                    "space": {"key": "LA", "name": "Lean-Agile"},
                    "updated": "",
                },
            ]
        )

        async def run() -> list[PageSummary]:
            return await adapter.search("roadmap", limit=5)

        result = _run(run())
        assert len(result) == 2
        assert result[0].id == "3087892481"
        assert result[0].title == "Roadmap"
        assert result[0].space_key == "rAIse"
        assert result[1].id == "9240577"
        # Verify correct MCP tool called
        call_args = adapter._bridge.call.call_args
        assert call_args[0][0] == "confluence_search"
        assert call_args[0][1]["query"] == "roadmap"
        assert call_args[0][1]["limit"] == 5

    def test_search_empty_results(self, tmp_path: Path) -> None:
        """Search returns empty list when no results."""
        adapter = _make_adapter(tmp_path)
        adapter._bridge.call.return_value = _ok_items([])

        async def run() -> list[PageSummary]:
            return await adapter.search("nonexistent", limit=10)

        result = _run(run())
        assert result == []


# =============================================================================
# health
# =============================================================================


class TestHealth:
    def test_health_returns_healthy(self, tmp_path: Path) -> None:
        """Health returns AdapterHealth with healthy=True when search succeeds."""
        adapter = _make_adapter(tmp_path)
        adapter._bridge.call.return_value = _ok_items(
            [{"id": "1", "title": "Any page", "url": "", "space": {"key": "X"}}]
        )

        async def run() -> AdapterHealth:
            return await adapter.health()

        result = _run(run())
        assert result.name == "confluence"
        assert result.healthy is True
        assert result.latency_ms is not None
        assert result.latency_ms >= 0

    def test_health_returns_unhealthy_on_error(self, tmp_path: Path) -> None:
        """Health returns unhealthy when bridge call fails."""
        adapter = _make_adapter(tmp_path)
        adapter._bridge.call.side_effect = McpBridgeError("Connection failed")

        async def run() -> AdapterHealth:
            return await adapter.health()

        result = _run(run())
        assert result.name == "confluence"
        assert result.healthy is False
        assert "Connection failed" in result.message


# =============================================================================
# Integration: entry point discovery + protocol compliance
# =============================================================================


class TestEntryPointDiscovery:
    def test_entry_point_discoverable(self) -> None:
        """get_doc_targets() discovers 'confluence' entry point."""
        targets = get_doc_targets()
        assert "confluence" in targets

    def test_entry_point_loads_correct_class(self) -> None:
        """Entry point loads PythonApiConfluenceAdapter (E1051 replaced MCP)."""
        from raise_cli.adapters.confluence_adapter import PythonApiConfluenceAdapter

        targets = get_doc_targets()
        assert targets["confluence"] is PythonApiConfluenceAdapter


class TestProtocolCompliance:
    def test_async_protocol(self, tmp_path: Path) -> None:
        """McpConfluenceAdapter satisfies AsyncDocumentationTarget."""
        adapter = _make_adapter(tmp_path)
        assert isinstance(adapter, AsyncDocumentationTarget)

    def test_sync_wrapper_satisfies_protocol(self, tmp_path: Path) -> None:
        """SyncDocsAdapter(McpConfluenceAdapter) satisfies DocumentationTarget."""
        adapter = _make_adapter(tmp_path)
        sync = SyncDocsAdapter(adapter)
        assert isinstance(sync, DocumentationTarget)
