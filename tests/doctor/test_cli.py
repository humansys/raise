"""Tests for rai doctor CLI command."""

from typer.testing import CliRunner

from rai_cli.cli.main import app

runner = CliRunner()


class TestDoctorCLI:
    def test_doctor_runs_without_error(self) -> None:
        """rai doctor should run without crashing (even with no checks)."""
        result = runner.invoke(app, ["doctor"])
        assert result.exit_code == 0

    def test_doctor_json_output(self) -> None:
        result = runner.invoke(app, ["doctor", "--json"])
        assert result.exit_code == 0
        assert '"results"' in result.output
        assert '"summary"' in result.output

    def test_doctor_verbose(self) -> None:
        result = runner.invoke(app, ["doctor", "-v"])
        assert result.exit_code == 0

    def test_doctor_unknown_category(self) -> None:
        result = runner.invoke(app, ["doctor", "nonexistent"])
        assert result.exit_code == 1
        assert "Unknown category" in result.output

    def test_doctor_help(self) -> None:
        result = runner.invoke(app, ["doctor", "--help"])
        assert result.exit_code == 0
        assert "Diagnose" in result.output
