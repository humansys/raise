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

from rai_cli.adapters.models import BackendHealth
from rai_cli.context.graph import UnifiedGraph

# Re-export for convenience
__all__ = ["FilesystemGraphBackend", "get_active_backend"]


class FilesystemGraphBackend:
    """Built-in graph backend — persists to local filesystem.

    COMMUNITY backend. Zero external dependencies.
    Registered as entry point 'local' in rai.graph.backends.
    """

    def persist(self, graph: UnifiedGraph, path: Path) -> None:
        """Save graph to JSON file using NetworkX node_link_data format.

        Args:
            graph: The unified graph to persist.
            path: Path to save the JSON file.
        """
        data: dict[str, Any] = nx.node_link_data(graph.graph)  # type: ignore[assignment]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")

    def load(self, path: Path) -> UnifiedGraph:
        """Load graph from JSON file.

        Args:
            path: Path to the JSON file.

        Returns:
            UnifiedGraph instance with loaded data.

        Raises:
            FileNotFoundError: If the file doesn't exist.
            json.JSONDecodeError: If the file is not valid JSON.
        """
        loaded_data: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
        instance = UnifiedGraph()
        instance.graph = nx.node_link_graph(loaded_data, directed=True, multigraph=True)
        return instance

    def health(self) -> BackendHealth:
        """Check backend health. Filesystem is always available."""
        return BackendHealth(
            status="healthy",
            message="Filesystem backend operational",
            metadata={"backend": "filesystem"},
        )


def get_active_backend() -> FilesystemGraphBackend:
    """Resolve the active graph backend.

    Returns FilesystemGraphBackend (COMMUNITY). S211.5 (TierContext)
    will add tier-based selection via entry point discovery.
    """
    return FilesystemGraphBackend()
