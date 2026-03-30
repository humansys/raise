"""Confluence adapter implementing DocumentationTarget.

Pure Python adapter using ConfluenceClient (S1051.1) and config schema (S1051.3).
Registered via entry point: ``rai.docs.targets`` → ``confluence``.

Optional dependency: ``pip install raise-cli[confluence]``

RAISE-1055 (S1051.2)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from raise_cli.adapters.confluence_client import ConfluenceClient
from raise_cli.adapters.confluence_config import (
    ConfluenceConfig,
    load_confluence_config,
)
from raise_cli.adapters.models.docs import PageContent, PageSummary, PublishResult
from raise_cli.adapters.models.health import AdapterHealth


class PythonApiConfluenceAdapter:
    """Confluence adapter implementing DocumentationTarget (sync).

    No-arg constructor for entry point discovery: loads config from
    ``.raise/confluence.yaml`` in CWD. Pass ``project_root`` for testing.
    """

    def __init__(self, project_root: Path | None = None) -> None:
        root = project_root or Path.cwd()
        self._config: ConfluenceConfig = load_confluence_config(root)
        instance = self._config.get_instance()
        self._client: ConfluenceClient = ConfluenceClient(instance)

    def can_publish(self, doc_type: str, metadata: dict[str, Any]) -> bool:
        """True only if routing is explicitly configured for doc_type."""
        return self._config.resolve_routing(doc_type) is not None

    def publish(
        self, doc_type: str, content: str, metadata: dict[str, Any]
    ) -> PublishResult:
        """Publish doc: resolve routing, find/create page, apply labels."""
        title = metadata.get("title")
        if not title:
            return PublishResult(
                success=False,
                message="metadata['title'] is required for publishing",
            )

        routing = self._config.resolve_routing(doc_type)
        if not routing:
            return PublishResult(
                success=False,
                message=f"No routing configured for doc_type '{doc_type}'",
            )

        labels = routing.labels
        parent_id: str | None = None

        # Resolve parent page — fail if not found (reliability over convenience)
        parent_page = self._client.get_page_by_title(routing.parent_title)
        if not parent_page:
            return PublishResult(
                success=False,
                message=(
                    f"Parent page '{routing.parent_title}' not found in Confluence. "
                    "Create it first or fix routing config."
                ),
            )
        parent_id = parent_page.id

        # Check if page already exists
        existing = self._client.get_page_by_title(title)

        if existing:
            page = self._client.update_page(existing.id, title, content)
        else:
            page = self._client.create_page(title, content, parent_id=parent_id)

        if labels:
            self._client.set_labels(page.id, labels)

        return PublishResult(success=True, url=page.url)

    def get_page(self, identifier: str) -> PageContent:
        """Get page by ID."""
        return self._client.get_page_by_id(identifier)

    def search(self, query: str, limit: int = 10) -> list[PageSummary]:
        """Search via CQL."""
        return self._client.search(query, limit=limit)

    def health(self) -> AdapterHealth:
        """Delegate to client health check."""
        return self._client.health()
