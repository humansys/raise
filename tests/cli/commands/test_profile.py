"""Tests for the raise profile command."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from raise_cli.cli.main import app
from raise_cli.onboarding.profile import (
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


class TestProfileHelp:
    """Tests for profile command help."""

    def test_profile_no_args_shows_help(self) -> None:
        """Profile without subcommand shows help."""
        result = runner.invoke(app, ["profile"])

        # no_args_is_help=True causes exit code 0 or 2
        assert result.exit_code in (0, 2)
        assert "show" in result.output

    def test_profile_show_help(self) -> None:
        """Profile show --help shows usage."""
        result = runner.invoke(app, ["profile", "show", "--help"])

        assert result.exit_code == 0
        assert "Display the developer profile" in result.output
