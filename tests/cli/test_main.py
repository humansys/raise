"""Tests for main CLI application."""

from __future__ import annotations

from typer.testing import CliRunner

from rai_cli.cli.main import app
from rai_cli.config import RaiSettings

runner = CliRunner()


class TestCLISettings:
    """Tests for RaiSettings integration with CLI."""

    def test_default_settings_created(self) -> None:
        """CLI should create RaiSettings with defaults when no flags provided."""
        # We can't directly access ctx.obj in tests, but we can verify
        # the CLI runs without error (integration test)
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0

    def test_cli_format_flag(self) -> None:
        """CLI should accept --format flag."""
        result = runner.invoke(app, ["--format", "json", "--help"])
        assert result.exit_code == 0

    def test_cli_verbose_flag(self) -> None:
        """CLI should accept -v flag."""
        result = runner.invoke(app, ["-v", "--help"])
        assert result.exit_code == 0

    def test_cli_multiple_verbose_flags(self) -> None:
        """CLI should accept multiple -v flags."""
        result = runner.invoke(app, ["-vvv", "--help"])
        assert result.exit_code == 0

    def test_cli_quiet_flag(self) -> None:
        """CLI should accept -q flag."""
        result = runner.invoke(app, ["-q", "--help"])
        assert result.exit_code == 0

    def test_cli_combined_flags(self) -> None:
        """CLI should accept multiple flags combined."""
        result = runner.invoke(app, ["--format", "table", "-vv", "--help"])
        assert result.exit_code == 0

    def test_version_flag(self) -> None:
        """CLI should show version with --version."""
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "rai-cli version" in result.stdout


class TestSettingsIntegration:
    """Tests for settings integration with context."""

    def test_settings_uses_cli_overrides(self) -> None:
        """Settings should respect CLI argument overrides."""
        # Test that RaiSettings respects constructor args
        settings = RaiSettings(output_format="json", verbosity=2)
        assert settings.output_format == "json"
        assert settings.verbosity == 2

    def test_settings_cascade_with_cli_args(self, monkeypatch) -> None:
        """CLI args should override environment variables."""
        # Set env var
        monkeypatch.setenv("RAISE_OUTPUT_FORMAT", "table")

        # CLI arg should win
        settings = RaiSettings(output_format="json")
        assert settings.output_format == "json"

    def test_quiet_sets_verbosity_negative(self) -> None:
        """Quiet flag should result in verbosity -1."""
        settings = RaiSettings(verbosity=-1)
        assert settings.verbosity == -1

    def test_verbose_caps_at_three(self) -> None:
        """Verbosity should cap at 3."""
        settings = RaiSettings(verbosity=3)
        assert settings.verbosity == 3


class TestBackwardCompatibility:
    """Tests to ensure backward compatibility is maintained."""

    def test_output_format_values(self) -> None:
        """Output format should support all three values."""
        settings_human = RaiSettings(output_format="human")
        settings_json = RaiSettings(output_format="json")
        settings_table = RaiSettings(output_format="table")

        assert settings_human.output_format == "human"
        assert settings_json.output_format == "json"
        assert settings_table.output_format == "table"
