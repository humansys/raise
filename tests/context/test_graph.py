"""Tests for Graph class."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from raise_core.graph.backends.filesystem import FilesystemGraphBackend
from raise_core.graph.engine import Graph
from raise_core.graph.models import (
    EpicNode,
    GraphEdge,
    GraphNode,
    PatternNode,
    SessionNode,
)


@pytest.fixture
def empty_graph() -> Graph:
    """Create an empty graph."""
    return Graph()


@pytest.fixture
def sample_graph() -> Graph:
    """Create a graph with sample data."""
    graph = Graph()

    # Add nodes
    nodes = [
        GraphNode(
            id="PAT-001",
            type="pattern",
            content="Singleton pattern for testing",
            created="2026-01-31",
            metadata={"sub_type": "codebase"},
        ),
        GraphNode(
            id="PAT-002",
            type="pattern",
            content="Risk-first sequencing pattern",
            created="2026-02-01",
            metadata={"sub_type": "process"},
        ),
        GraphNode(
            id="SES-015",
            type="session",
            content="E11 Unified Context Architecture Design",
            created="2026-02-03",
        ),
        GraphNode(
            id="§2",
            type="principle",
            content="Governance as Code",
            created="2026-01-01",
        ),
        GraphNode(
            id="/story-plan",
            type="skill",
            content="Decompose user stories into tasks",
            created="2026-02-01",
        ),
    ]
    for node in nodes:
        graph.add_concept(node)

    # Add edges
    edges = [
        GraphEdge(source="PAT-001", target="SES-015", type="learned_from"),
        GraphEdge(source="PAT-002", target="SES-015", type="learned_from"),
        GraphEdge(source="PAT-002", target="/story-plan", type="applies_to"),
        GraphEdge(source="/story-plan", target="§2", type="governed_by"),
    ]
    for edge in edges:
        graph.add_relationship(edge)

    return graph


class TestGraphBasics:
    """Basic Graph tests."""

    def test_empty_graph(self, empty_graph: Graph) -> None:
        """Test empty graph initialization."""
        assert empty_graph.node_count == 0
        assert empty_graph.edge_count == 0

    def test_add_concept(self, empty_graph: Graph) -> None:
        """Test adding a concept."""
        node = GraphNode(
            id="PAT-001",
            type="pattern",
            content="Test pattern",
            created="2026-02-03",
        )
        empty_graph.add_concept(node)
        assert empty_graph.node_count == 1

    def test_add_relationship(self, empty_graph: Graph) -> None:
        """Test adding a relationship."""
        edge = GraphEdge(
            source="A",
            target="B",
            type="related_to",
        )
        empty_graph.add_relationship(edge)
        assert empty_graph.edge_count == 1

    def test_get_concept(self, sample_graph: Graph) -> None:
        """Test getting a concept by ID."""
        node = sample_graph.get_concept("PAT-001")
        assert node is not None
        assert node.id == "PAT-001"
        assert node.type == "pattern"
        assert "Singleton" in node.content

    def test_get_concept_not_found(self, sample_graph: Graph) -> None:
        """Test getting a non-existent concept."""
        node = sample_graph.get_concept("NONEXISTENT")
        assert node is None

    def test_sample_graph_counts(self, sample_graph: Graph) -> None:
        """Test sample graph has expected counts."""
        assert sample_graph.node_count == 5
        assert sample_graph.edge_count == 4


class TestGraphQueries:
    """Query-related tests."""

    def test_get_concepts_by_type(self, sample_graph: Graph) -> None:
        """Test getting concepts by type."""
        patterns = sample_graph.get_concepts_by_type("pattern")
        assert len(patterns) == 2
        assert all(p.type == "pattern" for p in patterns)

    def test_get_concepts_by_type_empty(self, sample_graph: Graph) -> None:
        """Test getting concepts of type with no matches."""
        calibrations = sample_graph.get_concepts_by_type("calibration")
        assert len(calibrations) == 0

    def test_get_neighbors_depth_1(self, sample_graph: Graph) -> None:
        """Test getting neighbors at depth 1."""
        neighbors = sample_graph.get_neighbors("SES-015", depth=1)
        # SES-015 has incoming edges from PAT-001 and PAT-002
        assert len(neighbors) == 2
        neighbor_ids = {n.id for n in neighbors}
        assert "PAT-001" in neighbor_ids
        assert "PAT-002" in neighbor_ids

    def test_get_neighbors_depth_2(self, sample_graph: Graph) -> None:
        """Test getting neighbors at depth 2."""
        neighbors = sample_graph.get_neighbors("SES-015", depth=2)
        # Depth 2 should also include /story-plan (via PAT-002)
        neighbor_ids = {n.id for n in neighbors}
        assert "PAT-001" in neighbor_ids
        assert "PAT-002" in neighbor_ids
        assert "/story-plan" in neighbor_ids

    def test_get_neighbors_with_edge_filter(self, sample_graph: Graph) -> None:
        """Test getting neighbors with edge type filter."""
        neighbors = sample_graph.get_neighbors(
            "PAT-002", depth=1, edge_types=["applies_to"]
        )
        neighbor_ids = {n.id for n in neighbors}
        assert "/story-plan" in neighbor_ids
        # Should not include SES-015 (learned_from edge)
        assert "SES-015" not in neighbor_ids

    def test_get_neighbors_not_found(self, sample_graph: Graph) -> None:
        """Test getting neighbors of non-existent node."""
        neighbors = sample_graph.get_neighbors("NONEXISTENT")
        assert len(neighbors) == 0


class TestGraphIteration:
    """Iteration tests."""

    def test_iter_concepts(self, sample_graph: Graph) -> None:
        """Test iterating over all concepts."""
        concepts = list(sample_graph.iter_concepts())
        assert len(concepts) == 5
        concept_ids = {c.id for c in concepts}
        assert "PAT-001" in concept_ids
        assert "SES-015" in concept_ids

    def test_iter_relationships(self, sample_graph: Graph) -> None:
        """Test iterating over all relationships."""
        edges = list(sample_graph.iter_relationships())
        assert len(edges) == 4
        edge_types = {e.type for e in edges}
        assert "learned_from" in edge_types
        assert "applies_to" in edge_types
        assert "governed_by" in edge_types


class TestGraphPersistence:
    """Persistence tests via FilesystemGraphBackend."""

    def test_save_and_load(self, sample_graph: Graph, tmp_path: Path) -> None:
        """Test saving and loading a graph via backend."""
        save_path = tmp_path / "test_graph.json"
        backend = FilesystemGraphBackend(save_path)
        backend.persist(sample_graph)
        assert save_path.exists()

        # Verify JSON structure
        data = json.loads(save_path.read_text(encoding="utf-8"))
        assert "nodes" in data
        assert "edges" in data or "links" in data  # NetworkX 3.x uses "edges"

        # Load
        loaded = backend.load()
        assert loaded.node_count == sample_graph.node_count
        assert loaded.edge_count == sample_graph.edge_count

        # Verify concepts
        pat = loaded.get_concept("PAT-001")
        assert pat is not None
        assert pat.type == "pattern"

    def test_save_creates_parent_dirs(self, empty_graph: Graph, tmp_path: Path) -> None:
        """Test that persist creates parent directories."""
        save_path = tmp_path / "nested" / "dir" / "graph.json"
        backend = FilesystemGraphBackend(save_path)
        backend.persist(empty_graph)
        assert save_path.exists()

    def test_load_file_not_found(self, tmp_path: Path) -> None:
        """Test loading non-existent file raises error."""
        backend = FilesystemGraphBackend(tmp_path / "nonexistent.json")
        with pytest.raises(FileNotFoundError):
            backend.load()

    def test_load_preserves_metadata(self, sample_graph: Graph, tmp_path: Path) -> None:
        """Test that node metadata is preserved on load."""
        save_path = tmp_path / "test_graph.json"
        backend = FilesystemGraphBackend(save_path)
        backend.persist(sample_graph)

        loaded = backend.load()
        pat = loaded.get_concept("PAT-001")
        assert pat is not None
        assert pat.metadata.get("sub_type") == "codebase"


class TestGraphEdgeCases:
    """Edge case tests."""

    def test_duplicate_node_overwrites(self, empty_graph: Graph) -> None:
        """Test that adding duplicate node ID overwrites."""
        node1 = GraphNode(
            id="PAT-001",
            type="pattern",
            content="Original",
            created="2026-02-01",
        )
        node2 = GraphNode(
            id="PAT-001",
            type="pattern",
            content="Updated",
            created="2026-02-02",
        )
        empty_graph.add_concept(node1)
        empty_graph.add_concept(node2)

        assert empty_graph.node_count == 1
        retrieved = empty_graph.get_concept("PAT-001")
        assert retrieved is not None
        assert retrieved.content == "Updated"

    def test_self_referential_edge(self, empty_graph: Graph) -> None:
        """Test self-referential edge."""
        edge = GraphEdge(
            source="A",
            target="A",
            type="related_to",
        )
        empty_graph.add_relationship(edge)
        assert empty_graph.edge_count == 1

    def test_multiple_edges_same_nodes(self, empty_graph: Graph) -> None:
        """Test multiple edges between same nodes (MultiDiGraph)."""
        edge1 = GraphEdge(source="A", target="B", type="related_to")
        edge2 = GraphEdge(source="A", target="B", type="implements")
        empty_graph.add_relationship(edge1)
        empty_graph.add_relationship(edge2)
        assert empty_graph.edge_count == 2


class TestGraphNodeDeserialization:
    """Tests for typed GraphNode reconstruction from graph storage."""

    def test_get_concept_returns_correct_subclass(self) -> None:
        """Adding an EpicNode and retrieving it returns EpicNode instance."""
        graph = Graph()
        node = EpicNode(id="E1", content="test epic", created="2026-01-01")
        graph.add_concept(node)
        retrieved = graph.get_concept("E1")
        assert retrieved is not None
        assert isinstance(retrieved, EpicNode)
        assert retrieved.type == "epic"

    def test_get_concepts_by_type_returns_subclasses(self) -> None:
        """get_concepts_by_type returns correct subclass instances."""
        graph = Graph()
        graph.add_concept(PatternNode(id="P1", content="pat1", created="2026-01-01"))
        graph.add_concept(PatternNode(id="P2", content="pat2", created="2026-01-01"))
        graph.add_concept(EpicNode(id="E1", content="epic1", created="2026-01-01"))
        patterns = graph.get_concepts_by_type("pattern")
        assert len(patterns) == 2
        assert all(isinstance(p, PatternNode) for p in patterns)

    def test_iter_concepts_yields_subclasses(self) -> None:
        """iter_concepts yields correct subclass instances."""
        graph = Graph()
        graph.add_concept(EpicNode(id="E1", content="epic", created="2026-01-01"))
        graph.add_concept(SessionNode(id="S1", content="session", created="2026-01-01"))
        concepts = list(graph.iter_concepts())
        types_found = {type(c).__name__ for c in concepts}
        assert "EpicNode" in types_found
        assert "SessionNode" in types_found

    def test_save_load_roundtrip_preserves_subclass(self, tmp_path: Path) -> None:
        """Persist → load → get_concept returns correct subclass."""
        path = tmp_path / "graph.json"
        backend = FilesystemGraphBackend(path)
        graph = Graph()
        graph.add_concept(
            EpicNode(
                id="E1",
                content="test epic",
                created="2026-01-01",
                metadata={"key": "RAISE-211"},
            )
        )
        backend.persist(graph)

        loaded = backend.load()
        retrieved = loaded.get_concept("E1")
        assert retrieved is not None
        assert isinstance(retrieved, EpicNode)
        assert retrieved.type == "epic"
        assert retrieved.metadata["key"] == "RAISE-211"

    def test_unknown_type_falls_back_to_graphnode(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Node with unregistered type loads as GraphNode base with warning."""
        import logging

        graph = Graph()
        # Manually inject a node with unknown type via NetworkX
        graph.graph.add_node(
            "U1",
            type="jira.sprint",
            content="Sprint 42",
            created="2026-01-01",
            metadata={},
        )
        with caplog.at_level(logging.WARNING):
            retrieved = graph.get_concept("U1")
        assert retrieved is not None
        assert isinstance(retrieved, GraphNode)
        assert type(retrieved) is GraphNode  # exact type, not subclass
        assert retrieved.type == "jira.sprint"
        assert "not registered" in caplog.text

    def test_iter_concepts_skips_invalid_node_from_backend(
        self, caplog: pytest.LogCaptureFixture, tmp_path: Path
    ) -> None:
        """iter_concepts survives corrupt graph JSON loaded via FilesystemGraphBackend.

        Mirrors the actual crash path in `rai graph build`:
          backend.load() → diff_graphs(old_graph, new) → old_graph.iter_concepts()
        """
        import json
        import logging

        # Build a graph JSON with one valid node and one invalid node
        # (missing required fields — simulates removed plugin or schema drift)
        valid_node = {
            "id": "PAT-001",
            "type": "pattern",
            "content": "valid content",
            "created": "2026-01-01",
            "source_file": None,
            "metadata": {},
        }
        invalid_node = {
            "id": "BAD-001",
            "type": "removed.plugin.type",
            # missing content and created — will fail model_validate
        }

        # Build networkx node_link_data format directly
        graph_data: dict[str, object] = {
            "directed": True,
            "multigraph": True,
            "graph": {},
            "nodes": [valid_node, invalid_node],
            "edges": [],
        }
        graph_path = tmp_path / "graph.json"
        graph_path.write_text(json.dumps(graph_data), encoding="utf-8")

        backend = FilesystemGraphBackend(graph_path)
        loaded = backend.load()

        with caplog.at_level(logging.WARNING):
            concepts = list(loaded.iter_concepts())

        # Valid node returned; invalid node skipped without raising
        assert len(concepts) == 1
        assert concepts[0].id == "PAT-001"
        assert "BAD-001" in caplog.text

    def test_iter_concepts_skips_invalid_node(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """iter_concepts skips nodes with schema drift and emits a warning.

        Simulates a node saved by a now-removed plugin that lacks required fields.
        The valid node must still be returned; the invalid one must be skipped,
        not crash the process.
        """
        import logging

        graph = Graph()
        # Valid node
        graph.add_concept(
            GraphNode(
                id="PAT-001",
                type="pattern",
                content="good node",
                created="2026-01-01",
            )
        )
        # Invalid node — missing required fields (content, created), simulating
        # schema drift from a removed plugin.
        graph.graph.add_node(
            "BAD-001",
            type="removed.plugin.type",
        )

        with caplog.at_level(logging.WARNING):
            concepts = list(graph.iter_concepts())

        # Invalid node skipped — does not raise
        assert len(concepts) == 1
        assert concepts[0].id == "PAT-001"
        # Warning emitted containing the bad node's ID
        assert "BAD-001" in caplog.text
