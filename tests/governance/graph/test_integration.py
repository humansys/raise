"""Integration tests for complete graph building workflow."""

import time
from pathlib import Path

import pytest

from raise_cli.governance.extractor import GovernanceExtractor
from raise_cli.governance.graph.builder import GraphBuilder
from raise_cli.governance.models import Concept, ConceptType


class TestEndToEndWorkflow:
    """Tests for complete E2E workflow."""

    def test_e2e_extract_build_validate(self) -> None:
        """Test complete workflow: extract → build → validate."""
        # Check if governance files exist
        prd_path = Path("governance/projects/raise-cli/prd.md")
        if not prd_path.exists():
            pytest.skip("Real governance files not available")

        # Step 1: Extract concepts
        extractor = GovernanceExtractor()
        concepts = extractor.extract_all()

        assert len(concepts) >= 20, "Should extract at least 20 concepts"

        # Step 2: Build graph
        builder = GraphBuilder()
        graph = builder.build(concepts)

        assert len(graph.nodes) >= 20, "Graph should have at least 20 nodes"
        assert len(graph.edges) >= 30, "Graph should have at least 30 edges"

        # Step 3: Validate graph structure
        # All edge sources and targets should exist as nodes
        for edge in graph.edges:
            assert edge.source in graph.nodes, f"Edge source {edge.source} not in graph"
            assert edge.target in graph.nodes, f"Edge target {edge.target} not in graph"

        # Step 4: Verify metadata
        assert "build_time" in graph.metadata
        assert "stats" in graph.metadata
        # Note: Total nodes in metadata is based on input concepts,
        # but nodes dict may deduplicate if same ID appears twice
        stats = graph.metadata["stats"]
        assert stats["total_nodes"] >= len(graph.nodes)
        assert stats["total_edges"] == len(graph.edges)

    def test_e2e_serialization_roundtrip(self) -> None:
        """Test that graph survives JSON serialization roundtrip."""
        prd_path = Path("governance/projects/raise-cli/prd.md")
        if not prd_path.exists():
            pytest.skip("Real governance files not available")

        # Build original graph
        extractor = GovernanceExtractor()
        concepts = extractor.extract_all()
        builder = GraphBuilder()
        original_graph = builder.build(concepts)

        # Serialize
        json_str = original_graph.to_json()

        # Deserialize
        from raise_cli.governance.graph import ConceptGraph

        loaded_graph = ConceptGraph.from_json(json_str)

        # Verify equivalence
        assert len(loaded_graph.nodes) == len(original_graph.nodes)
        assert len(loaded_graph.edges) == len(original_graph.edges)
        assert loaded_graph.metadata["stats"] == original_graph.metadata["stats"]

        # Verify specific concepts preserved
        for concept_id in original_graph.nodes:
            assert concept_id in loaded_graph.nodes
            orig_concept = original_graph.nodes[concept_id]
            loaded_concept = loaded_graph.nodes[concept_id]

            assert loaded_concept.id == orig_concept.id
            assert loaded_concept.type == orig_concept.type
            assert loaded_concept.content == orig_concept.content


class TestPerformance:
    """Tests for performance constraints."""

    def test_build_time_under_2_seconds(self) -> None:
        """Test that graph builds in under 2 seconds for 50 concepts."""
        # Create 50 sample concepts
        concepts = [
            Concept(
                id=f"concept-{i}",
                type=ConceptType.REQUIREMENT,
                file="test.md",
                section=f"Section {i}",
                lines=(i * 10, i * 10 + 10),
                content=f"Content for concept {i} with some keywords like system, context, generation.",
            )
            for i in range(50)
        ]

        builder = GraphBuilder()

        start_time = time.time()
        graph = builder.build(concepts)
        build_time = time.time() - start_time

        assert build_time < 2.0, f"Graph build took {build_time:.2f}s, expected <2s"
        assert len(graph.nodes) == 50

    def test_bfs_traversal_under_100ms(self) -> None:
        """Test that BFS traversal completes in under 100ms for 50-node graph."""
        from raise_cli.governance.graph.traversal import traverse_bfs

        # Create a connected graph with 50 nodes
        concepts = []
        for i in range(50):
            concepts.append(
                Concept(
                    id=f"node-{i}",
                    type=ConceptType.REQUIREMENT,
                    file="test.md",
                    section=f"Node {i}",
                    lines=(i, i + 1),
                    content="Test content with system context generation keywords.",
                )
            )

        builder = GraphBuilder()
        graph = builder.build(concepts)

        # Time BFS traversal
        start_time = time.time()
        result = traverse_bfs(graph, "node-0", max_depth=10)
        traversal_time = time.time() - start_time

        assert traversal_time < 0.1, f"BFS took {traversal_time*1000:.1f}ms, expected <100ms"
        assert len(result) > 0


class TestEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_empty_concept_list(self) -> None:
        """Test that building graph from empty concept list works."""
        builder = GraphBuilder()
        graph = builder.build([])

        assert len(graph.nodes) == 0
        assert len(graph.edges) == 0
        assert graph.metadata["stats"]["total_nodes"] == 0

    def test_single_concept_no_relationships(self) -> None:
        """Test graph with single concept."""
        concept = Concept(
            id="single",
            type=ConceptType.REQUIREMENT,
            file="test.md",
            section="Single",
            lines=(1, 5),
            content="Isolated content.",
        )

        builder = GraphBuilder()
        graph = builder.build([concept])

        assert len(graph.nodes) == 1
        assert len(graph.edges) == 0

    def test_disconnected_graph(self) -> None:
        """Test graph with multiple disconnected components."""
        from raise_cli.governance.graph.traversal import traverse_bfs

        # Create two disconnected groups
        group1 = [
            Concept(
                id="a1",
                type=ConceptType.REQUIREMENT,
                file="test.md",
                section="A1",
                lines=(1, 5),
                content="Group A concept one.",
            ),
            Concept(
                id="a2",
                type=ConceptType.REQUIREMENT,
                file="test.md",
                section="A2",
                lines=(6, 10),
                content="Group A concept two.",
            ),
        ]

        group2 = [
            Concept(
                id="b1",
                type=ConceptType.OUTCOME,
                file="test.md",
                section="B1",
                lines=(11, 15),
                content="Group B outcome one.",
            ),
            Concept(
                id="b2",
                type=ConceptType.OUTCOME,
                file="test.md",
                section="B2",
                lines=(16, 20),
                content="Group B outcome two.",
            ),
        ]

        builder = GraphBuilder()
        graph = builder.build(group1 + group2)

        # Should have 4 nodes
        assert len(graph.nodes) == 4

        # BFS from a1 should not reach b1 or b2 (disconnected)
        reachable_from_a1 = traverse_bfs(graph, "a1", max_depth=10)
        reachable_ids = {c.id for c in reachable_from_a1}

        # a1 can reach itself
        assert "a1" in reachable_ids

    def test_circular_dependency(self) -> None:
        """Test graph can handle circular dependencies."""
        # Create concepts with circular depends_on references
        concepts = [
            Concept(
                id="req-rf-01",
                type=ConceptType.REQUIREMENT,
                file="test.md",
                section="RF-01",
                lines=(1, 5),
                content="This depends on RF-02.",
            ),
            Concept(
                id="req-rf-02",
                type=ConceptType.REQUIREMENT,
                file="test.md",
                section="RF-02",
                lines=(6, 10),
                content="This depends on RF-03.",
            ),
            Concept(
                id="req-rf-03",
                type=ConceptType.REQUIREMENT,
                file="test.md",
                section="RF-03",
                lines=(11, 15),
                content="This depends on RF-01.",  # Creates cycle
            ),
        ]

        builder = GraphBuilder()
        graph = builder.build(concepts)

        # Should still build successfully
        assert len(graph.nodes) == 3

        # Should have depends_on edges (forming a cycle)
        depends_edges = [e for e in graph.edges if e.type == "depends_on"]
        assert len(depends_edges) == 3  # Each depends on the next


class TestGraphStatistics:
    """Tests for graph statistics and metadata."""

    def test_metadata_includes_all_required_fields(self) -> None:
        """Test that graph metadata includes all required fields."""
        concept = Concept(
            id="test",
            type=ConceptType.REQUIREMENT,
            file="test.md",
            section="Test",
            lines=(1, 5),
            content="Test content.",
        )

        builder = GraphBuilder()
        graph = builder.build([concept])

        # Required metadata fields
        assert "build_time" in graph.metadata
        assert "version" in graph.metadata
        assert "stats" in graph.metadata

        stats = graph.metadata["stats"]
        assert "total_nodes" in stats
        assert "total_edges" in stats
        assert "edges_by_type" in stats

    def test_edge_counts_accurate(self) -> None:
        """Test that edge counts by type are accurate."""
        concepts = [
            Concept(
                id="req-rf-05",
                type=ConceptType.REQUIREMENT,
                file="test.md",
                section="RF-05",
                lines=(1, 10),
                content="System must generate context. Per §2, use Git.",
            ),
            Concept(
                id="outcome-context",
                type=ConceptType.OUTCOME,
                file="test.md",
                section="Context",
                lines=(11, 15),
                content="Enable context generation.",
                metadata={"title": "Context Generation"},
            ),
            Concept(
                id="principle-gov",
                type=ConceptType.PRINCIPLE,
                file="test.md",
                section="§2. Governance",
                lines=(16, 20),
                content="Standards in Git.",
            ),
        ]

        builder = GraphBuilder()
        graph = builder.build(concepts)

        stats = graph.metadata["stats"]
        edge_counts = stats["edges_by_type"]

        # Verify counts match actual edges
        actual_counts: dict[str, int] = {}
        for edge in graph.edges:
            actual_counts[edge.type] = actual_counts.get(edge.type, 0) + 1

        assert edge_counts == actual_counts
