"""Tests for session close orchestrator."""

from __future__ import annotations

from pathlib import Path

import yaml

from raise_cli.onboarding.profile import DeveloperProfile, ExperienceLevel
from raise_cli.session.close import CloseInput, load_state_file, process_session_close


class TestLoadStateFile:
    """Tests for load_state_file."""

    def test_loads_minimal_state_file(self, tmp_path: Path) -> None:
        """Loads a minimal state file with just summary."""
        state_file = tmp_path / "state.yaml"
        state_file.write_text("summary: test session\ntype: feature\n")

        result = load_state_file(state_file)
        assert result.summary == "test session"
        assert result.session_type == "feature"

    def test_loads_full_state_file(self, tmp_path: Path) -> None:
        """Loads a full state file with all fields."""
        data = {
            "summary": "Session protocol design",
            "type": "feature",
            "outcomes": ["S15.7 scope committed"],
            "patterns": [
                {"description": "Code as Gemba", "context": "process,lean", "type": "process"}
            ],
            "corrections": [
                {"what": "Skipped design", "lesson": "Always design"}
            ],
            "current_work": {
                "epic": "E15",
                "story": "S15.7",
                "phase": "design",
                "branch": "story/s15.7/session-protocol",
            },
            "pending": {
                "decisions": ["Pattern curation"],
                "next_actions": ["Implement schema"],
            },
            "notes": "ADR-024 created",
        }
        state_file = tmp_path / "state.yaml"
        state_file.write_text(yaml.dump(data))

        result = load_state_file(state_file)
        assert result.summary == "Session protocol design"
        assert len(result.patterns) == 1
        assert len(result.corrections) == 1
        assert result.current_work is not None
        assert result.current_work["epic"] == "E15"
        assert result.notes == "ADR-024 created"

    def test_defaults_for_missing_fields(self, tmp_path: Path) -> None:
        """Missing optional fields default to empty."""
        state_file = tmp_path / "state.yaml"
        state_file.write_text("summary: minimal\n")

        result = load_state_file(state_file)
        assert result.patterns == []
        assert result.corrections == []
        assert result.current_work is None


class TestProcessSessionClose:
    """Tests for process_session_close."""

    def _setup_project(self, tmp_path: Path) -> Path:
        """Create a project with memory directory."""
        project = tmp_path / "project"
        memory_dir = project / ".raise" / "rai" / "memory" / "sessions"
        memory_dir.mkdir(parents=True)
        return project

    def test_records_session(
        self, tmp_path: Path, monkeypatch: "object"
    ) -> None:
        """process_session_close records session in index.jsonl."""
        import pytest

        mp = pytest.MonkeyPatch()
        rai_home = tmp_path / ".rai"
        mp.setattr("raise_cli.onboarding.profile.get_rai_home", lambda: rai_home)

        project = self._setup_project(tmp_path)
        profile = DeveloperProfile(name="Test")
        close_input = CloseInput(summary="test session", session_type="feature")

        result = process_session_close(close_input, profile, project)

        assert result.success
        assert result.session_id.startswith("SES-")
        assert "Session" in result.messages[0]
        mp.undo()

    def test_adds_patterns(
        self, tmp_path: Path,
    ) -> None:
        """process_session_close appends patterns to patterns.jsonl."""
        import pytest

        mp = pytest.MonkeyPatch()
        rai_home = tmp_path / ".rai"
        mp.setattr("raise_cli.onboarding.profile.get_rai_home", lambda: rai_home)

        project = self._setup_project(tmp_path)
        profile = DeveloperProfile(name="Test")
        close_input = CloseInput(
            summary="test",
            patterns=[
                {"description": "New pattern", "type": "process", "context": "test,dev"},
            ],
        )

        result = process_session_close(close_input, profile, project)

        assert result.patterns_added == 1
        # Verify pattern was written
        patterns_file = project / ".raise" / "rai" / "memory" / "patterns.jsonl"
        assert patterns_file.exists()
        mp.undo()

    def test_adds_corrections_to_profile(
        self, tmp_path: Path,
    ) -> None:
        """process_session_close adds corrections to developer profile."""
        import pytest

        mp = pytest.MonkeyPatch()
        rai_home = tmp_path / ".rai"
        mp.setattr("raise_cli.onboarding.profile.get_rai_home", lambda: rai_home)

        project = self._setup_project(tmp_path)
        profile = DeveloperProfile(name="Test")
        close_input = CloseInput(
            summary="test",
            corrections=[
                {"what": "Skipped design", "lesson": "Always design"},
            ],
        )

        result = process_session_close(close_input, profile, project)

        assert result.corrections_added == 1
        # Verify profile was saved with correction
        from raise_cli.onboarding.profile import load_developer_profile

        loaded = load_developer_profile()
        assert loaded is not None
        assert len(loaded.coaching.corrections) == 1
        assert loaded.coaching.corrections[0].what == "Skipped design"
        mp.undo()

    def test_writes_session_state(
        self, tmp_path: Path,
    ) -> None:
        """process_session_close writes session-state.yaml."""
        import pytest

        mp = pytest.MonkeyPatch()
        rai_home = tmp_path / ".rai"
        mp.setattr("raise_cli.onboarding.profile.get_rai_home", lambda: rai_home)

        project = self._setup_project(tmp_path)
        profile = DeveloperProfile(name="Test")
        close_input = CloseInput(
            summary="test session",
            current_work={
                "epic": "E15",
                "story": "S15.7",
                "phase": "implement",
                "branch": "story/s15.7/x",
            },
            pending={
                "next_actions": ["Continue implementing"],
            },
        )

        process_session_close(close_input, profile, project)

        # Verify session state was written
        from raise_cli.session.state import load_session_state

        state = load_session_state(project)
        assert state is not None
        assert state.current_work.epic == "E15"
        assert state.last_session.summary == "test session"
        assert "Continue implementing" in state.pending.next_actions
        mp.undo()

    def test_clears_current_session(
        self, tmp_path: Path,
    ) -> None:
        """process_session_close clears current_session in profile."""
        import pytest

        mp = pytest.MonkeyPatch()
        rai_home = tmp_path / ".rai"
        mp.setattr("raise_cli.onboarding.profile.get_rai_home", lambda: rai_home)

        project = self._setup_project(tmp_path)
        profile = DeveloperProfile(name="Test")

        from raise_cli.onboarding.profile import save_developer_profile, start_session

        active = start_session(profile, str(project))
        save_developer_profile(active)

        close_input = CloseInput(summary="done")
        process_session_close(close_input, active, project)

        from raise_cli.onboarding.profile import load_developer_profile

        loaded = load_developer_profile()
        assert loaded is not None
        assert loaded.current_session is None
        mp.undo()
