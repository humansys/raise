"""Tests for FilesystemGraphBackend."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from rai_cli.adapters.models import BackendHealth
from rai_cli.adapters.protocols import KnowledgeGraphBackend
from rai_cli.context.graph import UnifiedGraph
from rai_cli.context.models import ConceptEdge, ConceptNode
from rai_cli.graph.filesystem_backend import FilesystemGraphBackend


def _make_sample_graph() -> UnifiedGraph:
    """Create a graph with nodes and edges for testing."""
    graph = UnifiedGraph()
    graph.add_concept(
        ConceptNode(
            id="PAT-001",
            type="pattern",
            content="Test pattern content",
            created="2026-01-01",
        )
    )
    graph.add_concept(
        ConceptNode(
            id="SES-001",
            type="session",
            content="Test session content",
            created="2026-01-02",
        )
    )
    graph.add_relationship(
        ConceptEdge(
            source="PAT-001",
            target="SES-001",
            type="learned_from",
            weight=1.0,
        )
    )
    return graph


class TestFilesystemGraphBackend:
    """Tests for FilesystemGraphBackend class."""

    def test_implements_protocol(self) -> None:
        assert isinstance(FilesystemGraphBackend(), KnowledgeGraphBackend)

    def test_persist_saves_graph_to_json(self, tmp_path: Path) -> None:
        backend = FilesystemGraphBackend()
        graph = _make_sample_graph()
        out = tmp_path / "index.json"

        backend.persist(graph, out)

        assert out.exists()
        data = json.loads(out.read_text(encoding="utf-8"))
        assert "nodes" in data
        assert "edges" in data or "links" in data

    def test_persist_creates_parent_dirs(self, tmp_path: Path) -> None:
        backend = FilesystemGraphBackend()
        graph = _make_sample_graph()
        out = tmp_path / "nested" / "deep" / "index.json"

        backend.persist(graph, out)

        assert out.exists()

    def test_load_reads_graph_from_json(self, tmp_path: Path) -> None:
        backend = FilesystemGraphBackend()
        graph = _make_sample_graph()
        out = tmp_path / "index.json"
        backend.persist(graph, out)

        loaded = backend.load(out)

        assert loaded.node_count == 2
        assert loaded.edge_count == 1

    def test_persist_load_roundtrip(self, tmp_path: Path) -> None:
        backend = FilesystemGraphBackend()
        graph = _make_sample_graph()
        out = tmp_path / "index.json"

        backend.persist(graph, out)
        loaded = backend.load(out)

        # Same structure
        assert loaded.node_count == graph.node_count
        assert loaded.edge_count == graph.edge_count

        # Same content
        original_node = graph.get_concept("PAT-001")
        loaded_node = loaded.get_concept("PAT-001")
        assert original_node is not None
        assert loaded_node is not None
        assert loaded_node.content == original_node.content
        assert loaded_node.type == original_node.type

    def test_load_nonexistent_raises(self, tmp_path: Path) -> None:
        backend = FilesystemGraphBackend()

        with pytest.raises(FileNotFoundError):
            backend.load(tmp_path / "nonexistent.json")

    def test_load_invalid_json_raises(self, tmp_path: Path) -> None:
        backend = FilesystemGraphBackend()
        bad_file = tmp_path / "bad.json"
        bad_file.write_text("not json", encoding="utf-8")

        with pytest.raises(json.JSONDecodeError):
            backend.load(bad_file)

    def test_health_returns_healthy(self) -> None:
        backend = FilesystemGraphBackend()

        result = backend.health()

        assert isinstance(result, BackendHealth)
        assert result.status == "healthy"
        assert "filesystem" in result.message.lower() or "filesystem" in str(
            result.metadata
        )

    def test_persist_format_identical_to_networkx_node_link(
        self, tmp_path: Path
    ) -> None:
        """Verify output format matches what UnifiedGraph.save() produced."""
        import networkx as nx  # type: ignore[import-untyped]

        backend = FilesystemGraphBackend()
        graph = _make_sample_graph()

        # Persist via backend
        backend_path = tmp_path / "backend.json"
        backend.persist(graph, backend_path)

        # Manually serialize the same way the old save() did
        old_data = nx.node_link_data(graph.graph)
        old_json = json.dumps(old_data, indent=2, default=str)

        # Compare
        backend_json = backend_path.read_text(encoding="utf-8")
        assert backend_json == old_json
