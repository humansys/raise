"""Atomic SQLite-backed sequential counters.

A counter is a named integer that increments monotonically. Each counter
seeds itself once on first use via a caller-provided ``seed_fn``; from then
on, increments are pure ``UPDATE ... RETURNING`` and are safe under any
number of concurrent writers.

Used by:
- ``adapters/filesystem.py`` for epic and story key generation
- ``session/index.py`` for per-developer session numbering
- ``artifacts/store.py`` for artifact ID allocation
"""

from __future__ import annotations

import sqlite3
from collections.abc import Callable


def next_counter(
    db: sqlite3.Connection,
    name: str,
    seed_fn: Callable[[], int],
    project_id: str = "",
) -> int:
    """Atomically allocate the next value of a named counter.

    On first use for a given ``name``, ``seed_fn()`` is invoked and the
    counter is seeded at that value via ``INSERT OR IGNORE``. Subsequent
    calls skip ``seed_fn`` entirely (the row already exists).

    The increment is a single ``UPDATE ... RETURNING`` statement, atomic
    under SQLite's per-connection write serialization. With WAL mode and
    ``busy_timeout``, multiple connections increment safely without lost
    updates or duplicate values.

    Args:
        db: SQLite connection. Caller owns lifecycle.
        name: Counter identifier (e.g., ``"epic"``, ``"story_15"``, ``"session"``).
        seed_fn: Zero-arg callable returning the seed value. Called only on
            first use for this counter; ignored thereafter.
        project_id: Project discriminator for the global DB.

    Returns:
        The new counter value (always ``previous + 1``, or ``seed + 1`` on
        first use).
    """
    existing = db.execute(
        "SELECT 1 FROM counters WHERE project_id = ? AND name = ?",
        (project_id, name),
    ).fetchone()
    if existing is None:
        db.execute(
            "INSERT OR IGNORE INTO counters (project_id, name, value) VALUES (?, ?, ?)",
            (project_id, name, seed_fn()),
        )
    row = db.execute(
        "UPDATE counters SET value = value + 1 WHERE project_id = ? AND name = ? RETURNING value",
        (project_id, name),
    ).fetchone()
    db.commit()
    return int(row[0])
