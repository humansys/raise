"""Pending sync marker — tracks failed remote writes for retry.

When DualWriteBackend fails to sync remotely, a marker file is created
in .raise/pending_sync.json. On next successful sync, the marker is cleared.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path

from pydantic import BaseModel

logger = logging.getLogger(__name__)

__all__ = [
    "PendingSyncMarker",
    "write_pending_marker",
    "read_pending_marker",
    "clear_pending_marker",
]

MARKER_FILENAME = "pending_sync.json"


class PendingSyncMarker(BaseModel):
    """Marker for a failed remote graph sync."""

    timestamp: datetime
    graph_path: str
    node_count: int
    edge_count: int
    error: str


def write_pending_marker(raise_dir: Path, marker: PendingSyncMarker) -> None:
    """Write pending_sync.json to .raise/ directory.

    Args:
        raise_dir: Path to .raise/ directory.
        marker: The marker data to write.
    """
    path = raise_dir / MARKER_FILENAME
    path.write_text(marker.model_dump_json(indent=2))
    logger.warning("Remote sync failed, marked as pending: %s", path)


def read_pending_marker(raise_dir: Path) -> PendingSyncMarker | None:
    """Read pending_sync.json, return None if not present or corrupt.

    Args:
        raise_dir: Path to .raise/ directory.

    Returns:
        PendingSyncMarker if file exists and is valid, None otherwise.
    """
    path = raise_dir / MARKER_FILENAME
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text())
        return PendingSyncMarker.model_validate(data)
    except ValueError:
        logger.warning("Corrupt pending_sync marker at %s, ignoring", path)
        return None


def clear_pending_marker(raise_dir: Path) -> bool:
    """Delete pending_sync.json.

    Args:
        raise_dir: Path to .raise/ directory.

    Returns:
        True if file existed and was deleted, False otherwise.
    """
    path = raise_dir / MARKER_FILENAME
    if path.exists():
        path.unlink()
        logger.info("Cleared pending sync marker — remote sync successful")
        return True
    return False
