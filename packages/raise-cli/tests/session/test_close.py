"""Tests for session close orchestrator."""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from raise_cli.onboarding.profile import DeveloperProfile
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
                {
                    "description": "Code as Gemba",
                    "context": "process,lean",
                    "type": "process",
                }
            ],
            "corrections": [{"what": "Skipped design", "lesson": "Always design"}],
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
        """Create a project with memory and personal directories."""
        project = tmp_path / "project"
        (project / ".raise" / "rai" / "memory" / "sessions").mkdir(parents=True)
        (project / ".raise" / "rai" / "personal" / "sessions").mkdir(parents=True)
        return project

    def test_records_session(self, tmp_path: Path, monkeypatch: object) -> None:
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
        self,
        tmp_path: Path,
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
                {
                    "description": "New pattern",
                    "type": "process",
                    "context": "test,dev",
                },
            ],
        )

        result = process_session_close(close_input, profile, project)

        assert result.patterns_added == 1
        # Verify pattern was written
        patterns_file = project / ".raise" / "rai" / "memory" / "patterns.jsonl"
        assert patterns_file.exists()
        mp.undo()

    def test_adds_corrections_to_profile(
        self,
        tmp_path: Path,
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
        self,
        tmp_path: Path,
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
        self,
        tmp_path: Path,
    ) -> None:
        """process_session_close clears current_session in profile."""
        import pytest

        mp = pytest.MonkeyPatch()
        rai_home = tmp_path / ".rai"
        mp.setattr("raise_cli.onboarding.profile.get_rai_home", lambda: rai_home)

        project = self._setup_project(tmp_path)
        profile = DeveloperProfile(name="Test")

        from raise_cli.onboarding.profile import save_developer_profile, start_session

        # Session ID must match what append_session will generate (SES-001 for first session)
        active, _ = start_session(
            profile, session_id="SES-001", project_path=str(project), agent="test"
        )
        save_developer_profile(active)

        close_input = CloseInput(summary="done")
        process_session_close(close_input, active, project)

        from raise_cli.onboarding.profile import load_developer_profile

        loaded = load_developer_profile()
        assert loaded is not None
        assert len(loaded.active_sessions) == 0  # Session removed
        mp.undo()


class TestProcessSessionClosePatternPrefix:
    """Tests for pattern prefix wiring in session close."""

    def _setup_project(self, tmp_path: Path) -> Path:
        """Create a project with memory and personal directories."""
        project = tmp_path / "project"
        (project / ".raise" / "rai" / "memory" / "sessions").mkdir(parents=True)
        (project / ".raise" / "rai" / "personal" / "sessions").mkdir(parents=True)
        return project

    def test_patterns_use_developer_prefix(self, tmp_path: Path) -> None:
        """Patterns added during close use developer's prefix."""
        import pytest

        mp = pytest.MonkeyPatch()
        rai_home = tmp_path / ".rai"
        mp.setattr("raise_cli.onboarding.profile.get_rai_home", lambda: rai_home)

        project = self._setup_project(tmp_path)
        profile = DeveloperProfile(name="Emilio", pattern_prefix="E")
        close_input = CloseInput(
            summary="test",
            patterns=[
                {"description": "Test pattern", "type": "process", "context": "test"},
            ],
        )

        result = process_session_close(close_input, profile, project)

        assert result.patterns_added == 1
        patterns_file = project / ".raise" / "rai" / "memory" / "patterns.jsonl"
        data = json.loads(patterns_file.read_text(encoding="utf-8").strip())
        assert data["id"].startswith("PAT-E-")
        mp.undo()

    def test_patterns_use_name_initial_without_explicit_prefix(
        self, tmp_path: Path
    ) -> None:
        """Without explicit prefix, uses first letter of name."""
        import pytest

        mp = pytest.MonkeyPatch()
        rai_home = tmp_path / ".rai"
        mp.setattr("raise_cli.onboarding.profile.get_rai_home", lambda: rai_home)

        project = self._setup_project(tmp_path)
        profile = DeveloperProfile(name="Fernando")
        close_input = CloseInput(
            summary="test",
            patterns=[
                {"description": "Fer pattern", "type": "process", "context": "test"},
            ],
        )

        result = process_session_close(close_input, profile, project)

        assert result.patterns_added == 1
        patterns_file = project / ".raise" / "rai" / "memory" / "patterns.jsonl"
        data = json.loads(patterns_file.read_text(encoding="utf-8").strip())
        assert data["id"].startswith("PAT-F-")
        mp.undo()


