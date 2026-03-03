"""Round-trip test: write → read → compare."""

from __future__ import annotations

from datetime import datetime

from rai_cli.artifacts.models import ArtifactRefs, ArtifactType, SkillArtifact
from rai_cli.artifacts.reader import read_artifact
from rai_cli.artifacts.writer import write_artifact


def test_roundtrip_integrity(project_root, sample_created: datetime) -> None:
    original = SkillArtifact(
        artifact_type=ArtifactType.STORY_DESIGN,
        version=1,
        skill="rai-story-design",
        created=sample_created,
        story="S354.1",
        epic="E354",
        content={"summary": "test", "complexity": "small"},
        refs=ArtifactRefs(
            backlog_item="RAISE-402",
            epic_scope="work/epics/e354/scope.md",
            related_artifacts=["other.yaml"],
        ),
        metadata={"origin": "test"},
    )

    path = write_artifact(original, project_root)
    loaded = read_artifact(path)

    assert loaded.artifact_type == original.artifact_type
    assert loaded.version == original.version
    assert loaded.skill == original.skill
    assert loaded.created == original.created
    assert loaded.story == original.story
    assert loaded.epic == original.epic
    assert loaded.content == original.content
    assert loaded.refs == original.refs
    assert loaded.metadata == original.metadata
