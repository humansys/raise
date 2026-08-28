"""Confluence adapter implementing DocumentationTarget.

Pure Python adapter using ConfluenceClient (S1051.1) and config schema (S1051.3).
Registered via entry point: ``rai.docs.targets`` → ``confluence``.

Optional dependency: ``pip install raise-cli[confluence]``

RAISE-1055 (S1051.2), RAISE-4358 (S4342.1)
"""

from __future__ import annotations

import mimetypes
import sys
from pathlib import Path
from typing import Any

from raise_cli.adapters.confluence_client import ConfluenceClient
from raise_cli.adapters.confluence_config import (
    ConfluenceTargetConfig,
    load_all_confluence_targets,
)
from raise_cli.adapters.models.docs import (
    AttachmentSummary,
    CommentSummary,
    PageContent,
    PageSummary,
    PublishResult,
)
from raise_cli.adapters.models.health import AdapterHealth
from raise_cli.output.symbols import WARN


class PublishError(Exception):
    """Raised when publish cannot proceed due to missing configuration."""


class PythonApiConfluenceAdapter:
    """Confluence adapter implementing DocumentationTarget (sync).

    No-arg constructor for entry point discovery: loads config from
    ``.raise/docs.yaml`` in CWD. Pass ``project_root`` for testing.
    """

    def __init__(self, project_root: Path | None = None) -> None:
        root = project_root or Path.cwd()
        self._default_name, self._targets = load_all_confluence_targets(root)
        self._clients: dict[str, ConfluenceClient] = {
            name: ConfluenceClient(cfg) for name, cfg in self._targets.items()
        }
        self._remote: ConfluenceClient = self._clients[self._default_name]

    def _find_target_for(
        self, doc_type: str | None
    ) -> tuple[str, ConfluenceTargetConfig, ConfluenceClient]:
        """Return (name, config, client) for the target that handles doc_type.

        Searches default_target first (wins ties), then others. Falls back to
        default_target when no routing match is found.
        """
        search_order = [self._default_name] + [
            n for n in self._targets if n != self._default_name
        ]
        for name in search_order:
            if doc_type in self._targets[name].routing:
                return name, self._targets[name], self._clients[name]
        return (
            self._default_name,
            self._targets[self._default_name],
            self._clients[self._default_name],
        )

    def _resolve_or_create_parent(
        self,
        parent_title: str,
        config: ConfluenceTargetConfig,
        client: ConfluenceClient,
    ) -> str:
        """Return parent page ID by title, auto-creating under home_page_id if missing.

        Emits PARENT_CREATED_AT_ROOT to stderr when a page is created so agents
        and developers cannot silently miss the structural change.
        """
        page = client.get_page_by_title(parent_title)
        if page:
            return page.id
        if not config.home_page_id:
            raise PublishError(
                f"Parent page '{parent_title}' not found and home_page_id is not "
                "configured — create the page manually or set home_page_id in docs.yaml"
            )
        created = client.create_page(parent_title, "", parent_id=config.home_page_id)
        print(
            f"\n⚠ PARENT_CREATED_AT_ROOT\n"
            f'  Created: "{parent_title}" (id: {created.id})\n'
            f"  Location: root of space {config.space_key} (under home page)\n"
            f"  Reason: parent_title not found — created automatically\n"
            f"  Action: if this is wrong, delete the page and configure\n"
            f"          parent_title to an existing page in docs.yaml",
            file=sys.stderr,
        )
        return created.id

    def _resolve_parent_path(
        self,
        path: list[str],
        config: ConfluenceTargetConfig,
        client: ConfluenceClient,
    ) -> str:
        """Traverse hierarchical path, returning the ID of the deepest page.

        Iterates left→right. Found pages advance the current parent.
        Missing pages are created under the current parent (requires home_page_id
        as the root anchor for the first segment).

        Raises PublishError if a segment is missing and no parent ID is available.
        """
        current_id: str | None = config.home_page_id
        for title in path:
            page = client.get_page_by_title(title)
            if page:
                current_id = page.id
            else:
                if not current_id:
                    raise PublishError(
                        f"Cannot create page '{title}': no parent ID available. "
                        "Set home_page_id in docs.yaml or ensure the preceding "
                        "path segment exists in Confluence."
                    )
                created = client.create_page(title, "", parent_id=current_id)
                current_id = created.id
        return current_id  # type: ignore[return-value]

    def can_publish(self, doc_type: str | None, metadata: dict[str, Any]) -> bool:
        """True if routing configured for doc_type in any target, or free-form with parent anchor."""
        if doc_type is None:
            return bool(metadata.get("parent_id")) or any(
                bool(cfg.home_page_id) for cfg in self._targets.values()
            )
        return any(doc_type in cfg.routing for cfg in self._targets.values())

    def publish(
        self, doc_type: str | None, content: str, metadata: dict[str, Any]
    ) -> PublishResult:
        """Publish doc: route by doc_type, resolve parent, find/create page.

        Parent resolution priority (RAISE-605, S20.9, S4342.1, S4342.2):
        1. metadata["parent_id"] — explicit override
        2. routing.parent_path — hierarchical traversal (S4342.1)
        3. routing.parent_title — flat title lookup + auto-create
        4. config.home_page_id — fallback for free-form publish (with warning)
        5. Error — no parent anchor available
        """
        title = metadata.get("title")
        if not title:
            return PublishResult(
                success=False,
                message="metadata['title'] is required for publishing",
            )

        _, config, client = self._find_target_for(doc_type)
        routing = config.routing.get(doc_type) if doc_type is not None else None
        labels: list[str] = routing.labels if routing else []
        parent_id: str | None = metadata.get("parent_id")

        if parent_id is None:
            if routing and routing.parent_path:
                # Hierarchical path traversal (takes priority over parent_title)
                try:
                    parent_id = self._resolve_parent_path(
                        routing.parent_path, config, client
                    )
                except PublishError as exc:
                    return PublishResult(success=False, message=str(exc))
            elif routing and routing.parent_title:
                # Flat title lookup + auto-create if missing
                try:
                    parent_id = self._resolve_or_create_parent(
                        routing.parent_title, config, client
                    )
                except PublishError as exc:
                    return PublishResult(success=False, message=str(exc))
            elif config.home_page_id:
                # Free-form fallback: publish under space home page
                print(
                    f"{WARN} publishing under home page -- no parent configured "
                    "(set parent_title in routing or pass --parent)",
                    file=sys.stderr,
                )
                parent_id = config.home_page_id
            else:
                return PublishResult(
                    success=False,
                    message=(
                        f"No routing configured for doc_type '{doc_type}' "
                        "and no parent_id provided — configure home_page_id "
                        "in docs.yaml or pass --parent <page_id>"
                    ),
                )

        # RAISE-5894: use remote_id for direct PUT when available; fallback to title lookup
        remote_id: str | None = metadata.get("remote_id") or None
        page, msg = self._upsert_page(client, title, content, parent_id, remote_id)

        if labels:
            client.set_labels(page.id, labels)

        return PublishResult(success=True, url=page.url, remote_id=page.id, message=msg)

    def _upsert_page(
        self,
        client: Any,
        title: str,
        content: str,
        parent_id: str | None,
        remote_id: str | None,
    ) -> tuple[Any, str]:
        """PUT by remote_id when known; fallback to title lookup + create."""
        if remote_id:
            return client.update_page(
                remote_id, title, content
            ), f"Page {title!r} updated by remote_id"
        existing = client.get_page_by_title(title)
        if existing:
            return client.update_page(
                existing.id, title, content
            ), f"Page {title!r} already exists — updating"
        return client.create_page(title, content, parent_id=parent_id), ""

    def get_page(self, identifier: str) -> PageContent:
        """Get page by ID."""
        return self._remote.get_page_by_id(identifier)

    def search(self, query: str, limit: int = 10) -> list[PageSummary]:
        """Search via CQL."""
        return self._remote.search(query, limit=limit)

    def health(self) -> AdapterHealth:
        """Delegate to default client health check."""
        return self._remote.health()

    def add_label(self, page_id: str, name: str) -> None:
        """Add a single label to a page."""
        self._remote.add_labels(page_id, [name])

    def get_labels(self, page_id: str) -> list[str]:
        """Return labels for a page."""
        return self._remote.get_labels(page_id)

    def get_page_children(self, page_id: str) -> list[PageSummary]:
        """Return child pages of a page."""
        return self._remote.get_page_children(page_id)

    def delete_page(self, page_id: str) -> None:
        """Delete a page by ID."""
        self._remote.delete_page(page_id)

    def add_comment(self, page_id: str, body: str) -> None:
        """Add a page-level comment."""
        self._remote.add_comment(page_id, body)

    def get_comments(self, page_id: str) -> list[CommentSummary]:
        """Return page-level comments."""
        return self._remote.get_comments(page_id)

    def upload_attachment(
        self, page_id: str, file_path: str, comment: str | None = None
    ) -> str:
        """Upload a file to a page and return the download URL."""
        content_type = mimetypes.guess_type(file_path)[0] or "application/octet-stream"
        return self._remote.upload_attachment(page_id, file_path, content_type, comment)

    def get_attachments(self, page_id: str) -> list[AttachmentSummary]:
        """Return attachments on a page."""
        return self._remote.get_attachments(page_id)

    def embed_attachment(self, page_id: str, filename: str) -> PageContent:
        """Append a view-file macro for filename to the page body."""
        return self._remote.append_attachment_macro(page_id, filename)