class TestProcessSessionClosePatternsCaptured:
    """Tests for patterns_captured in session state after close."""

    def _setup_project(self, tmp_path: Path) -> Path:
        """Create a project with memory and personal directories."""
        project = tmp_path / "project"
        (project / ".raise" / "rai" / "memory" / "sessions").mkdir(parents=True)
        (project / ".raise" / "rai" / "personal" / "sessions").mkdir(parents=True)
        return project

    def test_patterns_captured_contains_real_unique_ids(self, tmp_path: Path) -> None:
        """patterns_captured should list actual pattern IDs, not placeholders."""
        import pytest

        mp = pytest.MonkeyPatch()
        rai_home = tmp_path / ".rai"
        mp.setattr("raise_cli.onboarding.profile.get_rai_home", lambda: rai_home)

        project = self._setup_project(tmp_path)
        profile = DeveloperProfile(name="Emilio", pattern_prefix="E")
        close_input = CloseInput(
            summary="test",
            patterns=[
                {"description": "First pattern", "type": "process", "context": "a"},
                {"description": "Second pattern", "type": "technical", "context": "b"},
                {
                    "description": "Third pattern",
                    "type": "architecture",
                    "context": "c",
                },
            ],
        )

        process_session_close(close_input, profile, project)

        from raise_cli.session.state import load_session_state

        state = load_session_state(project)
        assert state is not None
        captured = state.last_session.patterns_captured
        # Should have 3 unique real IDs
        assert len(captured) == 3
        assert len(set(captured)) == 3  # all unique
        # Each should be a real pattern ID, not a placeholder
        for pid in captured:
            assert pid.startswith("PAT-E-"), f"Expected real ID, got {pid}"
        mp.undo()


class TestLoadStateFileCoaching:
    """Tests for load_state_file with coaching observations."""

    def test_loads_state_file_with_coaching(self, tmp_path: Path) -> None:
        """State file with coaching populates CloseInput.coaching."""
        data = {
            "summary": "coaching session",
            "coaching": {
                "trust_level": "developing",
                "strengths": ["design discipline", "structured thinking"],
                "growth_edge": "async patterns",
                "autonomy": "high within defined scope",
                "relationship": {"quality": "productive", "trajectory": "growing"},
                "communication_notes": ["prefers direct"],
            },
        }
        state_file = tmp_path / "state.yaml"
        state_file.write_text(yaml.dump(data))

        result = load_state_file(state_file)
        assert result.coaching is not None
        assert result.coaching["trust_level"] == "developing"
        assert result.coaching["strengths"] == [
            "design discipline",
            "structured thinking",
        ]

    def test_loads_state_file_without_coaching_defaults_none(
        self, tmp_path: Path
    ) -> None:
        """State file without coaching defaults to None."""
        state_file = tmp_path / "state.yaml"
        state_file.write_text("summary: no coaching\n")

        result = load_state_file(state_file)
        assert result.coaching is None


