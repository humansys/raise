"""Tests for GraphBuilder.load_artifacts() — artifact graph ingestion."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from raise_cli.artifacts.models import ArtifactRefs
from raise_cli.artifacts.story_design import (
    AcceptanceCriterion,
    Complexity,
    StoryDesignArtifact,
    StoryDesignContent,
)
from raise_cli.artifacts.writer import write_artifact
from raise_cli.context.builder import GraphBuilder


def _write_sample_artifact(project_root: Path) -> None:
    """Write a sample story-design artifact to .raise/artifacts/."""
    artifact = StoryDesignArtifact(
        skill="rai-story-design",
        created=datetime(2026, 3, 3, 10, 0, 0, tzinfo=UTC),
        story="S354.1",
        epic="E354",
        content=StoryDesignContent(
            summary="Base artifact model",
            complexity=Complexity.SIMPLE,
            acceptance_criteria=[
                AcceptanceCriterion(id="AC1", description="Model validates"),
            ],
        ),
        refs=ArtifactRefs(backlog_item="RAISE-402"),
    )
    write_artifact(artifact, project_root)


class TestLoadArtifacts:
    def test_returns_graph_nodes(self, tmp_path: Path) -> None:
        _write_sample_artifact(tmp_path)
        builder = GraphBuilder(project_root=tmp_path)
        nodes = builder.load_artifacts()
        assert len(nodes) == 1

    def test_node_fields(self, tmp_path: Path) -> None:
        _write_sample_artifact(tmp_path)
        builder = GraphBuilder(project_root=tmp_path)
        node = builder.load_artifacts()[0]
        assert node.id == "artifact-s354.1-story-design"
        assert node.type == "artifact"
        assert "Base artifact model" in node.content
        assert node.metadata["artifact_type"] == "story-design"
        assert node.metadata["skill"] == "rai-story-design"
        assert node.metadata["story"] == "S354.1"
        assert node.metadata["epic"] == "E354"

    def test_empty_directory(self, tmp_path: Path) -> None:
        (tmp_path / ".raise" / "artifacts").mkdir(parents=True)
        builder = GraphBuilder(project_root=tmp_path)
        assert builder.load_artifacts() == []

    def test_missing_directory(self, tmp_path: Path) -> None:
        builder = GraphBuilder(project_root=tmp_path)
        assert builder.load_artifacts() == []

    def test_source_file_set(self, tmp_path: Path) -> None:
        _write_sample_artifact(tmp_path)
        builder = GraphBuilder(project_root=tmp_path)
        node = builder.load_artifacts()[0]
        assert node.source_file == ".raise/artifacts/s354.1-design.yaml"
