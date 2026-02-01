"""Tests for graph models."""

import json

import pytest

from raise_cli.governance.graph.models import ConceptGraph, Relationship
from raise_cli.governance.models import Concept, ConceptType


@pytest.fixture
def sample_concept() -> Concept:
    """Create a sample concept for testing."""
    return Concept(
        id="req-rf-05",
        type=ConceptType.REQUIREMENT,
        file="governance/projects/raise-cli/prd.md",
        section="RF-05: Golden Context Generation",
        lines=(206, 214),
        content="The system MUST generate CLAUDE.md...",
        metadata={"requirement_id": "RF-05", "title": "Golden Context Generation"},
    )


@pytest.fixture
def sample_outcome() -> Concept:
    """Create a sample outcome for testing."""
    return Concept(
        id="outcome-context-generation",
        type=ConceptType.OUTCOME,
        file="governance/solution/vision.md",
        section="Context Generation",
        lines=(50, 55),
        content="Enable AI agents to receive relevant context...",
        metadata={"title": "Context Generation"},
    )


@pytest.fixture
def sample_principle() -> Concept:
    """Create a sample principle for testing."""
    return Concept(
        id="principle-governance-as-code",
        type=ConceptType.PRINCIPLE,
        file="framework/reference/constitution.md",
        section="§2. Governance as Code",
        lines=(100, 115),
        content="Standards versioned in Git; what's not in repo doesn't exist",
        metadata={"principle_number": 2},
    )


class TestRelationship:
    """Tests for Relationship model."""

    def test_create_relationship(self) -> None:
        """Test relationship creation."""
        rel = Relationship(
            source="req-rf-05",
            target="outcome-context-generation",
            type="implements",
            metadata={"confidence": 0.8, "method": "keyword_match"},
        )

        assert rel.source == "req-rf-05"
        assert rel.target == "outcome-context-generation"
        assert rel.type == "implements"
        assert rel.metadata["confidence"] == 0.8
        assert rel.metadata["method"] == "keyword_match"

    def test_relationship_types(self) -> None:
        """Test all relationship types are valid."""
        valid_types = ["implements", "governed_by", "depends_on", "related_to", "validates"]

        for rel_type in valid_types:
            rel = Relationship(source="a", target="b", type=rel_type)  # type: ignore
            assert rel.type == rel_type

    def test_relationship_default_metadata(self) -> None:
        """Test relationship with default empty metadata."""
        rel = Relationship(source="a", target="b", type="implements")
        assert rel.metadata == {}


