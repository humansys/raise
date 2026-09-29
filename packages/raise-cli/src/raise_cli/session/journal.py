"""Session journal — incremental memory persistence (SQLite backend).

Append-only journal for preserving decisions, insights, and task completions
across context compaction events. Each entry is stored in the journal_entries
table in the project SQLite database. Replaces the previous JSONL+FilesystemAdapter
persistence (S2780.3).

Two consumers:
- Agent: calls `rai session journal add` to record decisions/insights
- Hooks: call `rai session journal show --compact` to inject context post-compaction
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from raise_cli.memory.writer import WriteResult
from raise_cli.schemas.journal import JournalEntry, JournalEntryType
from raise_cli.storage.connection import get_project_db, get_project_id
from raise_cli.storage.schema import create_all

JOURNAL_FILE = "journal.jsonl"


def append_journal_entry(
    project_path: Path,
    session_id: str,
    entry_type: JournalEntryType,
    content: str,
    tags: list[str] | None = None,
    timestamp: datetime | None = None,
) -> WriteResult:
    """Append a journal entry to the session journal in SQLite.

    Args:
        project_path: Path to the project root.
        session_id: Session ID to associate the entry with.
        entry_type: Category of entry.
        content: The content to preserve.
        tags: Optional context tags.
        timestamp: When the entry was created. Defaults to now.

    Returns:
        WriteResult with generated ID.
    """
    ts = timestamp or datetime.now()
    root = project_path.resolve()

    pid = get_project_id(root)
    conn = get_project_db(root)
    create_all(conn)

    cursor = conn.execute(
        """INSERT INTO journal_entries (project_id, session_id, timestamp, entry_type, content, tags)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (
            pid,
            session_id,
            ts.isoformat(),
            entry_type.value,
            content,
            json.dumps(tags or []),
        ),
    )
    row_id = cursor.lastrowid
    conn.commit()
    conn.close()

    entry_id = f"JRN-{row_id:03d}"

    return WriteResult(
        success=True,
        id=entry_id,
        file_path=str(root),
        message=f"Journal {entry_id} appended ({entry_type.value})",
    )


def read_journal(
    project_path: Path,
    session_id: str,
    last_n: int | None = None,
) -> list[JournalEntry]:
    """Read journal entries for a session from SQLite.

    Args:
        project_path: Path to the project root.
        session_id: Session ID to read entries for.
        last_n: If set, return only the last N entries.

    Returns:
        List of JournalEntry objects, oldest first.
    """
    root = project_path.resolve()
    try:
        conn = get_project_db(root)
        create_all(conn)
    except OSError:
        return []

    pid = get_project_id(root)

    if last_n is not None:
        rows = conn.execute(
            """SELECT * FROM (
                   SELECT * FROM journal_entries
                   WHERE project_id = ? AND session_id = ?
                   ORDER BY id DESC LIMIT ?
               ) sub ORDER BY id ASC""",
            (pid, session_id, last_n),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM journal_entries WHERE project_id = ? AND session_id = ? ORDER BY id ASC",
            (pid, session_id),
        ).fetchall()
    conn.close()

    entries: list[JournalEntry] = []
    for row in rows:
        entries.append(
            JournalEntry(
                id=f"JRN-{row['id']:03d}",
                timestamp=datetime.fromisoformat(row["timestamp"]),
                entry_type=JournalEntryType(row["entry_type"]),
                content=row["content"],
                tags=json.loads(row["tags"]),
            )
        )

    return entries


def format_journal_compact(entries: list[JournalEntry]) -> str:
    """Format journal entries for compact context injection.

    Produces a token-efficient summary suitable for post-compaction
    context injection via hook stdout.

    Args:
        entries: Journal entries to format.

    Returns:
        Compact multi-line string.
    """
    if not entries:
        return "No journal entries."

    lines: list[str] = ["# Session Journal"]
    for entry in entries:
        tag_suffix = f" [{', '.join(entry.tags)}]" if entry.tags else ""
        lines.append(f"- {entry.entry_type.value.upper()}: {entry.content}{tag_suffix}")

    return "\n".join(lines)
