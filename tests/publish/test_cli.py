"""Tests for publish CLI commands."""

from __future__ import annotations

from unittest.mock import patch

from typer.testing import CliRunner

from rai_cli.cli.main import app
from rai_cli.publish.check import CheckResult

runner = CliRunner()


class TestPublishCheck:
    """Test `rai publish check` command."""

    def test_check_command_exists(self) -> None:
        result = runner.invoke(app, ["publish", "check", "--help"])
        assert result.exit_code == 0
        assert "quality" in result.output.lower() or "check" in result.output.lower()

    def test_check_all_pass(self) -> None:
        mock_results = [
            CheckResult(gate="Tests pass", passed=True, message="OK"),
            CheckResult(gate="Type checks", passed=True, message="OK"),
            CheckResult(gate="Lint clean", passed=True, message="OK"),
            CheckResult(gate="Security scan", passed=True, message="OK"),
            CheckResult(gate="Coverage", passed=True, message="OK"),
            CheckResult(gate="Build succeeds", passed=True, message="OK"),
            CheckResult(gate="Package validates", passed=True, message="OK"),
            CheckResult(gate="CHANGELOG", passed=True, message="OK"),
            CheckResult(gate="Version PEP 440", passed=True, message="OK"),
            CheckResult(gate="Version sync", passed=True, message="OK"),
        ]
        with patch(
            "rai_cli.cli.commands.publish.run_checks", return_value=mock_results
        ):
            result = runner.invoke(app, ["publish", "check"])
        assert result.exit_code == 0

    def test_check_failure_exits_nonzero(self) -> None:
        mock_results = [
            CheckResult(gate="Tests pass", passed=False, message="3 failed"),
            CheckResult(gate="Type checks", passed=True, message="OK"),
        ]
        with patch(
            "rai_cli.cli.commands.publish.run_checks", return_value=mock_results
        ):
            result = runner.invoke(app, ["publish", "check"])
        assert result.exit_code != 0


class TestPublishRelease:
    """Test `rai publish release` command."""

    def test_release_command_exists(self) -> None:
        result = runner.invoke(app, ["publish", "release", "--help"])
        assert result.exit_code == 0
        assert "bump" in result.output.lower()

    def test_release_dry_run(self) -> None:
        mock_results = [
            CheckResult(gate=f"Gate {i}", passed=True, message="OK")
            for i in range(10)
        ]
        with (
            patch(
                "rai_cli.cli.commands.publish.run_checks", return_value=mock_results
            ),
            patch(
                "rai_cli.cli.commands.publish._read_current_version",
                return_value="2.0.0a7",
            ),
        ):
            result = runner.invoke(app, ["publish", "release", "--bump", "alpha", "--dry-run"])
        assert result.exit_code == 0
        assert "2.0.0a8" in result.output
        assert "dry" in result.output.lower()

    def test_release_requires_bump_or_version(self) -> None:
        result = runner.invoke(app, ["publish", "release"])
        assert result.exit_code != 0
