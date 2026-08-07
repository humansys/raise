"""LedgerAwareAdapter — transparent key translation via WorkItemStore.

Wraps any ProjectManagementAdapter and translates local keys (E1700, S1700.3)
to remote keys (RAISE-1784) before delegating. Pass-through if key not in store.

Inspired by Terraform state binding pattern: local logical name → remote physical ID.

Story: S1700.4 | Epic: E1700 Adapter Migration Path
"""

from __future__ import annotations

import logging
from collections.abc import Callable
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
    ProjectVersion,
    WorkflowState,
)
from raise_cli.storage.work_items import WorkItemStore

logger = logging.getLogger(__name__)


class LedgerAwareAdapter:
    """Translates local keys via WorkItemStore before delegating to remote.

    - If key is in work_items → translate to jira_key, then delegate
    - If key is not in work_items → pass-through (might be a remote key already)
    """

    def __init__(self, remote: Any, store: WorkItemStore) -> None:
        self._remote = remote
        self._store = store

    @property
    def remote(self) -> Any:
        """Wrapped remote adapter."""
        return self._remote

    def _resolve(self, key: str) -> str:
        """Translate local key to remote key, or pass-through."""
        return self._store.get_jira_key(key) or key

    # -- Write ops (key-translated) ------------------------------------------

    def create_issue(self, project_key: str, issue: IssueSpec) -> IssueRef:
        """Create on remote, translating local parent key via ledger if present."""
        if issue.parent is not None:
            issue = issue.model_copy(update={"parent": self._resolve(issue.parent)})
        return self._remote.create_issue(project_key, issue)  # type: ignore[no-any-return]

    def update_issue(self, key: str, fields: dict[str, Any]) -> IssueRef:
        """Translate key, then update on remote."""
        return self._remote.update_issue(self._resolve(key), fields)  # type: ignore[no-any-return]

    def transition_issue(self, key: str, status: str) -> IssueRef:
        """Translate key, then transition on remote."""
        return self._remote.transition_issue(self._resolve(key), status)  # type: ignore[no-any-return]

    def batch_transition(self, keys: list[str], status: str) -> BatchResult:
        """Translate all keys, then batch transition on remote."""
        resolved = [self._resolve(k) for k in keys]
        return self._remote.batch_transition(resolved, status)  # type: ignore[no-any-return]

    def link_to_parent(self, child_key: str, parent_key: str) -> bool:
        """Translate both keys, then link on remote."""
        return self._remote.link_to_parent(  # type: ignore[no-any-return]
            self._resolve(child_key), self._resolve(parent_key)
        )

    def link_issues(self, source: str, target: str, link_type: str) -> bool:
        """Translate both keys, then link on remote."""
        return self._remote.link_issues(
            self._resolve(source), self._resolve(target), link_type
        )

    def batch_create(self, issues: list[IssueSpec]) -> BatchResult:
        """Delegate batch create to remote (keys assigned by remote)."""
        return self._remote.batch_create(issues)  # type: ignore[no-any-return]

    def remove_link(self, link_id: str) -> None:
        """Delegate to remote — link IDs are remote-native."""
        self._remote.remove_link(link_id)

    def add_comment(self, key: str, body: str) -> CommentRef:
        """Translate key, then add comment on remote."""
        return self._remote.add_comment(self._resolve(key), body)  # type: ignore[no-any-return]

    # -- Read ops (key-translated) -------------------------------------------

    def get_issue(self, key: str) -> IssueDetail:
        """Translate key, then fetch from remote."""
        return self._remote.get_issue(self._resolve(key))  # type: ignore[no-any-return]

    def get_comments(
        self, key: str, limit: int = 10, offset: int = 0, fetch_all: bool = False
    ) -> list[Comment]:
        """Translate key, then fetch comments from remote."""
        return self._remote.get_comments(
            self._resolve(key), limit=limit, offset=offset, fetch_all=fetch_all
        )  # type: ignore[no-any-return]

    def search(
        self, query: str, limit: int = 50, offset: int = 0, fetch_all: bool = False
    ) -> list[IssueSummary]:
        """Pass query through to remote (JQL, no key translation)."""
        return self._remote.search(
            query, limit=limit, offset=offset, fetch_all=fetch_all
        )  # type: ignore[no-any-return]

    def health(self) -> AdapterHealth:
        """Delegate health check to remote."""
        return self._remote.health()  # type: ignore[no-any-return]

    def discover_fields(self, project_key: str) -> list[FieldDefinition]:
        """Delegate to remote adapter."""
        return self._remote.discover_fields(project_key)  # type: ignore[no-any-return]

    def discover_statuses(
        self, project_key: str, issue_type: str = "Story"
    ) -> list[WorkflowState]:
        """Delegate to remote adapter."""
        return self._remote.discover_statuses(project_key, issue_type=issue_type)  # type: ignore[no-any-return]

    def discover_link_types(self) -> list[LinkTypeDefinition]:
        """Delegate to remote adapter."""
        return self._remote.discover_link_types()  # type: ignore[no-any-return]

    def discover_issue_types(self, project_key: str) -> list[IssueTypeInfo]:
        """Delegate to remote adapter."""
        return self._remote.discover_issue_types(project_key)  # type: ignore[no-any-return]

    def discover_named_fields(
        self, names: list[str], issue_type: str, project_key: str | None = None
    ) -> list[CustomField]:
        """Delegate to remote adapter."""
        return self._remote.discover_named_fields(  # type: ignore[no-any-return]
            names, issue_type, project_key=project_key
        )

    # ── Project versions / fixVersions ──────────────────────────────

    def _remote_version_op(self, operation: str) -> Callable[..., Any]:
        """Return a supported project-version operation from the wrapped remote."""
        method = getattr(self._remote, operation, None)
        if not callable(method):
            raise NotImplementedError(
                f"Wrapped remote adapter does not support {operation}()"
            )
        return method

    def list_versions(self, project_key: str) -> list[ProjectVersion]:
        """Delegate project version discovery to remote adapter."""
        return self._remote_version_op("list_versions")(project_key)  # type: ignore[no-any-return]

    def create_version(self, project_key: str, name: str) -> ProjectVersion:
        """Delegate project version creation to remote adapter."""
        return self._remote_version_op("create_version")(project_key, name)  # type: ignore[no-any-return]

    # ── Attachments (S2503.7) ────────────────────────────────────────

    def attach(
        self, key: str, path: Path, mime_type: str | None = None
    ) -> AttachmentRef:
        """Delegate to remote adapter (key translated if in ledger)."""
        remote_key = self._store.get_jira_key(key) or key
        return self._remote.attach(remote_key, path, mime_type)  # type: ignore[no-any-return]

    def get_attachments(self, key: str) -> list[AttachmentDetail]:
        """Delegate to remote adapter (key translated if in ledger)."""
        remote_key = self._store.get_jira_key(key) or key
        return self._remote.get_attachments(remote_key)  # type: ignore[no-any-return]

    def download_attachment(self, attachment_id: str) -> bytes:
        """Delegate to remote adapter (attachment IDs are global, no translation)."""
        return self._remote.download_attachment(attachment_id)  # type: ignore[no-any-return]

    # ── Sprint (Jira-specific) ───────────────────────────────────────

    def get_sprints(self, project_key: str, state: str | None = None) -> list[Any]:
        """Delegate to remote adapter."""
        return self._remote.get_sprints(project_key, state=state)  # type: ignore[no-any-return]

    def assign_to_sprint(self, issue_key: str, sprint_id: int) -> None:
        """Delegate to remote adapter (key translated if in store)."""
        remote_key = self._store.get_jira_key(issue_key) or issue_key
        self._remote.assign_to_sprint(remote_key, sprint_id)
