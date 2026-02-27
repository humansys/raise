"""Tests for adapter Protocol contracts."""

from __future__ import annotations

from typing import Any

import pytest
from rai_core.graph.backends.models import BackendHealth
from rai_core.graph.backends.protocol import KnowledgeGraphBackend
from rai_core.graph.models import GraphNode

from rai_cli.adapters.models import (
    ArtifactLocator,
    IssueRef,
    IssueSpec,
    PublishResult,
)
from rai_cli.adapters.protocols import (
    DocumentationTarget,
    GovernanceParser,
    GovernanceSchemaProvider,
    ProjectManagementAdapter,
)
from rai_core.graph.backends.models import BackendHealth
from rai_core.graph.backends.protocol import KnowledgeGraphBackend
from rai_core.graph.models import GraphNode

# --- Conforming stubs ---


class StubPM:
    def create_issue(self, project_key: str, issue: IssueSpec) -> IssueRef:
        return IssueRef(key=f"{project_key}-1")

    def get_issue(self, ref: IssueRef) -> IssueRef:
        return ref

    def update_issue(self, ref: IssueRef, fields: dict[str, Any]) -> IssueRef:
        return ref

    def transition_issue(self, ref: IssueRef, transition: str) -> IssueRef:
        return ref


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


class StubDocTarget:
    def can_publish(self, doc_type: str, metadata: dict[str, Any]) -> bool:
        return doc_type == "architecture"

    def publish(
        self, doc_type: str, content: str, metadata: dict[str, Any]
    ) -> PublishResult:
        return PublishResult(success=True, url="https://docs.example.com")


class StubGraphBackend:
    def persist(self, graph: Any) -> None:
        pass

    def load(self) -> Any:
        return None

    def health(self) -> BackendHealth:
        return BackendHealth(status="healthy")


# --- Non-conforming stubs ---


class IncompletePM:
    """Only implements create_issue — missing 3 methods."""

    def create_issue(self, project_key: str, issue: IssueSpec) -> IssueRef:
        return IssueRef(key="X-1")


class IncompleteParser:
    """Only implements can_parse — missing parse."""

    def can_parse(self, locator: ArtifactLocator) -> bool:
        return True


# --- Tests ---


class TestProjectManagementAdapter:
    def test_conforming_stub_passes_isinstance(self) -> None:
        assert isinstance(StubPM(), ProjectManagementAdapter)

    def test_incomplete_fails_isinstance(self) -> None:
        assert not isinstance(IncompletePM(), ProjectManagementAdapter)


class TestGovernanceSchemaProvider:
    def test_conforming_stub_passes_isinstance(self) -> None:
        assert isinstance(StubSchemaProvider(), GovernanceSchemaProvider)


class TestGovernanceParser:
    def test_conforming_stub_passes_isinstance(self) -> None:
        assert isinstance(StubParser(), GovernanceParser)

    def test_incomplete_fails_isinstance(self) -> None:
        assert not isinstance(IncompleteParser(), GovernanceParser)


class TestDocumentationTarget:
    def test_conforming_stub_passes_isinstance(self) -> None:
        assert isinstance(StubDocTarget(), DocumentationTarget)


class TestKnowledgeGraphBackend:
    def test_conforming_stub_passes_isinstance(self) -> None:
        assert isinstance(StubGraphBackend(), KnowledgeGraphBackend)


class TestAllProtocolsAreRuntimeCheckable:
    """Verify all 5 Protocols have @runtime_checkable."""

    @pytest.mark.parametrize(
        "protocol_cls",
        [
            ProjectManagementAdapter,
            GovernanceSchemaProvider,
            GovernanceParser,
            DocumentationTarget,
            KnowledgeGraphBackend,
        ],
    )
    def test_is_runtime_checkable(self, protocol_cls: type) -> None:
        assert getattr(protocol_cls, "__protocol_attrs__", None) is not None
