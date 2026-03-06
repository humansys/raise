"""Round-trip test: write → read → compare."""

from __future__ import annotations

from datetime import datetime

from raise_cli.artifacts.models import ArtifactRefs, ArtifactType
from raise_cli.artifacts.reader import read_artifact
from raise_cli.artifacts.story_design import (
    AcceptanceCriterion,
    Complexity,
    Decision,
    StoryDesignArtifact,
    StoryDesignContent,
)
from raise_cli.artifacts.writer import write_artifact


def test_roundtrip_integrity(project_root, sample_created: datetime) -> None:
    original = StoryDesignArtifact(
        version=1,
        skill="rai-story-design",
        created=sample_created,
        story="S354.1",
        epic="E354",
        content=StoryDesignContent(
            summary="Round-trip test",
            complexity=Complexity.SIMPLE,
            acceptance_criteria=[
                AcceptanceCriterion(id="AC1", description="Validates"),
                AcceptanceCriterion(id="AC2", description="Persists"),
            ],
            decisions=[
                Decision(id="D1", choice="Registry", rationale="Simple dispatch"),
            ],
        ),
        refs=ArtifactRefs(
            backlog_item="RAISE-402",
            epic_scope="work/epics/e354/scope.md",
            related_artifacts=["other.yaml"],
        ),
        metadata={"origin": "test"},
    )

    path = write_artifact(original, project_root)
    loaded = read_artifact(path)

    assert isinstance(loaded, StoryDesignArtifact)
    assert loaded.artifact_type == ArtifactType.STORY_DESIGN
    assert loaded.version == original.version
    assert loaded.skill == original.skill
    assert loaded.created == original.created
    assert loaded.story == original.story
    assert loaded.epic == original.epic
    assert loaded.content == original.content
    assert loaded.refs == original.refs
    assert loaded.metadata == original.metadata
