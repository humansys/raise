"""Tests for shared session index and active session pointer."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from raise_cli.session.index import (
    SessionIndexEntry,
    clear_active_session,
    read_active_session,
    read_session_entries,
    write_active_session,
    write_session_entry,
)


class TestSessionIndexEntry:
    """Tests for SessionIndexEntry model."""

    def test_create_minimal(self) -> None:
        """Should create entry with required fields only."""
        entry = SessionIndexEntry(
            id="S-E-260322-1430",
            name="gemba session",
            started=datetime(2026, 3, 22, 14, 30),
        )
        assert entry.id == "S-E-260322-1430"
        assert entry.name == "gemba session"
        assert entry.closed is None

    def test_create_full(self) -> None:
        """Should create entry with all fields."""
        entry = SessionIndexEntry(
            id="S-E-260322-1430",
            name="gemba session identity",
            started=datetime(2026, 3, 22, 14, 30),
            closed=datetime(2026, 3, 22, 18, 45),
            type="research",
            summary="Analyzed session implementation",
            outcomes=["7 failure modes identified"],
            branch="dev",
        )
        assert entry.closed == datetime(2026, 3, 22, 18, 45)
        assert entry.type == "research"
        assert len(entry.outcomes) == 1

    def test_frozen(self) -> None:
        """Entry should be immutable."""
        entry = SessionIndexEntry(
            id="S-E-260322-1430",
            name="test",
            started=datetime(2026, 3, 22, 14, 30),
        )
        try:
            entry.name = "changed"  # type: ignore[misc]
            raise AssertionError("Should have raised")
        except (AttributeError, TypeError, Exception):
            pass  # Expected — frozen model


class TestWriteAndReadIndex:
    """Tests for shared index JSONL read/write."""

    def test_write_creates_dir_and_file(self, tmp_path: Path) -> None:
        """First write should create prefix dir and index.jsonl."""
        entry = SessionIndexEntry(
            id="S-E-260322-1430",
            name="first session",
            started=datetime(2026, 3, 22, 14, 30),
        )
        result = write_session_entry("E", entry, project_root=tmp_path)
        assert result.exists()
        assert result.name == "index.jsonl"
        assert "sessions" in str(result)
        assert result.read_text(encoding="utf-8").strip() != ""

    def test_write_appends_not_overwrites(self, tmp_path: Path) -> None:
        """Second write should append, not overwrite first entry."""
        entry1 = SessionIndexEntry(
            id="S-E-260322-1430",
            name="first",
            started=datetime(2026, 3, 22, 14, 30),
        )
        entry2 = SessionIndexEntry(
            id="S-E-260322-1600",
            name="second",
            started=datetime(2026, 3, 22, 16, 0),
        )
        write_session_entry("E", entry1, project_root=tmp_path)
        write_session_entry("E", entry2, project_root=tmp_path)

        entries = read_session_entries("E", project_root=tmp_path)
        assert len(entries) == 2
        assert entries[0].name == "first"
        assert entries[1].name == "second"

    def test_read_entries_returns_all(self, tmp_path: Path) -> None:
        """Should return all entries in order."""
        for i in range(3):
            entry = SessionIndexEntry(
                id=f"S-E-260322-{1430 + i}",
                name=f"session {i}",
                started=datetime(2026, 3, 22, 14, 30 + i),
            )
            write_session_entry("E", entry, project_root=tmp_path)

        entries = read_session_entries("E", project_root=tmp_path)
        assert len(entries) == 3
        assert [e.name for e in entries] == ["session 0", "session 1", "session 2"]

    def test_read_entries_nonexistent(self, tmp_path: Path) -> None:
        """Should return empty list if index doesn't exist."""
        entries = read_session_entries("E", project_root=tmp_path)
        assert entries == []

    def test_read_entries_empty_file(self, tmp_path: Path) -> None:
        """Should return empty list if index file is empty."""
        index_dir = tmp_path / ".raise" / "rai" / "sessions" / "E"
        index_dir.mkdir(parents=True)
        (index_dir / "index.jsonl").write_text("", encoding="utf-8")

        entries = read_session_entries("E", project_root=tmp_path)
        assert entries == []

    def test_entry_roundtrip_datetime(self, tmp_path: Path) -> None:
        """Datetime serialization should survive write/read roundtrip."""
        entry = SessionIndexEntry(
            id="S-E-260322-1430",
            name="roundtrip test",
            started=datetime(2026, 3, 22, 14, 30, 22),
            closed=datetime(2026, 3, 22, 18, 45, 11),
        )
        write_session_entry("E", entry, project_root=tmp_path)
        entries = read_session_entries("E", project_root=tmp_path)
        assert entries[0].started == entry.started
        assert entries[0].closed == entry.closed


class TestActiveSessionPointer:
    """Tests for active session pointer (plain text file)."""

    def test_write_active_session(self, tmp_path: Path) -> None:
        """Should write session ID to active-session file."""
        write_active_session("S-E-260322-1430", project_root=tmp_path)
        pointer_file = tmp_path / ".raise" / "rai" / "personal" / "active-session"
        assert pointer_file.exists()
        assert pointer_file.read_text(encoding="utf-8").strip() == "S-E-260322-1430"

    def test_read_active_session(self, tmp_path: Path) -> None:
        """Should read back the session ID."""
        write_active_session("S-E-260322-1430", project_root=tmp_path)
        result = read_active_session(project_root=tmp_path)
        assert result == "S-E-260322-1430"

    def test_read_active_session_nonexistent(self, tmp_path: Path) -> None:
        """Should return None if no active session."""
        result = read_active_session(project_root=tmp_path)
        assert result is None

    def test_clear_active_session(self, tmp_path: Path) -> None:
        """Should remove the active session pointer file."""
        write_active_session("S-E-260322-1430", project_root=tmp_path)
        clear_active_session(project_root=tmp_path)
        result = read_active_session(project_root=tmp_path)
        assert result is None

    def test_clear_nonexistent_is_noop(self, tmp_path: Path) -> None:
        """Clearing nonexistent pointer should not raise."""
        clear_active_session(project_root=tmp_path)  # Should not raise
