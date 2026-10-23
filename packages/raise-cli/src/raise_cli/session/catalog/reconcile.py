"""Reconciliation — reap stale provisioning rows in runtime_sessions.

On-demand reconciler triggered by list/resume reads. Provisioning rows
older than PROVISIONING_TIMEOUT_S are considered abandoned and moved to
'exited'. Live rows are never reaped by time alone — liveness check (T3)
handles those in S2.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass

PROVISIONING_TIMEOUT_S: int = 60


@dataclass(frozen=True)
class ReconcileResult:
    """Summary of one reconciliation pass."""

    reaped: int


def reconcile(conn: sqlite3.Connection) -> ReconcileResult:
    """Reap provisioning rows older than PROVISIONING_TIMEOUT_S seconds.

    Returns a ReconcileResult with the number of rows moved to 'exited'.
    """
    cursor = conn.execute(
        """
        UPDATE runtime_sessions
           SET state = 'exited',
               updated_at = datetime('now')
         WHERE state = 'provisioning'
           AND created_at <= datetime('now', ? || ' seconds')
        """,
        (f"-{PROVISIONING_TIMEOUT_S}",),
    )
    conn.commit()
    return ReconcileResult(reaped=cursor.rowcount)
