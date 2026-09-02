"""Reconciliation migration for project_id splinters in ~/.rai/raise.db.

Originally a one-shot fix for RAISE-13467's `raise` trickle rows: RAISE-13298
flipped `get_project_id()` to prefer `server_slug` over the local project
name, which silently re-keyed every subsequent local write in this checkout
from `raise-commons` to `raise` until RAISE-13467 reverted it (see
`raise_cli.storage.connection`).

Generalized for RAISE-13319 (Camp A/Camp B split project identity): the
worktree-redirect resolvers (`resolve_project_root()`/`resolve_repo_root()`)
sent some local-keying callers to the MAIN checkout's manifest while others
correctly resolved the CURRENT checkout's, splitting rows for the same
logical project across two `project_id`s.

Coverage is now GENERIC: ``migrate_project_slug()`` discovers EVERY
project_id-bearing table from the live schema (``PRAGMA table_info``) and
reconciles all of them — not a hardcoded subset. This closes the F2 gap
where graph_nodes/graph_edges (the ~10K RAISE-13467 rows), patterns,
pipeline_runs, etc. stayed orphaned. Three tables keep bespoke collision
policy because a blind newer-wins would corrupt them:

- ``counters``     — keep-MAX (high-water-mark; summing/overwriting breaks
                     the ``counter == max(session_number)`` invariant, RCA
                     RAISE-6255).
- ``active_sessions`` — dedup by ``cc_session_id`` (a NON-PK semantic key;
                     the generic PK-based path can't see that collision).
- ``governance_cache`` — PK is project_id alone and the cache is
                     refetchable, so the splinter row is simply dropped.

Every other table goes through the generic path: rows with no PK collision
are moved with a blind ``UPDATE``; on a PK collision the newer row (by the
table's recency column) wins WHOLESALE — all non-key columns are carried,
never a partial overwrite (F4). Tables whose PK does not include
``project_id`` can never collide (the PK is globally unique), so they take a
single bulk ``UPDATE``.

Idempotent — a second run finds zero rows under ``old_id`` and returns an
empty report without touching the DB. Reuses ``MaintenanceLockStore``
(ADR-104) to guard against a concurrent ``rai`` process and mirrors
``consolidate.py``'s WAL-checkpoint-then-copy backup.

``old_id`` and ``new_id`` are parameters (defaulting to the historical
RAISE-13467 pair). Passing ``old_id == new_id`` is rejected with a
``ValueError`` — without that guard every dedup path would treat a row's own
self as a colliding counterpart and DELETE it, emptying tables while
reporting success (F1 data-loss bug).

CRITICAL: this module must NOT be invoked against the real
``~/.rai/raise.db`` as part of implementing/testing a fix — that execution
is a separate, explicitly-confirmed step (dry-run by default at the CLI).
"""

from __future__ import annotations

import os
import shutil
import sqlite3
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

from raise_cli.storage.maintenance_lock import MaintenanceLockStore
from raise_cli.storage.schema import create_all

OLD_PROJECT_ID = "raise"
NEW_PROJECT_ID = "raise-commons"

_LOCK_NAME = "project_slug_migration"

# Recency columns, most-authoritative first, for generic newer-wins.
# `last_used_at` beats `created_at` for missions; `updated_at` for graph/docs.
_RECENCY_PRIORITY = (
    "updated_at",
    "last_used_at",
    "bound_at",
    "completed_at",
    "started_at",
    "started",
    "timestamp",
    "fetched_at",
    "created_at",
)


@dataclass
class TableCounts:
    """Per-table reconciliation counts."""

    migrated: int = 0  # rows moved with no PK collision
    merged: int = 0  # rows where a PK collision was resolved
    deleted: int = 0  # rows dropped without carry-over (e.g. governance_cache)

    @property
    def total(self) -> int:
        """Total rows touched in this table (migrated + merged + deleted)."""
        return self.migrated + self.merged + self.deleted


