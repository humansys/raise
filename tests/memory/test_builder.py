"""Tests for memory graph builder."""

from datetime import date

import pytest

from raise_cli.memory.builder import (
    MemoryGraph,
    MemoryGraphBuilder,
    traverse_bfs,
)
from raise_cli.memory.models import (
    MemoryConcept,
    MemoryConceptType,
    MemoryRelationship,
    MemoryRelationshipType,
)


class TestMemoryGraph:
    """Tests for MemoryGraph class."""

    def test_create_empty_graph(self) -> None:
        """Create an empty graph."""
        graph = MemoryGraph()
        assert graph.nodes == {}
        assert graph.edges == []
        assert graph.metadata == {}

    def test_create_graph_with_nodes(self) -> None:
        """Create a graph with nodes."""
        concept = MemoryConcept(
            id="PAT-001",
            type=MemoryConceptType.PATTERN,
            content="Test pattern",
            created=date(2026, 1, 31),
        )
        graph = MemoryGraph(nodes={"PAT-001": concept})
        assert len(graph.nodes) == 1
        assert graph.get_node("PAT-001") == concept

    def test_get_node_not_found(self) -> None:
        """Get non-existent node returns None."""
        graph = MemoryGraph()
        assert graph.get_node("NONEXISTENT") is None

    def test_get_outgoing_edges(self) -> None:
        """Get outgoing edges from a concept."""
        edge = MemoryRelationship(
            source="PAT-001",
            target="SES-001",
            type=MemoryRelationshipType.LEARNED_FROM,
        )
        graph = MemoryGraph(edges=[edge])

        outgoing = graph.get_outgoing_edges("PAT-001")
        assert len(outgoing) == 1
        assert outgoing[0].target == "SES-001"

        # No outgoing from target
        assert graph.get_outgoing_edges("SES-001") == []

    def test_get_outgoing_edges_filtered(self) -> None:
        """Get outgoing edges with type filter."""
        edges = [
            MemoryRelationship(
                source="PAT-001",
                target="SES-001",
                type=MemoryRelationshipType.LEARNED_FROM,
            ),
            MemoryRelationship(
                source="PAT-001",
                target="PAT-002",
                type=MemoryRelationshipType.RELATED_TO,
            ),
        ]
        graph = MemoryGraph(edges=edges)

        learned = graph.get_outgoing_edges(
            "PAT-001", edge_type=MemoryRelationshipType.LEARNED_FROM
        )
        assert len(learned) == 1
        assert learned[0].type == MemoryRelationshipType.LEARNED_FROM

    def test_get_incoming_edges(self) -> None:
        """Get incoming edges to a concept."""
        edge = MemoryRelationship(
            source="PAT-001",
            target="SES-001",
            type=MemoryRelationshipType.LEARNED_FROM,
        )
        graph = MemoryGraph(edges=[edge])

        incoming = graph.get_incoming_edges("SES-001")
        assert len(incoming) == 1
        assert incoming[0].source == "PAT-001"

    def test_to_json_and_from_json(self) -> None:
        """Serialize and deserialize graph."""
        concept = MemoryConcept(
            id="PAT-001",
            type=MemoryConceptType.PATTERN,
            content="Test",
            created=date(2026, 1, 31),
        )
        edge = MemoryRelationship(
            source="PAT-001",
            target="SES-001",
            type=MemoryRelationshipType.LEARNED_FROM,
        )
        graph = MemoryGraph(
            nodes={"PAT-001": concept},
            edges=[edge],
            metadata={"test": "value"},
        )

        json_str = graph.to_json()
        loaded = MemoryGraph.from_json(json_str)

        assert len(loaded.nodes) == 1
        assert len(loaded.edges) == 1
        assert loaded.metadata["test"] == "value"


