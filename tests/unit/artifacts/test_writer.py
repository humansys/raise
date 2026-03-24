"""Tests for artifact YAML writer."""

from __future__ import annotations

from datetime import datetime

import yaml

from raise_cli.artifacts.models import ArtifactRefs, ArtifactType, SkillArtifact
from raise_cli.artifacts.writer import write_artifact


def _make_artifact(created: datetime) -> SkillArtifact:
    return SkillArtifact(
        artifact_type=ArtifactType.STORY_DESIGN,
        skill="rai-story-design",
        created=created,
        story="S354.1",
        epic="E354",
        content={"summary": "Base artifact model"},
        refs=ArtifactRefs(backlog_item="RAISE-402"),
    )


class TestWriteArtifact:
    def test_creates_file_at_correct_path(self, project_root, sample_created) -> None:
        artifact = _make_artifact(sample_created)
        path = write_artifact(artifact, project_root)
        assert path.exists()
        assert path.name == "s354.1-design.yaml"

    def test_creates_artifacts_dir_if_missing(
        self, project_root, sample_created
    ) -> None:
        artifact = _make_artifact(sample_created)
        write_artifact(artifact, project_root)
        assert (project_root / ".raise" / "artifacts").is_dir()

    def test_yaml_content_matches_model(self, project_root, sample_created) -> None:
        artifact = _make_artifact(sample_created)
        path = write_artifact(artifact, project_root)
        data = yaml.safe_load(path.read_text())
        assert data["artifact_type"] == "story-design"
        assert data["skill"] == "rai-story-design"
        assert data["story"] == "S354.1"
        assert data["content"]["summary"] == "Base artifact model"
        assert data["refs"]["backlog_item"] == "RAISE-402"

    def test_filename_from_story_and_type(self, project_root, sample_created) -> None:
        artifact = SkillArtifact(
            artifact_type=ArtifactType.STORY_DESIGN,
            skill="rai-story-design",
            created=sample_created,
            story="S999.3",
            content={},
        )
        path = write_artifact(artifact, project_root)
        assert path.name == "s999.3-design.yaml"

    def test_filename_from_epic_when_no_story(
        self, project_root, sample_created
    ) -> None:
        artifact = SkillArtifact(
            artifact_type=ArtifactType.STORY_DESIGN,
            skill="rai-story-design",
            created=sample_created,
            epic="E354",
            content={},
        )
        path = write_artifact(artifact, project_root)
        assert path.name == "e354-design.yaml"
