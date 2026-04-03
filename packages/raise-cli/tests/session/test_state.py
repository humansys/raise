"""Tests for session state schema and persistence."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from raise_cli.schemas.session_state import (
    CurrentWork,
    LastSession,
    PendingItems,
    SessionState,
)
from raise_cli.session.state import (
    StaleWriteError,
    get_session_state_path,
    load_session_state,
    save_session_state,
)


def _make_session_state() -> SessionState:
    """Create a typical session state for testing."""
    return SessionState(
        current_work=CurrentWork(
            epic="E15",
            story="S15.7",
            phase="implement",
            branch="story/s15.7/session-protocol",
        ),
        last_session=LastSession(
            id="SES-097",
            date=date(2026, 2, 8),
            developer="Emilio",
            summary="Session protocol design",
            patterns_captured=["PAT-187", "PAT-188"],
        ),
        pending=PendingItems(
            decisions=["Foundational pattern curation"],
            blockers=[],
            next_actions=["Implement session-state schema"],
        ),
        notes="ADR-024 created.",
    )


class TestSessionStateSchema:
    """Tests for SessionState Pydantic models."""

    def test_current_work_defaults_to_empty(self) -> None:
        """CurrentWork defaults all fields to empty string."""
        work = CurrentWork()
        assert work.epic == ""
        assert work.story == ""
        assert work.phase == ""
        assert work.branch == ""

    def test_last_session_requires_core_fields(self) -> None:
        """LastSession requires id, date, developer, summary."""
        with pytest.raises(ValidationError):
            LastSession()  # type: ignore[call-arg]

    def test_last_session_patterns_default_empty(self) -> None:
        """LastSession patterns_captured defaults to empty list."""
        session = LastSession(
            id="SES-001", date=date(2026, 2, 8), developer="Test", summary="test"
        )
        assert session.patterns_captured == []

    def test_pending_items_defaults_empty(self) -> None:
        """PendingItems defaults all lists to empty."""
        pending = PendingItems()
        assert pending.decisions == []
        assert pending.blockers == []
        assert pending.next_actions == []

    def test_session_state_requires_current_work_and_last_session(self) -> None:
        """SessionState requires current_work and last_session."""
        with pytest.raises(ValidationError):
            SessionState()  # type: ignore[call-arg]

    def test_session_state_pending_defaults(self) -> None:
        """SessionState pending defaults to empty PendingItems."""
        state = SessionState(
            current_work=CurrentWork(
                epic="E15", story="S15.7", phase="design", branch="main"
            ),
            last_session=LastSession(
                id="SES-001",
                date=date(2026, 2, 8),
                developer="Test",
                summary="test",
            ),
        )
        assert state.pending.decisions == []
        assert state.notes == ""


class TestGetSessionStatePath:
    """Tests for get_session_state_path."""

    def test_returns_personal_path_without_session_id(self, tmp_path: Path) -> None:
        """Path is project_root/.raise/rai/personal/session-state.yaml when no session_id."""
        path = get_session_state_path(tmp_path)
        assert path == tmp_path / ".raise" / "rai" / "personal" / "session-state.yaml"

    def test_returns_per_session_path_with_session_id(self, tmp_path: Path) -> None:
        """Path is .raise/rai/personal/sessions/{session_id}/state.yaml when session_id provided."""
        path = get_session_state_path(tmp_path, session_id="SES-177")
        expected = (
            tmp_path
            / ".raise"
            / "rai"
            / "personal"
            / "sessions"
            / "SES-177"
            / "state.yaml"
        )
        assert path == expected


class TestLoadSessionState:
    """Tests for load_session_state."""

    def test_returns_none_if_file_missing(self, tmp_path: Path) -> None:
        """Returns None when session-state.yaml doesn't exist."""
        result = load_session_state(tmp_path)
        assert result is None

    def test_returns_none_for_empty_file(self, tmp_path: Path) -> None:
        """Returns None for empty YAML file."""
        state_path = tmp_path / ".raise" / "rai" / "personal" / "session-state.yaml"
        state_path.parent.mkdir(parents=True)
        state_path.write_text("")
        result = load_session_state(tmp_path)
        assert result is None

    def test_returns_none_for_invalid_yaml(self, tmp_path: Path) -> None:
        """Returns None for invalid YAML."""
        state_path = tmp_path / ".raise" / "rai" / "personal" / "session-state.yaml"
        state_path.parent.mkdir(parents=True)
        state_path.write_text("invalid: yaml: [")
        result = load_session_state(tmp_path)
        assert result is None

    def test_returns_none_for_invalid_schema(self, tmp_path: Path) -> None:
        """Returns None for YAML that doesn't match schema."""
        state_path = tmp_path / ".raise" / "rai" / "personal" / "session-state.yaml"
        state_path.parent.mkdir(parents=True)
        state_path.write_text("not_a_field: true\n")
        result = load_session_state(tmp_path)
        assert result is None

    def test_migrates_from_old_path(self, tmp_path: Path) -> None:
        """Migrates session-state.yaml from old .raise/rai/ to personal/."""
        old_path = tmp_path / ".raise" / "rai" / "session-state.yaml"
        old_path.parent.mkdir(parents=True)
        old_path.write_text(
            yaml.dump(
                _make_session_state().model_dump(mode="json"),
                default_flow_style=False,
            )
        )
        new_path = tmp_path / ".raise" / "rai" / "personal" / "session-state.yaml"
        assert not new_path.exists()

        result = load_session_state(tmp_path)
        assert result is not None
        assert result.current_work.epic == "E15"
        # Old file should be gone, new file should exist
        assert not old_path.exists()
        assert new_path.exists()

    def test_no_migration_if_new_path_exists(self, tmp_path: Path) -> None:
        """Does not migrate if personal/ already has session-state.yaml."""
        old_path = tmp_path / ".raise" / "rai" / "session-state.yaml"
        old_path.parent.mkdir(parents=True)
        old_path.write_text("stale: true\n")

        new_path = tmp_path / ".raise" / "rai" / "personal" / "session-state.yaml"
        new_path.parent.mkdir(parents=True)
        new_path.write_text(
            yaml.dump(
                _make_session_state().model_dump(mode="json"),
                default_flow_style=False,
            )
        )

        result = load_session_state(tmp_path)
        assert result is not None
        assert result.current_work.epic == "E15"

    def test_loads_from_per_session_dir(self, tmp_path: Path) -> None:
        """Loads from sessions/{session_id}/state.yaml when session_id provided."""
        session_dir = tmp_path / ".raise" / "rai" / "personal" / "sessions" / "SES-177"
        session_dir.mkdir(parents=True)
        state_path = session_dir / "state.yaml"
        state_path.write_text(
            yaml.dump(
                _make_session_state().model_dump(mode="json"),
                default_flow_style=False,
            )
        )
        result = load_session_state(tmp_path, session_id="SES-177")
        assert result is not None
        assert result.current_work.epic == "E15"

    def test_loads_valid_state(self, tmp_path: Path) -> None:
        """Loads and validates a correct session state file."""
        state_path = tmp_path / ".raise" / "rai" / "personal" / "session-state.yaml"
        state_path.parent.mkdir(parents=True)
        state_path.write_text(
            yaml.dump(
                _make_session_state().model_dump(mode="json"),
                default_flow_style=False,
            )
        )
        result = load_session_state(tmp_path)
        assert result is not None
        assert result.current_work.epic == "E15"
        assert result.last_session.id == "SES-097"


