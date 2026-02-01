"""Tests for graph traversal utilities."""

import pytest

from raise_cli.governance.graph.models import ConceptGraph, Relationship
from raise_cli.governance.graph.traversal import traverse_bfs
from raise_cli.governance.models import Concept, ConceptType


@pytest.fixture
def sample_graph() -> ConceptGraph:
    """Create a sample graph for testing traversal.

    Graph structure:
        req-rf-05 --implements--> outcome-context
              |
              +--governed_by--> principle-gov
              |
              +--depends_on--> req-rf-03

        req-rf-03 --governed_by--> principle-gov
    """
    # Create concepts
    req_rf_05 = Concept(
        id="req-rf-05",
        type=ConceptType.REQUIREMENT,
        file="prd.md",
        section="RF-05",
        lines=(1, 10),
        content="...",
    )

    req_rf_03 = Concept(
        id="req-rf-03",
        type=ConceptType.REQUIREMENT,
        file="prd.md",
        section="RF-03",
        lines=(1, 10),
        content="...",
    )

    outcome = Concept(
        id="outcome-context",
        type=ConceptType.OUTCOME,
        file="vision.md",
        section="Context",
        lines=(1, 5),
        content="...",
    )

    principle = Concept(
        id="principle-gov",
        type=ConceptType.PRINCIPLE,
        file="constitution.md",
        section="§2",
        lines=(1, 10),
        content="...",
    )

    # Create relationships
    relationships = [
        Relationship(source="req-rf-05", target="outcome-context", type="implements"),
        Relationship(source="req-rf-05", target="principle-gov", type="governed_by"),
        Relationship(source="req-rf-05", target="req-rf-03", type="depends_on"),
        Relationship(source="req-rf-03", target="principle-gov", type="governed_by"),
    ]

    # Build graph
    return ConceptGraph(
        nodes={
            req_rf_05.id: req_rf_05,
            req_rf_03.id: req_rf_03,
            outcome.id: outcome,
            principle.id: principle,
        },
        edges=relationships,
    )


