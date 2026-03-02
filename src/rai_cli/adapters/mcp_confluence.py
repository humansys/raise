"""Confluence adapter via MCP bridge (mcp-atlassian server).

Implements ``AsyncDocumentationTarget`` by mapping each protocol method
to the corresponding ``mcp-atlassian`` Confluence tool via ``McpBridge``.

Configuration: reads ``.raise/confluence.yaml`` for space_key.
Connection: lazy — no MCP server connection until first method call.
Page tracking: ``.raise/confluence-pages.yaml`` maps artifact types to page IDs.

Architecture: S301.5 design (D1-D7)
"""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any

import yaml

from rai_cli.mcp.bridge import McpBridge, McpBridgeError, McpToolResult
from rai_cli.adapters.models import (
    AdapterHealth,
    PageContent,
    PageSummary,
    PublishResult,
)


class McpConfluenceAdapter:
    """Confluence adapter that delegates to mcp-atlassian via McpBridge.

    Implements ``AsyncDocumentationTarget`` protocol (structural typing).

    Args:
        project_root: Project root directory containing ``.raise/confluence.yaml``.
            Defaults to current working directory.
    """

    def __init__(self, project_root: Path | None = None) -> None:
        self._root = project_root or Path.cwd()
        config = self._load_config(self._root)

        space_key = config.get("space_key") or os.environ.get("CONFLUENCE_SPACE_KEY")
        if not space_key:
            msg = (
                "Missing 'space_key' in .raise/confluence.yaml and "
                "CONFLUENCE_SPACE_KEY env var not set."
            )
            raise ValueError(msg)

        self._space_key: str = space_key
        self._pages_path = self._root / ".raise" / "confluence-pages.yaml"
        self._bridge = self._create_bridge()

    @staticmethod
    def _create_bridge() -> McpBridge:
        """Create McpBridge with Confluence credentials from environment."""
        server_args: list[str] = ["mcp-atlassian"]
        confluence_url = os.environ.get("CONFLUENCE_URL")
        if confluence_url:
            server_args.extend(["--confluence-url", confluence_url])
        confluence_user = os.environ.get("CONFLUENCE_USERNAME")
        if confluence_user:
            server_args.extend(["--confluence-username", confluence_user])
        confluence_token = os.environ.get("CONFLUENCE_API_TOKEN")
        if confluence_token:
            server_args.extend(["--confluence-token", confluence_token])
        return McpBridge(server_command="uvx", server_args=server_args)

    @staticmethod
    def _load_config(root: Path) -> dict[str, Any]:
        """Read and parse .raise/confluence.yaml."""
        config_path = root / ".raise" / "confluence.yaml"
        if not config_path.exists():
            msg = f"Confluence config not found: {config_path}"
            raise FileNotFoundError(msg)
        with open(config_path, encoding="utf-8") as f:
            data: dict[str, Any] = yaml.safe_load(f)
        return data or {}

    # ----- Page ID tracking (D3) -----

    def _load_page_id(self, doc_type: str) -> str | None:
        """Load cached page ID for a doc type from confluence-pages.yaml."""
        if not self._pages_path.exists():
            return None
        with open(self._pages_path, encoding="utf-8") as f:
            pages: dict[str, str] = yaml.safe_load(f) or {}
        return pages.get(doc_type)

    def _save_page_id(self, doc_type: str, page_id: str) -> None:
        """Save page ID for a doc type to confluence-pages.yaml."""
        pages: dict[str, str] = {}
        if self._pages_path.exists():
            with open(self._pages_path, encoding="utf-8") as f:
                pages = yaml.safe_load(f) or {}
        pages[doc_type] = page_id
        with open(self._pages_path, "w", encoding="utf-8") as f:
            yaml.dump(pages, f, default_flow_style=False)

    def _remove_page_id(self, doc_type: str) -> None:
        """Remove a stale page ID entry from confluence-pages.yaml."""
        if not self._pages_path.exists():
            return
        with open(self._pages_path, encoding="utf-8") as f:
            pages: dict[str, str] = yaml.safe_load(f) or {}
        pages.pop(doc_type, None)
        with open(self._pages_path, "w", encoding="utf-8") as f:
            yaml.dump(pages, f, default_flow_style=False)

    # ----- DocumentationTarget methods -----

    async def can_publish(self, doc_type: str, metadata: dict[str, Any]) -> bool:
        """Accept all doc types — no restrictions."""
        return True

    async def publish(
        self, doc_type: str, content: str, metadata: dict[str, Any]
    ) -> PublishResult:
        """Publish content to Confluence. Creates or updates based on tracking."""
        title = metadata.get("title", doc_type)
        page_id = self._load_page_id(doc_type)

        if page_id:
            # Try update existing page
            try:
                result = await self._bridge.call(
                    "confluence_update_page",
                    {"page_id": page_id, "title": title, "content": content},
                )
                return self._parse_publish_result(result)
            except McpBridgeError as exc:
                # Auto-heal only when page was deleted — not on auth/network errors
                err = str(exc).lower()
                if "not found" in err or "404" in err or "does not exist" in err:
                    self._remove_page_id(doc_type)
                else:
                    raise

        # Create new page
        result = await self._bridge.call(
            "confluence_create_page",
            {"space_key": self._space_key, "title": title, "content": content},
        )
        publish_result = self._parse_publish_result(result)
        if publish_result.success:
            # Extract page_id from response and save
            page = result.data.get("page", {})
            new_id = str(page.get("id", ""))
            if new_id:
                self._save_page_id(doc_type, new_id)
        return publish_result

    async def get_page(self, identifier: str) -> PageContent:
        """Retrieve a page by ID from Confluence."""
        result = await self._bridge.call(
            "confluence_get_page", {"page_id": identifier}
        )
        return self._parse_page_content(result)

    async def search(self, query: str, limit: int = 10) -> list[PageSummary]:
        """Search Confluence pages."""
        result = await self._bridge.call(
            "confluence_search", {"query": query, "limit": limit}
        )
        return self._parse_search_results(result)

    async def health(self) -> AdapterHealth:
        """Check Confluence connectivity via minimal search."""
        start = time.monotonic()
        try:
            await self._bridge.call(
                "confluence_search",
                {"query": "type=page", "limit": 1},
            )
            elapsed_ms = int((time.monotonic() - start) * 1000)
            return AdapterHealth(
                name="confluence",
                healthy=True,
                message="OK",
                latency_ms=elapsed_ms,
            )
        except (McpBridgeError, Exception) as exc:
            elapsed_ms = int((time.monotonic() - start) * 1000)
            return AdapterHealth(
                name="confluence",
                healthy=False,
                message=str(exc),
                latency_ms=elapsed_ms,
            )

    # ----- Lifecycle -----

    async def aclose(self) -> None:
        """Close the underlying MCP bridge (RAISE-324)."""
        await self._bridge.aclose()

    # ----- Response parsers (D5 — probed formats) -----

    @staticmethod
    def _parse_publish_result(result: McpToolResult) -> PublishResult:
        """Parse create/update response into PublishResult.

        Format: {"message": "...", "page": {"id": "...", "url": "...", ...}}
        """
        if result.is_error:
            return PublishResult(success=False, message=result.error_message)
        page = result.data.get("page", {})
        url = page.get("url", "")
        return PublishResult(success=True, url=url)

    @staticmethod
    def _parse_page_content(result: McpToolResult) -> PageContent:
        """Parse get_page response into PageContent.

        Format: {"metadata": {"id": "...", "title": "...", "content": {"value": "..."}, ...}}
        """
        meta = result.data.get("metadata", {})
        content_obj = meta.get("content", {})
        space = meta.get("space", {})
        return PageContent(
            id=str(meta.get("id", "")),
            title=meta.get("title", ""),
            content=content_obj.get("value", ""),
            url=meta.get("url", ""),
            space_key=space.get("key", ""),
            version=meta.get("version", 1),
        )

    @staticmethod
    def _parse_search_results(result: McpToolResult) -> list[PageSummary]:
        """Parse search response into list[PageSummary].

        Bridge wraps JSON array as {"items": [...]}.
        """
        items = result.data.get("items", [])
        return [
            PageSummary(
                id=str(item.get("id", "")),
                title=item.get("title", ""),
                url=item.get("url", ""),
                space_key=item.get("space", {}).get("key", ""),
                updated=item.get("updated", ""),
            )
            for item in items
        ]
