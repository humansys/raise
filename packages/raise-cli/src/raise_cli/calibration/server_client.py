"""HTTP client for the calibration server API (S-KS.3).

Wraps /api/v1/calibration endpoints. Pattern follows CartridgeServerClient.
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)

__all__ = ["CalibrationServerClient", "CalibrationServerError"]


class CalibrationServerError(Exception):
    """Error communicating with the calibration server API."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code


class CalibrationServerClient:
    """Sync HTTP client for calibration sync API.

    Args:
        server_url: Base URL of raise-server (e.g. "http://localhost:8000").
        api_key: API key for authentication (rsk_ prefix).
    """

    def __init__(self, server_url: str, api_key: str) -> None:
        self._client = httpx.Client(
            base_url=server_url,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=httpx.Timeout(connect=5.0, read=30.0, write=30.0, pool=5.0),
        )

    def close(self) -> None:
        """Close the underlying HTTP connection pool."""
        self._client.close()

    def pull(self, project_id: str) -> list[dict[str, Any]]:
        """Download calibration entries from the server for the project.

        Normalizes server ``entry_id`` → local ``id`` so merge.py sees a
        uniform key on both local and server entries (AR C1).
        """
        data = self._get(f"/api/v1/calibration?project_id={project_id}")
        entries: list[dict[str, Any]] = []
        for raw in data.get("entries", []):
            e = dict(raw)
            if "entry_id" in e and "id" not in e:
                e["id"] = e.pop("entry_id")
            entries.append(e)
        return entries

    def push_bulk(self, project_id: str, entries: list[dict[str, Any]]) -> int:
        """Send local-only entries to the server. Returns count upserted.

        Remaps local ``id`` → server ``entry_id`` (AR C1).
        """
        remapped: list[dict[str, Any]] = []
        for raw in entries:
            e = dict(raw)
            if "id" in e and "entry_id" not in e:
                e["entry_id"] = e.pop("id")
            remapped.append(e)
        result = self._post(
            "/api/v1/calibration/bulk",
            json={"project_id": project_id, "entries": remapped},
        )
        return int(result.get("upserted", 0))

    def _get(self, url: str) -> Any:
        try:
            response = self._client.get(url=url)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise self._wrap_status_error(e) from e
        except httpx.HTTPError as e:
            raise CalibrationServerError(f"Server unreachable or timeout: {e}") from e
        return response.json()

    def _post(self, url: str, json: Any) -> Any:
        try:
            response = self._client.post(url=url, json=json)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise self._wrap_status_error(e) from e
        except httpx.HTTPError as e:
            raise CalibrationServerError(f"Server unreachable or timeout: {e}") from e
        return response.json()

    def _wrap_status_error(
        self, error: httpx.HTTPStatusError
    ) -> CalibrationServerError:
        status = error.response.status_code
        if status == 401:
            return CalibrationServerError(
                "Authentication failed — check RAISE_API_KEY",
                status_code=401,
            )
        if status == 403:
            return CalibrationServerError(
                "Plan upgrade required for this operation",
                status_code=403,
            )
        return CalibrationServerError(
            f"Server error {status}: {error}",
            status_code=status,
        )
