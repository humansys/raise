"""Tests for raise session commands."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from raise_cli.cli.main import app
from raise_cli.onboarding.profile import ActiveSession, DeveloperProfile
from raise_cli.session.close import CloseResult

runner = CliRunner()


class TestSessionStart:
    """Tests for raise session start command."""

    def test_start_first_time_requires_name(self) -> None:
        """First-time user without --name should get helpful error."""
        with patch(
            "raise_cli.cli.commands.session.load_developer_profile", return_value=None
        ):
            result = runner.invoke(app, ["session", "start"])

        assert result.exit_code != 0
        assert "No developer profile found" in result.output
        assert "--name" in result.output

    def test_start_first_time_with_name_creates_profile(self, tmp_path: Path) -> None:
        """First-time user with --name creates profile and starts session."""
        rai_home = tmp_path / ".rai"
        rai_home.mkdir(parents=True)

        with (
            patch(
                "raise_cli.cli.commands.session.load_developer_profile",
                return_value=None,
            ),
            patch("raise_cli.cli.commands.session.save_developer_profile") as mock_save,
        ):
            result = runner.invoke(app, ["session", "start", "--name", "Alice"])

        assert result.exit_code == 0
        assert "Welcome to RaiSE, Alice" in result.output
        assert "Session recorded" in result.output
        mock_save.assert_called_once()

    def test_start_existing_profile_updates_metadata(self) -> None:
        """Existing user starts session, metadata updates."""
        profile = DeveloperProfile(name="Bob")

        with (
            patch(
                "raise_cli.cli.commands.session.load_developer_profile",
                return_value=profile,
            ),
            patch("raise_cli.cli.commands.session.save_developer_profile") as mock_save,
        ):
            result = runner.invoke(app, ["session", "start"])

        assert result.exit_code == 0
        assert "Session recorded" in result.output
        mock_save.assert_called_once()

    def test_start_with_project_path(self, tmp_path: Path) -> None:
        """Session start with --project associates project."""
        profile = DeveloperProfile(name="Carol")
        project_path = tmp_path / "my-project"
        project_path.mkdir()

        with (
            patch(
                "raise_cli.cli.commands.session.load_developer_profile",
                return_value=profile,
            ),
            patch("raise_cli.cli.commands.session.save_developer_profile") as mock_save,
        ):
            result = runner.invoke(
                app, ["session", "start", "--project", str(project_path)]
            )

        assert result.exit_code == 0
        assert "Session recorded" in result.output
        mock_save.assert_called_once()
        saved_profile = mock_save.call_args[0][0]
        assert len(saved_profile.active_sessions) == 1
        assert saved_profile.active_sessions[0].project == str(project_path)
        assert "S-C-" in result.output  # New-format session ID displayed (C for Carol)

    def test_start_warns_on_stale_session(self, tmp_path: Path) -> None:
        """Starting when stale session exists warns user."""
        from datetime import UTC, datetime, timedelta

        from raise_cli.onboarding.profile import ActiveSession

        project_path = tmp_path / "test-project"
        project_path.mkdir()

        stale_session = ActiveSession(
            session_id="SES-OLD",
            started_at=datetime.now(UTC) - timedelta(days=2),
            project="/old/project",
            agent="old-agent",
        )
        profile = DeveloperProfile(name="Dave", active_sessions=[stale_session])

        with (
            patch(
                "raise_cli.cli.commands.session.load_developer_profile",
                return_value=profile,
            ),
            patch("raise_cli.cli.commands.session.save_developer_profile"),
        ):
            result = runner.invoke(
                app, ["session", "start", "--project", str(project_path)]
            )

        assert result.exit_code == 0
        assert "Stale sessions detected" in result.output
        assert "SES-OLD" in result.output

    def test_start_allows_multiple_sessions(self) -> None:
        """Starting when recent session exists allows it (multi-session support)."""
        from datetime import UTC, datetime

        existing_session = ActiveSession(
            session_id="SES-001",
            started_at=datetime.now(UTC),
            project="/current/project",
            agent="existing-agent",
        )
        profile = DeveloperProfile(name="Eve", active_sessions=[existing_session])

        with (
            patch(
                "raise_cli.cli.commands.session.load_developer_profile",
                return_value=profile,
            ),
            patch("raise_cli.cli.commands.session.save_developer_profile"),
        ):
            result = runner.invoke(app, ["session", "start"])

        assert result.exit_code == 0
        # No warning for fresh sessions - multi-session support allows concurrent sessions
        assert "Warning" not in result.output

    def test_start_context_outputs_bundle(self, tmp_path: Path) -> None:
        """Session start --context outputs context bundle."""
        profile = DeveloperProfile(name="Hank")

        with (
            patch(
                "raise_cli.cli.commands.session.load_developer_profile",
                return_value=profile,
            ),
            patch("raise_cli.cli.commands.session.save_developer_profile"),
            patch(
                "raise_cli.cli.commands.session.assemble_context_bundle",
                return_value="# Session Context\nDeveloper: Hank (shu)",
            ),
            patch(
                "raise_cli.cli.commands.session.load_session_state",
                return_value=None,
            ),
        ):
            result = runner.invoke(
                app,
                ["session", "start", "--project", str(tmp_path), "--context"],
            )

        assert result.exit_code == 0
        assert "# Session Context" in result.output
        assert "Developer: Hank (shu)" in result.output
        # Should NOT show "Session recorded" when --context is used
        assert "Session recorded" not in result.output

    def test_start_context_without_project_falls_back(self) -> None:
        """Session start --context without --project falls back to default."""
        profile = DeveloperProfile(name="Ivy")

        with (
            patch(
                "raise_cli.cli.commands.session.load_developer_profile",
                return_value=profile,
            ),
            patch("raise_cli.cli.commands.session.save_developer_profile"),
        ):
            result = runner.invoke(app, ["session", "start", "--context"])

        assert result.exit_code == 0
        # Without --project, falls back to "Session recorded"
        assert "Session recorded" in result.output

    def test_start_without_context_preserves_behavior(self) -> None:
        """Session start without --context preserves existing behavior."""
        profile = DeveloperProfile(name="Jack")

        with (
            patch(
                "raise_cli.cli.commands.session.load_developer_profile",
                return_value=profile,
            ),
            patch("raise_cli.cli.commands.session.save_developer_profile"),
        ):
            result = runner.invoke(app, ["session", "start"])

        assert result.exit_code == 0
        assert "Session recorded" in result.output

    def test_start_help_shows_context_option(self) -> None:
        """Session start --help shows --context option."""
        result = runner.invoke(app, ["session", "start", "--help"])
        assert result.exit_code == 0
        assert "--context" in result.output


class TestSessionClose:
    """Tests for raise session close command."""

    def test_close_no_profile_errors(self) -> None:
        """Close without profile gives error."""
        with patch(
            "raise_cli.cli.commands.session.load_developer_profile", return_value=None
        ):
            result = runner.invoke(app, ["session", "close"])

        assert result.exit_code != 0
        assert "No developer profile found" in result.output

    def test_close_no_active_session_is_noop(self) -> None:
        """Close when no active session is informational no-op."""
        profile = DeveloperProfile(name="Frank", active_sessions=[])

        with patch(
            "raise_cli.cli.commands.session.load_developer_profile",
            return_value=profile,
        ):
            result = runner.invoke(app, ["session", "close"])

        assert result.exit_code == 0
        assert "No active session to close" in result.output

    def test_close_active_session_removes_from_list(self, tmp_path: Path) -> None:
        """Close with active session removes it from active_sessions."""
        from datetime import UTC, datetime

        project = tmp_path / "project"
        project.mkdir()

        active_session = ActiveSession(
            session_id="SES-100",
            started_at=datetime.now(UTC),
            project=str(project),
            agent="test-agent",
        )
        profile = DeveloperProfile(name="Grace", active_sessions=[active_session])

        with (
            patch(
                "raise_cli.cli.commands.session.load_developer_profile",
                return_value=profile,
            ),
            patch("raise_cli.cli.commands.session.save_developer_profile") as mock_save,
        ):
            result = runner.invoke(app, ["session", "close", "--project", str(project)])

        assert result.exit_code == 0
        assert "Session SES-100 closed" in result.output
        mock_save.assert_called_once()
        saved_profile = mock_save.call_args[0][0]
        assert len(saved_profile.active_sessions) == 0

    def test_close_structured_with_summary(self) -> None:
        """Close with --summary triggers structured close."""
        profile = DeveloperProfile(name="Henry")
        close_result = CloseResult(
            success=True,
            session_id="SES-098",
            patterns_added=0,
            corrections_added=0,
        )

        with (
            patch(
                "raise_cli.cli.commands.session.load_developer_profile",
                return_value=profile,
            ),
            patch(
                "raise_cli.cli.commands.session.process_session_close",
                return_value=close_result,
            ),
        ):
            result = runner.invoke(
                app,
                ["session", "close", "--summary", "test session", "--type", "feature"],
            )

        assert result.exit_code == 0
        assert "SES-098 closed" in result.output

    def test_close_structured_with_state_file(self, tmp_path: Path) -> None:
        """Close with --state-file reads from file."""
        profile = DeveloperProfile(name="Iris")
        state_file = tmp_path / "state.yaml"
        state_file.write_text("summary: from file\ntype: research\n")
        close_result = CloseResult(
            success=True,
            session_id="SES-099",
            patterns_added=1,
            corrections_added=0,
        )

        with (
            patch(
                "raise_cli.cli.commands.session.load_developer_profile",
                return_value=profile,
            ),
            patch(
                "raise_cli.cli.commands.session.process_session_close",
                return_value=close_result,
            ) as mock_close,
        ):
            result = runner.invoke(
                app,
                [
                    "session",
                    "close",
                    "--state-file",
                    str(state_file),
                    "--project",
                    str(tmp_path),
                ],
            )

        assert result.exit_code == 0
        assert "SES-099 closed" in result.output
        assert "Patterns added: 1" in result.output
        # Verify the close input was populated from file
        call_args = mock_close.call_args
        close_input = call_args[0][0]
        assert close_input.summary == "from file"

    def test_close_structured_with_pattern_and_correction(self) -> None:
        """Close with --pattern and --correction flags."""
        profile = DeveloperProfile(name="Jane")
        close_result = CloseResult(
            success=True,
            session_id="SES-100",
            patterns_added=1,
            corrections_added=1,
        )

        with (
            patch(
                "raise_cli.cli.commands.session.load_developer_profile",
                return_value=profile,
            ),
            patch(
                "raise_cli.cli.commands.session.process_session_close",
                return_value=close_result,
            ) as mock_close,
        ):
            result = runner.invoke(
                app,
                [
                    "session",
                    "close",
                    "--summary",
                    "test",
                    "--pattern",
                    "New pattern discovered",
                    "--correction",
                    "Skipped design",
                    "--correction-lesson",
                    "Always design",
                ],
            )

        assert result.exit_code == 0
        assert "Patterns added: 1" in result.output
        assert "Corrections recorded: 1" in result.output
        call_args = mock_close.call_args
        close_input = call_args[0][0]
        assert len(close_input.patterns) == 1
        assert len(close_input.corrections) == 1

    def test_close_state_file_passes_progress(self, tmp_path: Path) -> None:
        """Close with --state-file passes progress to process_session_close."""
        import yaml

        profile = DeveloperProfile(name="Kay")
        data = {
            "summary": "progress session",
            "progress": {
                "epic": "E15",
                "stories_done": 5,
                "stories_total": 8,
                "sp_done": 15,
                "sp_total": 24,
            },
            "completed_epics": ["E12", "E14"],
        }
        state_file = tmp_path / "state.yaml"
        state_file.write_text(yaml.dump(data))
        close_result = CloseResult(
            success=True,
            session_id="SES-101",
            patterns_added=0,
            corrections_added=0,
        )

        with (
            patch(
                "raise_cli.cli.commands.session.load_developer_profile",
                return_value=profile,
            ),
            patch(
                "raise_cli.cli.commands.session.process_session_close",
                return_value=close_result,
            ) as mock_close,
        ):
            result = runner.invoke(
                app,
                [
                    "session",
                    "close",
                    "--state-file",
                    str(state_file),
                    "--project",
                    str(tmp_path),
                ],
            )

        assert result.exit_code == 0
        assert "SES-101 closed" in result.output
        call_args = mock_close.call_args
        close_input = call_args[0][0]
        assert close_input.progress is not None
        assert close_input.progress["epic"] == "E15"
        assert close_input.completed_epics == ["E12", "E14"]

    def test_close_cleanup_session_dir(self, tmp_path: Path) -> None:
        """Session close removes per-session directory after close."""
        from datetime import UTC, datetime

        profile = DeveloperProfile(
            name="Test",
            active_sessions=[
                ActiveSession(
                    session_id="SES-050",
                    started_at=datetime.now(UTC),
                    project=str(tmp_path),
                    agent="test",
                ),
            ],
        )

        # Create per-session directory (simulating what start would create)
        session_dir = tmp_path / ".raise" / "rai" / "personal" / "sessions" / "SES-050"
        session_dir.mkdir(parents=True)
        (session_dir / "state.yaml").write_text("current_work: {}")
        (session_dir / "signals.jsonl").write_text("{}")

        close_result = CloseResult(
            success=True,
            session_id="SES-050",
            patterns_added=0,
            corrections_added=0,
        )

        with (
            patch(
                "raise_cli.cli.commands.session.load_developer_profile",
                return_value=profile,
            ),
            patch(
                "raise_cli.cli.commands.session.process_session_close",
                return_value=close_result,
            ),
            patch(
                "raise_cli.cli.commands.session.resolve_session_id",
                return_value="SES-050",
            ),
        ):
            result = runner.invoke(
                app,
                [
                    "session",
                    "close",
                    "--summary",
                    "test",
                    "--session",
                    "SES-050",
                    "--project",
                    str(tmp_path),
                ],
            )

        assert result.exit_code == 0
        assert not session_dir.exists(), "Session dir should be cleaned up after close"

    def test_close_help_shows_new_options(self) -> None:
        """Close --help shows new structured close options."""
        result = runner.invoke(app, ["session", "close", "--help"])
        assert result.exit_code == 0
        assert "--summary" in result.output
        assert "--state-file" in result.output
        assert "--pattern" in result.output
        assert "--correction" in result.output


class TestSessionContext:
    """Tests for raise session context command."""

    def test_context_returns_formatted_sections(self) -> None:
        """Session context --sections returns formatted output."""
        profile = DeveloperProfile(name="Test")

        with (
            patch(
                "raise_cli.cli.commands.session.load_developer_profile",
                return_value=profile,
            ),
            patch(
                "raise_cli.cli.commands.session.assemble_sections",
                return_value="# Governance Primes\n- guardrail-must-001: Type hints",
            ),
            patch(
                "raise_cli.cli.commands.session.load_session_state",
                return_value=None,
            ),
        ):
            result = runner.invoke(
                app,
                ["session", "context", "--sections", "governance", "--project", "."],
            )

        assert result.exit_code == 0
        assert "# Governance Primes" in result.output

    def test_context_requires_sections(self) -> None:
        """Session context without --sections shows error."""
        result = runner.invoke(app, ["session", "context"])
        assert result.exit_code != 0

    def test_context_requires_project(self) -> None:
        """Session context without --project shows error."""
        result = runner.invoke(app, ["session", "context", "--sections", "governance"])
        assert result.exit_code != 0

    def test_context_unknown_section_shows_error(self) -> None:
        """Session context with unknown section shows helpful error."""
        profile = DeveloperProfile(name="Test")

        with (
            patch(
                "raise_cli.cli.commands.session.load_developer_profile",
                return_value=profile,
            ),
            patch(
                "raise_cli.cli.commands.session.assemble_sections",
                side_effect=ValueError(
                    "Unknown section: 'bogus'. Valid: ['behavioral', 'coaching', 'deadlines', 'governance', 'progress']"
                ),
            ),
            patch(
                "raise_cli.cli.commands.session.load_session_state",
                return_value=None,
            ),
        ):
            result = runner.invoke(
                app,
                ["session", "context", "--sections", "bogus", "--project", "."],
            )

        assert result.exit_code != 0
        assert "Unknown section" in result.output

    def test_context_no_profile_errors(self) -> None:
        """Session context without profile gives error."""
        with patch(
            "raise_cli.cli.commands.session.load_developer_profile", return_value=None
        ):
            result = runner.invoke(
                app,
                ["session", "context", "--sections", "governance", "--project", "."],
            )

        assert result.exit_code != 0
        assert "No developer profile found" in result.output


class TestSessionHelp:
    """Tests for session command help."""

    def test_session_no_args_shows_help(self) -> None:
        """Session without subcommand shows help."""
        result = runner.invoke(app, ["session"])

        # no_args_is_help=True causes exit code 0 or 2 depending on typer version
        assert result.exit_code in (0, 2)
        assert "start" in result.output
        assert "close" in result.output
        assert "context" in result.output
        assert "Manage working sessions" in result.output

    def test_session_start_help(self) -> None:
        """Session start --help shows usage."""
        result = runner.invoke(app, ["session", "start", "--help"])

        assert result.exit_code == 0
        assert "--name" in result.output
        assert "--project" in result.output

    def test_session_close_help(self) -> None:
        """Session close --help shows usage."""
        result = runner.invoke(app, ["session", "close", "--help"])

        assert result.exit_code == 0
        assert "End the current working session" in result.output


class TestSessionStartAutoSyncSkills:
    """Tests for auto-syncing skills on version mismatch (RAISE-509)."""

    def test_syncs_skills_when_version_mismatch(self, tmp_path: Path) -> None:
        """Session start auto-syncs skills when CLI version > manifest version."""
        from raise_cli.onboarding.skills import SkillScaffoldResult

        profile = DeveloperProfile(name="Test")
        project_path = tmp_path / "project"
        (project_path / ".raise" / "manifests").mkdir(parents=True)

        scaffold_result = SkillScaffoldResult(
            skills_updated=["rai-session-start"],
            skills_installed=["rai-new-skill"],
        )

        with (
            patch(
                "raise_cli.cli.commands.session.load_developer_profile",
                return_value=profile,
            ),
            patch("raise_cli.cli.commands.session.save_developer_profile"),
            patch(
                "raise_cli.cli.commands.session._maybe_sync_skills",
                return_value=scaffold_result,
            ) as mock_sync,
        ):
            result = runner.invoke(
                app, ["session", "start", "--project", str(project_path)]
            )

        assert result.exit_code == 0
        mock_sync.assert_called_once_with(project_path)

    def test_skips_sync_when_no_project(self) -> None:
        """Session start without --project does not attempt skill sync."""
        profile = DeveloperProfile(name="Test")

        with (
            patch(
                "raise_cli.cli.commands.session.load_developer_profile",
                return_value=profile,
            ),
            patch("raise_cli.cli.commands.session.save_developer_profile"),
            patch(
                "raise_cli.cli.commands.session._maybe_sync_skills",
            ) as mock_sync,
        ):
            result = runner.invoke(app, ["session", "start"])

        assert result.exit_code == 0
        mock_sync.assert_not_called()


class TestSessionStartCreatesDir:
    """Tests for session start creating per-session directory (RAISE-138)."""

    def test_start_creates_session_dir(self, tmp_path: Path) -> None:
        """Session start with --project creates per-session directory."""
        profile = DeveloperProfile(name="Test")
        project_path = tmp_path / "project"
        project_path.mkdir()

        with (
            patch(
                "raise_cli.cli.commands.session.load_developer_profile",
                return_value=profile,
            ),
            patch("raise_cli.cli.commands.session.save_developer_profile"),
        ):
            result = runner.invoke(
                app,
                ["session", "start", "--project", str(project_path)],
            )

        assert result.exit_code == 0
        # Per-session directory should exist (new format: S-{P}-YYMMDD-HHMM)
        sessions_dir = project_path / ".raise" / "rai" / "personal" / "sessions"
        assert sessions_dir.exists(), "Sessions directory should exist after start"
        session_dirs = [
            d for d in sessions_dir.iterdir() if d.is_dir() and d.name.startswith("S-")
        ]
        assert len(session_dirs) >= 1, (
            "Per-session directory should be created on start"
        )

    def test_start_migrates_flat_files(self, tmp_path: Path) -> None:
        """Session start migrates flat state/telemetry files to per-session dir."""
        profile = DeveloperProfile(name="Test")
        project_path = tmp_path / "project"
        project_path.mkdir()

        # Create flat files (legacy layout)
        personal_dir = project_path / ".raise" / "rai" / "personal"
        personal_dir.mkdir(parents=True)
        flat_state = personal_dir / "session-state.yaml"
        flat_state.write_text("current_work:\n  epic: E15\n")
        flat_telemetry_dir = personal_dir / "telemetry"
        flat_telemetry_dir.mkdir()
        flat_signals = flat_telemetry_dir / "signals.jsonl"
        flat_signals.write_text('{"signal_type": "test"}\n')

        with (
            patch(
                "raise_cli.cli.commands.session.load_developer_profile",
                return_value=profile,
            ),
            patch("raise_cli.cli.commands.session.save_developer_profile"),
        ):
            result = runner.invoke(
                app,
                ["session", "start", "--project", str(project_path)],
            )

        assert result.exit_code == 0
        # Flat files should be moved to a per-session dir (new format: S-T-YYMMDD-HHMM)
        sessions_dir = project_path / ".raise" / "rai" / "personal" / "sessions"
        session_dirs = [
            d
            for d in sessions_dir.iterdir()
            if d.is_dir() and (d / "state.yaml").exists()
        ]
        assert len(session_dirs) == 1, (
            "Migration should create one session dir with state"
        )
        assert (session_dirs[0] / "signals.jsonl").exists()
        # Old flat files should be removed
        assert not flat_state.exists(), (
            "Flat state file should be removed after migration"
        )
        assert not flat_signals.exists(), (
            "Flat signals file should be removed after migration"
        )


class TestSessionStartWithAgent:
    """Tests for raise session start --agent flag (RAISE-137)."""

    def test_start_with_agent_flag(self, tmp_path: Path) -> None:
        """Session start --agent includes agent in output."""
        profile = DeveloperProfile(name="Test")
        project_path = tmp_path / "test-project"
        project_path.mkdir()

        with (
            patch(
                "raise_cli.cli.commands.session.load_developer_profile",
                return_value=profile,
            ),
            patch("raise_cli.cli.commands.session.save_developer_profile"),
        ):
            result = runner.invoke(
                app,
                [
                    "session",
                    "start",
                    "--project",
                    str(project_path),
                    "--agent",
                    "claude-code",
                ],
            )

        assert result.exit_code == 0
        assert "S-T-" in result.output  # New-format session ID present
        assert "(claude-code)" in result.output

    def test_start_without_agent_defaults(self, tmp_path: Path) -> None:
        """Session start without --agent defaults to unknown."""
        profile = DeveloperProfile(name="Test")
        project_path = tmp_path / "test-project"
        project_path.mkdir()

        with (
            patch(
                "raise_cli.cli.commands.session.load_developer_profile",
                return_value=profile,
            ),
            patch("raise_cli.cli.commands.session.save_developer_profile"),
        ):
            result = runner.invoke(
                app, ["session", "start", "--project", str(project_path)]
            )

        assert result.exit_code == 0
        assert "(unknown)" in result.output  # Default agent


class TestSessionCloseCwdGuard:
    """Tests for CWD poka-yoke guard on session close (RAISE-139)."""

    def test_close_skips_session_from_different_project(self, tmp_path: Path) -> None:
        """Session close from project-b ignores active session from project-a."""
        from datetime import UTC, datetime

        session_project = tmp_path / "project-a"
        session_project.mkdir()
        wrong_project = tmp_path / "project-b"
        wrong_project.mkdir()

        active = ActiveSession(
            session_id="SES-050",
            started_at=datetime.now(UTC),
            project=str(session_project),
            agent="test",
        )
        profile = DeveloperProfile(name="Test", active_sessions=[active])

        with (
            patch(
                "raise_cli.cli.commands.session.load_developer_profile",
                return_value=profile,
            ),
            patch("raise_cli.cli.commands.session.save_developer_profile"),
        ):
            result = runner.invoke(
                app,
                [
                    "session",
                    "close",
                    "--summary",
                    "test",
                    "--project",
                    str(wrong_project),
                ],
            )

        # Structured close proceeds — CWD guard skips because no session matches project-b
        assert result.exit_code == 0
        assert "closed" in result.output

    def test_close_allows_matching_project(self, tmp_path: Path) -> None:
        """Session close allows writes when projects match."""
        from datetime import UTC, datetime

        project = tmp_path / "project"
        project.mkdir()

        active = ActiveSession(
            session_id="SES-050",
            started_at=datetime.now(UTC),
            project=str(project),
            agent="test",
        )
        profile = DeveloperProfile(name="Test", active_sessions=[active])
        close_result = CloseResult(
            success=True,
            session_id="SES-050",
            patterns_added=0,
            corrections_added=0,
        )

        with (
            patch(
                "raise_cli.cli.commands.session.load_developer_profile",
                return_value=profile,
            ),
            patch(
                "raise_cli.cli.commands.session.process_session_close",
                return_value=close_result,
            ),
            patch(
                "raise_cli.cli.commands.session.resolve_session_id",
                return_value="SES-050",
            ),
        ):
            result = runner.invoke(
                app,
                [
                    "session",
                    "close",
                    "--summary",
                    "test",
                    "--session",
                    "SES-050",
                    "--project",
                    str(project),
                ],
            )

        assert result.exit_code == 0
        assert "SES-050 closed" in result.output

    def test_close_no_active_session_skips_guard(self) -> None:
        """Guard is skipped when no active session has project info."""
        profile = DeveloperProfile(name="Test", active_sessions=[])
        close_result = CloseResult(
            success=True,
            session_id="SES-099",
            patterns_added=0,
            corrections_added=0,
        )

        with (
            patch(
                "raise_cli.cli.commands.session.load_developer_profile",
                return_value=profile,
            ),
            patch(
                "raise_cli.cli.commands.session.process_session_close",
                return_value=close_result,
            ),
        ):
            result = runner.invoke(
                app,
                ["session", "close", "--summary", "test"],
            )

        assert result.exit_code == 0

    def test_close_rejects_mismatch_on_legacy_close(self, tmp_path: Path) -> None:
        """Legacy close from wrong CWD skips session from different project."""
        from datetime import UTC, datetime

        session_project = tmp_path / "correct"
        session_project.mkdir()
        wrong_project = tmp_path / "wrong"
        wrong_project.mkdir()

        active = ActiveSession(
            session_id="SES-050",
            started_at=datetime.now(UTC),
            project=str(session_project),
            agent="test",
        )
        profile = DeveloperProfile(name="Test", active_sessions=[active])

        with (
            patch(
                "raise_cli.cli.commands.session.load_developer_profile",
                return_value=profile,
            ),
            patch("raise_cli.cli.commands.session.save_developer_profile"),
            patch("raise_cli.cli.commands.session.Path") as mock_path_cls,
        ):
            # Mock Path.cwd() to return wrong project
            mock_path_cls.cwd.return_value = wrong_project
            # But we need real Path for other uses, so let Path(x) work normally
            mock_path_cls.side_effect = Path

            result = runner.invoke(
                app,
                ["session", "close"],
            )

        assert result.exit_code == 0
        assert "No active session for this project" in result.output


class TestSessionCloseWithSessionFlag:
    """Tests for raise session close --session flag (RAISE-137)."""

    def test_close_with_session_flag(self, tmp_path: Path) -> None:
        """Session close --session uses resolver to identify session."""
        profile = DeveloperProfile(name="Test")

        with (
            patch(
                "raise_cli.cli.commands.session.load_developer_profile",
                return_value=profile,
            ),
            patch("raise_cli.cli.commands.session.save_developer_profile"),
            patch("raise_cli.cli.commands.session.resolve_session_id") as mock_resolve,
        ):
            mock_resolve.return_value = "SES-177"
            result = runner.invoke(
                app,
                [
                    "session",
                    "close",
                    "--session",
                    "SES-177",
                ],
            )

        # Should succeed (legacy close behavior for now)
        assert result.exit_code == 0
        # Resolver was called during session ID resolution
        mock_resolve.assert_called_once_with(session_flag="SES-177", env_var=None)


class TestSessionCloseCoherenceValidation:
    """Tests for session close state file coherence validation (RAISE-201)."""

    def test_rejects_state_file_with_mismatched_session_id(
        self,
        tmp_path: Path,
    ) -> None:
        """CLI rejects state file when session_id doesn't match --session."""
        import yaml

        profile = DeveloperProfile(name="Test")

        # Write state file with SES-217 data
        state_file = tmp_path / "session-output.yaml"
        state_file.write_text(
            yaml.dump(
                {
                    "session_id": "SES-217",
                    "summary": "wrong session data",
                    "type": "feature",
                }
            )
        )

        with (
            patch(
                "raise_cli.cli.commands.session.load_developer_profile",
                return_value=profile,
            ),
            patch("raise_cli.cli.commands.session.resolve_session_id") as mock_resolve,
        ):
            mock_resolve.return_value = "SES-219"
            result = runner.invoke(
                app,
                [
                    "session",
                    "close",
                    "--state-file",
                    str(state_file),
                    "--session",
                    "SES-219",
                    "--project",
                    str(tmp_path),
                ],
            )

        assert result.exit_code != 0
        assert "SES-217" in result.output
        assert "SES-219" in result.output

    def test_accepts_state_file_with_matching_session_id(
        self,
        tmp_path: Path,
    ) -> None:
        """CLI accepts state file when session_id matches --session."""
        import yaml

        profile = DeveloperProfile(name="Test")

        # Create project structure
        project = tmp_path / "project"
        (project / ".raise" / "rai" / "memory" / "sessions").mkdir(parents=True)
        (project / ".raise" / "rai" / "personal" / "sessions").mkdir(parents=True)

        state_file = tmp_path / "session-output.yaml"
        state_file.write_text(
            yaml.dump(
                {
                    "session_id": "SES-219",
                    "summary": "correct session",
                    "type": "feature",
                }
            )
        )

        with (
            patch(
                "raise_cli.cli.commands.session.load_developer_profile",
                return_value=profile,
            ),
            patch("raise_cli.cli.commands.session.save_developer_profile"),
            patch("raise_cli.cli.commands.session.resolve_session_id") as mock_resolve,
            patch("raise_cli.cli.commands.session.process_session_close") as mock_close,
            patch("raise_cli.cli.commands.session.cleanup_session_dir"),
        ):
            mock_resolve.return_value = "SES-219"
            mock_close.return_value = CloseResult(success=True, session_id="SES-219")
            result = runner.invoke(
                app,
                [
                    "session",
                    "close",
                    "--state-file",
                    str(state_file),
                    "--session",
                    "SES-219",
                    "--project",
                    str(project),
                ],
            )

        assert result.exit_code == 0
        assert "SES-219 closed" in result.output

    def test_skips_validation_when_state_file_has_no_session_id(
        self,
        tmp_path: Path,
    ) -> None:
        """CLI proceeds when state file has no session_id (backwards compat)."""
        import yaml

        profile = DeveloperProfile(name="Test")

        project = tmp_path / "project"
        (project / ".raise" / "rai" / "memory" / "sessions").mkdir(parents=True)
        (project / ".raise" / "rai" / "personal" / "sessions").mkdir(parents=True)

        state_file = tmp_path / "session-output.yaml"
        state_file.write_text(
            yaml.dump(
                {
                    "summary": "old format without session_id",
                    "type": "feature",
                }
            )
        )

        with (
            patch(
                "raise_cli.cli.commands.session.load_developer_profile",
                return_value=profile,
            ),
            patch("raise_cli.cli.commands.session.save_developer_profile"),
            patch("raise_cli.cli.commands.session.resolve_session_id") as mock_resolve,
            patch("raise_cli.cli.commands.session.process_session_close") as mock_close,
            patch("raise_cli.cli.commands.session.cleanup_session_dir"),
            patch("raise_cli.cli.commands.session.write_session_entry"),
            patch("raise_cli.cli.commands.session.clear_active_session"),
            patch(
                "raise_cli.cli.commands.session.read_active_session", return_value=None
            ),
        ):
            mock_resolve.return_value = "SES-219"
            mock_close.return_value = CloseResult(success=True, session_id="SES-219")
            result = runner.invoke(
                app,
                [
                    "session",
                    "close",
                    "--state-file",
                    str(state_file),
                    "--session",
                    "SES-219",
                    "--project",
                    str(project),
                ],
            )

        assert result.exit_code == 0


