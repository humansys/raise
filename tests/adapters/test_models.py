"""Tests for adapter boundary models."""

from __future__ import annotations

import pytest
from pydantic import BaseModel, ValidationError

from rai_cli.adapters.models import (
    ArtifactLocator,
    BackendHealth,
    CoreArtifactType,
    IssueRef,
    IssueSpec,
    PublishResult,
)


class TestCoreArtifactType:
    """CoreArtifactType StrEnum tests."""

    def test_all_nine_members_exist(self) -> None:
        assert len(CoreArtifactType) == 9

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

    def test_construct_with_metadata(self) -> None:
        loc = ArtifactLocator(
            path="dev/decisions/adr-033.md",
            artifact_type=CoreArtifactType.ADR,
            metadata={"version": "v2"},
        )
        assert loc.metadata == {"version": "v2"}

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

    def test_full_construction(self) -> None:
        spec = IssueSpec(
            summary="Add dark mode",
            description="## Details\nImplement theme toggle",
            issue_type="Story",
            labels=["frontend", "ux"],
            metadata={"priority": "High"},
        )
        assert spec.issue_type == "Story"
        assert len(spec.labels) == 2

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

    def test_full_construction(self) -> None:
        ref = IssueRef(
            key="PROJ-456",
            url="https://jira.example.com/browse/PROJ-456",
            metadata={"status": "Open"},
        )
        assert ref.url.startswith("https://")

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

    def test_degraded_with_details(self) -> None:
        health = BackendHealth(
            status="degraded",
            message="High latency",
            metadata={"latency_ms": 2500},
        )
        assert health.status == "degraded"
        assert health.metadata["latency_ms"] == 2500

    def test_roundtrip(self) -> None:
        health = BackendHealth(status="unavailable", message="Connection refused")
        rebuilt = BackendHealth.model_validate(health.model_dump())
        assert rebuilt == health


class TestAllModelsAreBaseModel:
    """Guardrail: All models inherit BaseModel (guardrail-must-arch-002)."""

    @pytest.mark.parametrize(
        "model_cls",
        [ArtifactLocator, IssueSpec, IssueRef, PublishResult, BackendHealth],
    )
    def test_inherits_base_model(self, model_cls: type) -> None:
        assert issubclass(model_cls, BaseModel)
