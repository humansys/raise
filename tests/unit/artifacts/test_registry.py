"""Tests for artifact type registry dispatch in reader."""

from __future__ import annotations

from datetime import datetime

import pytest
from pydantic import ValidationError

from raise_cli.artifacts.models import ArtifactType, SkillArtifact
from raise_cli.artifacts.reader import read_artifact
from raise_cli.artifacts.story_design import (
    AcceptanceCriterion,
    Complexity,
    StoryDesignArtifact,
    StoryDesignContent,
)
from raise_cli.artifacts.writer import write_artifact


class TestRegistryDispatch:
    def test_dispatches_to_story_design(
        self, project_root, sample_created: datetime
    ) -> None:
        artifact = StoryDesignArtifact(
            skill="rai-story-design",
            created=sample_created,
            story="S354.2",
            content=StoryDesignContent(
                summary="Test dispatch",
                complexity=Complexity.SIMPLE,
                acceptance_criteria=[
                    AcceptanceCriterion(id="AC1", description="Works"),
                ],
            ),
        )
        path = write_artifact(artifact, project_root)
        loaded = read_artifact(path)
        assert isinstance(loaded, StoryDesignArtifact)
        assert isinstance(loaded.content, StoryDesignContent)
        assert loaded.content.summary == "Test dispatch"

    def test_unknown_type_raises_validation_error(
        self, project_root, sample_created: datetime
    ) -> None:
        artifact = SkillArtifact(
            artifact_type=ArtifactType.STORY_DESIGN,
            skill="unknown-skill",
            created=sample_created,
            content={"custom": "data"},
        )
        path = write_artifact(artifact, project_root)
        # Manually change type to something not in the enum
        text = path.read_text().replace("story-design", "unknown-type")
        path.write_text(text)

        with pytest.raises(ValidationError):
            read_artifact(path)

    def test_roundtrip_with_typed_artifact(
        self, project_root, sample_created: datetime
    ) -> None:
        original = StoryDesignArtifact(
            skill="rai-story-design",
            created=sample_created,
            story="S354.2",
            epic="E354",
            content=StoryDesignContent(
                summary="Round-trip test",
                complexity=Complexity.MODERATE,
                acceptance_criteria=[
                    AcceptanceCriterion(id="AC1", description="Validates"),
                    AcceptanceCriterion(id="AC2", description="Persists"),
                ],
                decisions=[
                    {
                        "id": "D1",
                        "choice": "Registry",
                        "rationale": "Simple dispatch",
                    },
                ],
            ),
        )
        path = write_artifact(original, project_root)
        loaded = read_artifact(path)

        assert isinstance(loaded, StoryDesignArtifact)
        assert loaded.content.complexity == Complexity.MODERATE
        assert len(loaded.content.acceptance_criteria) == 2
        assert loaded.content.decisions[0].rationale == "Simple dispatch"
