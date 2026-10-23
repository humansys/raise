"""HTTP client for pushing learning records to raise-server.

Posts learning records as agent events (event_type: "learning_record")
to POST /api/v1/agent/events. Zero server changes — reuses existing
append-only telemetry endpoint.
"""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime
from pathlib import Path

import httpx

from raise_cli.memory.learning import LearningRecord

logger = logging.getLogger(__name__)

_EVENTS_ENDPOINT = "/api/v1/agent/events"
_EVENT_TYPE = "learning_record"
_MARKER_FILENAME = ".pushed"


class LearningPushClient:
    """Push learning records to raise-server via agent events endpoint.

    Args:
        server_url: Base URL of the raise-server (e.g. "http://localhost:8000").
        api_key: API key for authentication (rsk_ prefix).
    """

    def __init__(
        self,
        server_url: str,
        api_key: str,
        *,
        _client: httpx.Client | None = None,
    ) -> None:
        self.server_url = server_url
        self._client = _client or httpx.Client(
            base_url=server_url,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=httpx.Timeout(connect=5.0, read=30.0, write=30.0, pool=5.0),
        )

    def push(self, record: LearningRecord) -> uuid.UUID:
        """Push a learning record to the server.

        Args:
            record: Validated learning record to push.

        Returns:
            Server-assigned UUID for the stored event.

        Raises:
            httpx.HTTPStatusError: On 4xx/5xx responses.
            httpx.ConnectError: When server is unreachable.
        """
        payload = {
            "event_type": _EVENT_TYPE,
            "payload": record.model_dump(mode="json"),
        }
        response = self._client.post(url=_EVENTS_ENDPOINT, json=payload)
        response.raise_for_status()
        return uuid.UUID(response.json()["id"])

    def close(self) -> None:
        """Close the underlying HTTP connection pool."""
        self._client.close()


def write_push_marker(record_dir: Path, server_id: uuid.UUID) -> Path:
    """Write a .pushed marker file after successful push.

    Args:
        record_dir: Directory containing record.yaml.
        server_id: UUID returned by the server.

    Returns:
        Path to the marker file.
    """
    marker = record_dir / _MARKER_FILENAME
    marker.write_text(
        f"{server_id}\n{datetime.now(UTC).isoformat()}\n",
        encoding="utf-8",
    )
    return marker


def is_pushed(record_dir: Path) -> bool:
    """Check if a record has already been pushed.

    Args:
        record_dir: Directory containing record.yaml.

    Returns:
        True if .pushed marker exists.
    """
    return (record_dir / _MARKER_FILENAME).exists()