class TestSaveSessionState:
    """Tests for save_session_state."""

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        """Creates .raise/rai/personal/ if it doesn't exist."""
        state = _make_session_state()
        save_session_state(tmp_path, state)
        state_path = tmp_path / ".raise" / "rai" / "personal" / "session-state.yaml"
        assert state_path.exists()

    def test_writes_valid_yaml(self, tmp_path: Path) -> None:
        """Written file is valid YAML."""
        state = _make_session_state()
        save_session_state(tmp_path, state)
        state_path = tmp_path / ".raise" / "rai" / "personal" / "session-state.yaml"
        data = yaml.safe_load(state_path.read_text(encoding="utf-8"))
        assert data["current_work"]["epic"] == "E15"
        assert data["last_session"]["id"] == "SES-097"

    def test_overwrites_existing_file(self, tmp_path: Path) -> None:
        """Overwrites existing session-state.yaml."""
        state1 = _make_session_state()
        save_session_state(tmp_path, state1)

        state2 = SessionState(
            current_work=CurrentWork(
                epic="E16", story="S16.1", phase="design", branch="main"
            ),
            last_session=LastSession(
                id="SES-100",
                date=date(2026, 2, 9),
                developer="Test",
                summary="new session",
            ),
        )
        save_session_state(tmp_path, state2)

        result = load_session_state(tmp_path)
        assert result is not None
        assert result.current_work.epic == "E16"
        assert result.last_session.id == "SES-100"

    def test_saves_to_per_session_dir(self, tmp_path: Path) -> None:
        """Writes to sessions/{session_id}/state.yaml when session_id provided."""
        state = _make_session_state()
        save_session_state(tmp_path, state, session_id="SES-177")
        expected = (
            tmp_path
            / ".raise"
            / "rai"
            / "personal"
            / "sessions"
            / "SES-177"
            / "state.yaml"
        )
        assert expected.exists()
        data = yaml.safe_load(expected.read_text(encoding="utf-8"))
        assert data["current_work"]["epic"] == "E15"

    def test_saves_to_per_session_dir_without_flat(self, tmp_path: Path) -> None:
        """Saves to per-session dir without creating flat file."""
        state = _make_session_state()
        save_session_state(tmp_path, state, session_id="SES-200")
        flat_path = tmp_path / ".raise" / "rai" / "personal" / "session-state.yaml"
        assert not flat_path.exists(), (
            "Should not create flat file when session_id provided"
        )

    def test_roundtrip(self, tmp_path: Path) -> None:
        """Save then load returns equivalent state."""
        original = _make_session_state()
        save_session_state(tmp_path, original)
        loaded = load_session_state(tmp_path)

        assert loaded is not None
        assert loaded.current_work.epic == original.current_work.epic
        assert loaded.current_work.story == original.current_work.story
        assert loaded.last_session.id == original.last_session.id
        assert loaded.last_session.date == original.last_session.date
        assert loaded.last_session.developer == original.last_session.developer
        assert loaded.last_session.summary == original.last_session.summary
        assert (
            loaded.last_session.patterns_captured
            == original.last_session.patterns_captured
        )
        assert loaded.pending.decisions == original.pending.decisions
        assert loaded.pending.next_actions == original.pending.next_actions
        assert loaded.notes == original.notes


