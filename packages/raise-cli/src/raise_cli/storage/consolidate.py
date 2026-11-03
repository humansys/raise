"""Consolidate orphaned per-project SQLite DBs into the global ~/.rai/raise.db.

Scans three families of sources (legacy ~/.rai/projects/{hash} partitions,
project-local .raise DBs, and worktree copies), merges rows with
INSERT OR IGNORE over the column intersection, verifies per-table counts,
and renames each verified source to *.consolidated — never deletes.

Safe to run multiple times — skips already-consolidated DBs. Exposed via
``rai db consolidate [--dry-run]`` (S8204.1).
"""

from __future__ import annotations

import logging
import os
import sqlite3
from dataclasses import dataclass, field
from datetime import UTC
from pathlib import Path

from raise_cli.config.paths import get_global_rai_dir
from raise_cli.storage.maintenance_lock import MaintenanceLockStore
from raise_cli.storage.schema import create_all

logger = logging.getLogger(__name__)

_PROJECT_SCOPED_TABLES = [
    "sessions",
    "journal_entries",
    "signals",
    "active_sessions",
    "pipeline_runs",
    "patterns",
    "artifacts",
    "story_stats",
    "ledger_entries",
    "session_records",
    "session_patterns",
    "session_corrections",
    "graph_nodes",
    "graph_edges",
    "counters",
    "pending_sync",
]

_GLOBAL_TABLES = [
    "missions",
    # active_mission: removed in v55 (RAISE-14643/S4, ADR-130 D5)
    "agent_session_missions",
    "agent_session_workitems",  # v55 — RAISE-14643/S4 ADR-130 D3
    "work_items",
]

_PROJECT_LOCAL_REL_PATHS = (
    Path(".raise") / "rai" / "raise.db",
    Path(".raise") / "rai" / "personal" / "raise.db",
    Path(".raise") / "rai.db",
)


@dataclass(frozen=True)
class SourceDb:
    """A candidate per-project SQLite DB to consolidate into the global DB."""

    path: Path
    project_id: str
    kind: str  # "global-partition" | "project-local" | "worktree"


def _is_consolidatable(db_path: Path) -> bool:
    """True if the file is a real, unmigrated SQLite DB (not a marker/backup)."""
    if not db_path.is_file() or db_path.stat().st_size == 0:
        return False
    if ".backup-" in db_path.name:
        return False
    if db_path.with_suffix(".db.consolidated").exists():
        return False
    return not db_path.with_suffix(".db.migrated").exists()


def discover_sources(project_root: Path | None) -> list[SourceDb]:
    """Discover all per-project DBs eligible for consolidation.

    Three families:
    1. ``~/.rai/projects/{hash}/raise.db`` — legacy global partitions,
       ``project_id`` stays the hash (converted lazily by the hash→slug
       migration when each project is opened, RAISE-6143).
    2. ``{project_root}/.raise/...`` — project-local DBs, ``project_id``
       is the project slug.
    3. ``{project_root}/.worktree/*/.raise/...`` — worktree copies, same
       slug as the parent project.

    Skips 0-byte files, ``*.backup-*`` copies, WAL/SHM siblings, and DBs
    already marked ``*.consolidated`` / ``*.migrated``.
    """
    sources = _scan_global_partitions()

    if project_root is None:
        return sources

    from raise_cli.storage.connection import get_project_id

    slug = get_project_id(project_root)
    sources.extend(_scan_tree(project_root, slug, kind="project-local"))

    worktrees_dir = project_root / ".worktree"
    if worktrees_dir.exists():
        for wt_dir in sorted(worktrees_dir.iterdir()):
            if wt_dir.is_dir():
                sources.extend(_scan_tree(wt_dir, slug, kind="worktree"))

    return sources


def _scan_global_partitions() -> list[SourceDb]:
    """Family 1: legacy ``~/.rai/projects/{hash}/raise.db`` partitions."""
    projects_dir = get_global_rai_dir() / "projects"
    if not projects_dir.exists():
        return []
    return [
        SourceDb(
            path=project_dir / "raise.db",
            project_id=project_dir.name,
            kind="global-partition",
        )
        for project_dir in sorted(projects_dir.iterdir())
        if project_dir.is_dir() and _is_consolidatable(project_dir / "raise.db")
    ]


def _scan_tree(root: Path, project_id: str, *, kind: str) -> list[SourceDb]:
    """Families 2/3: known per-project DB locations under a checkout root."""
    return [
        SourceDb(path=root / rel, project_id=project_id, kind=kind)
        for rel in _PROJECT_LOCAL_REL_PATHS
        if _is_consolidatable(root / rel)
    ]


@dataclass
class ConsolidationResult:
    """Result of consolidating per-project DBs into the global DB."""

    sources_found: int = 0
    sources_migrated: int = 0
    rows_migrated: dict[str, int] = field(default_factory=dict)
    rows_inserted: dict[str, int] = field(default_factory=dict)
    tables_skipped: set[str] = field(default_factory=set)
    backup_path: Path | None = None
    errors: list[str] = field(default_factory=list)


