"""Tests for the raise init command."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from raise_cli.cli.main import app
from raise_cli.onboarding.detection import ProjectType
from raise_cli.onboarding.manifest import load_manifest
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


@pytest.fixture
def greenfield_project(tmp_path: Path) -> Path:
    """Create an empty greenfield project directory."""
    project = tmp_path / "greenfield-project"
    project.mkdir()
    return project


@pytest.fixture
def brownfield_project(tmp_path: Path) -> Path:
    """Create a brownfield project with code files."""
    project = tmp_path / "brownfield-project"
    project.mkdir()
    src = project / "src"
    src.mkdir()
    (src / "main.py").write_text("print('hello')")
    (src / "utils.py").write_text("def helper(): pass")
    (project / "app.py").write_text("from src import main")
    return project


class TestInitCommand:
    """Tests for raise init command."""

    def test_init_creates_manifest(
        self, greenfield_project: Path, mock_home: Path
    ) -> None:
        """Init creates .rai/manifest.yaml."""
        mock_home.mkdir(parents=True, exist_ok=True)

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(
                app, ["init", "--path", str(greenfield_project)], catch_exceptions=False
            )

        assert result.exit_code == 0
        manifest = load_manifest(greenfield_project)
        assert manifest is not None

    def test_init_greenfield_detection(
        self, greenfield_project: Path, mock_home: Path
    ) -> None:
        """Init detects greenfield project correctly."""
        mock_home.mkdir(parents=True, exist_ok=True)

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(
                app, ["init", "--path", str(greenfield_project)], catch_exceptions=False
            )

        assert result.exit_code == 0
        assert "greenfield" in result.output.lower()

        manifest = load_manifest(greenfield_project)
        assert manifest is not None
        assert manifest.project.project_type == ProjectType.GREENFIELD

    def test_init_brownfield_detection(
        self, brownfield_project: Path, mock_home: Path
    ) -> None:
        """Init detects brownfield project correctly."""
        mock_home.mkdir(parents=True, exist_ok=True)

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(
                app, ["init", "--path", str(brownfield_project)], catch_exceptions=False
            )

        assert result.exit_code == 0
        assert "brownfield" in result.output.lower()

        manifest = load_manifest(brownfield_project)
        assert manifest is not None
        assert manifest.project.project_type == ProjectType.BROWNFIELD
        assert manifest.project.code_file_count == 3

    def test_init_creates_new_profile(
        self, greenfield_project: Path, mock_home: Path
    ) -> None:
        """Init creates new developer profile if none exists."""
        mock_home.mkdir(parents=True, exist_ok=True)

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(
                app, ["init", "--path", str(greenfield_project)], catch_exceptions=False
            )

        assert result.exit_code == 0
        # Check profile was created
        profile_path = mock_home / "developer.yaml"
        assert profile_path.exists()

    def test_init_loads_existing_profile(
        self, greenfield_project: Path, mock_home: Path
    ) -> None:
        """Init loads existing developer profile."""
        mock_home.mkdir(parents=True, exist_ok=True)

        # Create existing profile
        existing_profile = DeveloperProfile(
            name="Test User",
            experience_level=ExperienceLevel.RI,
        )
        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            save_developer_profile(existing_profile)

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(
                app, ["init", "--path", str(greenfield_project)], catch_exceptions=False
            )

        assert result.exit_code == 0
        # Should welcome back existing user
        assert "test user" in result.output.lower() or "welcome back" in result.output.lower()


class TestInitOutputAdaptation:
    """Tests for experience-level adaptive output."""

    def test_shu_output_is_verbose(
        self, greenfield_project: Path, mock_home: Path
    ) -> None:
        """Shu users get verbose, educational output."""
        mock_home.mkdir(parents=True, exist_ok=True)

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(
                app, ["init", "--path", str(greenfield_project)], catch_exceptions=False
            )

        assert result.exit_code == 0
        # Shu output should include welcome and next steps
        output_lower = result.output.lower()
        assert "welcome" in output_lower or "rai" in output_lower
        assert "next" in output_lower or "/session-start" in result.output

    def test_ri_output_is_concise(
        self, greenfield_project: Path, mock_home: Path
    ) -> None:
        """Ri users get concise output."""
        mock_home.mkdir(parents=True, exist_ok=True)

        # Create Ri-level profile
        ri_profile = DeveloperProfile(
            name="Expert",
            experience_level=ExperienceLevel.RI,
        )
        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            save_developer_profile(ri_profile)

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(
                app, ["init", "--path", str(greenfield_project)], catch_exceptions=False
            )

        assert result.exit_code == 0
        # Ri output should be shorter (less verbose)
        # Check that it doesn't have the full welcome text
        output_lines = [line for line in result.output.split("\n") if line.strip()]
        # Ri output should be more concise
        assert len(output_lines) < 15  # Reasonable limit for concise output


class TestInitIdempotency:
    """Tests for init being safe to run multiple times."""

    def test_init_updates_existing_manifest(
        self, brownfield_project: Path, mock_home: Path
    ) -> None:
        """Running init again updates the manifest."""
        mock_home.mkdir(parents=True, exist_ok=True)

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            # First init
            result1 = runner.invoke(
                app, ["init", "--path", str(brownfield_project)], catch_exceptions=False
            )
            assert result1.exit_code == 0

            # Add more files
            (brownfield_project / "new_module.py").write_text("# new")

            # Second init
            result2 = runner.invoke(
                app, ["init", "--path", str(brownfield_project)], catch_exceptions=False
            )
            assert result2.exit_code == 0

        manifest = load_manifest(brownfield_project)
        assert manifest is not None
        assert manifest.project.code_file_count == 4  # 3 original + 1 new


class TestInitWithCustomName:
    """Tests for --name option."""

    def test_init_with_custom_name(
        self, greenfield_project: Path, mock_home: Path
    ) -> None:
        """Init uses custom name when provided."""
        mock_home.mkdir(parents=True, exist_ok=True)

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(
                app,
                ["init", "--path", str(greenfield_project), "--name", "my-custom-api"],
                catch_exceptions=False,
            )

        assert result.exit_code == 0
        manifest = load_manifest(greenfield_project)
        assert manifest is not None
        assert manifest.project.name == "my-custom-api"

    def test_init_defaults_to_directory_name(
        self, greenfield_project: Path, mock_home: Path
    ) -> None:
        """Init uses directory name when --name not provided."""
        mock_home.mkdir(parents=True, exist_ok=True)

        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            result = runner.invoke(
                app, ["init", "--path", str(greenfield_project)], catch_exceptions=False
            )

        assert result.exit_code == 0
        manifest = load_manifest(greenfield_project)
        assert manifest is not None
        assert manifest.project.name == "greenfield-project"
