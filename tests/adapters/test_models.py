"""Tests for adapter boundary models."""

from __future__ import annotations

import pytest
from pydantic import BaseModel, ValidationError

from raise_cli.adapters.models import (
    AdapterHealth,
    ArtifactLocator,
    BatchResult,
    Comment,
    CommentRef,
    CoreArtifactType,
    FailureDetail,
    IssueDetail,
    IssueRef,
    IssueSpec,
    IssueSummary,
    PageContent,
    PageSummary,
    PublishResult,
)
from raise_core.graph.backends.models import BackendHealth


class TestCoreArtifactType:
    """CoreArtifactType StrEnum tests."""

    def test_values_are_lowercase_strings(self) -> None:
        assert CoreArtifactType.BACKLOG == "backlog"
        assert CoreArtifactType.ADR == "adr"
        assert CoreArtifactType.CONSTITUTION == "constitution"
        assert CoreArtifactType.PRD == "prd"
        assert CoreArtifactType.VISION == "vision"
        assert CoreArtifactType.GUARDRAILS == "guardrails"
        assert CoreArtifactType.GLOSSARY == "glossary"
        assert CoreArtifactType.ROADMAP == "roadmap"
        assert CoreArtifactType.EPIC_SCOPE == "epic_scope"

    def test_is_str_subclass(self) -> None:
        """StrEnum members are usable as plain strings."""
        artifact_type: str = CoreArtifactType.BACKLOG
        assert isinstance(artifact_type, str)


class TestArtifactLocator:
    """ArtifactLocator model tests."""

    def test_construct_with_required_fields(self) -> None:
        loc = ArtifactLocator(path="governance/backlog.md", artifact_type="backlog")
        assert loc.path == "governance/backlog.md"
        assert loc.artifact_type == "backlog"
        assert loc.metadata == {}

    def test_missing_required_field_raises(self) -> None:
        with pytest.raises(ValidationError):
            ArtifactLocator(artifact_type="backlog")  # type: ignore[call-arg]

    def test_roundtrip(self) -> None:
        loc = ArtifactLocator(path="governance/prd.md", artifact_type="prd")
        rebuilt = ArtifactLocator.model_validate(loc.model_dump())
        assert rebuilt == loc


class TestIssueSpec:
    """IssueSpec model tests."""

    def test_minimal_construction(self) -> None:
        spec = IssueSpec(summary="Fix login bug")
        assert spec.summary == "Fix login bug"
        assert spec.description == ""
        assert spec.issue_type == "Task"
        assert spec.labels == []
        assert spec.metadata == {}

    def test_summary_required(self) -> None:
        with pytest.raises(ValidationError):
            IssueSpec()  # type: ignore[call-arg]


class TestIssueRef:
    """IssueRef model tests."""

    def test_minimal_construction(self) -> None:
        ref = IssueRef(key="PROJ-123")
        assert ref.key == "PROJ-123"
        assert ref.url == ""
        assert ref.metadata == {}

    def test_key_required(self) -> None:
        with pytest.raises(ValidationError):
            IssueRef()  # type: ignore[call-arg]


class TestPublishResult:
    """PublishResult model tests."""

    def test_success_result(self) -> None:
        result = PublishResult(success=True, url="https://docs.example.com/page")
        assert result.success is True
        assert result.message == ""

    def test_failure_result(self) -> None:
        result = PublishResult(success=False, message="Authentication failed")
        assert result.success is False
        assert result.url == ""

    def test_roundtrip(self) -> None:
        result = PublishResult(success=True, url="https://x.com", message="OK")
        rebuilt = PublishResult.model_validate(result.model_dump())
        assert rebuilt == result


class TestBackendHealth:
    """BackendHealth model tests."""

    def test_healthy(self) -> None:
        health = BackendHealth(status="healthy")
        assert health.status == "healthy"
        assert health.message == ""
        assert health.metadata == {}

    def test_roundtrip(self) -> None:
        health = BackendHealth(status="unavailable", message="Connection refused")
        rebuilt = BackendHealth.model_validate(health.model_dump())
        assert rebuilt == health


class TestIssueDetail:
    """IssueDetail model tests — extends IssueRef."""

    def test_minimal_construction(self) -> None:
        detail = IssueDetail(
            key="RAISE-301",
            summary="Agent Tool Abstraction",
            status="In Progress",
            issue_type="Epic",
        )
        assert detail.key == "RAISE-301"
        assert detail.summary == "Agent Tool Abstraction"
        assert detail.status == "In Progress"
        assert detail.issue_type == "Epic"
        # Defaults
        assert detail.description == ""
        assert detail.parent_key is None
        assert detail.labels == []
        assert detail.assignee is None
        assert detail.priority is None
        assert detail.created == ""
        assert detail.updated == ""
        # Inherited from IssueRef
        assert detail.url == ""
        assert detail.metadata == {}

    def test_liskov_substitution(self) -> None:
        """IssueDetail is a valid IssueRef — Liskov holds."""
        detail = IssueDetail(key="R-1", summary="X", status="Open", issue_type="Story")
        ref: IssueRef = detail
        assert isinstance(ref, IssueRef)
        assert ref.key == "R-1"

    def test_inherits_issueref(self) -> None:
        assert issubclass(IssueDetail, IssueRef)

    def test_required_fields(self) -> None:
        with pytest.raises(ValidationError):
            IssueDetail(key="R-1")  # type: ignore[call-arg]

    def test_roundtrip(self) -> None:
        detail = IssueDetail(
            key="R-1",
            summary="Test",
            status="Done",
            issue_type="Task",
            labels=["a", "b"],
            created="2026-02-27T10:30:00Z",
        )
        rebuilt = IssueDetail.model_validate(detail.model_dump())
        assert rebuilt == detail


