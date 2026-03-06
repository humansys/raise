"""API-based graph backend — sends graph data to rai-server via HTTP.

PRO backend. Requires RAI_SERVER_URL and RAI_API_KEY.
Implements KnowledgeGraphBackend protocol from raise-core (ADR-036).
"""

from __future__ import annotations

import logging
from typing import Any

try:
    import httpx
except ModuleNotFoundError as exc:
    raise ModuleNotFoundError(
        "httpx is required for the API graph backend. "
        "Install with: pip install 'raise-cli[dev]'"
    ) from exc

from raise_core.graph.backends.models import BackendHealth
from raise_core.graph.engine import Graph

logger = logging.getLogger(__name__)

__all__ = ["ApiGraphBackend"]


class ApiGraphBackend:
    """HTTP client backend — persists graph to rai-server.

    Args:
        server_url: Base URL of the rai-server (e.g. "http://localhost:8000").
        api_key: API key for authentication (rsk_ prefix).
        project_id: Project identifier for graph sync.
    """

    def __init__(self, server_url: str, api_key: str, project_id: str) -> None:
        self.server_url = server_url
        self.api_key = api_key
        self.project_id = project_id
        self._client = httpx.Client(
            base_url=server_url,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=httpx.Timeout(connect=5.0, read=30.0, write=30.0, pool=5.0),
        )

    def close(self) -> None:
        """Close the underlying HTTP connection pool."""
        self._client.close()

    def persist(self, graph: Graph) -> None:
        """Send graph to server via POST /api/v1/graph/sync.

        Serializes all nodes and edges from the Graph into the server's
        expected sync payload format.

        Args:
            graph: The graph to persist.
        """
        skipped = 0
        nodes: list[dict[str, Any]] = []
        for node in graph.iter_concepts():
            if not node.content:
                skipped += 1
                continue
            nodes.append(
                {
                    "node_id": node.id,
                    "node_type": node.type,
                    "scope": "project",
                    "content": node.content,
                    "source_file": node.source_file,
                    "properties": node.metadata,
                }
            )
        if skipped:
            logger.info("Skipped %d nodes with empty content", skipped)
        edges: list[dict[str, Any]] = [
            {
                "source_node_id": edge.source,
                "target_node_id": edge.target,
                "edge_type": edge.type,
                "weight": edge.weight,
                "properties": edge.metadata,
            }
            for edge in graph.iter_relationships()
        ]
        payload: dict[str, Any] = {
            "project_id": self.project_id,
            "nodes": nodes,
            "edges": edges,
        }
        response = self._client.post(url="/api/v1/graph/sync", json=payload)
        response.raise_for_status()
        logger.info(
            "Synced to remote server (%d nodes, %d edges)",
            len(nodes),
            len(edges),
        )

    def load(self) -> Graph:
        """Not supported — DualWriteBackend reads from local.

        Raises:
            NotImplementedError: Always. Use DualWriteBackend for load,
                which delegates to local FilesystemGraphBackend.
        """
        raise NotImplementedError(
            "ApiGraphBackend.load() is not supported. "
            "Use DualWriteBackend, which loads from local filesystem."
        )

    def health(self) -> BackendHealth:
        """Check server availability via GET /health.

        Returns:
            BackendHealth with status healthy or unavailable.
        """
        try:
            response = self._client.get(url="/health")
            if response.status_code == 200:
                return BackendHealth(
                    status="healthy",
                    message="API server operational",
                    metadata={"backend": "api", "server_url": self.server_url},
                )
            return BackendHealth(
                status="degraded",
                message=f"Server returned {response.status_code}",
                metadata={"backend": "api", "server_url": self.server_url},
            )
        except httpx.HTTPError as e:
            return BackendHealth(
                status="unavailable",
                message=f"Connection failed: {e}",
                metadata={"backend": "api", "server_url": self.server_url},
            )
