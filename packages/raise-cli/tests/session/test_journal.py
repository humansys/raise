"""Tests for session journal — incremental memory persistence."""

from __future__ import annotations

import json
from pathlib import Path

from raise_cli.schemas.journal import JournalEntry, JournalEntryType
from raise_cli.session.journal import append_journal_entry, read_journal


class TestJournalEntry:
    """Tests for JournalEntry model."""

    def test_creates_with_required_fields(self) -> None:
        entry = JournalEntry(
            id="JRN-001",
            entry_type=JournalEntryType.DECISION,
            content="Use incremental persistence",
        )
        assert entry.id == "JRN-001"
        assert entry.entry_type == JournalEntryType.DECISION
        assert entry.content == "Use incremental persistence"
        assert entry.tags == []

    def test_entry_type_values(self) -> None:
        assert JournalEntryType.DECISION.value == "decision"
        assert JournalEntryType.INSIGHT.value == "insight"
        assert JournalEntryType.TASK_DONE.value == "task_done"
        assert JournalEntryType.NOTE.value == "note"

    def test_tags_preserved(self) -> None:
        entry = JournalEntry(
            id="JRN-001",
            entry_type=JournalEntryType.NOTE,
            content="test",
            tags=["arch", "spike"],
        )
        assert entry.tags == ["arch", "spike"]


class TestAppendJournalEntry:
    """Tests for append_journal_entry writer."""

    def test_creates_file_and_appends(self, tmp_path: Path) -> None:
        session_dir = tmp_path / "sessions" / "SES-308"
        result = append_journal_entry(
            session_dir=session_dir,
            entry_type=JournalEntryType.DECISION,
            content="Use JSONL for journal",
        )
        assert result.success
        assert result.id == "JRN-001"

        journal_file = session_dir / "journal.jsonl"
        assert journal_file.exists()
        data = json.loads(journal_file.read_text().strip())
        assert data["entry_type"] == "decision"
        assert data["content"] == "Use JSONL for journal"

    def test_increments_id(self, tmp_path: Path) -> None:
        session_dir = tmp_path / "sessions" / "SES-308"
        append_journal_entry(
            session_dir=session_dir,
            entry_type=JournalEntryType.NOTE,
            content="first",
        )
        result = append_journal_entry(
            session_dir=session_dir,
            entry_type=JournalEntryType.NOTE,
            content="second",
        )
        assert result.id == "JRN-002"

    def test_tags_stored(self, tmp_path: Path) -> None:
        session_dir = tmp_path / "sessions" / "SES-308"
        append_journal_entry(
            session_dir=session_dir,
            entry_type=JournalEntryType.INSIGHT,
            content="Compaction loses rationale",
            tags=["compaction", "memory"],
        )
        journal_file = session_dir / "journal.jsonl"
        data = json.loads(journal_file.read_text().strip())
        assert data["tags"] == ["compaction", "memory"]


class TestReadJournal:
    """Tests for read_journal reader."""

    def _populate(self, session_dir: Path, count: int = 5) -> None:
        for i in range(count):
            append_journal_entry(
                session_dir=session_dir,
                entry_type=JournalEntryType.NOTE,
                content=f"entry {i + 1}",
            )

    def test_reads_all_entries(self, tmp_path: Path) -> None:
        session_dir = tmp_path / "sessions" / "SES-308"
        self._populate(session_dir, 3)

        entries = read_journal(session_dir)
        assert len(entries) == 3
        assert entries[0].content == "entry 1"
        assert entries[2].content == "entry 3"

    def test_reads_last_n(self, tmp_path: Path) -> None:
        session_dir = tmp_path / "sessions" / "SES-308"
        self._populate(session_dir, 5)

        entries = read_journal(session_dir, last_n=2)
        assert len(entries) == 2
        assert entries[0].content == "entry 4"
        assert entries[1].content == "entry 5"

    def test_empty_dir_returns_empty(self, tmp_path: Path) -> None:
        session_dir = tmp_path / "sessions" / "SES-308"
        entries = read_journal(session_dir)
        assert entries == []

    def test_compact_format(self, tmp_path: Path) -> None:
        session_dir = tmp_path / "sessions" / "SES-308"
        append_journal_entry(
            session_dir=session_dir,
            entry_type=JournalEntryType.DECISION,
            content="Use JSONL",
            tags=["arch"],
        )
        append_journal_entry(
            session_dir=session_dir,
            entry_type=JournalEntryType.TASK_DONE,
            content="T1 complete",
        )

        from raise_cli.session.journal import format_journal_compact

        output = format_journal_compact(read_journal(session_dir))
        assert "DECISION:" in output
        assert "Use JSONL" in output
        assert "TASK_DONE:" in output
        assert "T1 complete" in output


class TestAppendJournalEntryAdapter:
    """Verify append_journal_entry uses FilesystemAdapter (S1040.2 T3a)."""

    def test_delegates_to_adapter_append(self, tmp_path: Path) -> None:
        """append_journal_entry should use FilesystemAdapter.append."""
        from unittest.mock import patch

        session_dir = tmp_path / "sessions" / "SES-308"

        with patch("raise_cli.session.journal.FilesystemAdapter") as mock_adapter_cls:
            append_journal_entry(
                session_dir=session_dir,
                entry_type=JournalEntryType.DECISION,
                content="Test decision",
            )

            mock_adapter_cls.assert_called_once_with(root=session_dir)
            mock_adapter_cls.return_value.append.assert_called_once()