class TestMigrateFlatToSession:
    """Tests for migrate_flat_to_session (RAISE-138)."""

    def test_migrates_state_and_signals(self, tmp_path: Path) -> None:
        """Moves flat state and signals files into per-session directory."""
        from raise_cli.session.state import migrate_flat_to_session

        personal_dir = tmp_path / ".raise" / "rai" / "personal"
        personal_dir.mkdir(parents=True)
        # Create flat files
        flat_state = personal_dir / "session-state.yaml"
        flat_state.write_text("current_work:\n  epic: E15\n")
        telemetry_dir = personal_dir / "telemetry"
        telemetry_dir.mkdir()
        flat_signals = telemetry_dir / "signals.jsonl"
        flat_signals.write_text('{"signal_type": "test"}\n')

        result = migrate_flat_to_session(tmp_path, "SES-100")

        assert result is True
        session_dir = personal_dir / "sessions" / "SES-100"
        assert (session_dir / "state.yaml").exists()
        assert (session_dir / "state.yaml").read_text(
            encoding="utf-8"
        ) == "current_work:\n  epic: E15\n"
        assert (session_dir / "signals.jsonl").exists()
        assert (session_dir / "signals.jsonl").read_text(
            encoding="utf-8"
        ) == '{"signal_type": "test"}\n'
        # Flat files removed
        assert not flat_state.exists()
        assert not flat_signals.exists()

    def test_migrates_state_only(self, tmp_path: Path) -> None:
        """Migrates state file when no signals file exists."""
        from raise_cli.session.state import migrate_flat_to_session

        personal_dir = tmp_path / ".raise" / "rai" / "personal"
        personal_dir.mkdir(parents=True)
        flat_state = personal_dir / "session-state.yaml"
        flat_state.write_text("current_work:\n  epic: E15\n")

        result = migrate_flat_to_session(tmp_path, "SES-100")

        assert result is True
        session_dir = personal_dir / "sessions" / "SES-100"
        assert (session_dir / "state.yaml").exists()
        assert not flat_state.exists()

    def test_no_migration_when_no_flat_files(self, tmp_path: Path) -> None:
        """Returns False when no flat files exist."""
        from raise_cli.session.state import migrate_flat_to_session

        result = migrate_flat_to_session(tmp_path, "SES-100")
        assert result is False

    def test_no_migration_when_session_dir_exists(self, tmp_path: Path) -> None:
        """Skips migration if per-session dir already exists."""
        from raise_cli.session.state import migrate_flat_to_session

        personal_dir = tmp_path / ".raise" / "rai" / "personal"
        personal_dir.mkdir(parents=True)
        flat_state = personal_dir / "session-state.yaml"
        flat_state.write_text("current_work:\n  epic: E15\n")
        # Session dir already exists
        session_dir = personal_dir / "sessions" / "SES-100"
        session_dir.mkdir(parents=True)

        result = migrate_flat_to_session(tmp_path, "SES-100")

        assert result is False
        assert flat_state.exists(), "Should not touch flat files if session dir exists"

    def test_handles_empty_flat_files_gracefully(self, tmp_path: Path) -> None:
        """Handles empty flat files without error."""
        from raise_cli.session.state import migrate_flat_to_session

        personal_dir = tmp_path / ".raise" / "rai" / "personal"
        personal_dir.mkdir(parents=True)
        flat_state = personal_dir / "session-state.yaml"
        flat_state.write_text("")

        result = migrate_flat_to_session(tmp_path, "SES-100")

        assert result is True
        session_dir = personal_dir / "sessions" / "SES-100"
        assert (session_dir / "state.yaml").exists()

    def test_migrates_to_last_session_id_not_new_id(self, tmp_path: Path) -> None:
        """Migration target should be last_session.id from state, not the new session ID."""
        from raise_cli.session.state import migrate_flat_to_session

        personal_dir = tmp_path / ".raise" / "rai" / "personal"
        personal_dir.mkdir(parents=True)
        flat_state = personal_dir / "session-state.yaml"
        flat_state.write_text(
            "last_session:\n"
            "  id: SES-024\n"
            "  date: 2026-03-05\n"
            "  developer: Test\n"
            "  summary: previous session\n"
            "current_work:\n"
            "  epic: E15\n"
        )

        result = migrate_flat_to_session(tmp_path, "SES-025")

        assert result is True
        # State should be in SES-024's dir (the session it belongs to), not SES-025
        correct_dir = personal_dir / "sessions" / "SES-024"
        wrong_dir = personal_dir / "sessions" / "SES-025"
        assert (correct_dir / "state.yaml").exists()
        assert not wrong_dir.exists()

    def test_falls_back_to_passed_id_when_no_last_session(self, tmp_path: Path) -> None:
        """When flat state has no last_session.id, use the passed session_id."""
        from raise_cli.session.state import migrate_flat_to_session

        personal_dir = tmp_path / ".raise" / "rai" / "personal"
        personal_dir.mkdir(parents=True)
        flat_state = personal_dir / "session-state.yaml"
        flat_state.write_text("current_work:\n  epic: E15\n")

        result = migrate_flat_to_session(tmp_path, "SES-100")

        assert result is True
        session_dir = personal_dir / "sessions" / "SES-100"
        assert (session_dir / "state.yaml").exists()


