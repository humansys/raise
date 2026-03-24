"""Tests for sync adapter wrappers."""

from __future__ import annotations

import asyncio
from typing import Any

from raise_cli.adapters.models import (
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
from raise_cli.adapters.protocols import (
    DocumentationTarget,
    ProjectManagementAdapter,
)
from raise_cli.adapters.sync import SyncDocsAdapter, SyncPMAdapter, _run_sync

# --- Async mocks for wrapping ---


class FakeAsyncPM:
    """Minimal async PM adapter for testing sync wrapper delegation."""

    async def create_issue(self, project_key: str, issue: IssueSpec) -> IssueRef:
        return IssueRef(key=f"{project_key}-99")

    async def get_issue(self, key: str) -> IssueDetail:
        return IssueDetail(key=key, summary="Wrapped", status="Open", issue_type="Task")

    async def update_issue(self, key: str, fields: dict[str, Any]) -> IssueRef:
        return IssueRef(key=key)

    async def transition_issue(self, key: str, status: str) -> IssueRef:
        return IssueRef(key=key, metadata={"transitioned_to": status})

    async def batch_transition(self, keys: list[str], status: str) -> BatchResult:
        return BatchResult(succeeded=[IssueRef(key=k) for k in keys])

    async def link_to_parent(self, child_key: str, parent_key: str) -> None:
        pass

    async def link_issues(self, source: str, target: str, link_type: str) -> None:
        pass

    async def add_comment(self, key: str, body: str) -> CommentRef:
        return CommentRef(id="42", url=f"https://jira.example.com/{key}/comment/42")

    async def get_comments(self, key: str, limit: int = 10) -> list[Comment]:
        return [
            Comment(id="1", body="Hello", author="rai", created="2026-02-27T10:00:00Z")
        ]

    async def search(self, query: str, limit: int = 50) -> list[IssueSummary]:
        return [
            IssueSummary(key="R-1", summary="Found", status="Open", issue_type="Task")
        ]

    async def health(self) -> AdapterHealth:
        return AdapterHealth(name="fake-jira", healthy=True, latency_ms=10)


class FakeAsyncDocs:
    """Minimal async docs target for testing sync wrapper delegation."""

    async def can_publish(self, doc_type: str, metadata: dict[str, Any]) -> bool:
        return doc_type == "architecture"

    async def publish(
        self, doc_type: str, content: str, metadata: dict[str, Any]
    ) -> PublishResult:
        return PublishResult(success=True, url="https://wiki.example.com/1")

    async def get_page(self, identifier: str) -> PageContent:
        return PageContent(id=identifier, title="Wrapped Page", content="# Hello")

    async def search(self, query: str, limit: int = 10) -> list[PageSummary]:
        return [PageSummary(id="1", title="Found Page")]

    async def health(self) -> AdapterHealth:
        return AdapterHealth(name="fake-confluence", healthy=True)


# --- Tests ---


class TestSyncPMAdapter:
    def test_satisfies_sync_protocol(self) -> None:
        wrapper = SyncPMAdapter(FakeAsyncPM())
        assert isinstance(wrapper, ProjectManagementAdapter)

    def test_get_issue_delegates(self) -> None:
        wrapper = SyncPMAdapter(FakeAsyncPM())
        detail = wrapper.get_issue("RAISE-301")
        assert isinstance(detail, IssueDetail)
        assert detail.key == "RAISE-301"
        assert detail.summary == "Wrapped"

    def test_create_issue_delegates(self) -> None:
        wrapper = SyncPMAdapter(FakeAsyncPM())
        ref = wrapper.create_issue("RAISE", IssueSpec(summary="New issue"))
        assert ref.key == "RAISE-99"

    def test_transition_issue_delegates(self) -> None:
        wrapper = SyncPMAdapter(FakeAsyncPM())
        ref = wrapper.transition_issue("R-1", "done")
        assert ref.metadata["transitioned_to"] == "done"

    def test_batch_transition_delegates(self) -> None:
        wrapper = SyncPMAdapter(FakeAsyncPM())
        result = wrapper.batch_transition(["R-1", "R-2"], "done")
        assert len(result.succeeded) == 2

    def test_add_comment_delegates(self) -> None:
        wrapper = SyncPMAdapter(FakeAsyncPM())
        ref = wrapper.add_comment("R-1", "Nice work")
        assert ref.id == "42"

    def test_search_delegates(self) -> None:
        wrapper = SyncPMAdapter(FakeAsyncPM())
        results = wrapper.search("project = RAISE")
        assert len(results) == 1
        assert results[0].key == "R-1"

    def test_health_delegates(self) -> None:
        wrapper = SyncPMAdapter(FakeAsyncPM())
        h = wrapper.health()
        assert h.healthy is True
        assert h.name == "fake-jira"


class TestSyncDocsAdapter:
    def test_satisfies_sync_protocol(self) -> None:
        wrapper = SyncDocsAdapter(FakeAsyncDocs())
        assert isinstance(wrapper, DocumentationTarget)

    def test_can_publish_delegates(self) -> None:
        wrapper = SyncDocsAdapter(FakeAsyncDocs())
        assert wrapper.can_publish("architecture", {}) is True
        assert wrapper.can_publish("unknown", {}) is False

    def test_get_page_delegates(self) -> None:
        wrapper = SyncDocsAdapter(FakeAsyncDocs())
        page = wrapper.get_page("123")
        assert isinstance(page, PageContent)
        assert page.id == "123"
        assert page.title == "Wrapped Page"

    def test_search_delegates(self) -> None:
        wrapper = SyncDocsAdapter(FakeAsyncDocs())
        results = wrapper.search("architecture")
        assert len(results) == 1

    def test_health_delegates(self) -> None:
        wrapper = SyncDocsAdapter(FakeAsyncDocs())
        h = wrapper.health()
        assert h.healthy is True


class TestRunSyncCloseable:
    """RAISE-324: _run_sync calls aclose() on closeable within the same event loop."""

    def test_aclose_called_on_success(self) -> None:
        """closeable.aclose() is called after successful coroutine."""
        calls: list[str] = []

        class Closeable:
            async def aclose(self) -> None:
                calls.append("closed")

        async def _work() -> str:
            return "done"

        result = _run_sync(_work(), closeable=Closeable())
        assert result == "done"
        assert calls == ["closed"]

    def test_aclose_called_on_failure(self) -> None:
        """closeable.aclose() is called even when coroutine raises."""
        calls: list[str] = []

        class Closeable:
            async def aclose(self) -> None:
                calls.append("closed")

        async def _fail() -> None:
            msg = "boom"
            raise RuntimeError(msg)

        import pytest

        with pytest.raises(RuntimeError, match="boom"):
            _run_sync(_fail(), closeable=Closeable())
        assert calls == ["closed"]

    def test_no_closeable_still_works(self) -> None:
        """_run_sync works without closeable (backwards compat)."""

        async def _work() -> int:
            return 42

        assert _run_sync(_work()) == 42

    def test_closeable_without_aclose_ignored(self) -> None:
        """Objects without aclose() are silently ignored."""

        async def _work() -> str:
            return "ok"

        result = _run_sync(_work(), closeable=object())
        assert result == "ok"

    def test_pm_wrapper_calls_aclose(self) -> None:
        """SyncPMAdapter passes adapter as closeable so aclose() runs."""
        calls: list[str] = []
        fake = FakeAsyncPM()

        async def _aclose() -> None:
            calls.append("closed")

        fake.aclose = _aclose  # type: ignore[attr-defined]

        wrapper = SyncPMAdapter(fake)
        results = wrapper.search("project = RAISE")
        assert len(results) == 1
        assert calls == ["closed"]


class TestRunSyncFromAsyncContext:
    """C1 fix: verify wrappers work when called from within a running event loop."""

    def test_pm_wrapper_from_async_context(self) -> None:
        async def _inner() -> IssueDetail:
            wrapper = SyncPMAdapter(FakeAsyncPM())
            return wrapper.get_issue("R-1")

        detail = asyncio.run(_inner())
        assert detail.key == "R-1"
        assert detail.summary == "Wrapped"

    def test_docs_wrapper_from_async_context(self) -> None:
        async def _inner() -> PageContent:
            wrapper = SyncDocsAdapter(FakeAsyncDocs())
            return wrapper.get_page("42")

        page = asyncio.run(_inner())
        assert page.id == "42"
        assert page.title == "Wrapped Page"