@dataclass
class ProjectSlugMigrationReport:
    """Result of reconciling `project_id=old_id` rows onto `new_id`."""

    dry_run: bool = False
    backup_path: Path | None = None
    tables: dict[str, TableCounts] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)

    @property
    def tables_covered(self) -> set[str]:
        """Every project_id table the migration processed this run."""
        return set(self.tables)

    @property
    def total_rows_affected(self) -> int:
        """Total rows migrated, merged, or deleted across every table."""
        return sum(t.total for t in self.tables.values())


# ---------------------------------------------------------------------------
# Schema introspection
# ---------------------------------------------------------------------------


def _project_id_tables(conn: sqlite3.Connection) -> list[str]:
    """Every table in the live DB that has a ``project_id`` column."""
    tables = [
        r[0]
        for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    ]
    result: list[str] = []
    for table in tables:
        cols = {c[1] for c in conn.execute(f"PRAGMA table_info({table})").fetchall()}
        if "project_id" in cols:
            result.append(table)
    return sorted(result)


def _pk_columns(conn: sqlite3.Connection, table: str) -> list[str]:
    """Primary-key columns of *table*, in key order."""
    rows = [
        c for c in conn.execute(f"PRAGMA table_info({table})").fetchall() if c[5] > 0
    ]
    return [c[1] for c in sorted(rows, key=lambda c: c[5])]


def _all_columns(conn: sqlite3.Connection, table: str) -> list[str]:
    return [c[1] for c in conn.execute(f"PRAGMA table_info({table})").fetchall()]


def _pick_recency(columns: list[str]) -> str | None:
    for candidate in _RECENCY_PRIORITY:
        if candidate in columns:
            return candidate
    return None


# ---------------------------------------------------------------------------
# Explicit (bespoke) handlers
# ---------------------------------------------------------------------------


def _migrate_active_sessions(
    conn: sqlite3.Connection, *, old_id: str, new_id: str
) -> TableCounts:
    """Keep-latest-by-`started` per `cc_session_id` (a NON-PK semantic key)."""
    counts = TableCounts()
    old_rows = conn.execute(
        "SELECT session_id, started, cc_session_id FROM active_sessions "
        "WHERE project_id = ?",
        (old_id,),
    ).fetchall()
    for row in old_rows:
        counterpart = conn.execute(
            "SELECT session_id, started FROM active_sessions "
            "WHERE project_id = ? AND cc_session_id = ?",
            (new_id, row["cc_session_id"]),
        ).fetchone()
        if counterpart is None:
            conn.execute(
                "UPDATE active_sessions SET project_id = ? WHERE session_id = ?",
                (new_id, row["session_id"]),
            )
            counts.migrated += 1
            continue

        counts.merged += 1
        if row["started"] > counterpart["started"]:
            conn.execute(
                "DELETE FROM active_sessions WHERE session_id = ?",
                (counterpart["session_id"],),
            )
            conn.execute(
                "UPDATE active_sessions SET project_id = ? WHERE session_id = ?",
                (new_id, row["session_id"]),
            )
        else:
            conn.execute(
                "DELETE FROM active_sessions WHERE session_id = ?",
                (row["session_id"],),
            )
    return counts


def _migrate_counters(
    conn: sqlite3.Connection, *, old_id: str, new_id: str
) -> TableCounts:
    """PK (project_id, name) — keep-MAX on collision, plain UPDATE otherwise.

    Counters are high-water-marks: the survivor keeps the HIGHEST value,
    never a newer-wins overwrite (which would lose a higher old value and
    break the ``counter == max(...)`` invariant, RCA RAISE-6255).
    """
    counts = TableCounts()
    old_rows = conn.execute(
        "SELECT name, value FROM counters WHERE project_id = ?", (old_id,)
    ).fetchall()
    for row in old_rows:
        counterpart = conn.execute(
            "SELECT value FROM counters WHERE project_id = ? AND name = ?",
            (new_id, row["name"]),
        ).fetchone()
        if counterpart is None:
            conn.execute(
                "UPDATE counters SET project_id = ? WHERE project_id = ? AND name = ?",
                (new_id, old_id, row["name"]),
            )
            counts.migrated += 1
            continue

        counts.merged += 1
        conn.execute(
            "UPDATE counters SET value = ? WHERE project_id = ? AND name = ?",
            (max(counterpart["value"], row["value"]), new_id, row["name"]),
        )
        conn.execute(
            "DELETE FROM counters WHERE project_id = ? AND name = ?",
            (old_id, row["name"]),
        )
    return counts