class TestSessionStartContextLoadsState:
    """Regression test for RAISE-566: prior session state must survive migration."""

    def test_session_start_loads_prior_state(self, tmp_path: Path) -> None:
        """State passed to assemble_context_bundle is not None when flat state exists.

        Before the fix: migrate_flat_to_session moves session-state.yaml to
        SES-{prev}/state.yaml, then load_session_state(session_id=SES-{new})
        looks in the wrong dir → returns None.
        """
        import yaml

        profile = DeveloperProfile(name="Fer")
        project = tmp_path / "project"
        personal_dir = project / ".raise" / "rai" / "personal"
        personal_dir.mkdir(parents=True)

        (personal_dir / "session-state.yaml").write_text(
            yaml.dump(
                {
                    "current_work": {
                        "story": "RAISE-566",
                        "epic": "E479",
                        "phase": "fix",
                        "branch": "bug/raise-566/session-start-context-loss",
                        "release": "",
                    },
                    "last_session": {
                        "id": "SES-085",
                        "date": "2026-03-17",
                        "developer": "Fer",
                        "summary": "RAISE-566 scoped",
                    },
                }
            )
        )

        captured: list[object] = []

        def capture_bundle(
            dev_profile: object,
            state: object,
            project_path: object,
            **kwargs: object,
        ) -> str:
            captured.append(state)
            return "# Session Context\n"

        with (
            patch(
                "raise_cli.cli.commands.session.load_developer_profile",
                return_value=profile,
            ),
            patch("raise_cli.cli.commands.session.save_developer_profile"),
            patch(
                "raise_cli.cli.commands.session.assemble_context_bundle",
                side_effect=capture_bundle,
            ),
        ):
            result = runner.invoke(
                app,
                ["session", "start", "--project", str(project), "--context"],
            )

        assert result.exit_code == 0
        assert len(captured) == 1, "assemble_context_bundle must be called once"
        state = captured[0]
        assert state is not None, (
            "state must not be None when flat session-state.yaml exists before start"
        )
        from raise_cli.schemas.session_state import SessionState

        assert isinstance(state, SessionState)
        assert state.current_work.story == "RAISE-566"


