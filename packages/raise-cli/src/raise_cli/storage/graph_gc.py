"""Garbage collection of dead graph checkout partitions (RAISE-18985).

The global ``~/.rai/raise.db`` holds graph rows for every project and every
worktree checkout. Worktrees removed outside ``rai worktree complete`` leave
their partitions behind; this module reclaims them.

Safety invariants:
- the repo-wide ``''`` partition is never touched;
- a checkout whose path still exists — or cannot be verified (permission
  error, non-absolute id) — is never touched;
- a partition holding ``graph_node_annotations`` rows is irreplaceable and is
  skipped (and reported);
- the automatic (post-build) pass also skips any checkout the worktrees
  registry still lists as open: a path this process cannot see (sandbox,
  container, unmounted drive) is not proof the checkout is gone — and it
  purges only with positive evidence: a closed registry row or a path under
  the system tmpdir (RAISE-18988).
"""

from __future__ import annotations

import logging
import sqlite3
import tempfile
from datetime import UTC, datetime, timedelta
from pathlib import Path

from pydantic import BaseModel, Field

from raise_cli.compat import try_file_lock

logger = logging.getLogger(__name__)

GC_STAMP_FILE = "graph-gc.last"
GC_LOCK_FILE = "graph-gc.lock"
GC_INTERVAL = timedelta(hours=24)
RECLAIM_CHUNK_PAGES = 2000


class GraphGcResult(BaseModel):
    """Outcome of a dead-checkout GC pass."""

    purged_checkouts: int = 0
    purged_nodes: int = 0
    skipped_annotated: list[tuple[str, str]] = Field(default_factory=list)
    purged: list[tuple[str, str]] = Field(default_factory=list)


def _is_live_or_unverifiable(checkout: str) -> bool:
    """True unless the checkout path is absolute and verifiably gone.

    Uses ``stat()`` rather than ``Path.exists()``: newer Pythons make
    ``exists()`` swallow every OSError, which would report an unreadable
    path as gone. Only not-found errors count as dead.
    """
    path = Path(checkout)
    if not path.is_absolute():
        return True
    try:
        path.stat()
    except (FileNotFoundError, NotADirectoryError):
        return False
    except (OSError, ValueError):
        return True
    return True


def _missing_table(exc: sqlite3.OperationalError) -> bool:
    return "no such table" in str(exc)


def _has_annotations(conn: sqlite3.Connection, pid: str, checkout: str) -> bool:
    """True when the partition holds annotations. Pre-V72 DB: no table, none."""
    try:
        row = conn.execute(
            "SELECT 1 FROM graph_node_annotations "
            "WHERE project_id = ? AND checkout_id = ? LIMIT 1",
            (pid, checkout),
        ).fetchone()
    except sqlite3.OperationalError as exc:
        if _missing_table(exc):
            return False
        raise
    return row is not None


def _registered_open(conn: sqlite3.Connection, pid: str, checkout: str) -> bool:
    """True when the worktrees registry lists ``checkout`` as an open worktree."""
    try:
        row = conn.execute(
            "SELECT 1 FROM worktrees WHERE project_id = ? AND path = ? "
            "AND status = 'open' LIMIT 1",
            (pid, checkout),
        ).fetchone()
    except sqlite3.OperationalError as exc:
        if _missing_table(exc):
            return False
        raise
    return row is not None


def _under_tmpdir(checkout: str) -> bool:
    tmp_root = str(Path(tempfile.gettempdir()).resolve())
    return checkout == tmp_root or checkout.startswith(tmp_root + "/")


def _registered_closed(conn: sqlite3.Connection, pid: str, checkout: str) -> bool:
    """True when the registry has a closed row for ``checkout``.

    Callers check open registrations first (``_registered_open``).
    """
    try:
        row = conn.execute(
            "SELECT 1 FROM worktrees WHERE project_id = ? AND path = ? "
            "AND status = 'closed' LIMIT 1",
            (pid, checkout),
        ).fetchone()
    except sqlite3.OperationalError as exc:
        if _missing_table(exc):
            return False
        raise
    return row is not None


def prune_dead_checkouts(
    conn: sqlite3.Connection,
    *,
    project_id: str | None,
    dry_run: bool = False,
    skip_registered_open: bool = False,
    require_evidence: bool = False,
) -> GraphGcResult:
    """Delete graph rows of checkouts whose path no longer exists.

    Each partition is re-checked and deleted inside one ``BEGIN IMMEDIATE``
    transaction, so an annotation written concurrently cannot be lost
    between the check and the delete.

    Args:
        conn: Open connection to the global raise.db.
        project_id: Restrict to one project; ``None`` means all projects.
        dry_run: Count what would be purged without deleting.
        skip_registered_open: Also spare checkouts the worktrees registry
            lists as open (used by the unattended post-build GC).
        require_evidence: Purge only with positive evidence the checkout is
            disposable — a closed registry row, or a path under the system
            tmpdir (RAISE-18988 F2). A path that merely fails to stat may be
            an unmounted volume; the unattended GC must not act on that alone.
    """
    sql = "SELECT DISTINCT project_id, checkout_id FROM graph_nodes WHERE checkout_id != ''"
    params: tuple[str, ...] = ()
    if project_id is not None:
        sql += " AND project_id = ?"
        params = (project_id,)
    result = GraphGcResult()
    for pid, checkout in conn.execute(sql, params).fetchall():
        if _is_live_or_unverifiable(checkout):
            continue
        # Only transactions opened here are committed or rolled back; a
        # dry run never touches the caller's transaction.
        owned = not dry_run
        if owned:
            conn.execute("BEGIN IMMEDIATE")
        try:
            purged = _purge_one(
                conn,
                pid,
                checkout,
                result,
                dry_run=dry_run,
                skip_registered_open=skip_registered_open,
                require_evidence=require_evidence,
            )
        except BaseException:
            if owned:
                conn.rollback()
            raise
        if owned:
            conn.commit() if purged else conn.rollback()
    return result


