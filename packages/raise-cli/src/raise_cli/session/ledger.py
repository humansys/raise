"""Session ledger — cross-project self-surfacing store (RAISE-13146, O2).

Externalized, self-surfacing session ledger: independent of the fragile
session-binding (path-equality across worktrees) that `rai session journal
add` depends on (deprecated, RAISE-1433). Persists to the
``session_ledger_entries`` table in the global ``~/.rai/raise.db`` — outside
the agent's context, so it survives compaction.

UPSERT real (transactional, latest-wins) keyed by ``(session_id,
natural_key)`` — NOT an append-only log with fold-at-read (that reintroduces
the stale/race failure mode this ledger exists to kill).

Shape mirrors ``session/journal.py`` (function signatures, try/except-OSError
on read) — but ``journal.py`` is a pattern reference only, not a target to
extend (it is deprecated).
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path

from raise_cli.schemas.session_ledger import LedgerEntry, LedgerKind
from raise_cli.session.scope import SessionScope
from raise_cli.storage.connection import get_project_db, get_project_id
from raise_cli.storage.schema import create_all

_SECTION_TITLES: dict[LedgerKind, str] = {
    LedgerKind.meta: "Meta",
    LedgerKind.project: "Proyectos",
    LedgerKind.cartridge: "Cartuchos",
    LedgerKind.issue: "Issues",
    LedgerKind.branch: "Branches",
    LedgerKind.artifact: "Artefactos",
    LedgerKind.mission: "Misiones",
    LedgerKind.open_thread: "Cabos abiertos",
    LedgerKind.friction: "Fricción",
}

# Rendering order: specimen's 8 sections, friction last (quality signal).
_SECTION_ORDER: list[LedgerKind] = [
    LedgerKind.meta,
    LedgerKind.project,
    LedgerKind.cartridge,
    LedgerKind.issue,
    LedgerKind.branch,
    LedgerKind.artifact,
    LedgerKind.mission,
    LedgerKind.open_thread,
    LedgerKind.friction,
]


def upsert_entry(entry: LedgerEntry, project_root: Path) -> None:
    """Upsert a ledger entry — transactional latest-wins on (session_id, natural_key).

    Args:
        entry: The typed ledger row to write.
        project_root: Project root used to resolve the global DB connection.
    """
    conn = get_project_db(project_root)
    create_all(conn)
    conn.execute(
        """INSERT INTO session_ledger_entries
               (session_id, natural_key, kind, project_id, timestamp, fields_json)
           VALUES (?, ?, ?, ?, ?, ?)
           ON CONFLICT(session_id, natural_key) DO UPDATE SET
               kind=excluded.kind,
               project_id=excluded.project_id,
               timestamp=excluded.timestamp,
               fields_json=excluded.fields_json""",
        (
            entry.session_id,
            entry.natural_key,
            entry.kind.value,
            entry.project_id,
            entry.timestamp.isoformat(),
            json.dumps(entry.fields),
        ),
    )
    conn.commit()
    conn.close()


def _row_to_entry(row: sqlite3.Row) -> LedgerEntry:
    """Deserialize a `session_ledger_entries` row into a LedgerEntry."""
    return LedgerEntry(
        session_id=row["session_id"],
        kind=LedgerKind(row["kind"]),
        natural_key=row["natural_key"],
        timestamp=datetime.fromisoformat(row["timestamp"]),
        project_id=row["project_id"],
        fields=json.loads(row["fields_json"]),
    )


def read_entries(
    session_id: str,
    project_root: Path,
    kind: LedgerKind | None = None,
) -> list[LedgerEntry]:
    """Read ledger entries for a session, optionally filtered by kind.

    Args:
        session_id: Partition key — discover_agent_session_id().
        project_root: Project root used to resolve the global DB connection.
        kind: Optional kind filter.

    Returns:
        List of LedgerEntry, insertion order by rowid (stable, not semantic).
    """
    try:
        conn = get_project_db(project_root)
        create_all(conn)
    except OSError:
        return []

    if kind is not None:
        rows = conn.execute(
            "SELECT * FROM session_ledger_entries WHERE session_id = ? AND kind = ? "
            "ORDER BY rowid ASC",
            (session_id, kind.value),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM session_ledger_entries WHERE session_id = ? "
            "ORDER BY rowid ASC",
            (session_id,),
        ).fetchall()
    conn.close()

    return [_row_to_entry(row) for row in rows]


def resolve_surface_session(
    project_root: Path,
    current_session_id: str | None,
    *,
    scope: SessionScope,
) -> str | None:
    """Resolve which session's ledger to auto-surface (RAISE-13341, E15456).

    Cross-session continuity: a brand-new session (distinct ``agent_session_id``)
    would otherwise see an empty ledger. This picks the session whose ledger is
    most relevant to surface at orientation:

    - If ``current_session_id`` already has entries for this project → itself
      (the active session always wins, unchanged).
    - Otherwise → the most recent PREVIOUS session that touched this
      ``project_id`` AND is attributable to the caller's worktree. Attribution
      comes from the sessions table (S15456.1):
      ``session_ledger_entries.session_id`` matches
      ``sessions.agent_session_id``. NOTE: ``project_id`` is shared by all
      worktrees of the project — it never prevented cross-worktree jumps (the
      pre-E15456 comment claiming otherwise was wrong); scope now comes from
      the attribution join. Empty agent keys never match (D1).
    - ``None`` when no in-scope session has entries — an honest empty ledger
      beats a foreign one (epic D2). Explicit ``--session`` surfacing
      (`rai session context/ledger show --session X`) never falls back
      (unchanged).

    Args:
        project_root: Project root — resolves the global DB and the project_id.
        current_session_id: The session resolved for this run (may be None).
        scope: Caller's resolved scope identity (worktree attribution filter).

    Returns:
        The session_id to surface, or None.
    """
    pid = get_project_id(project_root)
    try:
        conn = get_project_db(project_root)
        create_all(conn)
    except OSError:
        return None

    attributable = (
        "AND sle.session_id <> '' "
        "AND EXISTS ("
        "  SELECT 1 FROM sessions s "
        "  WHERE s.project_id = sle.project_id "
        "    AND s.agent_session_id = sle.session_id "
        "    AND s.agent_session_id <> '' "
        "    AND s.worktree_id = ?"
        ")"
    )
    try:
        if current_session_id:
            has_own = conn.execute(
                "SELECT 1 FROM session_ledger_entries "
                "WHERE session_id = ? AND project_id = ? LIMIT 1",
                (current_session_id, pid),
            ).fetchone()
            if has_own is not None:
                return current_session_id
            # The attributable fragment is a fixed literal; values use "?".
            sql = (
                "SELECT sle.session_id FROM session_ledger_entries sle "  # noqa: S608  # nosec B608
                "WHERE sle.project_id = ? AND sle.session_id != ? "
                f"{attributable} "
                "ORDER BY sle.timestamp DESC LIMIT 1"
            )
            row = conn.execute(
                sql, (pid, current_session_id, scope.worktree_id)
            ).fetchone()
        else:
            # The attributable fragment is a fixed literal; values use "?".
            sql = (
                "SELECT sle.session_id FROM session_ledger_entries sle "  # noqa: S608  # nosec B608
                f"WHERE sle.project_id = ? {attributable} "
                "ORDER BY sle.timestamp DESC LIMIT 1"
            )
            row = conn.execute(sql, (pid, scope.worktree_id)).fetchone()
    finally:
        conn.close()

    return row["session_id"] if row is not None else None


def render_sections(entries: list[LedgerEntry]) -> str:
    """Render ledger entries as Markdown, grouped by kind (8 sections + friction).

    Args:
        entries: Ledger entries to render (any order — grouped internally).

    Returns:
        Markdown string, empty when entries is empty.
    """
    if not entries:
        return ""

    by_kind: dict[LedgerKind, list[LedgerEntry]] = {}
    for entry in entries:
        by_kind.setdefault(entry.kind, []).append(entry)

    parts: list[str] = []
    for kind in _SECTION_ORDER:
        rows = by_kind.get(kind)
        if not rows:
            continue
        lines = [f"### {_SECTION_TITLES[kind]}"]
        for row in rows:
            field_str = " | ".join(f"{k}={v}" for k, v in row.fields.items())
            suffix = f" | {field_str}" if field_str else ""
            lines.append(f"- {row.natural_key}{suffix}")
        parts.append("\n".join(lines))

    return "\n\n".join(parts)