class TestSessionList:
    """Tests for raise session list command."""

    def test_list_empty_registry(self) -> None:
        """No sessions should show helpful message."""
        profile = DeveloperProfile(name="Alice")

        with (
            patch(
                "raise_cli.cli.commands.session.load_developer_profile",
                return_value=profile,
            ),
            patch(
                "raise_cli.cli.commands.session.read_session_entries",
                return_value=[],
            ),
        ):
            result = runner.invoke(app, ["session", "list"])

        assert result.exit_code == 0
        assert "No sessions found" in result.output

    def test_list_shows_sessions(self) -> None:
        """Should display session names and IDs."""
        from datetime import datetime

        from raise_cli.session.index import SessionIndexEntry

        profile = DeveloperProfile(name="Alice")
        entries = [
            SessionIndexEntry(
                id="S-A-260322-1430",
                name="gemba research",
                started=datetime(2026, 3, 22, 14, 30),
                closed=datetime(2026, 3, 22, 16, 0),
                type="research",
            ),
            SessionIndexEntry(
                id="S-A-260322-1600",
                name="epic design",
                started=datetime(2026, 3, 22, 16, 0),
                closed=datetime(2026, 3, 22, 18, 30),
                type="feature",
            ),
        ]

        with (
            patch(
                "raise_cli.cli.commands.session.load_developer_profile",
                return_value=profile,
            ),
            patch(
                "raise_cli.cli.commands.session.read_session_entries",
                return_value=entries,
            ),
            patch(
                "raise_cli.cli.commands.session.read_active_session",
                return_value=None,
            ),
        ):
            result = runner.invoke(app, ["session", "list"])

        assert result.exit_code == 0
        assert "gemba research" in result.output
        assert "epic design" in result.output
        assert "S-A-260322-1430" in result.output
        assert "2 total sessions" in result.output

    def test_list_shows_active_indicator(self) -> None:
        """Active session should show (active) marker."""
        from datetime import datetime

        from raise_cli.session.index import ActiveSessionPointer, SessionIndexEntry

        profile = DeveloperProfile(name="Alice")
        entries = [
            SessionIndexEntry(
                id="S-A-260322-1430",
                name="active session",
                started=datetime(2026, 3, 22, 14, 30),
            ),
        ]
        active = ActiveSessionPointer(
            id="S-A-260322-1430",
            name="active session",
            started=datetime(2026, 3, 22, 14, 30),
        )

        with (
            patch(
                "raise_cli.cli.commands.session.load_developer_profile",
                return_value=profile,
            ),
            patch(
                "raise_cli.cli.commands.session.read_session_entries",
                return_value=entries,
            ),
            patch(
                "raise_cli.cli.commands.session.read_active_session",
                return_value=active,
            ),
        ):
            result = runner.invoke(app, ["session", "list"])

        assert result.exit_code == 0
        assert "(active)" in result.output


