"""API-based pipeline run store — thin async HTTP client for raise-server.

Implements PipelineRunStore Protocol via REST calls to
/api/v1/pipeline/runs. Requires RAISE_SERVER_URL and RAISE_API_KEY.

Uses ``httpx.AsyncClient`` so that network I/O never blocks the MCP server's
event loop (RAISE-8386): a slow or unreachable raise-server must not freeze
every other MCP tool while a request is in flight.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import httpx

__all__ = ["ApiRunStore"]

_logger = logging.getLogger(__name__)

# Short timeouts: a hung server should surface fast, not after 30s (RAISE-8386).
_TIMEOUT = httpx.Timeout(connect=2.0, read=5.0, write=5.0, pool=2.0)
# Idempotent GETs get one retry with linear backoff before failing loud.
_GET_RETRIES = 1
# Writes (POST/DELETE) are idempotent (upsert / no-op on unknown) — safe to retry.
_WRITE_RETRIES = 2
_BACKOFF_SECONDS = 0.5


class ApiRunStore:
    """Async HTTP client for pipeline run persistence on raise-server.

    Args:
        server_url: Base URL of raise-server (e.g. "https://raise-server.fly.dev").
        api_key: API key for authentication (rsk_ prefix).
        transport: Optional transport override (for tests / custom routing).
    """

    def __init__(
        self,
        server_url: str,
        api_key: str,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._server_url = server_url
        kwargs: dict[str, Any] = {
            "base_url": server_url,
            "headers": {"Authorization": f"Bearer {api_key}"},
            "timeout": _TIMEOUT,
        }
        if transport is not None:
            kwargs["transport"] = transport
        self._client = httpx.AsyncClient(**kwargs)

    async def aclose(self) -> None:
        """Close the underlying HTTP connection pool."""
        await self._client.aclose()

    def _unreachable(
        self, exc: httpx.TransportError, *, verb: str = "request"
    ) -> RuntimeError:
        """Build an actionable error for a connection/timeout failure."""
        return RuntimeError(
            f"raise-server unreachable ({verb}) at {self._server_url}: {exc}. "
            "Run is preserved locally — retry later or check the server "
            "(e.g. `fly status`, RAISE_SERVER_URL)."
        )

    async def _get_with_retry(self, url: str) -> httpx.Response:
        """GET an idempotent endpoint with one backoff retry on transport errors."""
        attempt = 0
        while True:
            try:
                return await self._client.get(url)
            except httpx.TransportError as exc:
                if attempt >= _GET_RETRIES:
                    _logger.warning("GET %s failed after retry: %s", url, exc)
                    raise self._unreachable(exc) from exc
                attempt += 1
                await asyncio.sleep(_BACKOFF_SECONDS * attempt)

    async def save(self, run: dict[str, Any]) -> None:
        """Upsert a run via POST /api/v1/pipeline/runs (with retry)."""
        payload = self._sanitize_payload(run)
        attempt = 0
        while True:
            try:
                resp = await self._client.post("/api/v1/pipeline/runs", json=payload)
                resp.raise_for_status()
                return
            except httpx.HTTPStatusError as exc:
                raise RuntimeError(
                    f"raise-server rejected save ({exc.response.status_code}): "
                    f"{exc}. Run is preserved locally."
                ) from exc
            except httpx.TransportError as exc:
                if attempt >= _WRITE_RETRIES:
                    _logger.warning(
                        "POST /runs failed after %d retries: %s", _WRITE_RETRIES, exc
                    )
                    raise self._unreachable(exc, verb="POST save") from exc
                attempt += 1
                await asyncio.sleep(_BACKOFF_SECONDS * attempt)

    @staticmethod
    def _sanitize_payload(run: dict[str, Any]) -> dict[str, Any]:
        """Strip project_id when it's not a valid UUID (RAISE-17049)."""
        import uuid

        payload = dict(run)
        pid = payload.get("project_id")
        if pid is not None:
            try:
                uuid.UUID(pid)
            except ValueError:
                payload["project_id"] = None
        return payload

    async def load(self, run_id: str) -> dict[str, Any] | None:
        """Load a run by ID. Returns None if not found (404)."""
        resp = await self._get_with_retry(f"/api/v1/pipeline/runs/{run_id}")
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return resp.json()

    async def list_runs(self) -> list[dict[str, Any]]:
        """List runs for the authenticated member (summary mode, last 50 — RAISE-8387)."""
        resp = await self._get_with_retry("/api/v1/pipeline/runs?summary=true&limit=50")
        resp.raise_for_status()
        return resp.json()["runs"]

    async def delete(self, run_id: str) -> None:
        """Delete a run by ID (with retry)."""
        attempt = 0
        while True:
            try:
                resp = await self._client.delete(f"/api/v1/pipeline/runs/{run_id}")
                resp.raise_for_status()
                return
            except httpx.TransportError as exc:
                if attempt >= _WRITE_RETRIES:
                    _logger.warning(
                        "DELETE /runs/%s failed after %d retries: %s",
                        run_id,
                        _WRITE_RETRIES,
                        exc,
                    )
                    raise self._unreachable(exc, verb="DELETE") from exc
                attempt += 1
                await asyncio.sleep(_BACKOFF_SECONDS * attempt)
