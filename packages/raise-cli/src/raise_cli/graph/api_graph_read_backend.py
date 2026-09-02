"""API-based graph read backend — thin HTTP client for raise-server.

Implements GraphReadBackend Protocol via REST calls to
/api/v1/graph/. Requires RAISE_SERVER_URL and RAISE_API_KEY.

Distinct from ApiGraphBackend (graph/backends/api.py) which implements
the write-side KnowledgeGraphBackend Protocol (persist/load/health).
"""

from __future__ import annotations

from typing import Any

import httpx

from raise_core.graph.filters import GraphFilter

__all__ = ["ApiGraphReadBackend"]


class ApiGraphReadBackend:
    """HTTP client for graph read operations on raise-server."""

    def __init__(self, server_url: str, api_key: str) -> None:
        self._client = httpx.Client(
            base_url=server_url,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=httpx.Timeout(connect=5.0, read=30.0, write=30.0, pool=5.0),
        )

    def close(self) -> None:
        """Close the underlying HTTP connection pool."""
        self._client.close()

    async def query(
        self,
        query: str,
        limit: int,
        filters: GraphFilter | None = None,
    ) -> dict[str, Any]:
        """Search graph by keyword via GET /api/v1/graph/query."""
        if filters is not None:
            return {
                "status": "error",
                "reason": "filters not supported on this backend",
            }
        resp = self._client.get(
            "/api/v1/graph/query",
            params={"q": query, "limit": limit},
        )
        resp.raise_for_status()
        return resp.json()

    async def context(self, module_id: str) -> dict[str, Any]:
        """Get module context via GET /api/v1/graph/context/{module_id}."""
        resp = self._client.get(f"/api/v1/graph/context/{module_id}")
        resp.raise_for_status()
        return resp.json()

    def semantic_search(self, query: str, limit: int = 10) -> dict[str, Any]:
        """Search via POST /api/v2/graph/semantic-search (pgvector).

        Args:
            query: Search string to embed and query against pgvector.
            limit: Maximum number of results to return (default 10).

        Returns:
            Raw server response dict with "results", "total", "query" keys.

        Raises:
            httpx.HTTPStatusError: On 4xx/5xx responses.
            httpx.RequestError: On network errors (timeout, DNS, refused).
        """
        resp = self._client.post(
            "/api/v2/graph/semantic-search",
            json={"query": query, "limit": limit},
        )
        resp.raise_for_status()
        return resp.json()  # type: ignore[no-any-return]