def _migrate_governance_cache(
    conn: sqlite3.Connection, *, old_id: str, new_id: str
) -> TableCounts:
    """PK project_id alone — always DELETE the splinter row (refetchable cache)."""
    del new_id  # cache is discarded, never merged
    cur = conn.execute("DELETE FROM governance_cache WHERE project_id = ?", (old_id,))
    return TableCounts(deleted=max(cur.rowcount, 0))


# ---------------------------------------------------------------------------
# Generic handler (all other project_id tables)
# ---------------------------------------------------------------------------


def _migrate_generic(
    conn: sqlite3.Connection, table: str, *, old_id: str, new_id: str
) -> TableCounts:
    """Reconcile *table* by PK identity, newer-wins-wholesale on collision.

    - project_id NOT in the PK -> the PK is globally unique, so no collision
      is possible; a single bulk UPDATE moves every splinter row.
    - project_id IN the PK -> per-row: no counterpart => UPDATE (migrate);
      counterpart => newer row (by recency column) wins WHOLESALE (all
      non-key columns carried), then the splinter row is deleted.
    """
    counts = TableCounts()
    pk_cols = _pk_columns(conn, table)
    all_cols = _all_columns(conn, table)

    # No project_id in PK => PK globally unique => collisions impossible.
    if "project_id" not in pk_cols:
        cur = conn.execute(
            f"UPDATE {table} SET project_id = ? WHERE project_id = ?",  # noqa: S608  # nosec B608
            (new_id, old_id),
        )
        counts.migrated = max(cur.rowcount, 0)
        return counts

    key_cols = [c for c in pk_cols if c != "project_id"]
    data_cols = [c for c in all_cols if c != "project_id" and c not in key_cols]
    recency = _pick_recency(all_cols)

    # PK exactly (project_id): every splinter row "collides" with the single
    # new-id row (empty key match) — keep new, drop splinter.
    key_match = " AND ".join(f"{c} = ?" for c in key_cols) if key_cols else "1=1"

    old_rows = conn.execute(
        f"SELECT * FROM {table} WHERE project_id = ?",  # noqa: S608  # nosec B608
        (old_id,),
    ).fetchall()
    for row in old_rows:
        key_vals = [row[c] for c in key_cols]
        counterpart = conn.execute(
            f"SELECT * FROM {table} WHERE project_id = ? AND {key_match}",  # noqa: S608  # nosec B608
            (new_id, *key_vals),
        ).fetchone()

        if counterpart is None:
            conn.execute(
                f"UPDATE {table} SET project_id = ? "  # noqa: S608  # nosec B608
                f"WHERE project_id = ? AND {key_match}",
                (new_id, old_id, *key_vals),
            )
            counts.migrated += 1
            continue

        counts.merged += 1
        old_wins = (
            recency is not None
            and row[recency] is not None
            and (counterpart[recency] is None or row[recency] > counterpart[recency])
        )
        if old_wins and data_cols:
            set_clause = ", ".join(f"{c} = ?" for c in data_cols)
            conn.execute(
                f"UPDATE {table} SET {set_clause} "  # noqa: S608  # nosec B608
                f"WHERE project_id = ? AND {key_match}",
                (*[row[c] for c in data_cols], new_id, *key_vals),
            )
        conn.execute(
            f"DELETE FROM {table} WHERE project_id = ? AND {key_match}",  # noqa: S608  # nosec B608
            (old_id, *key_vals),
        )
    return counts


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------