class TestIssueSummary:
    """IssueSummary model tests."""

    def test_minimal_construction(self) -> None:
        summary = IssueSummary(
            key="R-1", summary="Fix bug", status="Open", issue_type="Bug"
        )
        assert summary.key == "R-1"
        assert summary.parent_key is None

    def test_required_fields(self) -> None:
        with pytest.raises(ValidationError):
            IssueSummary(key="R-1")  # type: ignore[call-arg]


class TestComment:
    """Comment model tests."""

    def test_construction(self) -> None:
        comment = Comment(
            id="10001",
            body="Looks good",
            author="emilio",
            created="2026-02-27T10:00:00Z",
        )
        assert comment.id == "10001"
        assert comment.body == "Looks good"
        assert comment.author == "emilio"
        assert comment.created == "2026-02-27T10:00:00Z"

    def test_all_fields_required(self) -> None:
        with pytest.raises(ValidationError):
            Comment(id="1", body="x")  # type: ignore[call-arg]


class TestCommentRef:
    """CommentRef model tests."""

    def test_minimal_construction(self) -> None:
        ref = CommentRef(id="10001")
        assert ref.id == "10001"
        assert ref.url == ""

    def test_with_url(self) -> None:
        ref = CommentRef(id="1", url="https://jira.example.com/comment/1")
        assert ref.url == "https://jira.example.com/comment/1"


class TestFailureDetail:
    """FailureDetail model tests."""

    def test_construction(self) -> None:
        f = FailureDetail(key="R-3", error="not found")
        assert f.key == "R-3"
        assert f.error == "not found"

    def test_required_fields(self) -> None:
        with pytest.raises(ValidationError):
            FailureDetail(key="R-3")  # type: ignore[call-arg]


class TestBatchResult:
    """BatchResult model tests."""

    def test_empty_defaults(self) -> None:
        result = BatchResult()
        assert result.succeeded == []
        assert result.failed == []

    def test_with_successes_and_failures(self) -> None:
        result = BatchResult(
            succeeded=[IssueRef(key="R-1"), IssueRef(key="R-2")],
            failed=[FailureDetail(key="R-3", error="not found")],
        )
        assert len(result.succeeded) == 2
        assert result.failed[0].key == "R-3"
        assert result.failed[0].error == "not found"

    def test_roundtrip(self) -> None:
        result = BatchResult(
            succeeded=[IssueRef(key="R-1")],
            failed=[FailureDetail(key="R-2", error="timeout")],
        )
        rebuilt = BatchResult.model_validate(result.model_dump())
        assert rebuilt == result


class TestPageContent:
    """PageContent model tests."""

    def test_minimal_construction(self) -> None:
        page = PageContent(id="123", title="Arch Overview", content="# Heading")
        assert page.id == "123"
        assert page.content == "# Heading"
        assert page.url == ""
        assert page.space_key == ""
        assert page.version == 1

    def test_required_fields(self) -> None:
        with pytest.raises(ValidationError):
            PageContent(id="123")  # type: ignore[call-arg]


class TestPageSummary:
    """PageSummary model tests."""

    def test_minimal_construction(self) -> None:
        ps = PageSummary(id="123", title="Overview")
        assert ps.url == ""
        assert ps.space_key == ""
        assert ps.updated == ""

    def test_with_all_fields(self) -> None:
        ps = PageSummary(
            id="123",
            title="Overview",
            url="https://wiki.example.com/123",
            space_key="DEV",
            updated="2026-02-27T10:00:00Z",
        )
        assert ps.space_key == "DEV"


class TestAdapterHealth:
    """AdapterHealth model tests."""

    def test_healthy(self) -> None:
        h = AdapterHealth(name="jira", healthy=True, latency_ms=42)
        assert h.name == "jira"
        assert h.healthy is True
        assert h.message == ""
        assert h.latency_ms == 42

    def test_unhealthy(self) -> None:
        h = AdapterHealth(
            name="confluence", healthy=False, message="Connection refused"
        )
        assert h.healthy is False
        assert h.latency_ms is None

    def test_required_fields(self) -> None:
        with pytest.raises(ValidationError):
            AdapterHealth(name="jira")  # type: ignore[call-arg]


class TestAllModelsAreBaseModel:
    """Guardrail: All models inherit BaseModel (guardrail-must-arch-002)."""

    @pytest.mark.parametrize(
        "model_cls",
        [
            ArtifactLocator,
            IssueSpec,
            IssueRef,
            PublishResult,
            BackendHealth,
            IssueDetail,
            IssueSummary,
            Comment,
            CommentRef,
            FailureDetail,
            BatchResult,
            PageContent,
            PageSummary,
            AdapterHealth,
        ],
    )
    def test_inherits_base_model(self, model_cls: type) -> None:
        assert issubclass(model_cls, BaseModel)
