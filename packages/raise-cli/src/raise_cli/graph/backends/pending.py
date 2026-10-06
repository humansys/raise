"""Pending sync marker — tracks failed remote writes for retry.

When DualWriteBackend fails to sync remotely, a marker row is written to
the pending_sync table in raise.db. On next successful sync, the row is cleared.
"""

from __future__ import annotations

import logging
import sqlite3
from datetime import datetime
from pathlib import Path

from pydantic import BaseModel

from raise_cli.storage.schema import create_all as _create_all

logger = logging.getLogger(__name__)

__all__ = [
    "PendingSyncMarker",
    "write_pending_marker",
    "read_pending_marker",
    "clear_pending_marker",
]


class PendingSyncMarker(BaseModel):
    """Marker for a failed remote graph sync."""

    timestamp: datetime
    graph_path: str
    node_count: int
    edge_count: int
    error: str


def write_pending_marker(db_path: Path, marker: PendingSyncMarker) -> None:
    """Insert or replace pending_sync row in raise.db.

    Args:
        db_path: Path to raise.db SQLite file.
        marker: The marker data to persist.
    """
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    _create_all(conn)
    try:
        conn.execute(
            "INSERT OR REPLACE INTO pending_sync"
            " (id, timestamp, graph_path, node_count, edge_count, error)"
            " VALUES (1, ?, ?, ?, ?, ?)",
            (
                marker.timestamp.isoformat(),
                marker.graph_path,
                marker.node_count,
                marker.edge_count,
                marker.error,
            ),
        )
        conn.commit()
    finally:
        conn.close()
    logger.warning("Remote sync failed, marked as pending in raise.db")


def read_pending_marker(db_path: Path) -> PendingSyncMarker | None:
    """Read pending_sync row from raise.db.

    Args:
        db_path: Path to raise.db SQLite file.

    Returns:
        PendingSyncMarker if a row exists, None otherwise.
    """
    if not db_path.exists():
        return None
    conn = sqlite3.connect(str(db_path))
    _create_all(conn)
    try:
        row = conn.execute(
            "SELECT timestamp, graph_path, node_count, edge_count, error"
            " FROM pending_sync WHERE id = 1"
        ).fetchone()
    finally:
        conn.close()
    if row is None:
        return None
    try:
        return PendingSyncMarker(
            timestamp=row[0],
            graph_path=row[1],
            node_count=row[2],
            edge_count=row[3],
            error=row[4],
        )
    except Exception:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
        logger.warning("Corrupt pending_sync row in raise.db, ignoring")
        return None


def clear_pending_marker(db_path: Path) -> bool:
    """Delete pending_sync row from raise.db.

    Args:
        db_path: Path to raise.db SQLite file.

    Returns:
        True if a row was deleted, False if no row existed.
    """
    if not db_path.exists():
        return False
    conn = sqlite3.connect(str(db_path))
    _create_all(conn)
    try:
        cursor = conn.execute("DELETE FROM pending_sync WHERE id = 1")
        conn.commit()
        deleted = cursor.rowcount > 0
    finally:
        conn.close()
    if deleted:
        logger.info("Cleared pending sync marker — remote sync successful")
    return deleted
