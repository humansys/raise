"""Sync wrappers for async adapter protocols.

Bridges async adapters to sync consumption. Safe to call from both sync
contexts (CLI) and async contexts (hooks, server) — uses a thread-based
fallback when an event loop is already running.

Usage::

    from raise_cli.adapters.sync import SyncPMAdapter

    async_adapter = JiraAdapter(config)
    sync_adapter = SyncPMAdapter(async_adapter)
    issue = sync_adapter.get_issue("PROJ-301")  # sync call
"""

from __future__ import annotations

import asyncio
import concurrent.futures
from collections.abc import Coroutine
from pathlib import Path
from typing import Any

from raise_cli.adapters.models import (
    AdapterHealth,
    AttachmentDetail,
    AttachmentRef,
    BatchResult,
    Comment,
    CommentRef,
    CustomField,
    FieldDefinition,
    IssueDetail,
    IssueRef,
    IssueSpec,
    IssueSummary,
    IssueTypeInfo,
    LinkTypeDefinition,
    PageContent,
    PageSummary,
    ProjectVersion,
    PublishResult,
    WorkflowState,
)
from raise_cli.adapters.models.docs import AttachmentSummary, CommentSummary
from raise_cli.adapters.protocols import (
    AsyncDocumentationTarget,
    AsyncProjectManagementAdapter,
    AsyncProjectVersionManagementAdapter,
)


def run_sync[T](coro: Coroutine[Any, Any, T], closeable: Any = None) -> T:
    """Run a coroutine synchronously, safe from both sync and async contexts.

    - **No running loop:** uses ``asyncio.run()`` directly.
    - **Loop already running:** runs ``asyncio.run()`` in a separate thread
      so each thread gets its own event loop, avoiding the
      ``RuntimeError: asyncio.run() cannot be called from a running event loop``.

    Args:
        coro: The coroutine to run.
        closeable: Optional object with ``aclose()`` method. Called in a
            ``finally`` block within the same event loop to prevent
            asyncgen finalizer tracebacks.
    """

    async def _wrapped() -> T:
        try:
            return await coro
        finally:
            if closeable is not None:
                aclose = getattr(closeable, "aclose", None)
                if aclose:
                    await aclose()

    try:
        asyncio.get_running_loop()
    except RuntimeError:
        # No loop running — safe to use asyncio.run()
        return asyncio.run(_wrapped())
    else:
        # Loop already running — delegate to a thread with its own loop
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(asyncio.run, _wrapped())
            return future.result()


