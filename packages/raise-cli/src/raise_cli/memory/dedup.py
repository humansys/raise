"""Pattern-store dedup collapse (S14056.2, RAISE-14579).

S1 (V50) landed ``content_hash`` + a NON-unique index with backfill. This
module collapses the 68% residual duplicate rows created by the old
project_id-scoped dedup check (``validate_pattern_add``, which never saw the
``project_id=''`` shadow rows inserted by ``sync.py::_apply_server_pattern``).

All functions here are PURE over an injected ``sqlite3.Connection`` — none of
them resolve ``~/.rai/raise.db`` or any other global path (AC8). Only the
``rai memory dedup`` CLI wrapper (``cli/commands/memory.py``) touches the
real store. See ``s14056.2-design.md`` for the full algorithm and rationale.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

_SELECT_ACTIVE = (
    "SELECT pattern_id, project_id, content_hash, base, "
    "positives, negatives, evaluations, last_evaluated "
    "FROM patterns WHERE archived = 0"
)

# Column indices into the tuples returned by _SELECT_ACTIVE / sqlite3.Row —
# positional access works for both plain tuples (hermetic :memory: tests,
# which don't set row_factory) and sqlite3.Row (real injected connections
# that do — see storage/connection.py's `_configure`).
_COL_PATTERN_ID = 0
_COL_PROJECT_ID = 1
_COL_CONTENT_HASH = 2
_COL_BASE = 3
_COL_POSITIVES = 4
_COL_NEGATIVES = 5
_COL_EVALUATIONS = 6

# (pattern_id, project_id, content_hash, base, positives, negatives,
# evaluations, last_evaluated) — matches _SELECT_ACTIVE column order. Accepts
# both plain tuples and sqlite3.Row (both support positional indexing).
PatternRow = tuple[str, str, str | None, int, int, int, int, str | None]


@dataclass
class DedupGroup:
    """One ``(norm_pid, content_hash)`` partition with more than 1 active row."""

    norm_pid: str
    content_hash: str
    winner_id: str
    loser_ids: list[str]
    merged: dict[str, int]  # positives/negatives/evaluations (MAX per column)


@dataclass
class DedupPlan:
    """Read-only collapse plan produced by ``plan_dedup`` — mutates nothing."""

    groups: list[DedupGroup] = field(default_factory=list)
    total_active: int = 0
    losers: int = 0
    null_hash_skipped: int = 0
    per_project: dict[str, int] = field(default_factory=dict)


def _pattern_id_num(pattern_id: str) -> int:
    """Numeric tail of a pattern_id ('PAT-42' -> 42); non-numeric sorts last."""
    tail = pattern_id.rsplit("-", 1)[-1]
    return int(tail) if tail.isdigit() else 1 << 62


def _winner_key(row: PatternRow) -> tuple[int, int, int]:
    """Sort key for winner selection — ``min()`` over a group's rows wins.

    Priority order: ``base=1`` first (protects foundational patterns),
    ``project_id != ''`` first (local authorship beats a sync shadow),
    lowest numeric ``pattern_id`` (oldest, deterministic tiebreak).
    """
    pattern_id = row[_COL_PATTERN_ID]
    project_id = row[_COL_PROJECT_ID]
    base = row[_COL_BASE]
    return (
        -int(base),
        0 if project_id else 1,
        _pattern_id_num(pattern_id),
    )


def plan_dedup(conn: sqlite3.Connection, local_pid: str) -> DedupPlan:
    """Compute a read-only collapse plan. Mutates nothing (AC1/AC2/AC3/AC12).

    Groups active rows by ``(norm_pid, content_hash)`` where
    ``norm_pid = local_pid if project_id == '' else project_id`` — only the
    empty shadow partition is ever re-keyed; a non-empty ``project_id`` is
    never touched (RAISE-13467). Rows with ``content_hash IS NULL`` are
    omitted from grouping and reported via ``null_hash_skipped``.
    """
    rows = conn.execute(_SELECT_ACTIVE).fetchall()

    groups: dict[tuple[str, str], list[PatternRow]] = {}
    null_skipped = 0
    per_project: dict[str, int] = {}

    for row in rows:
        project_id = row[_COL_PROJECT_ID]
        content_hash = row[_COL_CONTENT_HASH]
        norm = local_pid if project_id == "" else project_id
        per_project[norm] = per_project.get(norm, 0) + 1
        if content_hash is None:
            null_skipped += 1
            continue
        groups.setdefault((norm, content_hash), []).append(row)

    dedup_groups: list[DedupGroup] = []
    total_losers = 0
    for (norm, content_hash), group_rows in groups.items():
        if len(group_rows) < 2:
            continue
        winner_row = min(group_rows, key=_winner_key)
        winner_id = winner_row[_COL_PATTERN_ID]
        loser_ids = [
            r[_COL_PATTERN_ID] for r in group_rows if r[_COL_PATTERN_ID] != winner_id
        ]
        merged = {
            "positives": max(r[_COL_POSITIVES] for r in group_rows),
            "negatives": max(r[_COL_NEGATIVES] for r in group_rows),
            "evaluations": max(r[_COL_EVALUATIONS] for r in group_rows),
        }
        dedup_groups.append(
            DedupGroup(
                norm_pid=norm,
                content_hash=content_hash,
                winner_id=winner_id,
                loser_ids=loser_ids,
                merged=merged,
            )
        )
        total_losers += len(loser_ids)

    return DedupPlan(
        groups=dedup_groups,
        total_active=len(rows),
        losers=total_losers,
        null_hash_skipped=null_skipped,
        per_project=per_project,
    )


def apply_collapse(conn: sqlite3.Connection, plan: DedupPlan) -> None:
    """Apply a ``DedupPlan``: archive losers, normalize + merge winners.

    NEVER deletes a row (AC4) — losers are marked ``archived = 1`` so the
    collapse is a reversible checkpoint (``SELECT ... WHERE archived = 1``
    recovers them). Runs inside a single transaction. Idempotent (AC9): a
    plan with no groups (e.g. a re-run of ``plan_dedup`` post-collapse) is a
    no-op.
    """
    if not plan.groups:
        return
    now = datetime.now(UTC).isoformat()
    with conn:
        for group in plan.groups:
            conn.execute(
                "UPDATE patterns SET project_id = ?, positives = ?, "
                "negatives = ?, evaluations = ?, updated_at = ? "
                "WHERE pattern_id = ?",
                (
                    group.norm_pid,
                    group.merged["positives"],
                    group.merged["negatives"],
                    group.merged["evaluations"],
                    now,
                    group.winner_id,
                ),
            )
            if group.loser_ids:
                placeholders = ",".join("?" for _ in group.loser_ids)
                # Only generated "?" placeholders are interpolated.
                conn.execute(
                    "UPDATE patterns SET archived = 1, updated_at = ? "  # noqa: S608  # nosec B608
                    f"WHERE pattern_id IN ({placeholders})",
                    (now, *group.loser_ids),
                )


# Self-identifying loser predicate (DD-4): an archived=1 row is a dedup loser
# (not a prune_stale_patterns leftover, which shares the same archived=1 flag)
# iff a live winner still exists for its (norm_pid, content_hash) partition.
# No archived_reason column needed — the gemelo's presence is the signal.
_PURGE_LOSERS_SQL = (
    "DELETE FROM patterns AS loser "
    "WHERE loser.archived = 1 "
    "AND loser.content_hash IS NOT NULL "
    "AND EXISTS ("
    "SELECT 1 FROM patterns AS w "
    "WHERE w.archived = 0 "
    "AND w.content_hash = loser.content_hash "
    "AND w.project_id = COALESCE(NULLIF(loser.project_id, ''), ?)"
    ")"
)


def purge_archived_losers(conn: sqlite3.Connection, local_pid: str) -> int:
    """DELETE only dedup losers that still have a live winner gemelo.

    Two producers set ``archived = 1``: dedup losers (this module) and
    ``prune_stale_patterns`` (unrelated, no gemelo). A dedup loser is
    self-identifying (DD-4) — no ``archived_reason`` column needed — because
    an active winner still exists for its ``(norm_pid, content_hash)``
    partition; a stale-archived row has none and is left untouched. Returns
    the number of rows deleted. Idempotent: a second run deletes 0.
    """
    with conn:
        cur = conn.execute(_PURGE_LOSERS_SQL, (local_pid,))
        return max(cur.rowcount, 0)


def vacuum(conn: sqlite3.Connection) -> None:
    """Reclaim free pages after a purge. Requires a file-backed DB, not ``:memory:``."""
    conn.execute("VACUUM")


def backup_db(conn: sqlite3.Connection, dst: Path) -> None:
    """Online-consistent backup via the sqlite3 backup API (DD-5) — never ``cp``.

    ``cp`` mid-WAL-write can copy an inconsistent snapshot; ``Connection.backup``
    is the sqlite3-native online-consistent equivalent.
    """
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst_conn = sqlite3.connect(str(dst))
    try:
        conn.backup(dst_conn)
    finally:
        dst_conn.close()
