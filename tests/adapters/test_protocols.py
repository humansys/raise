"""Tests for adapter Protocol contracts."""

from __future__ import annotations

import asyncio
from typing import Any

import pytest

from raise_cli.adapters.models import (
    AdapterHealth,
    ArtifactLocator,
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
    AsyncDocumentationTarget,
    AsyncProjectManagementAdapter,
    DocumentationTarget,
    GovernanceParser,
    GovernanceSchemaProvider,
    ProjectManagementAdapter,
)
from raise_core.graph.backends.models import BackendHealth
from raise_core.graph.backends.protocol import KnowledgeGraphBackend
from raise_core.graph.models import GraphNode

# --- Conforming sync stubs (updated signatures) ---


class StubPM:
    """Sync PM stub — satisfies ProjectManagementAdapter (11 methods)."""

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


class StubDocTarget:
    """Sync docs stub — satisfies DocumentationTarget (5 methods)."""

    def can_publish(self, doc_type: str, metadata: dict[str, Any]) -> bool:
        return doc_type == "architecture"

    def publish(
        self, doc_type: str, content: str, metadata: dict[str, Any]
    ) -> PublishResult:
        return PublishResult(success=True, url="https://docs.example.com")

    def get_page(self, identifier: str) -> PageContent:
        return PageContent(id="1", title="Test", content="# Test")

    def search(self, query: str, limit: int = 10) -> list[PageSummary]:
        return []

    def health(self) -> AdapterHealth:
        return AdapterHealth(name="stub-docs", healthy=True)


# --- Conforming async stubs ---


class StubAsyncPM:
    """Async PM stub — satisfies AsyncProjectManagementAdapter (11 methods)."""

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


class StubAsyncDocTarget:
    """Async docs stub — satisfies AsyncDocumentationTarget (5 methods)."""

    async def can_publish(self, doc_type: str, metadata: dict[str, Any]) -> bool:
        return doc_type == "architecture"

    async def publish(
        self, doc_type: str, content: str, metadata: dict[str, Any]
    ) -> PublishResult:
        return PublishResult(success=True, url="https://docs.example.com")

    async def get_page(self, identifier: str) -> PageContent:
        return PageContent(id="1", title="Test", content="# Test")

    async def search(self, query: str, limit: int = 10) -> list[PageSummary]:
        return []

    async def health(self) -> AdapterHealth:
        return AdapterHealth(name="async-docs-stub", healthy=True)


# --- Unchanged governance stubs ---


class StubSchemaProvider:
    def list_artifact_types(self) -> list[str]:
        return ["backlog", "adr"]

    def locate(self, artifact_type: str) -> list[ArtifactLocator]:
        return [
            ArtifactLocator(path="governance/backlog.md", artifact_type=artifact_type)
        ]


class StubParser:
    def can_parse(self, locator: ArtifactLocator) -> bool:
        return locator.artifact_type == "backlog"

    def parse(self, locator: ArtifactLocator) -> list[GraphNode]:
        return [GraphNode(id="test-1", content="Test concept", created="2026-01-01")]


class StubGraphBackend:
    def persist(self, graph: Any) -> None:
        pass

    def load(self) -> Any:
        return None

    def health(self) -> BackendHealth:
        return BackendHealth(status="healthy")


# --- Non-conforming stubs ---


class IncompletePM:
    """Only implements create_issue — missing 10 methods."""

    def create_issue(self, project_key: str, issue: IssueSpec) -> IssueRef:
        return IssueRef(key="X-1")


class IncompleteAsyncPM:
    """Only implements async create_issue — missing 10 methods."""

    async def create_issue(self, project_key: str, issue: IssueSpec) -> IssueRef:
        return IssueRef(key="X-1")


class IncompleteParser:
    """Only implements can_parse — missing parse."""

    def can_parse(self, locator: ArtifactLocator) -> bool:
        return True


# --- Sync protocol tests ---


class TestProjectManagementAdapter:
    def test_conforming_stub_passes_isinstance(self) -> None:
        assert isinstance(StubPM(), ProjectManagementAdapter)

    def test_incomplete_fails_isinstance(self) -> None:
        assert not isinstance(IncompletePM(), ProjectManagementAdapter)

    def test_stub_returns_correct_types(self) -> None:
        pm = StubPM()
        detail = pm.get_issue("R-1")
        assert isinstance(detail, IssueDetail)
        assert detail.key == "R-1"

        batch = pm.batch_transition(["R-1", "R-2"], "done")
        assert len(batch.succeeded) == 2

        health = pm.health()
        assert health.healthy is True


class TestDocumentationTarget:
    def test_conforming_stub_passes_isinstance(self) -> None:
        assert isinstance(StubDocTarget(), DocumentationTarget)

    def test_stub_returns_correct_types(self) -> None:
        doc = StubDocTarget()
        page = doc.get_page("123")
        assert isinstance(page, PageContent)

        health = doc.health()
        assert health.healthy is True


# --- Async protocol tests ---


class TestAsyncProjectManagementAdapter:
    def test_conforming_stub_passes_isinstance(self) -> None:
        assert isinstance(StubAsyncPM(), AsyncProjectManagementAdapter)

    def test_incomplete_fails_isinstance(self) -> None:
        assert not isinstance(IncompleteAsyncPM(), AsyncProjectManagementAdapter)

    def test_stub_returns_correct_types(self) -> None:
        pm = StubAsyncPM()
        detail = asyncio.run(pm.get_issue("R-1"))
        assert isinstance(detail, IssueDetail)
        assert detail.key == "R-1"

        batch = asyncio.run(pm.batch_transition(["R-1", "R-2"], "done"))
        assert len(batch.succeeded) == 2

        health = asyncio.run(pm.health())
        assert health.healthy is True


class TestAsyncDocumentationTarget:
    def test_conforming_stub_passes_isinstance(self) -> None:
        assert isinstance(StubAsyncDocTarget(), AsyncDocumentationTarget)

    def test_stub_returns_correct_types(self) -> None:
        doc = StubAsyncDocTarget()
        page = asyncio.run(doc.get_page("123"))
        assert isinstance(page, PageContent)

        health = asyncio.run(doc.health())
        assert health.healthy is True


# --- Unchanged protocol tests ---


class TestGovernanceSchemaProvider:
    def test_conforming_stub_passes_isinstance(self) -> None:
        assert isinstance(StubSchemaProvider(), GovernanceSchemaProvider)


class TestGovernanceParser:
    def test_conforming_stub_passes_isinstance(self) -> None:
        assert isinstance(StubParser(), GovernanceParser)

    def test_incomplete_fails_isinstance(self) -> None:
        assert not isinstance(IncompleteParser(), GovernanceParser)


class TestKnowledgeGraphBackend:
    def test_conforming_stub_passes_isinstance(self) -> None:
        assert isinstance(StubGraphBackend(), KnowledgeGraphBackend)


class TestAllProtocolsAreRuntimeCheckable:
    """Verify all 7 Protocols have @runtime_checkable."""

    @pytest.mark.parametrize(
        "protocol_cls",
        [
            ProjectManagementAdapter,
            AsyncProjectManagementAdapter,
            GovernanceSchemaProvider,
            GovernanceParser,
            DocumentationTarget,
            AsyncDocumentationTarget,
            KnowledgeGraphBackend,
        ],
    )
    def test_is_runtime_checkable(self, protocol_cls: type) -> None:
        assert getattr(protocol_cls, "__protocol_attrs__", None) is not None
