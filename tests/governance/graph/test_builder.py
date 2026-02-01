"""Tests for graph builder."""

import pytest

from raise_cli.governance.graph.builder import GraphBuilder
from raise_cli.governance.models import Concept, ConceptType


@pytest.fixture
def sample_concepts() -> list[Concept]:
    """Create sample concepts for testing."""
    return [
        Concept(
            id="req-rf-05",
            type=ConceptType.REQUIREMENT,
            file="prd.md",
            section="RF-05: Context Generation",
            lines=(1, 10),
            content="The system MUST generate context. Per §2, use Git.",
            metadata={"requirement_id": "RF-05", "title": "Context Generation"},
        ),
        Concept(
            id="outcome-context",
            type=ConceptType.OUTCOME,
            file="vision.md",
            section="Context Generation",
            lines=(1, 5),
            content="Enable context generation for agents.",
            metadata={"title": "Context Generation"},
        ),
        Concept(
            id="principle-governance",
            type=ConceptType.PRINCIPLE,
            file="constitution.md",
            section="§2. Governance as Code",
            lines=(1, 10),
            content="Standards versioned in Git.",
            metadata={"principle_number": 2},
        ),
    ]


class TestGraphBuilder:
    """Tests for GraphBuilder class."""

    def test_build_graph_from_concepts(self, sample_concepts: list[Concept]) -> None:
        """Test building graph from concepts."""
        builder = GraphBuilder()
        graph = builder.build(sample_concepts)

        # Verify nodes created
        assert len(graph.nodes) == 3
        assert "req-rf-05" in graph.nodes
        assert "outcome-context" in graph.nodes
        assert "principle-governance" in graph.nodes

        # Verify edges created (should have implements and governed_by)
        assert len(graph.edges) > 0
        edge_types = {e.type for e in graph.edges}
        assert "implements" in edge_types
        assert "governed_by" in edge_types

    def test_build_empty_graph(self) -> None:
        """Test building graph from empty concept list."""
        builder = GraphBuilder()
        graph = builder.build([])

        assert len(graph.nodes) == 0
        assert len(graph.edges) == 0
        assert graph.metadata["stats"]["total_nodes"] == 0
        assert graph.metadata["stats"]["total_edges"] == 0

    def test_build_single_concept(self) -> None:
        """Test building graph from single concept."""
        concept = Concept(
            id="single",
            type=ConceptType.REQUIREMENT,
            file="prd.md",
            section="Test",
            lines=(1, 5),
            content="Test content.",
        )

        builder = GraphBuilder()
        graph = builder.build([concept])

        assert len(graph.nodes) == 1
        assert "single" in graph.nodes
        assert len(graph.edges) == 0  # No relationships with single concept

    def test_metadata_includes_build_time(self, sample_concepts: list[Concept]) -> None:
        """Test that metadata includes build time."""
        builder = GraphBuilder()
        graph = builder.build(sample_concepts)

        assert "build_time" in graph.metadata
        assert "version" in graph.metadata
        assert graph.metadata["version"] == "1.0"

    def test_metadata_includes_statistics(
        self, sample_concepts: list[Concept]
    ) -> None:
        """Test that metadata includes graph statistics."""
        builder = GraphBuilder()
        graph = builder.build(sample_concepts)

        assert "stats" in graph.metadata
        stats = graph.metadata["stats"]

        assert "total_nodes" in stats
        assert "total_edges" in stats
        assert "edges_by_type" in stats

        assert stats["total_nodes"] == 3
        assert stats["total_edges"] == len(graph.edges)

        # Verify edge counts by type
        edge_counts = stats["edges_by_type"]
        assert isinstance(edge_counts, dict)
        assert sum(edge_counts.values()) == stats["total_edges"]

    def test_edge_counts_by_type(self, sample_concepts: list[Concept]) -> None:
        """Test that edge counts are correctly calculated by type."""
        builder = GraphBuilder()
        graph = builder.build(sample_concepts)

        stats = graph.metadata["stats"]
        edge_counts = stats["edges_by_type"]

        # Manually count edges by type
        actual_counts: dict[str, int] = {}
        for edge in graph.edges:
            actual_counts[edge.type] = actual_counts.get(edge.type, 0) + 1

        assert edge_counts == actual_counts

    def test_build_preserves_concept_data(
        self, sample_concepts: list[Concept]
    ) -> None:
        """Test that building preserves all concept data."""
        builder = GraphBuilder()
        graph = builder.build(sample_concepts)

        # Verify each concept is preserved exactly
        for concept in sample_concepts:
            assert concept.id in graph.nodes
            node = graph.nodes[concept.id]

            assert node.id == concept.id
            assert node.type == concept.type
            assert node.file == concept.file
            assert node.section == concept.section
            assert node.lines == concept.lines
            assert node.content == concept.content
            assert node.metadata == concept.metadata

    def test_build_from_real_governance(self) -> None:
        """Integration test: build from real governance files."""
        from pathlib import Path

        from raise_cli.governance.extractor import GovernanceExtractor

        # Check if governance files exist
        prd_path = Path("governance/projects/raise-cli/prd.md")
        if not prd_path.exists():
            pytest.skip("Real governance files not available")

        extractor = GovernanceExtractor()
        concepts = extractor.extract_all()

        # Should have extracted concepts
        assert len(concepts) >= 20

        # Build graph
        builder = GraphBuilder()
        graph = builder.build(concepts)

        # Verify graph has reasonable structure
        assert len(graph.nodes) >= 20
        assert len(graph.edges) >= 30

        # Verify metadata populated
        assert "build_time" in graph.metadata
        assert "stats" in graph.metadata

        # Verify edge types are present
        edge_types = {e.type for e in graph.edges}
        assert len(edge_types) > 0
        # Note: Edge types depend on content patterns in governance files
        # At minimum, should have some relationships (e.g., related_to from keyword matching)
        assert len(graph.edges) > 0

    def test_build_is_deterministic(self, sample_concepts: list[Concept]) -> None:
        """Test that building the same concepts produces consistent results."""
        builder = GraphBuilder()

        graph1 = builder.build(sample_concepts)
        graph2 = builder.build(sample_concepts)

        # Nodes should be identical
        assert graph1.nodes.keys() == graph2.nodes.keys()

        # Edges should be identical (same count and types)
        assert len(graph1.edges) == len(graph2.edges)

        edge_types_1 = sorted([e.type for e in graph1.edges])
        edge_types_2 = sorted([e.type for e in graph2.edges])
        assert edge_types_1 == edge_types_2