class TestProcessSessionCloseCoaching:
    """Tests for process_session_close updating coaching in profile."""

    def _setup_project(self, tmp_path: Path) -> Path:
        """Create a project with memory and personal directories."""
        project = tmp_path / "project"
        (project / ".raise" / "rai" / "memory" / "sessions").mkdir(parents=True)
        (project / ".raise" / "rai" / "personal" / "sessions").mkdir(parents=True)
        return project

    def test_close_updates_coaching_in_profile(
        self,
        tmp_path: Path,
    ) -> None:
        """process_session_close updates coaching fields in developer profile."""
        import pytest

        mp = pytest.MonkeyPatch()
        rai_home = tmp_path / ".rai"
        mp.setattr("raise_cli.onboarding.profile.get_rai_home", lambda: rai_home)

        project = self._setup_project(tmp_path)
        profile = DeveloperProfile(name="Test")
        close_input = CloseInput(
            summary="coaching test",
            coaching={
                "trust_level": "developing",
                "strengths": ["design", "testing"],
                "growth_edge": "async patterns",
            },
        )

        result = process_session_close(close_input, profile, project)

        assert "Coaching updated" in result.messages
        from raise_cli.onboarding.profile import load_developer_profile

        loaded = load_developer_profile()
        assert loaded is not None
        assert loaded.coaching.trust_level == "developing"
        assert loaded.coaching.strengths == ["design", "testing"]
        assert loaded.coaching.growth_edge == "async patterns"
        mp.undo()

    def test_close_updates_relationship_in_profile(
        self,
        tmp_path: Path,
    ) -> None:
        """process_session_close updates relationship state in profile."""
        import pytest

        mp = pytest.MonkeyPatch()
        rai_home = tmp_path / ".rai"
        mp.setattr("raise_cli.onboarding.profile.get_rai_home", lambda: rai_home)

        project = self._setup_project(tmp_path)
        profile = DeveloperProfile(name="Test")
        close_input = CloseInput(
            summary="relationship test",
            coaching={
                "relationship": {"quality": "productive", "trajectory": "growing"},
            },
        )

        process_session_close(close_input, profile, project)

        from raise_cli.onboarding.profile import load_developer_profile

        loaded = load_developer_profile()
        assert loaded is not None
        assert loaded.coaching.relationship.quality == "productive"
        assert loaded.coaching.relationship.trajectory == "growing"
        mp.undo()

    def test_close_without_coaching_leaves_defaults(
        self,
        tmp_path: Path,
    ) -> None:
        """process_session_close without coaching leaves profile defaults."""
        import pytest

        mp = pytest.MonkeyPatch()
        rai_home = tmp_path / ".rai"
        mp.setattr("raise_cli.onboarding.profile.get_rai_home", lambda: rai_home)

        project = self._setup_project(tmp_path)
        profile = DeveloperProfile(name="Test")
        close_input = CloseInput(summary="no coaching")

        result = process_session_close(close_input, profile, project)

        assert "Coaching updated" not in result.messages
        from raise_cli.onboarding.profile import load_developer_profile

        loaded = load_developer_profile()
        assert loaded is not None
        assert loaded.coaching.trust_level == "new"
        assert loaded.coaching.strengths == []
        mp.undo()

    def test_close_partial_coaching_preserves_existing(
        self,
        tmp_path: Path,
    ) -> None:
        """process_session_close with partial coaching preserves other fields."""
        import pytest

        from raise_cli.onboarding.profile import CoachingContext

        mp = pytest.MonkeyPatch()
        rai_home = tmp_path / ".rai"
        mp.setattr("raise_cli.onboarding.profile.get_rai_home", lambda: rai_home)

        project = self._setup_project(tmp_path)
        coaching = CoachingContext(strengths=["existing"], trust_level="developing")
        profile = DeveloperProfile(name="Test", coaching=coaching)

        close_input = CloseInput(
            summary="partial coaching",
            coaching={"growth_edge": "new edge"},
        )

        process_session_close(close_input, profile, project)

        from raise_cli.onboarding.profile import load_developer_profile

        loaded = load_developer_profile()
        assert loaded is not None
        assert loaded.coaching.strengths == ["existing"]
        assert loaded.coaching.trust_level == "developing"
        assert loaded.coaching.growth_edge == "new edge"
        mp.undo()


