"""Tests for session state schema and persistence."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from rai_cli.schemas.session_state import (
    CurrentWork,
    LastSession,
    PendingItems,
    SessionState,
)
from rai_cli.session.state import (
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

    def test_current_work_valid(self) -> None:
        """CurrentWork accepts all required fields."""
        work = CurrentWork(
            epic="E15", story="S15.7", phase="design", branch="story/s15.7/x"
        )
        assert work.epic == "E15"
        assert work.story == "S15.7"

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

    def test_session_state_full(self) -> None:
        """SessionState accepts all fields including notes."""
        state = _make_session_state()
        assert state.current_work.epic == "E15"
        assert state.last_session.id == "SES-097"
        assert len(state.pending.next_actions) == 1
        assert state.notes == "ADR-024 created."


class TestGetSessionStatePath:
    """Tests for get_session_state_path."""

    def test_returns_personal_path(self, tmp_path: Path) -> None:
        """Path is project_root/.raise/rai/personal/session-state.yaml."""
        path = get_session_state_path(tmp_path)
        assert path == tmp_path / ".raise" / "rai" / "personal" / "session-state.yaml"


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
        data = yaml.safe_load(state_path.read_text())
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
        assert loaded.last_session.patterns_captured == original.last_session.patterns_captured
        assert loaded.pending.decisions == original.pending.decisions
        assert loaded.pending.next_actions == original.pending.next_actions
        assert loaded.notes == original.notes
