"""Tests for generic entry-point resolver (resolve_entrypoint, resolve_adapter, resolve_docs_target).

Covers: D7 (generic resolver), MUST-4 (both backlog and docs use it).
Replaces test_adapter_resolve.py after _adapter_resolve.py → _resolve.py refactor.
"""

from __future__ import annotations

from typing import Any

import pytest

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
from rai_cli.adapters.protocols import DocumentationTarget, ProjectManagementAdapter
from rai_cli.adapters.sync import SyncDocsAdapter, SyncPMAdapter

# --- Stub adapters for tests ---

# Monkeypatch target for the generic resolver
_RESOLVE_MOD = "rai_cli.cli.commands._resolve"


class _StubAsyncPM:
    """Minimal async PM stub."""

    async def create_issue(self, project_key: str, issue: IssueSpec) -> IssueRef:
        return IssueRef(key=f"{project_key}-1")

    async def get_issue(self, key: str) -> IssueDetail:
        return IssueDetail(key=key, summary="Test", status="Open", issue_type="Task")

    async def update_issue(self, key: str, fields: dict[str, Any]) -> IssueRef:
        return IssueRef(key=key)

    async def transition_issue(self, key: str, status: str) -> IssueRef:
        return IssueRef(key=key)

    async def batch_transition(self, keys: list[str], status: str) -> BatchResult:
        return BatchResult(succeeded=[IssueRef(key=k) for k in keys])

    async def link_to_parent(self, child_key: str, parent_key: str) -> None:
        pass

    async def link_issues(self, source: str, target: str, link_type: str) -> None:
        pass

    async def add_comment(self, key: str, body: str) -> CommentRef:
        return CommentRef(id="1")

    async def get_comments(self, key: str, limit: int = 10) -> list[Comment]:
        return []

    async def search(self, query: str, limit: int = 50) -> list[IssueSummary]:
        return []

    async def health(self) -> AdapterHealth:
        return AdapterHealth(name="async-stub", healthy=True)


class _StubPM:
    """Minimal sync PM stub."""

    def create_issue(self, project_key: str, issue: IssueSpec) -> IssueRef:
        return IssueRef(key=f"{project_key}-1")

    def get_issue(self, key: str) -> IssueDetail:
        return IssueDetail(key=key, summary="Test", status="Open", issue_type="Task")

    def update_issue(self, key: str, fields: dict[str, Any]) -> IssueRef:
        return IssueRef(key=key)

    def transition_issue(self, key: str, status: str) -> IssueRef:
        return IssueRef(key=key)

    def batch_transition(self, keys: list[str], status: str) -> BatchResult:
        return BatchResult(succeeded=[IssueRef(key=k) for k in keys])

    def link_to_parent(self, child_key: str, parent_key: str) -> None:
        pass

    def link_issues(self, source: str, target: str, link_type: str) -> None:
        pass

    def add_comment(self, key: str, body: str) -> CommentRef:
        return CommentRef(id="1")

    def get_comments(self, key: str, limit: int = 10) -> list[Comment]:
        return []

    def search(self, query: str, limit: int = 50) -> list[IssueSummary]:
        return []

    def health(self) -> AdapterHealth:
        return AdapterHealth(name="stub", healthy=True)


class _StubAsyncDocs:
    """Minimal async docs target stub."""

    async def can_publish(self, doc_type: str, metadata: dict[str, Any]) -> bool:
        return True

    async def publish(
        self, doc_type: str, content: str, metadata: dict[str, Any]
    ) -> PublishResult:
        return PublishResult(success=True, url="https://example.com/page/1")

    async def get_page(self, identifier: str) -> PageContent:
        return PageContent(id=identifier, title="Test Page", content="# Test")

    async def search(self, query: str, limit: int = 10) -> list[PageSummary]:
        return []

    async def health(self) -> AdapterHealth:
        return AdapterHealth(name="async-docs-stub", healthy=True)


class _StubDocs:
    """Minimal sync docs target stub."""

    def can_publish(self, doc_type: str, metadata: dict[str, Any]) -> bool:
        return True

    def publish(
        self, doc_type: str, content: str, metadata: dict[str, Any]
    ) -> PublishResult:
        return PublishResult(success=True, url="https://example.com/page/1")

    def get_page(self, identifier: str) -> PageContent:
        return PageContent(id=identifier, title="Test Page", content="# Test")

    def search(self, query: str, limit: int = 10) -> list[PageSummary]:
        return []

    def health(self) -> AdapterHealth:
        return AdapterHealth(name="docs-stub", healthy=True)


# --- PM adapter tests (migrated from test_adapter_resolve.py) ---


