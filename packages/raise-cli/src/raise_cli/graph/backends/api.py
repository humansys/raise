"""API-based graph backend — sends graph data to rai-server via HTTP.

PRO backend. Requires RAISE_SERVER_URL and RAISE_API_KEY.
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

CHUNK_SIZE = 500


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
        self._embeddings: dict[str, list[float]] = {}
        self._client = httpx.Client(
            base_url=server_url,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=httpx.Timeout(connect=5.0, read=60.0, write=60.0, pool=5.0),
        )

    def close(self) -> None:
        """Close the underlying HTTP connection pool."""
        self._client.close()

    def _post_sync(
        self,
        nodes: list[dict[str, Any]],
        edges: list[dict[str, Any]],
        *,
        prune: bool = False,
    ) -> dict[str, Any]:
        """Send a single sync request and return the parsed response."""
        payload: dict[str, Any] = {
            "project_id": self.project_id,
            "nodes": nodes,
            "edges": edges,
            "prune": prune,
        }
        response = self._client.post(url="/api/v1/graph/sync", json=payload)
        response.raise_for_status()
        return response.json()  # type: ignore[no-any-return]

    def set_embeddings(self, embeddings: dict[str, list[float]]) -> None:
        """Attach pre-computed embeddings to include in next sync."""
        self._embeddings = embeddings

    def persist(self, graph: Graph, *, prune: bool = False) -> None:
        """Send graph to server via chunked POST /api/v1/graph/sync.

        Splits nodes into chunks of CHUNK_SIZE. Each chunk is sent with
        prune=False (upsert-only). Edges are sent with the last chunk.
        If embeddings were set via set_embeddings(), they are included
        in the node payload for nodes that have a matching embedding.

        When prune=True, a final request is sent after all chunks with
        prune=True and all node_ids so the server can delete orphan nodes
        via prune_orphan_nodes(). This request re-sends all nodes because
        the server's NodeInput schema requires content with min_length=1;
        a dedicated /prune endpoint would require a server change (Opt B
        in design doc). The overhead (~1 extra request for full node set)
        is acceptable for a full rebuild sync.
        """
        skipped = 0
        nodes: list[dict[str, Any]] = []
        for node in graph.iter_concepts():
            if not node.content:
                skipped += 1
                continue
            node_dict: dict[str, Any] = {
                "node_id": node.id,
                "node_type": node.type,
                "scope": "project",
                "content": node.content,
                "source_file": node.source_file,
                "properties": node.metadata,
            }
            if node.id in self._embeddings:
                node_dict["embedding"] = self._embeddings[node.id]
            nodes.append(node_dict)
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

        if not nodes:
            logger.info("No nodes to sync — skipping remote push")
            return

        chunks = [nodes[i : i + CHUNK_SIZE] for i in range(0, len(nodes), CHUNK_SIZE)]
        total_upserted = 0
        total_edges = 0

        for i, chunk in enumerate(chunks):
            is_last = i == len(chunks) - 1
            chunk_edges = edges if is_last else []
            result = self._post_sync(chunk, chunk_edges, prune=False)
            total_upserted += result.get("nodes_upserted", 0)
            total_edges += result.get("edges_created", 0)
            logger.info(
                "Chunk %d/%d: %d nodes, %d edges",
                i + 1,
                len(chunks),
                len(chunk),
                len(chunk_edges),
            )

        logger.info(
            "Synced to remote server (%d nodes in %d chunks, %d edges)",
            total_upserted,
            len(chunks),
            total_edges,
        )

        if prune:
            # Final request with ALL nodes so keep_node_ids is complete for
            # prune_orphan_nodes. Must include edges — replace_edges() runs
            # unconditionally in sync_graph() and would delete all edges if
            # we sent [].
            self._post_sync(nodes, edges, prune=True)
            logger.info("Prune request sent (%d keep_node_ids)", len(nodes))

    def query(
        self,
        keyword: str,
        limit: int = 20,
        exclude_repo_id: str | None = None,
    ) -> list[dict[str, Any]]:
        """Query the server's knowledge graph for cross-repo retrieval.

        Returns empty list on any HTTP error (graceful degradation).
        """
        params: dict[str, Any] = {"q": keyword, "limit": limit}
        if exclude_repo_id is not None:
            params["exclude_repo_id"] = exclude_repo_id
        try:
            response = self._client.get(url="/api/v1/graph/query", params=params)
            response.raise_for_status()
        except httpx.HTTPError as e:
            logger.warning("Cross-repo query failed: %s", e)
            return []
        data = response.json()
        return data.get("results", [])

    def pull(self) -> dict[str, Any]:
        """Download graph from server via GET /api/v1/graph/export.

        Returns the raw export payload (nodes, edges, totals).
        """
        response = self._client.get(
            url="/api/v1/graph/export",
            params={"project_id": self.project_id},
        )
        response.raise_for_status()
        return response.json()  # type: ignore[no-any-return]

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