class TestSessionCloseSharedIndex:
    """Tests for shared index write during structured close."""

    def test_close_writes_to_shared_index(self, tmp_path: Path) -> None:
        """Structured close should write SessionIndexEntry to shared index."""
        profile = DeveloperProfile(name="Test")
        project = tmp_path / "project"
        (project / ".raise" / "rai" / "memory" / "sessions").mkdir(parents=True)
        (project / ".raise" / "rai" / "personal" / "sessions").mkdir(parents=True)

        with (
            patch(
                "raise_cli.cli.commands.session.load_developer_profile",
                return_value=profile,
            ),
            patch("raise_cli.cli.commands.session.save_developer_profile"),
            patch("raise_cli.cli.commands.session.process_session_close") as mock_close,
            patch("raise_cli.cli.commands.session.cleanup_session_dir"),
            patch(
                "raise_cli.cli.commands.session.write_session_entry"
            ) as mock_write_entry,
            patch("raise_cli.cli.commands.session.clear_active_session"),
            patch(
                "raise_cli.cli.commands.session.read_active_session", return_value=None
            ),
        ):
            mock_close.return_value = CloseResult(
                success=True, session_id="S-T-260322-1430"
            )
            result = runner.invoke(
                app,
                [
                    "session",
                    "close",
                    "--summary",
                    "test close",
                    "--project",
                    str(project),
                ],
            )

        assert result.exit_code == 0
        mock_write_entry.assert_called_once()
        entry = mock_write_entry.call_args[0][1]
        assert entry.summary == "test close"
        assert entry.id == "S-T-260322-1430"

    def test_close_does_not_write_index_on_failure(self, tmp_path: Path) -> None:
        """Failed close should NOT write to shared index."""
        profile = DeveloperProfile(name="Test")
        project = tmp_path / "project"
        (project / ".raise" / "rai" / "memory" / "sessions").mkdir(parents=True)
        (project / ".raise" / "rai" / "personal" / "sessions").mkdir(parents=True)

        with (
            patch(
                "raise_cli.cli.commands.session.load_developer_profile",
                return_value=profile,
            ),
            patch("raise_cli.cli.commands.session.save_developer_profile"),
            patch("raise_cli.cli.commands.session.process_session_close") as mock_close,
            patch("raise_cli.cli.commands.session.cleanup_session_dir"),
            patch(
                "raise_cli.cli.commands.session.write_session_entry"
            ) as mock_write_entry,
            patch("raise_cli.cli.commands.session.clear_active_session"),
        ):
            mock_close.return_value = CloseResult(
                success=False, session_id="S-T-260322-1430"
            )
            runner.invoke(
                app,
                [
                    "session",
                    "close",
                    "--summary",
                    "failed close",
                    "--project",
                    str(project),
                ],
            )

        mock_write_entry.assert_not_called()
