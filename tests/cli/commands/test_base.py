"""Tests for rai info command (formerly base show)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from raise_cli.cli.main import app

runner = CliRunner()


class TestInfo:
    """Tests for rai info command."""

    def test_shows_base_version(self) -> None:
        """Should display base Rai version."""
        result = runner.invoke(app, ["info"])

        assert result.exit_code == 0
        assert "1.0.0" in result.output

    def test_shows_bundled_contents(self) -> None:
        """Should show identity files, patterns, methodology."""
        result = runner.invoke(app, ["info"])

        assert result.exit_code == 0
        assert "identity" in result.output.lower() or "Identity" in result.output
        assert "pattern" in result.output.lower() or "Pattern" in result.output
        assert "methodology" in result.output.lower() or "Methodology" in result.output

    def test_shows_installed_status_when_bootstrapped(self, tmp_path: Path) -> None:
        """Should show installed status when .raise/rai/identity/ exists."""
        identity_dir = tmp_path / ".raise" / "rai" / "identity"
        identity_dir.mkdir(parents=True)
        (identity_dir / "core.yaml").write_text("values: []")

        with patch(
            "raise_cli.cli.commands.info._get_project_root", return_value=tmp_path
        ):
            result = runner.invoke(app, ["info"])

        assert result.exit_code == 0
        assert "installed" in result.output.lower()

    def test_shows_not_installed_when_missing(self, tmp_path: Path) -> None:
        """Should show not installed when .raise/rai/ doesn't exist."""
        with patch(
            "raise_cli.cli.commands.info._get_project_root", return_value=tmp_path
        ):
            result = runner.invoke(app, ["info"])

        assert result.exit_code == 0
        assert "not installed" in result.output.lower()
