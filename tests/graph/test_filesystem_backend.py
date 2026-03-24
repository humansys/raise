"""Tests for FilesystemGraphBackend."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from raise_core.graph.backends.filesystem import (
    FilesystemGraphBackend,
    get_active_backend,
)
from raise_core.graph.backends.models import BackendHealth
from raise_core.graph.backends.protocol import KnowledgeGraphBackend
from raise_core.graph.engine import Graph
from raise_core.graph.models import GraphEdge, GraphNode


def _make_sample_graph() -> Graph:
    """Create a graph with nodes and edges for testing."""
    graph = Graph()
    graph.add_concept(
        GraphNode(
            id="PAT-001",
            type="pattern",
            content="Test pattern content",
            created="2026-01-01",
        )
    )
    graph.add_concept(
        GraphNode(
            id="SES-001",
            type="session",
            content="Test session content",
            created="2026-01-02",
        )
    )
    graph.add_relationship(
        GraphEdge(
            source="PAT-001",
            target="SES-001",
            type="learned_from",
            weight=1.0,
        )
    )
    return graph


class TestFilesystemGraphBackend:
    """Tests for FilesystemGraphBackend class."""

    def test_implements_protocol(self, tmp_path: Path) -> None:
        assert isinstance(
            FilesystemGraphBackend(tmp_path / "g.json"), KnowledgeGraphBackend
        )

    def test_persist_saves_graph_to_json(self, tmp_path: Path) -> None:
        out = tmp_path / "index.json"
        backend = FilesystemGraphBackend(out)
        graph = _make_sample_graph()

        backend.persist(graph)

        assert out.exists()
        data = json.loads(out.read_text(encoding="utf-8"))
        assert "nodes" in data
        assert "edges" in data or "links" in data

    def test_persist_creates_parent_dirs(self, tmp_path: Path) -> None:
        out = tmp_path / "nested" / "deep" / "index.json"
        backend = FilesystemGraphBackend(out)
        graph = _make_sample_graph()

        backend.persist(graph)

        assert out.exists()

    def test_load_reads_graph_from_json(self, tmp_path: Path) -> None:
        out = tmp_path / "index.json"
        backend = FilesystemGraphBackend(out)
        graph = _make_sample_graph()
        backend.persist(graph)

        loaded = backend.load()

        assert loaded.node_count == 2
        assert loaded.edge_count == 1

    def test_persist_load_roundtrip(self, tmp_path: Path) -> None:
        out = tmp_path / "index.json"
        backend = FilesystemGraphBackend(out)
        graph = _make_sample_graph()

        backend.persist(graph)
        loaded = backend.load()

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
        backend = FilesystemGraphBackend(tmp_path / "nonexistent.json")

        with pytest.raises(FileNotFoundError):
            backend.load()

    def test_load_invalid_json_raises(self, tmp_path: Path) -> None:
        bad_file = tmp_path / "bad.json"
        bad_file.write_text("not json", encoding="utf-8")
        backend = FilesystemGraphBackend(bad_file)

        with pytest.raises(json.JSONDecodeError):
            backend.load()

    def test_health_returns_healthy(self, tmp_path: Path) -> None:
        backend = FilesystemGraphBackend(tmp_path / "g.json")

        result = backend.health()

        assert isinstance(result, BackendHealth)
        assert result.status == "healthy"
        assert "filesystem" in result.message.lower() or "filesystem" in str(
            result.metadata
        )

    def test_persist_format_identical_to_networkx_node_link(
        self, tmp_path: Path
    ) -> None:
        """Verify output format matches what Graph.save() produced."""
        import networkx as nx  # type: ignore[import-untyped]

        backend_path = tmp_path / "backend.json"
        backend = FilesystemGraphBackend(backend_path)
        graph = _make_sample_graph()

        backend.persist(graph)

        # Manually serialize the same way the old save() did
        old_data = nx.node_link_data(graph.graph)
        old_json = json.dumps(old_data, indent=2, default=str)

        # Compare
        backend_json = backend_path.read_text(encoding="utf-8")
        assert backend_json == old_json


class TestGetActiveBackend:
    """Tests for get_active_backend helper."""

    def test_returns_filesystem_backend(self, tmp_path: Path) -> None:
        backend = get_active_backend(tmp_path / "index.json")
        assert isinstance(backend, FilesystemGraphBackend)

    def test_returns_protocol_compatible(self, tmp_path: Path) -> None:
        backend = get_active_backend(tmp_path / "index.json")
        assert isinstance(backend, KnowledgeGraphBackend)

    def test_backend_has_correct_path(self, tmp_path: Path) -> None:
        path = tmp_path / "custom.json"
        backend = get_active_backend(path)
        assert backend.path == path