class SyncPMAdapter:
    """Wraps ``AsyncProjectManagementAdapter`` for sync CLI consumption.

    Satisfies ``ProjectManagementAdapter`` protocol via structural typing.
    Each method delegates to the async adapter via ``run_sync()``.
    """

    def __init__(self, async_adapter: AsyncProjectManagementAdapter) -> None:
        self._adapter = async_adapter

    @property
    def adapter(self) -> AsyncProjectManagementAdapter:
        """Wrapped async adapter."""
        return self._adapter

    def create_issue(self, project_key: str, issue: IssueSpec) -> IssueRef:
        return run_sync(self._adapter.create_issue(project_key, issue), self._adapter)

    def get_issue(self, key: str) -> IssueDetail:
        return run_sync(self._adapter.get_issue(key), self._adapter)

    def update_issue(self, key: str, fields: dict[str, Any]) -> IssueRef:
        return run_sync(self._adapter.update_issue(key, fields), self._adapter)

    def transition_issue(self, key: str, status: str) -> IssueRef:
        return run_sync(self._adapter.transition_issue(key, status), self._adapter)

    def batch_transition(self, keys: list[str], status: str) -> BatchResult:
        return run_sync(self._adapter.batch_transition(keys, status), self._adapter)

    def batch_create(self, issues: list[IssueSpec]) -> BatchResult:
        return run_sync(self._adapter.batch_create(issues), self._adapter)

    def link_to_parent(self, child_key: str, parent_key: str) -> bool:
        return run_sync(
            self._adapter.link_to_parent(child_key, parent_key), self._adapter
        )

    def link_issues(self, source: str, target: str, link_type: str) -> bool:
        return run_sync(
            self._adapter.link_issues(source, target, link_type), self._adapter
        )

    def remove_link(self, link_id: str) -> None:
        run_sync(self._adapter.remove_link(link_id), self._adapter)

    def add_comment(self, key: str, body: str) -> CommentRef:
        return run_sync(self._adapter.add_comment(key, body), self._adapter)

    def get_comments(
        self, key: str, limit: int = 10, offset: int = 0, fetch_all: bool = False
    ) -> list[Comment]:
        return run_sync(
            self._adapter.get_comments(
                key, limit=limit, offset=offset, fetch_all=fetch_all
            ),
            self._adapter,
        )

    def search(
        self, query: str, limit: int = 50, offset: int = 0, fetch_all: bool = False
    ) -> list[IssueSummary]:
        return run_sync(
            self._adapter.search(
                query, limit=limit, offset=offset, fetch_all=fetch_all
            ),
            self._adapter,
        )

    def health(self) -> AdapterHealth:
        return run_sync(self._adapter.health(), self._adapter)

    def discover_fields(self, project_key: str) -> list[FieldDefinition]:
        return run_sync(self._adapter.discover_fields(project_key), self._adapter)

    def discover_statuses(
        self, project_key: str, issue_type: str = "Story"
    ) -> list[WorkflowState]:
        return run_sync(
            self._adapter.discover_statuses(project_key, issue_type=issue_type),
            self._adapter,
        )

    def discover_link_types(self) -> list[LinkTypeDefinition]:
        return run_sync(self._adapter.discover_link_types(), self._adapter)

    def discover_issue_types(self, project_key: str) -> list[IssueTypeInfo]:
        return run_sync(self._adapter.discover_issue_types(project_key), self._adapter)

    def discover_named_fields(
        self, names: list[str], issue_type: str, project_key: str | None = None
    ) -> list[CustomField]:
        return run_sync(
            self._adapter.discover_named_fields(
                names, issue_type, project_key=project_key
            ),
            self._adapter,
        )

    # ── Attachments (S2503.7) ────────────────────────────────────────

    def attach(
        self, key: str, path: Path, mime_type: str | None = None
    ) -> AttachmentRef:
        return run_sync(self._adapter.attach(key, path, mime_type), self._adapter)

    def get_attachments(self, key: str) -> list[AttachmentDetail]:
        return run_sync(self._adapter.get_attachments(key), self._adapter)

    def download_attachment(self, attachment_id: str) -> bytes:
        return run_sync(self._adapter.download_attachment(attachment_id), self._adapter)

    # ── Project versions / fixVersions (optional Jira capability) ───

    def _version_adapter(self) -> AsyncProjectVersionManagementAdapter:
        if not isinstance(self._adapter, AsyncProjectVersionManagementAdapter):
            msg = "Wrapped PM adapter does not support project version management"
            raise NotImplementedError(msg)
        return self._adapter

    def list_versions(self, project_key: str) -> list[ProjectVersion]:
        adapter = self._version_adapter()
        return run_sync(adapter.list_versions(project_key), self._adapter)

    def create_version(self, project_key: str, name: str) -> ProjectVersion:
        adapter = self._version_adapter()
        return run_sync(adapter.create_version(project_key, name), self._adapter)

    # ── Sprint (Jira-specific, sync in underlying adapter) ───────────

    def get_sprints(self, project_key: str, state: str | None = None) -> list[Any]:
        return self._adapter.get_sprints(project_key, state=state)  # type: ignore[no-any-return]

    def assign_to_sprint(self, issue_key: str, sprint_id: int) -> None:
        self._adapter.assign_to_sprint(issue_key, sprint_id)  # type: ignore[attr-defined]


class SyncDocsAdapter:
    """Wraps ``AsyncDocumentationTarget`` for sync CLI consumption.

    Satisfies ``DocumentationTarget`` protocol via structural typing.
    Each method delegates to the async target via ``run_sync()``.
    """

    def __init__(self, async_target: AsyncDocumentationTarget) -> None:
        self._target = async_target

    def can_publish(
        self,
        doc_type: str | None,
        metadata: dict[str, Any],
        format: str = "markdown",
    ) -> bool:
        return run_sync(
            self._target.can_publish(doc_type, metadata, format), self._target
        )

    def publish(
        self,
        doc_type: str | None,
        content: str,
        metadata: dict[str, Any],
        format: str = "markdown",
    ) -> PublishResult:
        return run_sync(
            self._target.publish(doc_type, content, metadata, format), self._target
        )

    def get_page(self, identifier: str) -> PageContent:
        return run_sync(self._target.get_page(identifier), self._target)

    def search(self, query: str, limit: int = 10) -> list[PageSummary]:
        return run_sync(self._target.search(query, limit), self._target)

    def health(self) -> AdapterHealth:
        return run_sync(self._target.health(), self._target)

    def add_label(self, page_id: str, name: str) -> None:
        return run_sync(self._target.add_label(page_id, name), self._target)

    def get_labels(self, page_id: str) -> list[str]:
        return run_sync(self._target.get_labels(page_id), self._target)

    def get_page_children(self, page_id: str) -> list[PageSummary]:
        return run_sync(self._target.get_page_children(page_id), self._target)

    def delete_page(self, page_id: str) -> None:
        return run_sync(self._target.delete_page(page_id), self._target)

    def add_comment(self, page_id: str, body: str) -> None:
        return run_sync(self._target.add_comment(page_id, body), self._target)

    def get_comments(self, page_id: str) -> list[CommentSummary]:
        return run_sync(self._target.get_comments(page_id), self._target)

    def upload_attachment(
        self, page_id: str, file_path: str, comment: str | None = None
    ) -> str:
        return run_sync(
            self._target.upload_attachment(page_id, file_path, comment), self._target
        )

    def get_attachments(self, page_id: str) -> list[AttachmentSummary]:
        return run_sync(self._target.get_attachments(page_id), self._target)

    def embed_attachment(self, page_id: str, filename: str) -> PageContent:
        return run_sync(self._target.embed_attachment(page_id, filename), self._target)