class TestTraverseBFS:
    """Tests for BFS traversal."""

    def test_traverse_all_edges_depth_1(self, sample_graph: ConceptGraph) -> None:
        """Test BFS traversal with depth 1."""
        result = traverse_bfs(sample_graph, "req-rf-05", max_depth=1)

        # Should include start + direct neighbors
        assert len(result) == 4  # req-rf-05, outcome, principle, req-rf-03
        concept_ids = {c.id for c in result}
        assert "req-rf-05" in concept_ids
        assert "outcome-context" in concept_ids
        assert "principle-gov" in concept_ids
        assert "req-rf-03" in concept_ids

    def test_traverse_all_edges_depth_2(self, sample_graph: ConceptGraph) -> None:
        """Test BFS traversal with depth 2."""
        result = traverse_bfs(sample_graph, "req-rf-05", max_depth=2)

        # Should include all reachable nodes within depth 2
        # req-rf-05 -> {outcome, principle, req-rf-03}
        # req-rf-03 -> {principle} (but already visited)
        assert len(result) == 4
        concept_ids = {c.id for c in result}
        assert "req-rf-05" in concept_ids
        assert "outcome-context" in concept_ids
        assert "principle-gov" in concept_ids
        assert "req-rf-03" in concept_ids

    def test_traverse_filtered_by_edge_type(self, sample_graph: ConceptGraph) -> None:
        """Test BFS traversal filtered by edge type."""
        result = traverse_bfs(
            sample_graph,
            "req-rf-05",
            edge_types=["implements"],
            max_depth=2
        )

        # Should only traverse 'implements' edges
        assert len(result) == 2  # req-rf-05, outcome
        concept_ids = {c.id for c in result}
        assert "req-rf-05" in concept_ids
        assert "outcome-context" in concept_ids
        assert "principle-gov" not in concept_ids

    def test_traverse_multiple_edge_types(self, sample_graph: ConceptGraph) -> None:
        """Test BFS traversal with multiple edge type filters."""
        result = traverse_bfs(
            sample_graph,
            "req-rf-05",
            edge_types=["implements", "governed_by"],
            max_depth=2
        )

        # Should traverse 'implements' and 'governed_by' edges only
        assert len(result) == 3  # req-rf-05, outcome, principle
        concept_ids = {c.id for c in result}
        assert "req-rf-05" in concept_ids
        assert "outcome-context" in concept_ids
        assert "principle-gov" in concept_ids
        assert "req-rf-03" not in concept_ids  # depends_on excluded

    def test_traverse_nonexistent_start(self, sample_graph: ConceptGraph) -> None:
        """Test BFS traversal from non-existent start node."""
        result = traverse_bfs(sample_graph, "nonexistent-id", max_depth=2)

        # Should return empty list
        assert len(result) == 0

    def test_traverse_empty_graph(self) -> None:
        """Test BFS traversal on empty graph."""
        graph = ConceptGraph()
        result = traverse_bfs(graph, "any-id", max_depth=2)

        assert len(result) == 0

    def test_traverse_single_node_no_edges(self) -> None:
        """Test BFS traversal on graph with single node and no edges."""
        concept = Concept(
            id="single",
            type=ConceptType.REQUIREMENT,
            file="prd.md",
            section="Test",
            lines=(1, 5),
            content="...",
        )

        graph = ConceptGraph(nodes={"single": concept})
        result = traverse_bfs(graph, "single", max_depth=2)

        # Should return only the start node
        assert len(result) == 1
        assert result[0].id == "single"

    def test_traverse_respects_max_depth(self) -> None:
        """Test that BFS respects max_depth parameter."""
        # Create a chain: a -> b -> c -> d
        concepts = {
            f"node-{i}": Concept(
                id=f"node-{i}",
                type=ConceptType.REQUIREMENT,
                file="prd.md",
                section=f"Node {i}",
                lines=(1, 5),
                content="...",
            )
            for i in range(4)
        }

        edges = [
            Relationship(source=f"node-{i}", target=f"node-{i+1}", type="depends_on")
            for i in range(3)
        ]

        graph = ConceptGraph(nodes=concepts, edges=edges)

        # Depth 0: only start node
        result_depth_0 = traverse_bfs(graph, "node-0", max_depth=0)
        assert len(result_depth_0) == 1
        assert result_depth_0[0].id == "node-0"

        # Depth 1: start + node-1
        result_depth_1 = traverse_bfs(graph, "node-0", max_depth=1)
        assert len(result_depth_1) == 2

        # Depth 2: start + node-1 + node-2
        result_depth_2 = traverse_bfs(graph, "node-0", max_depth=2)
        assert len(result_depth_2) == 3

        # Depth 3: all nodes
        result_depth_3 = traverse_bfs(graph, "node-0", max_depth=3)
        assert len(result_depth_3) == 4

    def test_traverse_handles_cycles(self) -> None:
        """Test that BFS handles cycles correctly (doesn't infinite loop)."""
        # Create cycle: a -> b -> c -> a
        concepts = {
            "a": Concept(
                id="a",
                type=ConceptType.REQUIREMENT,
                file="prd.md",
                section="A",
                lines=(1, 5),
                content="...",
            ),
            "b": Concept(
                id="b",
                type=ConceptType.REQUIREMENT,
                file="prd.md",
                section="B",
                lines=(1, 5),
                content="...",
            ),
            "c": Concept(
                id="c",
                type=ConceptType.REQUIREMENT,
                file="prd.md",
                section="C",
                lines=(1, 5),
                content="...",
            ),
        }

        edges = [
            Relationship(source="a", target="b", type="depends_on"),
            Relationship(source="b", target="c", type="depends_on"),
            Relationship(source="c", target="a", type="depends_on"),
        ]

        graph = ConceptGraph(nodes=concepts, edges=edges)

        result = traverse_bfs(graph, "a", max_depth=5)

        # Should visit each node exactly once despite cycle
        assert len(result) == 3
        concept_ids = {c.id for c in result}
        assert concept_ids == {"a", "b", "c"}

    def test_traverse_disconnected_graph(self) -> None:
        """Test BFS on disconnected graph."""
        # Create two disconnected components
        concepts = {
            "a": Concept(
                id="a",
                type=ConceptType.REQUIREMENT,
                file="prd.md",
                section="A",
                lines=(1, 5),
                content="...",
            ),
            "b": Concept(
                id="b",
                type=ConceptType.REQUIREMENT,
                file="prd.md",
                section="B",
                lines=(1, 5),
                content="...",
            ),
            "c": Concept(
                id="c",
                type=ConceptType.REQUIREMENT,
                file="prd.md",
                section="C",
                lines=(1, 5),
                content="...",
            ),
        }

        # Only connect a -> b, leave c disconnected
        edges = [Relationship(source="a", target="b", type="depends_on")]

        graph = ConceptGraph(nodes=concepts, edges=edges)

        result = traverse_bfs(graph, "a", max_depth=3)

        # Should only reach a and b, not c
        assert len(result) == 2
        concept_ids = {c.id for c in result}
        assert concept_ids == {"a", "b"}

    def test_traverse_default_max_depth(self, sample_graph: ConceptGraph) -> None:
        """Test that default max_depth is 3."""
        # Call without specifying max_depth
        result = traverse_bfs(sample_graph, "req-rf-05")

        # Should use default max_depth=3
        assert len(result) > 0
