"""Tests for raise session commands."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from raise_cli.cli.main import app
from raise_cli.onboarding.profile import CurrentSession, DeveloperProfile

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

    def test_start_first_time_with_name_creates_profile(
        self, tmp_path: Path
    ) -> None:
        """First-time user with --name creates profile and starts session."""
        rai_home = tmp_path / ".rai"
        rai_home.mkdir(parents=True)

        with (
            patch(
                "raise_cli.cli.commands.session.load_developer_profile",
                return_value=None,
            ),
            patch(
                "raise_cli.cli.commands.session.save_developer_profile"
            ) as mock_save,
        ):
            result = runner.invoke(
                app, ["session", "start", "--name", "Alice"]
            )

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
            patch(
                "raise_cli.cli.commands.session.save_developer_profile"
            ) as mock_save,
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
            patch(
                "raise_cli.cli.commands.session.save_developer_profile"
            ) as mock_save,
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
                "raise_cli.cli.commands.session.load_developer_profile",
                return_value=profile,
            ),
            patch("raise_cli.cli.commands.session.save_developer_profile"),
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
                "raise_cli.cli.commands.session.load_developer_profile",
                return_value=profile,
            ),
            patch("raise_cli.cli.commands.session.save_developer_profile"),
        ):
            result = runner.invoke(app, ["session", "start"])

        assert result.exit_code == 0
        assert "Session already active" in result.output


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
        profile = DeveloperProfile(name="Frank", current_session=None)

        with patch(
            "raise_cli.cli.commands.session.load_developer_profile",
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
                "raise_cli.cli.commands.session.load_developer_profile",
                return_value=profile,
            ),
            patch(
                "raise_cli.cli.commands.session.save_developer_profile"
            ) as mock_save,
        ):
            result = runner.invoke(app, ["session", "close"])

        assert result.exit_code == 0
        assert "Session closed" in result.output
        mock_save.assert_called_once()
        saved_profile = mock_save.call_args[0][0]
        assert saved_profile.current_session is None


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