class VerificationError(RuntimeError):
    """A consolidated source has rows missing from the global DB."""


def _backup_global(
    global_conn: sqlite3.Connection, global_db_path: Path
) -> Path | None:
    """Snapshot the global DB before the first write. Returns backup path."""
    if not global_db_path.exists():
        return None
    import shutil
    from datetime import datetime

    global_conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    stamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
    backup = global_db_path.with_name(f"raise.db.pre-consolidate-{stamp}.bak")
    shutil.copy2(global_db_path, backup)
    return backup


def consolidate_all(
    *,
    project_root: Path | None = None,
    dry_run: bool = False,
    sources: list[SourceDb] | None = None,
) -> ConsolidationResult:
    """Migrate all per-project DBs into the global DB with verified counts.

    Each source is merged in its own transaction: a verification failure
    rolls back that source and leaves it unmarked, so nothing is partially
    consolidated. Sources are renamed to ``*.consolidated`` only after the
    merge is committed and verified. Files are never deleted.

    Known limitation: if the marker rename itself fails after a committed
    merge, re-running duplicates rows in surrogate-PK tables (their ids are
    reassigned on insert). Natural-PK tables stay idempotent.

    Args:
        project_root: Scan project-local and worktree DBs under this root
            in addition to the ``~/.rai/projects`` partitions.
        dry_run: Report what would happen without writing.
        sources: Explicit source list (skips discovery).

    Returns:
        ConsolidationResult with per-table counts and any errors.
    """
    if sources is None:
        sources = discover_sources(project_root)
    result = ConsolidationResult(sources_found=len(sources))
    if not sources:
        return result

    rai_dir = get_global_rai_dir()
    global_db_path = rai_dir / "raise.db"
    global_db_path.parent.mkdir(parents=True, exist_ok=True)
    global_conn = sqlite3.connect(str(global_db_path), check_same_thread=False)
    global_conn.execute("PRAGMA journal_mode=WAL")
    global_conn.execute("PRAGMA busy_timeout=5000")
    global_conn.execute("PRAGMA foreign_keys=OFF")
    global_conn.row_factory = sqlite3.Row
    create_all(global_conn)
    global_conn.commit()

    lock_store: MaintenanceLockStore | None = None
    if not dry_run:
        lock_store = MaintenanceLockStore(global_conn)
        # Raises MaintenanceLockHeldError when another live PID holds the lock.
        # Expired lock with dead PID is taken over automatically (ADR-104 D4).
        lock_store.acquire("db_consolidation", pid=os.getpid(), ttl_seconds=300)

    try:
        if not dry_run:
            result.backup_path = _backup_global(global_conn, global_db_path)

        for source in sources:
            try:
                _migrate_one(global_conn, source, result, dry_run=dry_run)
                if not dry_run:
                    global_conn.commit()
                    source.path.rename(source.path.with_suffix(".db.consolidated"))
                result.sources_migrated += 1
                logger.info(
                    "Consolidated %s (project_id=%s)", source.path, source.project_id
                )
            except Exception as exc:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
                if not dry_run:
                    global_conn.rollback()
                result.errors.append(f"{source.path}: {exc}")
                logger.warning("Failed to consolidate %s: %s", source.path, exc)
    finally:
        if lock_store is not None:
            lock_store.release("db_consolidation", pid=os.getpid())
        global_conn.close()
    return result


def _dst_schema(
    global_conn: sqlite3.Connection, table: str
) -> tuple[list[str], list[str], bool]:
    """Return (column names, pk columns in order, is_surrogate_pk) for a table."""
    info = global_conn.execute(f"PRAGMA table_info({table})").fetchall()
    cols = [r[1] for r in info]
    pk_rows = sorted((r for r in info if r[5]), key=lambda r: r[5])
    pk_cols = [r[1] for r in pk_rows]
    surrogate = len(pk_cols) == 1 and (pk_rows[0][2] or "").upper() == "INTEGER"
    return cols, pk_cols, surrogate


def _copy_table(
    src_conn: sqlite3.Connection,
    global_conn: sqlite3.Connection,
    table: str,
    dst_cols: list[str],
    *,
    project_id: str | None,
    exclude_cols: set[str],
    dry_run: bool,
) -> tuple[int, int]:
    """Copy rows from a single table. Returns (src_rows, inserted)."""
    rows = src_conn.execute(f"SELECT * FROM {table}").fetchall()  # noqa: S608  # nosec B608
    if not rows:
        return 0, 0

    src_cols = [
        d[0]
        for d in src_conn.execute(f"SELECT * FROM {table} LIMIT 0").description  # noqa: S608  # nosec B608
    ]
    exclude = set(exclude_cols)
    if project_id is not None:
        exclude.add("project_id")
    common_cols = [c for c in src_cols if c in dst_cols and c not in exclude]
    if not common_cols:
        return 0, 0
    if dry_run:
        return len(rows), 0

    insert_cols = (["project_id"] if project_id is not None else []) + common_cols
    cols_str = ", ".join(insert_cols)
    placeholders = ", ".join(["?"] * len(insert_cols))
    prefix: list[str] = [project_id] if project_id is not None else []

    before = global_conn.total_changes
    for row in rows:
        values = prefix + [row[c] for c in common_cols]
        global_conn.execute(
            f"INSERT OR IGNORE INTO {table} ({cols_str}) VALUES ({placeholders})",  # noqa: S608
            values,
        )
    inserted = global_conn.total_changes - before
    return len(rows), inserted