class TestResolveAdapter:
    """resolve_adapter() — auto-detect logic for PM adapters."""

    def test_zero_adapters_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(f"{_RESOLVE_MOD}.get_pm_adapters", lambda: {})
        from rai_cli.cli.commands._resolve import resolve_adapter

        with pytest.raises(SystemExit) as exc_info:
            resolve_adapter(None)
        assert exc_info.value.code == 1

    def test_single_adapter_auto_selects(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(f"{_RESOLVE_MOD}.get_pm_adapters", lambda: {"stub": _StubPM})
        from rai_cli.cli.commands._resolve import resolve_adapter

        adapter = resolve_adapter(None)
        assert isinstance(adapter, ProjectManagementAdapter)

    def test_multiple_adapters_without_flag_raises(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            f"{_RESOLVE_MOD}.get_pm_adapters",
            lambda: {"jira": _StubPM, "github": _StubPM},
        )
        from rai_cli.cli.commands._resolve import resolve_adapter

        with pytest.raises(SystemExit) as exc_info:
            resolve_adapter(None)
        assert exc_info.value.code == 1

    def test_flag_override_selects_named(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            f"{_RESOLVE_MOD}.get_pm_adapters",
            lambda: {"jira": _StubPM, "github": _StubPM},
        )
        from rai_cli.cli.commands._resolve import resolve_adapter

        adapter = resolve_adapter("jira")
        assert isinstance(adapter, ProjectManagementAdapter)

    def test_flag_unknown_name_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(f"{_RESOLVE_MOD}.get_pm_adapters", lambda: {"jira": _StubPM})
        from rai_cli.cli.commands._resolve import resolve_adapter

        with pytest.raises(SystemExit) as exc_info:
            resolve_adapter("nonexistent")
        assert exc_info.value.code == 1

    def test_async_adapter_gets_wrapped(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            f"{_RESOLVE_MOD}.get_pm_adapters", lambda: {"async-jira": _StubAsyncPM}
        )
        from rai_cli.cli.commands._resolve import resolve_adapter

        adapter = resolve_adapter(None)
        assert isinstance(adapter, SyncPMAdapter)
        assert isinstance(adapter, ProjectManagementAdapter)

    def test_sync_adapter_not_wrapped(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            f"{_RESOLVE_MOD}.get_pm_adapters", lambda: {"sync-stub": _StubPM}
        )
        from rai_cli.cli.commands._resolve import resolve_adapter

        adapter = resolve_adapter(None)
        assert isinstance(adapter, _StubPM)
        assert not isinstance(adapter, SyncPMAdapter)


# --- Docs target tests (new) ---


class TestResolveDocsTarget:
    """resolve_docs_target() — auto-detect logic for docs targets."""

    def test_zero_targets_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(f"{_RESOLVE_MOD}.get_doc_targets", lambda: {})
        from rai_cli.cli.commands._resolve import resolve_docs_target

        with pytest.raises(SystemExit) as exc_info:
            resolve_docs_target(None)
        assert exc_info.value.code == 1

    def test_single_target_auto_selects(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            f"{_RESOLVE_MOD}.get_doc_targets", lambda: {"confluence": _StubDocs}
        )
        from rai_cli.cli.commands._resolve import resolve_docs_target

        target = resolve_docs_target(None)
        assert isinstance(target, DocumentationTarget)

    def test_multiple_targets_without_flag_raises(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            f"{_RESOLVE_MOD}.get_doc_targets",
            lambda: {"confluence": _StubDocs, "notion": _StubDocs},
        )
        from rai_cli.cli.commands._resolve import resolve_docs_target

        with pytest.raises(SystemExit) as exc_info:
            resolve_docs_target(None)
        assert exc_info.value.code == 1

    def test_flag_override_selects_named(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            f"{_RESOLVE_MOD}.get_doc_targets",
            lambda: {"confluence": _StubDocs, "notion": _StubDocs},
        )
        from rai_cli.cli.commands._resolve import resolve_docs_target

        target = resolve_docs_target("confluence")
        assert isinstance(target, DocumentationTarget)

    def test_async_target_gets_wrapped(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            f"{_RESOLVE_MOD}.get_doc_targets",
            lambda: {"async-confluence": _StubAsyncDocs},
        )
        from rai_cli.cli.commands._resolve import resolve_docs_target

        target = resolve_docs_target(None)
        assert isinstance(target, SyncDocsAdapter)
        assert isinstance(target, DocumentationTarget)

    def test_sync_target_not_wrapped(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            f"{_RESOLVE_MOD}.get_doc_targets", lambda: {"sync-stub": _StubDocs}
        )
        from rai_cli.cli.commands._resolve import resolve_docs_target

        target = resolve_docs_target(None)
        assert isinstance(target, _StubDocs)
        assert not isinstance(target, SyncDocsAdapter)