class TestLoadStateFileNarrative:
    """Tests for load_state_file with narrative field."""

    def test_loads_state_file_with_narrative(self, tmp_path: Path) -> None:
        """State file with narrative populates CloseInput.narrative."""
        data = {
            "summary": "narrative session",
            "narrative": "## Decisions\n- Chose sync model over adapters\n\n## Artifacts\n- adr-026.md created",
        }
        state_file = tmp_path / "state.yaml"
        state_file.write_text(yaml.dump(data))

        result = load_state_file(state_file)
        assert "sync model" in result.narrative

    def test_loads_state_file_without_narrative_defaults_empty(
        self,
        tmp_path: Path,
    ) -> None:
        """State file without narrative defaults to empty string."""
        state_file = tmp_path / "state.yaml"
        state_file.write_text("summary: no narrative\n")

        result = load_state_file(state_file)
        assert result.narrative == ""


class TestProcessSessionCloseNarrative:
    """Tests for process_session_close persisting narrative."""

    def _setup_project(self, tmp_path: Path) -> Path:
        """Create a project with memory and personal directories."""
        project = tmp_path / "project"
        (project / ".raise" / "rai" / "memory" / "sessions").mkdir(parents=True)
        (project / ".raise" / "rai" / "personal" / "sessions").mkdir(parents=True)
        return project

    def test_close_persists_narrative_in_session_state(
        self,
        tmp_path: Path,
    ) -> None:
        """process_session_close persists narrative in session-state.yaml."""
        import pytest

        mp = pytest.MonkeyPatch()
        rai_home = tmp_path / ".rai"
        mp.setattr("raise_cli.onboarding.profile.get_rai_home", lambda: rai_home)

        project = self._setup_project(tmp_path)
        profile = DeveloperProfile(name="Test")
        close_input = CloseInput(
            summary="narrative test",
            narrative="## Decisions\n- Chose sync model",
            current_work={
                "epic": "E21",
                "story": "S21.1",
                "phase": "implement",
                "branch": "epic/e21/platform",
            },
        )

        process_session_close(close_input, profile, project)

        from raise_cli.session.state import load_session_state

        state = load_session_state(project)
        assert state is not None
        assert "sync model" in state.narrative
        mp.undo()

    def test_close_without_narrative_defaults_empty(
        self,
        tmp_path: Path,
    ) -> None:
        """process_session_close without narrative leaves empty string."""
        import pytest

        mp = pytest.MonkeyPatch()
        rai_home = tmp_path / ".rai"
        mp.setattr("raise_cli.onboarding.profile.get_rai_home", lambda: rai_home)

        project = self._setup_project(tmp_path)
        profile = DeveloperProfile(name="Test")
        close_input = CloseInput(summary="no narrative")

        process_session_close(close_input, profile, project)

        from raise_cli.session.state import load_session_state

        state = load_session_state(project)
        assert state is not None
        assert state.narrative == ""
        mp.undo()


class TestProcessSessionCloseRelease:
    """Tests for session close persisting release field."""

    def _setup_project(self, tmp_path: Path) -> Path:
        """Create a project with memory and personal directories."""
        project = tmp_path / "project"
        (project / ".raise" / "rai" / "memory" / "sessions").mkdir(parents=True)
        (project / ".raise" / "rai" / "personal" / "sessions").mkdir(parents=True)
        return project

    def test_close_persists_release_in_session_state(
        self,
        tmp_path: Path,
    ) -> None:
        """process_session_close persists release field in session-state.yaml."""
        import pytest

        mp = pytest.MonkeyPatch()
        rai_home = tmp_path / ".rai"
        mp.setattr("raise_cli.onboarding.profile.get_rai_home", lambda: rai_home)

        project = self._setup_project(tmp_path)
        profile = DeveloperProfile(name="Test")
        close_input = CloseInput(
            summary="release wiring test",
            current_work={
                "release": "V3.0",
                "epic": "E19",
                "story": "S19.3",
                "phase": "implement",
                "branch": "epic/e19/v3",
            },
        )

        process_session_close(close_input, profile, project)

        from raise_cli.session.state import load_session_state

        state = load_session_state(project)
        assert state is not None
        assert state.current_work.release == "V3.0"
        assert state.current_work.epic == "E19"
        mp.undo()

    def test_close_without_release_defaults_empty(
        self,
        tmp_path: Path,
    ) -> None:
        """process_session_close without release defaults to empty string."""
        import pytest

        mp = pytest.MonkeyPatch()
        rai_home = tmp_path / ".rai"
        mp.setattr("raise_cli.onboarding.profile.get_rai_home", lambda: rai_home)

        project = self._setup_project(tmp_path)
        profile = DeveloperProfile(name="Test")
        close_input = CloseInput(
            summary="no release test",
            current_work={
                "epic": "E15",
                "story": "S15.7",
                "phase": "implement",
                "branch": "story/s15.7/x",
            },
        )

        process_session_close(close_input, profile, project)

        from raise_cli.session.state import load_session_state

        state = load_session_state(project)
        assert state is not None
        assert state.current_work.release == ""
        mp.undo()


