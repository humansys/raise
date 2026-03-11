"""Session journal — incremental memory persistence.

Append-only journal for preserving decisions, insights, and task completions
across context compaction events. Each entry is a JSONL line in
.raise/rai/personal/sessions/{session_id}/journal.jsonl.

Two consumers:
- Agent: calls `rai session journal add` to record decisions/insights
- Hooks: call `rai session journal show --compact` to inject context post-compaction
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from raise_cli.memory.writer import WriteResult, get_next_id
from raise_cli.schemas.journal import JournalEntry, JournalEntryType

JOURNAL_FILE = "journal.jsonl"


def append_journal_entry(
    session_dir: Path,
    entry_type: JournalEntryType,
    content: str,
    tags: list[str] | None = None,
    timestamp: datetime | None = None,
) -> WriteResult:
    """Append a journal entry to the session journal.

    Args:
        session_dir: Path to per-session directory.
        entry_type: Category of entry.
        content: The content to preserve.
        tags: Optional context tags.
        timestamp: When the entry was created. Defaults to now.

    Returns:
        WriteResult with generated ID.
    """
    file_path = session_dir / JOURNAL_FILE
    entry_id = get_next_id(file_path, "JRN")
    ts = timestamp or datetime.now()

    data: dict[str, Any] = {
        "id": entry_id,
        "timestamp": ts.isoformat(),
        "entry_type": entry_type.value,
        "content": content,
        "tags": tags or [],
    }

    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(data) + "\n")

    return WriteResult(
        success=True,
        id=entry_id,
        file_path=str(file_path),
        message=f"Journal {entry_id} appended ({entry_type.value})",
    )


def read_journal(
    session_dir: Path,
    last_n: int | None = None,
) -> list[JournalEntry]:
    """Read journal entries from a session.

    Args:
        session_dir: Path to per-session directory.
        last_n: If set, return only the last N entries.

    Returns:
        List of JournalEntry objects, oldest first.
    """
    file_path = session_dir / JOURNAL_FILE
    if not file_path.exists():
        return []

    entries: list[JournalEntry] = []
    for line in file_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        data = json.loads(line)
        entries.append(JournalEntry(**data))

    if last_n is not None:
        entries = entries[-last_n:]

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
