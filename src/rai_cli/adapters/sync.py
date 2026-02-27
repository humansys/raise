"""Sync wrappers for async adapter protocols.

Bridges async adapters to sync consumption. Safe to call from both sync
contexts (CLI) and async contexts (hooks, server) — uses a thread-based
fallback when an event loop is already running.

Usage::

    from rai_cli.adapters.sync import SyncPMAdapter

    async_adapter = JiraAdapter(config)
    sync_adapter = SyncPMAdapter(async_adapter)
    issue = sync_adapter.get_issue("RAISE-301")  # sync call
"""

from __future__ import annotations

import asyncio
import concurrent.futures
from typing import Any, TypeVar

from rai_cli.adapters.models import (
    AdapterHealth,
    BatchResult,
    Comment,
    CommentRef,
    IssueDetail,
    IssueRef,
    IssueSpec,
    IssueSummary,
    PageContent,
    PageSummary,
    PublishResult,
)
from rai_cli.adapters.protocols import (
    AsyncDocumentationTarget,
    AsyncProjectManagementAdapter,
)

T = TypeVar("T")


def _run_sync(coro: Any) -> Any:
    """Run a coroutine synchronously, safe from both sync and async contexts.

    - **No running loop:** uses ``asyncio.run()`` directly.
    - **Loop already running:** runs ``asyncio.run()`` in a separate thread
      so each thread gets its own event loop, avoiding the
      ``RuntimeError: asyncio.run() cannot be called from a running event loop``.
    """
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        # No loop running — safe to use asyncio.run()
        return asyncio.run(coro)
    else:
        # Loop already running — delegate to a thread with its own loop
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(asyncio.run, coro)
            return future.result()


class SyncPMAdapter:
    """Wraps ``AsyncProjectManagementAdapter`` for sync CLI consumption.

    Satisfies ``ProjectManagementAdapter`` protocol via structural typing.
    Each method delegates to the async adapter via ``_run_sync()``.
    """

    def __init__(self, async_adapter: AsyncProjectManagementAdapter) -> None:
        self._adapter = async_adapter

    def create_issue(self, project_key: str, issue: IssueSpec) -> IssueRef:
        return _run_sync(self._adapter.create_issue(project_key, issue))

    def get_issue(self, key: str) -> IssueDetail:
        return _run_sync(self._adapter.get_issue(key))

    def update_issue(self, key: str, fields: dict[str, Any]) -> IssueRef:
        return _run_sync(self._adapter.update_issue(key, fields))

    def transition_issue(self, key: str, status: str) -> IssueRef:
        return _run_sync(self._adapter.transition_issue(key, status))

    def batch_transition(self, keys: list[str], status: str) -> BatchResult:
        return _run_sync(self._adapter.batch_transition(keys, status))

    def link_to_parent(self, child_key: str, parent_key: str) -> None:
        _run_sync(self._adapter.link_to_parent(child_key, parent_key))

    def link_issues(self, source: str, target: str, link_type: str) -> None:
        _run_sync(self._adapter.link_issues(source, target, link_type))

    def add_comment(self, key: str, body: str) -> CommentRef:
        return _run_sync(self._adapter.add_comment(key, body))

    def get_comments(self, key: str, limit: int = 10) -> list[Comment]:
        return _run_sync(self._adapter.get_comments(key, limit))

    def search(self, query: str, limit: int = 50) -> list[IssueSummary]:
        return _run_sync(self._adapter.search(query, limit))

    def health(self) -> AdapterHealth:
        return _run_sync(self._adapter.health())


class SyncDocsAdapter:
    """Wraps ``AsyncDocumentationTarget`` for sync CLI consumption.

    Satisfies ``DocumentationTarget`` protocol via structural typing.
    Each method delegates to the async target via ``_run_sync()``.
    """

    def __init__(self, async_target: AsyncDocumentationTarget) -> None:
        self._target = async_target

    def can_publish(self, doc_type: str, metadata: dict[str, Any]) -> bool:
        return _run_sync(self._target.can_publish(doc_type, metadata))

    def publish(
        self, doc_type: str, content: str, metadata: dict[str, Any]
    ) -> PublishResult:
        return _run_sync(self._target.publish(doc_type, content, metadata))

    def get_page(self, identifier: str) -> PageContent:
        return _run_sync(self._target.get_page(identifier))

    def search(self, query: str, limit: int = 10) -> list[PageSummary]:
        return _run_sync(self._target.search(query, limit))

    def health(self) -> AdapterHealth:
        return _run_sync(self._target.health())
