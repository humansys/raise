"""API-based patterns backend — thin HTTP client for raise-server.

Implements PatternsBackend Protocol via REST calls to
/api/v1/memory/patterns. Requires RAISE_SERVER_URL and RAISE_API_KEY.
"""

from __future__ import annotations

from typing import Any

import httpx

__all__ = ["ApiPatternsBackend"]


class ApiPatternsBackend:
    """HTTP client for pattern operations on raise-server."""

    def __init__(self, server_url: str, api_key: str) -> None:
        self._client = httpx.Client(
            base_url=server_url,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=httpx.Timeout(connect=5.0, read=30.0, write=30.0, pool=5.0),
        )

    def close(self) -> None:
        """Close the underlying HTTP connection pool."""
        self._client.close()

    async def query(self, keywords: list[str], limit: int) -> list[dict[str, Any]]:
        """Return patterns matching any keyword."""
        resp = self._client.post(
            "/api/v1/memory/patterns/query",
            json={"keywords": keywords, "limit": limit},
        )
        resp.raise_for_status()
        return resp.json()["patterns"]

    async def add(
        self,
        content: str,
        context_tags: list[str],
        pattern_type: str = "technical",
        from_story: str = "",
    ) -> dict[str, Any]:
        """Add a new pattern via POST /api/v1/memory/patterns."""
        resp = self._client.post(
            "/api/v1/memory/patterns",
            json={
                "content": content,
                "context": context_tags,
                "properties": {
                    "type": pattern_type,
                    "from_story": from_story,
                },
            },
        )
        resp.raise_for_status()
        data = resp.json()
        return {"pattern_id": str(data["id"])}

    async def reinforce(
        self,
        pattern_id: str,
        vote: int = 1,
        from_story: str = "",
    ) -> dict[str, Any]:
        """Reinforce a pattern with a vote signal."""
        resp = self._client.post(
            f"/api/v1/memory/patterns/{pattern_id}/reinforce",
            json={"vote": vote, "from_story": from_story},
        )
        try:
            resp.raise_for_status()
        except httpx.HTTPStatusError as exc:
            return {
                "error": f"server {exc.response.status_code}: {exc.response.text[:200]}"
            }
        return resp.json()