class TestCleanupSessionDir:
    """Tests for cleanup_session_dir (RAISE-138)."""

    def test_removes_session_directory(self, tmp_path: Path) -> None:
        """Removes the per-session directory and all contents."""
        from raise_cli.session.state import cleanup_session_dir

        session_dir = tmp_path / ".raise" / "rai" / "personal" / "sessions" / "SES-100"
        session_dir.mkdir(parents=True)
        (session_dir / "state.yaml").write_text("test")
        (session_dir / "signals.jsonl").write_text("test")

        cleanup_session_dir(tmp_path, "SES-100")

        assert not session_dir.exists()

    def test_noop_when_dir_missing(self, tmp_path: Path) -> None:
        """No error when session directory doesn't exist."""
        from raise_cli.session.state import cleanup_session_dir

        # Should not raise
        cleanup_session_dir(tmp_path, "SES-NONEXISTENT")

    def test_does_not_remove_sibling_sessions(self, tmp_path: Path) -> None:
        """Cleanup of one session does not affect other sessions."""
        from raise_cli.session.state import cleanup_session_dir

        sessions_dir = tmp_path / ".raise" / "rai" / "personal" / "sessions"
        (sessions_dir / "SES-100").mkdir(parents=True)
        (sessions_dir / "SES-100" / "state.yaml").write_text("100")
        (sessions_dir / "SES-101").mkdir(parents=True)
        (sessions_dir / "SES-101" / "state.yaml").write_text("101")

        cleanup_session_dir(tmp_path, "SES-100")

        assert not (sessions_dir / "SES-100").exists()
        assert (sessions_dir / "SES-101").exists()
        assert (sessions_dir / "SES-101" / "state.yaml").read_text(
            encoding="utf-8"
        ) == "101"


