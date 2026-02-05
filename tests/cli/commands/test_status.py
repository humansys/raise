"""Tests for the raise status command."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from raise_cli.cli.main import app
from raise_cli.onboarding.profile import DeveloperProfile, save_developer_profile

runner = CliRunner()


@pytest.fixture
def mock_home(tmp_path: Path) -> Path:
    """Provide a temporary home directory for tests."""
    return tmp_path / "home"


@pytest.fixture
def initialized_project(tmp_path: Path) -> Path:
    """Create an initialized RaiSE project."""
    project = tmp_path / "project"
    project.mkdir()
    raise_dir = project / ".raise"
    raise_dir.mkdir()
    (raise_dir / "manifest.yaml").write_text("name: test-project\ntype: brownfield\n")
    return project


class TestStatusCommand:
    """Tests for raise status command."""

    def test_status_shows_initialized_project(
        self, initialized_project: Path, mock_home: Path
    ) -> None:
        """Status shows project info when initialized."""
        mock_home.mkdir(parents=True, exist_ok=True)

        with (
            patch("raise_cli.cli.commands.status.Path.cwd", return_value=initialized_project),
            patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home),
        ):
            result = runner.invoke(app, ["status"], catch_exceptions=False)

        assert result.exit_code == 0
        assert "test-project" in result.output.lower() or "initialized" in result.output.lower()

    def test_status_shows_not_initialized(self, tmp_path: Path, mock_home: Path) -> None:
        """Status shows warning when project not initialized."""
        project = tmp_path / "empty-project"
        project.mkdir()
        mock_home.mkdir(parents=True, exist_ok=True)

        with (
            patch("raise_cli.cli.commands.status.Path.cwd", return_value=project),
            patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home),
        ):
            result = runner.invoke(app, ["status"], catch_exceptions=False)

        assert result.exit_code == 0
        assert "not initialized" in result.output.lower() or "raise init" in result.output.lower()

    def test_status_shows_developer_profile(
        self, initialized_project: Path, mock_home: Path
    ) -> None:
        """Status shows developer profile info."""
        mock_home.mkdir(parents=True, exist_ok=True)

        profile = DeveloperProfile(
            name="Test Dev",
            sessions_total=15,
        )
        with patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home):
            save_developer_profile(profile)

        with (
            patch("raise_cli.cli.commands.status.Path.cwd", return_value=initialized_project),
            patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home),
        ):
            result = runner.invoke(app, ["status"], catch_exceptions=False)

        assert result.exit_code == 0
        assert "test dev" in result.output.lower()

    def test_status_shows_no_profile(
        self, initialized_project: Path, mock_home: Path
    ) -> None:
        """Status shows message when no developer profile."""
        mock_home.mkdir(parents=True, exist_ok=True)

        with (
            patch("raise_cli.cli.commands.status.Path.cwd", return_value=initialized_project),
            patch("raise_cli.onboarding.profile.get_rai_home", return_value=mock_home),
        ):
            result = runner.invoke(app, ["status"], catch_exceptions=False)

        assert result.exit_code == 0
        assert "no profile" in result.output.lower() or "not configured" in result.output.lower()
