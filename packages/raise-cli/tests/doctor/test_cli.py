"""Tests for rai doctor CLI command.

Uses a mock registry so tests are CI-safe (no dependency on CWD having
a .raise/ directory or specific project structure).
"""

from typing import ClassVar
from unittest.mock import patch

from typer.testing import CliRunner

from raise_cli.cli.main import app
from raise_cli.doctor.models import CheckResult, CheckStatus, DoctorContext

runner = CliRunner()


class _PassingCheck:
    """Dummy check that always passes."""

    check_id: ClassVar[str] = "test-pass"
    category: ClassVar[str] = "environment"
    description: ClassVar[str] = "always passes"
    requires_online: ClassVar[bool] = False

    def evaluate(self, context: DoctorContext) -> list[CheckResult]:
        return [
            CheckResult(
                check_id=self.check_id,
                category=self.category,
                status=CheckStatus.PASS,
                message="all good",
            )
        ]


def _mock_discover(self: object) -> None:
    """Replace real discovery with a single passing check."""
    self._checks = [_PassingCheck()]  # type: ignore[attr-defined]


class TestDoctorCLI:
    @patch("raise_cli.doctor.registry.CheckRegistry.discover", _mock_discover)
    def test_doctor_runs_without_error(self) -> None:
        """Rai doctor should run without crashing."""
        result = runner.invoke(app, ["doctor"])
        assert result.exit_code == 0

    @patch("raise_cli.doctor.registry.CheckRegistry.discover", _mock_discover)
    def test_doctor_json_output(self) -> None:
        result = runner.invoke(app, ["doctor", "--json"])
        assert result.exit_code == 0
        assert '"results"' in result.output
        assert '"summary"' in result.output

    @patch("raise_cli.doctor.registry.CheckRegistry.discover", _mock_discover)
    def test_doctor_verbose(self) -> None:
        result = runner.invoke(app, ["doctor", "-v"])
        assert result.exit_code == 0

    def test_doctor_unknown_category(self) -> None:
        result = runner.invoke(app, ["doctor", "--category", "nonexistent"])
        assert result.exit_code == 1
        assert "Unknown category" in result.output

    def test_doctor_help(self) -> None:
        result = runner.invoke(app, ["doctor", "--help"])
        assert result.exit_code == 0
        assert "Diagnose" in result.output