def _count_missing_pks(
    src_conn: sqlite3.Connection,
    global_conn: sqlite3.Connection,
    table: str,
    pk_cols: list[str],
    *,
    project_id: str | None,
) -> int:
    """Count src rows whose natural PK is absent from the global DB."""
    src_cols = {
        r[1] for r in src_conn.execute(f"PRAGMA table_info({table})").fetchall()
    }
    # IS (not =) so NULL pk values — legal for TEXT PRIMARY KEY in SQLite —
    # match their inserted counterpart instead of counting as missing.
    where = " AND ".join(f"{c} IS ?" for c in pk_cols)
    missing = 0
    for row in src_conn.execute(f"SELECT * FROM {table}"):  # noqa: S608  # nosec B608
        values: list[object] = []
        resolvable = True
        for col in pk_cols:
            if col == "project_id" and project_id is not None:
                values.append(project_id)
            elif col in src_cols:
                values.append(row[col])
            else:
                resolvable = False
                break
        if not resolvable:
            continue
        found = global_conn.execute(
            f"SELECT 1 FROM {table} WHERE {where}",  # noqa: S608  # nosec B608
            values,
        ).fetchone()
        if found is None:
            missing += 1
    return missing


def _verify_table(
    src_conn: sqlite3.Connection,
    global_conn: sqlite3.Connection,
    table: str,
    pk_cols: list[str],
    *,
    surrogate: bool,
    project_id: str | None,
    src_rows: int,
    inserted: int,
) -> None:
    """Raise VerificationError if any src row is unaccounted for."""
    if surrogate or not pk_cols:
        # PK was excluded from the copy (or no PK) — every row must insert.
        if inserted != src_rows:
            raise VerificationError(
                f"table {table}: {src_rows - inserted} of {src_rows} rows "
                "were silently dropped on insert"
            )
        return
    missing = _count_missing_pks(
        src_conn, global_conn, table, pk_cols, project_id=project_id
    )
    if missing:
        raise VerificationError(
            f"table {table}: {missing} rows missing from global DB after merge"
        )


def _migrate_one(
    global_conn: sqlite3.Connection,
    source: SourceDb,
    result: ConsolidationResult,
    *,
    dry_run: bool,
) -> None:
    """Open the source DB read-only and copy + verify rows into the global DB."""
    src_conn = sqlite3.connect(
        f"file:{source.path}?mode=ro", uri=True, check_same_thread=False
    )
    src_conn.row_factory = sqlite3.Row

    try:
        src_tables = {
            r[0]
            for r in src_conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
        known = set(_PROJECT_SCOPED_TABLES) | set(_GLOBAL_TABLES)
        result.tables_skipped |= src_tables - known - {"sqlite_sequence"}

        for table in _PROJECT_SCOPED_TABLES + _GLOBAL_TABLES:
            if table not in src_tables:
                continue
            project_id = source.project_id if table in _PROJECT_SCOPED_TABLES else None
            dst_cols, pk_cols, surrogate = _dst_schema(global_conn, table)
            src_rows, inserted = _copy_table(
                src_conn,
                global_conn,
                table,
                dst_cols,
                project_id=project_id,
                exclude_cols=set(pk_cols) if surrogate else set(),
                dry_run=dry_run,
            )
            if not src_rows:
                continue
            result.rows_migrated[table] = result.rows_migrated.get(table, 0) + src_rows
            if dry_run:
                continue
            result.rows_inserted[table] = result.rows_inserted.get(table, 0) + inserted
            if table == "counters":
                _max_merge_counters(src_conn, global_conn, source.project_id)
            _verify_table(
                src_conn,
                global_conn,
                table,
                pk_cols,
                surrogate=surrogate,
                project_id=project_id,
                src_rows=src_rows,
                inserted=inserted,
            )

    finally:
        src_conn.close()


def _max_merge_counters(
    src_conn: sqlite3.Connection,
    global_conn: sqlite3.Connection,
    project_id: str,
) -> None:
    """Counters keep the highest value on conflict (precedent: migrate.py).

    INSERT OR IGNORE keeps the global value even when the orphan DB is
    ahead — a stale lower counter would hand out colliding sequential IDs
    via ``next_counter()``.
    """
    for row in src_conn.execute("SELECT name, value FROM counters"):
        global_conn.execute(
            "UPDATE counters SET value = ? "
            "WHERE project_id = ? AND name = ? AND value < ?",
            (row["value"], project_id, row["name"], row["value"]),
        )
