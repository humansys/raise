"""Tests for raise session commands."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from rai_cli.cli.main import app
from rai_cli.onboarding.profile import CurrentSession, DeveloperProfile
from rai_cli.session.close import CloseResult

runner = CliRunner()


class TestSessionStart:
    """Tests for raise session start command."""

    def test_start_first_time_requires_name(self) -> None:
        """First-time user without --name should get helpful error."""
        with patch(
            "rai_cli.cli.commands.session.load_developer_profile", return_value=None
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
                "rai_cli.cli.commands.session.load_developer_profile",
                return_value=None,
            ),
            patch("rai_cli.cli.commands.session.save_developer_profile") as mock_save,
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
                "rai_cli.cli.commands.session.load_developer_profile",
                return_value=profile,
            ),
            patch("rai_cli.cli.commands.session.save_developer_profile") as mock_save,
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
                "rai_cli.cli.commands.session.load_developer_profile",
                return_value=profile,
            ),
            patch("rai_cli.cli.commands.session.save_developer_profile") as mock_save,
        ):
            result = runner.invoke(
                app, ["session", "start", "--project", str(project_path)]
            )

        assert result.exit_code == 0
        assert "Session recorded" in result.output
        mock_save.assert_called_once()
        saved_profile = mock_save.call_args[0][0]
        assert saved_profile.current_session is not None
        assert saved_profile.current_session.project == str(project_path)

    def test_start_warns_on_stale_session(self) -> None:
        """Starting when stale session exists warns user."""
        from datetime import UTC, datetime, timedelta

        stale_state = CurrentSession(
            started_at=datetime.now(UTC) - timedelta(days=2),
            project="/old/project",
        )
        profile = DeveloperProfile(name="Dave", current_session=stale_state)

        with (
            patch(
                "rai_cli.cli.commands.session.load_developer_profile",
                return_value=profile,
            ),
            patch("rai_cli.cli.commands.session.save_developer_profile"),
        ):
            result = runner.invoke(app, ["session", "start"])

        assert result.exit_code == 0
        assert "Stale session detected" in result.output
        assert "Learnings may have been lost" in result.output

    def test_start_notes_active_session(self) -> None:
        """Starting when recent session exists notes it."""
        from datetime import UTC, datetime

        recent_state = CurrentSession(
            started_at=datetime.now(UTC),
            project="/current/project",
        )
        profile = DeveloperProfile(name="Eve", current_session=recent_state)

        with (
            patch(
                "rai_cli.cli.commands.session.load_developer_profile",
                return_value=profile,
            ),
            patch("rai_cli.cli.commands.session.save_developer_profile"),
        ):
            result = runner.invoke(app, ["session", "start"])

        assert result.exit_code == 0
        assert "Session already active" in result.output

    def test_start_context_outputs_bundle(self, tmp_path: Path) -> None:
        """Session start --context outputs context bundle."""
        profile = DeveloperProfile(name="Hank")

        with (
            patch(
                "rai_cli.cli.commands.session.load_developer_profile",
                return_value=profile,
            ),
            patch("rai_cli.cli.commands.session.save_developer_profile"),
            patch(
                "rai_cli.cli.commands.session.assemble_context_bundle",
                return_value="# Session Context\nDeveloper: Hank (shu)",
            ),
            patch(
                "rai_cli.cli.commands.session.load_session_state",
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
                "rai_cli.cli.commands.session.load_developer_profile",
                return_value=profile,
            ),
            patch("rai_cli.cli.commands.session.save_developer_profile"),
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
                "rai_cli.cli.commands.session.load_developer_profile",
                return_value=profile,
            ),
            patch("rai_cli.cli.commands.session.save_developer_profile"),
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
            "rai_cli.cli.commands.session.load_developer_profile", return_value=None
        ):
            result = runner.invoke(app, ["session", "close"])

        assert result.exit_code != 0
        assert "No developer profile found" in result.output

    def test_close_no_active_session_is_noop(self) -> None:
        """Close when no active session is informational no-op."""
        profile = DeveloperProfile(name="Frank", current_session=None)

        with patch(
            "rai_cli.cli.commands.session.load_developer_profile",
            return_value=profile,
        ):
            result = runner.invoke(app, ["session", "close"])

        assert result.exit_code == 0
        assert "No active session to close" in result.output

    def test_close_active_session_clears_state(self) -> None:
        """Close with active session clears current_session."""
        from datetime import UTC, datetime

        active_state = CurrentSession(
            started_at=datetime.now(UTC),
            project="/my/project",
        )
        profile = DeveloperProfile(name="Grace", current_session=active_state)

        with (
            patch(
                "rai_cli.cli.commands.session.load_developer_profile",
                return_value=profile,
            ),
            patch("rai_cli.cli.commands.session.save_developer_profile") as mock_save,
        ):
            result = runner.invoke(app, ["session", "close"])

        assert result.exit_code == 0
        assert "Session closed" in result.output
        mock_save.assert_called_once()
        saved_profile = mock_save.call_args[0][0]
        assert saved_profile.current_session is None

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
                "rai_cli.cli.commands.session.load_developer_profile",
                return_value=profile,
            ),
            patch(
                "rai_cli.cli.commands.session.process_session_close",
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
                "rai_cli.cli.commands.session.load_developer_profile",
                return_value=profile,
            ),
            patch(
                "rai_cli.cli.commands.session.process_session_close",
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
                "rai_cli.cli.commands.session.load_developer_profile",
                return_value=profile,
            ),
            patch(
                "rai_cli.cli.commands.session.process_session_close",
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
                "rai_cli.cli.commands.session.load_developer_profile",
                return_value=profile,
            ),
            patch(
                "rai_cli.cli.commands.session.process_session_close",
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

    def test_close_help_shows_new_options(self) -> None:
        """Close --help shows new structured close options."""
        result = runner.invoke(app, ["session", "close", "--help"])
        assert result.exit_code == 0
        assert "--summary" in result.output
        assert "--state-file" in result.output
        assert "--pattern" in result.output
        assert "--correction" in result.output


class TestSessionHelp:
    """Tests for session command help."""

    def test_session_no_args_shows_help(self) -> None:
        """Session without subcommand shows help."""
        result = runner.invoke(app, ["session"])

        # no_args_is_help=True causes exit code 0 or 2 depending on typer version
        assert result.exit_code in (0, 2)
        assert "start" in result.output
        assert "close" in result.output
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


class TestSessionStartWithAgent:
    """Tests for raise session start --agent flag (RAISE-137)."""

    def test_start_with_agent_flag(self) -> None:
        """Session start --agent includes agent in output."""
        profile = DeveloperProfile(name="Test")

        with (
            patch(
                "rai_cli.cli.commands.session.load_developer_profile",
                return_value=profile,
            ),
            patch("rai_cli.cli.commands.session.save_developer_profile"),
        ):
            result = runner.invoke(
                app, ["session", "start", "--agent", "claude-code"]
            )

        assert result.exit_code == 0
        assert "SES-" in result.output  # Session ID present
        assert "(claude-code)" in result.output

    def test_start_without_agent_defaults(self) -> None:
        """Session start without --agent defaults to unknown."""
        profile = DeveloperProfile(name="Test")

        with (
            patch(
                "rai_cli.cli.commands.session.load_developer_profile",
                return_value=profile,
            ),
            patch("rai_cli.cli.commands.session.save_developer_profile"),
        ):
            result = runner.invoke(app, ["session", "start"])

        assert result.exit_code == 0
        # Should still work, just not show agent in output if not specified


class TestSessionCloseWithSessionFlag:
    """Tests for raise session close --session flag (RAISE-137)."""

    def test_close_with_session_flag(self, tmp_path: Path) -> None:
        """Session close --session uses resolver to identify session."""
        profile = DeveloperProfile(name="Test")

        with (
            patch(
                "rai_cli.cli.commands.session.load_developer_profile",
                return_value=profile,
            ),
            patch("rai_cli.cli.commands.session.save_developer_profile"),
            patch("rai_cli.cli.commands.session.resolve_session_id") as mock_resolve,
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
        mock_resolve.assert_called_once_with(
            session_flag="SES-177", env_var=None
        )
