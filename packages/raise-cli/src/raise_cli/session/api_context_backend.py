"""API-based session context backend — thin HTTP client for raise-server.

Implements SessionContextBackend Protocol via REST calls to
/api/v1/sessions/context. Requires RAISE_SERVER_URL and RAISE_API_KEY.
"""

from __future__ import annotations

from typing import Any

import httpx

__all__ = ["ApiSessionContextBackend"]


class ApiSessionContextBackend:
    """HTTP client for session context bundle on raise-server."""

    def __init__(self, server_url: str, api_key: str) -> None:
        self._client = httpx.Client(
            base_url=server_url,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=httpx.Timeout(connect=5.0, read=30.0, write=30.0, pool=5.0),
        )

    def close(self) -> None:
        """Close the underlying HTTP connection pool."""
        self._client.close()

    async def bundle(
        self, sections: list[str], session_id: str | None = None
    ) -> dict[str, Any]:
        """Assemble context bundle via POST /api/v1/sessions/context.

        Args:
            sections: Section names to load.
            session_id: Accepted for SessionContextBackend Protocol
                conformance; not yet threaded server-side (deferred to
                O2-platform parity, design §8 risk 1 — RAISE-13146).
        """
        resp = self._client.post(
            "/api/v1/sessions/context",
            json={"sections": sections},
        )
        resp.raise_for_status()
        return resp.json()