def _purge_one(
    conn: sqlite3.Connection,
    pid: str,
    checkout: str,
    result: GraphGcResult,
    *,
    dry_run: bool,
    skip_registered_open: bool,
    require_evidence: bool = False,
) -> bool:
    """Check and (unless dry-run) delete one partition. True when it counts.

    Runs under the caller's write lock, so the registry and annotation checks
    cannot race a concurrent registration or annotation write.
    """
    if (skip_registered_open or require_evidence) and _registered_open(
        conn, pid, checkout
    ):
        return False
    if (
        require_evidence
        and not _under_tmpdir(checkout)
        and not _registered_closed(conn, pid, checkout)
    ):
        return False
    if _has_annotations(conn, pid, checkout):
        result.skipped_annotated.append((pid, checkout))
        return False
    count = conn.execute(
        "SELECT COUNT(*) FROM graph_nodes WHERE project_id = ? AND checkout_id = ?",
        (pid, checkout),
    ).fetchone()[0]
    result.purged_checkouts += 1
    result.purged_nodes += int(count)
    result.purged.append((pid, checkout))
    if not dry_run:
        for table in ("graph_nodes", "graph_edges", "graph_builds"):
            conn.execute(
                f"DELETE FROM {table} WHERE project_id = ? AND checkout_id = ?",  # noqa: S608
                (pid, checkout),
            )
    return True


class ReclaimResult(BaseModel):
    """Outcome of a bounded free-page reclaim."""

    pages_freed: int = 0
    freelist_remaining: int = 0
    checkpoint_busy: bool = False
    unsupported: bool = False


def _freelist(conn: sqlite3.Connection) -> int:
    return int(conn.execute("PRAGMA freelist_count").fetchone()[0])


def reclaim_space(
    conn: sqlite3.Connection,
    *,
    max_pages: int,
    chunk_pages: int = RECLAIM_CHUNK_PAGES,
) -> ReclaimResult:
    """Return up to ``max_pages`` free pages to the OS, in short chunks.

    Needs ``auto_vacuum=INCREMENTAL`` (raise.db default). Each chunk is its
    own short write transaction, so sibling writers wait at most one chunk.
    The WAL is checkpointed before and after so freed pages actually shrink
    the files. Never runs a full ``VACUUM`` — for that, use
    ``VACUUM INTO`` a copy and swap it in while nothing has the DB open.
    """
    # auto_vacuum=INCREMENTAL (2) only applies to DBs created with it or
    # fully vacuumed since; on older DBs incremental_vacuum is a no-op.
    if int(conn.execute("PRAGMA auto_vacuum").fetchone()[0]) != 2:
        return ReclaimResult(freelist_remaining=_freelist(conn), unsupported=True)
    # PASSIVE never waits on readers; the closing TRUNCATE is what shrinks
    # the WAL, and its busy flag is reported instead of discarded.
    conn.execute("PRAGMA wal_checkpoint(PASSIVE)").fetchall()
    before = _freelist(conn)
    remaining = max(0, max_pages)
    while remaining > 0 and _freelist(conn) > 0:
        step = min(chunk_pages, remaining)
        # Each result row is one freed page: fetch all, or only one is freed.
        conn.execute(f"PRAGMA incremental_vacuum({step})").fetchall()
        conn.commit()
        remaining -= step
    busy = conn.execute("PRAGMA wal_checkpoint(TRUNCATE)").fetchone()
    after = _freelist(conn)
    return ReclaimResult(
        pages_freed=before - after,
        freelist_remaining=after,
        checkpoint_busy=bool(busy and busy[0]),
    )


def run_graph_gc_throttled(
    db_path: Path, *, now: datetime | None = None
) -> GraphGcResult | None:
    """Run an all-projects GC at most once per 24 h.

    The last-run timestamp lives next to the DB (``graph-gc.last``); no schema
    change. Returns ``None`` when throttled or when the DB does not exist.
    The stamp is only written after a successful run. A non-blocking lock
    file next to the stamp keeps concurrent builds from running it twice;
    a held lock also returns ``None``. Only purges with positive evidence
    (see ``prune_dead_checkouts(require_evidence=True)``).
    """
    if not db_path.exists():
        return None
    current = now or datetime.now(tz=UTC)
    if current.tzinfo is None:
        current = current.replace(tzinfo=UTC)
    stamp = db_path.parent / GC_STAMP_FILE
    try:
        last = datetime.fromisoformat(stamp.read_text().strip())
        if last.tzinfo is None:
            last = last.replace(tzinfo=UTC)
        # A future-dated stamp (clock skew, bad write) must not disable GC.
        if timedelta(0) <= current - last < GC_INTERVAL:
            return None
    except (OSError, ValueError):
        pass
    # RAISE-18988 F4: concurrent builds must not run the GC twice.
    with (db_path.parent / GC_LOCK_FILE).open("w") as lock:
        if not try_file_lock(lock):
            return None
        conn = sqlite3.connect(str(db_path), timeout=5)
        try:
            result = prune_dead_checkouts(conn, project_id=None, require_evidence=True)
        finally:
            conn.close()
        stamp.write_text(current.isoformat())
    log = logger.info if result.purged_checkouts else logger.debug
    log(
        "graph gc: purged %d checkouts, %d nodes, skipped %d annotated",
        result.purged_checkouts,
        result.purged_nodes,
        len(result.skipped_annotated),
    )
    return result
