"""Tests for artifact models."""

from __future__ import annotations

from datetime import datetime

import pytest
from pydantic import ValidationError

from raise_cli.artifacts.models import ArtifactRefs, ArtifactType, SkillArtifact


class TestArtifactType:
    def test_story_design_value(self) -> None:
        assert ArtifactType.STORY_DESIGN == "story-design"

    def test_str_returns_value(self) -> None:
        assert str(ArtifactType.STORY_DESIGN) == "story-design"


class TestArtifactRefs:
    def test_all_fields_optional(self) -> None:
        refs = ArtifactRefs()
        assert refs.backlog_item is None
        assert refs.epic_scope is None
        assert refs.related_artifacts == []

    def test_with_values(self) -> None:
        refs = ArtifactRefs(
            backlog_item="RAISE-402",
            epic_scope="work/epics/e354/scope.md",
            related_artifacts=["s354.2-design.yaml"],
        )
        assert refs.backlog_item == "RAISE-402"
        assert len(refs.related_artifacts) == 1


class TestSkillArtifact:
    def test_creation_with_all_fields(self, sample_created: datetime) -> None:
        artifact = SkillArtifact(
            artifact_type=ArtifactType.STORY_DESIGN,
            version=1,
            skill="rai-story-design",
            created=sample_created,
            story="S354.1",
            epic="E354",
            content={"summary": "test"},
            refs=ArtifactRefs(backlog_item="RAISE-402"),
        )
        assert artifact.artifact_type == ArtifactType.STORY_DESIGN
        assert artifact.version == 1
        assert artifact.skill == "rai-story-design"
        assert artifact.story == "S354.1"
        assert artifact.content == {"summary": "test"}

    def test_defaults(self, sample_created: datetime) -> None:
        artifact = SkillArtifact(
            artifact_type=ArtifactType.STORY_DESIGN,
            skill="rai-story-design",
            created=sample_created,
            content={},
        )
        assert artifact.version == 1
        assert artifact.story is None
        assert artifact.epic is None
        assert artifact.refs == ArtifactRefs()
        assert artifact.metadata == {}

    def test_version_must_be_positive(self, sample_created: datetime) -> None:
        with pytest.raises(ValidationError, match="greater than or equal to 1"):
            SkillArtifact(
                artifact_type=ArtifactType.STORY_DESIGN,
                version=0,
                skill="rai-story-design",
                created=sample_created,
                content={},
            )

    def test_artifact_type_required(self, sample_created: datetime) -> None:
        with pytest.raises(ValidationError):
            SkillArtifact(  # type: ignore[call-arg]
                skill="rai-story-design",
                created=sample_created,
                content={},
            )

    def test_model_dump_keys(self, sample_created: datetime) -> None:
        artifact = SkillArtifact(
            artifact_type=ArtifactType.STORY_DESIGN,
            skill="rai-story-design",
            created=sample_created,
            content={"summary": "test"},
        )
        data = artifact.model_dump()
        assert "artifact_type" in data
        assert "version" in data
        assert "content" in data
        assert "refs" in data