def _count_pending(conn: sqlite3.Connection, *, old_id: str) -> int:
    """Read-only count of rows still under old_id across ALL project_id tables."""
    total = 0
    for table in _project_id_tables(conn):
        row = conn.execute(
            f"SELECT COUNT(*) AS n FROM {table} WHERE project_id = ?",  # noqa: S608  # nosec B608
            (old_id,),
        ).fetchone()
        total += row["n"]
    return total


# Tables needing bespoke collision policy — every OTHER project_id table is
# handled generically (discovered from the live schema, never hardcoded).
_EXPLICIT_HANDLERS = {
    "active_sessions": _migrate_active_sessions,
    "counters": _migrate_counters,
    "governance_cache": _migrate_governance_cache,
}


def _run_all_migrations(
    conn: sqlite3.Connection,
    report: ProjectSlugMigrationReport,
    *,
    old_id: str,
    new_id: str,
) -> None:
    for table in _project_id_tables(conn):
        handler = _EXPLICIT_HANDLERS.get(table)
        if handler is not None:
            counts = handler(conn, old_id=old_id, new_id=new_id)
        else:
            counts = _migrate_generic(conn, table, old_id=old_id, new_id=new_id)
        report.tables[table] = counts


def _backup_before_migration(conn: sqlite3.Connection, db_path: Path) -> Path:
    """Snapshot the DB before the first write (WAL checkpoint then copy2)."""
    conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    stamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
    backup = db_path.with_name(f"{db_path.name}.pre-slug-migration-{stamp}.bak")
    shutil.copy2(db_path, backup)
    return backup


def migrate_project_slug(
    db_path: Path,
    *,
    dry_run: bool = False,
    old_id: str = OLD_PROJECT_ID,
    new_id: str = NEW_PROJECT_ID,
) -> ProjectSlugMigrationReport:
    """Reconcile `project_id=old_id` rows onto `new_id` across ALL tables.

    Args:
        db_path: Path to the raise.db to migrate (the real ``~/.rai/raise.db``
            in production, a fixture DB in tests).
        dry_run: Report what would be migrated without writing or locking.
        old_id: Splinter project_id to reconcile away.
        new_id: Canonical project_id to reconcile onto.

    Returns:
        ProjectSlugMigrationReport with per-table counts and the
        ``tables_covered`` set. When nothing is pending, returns an empty
        report (no lock, no backup) — this is what makes re-running
        idempotent.

    Raises:
        ValueError: If ``old_id == new_id`` — reconciling a project onto
            itself would delete every row as a self-collision (F1).
    """
    if old_id == new_id:
        msg = (
            f"old_id and new_id must differ (both are {old_id!r}); "
            "reconciling a project_id onto itself would destroy its own rows."
        )
        raise ValueError(msg)

    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=OFF")
    try:
        create_all(conn)
        conn.commit()

        if _count_pending(conn, old_id=old_id) == 0:
            report = ProjectSlugMigrationReport(dry_run=dry_run)
            # Record covered tables even on a no-op, so callers can audit
            # coverage without inspecting the schema themselves.
            for table in _project_id_tables(conn):
                report.tables[table] = TableCounts()
            return report

        if dry_run:
            report = ProjectSlugMigrationReport(dry_run=True)
            conn.execute("BEGIN")
            try:
                _run_all_migrations(conn, report, old_id=old_id, new_id=new_id)
            finally:
                conn.rollback()
            return report

        lock_store = MaintenanceLockStore(conn)
        lock_store.acquire(_LOCK_NAME, pid=os.getpid(), ttl_seconds=300)
        try:
            report = ProjectSlugMigrationReport()
            report.backup_path = _backup_before_migration(conn, db_path)
            conn.execute("BEGIN")
            try:
                _run_all_migrations(conn, report, old_id=old_id, new_id=new_id)
                conn.commit()
            except Exception:
                conn.rollback()
                raise
            return report
        finally:
            lock_store.release(_LOCK_NAME, pid=os.getpid())
    finally:
        conn.close()