class TestSaveSessionStateAdapter:
    """Tests for save_session_state using FilesystemAdapter (S1040.2 T2)."""

    def test_writes_via_adapter(self, tmp_path: Path) -> None:
        """save_session_state should delegate to FilesystemAdapter.write."""
        from unittest.mock import patch

        state = _make_session_state()

        with patch("raise_cli.session.state.FilesystemAdapter") as mock_adapter_cls:
            save_session_state(tmp_path, state)

            mock_adapter_cls.assert_called_once_with(root=tmp_path)
            mock_adapter_cls.return_value.write.assert_called_once()

    def test_stamps_last_modified(self, tmp_path: Path) -> None:
        """Saved state should contain a last_modified timestamp."""
        state = _make_session_state()
        save_session_state(tmp_path, state)

        loaded = load_session_state(tmp_path)
        assert loaded is not None
        assert loaded.last_modified is not None
        # Should be a valid ISO timestamp
        assert "T" in loaded.last_modified

    def test_first_write_succeeds(self, tmp_path: Path) -> None:
        """First write (no existing file) should succeed without errors."""
        state = _make_session_state()
        save_session_state(tmp_path, state)

        loaded = load_session_state(tmp_path)
        assert loaded is not None
        assert loaded.current_work.epic == "E15"

    def test_stale_overwrite_rejected(self, tmp_path: Path) -> None:
        """Write with older last_modified than on-disk should raise StaleWriteError."""
        state = _make_session_state()
        # First write - establishes on-disk timestamp
        save_session_state(tmp_path, state)

        loaded = load_session_state(tmp_path)
        assert loaded is not None
        assert loaded.last_modified is not None

        # Try to write with an older timestamp
        stale_state = state.model_copy(
            update={"last_modified": "2020-01-01T00:00:00+00:00"}
        )
        with pytest.raises(StaleWriteError) as exc_info:
            save_session_state(tmp_path, stale_state)

        assert exc_info.value.incoming_timestamp == "2020-01-01T00:00:00+00:00"
        assert exc_info.value.on_disk_timestamp == loaded.last_modified

    def test_fresh_write_succeeds_over_existing(self, tmp_path: Path) -> None:
        """Write with newer last_modified than on-disk should succeed."""
        state = _make_session_state()
        save_session_state(tmp_path, state)

        loaded = load_session_state(tmp_path)
        assert loaded is not None

        # Write with a future timestamp
        fresh_state = state.model_copy(
            update={"last_modified": "2099-12-31T23:59:59+00:00"}
        )
        save_session_state(tmp_path, fresh_state)

        reloaded = load_session_state(tmp_path)
        assert reloaded is not None
        # last_modified gets re-stamped by save, so it won't be the 2099 value
        assert reloaded.last_modified is not None

    def test_legacy_file_without_last_modified_succeeds(self, tmp_path: Path) -> None:
        """Write over a legacy file (no last_modified) should succeed."""
        # Manually create a legacy state file without last_modified
        state_path = tmp_path / ".raise" / "rai" / "personal" / "session-state.yaml"
        state_path.parent.mkdir(parents=True)
        legacy_data = _make_session_state().model_dump(mode="json")
        # Ensure no last_modified
        legacy_data.pop("last_modified", None)
        state_path.write_text(
            yaml.dump(legacy_data, default_flow_style=False),
            encoding="utf-8",
        )

        # Writing with last_modified=None should succeed (skip check)
        state = _make_session_state()
        save_session_state(tmp_path, state)

        loaded = load_session_state(tmp_path)
        assert loaded is not None
        assert loaded.last_modified is not None

    def test_stale_write_error_contains_path(self, tmp_path: Path) -> None:
        """StaleWriteError should include the file path."""
        state = _make_session_state()
        save_session_state(tmp_path, state)

        stale_state = state.model_copy(
            update={"last_modified": "2020-01-01T00:00:00+00:00"}
        )
        with pytest.raises(StaleWriteError) as exc_info:
            save_session_state(tmp_path, stale_state)

        assert exc_info.value.path is not None
        assert "session-state.yaml" in str(exc_info.value.path)