class TestConceptGraph:
    """Tests for ConceptGraph model."""

    def test_create_empty_graph(self) -> None:
        """Test creating an empty graph."""
        graph = ConceptGraph()

        assert len(graph.nodes) == 0
        assert len(graph.edges) == 0
        assert graph.metadata == {}

    def test_create_graph_with_nodes(
        self, sample_concept: Concept, sample_outcome: Concept
    ) -> None:
        """Test creating graph with nodes."""
        graph = ConceptGraph(
            nodes={
                sample_concept.id: sample_concept,
                sample_outcome.id: sample_outcome,
            }
        )

        assert len(graph.nodes) == 2
        assert sample_concept.id in graph.nodes
        assert sample_outcome.id in graph.nodes

    def test_create_graph_with_edges(
        self, sample_concept: Concept, sample_outcome: Concept
    ) -> None:
        """Test creating graph with edges."""
        rel = Relationship(
            source=sample_concept.id,
            target=sample_outcome.id,
            type="implements",
        )

        graph = ConceptGraph(
            nodes={
                sample_concept.id: sample_concept,
                sample_outcome.id: sample_outcome,
            },
            edges=[rel],
        )

        assert len(graph.edges) == 1
        assert graph.edges[0].source == sample_concept.id
        assert graph.edges[0].target == sample_outcome.id

    def test_get_node_existing(self, sample_concept: Concept) -> None:
        """Test getting an existing node."""
        graph = ConceptGraph(nodes={sample_concept.id: sample_concept})

        node = graph.get_node(sample_concept.id)

        assert node is not None
        assert node.id == sample_concept.id
        assert node.type == ConceptType.REQUIREMENT

    def test_get_node_nonexistent(self) -> None:
        """Test getting a non-existent node returns None."""
        graph = ConceptGraph()

        node = graph.get_node("nonexistent-id")

        assert node is None

    def test_get_outgoing_edges(
        self, sample_concept: Concept, sample_outcome: Concept, sample_principle: Concept
    ) -> None:
        """Test getting outgoing edges from a node."""
        rel1 = Relationship(source=sample_concept.id, target=sample_outcome.id, type="implements")
        rel2 = Relationship(source=sample_concept.id, target=sample_principle.id, type="governed_by")
        rel3 = Relationship(source=sample_outcome.id, target=sample_principle.id, type="governed_by")

        graph = ConceptGraph(
            nodes={
                sample_concept.id: sample_concept,
                sample_outcome.id: sample_outcome,
                sample_principle.id: sample_principle,
            },
            edges=[rel1, rel2, rel3],
        )

        # Get all outgoing edges
        edges = graph.get_outgoing_edges(sample_concept.id)
        assert len(edges) == 2

        # Get filtered by type
        implements_edges = graph.get_outgoing_edges(sample_concept.id, edge_type="implements")
        assert len(implements_edges) == 1
        assert implements_edges[0].type == "implements"

        governed_edges = graph.get_outgoing_edges(sample_concept.id, edge_type="governed_by")
        assert len(governed_edges) == 1
        assert governed_edges[0].type == "governed_by"

    def test_get_outgoing_edges_none(self, sample_concept: Concept) -> None:
        """Test getting outgoing edges when none exist."""
        graph = ConceptGraph(nodes={sample_concept.id: sample_concept})

        edges = graph.get_outgoing_edges(sample_concept.id)

        assert len(edges) == 0

    def test_get_incoming_edges(
        self, sample_concept: Concept, sample_outcome: Concept, sample_principle: Concept
    ) -> None:
        """Test getting incoming edges to a node."""
        rel1 = Relationship(source=sample_concept.id, target=sample_outcome.id, type="implements")
        rel2 = Relationship(source=sample_concept.id, target=sample_principle.id, type="governed_by")
        rel3 = Relationship(source=sample_outcome.id, target=sample_principle.id, type="governed_by")

        graph = ConceptGraph(
            nodes={
                sample_concept.id: sample_concept,
                sample_outcome.id: sample_outcome,
                sample_principle.id: sample_principle,
            },
            edges=[rel1, rel2, rel3],
        )

        # Get all incoming edges to principle
        edges = graph.get_incoming_edges(sample_principle.id)
        assert len(edges) == 2

        # Get filtered by type
        governed_edges = graph.get_incoming_edges(sample_principle.id, edge_type="governed_by")
        assert len(governed_edges) == 2

    def test_get_incoming_edges_none(self, sample_concept: Concept) -> None:
        """Test getting incoming edges when none exist."""
        graph = ConceptGraph(nodes={sample_concept.id: sample_concept})

        edges = graph.get_incoming_edges(sample_concept.id)

        assert len(edges) == 0

    def test_json_serialization_roundtrip(
        self, sample_concept: Concept, sample_outcome: Concept
    ) -> None:
        """Test JSON serialization and deserialization preserves graph."""
        rel = Relationship(source=sample_concept.id, target=sample_outcome.id, type="implements")

        original_graph = ConceptGraph(
            nodes={
                sample_concept.id: sample_concept,
                sample_outcome.id: sample_outcome,
            },
            edges=[rel],
            metadata={"build_time": "2026-01-31", "version": "1.0"},
        )

        # Serialize to JSON
        json_str = original_graph.to_json()

        # Verify it's valid JSON
        parsed = json.loads(json_str)
        assert "nodes" in parsed
        assert "edges" in parsed
        assert "metadata" in parsed

        # Deserialize back
        loaded_graph = ConceptGraph.from_json(json_str)

        # Verify equivalence
        assert len(loaded_graph.nodes) == len(original_graph.nodes)
        assert len(loaded_graph.edges) == len(original_graph.edges)
        assert loaded_graph.metadata == original_graph.metadata

        # Verify node data preserved
        assert sample_concept.id in loaded_graph.nodes
        loaded_concept = loaded_graph.nodes[sample_concept.id]
        assert loaded_concept.id == sample_concept.id
        assert loaded_concept.type == sample_concept.type
        assert loaded_concept.content == sample_concept.content

        # Verify edge data preserved
        assert loaded_graph.edges[0].source == rel.source
        assert loaded_graph.edges[0].target == rel.target
        assert loaded_graph.edges[0].type == rel.type

    def test_graph_with_metadata(self, sample_concept: Concept) -> None:
        """Test graph with metadata."""
        metadata = {
            "build_time": "2026-01-31T21:15:00",
            "version": "1.0",
            "stats": {"nodes": 1, "edges": 0},
        }

        graph = ConceptGraph(
            nodes={sample_concept.id: sample_concept},
            metadata=metadata,
        )

        assert graph.metadata["build_time"] == "2026-01-31T21:15:00"
        assert graph.metadata["version"] == "1.0"
        assert graph.metadata["stats"]["nodes"] == 1
