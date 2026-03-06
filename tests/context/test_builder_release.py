"""Tests for release node and edge integration in GraphBuilder."""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import pytest

from raise_cli.context.builder import GraphBuilder


@pytest.fixture
def project_with_releases(tmp_path: Path) -> Path:
    """Create a minimal project with roadmap and backlog for release testing."""
    project_root = tmp_path / "project"
    governance = project_root / "governance"
    governance.mkdir(parents=True)

    # Roadmap with two releases
    (governance / "roadmap.md").write_text(
        dedent(
            """\
            # Roadmap: test

            ## Releases

            | ID | Release | Target | Status | Epics |
            |----|---------|--------|--------|-------|
            | REL-V2.0 | V2.0 Core | 2026-02-15 | In Progress | E1, E2 |
            | REL-V3.0 | V3.0 Launch | 2026-03-14 | Planning | E3, E4 |
            """
        )
    )

    # Backlog with epics (so epic nodes exist for edge resolution)
    (governance / "backlog.md").write_text(
        dedent(
            """\
            # Backlog: test

            | ID | Epic | Status | Scope Doc | Priority |
            |----|------|--------|-----------|----------|
            | E1 | Foundation | ✅ Complete | — | — |
            | E2 | Governance | In Progress | — | P0 |
            | E3 | Commercial | Planning | — | P1 |
            """
        )
    )

    return project_root


class TestReleaseNodesInGraph:
    """Tests for release nodes appearing in built graph."""

    def test_graph_contains_release_nodes(self, project_with_releases: Path) -> None:
        """Should produce release nodes in the graph."""
        builder = GraphBuilder(project_with_releases)
        graph = builder.build()

        release_nodes = graph.get_concepts_by_type("release")
        assert len(release_nodes) == 2

    def test_release_node_ids(self, project_with_releases: Path) -> None:
        """Should produce correct release IDs."""
        builder = GraphBuilder(project_with_releases)
        graph = builder.build()

        release_nodes = graph.get_concepts_by_type("release")
        ids = {n.id for n in release_nodes}
        assert "rel-v2.0" in ids
        assert "rel-v3.0" in ids

    def test_release_node_metadata(self, project_with_releases: Path) -> None:
        """Should carry metadata through to graph nodes."""
        builder = GraphBuilder(project_with_releases)
        graph = builder.build()

        release_nodes = graph.get_concepts_by_type("release")
        v3 = next(n for n in release_nodes if n.id == "rel-v3.0")
        assert v3.metadata["epics"] == ["E3", "E4"]
        assert v3.metadata["target"] == "2026-03-14"


class TestReleasePartOfEdges:
    """Tests for epic → release part_of edges."""

    def test_epic_to_release_edges_created(self, project_with_releases: Path) -> None:
        """Should create part_of edges from epics to releases."""
        builder = GraphBuilder(project_with_releases)
        graph = builder.build()

        # E1 should be neighbor of rel-v2.0 via part_of
        neighbors = graph.get_neighbors("rel-v2.0", edge_types=["part_of"])
        neighbor_ids = {n.id for n in neighbors}
        assert "epic-e1" in neighbor_ids

    def test_missing_epic_node_skipped(self, project_with_releases: Path) -> None:
        """Should skip edges for epics not in graph (E4 not in backlog)."""
        builder = GraphBuilder(project_with_releases)
        graph = builder.build()

        # E4 doesn't exist in backlog → no node → no edge
        # Graph should still build without error
        release_nodes = graph.get_concepts_by_type("release")
        assert len(release_nodes) == 2  # Both releases still present

    def test_multiple_epics_per_release(self, project_with_releases: Path) -> None:
        """Should create edges for all epics in a release."""
        builder = GraphBuilder(project_with_releases)
        graph = builder.build()

        # Both E1 and E2 should be neighbors of rel-v2.0
        neighbors = graph.get_neighbors("rel-v2.0", edge_types=["part_of"])
        neighbor_ids = {n.id for n in neighbors}
        assert "epic-e1" in neighbor_ids
        assert "epic-e2" in neighbor_ids