class TestLoadStateFileNextSessionPrompt:
    """Tests for load_state_file with next_session_prompt field."""

    def test_loads_state_file_with_next_session_prompt(self, tmp_path: Path) -> None:
        """State file with next_session_prompt populates CloseInput."""
        data = {
            "summary": "prompt session",
            "next_session_prompt": "Verify encoding fix covers discovery tests. Emilio interested in backlog abstraction.",
        }
        state_file = tmp_path / "state.yaml"
        state_file.write_text(yaml.dump(data))

        result = load_state_file(state_file)
        assert "encoding fix" in result.next_session_prompt

    def test_loads_state_file_without_next_session_prompt_defaults_empty(
        self,
        tmp_path: Path,
    ) -> None:
        """State file without next_session_prompt defaults to empty string."""
        state_file = tmp_path / "state.yaml"
        state_file.write_text("summary: no prompt\n")

        result = load_state_file(state_file)
        assert result.next_session_prompt == ""


class TestProcessSessionCloseNextSessionPrompt:
    """Tests for process_session_close persisting next_session_prompt."""

    def _setup_project(self, tmp_path: Path) -> Path:
        """Create a project with memory and personal directories."""
        project = tmp_path / "project"
        (project / ".raise" / "rai" / "memory" / "sessions").mkdir(parents=True)
        (project / ".raise" / "rai" / "personal" / "sessions").mkdir(parents=True)
        return project

    def test_close_persists_next_session_prompt_in_session_state(
        self,
        tmp_path: Path,
    ) -> None:
        """process_session_close persists next_session_prompt in session-state.yaml."""
        import pytest

        mp = pytest.MonkeyPatch()
        rai_home = tmp_path / ".rai"
        mp.setattr("raise_cli.onboarding.profile.get_rai_home", lambda: rai_home)

        project = self._setup_project(tmp_path)
        profile = DeveloperProfile(name="Test")
        close_input = CloseInput(
            summary="prompt test",
            next_session_prompt="Check encoding in discovery tests next session.",
            current_work={
                "epic": "RAISE-144",
                "story": "",
                "phase": "",
                "branch": "v2",
            },
        )

        process_session_close(close_input, profile, project)

        from raise_cli.session.state import load_session_state

        state = load_session_state(project)
        assert state is not None
        assert "encoding" in state.next_session_prompt

        mp.undo()

    def test_close_without_next_session_prompt_defaults_empty(
        self,
        tmp_path: Path,
    ) -> None:
        """process_session_close without next_session_prompt leaves empty string."""
        import pytest

        mp = pytest.MonkeyPatch()
        rai_home = tmp_path / ".rai"
        mp.setattr("raise_cli.onboarding.profile.get_rai_home", lambda: rai_home)

        project = self._setup_project(tmp_path)
        profile = DeveloperProfile(name="Test")
        close_input = CloseInput(summary="no prompt")

        process_session_close(close_input, profile, project)

        from raise_cli.session.state import load_session_state

        state = load_session_state(project)
        assert state is not None
        assert state.next_session_prompt == ""

        mp.undo()


