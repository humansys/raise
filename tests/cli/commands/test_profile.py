"""Tests for the raise profile command."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from raise_cli.cli.main import app
from raise_cli.onboarding.profile import (
    CurrentSession,
    DeveloperProfile,
    ExperienceLevel,
    save_developer_profile,
)

runner = CliRunner()


@pytest.fixture
def mock_home(tmp_path: Path) -> Path:
    """Provide a temporary home directory for tests."""
    return tmp_path / "home"


class TestProfileShowCommand:
    """Tests for raise profile show command."""

    def test_show_displays_profile_yaml(self, mock_home: Path) -> None:
        """Show outputs profile in YAML format when profile exists."""
        mock_home.mkdir(parents=True, exist_ok=True)

        # Create a profile
        profile = DeveloperProfile(
            name="Test Developer",
            experience_level=ExperienceLevel.HA,
            sessions_total=15,
            projects=["/path/to/project1", "/path/to/project2"],
        )
        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            save_developer_profile(profile)

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(app, ["profile", "show"], catch_exceptions=False)

        assert result.exit_code == 0
        # Should contain YAML output with profile data
        assert "name: Test Developer" in result.output
        assert "experience_level: ha" in result.output
        assert "sessions_total: 15" in result.output

    def test_show_no_profile_shows_helpful_message(self, mock_home: Path) -> None:
        """Show outputs helpful message when no profile exists."""
        mock_home.mkdir(parents=True, exist_ok=True)

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(app, ["profile", "show"], catch_exceptions=False)

        assert result.exit_code == 0
        # Should show helpful message, not error
        assert "no developer profile found" in result.output.lower()
        assert "raise init" in result.output.lower()

    def test_show_includes_all_profile_fields(self, mock_home: Path) -> None:
        """Show includes all profile fields in output."""
        mock_home.mkdir(parents=True, exist_ok=True)

        profile = DeveloperProfile(
            name="Expert User",
            experience_level=ExperienceLevel.RI,
            sessions_total=50,
            skills_mastered=["tdd", "epic-planning"],
            universal_patterns=["always-use-types"],
        )
        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            save_developer_profile(profile)

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(app, ["profile", "show"], catch_exceptions=False)

        assert result.exit_code == 0
        assert "skills_mastered" in result.output
        assert "tdd" in result.output
        assert "universal_patterns" in result.output
        assert "always-use-types" in result.output

    def test_show_includes_communication_preferences(self, mock_home: Path) -> None:
        """Show includes communication preferences in output."""
        mock_home.mkdir(parents=True, exist_ok=True)

        profile = DeveloperProfile(
            name="Configured User",
            experience_level=ExperienceLevel.HA,
        )
        # Update communication preferences
        profile.communication.language = "es"
        profile.communication.skip_praise = True

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            save_developer_profile(profile)

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(app, ["profile", "show"], catch_exceptions=False)

        assert result.exit_code == 0
        assert "communication" in result.output
        assert "language: es" in result.output
        assert "skip_praise: true" in result.output


class TestProfileSessionCommand:
    """Tests for raise profile session-start command."""

    def test_session_increments_existing_profile(self, mock_home: Path) -> None:
        """Session increments sessions_total for existing profile."""
        mock_home.mkdir(parents=True, exist_ok=True)

        profile = DeveloperProfile(
            name="Test User",
            experience_level=ExperienceLevel.SHU,
            sessions_total=5,
        )
        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            save_developer_profile(profile)

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(app, ["profile", "session-start"], catch_exceptions=False)

        assert result.exit_code == 0
        assert "session recorded" in result.output.lower()
        assert "6" in result.output  # sessions_total incremented

    def test_session_creates_profile_for_first_time_user(self, mock_home: Path) -> None:
        """Session creates new profile with name prompt for first-time users."""
        mock_home.mkdir(parents=True, exist_ok=True)

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            # Provide name via --name flag for non-interactive test
            result = runner.invoke(
                app,
                ["profile", "session-start", "--name", "New User"],
                catch_exceptions=False,
            )

        assert result.exit_code == 0
        assert "welcome" in result.output.lower() or "created" in result.output.lower()

        # Verify profile was created
        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            from raise_cli.onboarding.profile import load_developer_profile

            saved = load_developer_profile()
            assert saved is not None
            assert saved.name == "New User"
            assert saved.sessions_total == 1

    def test_session_adds_project_path(self, mock_home: Path) -> None:
        """Session adds project path when --project is provided."""
        mock_home.mkdir(parents=True, exist_ok=True)

        profile = DeveloperProfile(name="Test User", sessions_total=3)
        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            save_developer_profile(profile)

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(
                app,
                ["profile", "session-start", "--project", "/path/to/myproject"],
                catch_exceptions=False,
            )

        assert result.exit_code == 0

        # Verify project was added
        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            from raise_cli.onboarding.profile import load_developer_profile

            saved = load_developer_profile()
            assert saved is not None
            assert "/path/to/myproject" in saved.projects

    def test_session_updates_last_session_date(self, mock_home: Path) -> None:
        """Session updates last_session to today."""
        from datetime import date

        mock_home.mkdir(parents=True, exist_ok=True)

        profile = DeveloperProfile(name="Test User", sessions_total=10)
        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            save_developer_profile(profile)

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(app, ["profile", "session-start"], catch_exceptions=False)

        assert result.exit_code == 0

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            from raise_cli.onboarding.profile import load_developer_profile

            saved = load_developer_profile()
            assert saved is not None
            assert saved.last_session == date.today()

    def test_session_without_name_and_no_profile_shows_error(
        self, mock_home: Path
    ) -> None:
        """Session without --name when no profile exists shows helpful error."""
        mock_home.mkdir(parents=True, exist_ok=True)

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(app, ["profile", "session-start"], catch_exceptions=False)

        # Should fail gracefully with helpful message
        assert result.exit_code != 0 or "name" in result.output.lower()

    def test_session_warns_when_session_already_active(self, mock_home: Path) -> None:
        """Session shows note when a session is already active."""
        mock_home.mkdir(parents=True, exist_ok=True)

        # Create profile with active session
        profile = DeveloperProfile(
            name="Test User",
            sessions_total=5,
            current_session=CurrentSession(
                started_at=datetime.now(UTC),
                project="/previous/project",
            ),
        )
        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            save_developer_profile(profile)

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(
                app,
                ["profile", "session-start", "--project", "/new/project"],
                catch_exceptions=False,
            )

        assert result.exit_code == 0
        # Should show note about active session
        assert (
            "already active" in result.output.lower() or "note" in result.output.lower()
        )

    def test_session_warns_when_session_is_stale(self, mock_home: Path) -> None:
        """Session shows warning when previous session is stale (>24h)."""
        mock_home.mkdir(parents=True, exist_ok=True)

        # Create profile with stale session (25 hours ago)
        stale_time = datetime.now(UTC) - timedelta(hours=25)
        profile = DeveloperProfile(
            name="Test User",
            sessions_total=5,
            current_session=CurrentSession(
                started_at=stale_time,
                project="/old/project",
            ),
        )
        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            save_developer_profile(profile)

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(
                app,
                ["profile", "session-start", "--project", "/new/project"],
                catch_exceptions=False,
            )

        assert result.exit_code == 0
        # Should show warning about stale session
        assert "stale" in result.output.lower() or "warning" in result.output.lower()

    def test_session_sets_current_session_state(self, mock_home: Path) -> None:
        """Session sets current_session when --project is provided."""
        mock_home.mkdir(parents=True, exist_ok=True)

        profile = DeveloperProfile(name="Test User", sessions_total=3)
        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            save_developer_profile(profile)

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(
                app,
                ["profile", "session-start", "--project", "/my/project"],
                catch_exceptions=False,
            )

        assert result.exit_code == 0

        # Verify current_session was set
        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            from raise_cli.onboarding.profile import load_developer_profile

            saved = load_developer_profile()
            assert saved is not None
            assert saved.current_session is not None
            assert saved.current_session.project == "/my/project"


class TestProfileSessionEndCommand:
    """Tests for raise profile session-end command."""

    def test_session_end_clears_active_session(self, mock_home: Path) -> None:
        """session-end clears current_session."""
        mock_home.mkdir(parents=True, exist_ok=True)

        # Create profile with active session
        profile = DeveloperProfile(
            name="Test User",
            sessions_total=5,
            current_session=CurrentSession(
                started_at=datetime.now(UTC),
                project="/my/project",
            ),
        )
        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            save_developer_profile(profile)

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(
                app, ["profile", "session-end"], catch_exceptions=False
            )

        assert result.exit_code == 0
        assert "ended" in result.output.lower()

        # Verify session was cleared
        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            from raise_cli.onboarding.profile import load_developer_profile

            saved = load_developer_profile()
            assert saved is not None
            assert saved.current_session is None

    def test_session_end_no_active_session_is_noop(self, mock_home: Path) -> None:
        """session-end is a no-op when no session is active."""
        mock_home.mkdir(parents=True, exist_ok=True)

        profile = DeveloperProfile(name="Test User", sessions_total=5)
        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            save_developer_profile(profile)

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(
                app, ["profile", "session-end"], catch_exceptions=False
            )

        assert result.exit_code == 0
        assert "no active session" in result.output.lower()

    def test_session_end_no_profile_shows_error(self, mock_home: Path) -> None:
        """session-end shows error when no profile exists."""
        mock_home.mkdir(parents=True, exist_ok=True)

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(
                app, ["profile", "session-end"], catch_exceptions=False
            )

        assert result.exit_code != 0
        assert "no developer profile" in result.output.lower()
