"""Filesystem-based graph backend.

Built-in COMMUNITY backend — persists the knowledge graph to local JSON files.
Zero external dependencies beyond NetworkX (already a core dependency).

Architecture: ADR-036 (KnowledgeGraphBackend)
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import networkx as nx  # type: ignore[import-untyped]

from raise_core.graph.backends.models import BackendHealth
from raise_core.graph.engine import Graph

__all__ = ["FilesystemGraphBackend", "get_active_backend"]


class FilesystemGraphBackend:
    """Built-in graph backend — persists to local filesystem.

    COMMUNITY backend. Zero external dependencies.
    Registered as entry point 'local' in rai.graph.backends.

    Args:
        path: Path to the graph JSON file (e.g. `.raise/rai/memory/index.json`).
    """

    def __init__(self, path: Path) -> None:
        self.path = path

    def persist(self, graph: Graph) -> None:
        """Save graph to JSON file using NetworkX node_link_data format.

        Args:
            graph: The graph to persist.
        """
        data: dict[str, Any] = nx.node_link_data(graph.graph)  # type: ignore[assignment]
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")

    def load(self) -> Graph:
        """Load graph from the configured path.

        Returns:
            Graph instance with loaded data.

        Raises:
            FileNotFoundError: If the file doesn't exist.
            json.JSONDecodeError: If the file is not valid JSON.
        """
        loaded_data: dict[str, Any] = json.loads(self.path.read_text(encoding="utf-8"))
        instance = Graph()
        instance.graph = nx.node_link_graph(loaded_data, directed=True, multigraph=True)
        return instance

    def health(self) -> BackendHealth:
        """Check backend health. Filesystem is always available."""
        return BackendHealth(
            status="healthy",
            message="Filesystem backend operational",
            metadata={"backend": "filesystem"},
        )


def get_active_backend(path: Path) -> FilesystemGraphBackend:
    """Resolve the active graph backend for the given path.

    Returns FilesystemGraphBackend (COMMUNITY). Future: tier-based
    selection via env vars (DualWriteBackend when RAI_SERVER_URL set).

    Args:
        path: Path to the graph JSON file.
    """
    return FilesystemGraphBackend(path=path)