class TestLoadStateFileSessionId:
    """Tests for load_state_file with session_id field (RAISE-201)."""

    def test_loads_state_file_with_session_id(self, tmp_path: Path) -> None:
        """State file with session_id populates CloseInput.session_id."""
        data = {
            "session_id": "SES-219",
            "summary": "session with id",
            "type": "feature",
        }
        state_file = tmp_path / "state.yaml"
        state_file.write_text(yaml.dump(data))

        result = load_state_file(state_file)
        assert result.session_id == "SES-219"

    def test_loads_state_file_without_session_id_defaults_empty(
        self,
        tmp_path: Path,
    ) -> None:
        """State file without session_id defaults to empty string."""
        state_file = tmp_path / "state.yaml"
        state_file.write_text("summary: no session id\n")

        result = load_state_file(state_file)
        assert result.session_id == ""


class TestLoadStateFileProgress:
    """Tests for load_state_file with progress and completed_epics."""

    def test_loads_state_file_with_progress(self, tmp_path: Path) -> None:
        """State file with progress populates CloseInput.progress."""
        data = {
            "summary": "E15 progress session",
            "progress": {
                "epic": "E15",
                "stories_done": 5,
                "stories_total": 8,
                "sp_done": 15,
                "sp_total": 24,
            },
        }
        state_file = tmp_path / "state.yaml"
        state_file.write_text(yaml.dump(data))

        result = load_state_file(state_file)
        assert result.progress is not None
        assert result.progress["epic"] == "E15"
        assert result.progress["stories_done"] == 5
        assert result.progress["sp_total"] == 24

    def test_loads_state_file_with_completed_epics(self, tmp_path: Path) -> None:
        """State file with completed_epics populates CloseInput."""
        data = {
            "summary": "Final epic session",
            "completed_epics": ["E12", "E13", "E14"],
        }
        state_file = tmp_path / "state.yaml"
        state_file.write_text(yaml.dump(data))

        result = load_state_file(state_file)
        assert result.completed_epics == ["E12", "E13", "E14"]

    def test_loads_state_file_without_progress_defaults(self, tmp_path: Path) -> None:
        """State file without progress defaults to None/empty."""
        state_file = tmp_path / "state.yaml"
        state_file.write_text("summary: no progress\n")

        result = load_state_file(state_file)
        assert result.progress is None
        assert result.completed_epics == []


class TestProcessSessionCloseProgress:
    """Tests for process_session_close writing progress to session state."""

    def _setup_project(self, tmp_path: Path) -> Path:
        """Create a project with memory and personal directories."""
        project = tmp_path / "project"
        (project / ".raise" / "rai" / "memory" / "sessions").mkdir(parents=True)
        (project / ".raise" / "rai" / "personal" / "sessions").mkdir(parents=True)
        return project

    def test_close_writes_progress_to_session_state(
        self,
        tmp_path: Path,
    ) -> None:
        """process_session_close writes progress to session-state.yaml."""
        import pytest

        mp = pytest.MonkeyPatch()
        rai_home = tmp_path / ".rai"
        mp.setattr("raise_cli.onboarding.profile.get_rai_home", lambda: rai_home)

        project = self._setup_project(tmp_path)
        profile = DeveloperProfile(name="Test")
        close_input = CloseInput(
            summary="progress test",
            progress={
                "epic": "E15",
                "stories_done": 3,
                "stories_total": 8,
                "sp_done": 10,
                "sp_total": 24,
            },
        )

        process_session_close(close_input, profile, project)

        from raise_cli.session.state import load_session_state

        state = load_session_state(project)
        assert state is not None
        assert state.progress is not None
        assert state.progress.epic == "E15"
        assert state.progress.stories_done == 3
        assert state.progress.sp_total == 24
        mp.undo()

    def test_close_writes_completed_epics_to_session_state(
        self,
        tmp_path: Path,
    ) -> None:
        """process_session_close writes completed_epics to session-state.yaml."""
        import pytest

        mp = pytest.MonkeyPatch()
        rai_home = tmp_path / ".rai"
        mp.setattr("raise_cli.onboarding.profile.get_rai_home", lambda: rai_home)

        project = self._setup_project(tmp_path)
        profile = DeveloperProfile(name="Test")
        close_input = CloseInput(
            summary="epics done",
            completed_epics=["E12", "E14"],
        )

        process_session_close(close_input, profile, project)

        from raise_cli.session.state import load_session_state

        state = load_session_state(project)
        assert state is not None
        assert state.completed_epics == ["E12", "E14"]
        mp.undo()

    def test_close_without_progress_leaves_none(
        self,
        tmp_path: Path,
    ) -> None:
        """process_session_close without progress leaves state.progress as None."""
        import pytest

        mp = pytest.MonkeyPatch()
        rai_home = tmp_path / ".rai"
        mp.setattr("raise_cli.onboarding.profile.get_rai_home", lambda: rai_home)

        project = self._setup_project(tmp_path)
        profile = DeveloperProfile(name="Test")
        close_input = CloseInput(summary="no progress")

        process_session_close(close_input, profile, project)

        from raise_cli.session.state import load_session_state

        state = load_session_state(project)
        assert state is not None
        assert state.progress is None
        assert state.completed_epics == []
        mp.undo()