class TestTraverseBfs:
    """Tests for BFS traversal."""

    def test_traverse_empty_graph(self) -> None:
        """Traverse empty graph returns empty list."""
        graph = MemoryGraph()
        result = traverse_bfs(graph, "PAT-001")
        assert result == []

    def test_traverse_single_node(self) -> None:
        """Traverse graph with single node."""
        concept = MemoryConcept(
            id="PAT-001",
            type=MemoryConceptType.PATTERN,
            content="Test",
            created=date(2026, 1, 31),
        )
        graph = MemoryGraph(nodes={"PAT-001": concept})

        result = traverse_bfs(graph, "PAT-001")
        assert len(result) == 1
        assert result[0].id == "PAT-001"

    def test_traverse_with_edges(self) -> None:
        """Traverse graph following edges."""
        concepts = [
            MemoryConcept(
                id="PAT-001",
                type=MemoryConceptType.PATTERN,
                content="Pattern 1",
                created=date(2026, 1, 31),
            ),
            MemoryConcept(
                id="SES-001",
                type=MemoryConceptType.SESSION,
                content="Session 1",
                created=date(2026, 1, 31),
            ),
        ]
        edge = MemoryRelationship(
            source="PAT-001",
            target="SES-001",
            type=MemoryRelationshipType.LEARNED_FROM,
        )
        graph = MemoryGraph(
            nodes={c.id: c for c in concepts},
            edges=[edge],
        )

        result = traverse_bfs(graph, "PAT-001")
        assert len(result) == 2
        ids = [c.id for c in result]
        assert "PAT-001" in ids
        assert "SES-001" in ids

    def test_traverse_respects_max_depth(self) -> None:
        """Traverse respects max_depth limit."""
        concepts = [
            MemoryConcept(
                id=f"PAT-{i:03d}",
                type=MemoryConceptType.PATTERN,
                content=f"Pattern {i}",
                created=date(2026, 1, 31),
            )
            for i in range(1, 5)
        ]
        # Chain: PAT-001 → PAT-002 → PAT-003 → PAT-004
        edges = [
            MemoryRelationship(
                source=f"PAT-{i:03d}",
                target=f"PAT-{i+1:03d}",
                type=MemoryRelationshipType.RELATED_TO,
            )
            for i in range(1, 4)
        ]
        graph = MemoryGraph(
            nodes={c.id: c for c in concepts},
            edges=edges,
        )

        # Depth 1: should get PAT-001, PAT-002
        result = traverse_bfs(graph, "PAT-001", max_depth=1)
        assert len(result) == 2

        # Depth 2: should get PAT-001, PAT-002, PAT-003
        result = traverse_bfs(graph, "PAT-001", max_depth=2)
        assert len(result) == 3

    def test_traverse_filters_edge_types(self) -> None:
        """Traverse filters by edge type."""
        concepts = [
            MemoryConcept(
                id="PAT-001",
                type=MemoryConceptType.PATTERN,
                content="Pattern",
                created=date(2026, 1, 31),
            ),
            MemoryConcept(
                id="SES-001",
                type=MemoryConceptType.SESSION,
                content="Session",
                created=date(2026, 1, 31),
            ),
            MemoryConcept(
                id="CAL-001",
                type=MemoryConceptType.CALIBRATION,
                content="Calibration",
                created=date(2026, 1, 31),
            ),
        ]
        edges = [
            MemoryRelationship(
                source="PAT-001",
                target="SES-001",
                type=MemoryRelationshipType.LEARNED_FROM,
            ),
            MemoryRelationship(
                source="PAT-001",
                target="CAL-001",
                type=MemoryRelationshipType.RELATED_TO,
            ),
        ]
        graph = MemoryGraph(
            nodes={c.id: c for c in concepts},
            edges=edges,
        )

        # Filter to only LEARNED_FROM
        result = traverse_bfs(
            graph, "PAT-001", edge_types=[MemoryRelationshipType.LEARNED_FROM]
        )
        ids = [c.id for c in result]
        assert "SES-001" in ids
        assert "CAL-001" not in ids


