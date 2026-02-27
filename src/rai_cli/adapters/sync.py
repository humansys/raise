"""Sync wrappers for async adapter protocols.

Bridges async adapters to sync consumption via ``asyncio.run()``.
CLI commands use these wrappers; async contexts consume adapters directly.

Usage::

    from rai_cli.adapters.sync import SyncPMAdapter

    async_adapter = JiraAdapter(config)
    sync_adapter = SyncPMAdapter(async_adapter)
    issue = sync_adapter.get_issue("RAISE-301")  # sync call
"""

from __future__ import annotations

import asyncio
from typing import Any

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


class SyncPMAdapter:
    """Wraps ``AsyncProjectManagementAdapter`` for sync CLI consumption.

    Satisfies ``ProjectManagementAdapter`` protocol via structural typing.
    Each method delegates to the async adapter via ``asyncio.run()``.
    """

    def __init__(self, async_adapter: AsyncProjectManagementAdapter) -> None:
        self._adapter = async_adapter

    def create_issue(self, project_key: str, issue: IssueSpec) -> IssueRef:
        return asyncio.run(self._adapter.create_issue(project_key, issue))

    def get_issue(self, key: str) -> IssueDetail:
        return asyncio.run(self._adapter.get_issue(key))

    def update_issue(self, key: str, fields: dict[str, Any]) -> IssueRef:
        return asyncio.run(self._adapter.update_issue(key, fields))

    def transition_issue(self, key: str, status: str) -> IssueRef:
        return asyncio.run(self._adapter.transition_issue(key, status))

    def batch_transition(self, keys: list[str], status: str) -> BatchResult:
        return asyncio.run(self._adapter.batch_transition(keys, status))

    def link_to_parent(self, child_key: str, parent_key: str) -> None:
        asyncio.run(self._adapter.link_to_parent(child_key, parent_key))

    def link_issues(self, source: str, target: str, link_type: str) -> None:
        asyncio.run(self._adapter.link_issues(source, target, link_type))

    def add_comment(self, key: str, body: str) -> CommentRef:
        return asyncio.run(self._adapter.add_comment(key, body))

    def get_comments(self, key: str, limit: int = 10) -> list[Comment]:
        return asyncio.run(self._adapter.get_comments(key, limit))

    def search(self, query: str, limit: int = 50) -> list[IssueSummary]:
        return asyncio.run(self._adapter.search(query, limit))

    def health(self) -> AdapterHealth:
        return asyncio.run(self._adapter.health())


class SyncDocsAdapter:
    """Wraps ``AsyncDocumentationTarget`` for sync CLI consumption.

    Satisfies ``DocumentationTarget`` protocol via structural typing.
    Each method delegates to the async target via ``asyncio.run()``.
    """

    def __init__(self, async_target: AsyncDocumentationTarget) -> None:
        self._target = async_target

    def can_publish(self, doc_type: str, metadata: dict[str, Any]) -> bool:
        return asyncio.run(self._target.can_publish(doc_type, metadata))

    def publish(
        self, doc_type: str, content: str, metadata: dict[str, Any]
    ) -> PublishResult:
        return asyncio.run(self._target.publish(doc_type, content, metadata))

    def get_page(self, identifier: str) -> PageContent:
        return asyncio.run(self._target.get_page(identifier))

    def search(self, query: str, limit: int = 10) -> list[PageSummary]:
        return asyncio.run(self._target.search(query, limit))

    def health(self) -> AdapterHealth:
        return asyncio.run(self._target.health())