class TestProcessSessionCloseRemovesActiveSession:
    """Regression tests for RAISE-327 and RAISE-155."""

    def _setup_project(self, tmp_path: Path) -> Path:
        project = tmp_path / "project"
        (project / ".raise" / "rai" / "memory" / "sessions").mkdir(parents=True)
        (project / ".raise" / "rai" / "personal" / "sessions").mkdir(parents=True)
        return project

    def test_close_removes_session_with_divergent_id(self, tmp_path: Path) -> None:
        """RAISE-327: close must use active session_id, not append_session's new ID."""
        import pytest

        mp = pytest.MonkeyPatch()
        rai_home = tmp_path / ".rai"
        mp.setattr("raise_cli.onboarding.profile.get_rai_home", lambda: rai_home)

        project = self._setup_project(tmp_path)
        profile = DeveloperProfile(name="Test")

        from raise_cli.onboarding.profile import save_developer_profile, start_session

        # Start a session — gets a real session_id like SES-177
        active_session_id = "SES-177"
        active, _ = start_session(
            profile,
            session_id=active_session_id,
            project_path=str(project),
            agent="test",
        )
        save_developer_profile(active)
        assert len(active.active_sessions) == 1

        # Pre-populate some sessions so append_session generates SES-003 (not SES-177)
        index_file = (
            project / ".raise" / "rai" / "personal" / "sessions" / "index.jsonl"
        )
        index_file.write_text('{"id":"SES-001"}\n{"id":"SES-002"}\n')

        close_input = CloseInput(summary="done")
        # Pass the actual active session_id
        process_session_close(
            close_input, active, project, session_id=active_session_id
        )

        from raise_cli.onboarding.profile import load_developer_profile

        loaded = load_developer_profile()
        assert loaded is not None
        assert len(loaded.active_sessions) == 0, (
            f"Session {active_session_id} should have been removed but "
            f"active_sessions still has: {[s.session_id for s in loaded.active_sessions]}"
        )
        mp.undo()

    def test_start_session_is_idempotent_per_project(self, tmp_path: Path) -> None:
        """RAISE-155: starting twice for same project should not duplicate entries."""
        import pytest

        mp = pytest.MonkeyPatch()
        rai_home = tmp_path / ".rai"
        mp.setattr("raise_cli.onboarding.profile.get_rai_home", lambda: rai_home)

        from raise_cli.onboarding.profile import start_session

        profile = DeveloperProfile(name="Test")
        project_path = str(tmp_path / "project")

        # Start same project twice
        updated1, _ = start_session(
            profile, session_id="SES-1", project_path=project_path, agent="test"
        )
        updated2, _ = start_session(
            updated1, session_id="SES-2", project_path=project_path, agent="test"
        )

        assert len(updated2.active_sessions) == 1, (
            f"Expected 1 session but got {len(updated2.active_sessions)}: "
            f"{[s.session_id for s in updated2.active_sessions]}"
        )
        # Should keep the newer session
        assert updated2.active_sessions[0].session_id == "SES-2"
        mp.undo()