class TestMemoryGraphBuilder:
    """Tests for MemoryGraphBuilder class."""

    def test_build_empty_concepts(self) -> None:
        """Build graph from empty concepts list."""
        builder = MemoryGraphBuilder()
        graph = builder.build([])

        assert len(graph.nodes) == 0
        assert len(graph.edges) == 0
        assert graph.metadata["node_count"] == 0

    def test_build_with_concepts(self) -> None:
        """Build graph from concepts."""
        concepts = [
            MemoryConcept(
                id="PAT-001",
                type=MemoryConceptType.PATTERN,
                content="Test pattern",
                context=["testing"],
                created=date(2026, 1, 31),
            ),
            MemoryConcept(
                id="CAL-001",
                type=MemoryConceptType.CALIBRATION,
                content="Test calibration",
                context=["testing"],
                created=date(2026, 1, 31),
            ),
        ]

        builder = MemoryGraphBuilder()
        graph = builder.build(concepts)

        assert len(graph.nodes) == 2
        assert graph.metadata["patterns"] == 1
        assert graph.metadata["calibrations"] == 1

    def test_infer_related_to_from_shared_context(self) -> None:
        """Infer related_to from shared context keywords."""
        concepts = [
            MemoryConcept(
                id="PAT-001",
                type=MemoryConceptType.PATTERN,
                content="Pattern",
                context=["testing", "pytest", "coverage"],
                created=date(2026, 1, 31),
            ),
            MemoryConcept(
                id="CAL-001",
                type=MemoryConceptType.CALIBRATION,
                content="Calibration",
                context=["testing", "pytest", "velocity"],
                created=date(2026, 1, 31),
            ),
        ]

        builder = MemoryGraphBuilder(min_shared_keywords=2)
        graph = builder.build(concepts)

        # Should have related_to edge
        related = [e for e in graph.edges if e.type == MemoryRelationshipType.RELATED_TO]
        assert len(related) == 1
        assert set(related[0].metadata["shared_keywords"]) == {"testing", "pytest"}

    def test_no_related_to_for_same_type(self) -> None:
        """Don't infer related_to between same type concepts."""
        concepts = [
            MemoryConcept(
                id="PAT-001",
                type=MemoryConceptType.PATTERN,
                content="Pattern 1",
                context=["testing", "pytest"],
                created=date(2026, 1, 31),
            ),
            MemoryConcept(
                id="PAT-002",
                type=MemoryConceptType.PATTERN,
                content="Pattern 2",
                context=["testing", "pytest"],
                created=date(2026, 1, 31),
            ),
        ]

        builder = MemoryGraphBuilder(min_shared_keywords=2)
        graph = builder.build(concepts)

        # Should NOT have related_to edge between patterns
        related = [e for e in graph.edges if e.type == MemoryRelationshipType.RELATED_TO]
        assert len(related) == 0

    def test_infer_validates_from_feature(self) -> None:
        """Infer validates from calibration → pattern with same feature."""
        concepts = [
            MemoryConcept(
                id="PAT-001",
                type=MemoryConceptType.PATTERN,
                content="Pattern",
                created=date(2026, 1, 31),
                metadata={"learned_from": "F2.1"},
            ),
            MemoryConcept(
                id="CAL-001",
                type=MemoryConceptType.CALIBRATION,
                content="Calibration",
                created=date(2026, 1, 31),
                metadata={"feature": "F2.1"},
            ),
        ]

        builder = MemoryGraphBuilder()
        graph = builder.build(concepts)

        validates = [e for e in graph.edges if e.type == MemoryRelationshipType.VALIDATES]
        assert len(validates) == 1
        assert validates[0].source == "CAL-001"
        assert validates[0].target == "PAT-001"

    def test_build_with_real_data(self) -> None:
        """Build graph from real .rai/memory data."""
        from pathlib import Path

        from raise_cli.memory.loader import load_memory_from_directory

        rai_memory = Path(".rai/memory")
        if not rai_memory.exists():
            pytest.skip(".rai/memory directory not found")

        result = load_memory_from_directory(rai_memory)
        builder = MemoryGraphBuilder()
        graph = builder.build(result.concepts)

        # Should have built a graph with nodes and edges
        assert len(graph.nodes) > 0
        assert graph.metadata["node_count"] == len(graph.nodes)
