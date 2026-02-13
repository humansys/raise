"""Tests for release CLI commands."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from rai_cli.cli.main import app
from rai_cli.context.graph import UnifiedGraph
from rai_cli.context.models import ConceptEdge, ConceptNode

runner = CliRunner()


def _build_graph_with_releases(project_path: Path) -> None:
    """Build a graph with release nodes for testing."""
    graph = UnifiedGraph()

    graph.add_concept(
        ConceptNode(
            id="rel-v2.0",
            type="release",
            content="V2.0 Open Core",
            source_file="governance/roadmap.md",
            created="2026-02-11",
            metadata={
                "release_id": "REL-V2.0",
                "name": "V2.0 Open Core",
                "target": "2026-02-15",
                "status": "In Progress",
            },
        )
    )
    graph.add_concept(
        ConceptNode(
            id="rel-v3.0",
            type="release",
            content="V3.0 Commercial Launch",
            source_file="governance/roadmap.md",
            created="2026-02-11",
            metadata={
                "release_id": "REL-V3.0",
                "name": "V3.0 Commercial Launch",
                "target": "2026-03-14",
                "status": "Planning",
            },
        )
    )

    # Add epics linked to releases
    graph.add_concept(
        ConceptNode(
            id="epic-e18",
            type="epic",
            content="V2 Open Core",
            source_file="governance/backlog.md",
            created="2026-02-11",
        )
    )
    graph.add_concept(
        ConceptNode(
            id="epic-e19",
            type="epic",
            content="V3 Product Design",
            source_file="governance/backlog.md",
            created="2026-02-11",
        )
    )
    graph.add_concept(
        ConceptNode(
            id="epic-e20",
            type="epic",
            content="V3 Hosted Rai",
            source_file="governance/backlog.md",
            created="2026-02-11",
        )
    )

    graph.add_relationship(
        ConceptEdge(source="epic-e18", target="rel-v2.0", type="part_of")
    )
    graph.add_relationship(
        ConceptEdge(source="epic-e19", target="rel-v3.0", type="part_of")
    )
    graph.add_relationship(
        ConceptEdge(source="epic-e20", target="rel-v3.0", type="part_of")
    )

    graph_path = project_path / ".raise" / "rai" / "memory" / "index.json"
    graph.save(graph_path)


class TestReleaseList:
    """Tests for rai release list command."""

    def test_lists_releases_from_graph(self, tmp_path: Path, monkeypatch: object) -> None:
        """rai release list shows releases from graph."""
        import pytest

        mp = pytest.MonkeyPatch()
        mp.chdir(tmp_path)

        _build_graph_with_releases(tmp_path)

        result = runner.invoke(app, ["release", "list", "--project", str(tmp_path)])
        assert result.exit_code == 0
        assert "REL-V2.0" in result.output
        assert "REL-V3.0" in result.output
        assert "V2.0 Open Core" in result.output
        assert "V3.0 Commercial Launch" in result.output
        mp.undo()

    def test_shows_error_when_no_graph(self, tmp_path: Path) -> None:
        """rai release list shows error when graph doesn't exist."""
        result = runner.invoke(app, ["release", "list", "--project", str(tmp_path)])
        assert result.exit_code != 0
        assert "build" in result.output.lower() or "build" in (result.stderr or "").lower()

    def test_shows_empty_message_when_no_releases(self, tmp_path: Path) -> None:
        """rai release list shows message when graph has no release nodes."""
        graph = UnifiedGraph()
        graph.add_concept(
            ConceptNode(
                id="epic-e18",
                type="epic",
                content="Some epic",
                source_file="governance/backlog.md",
                created="2026-02-11",
            )
        )
        graph_path = tmp_path / ".raise" / "rai" / "memory" / "index.json"
        graph.save(graph_path)

        result = runner.invoke(app, ["release", "list", "--project", str(tmp_path)])
        assert result.exit_code == 0
        assert "no release" in result.output.lower()
