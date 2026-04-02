"""Tests for the raise profile command."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
import yaml
from typer.testing import CliRunner

from raise_cli.cli.main import app
from raise_cli.onboarding.profile import (
    DeveloperProfile,
    ExperienceLevel,
    save_developer_profile,
)
from raise_cli.onboarding.profile_portability import export_profile, serialize_bundle

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
        assert "rai init" in result.output.lower()

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


class TestProfileNoSubcommand:
    """Tests for rai profile (no subcommand) showing profile directly."""

    def test_profile_no_args_shows_profile_or_message(self, mock_home: Path) -> None:
        """Profile without subcommand shows profile data or helpful message."""
        mock_home.mkdir(parents=True, exist_ok=True)

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(app, ["profile"], catch_exceptions=False)

        assert result.exit_code == 0
        # Should show helpful message (no profile exists), not help text
        assert "no developer profile found" in result.output.lower()


def _make_test_profile() -> DeveloperProfile:
    """Create a test profile for export/import tests."""
    return DeveloperProfile(
        name="Test Dev",
        pattern_prefix="T",
        experience_level=ExperienceLevel.HA,
        skills_mastered=["tdd"],
        projects=["/old/machine/path"],
    )


class TestProfileExportCommand:
    """Tests for rai profile export command."""

    def test_export_outputs_yaml_to_stdout(self, mock_home: Path) -> None:
        """Export should output YAML bundle to stdout."""
        mock_home.mkdir(parents=True, exist_ok=True)
        profile = _make_test_profile()
        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            save_developer_profile(profile)

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(app, ["profile", "export"], catch_exceptions=False)

        assert result.exit_code == 0
        parsed = yaml.safe_load(result.output)
        assert "_meta" in parsed
        assert parsed["profile"]["name"] == "Test Dev"

    def test_export_writes_to_file(self, mock_home: Path, tmp_path: Path) -> None:
        """Export with --output should write to file."""
        mock_home.mkdir(parents=True, exist_ok=True)
        profile = _make_test_profile()
        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            save_developer_profile(profile)

        output_file = tmp_path / "bundle.yaml"
        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(
                app,
                ["profile", "export", "--output", str(output_file)],
                catch_exceptions=False,
            )

        assert result.exit_code == 0
        assert output_file.exists()
        parsed = yaml.safe_load(output_file.read_text())
        assert parsed["profile"]["name"] == "Test Dev"

    def test_export_fails_without_profile(self, mock_home: Path) -> None:
        """Export should fail when no profile exists."""
        mock_home.mkdir(parents=True, exist_ok=True)
        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(app, ["profile", "export"])

        assert result.exit_code != 0


class TestProfileImportCommand:
    """Tests for rai profile import command."""

    def test_import_creates_profile(self, mock_home: Path, tmp_path: Path) -> None:
        """Import should create profile from valid bundle."""
        mock_home.mkdir(parents=True, exist_ok=True)
        profile = _make_test_profile()
        bundle_str = serialize_bundle(export_profile(profile))
        bundle_file = tmp_path / "bundle.yaml"
        bundle_file.write_text(bundle_str)

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(
                app,
                ["profile", "import", str(bundle_file)],
                catch_exceptions=False,
            )

        assert result.exit_code == 0
        # Verify profile was saved
        profile_path = mock_home / "developer.yaml"
        assert profile_path.exists()

    def test_import_with_force_skips_confirmation(
        self, mock_home: Path, tmp_path: Path
    ) -> None:
        """Import --force should overwrite without prompting."""
        mock_home.mkdir(parents=True, exist_ok=True)
        # Create existing profile
        old_profile = DeveloperProfile(name="Old Name")
        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            save_developer_profile(old_profile)

        # Create bundle with new name
        new_profile = _make_test_profile()
        bundle_str = serialize_bundle(export_profile(new_profile))
        bundle_file = tmp_path / "bundle.yaml"
        bundle_file.write_text(bundle_str)

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(
                app,
                ["profile", "import", str(bundle_file), "--force"],
                catch_exceptions=False,
            )

        assert result.exit_code == 0
        assert "Test Dev" in result.output or "imported" in result.output.lower()

    def test_import_rejects_invalid_bundle(
        self, mock_home: Path, tmp_path: Path
    ) -> None:
        """Import should fail on invalid bundle."""
        mock_home.mkdir(parents=True, exist_ok=True)
        bad_file = tmp_path / "bad.yaml"
        bad_file.write_text("not: a valid bundle\n")

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(app, ["profile", "import", str(bad_file)])

        assert result.exit_code != 0
