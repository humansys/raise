"""Tests for artifact YAML reader."""

from __future__ import annotations

from datetime import datetime

import pytest
from pydantic import ValidationError

from raise_cli.artifacts.models import ArtifactRefs, ArtifactType
from raise_cli.artifacts.reader import read_all_artifacts, read_artifact
from raise_cli.artifacts.story_design import (
    AcceptanceCriterion,
    Complexity,
    StoryDesignArtifact,
    StoryDesignContent,
)
from raise_cli.artifacts.writer import write_artifact


def _make_artifact(created: datetime) -> StoryDesignArtifact:
    return StoryDesignArtifact(
        skill="rai-story-design",
        created=created,
        story="S354.1",
        epic="E354",
        content=StoryDesignContent(
            summary="test",
            complexity=Complexity.SIMPLE,
            acceptance_criteria=[
                AcceptanceCriterion(id="AC1", description="Works"),
            ],
        ),
        refs=ArtifactRefs(backlog_item="RAISE-402"),
    )


class TestReadArtifact:
    def test_loads_valid_yaml(self, project_root, sample_created) -> None:
        artifact = _make_artifact(sample_created)
        path = write_artifact(artifact, project_root)
        loaded = read_artifact(path)
        assert loaded.artifact_type == ArtifactType.STORY_DESIGN
        assert loaded.skill == "rai-story-design"
        assert loaded.story == "S354.1"

    def test_invalid_yaml_raises(self, tmp_path) -> None:
        bad_file = tmp_path / "bad.yaml"
        bad_file.write_text("artifact_type: not-a-type\nskill: x\ncontent: {}")
        with pytest.raises(ValidationError):
            read_artifact(bad_file)


class TestReadAllArtifacts:
    def test_reads_all_from_directory(self, project_root, sample_created) -> None:
        a1 = _make_artifact(sample_created)
        a2 = StoryDesignArtifact(
            skill="rai-story-design",
            created=sample_created,
            story="S354.2",
            content=StoryDesignContent(
                summary="second",
                complexity=Complexity.SIMPLE,
                acceptance_criteria=[
                    AcceptanceCriterion(id="AC1", description="Also works"),
                ],
            ),
        )
        write_artifact(a1, project_root)
        write_artifact(a2, project_root)

        artifacts = read_all_artifacts(project_root / ".raise" / "artifacts")
        assert len(artifacts) == 2

    def test_empty_directory(self, artifacts_dir) -> None:
        assert read_all_artifacts(artifacts_dir) == []

    def test_nonexistent_directory(self, tmp_path) -> None:
        assert read_all_artifacts(tmp_path / "nope") == []
