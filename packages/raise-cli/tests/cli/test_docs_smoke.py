"""Smoke test for rai docs CLI wiring."""

from __future__ import annotations

from typer.testing import CliRunner

from raise_cli.cli.main import app

runner = CliRunner()

EXPECTED_COMMANDS = ["publish", "get", "search"]


class TestDocsSmoke:
    def test_help_lists_all_commands(self) -> None:
        """Rai docs --help shows all 3 commands."""
        result = runner.invoke(app, ["docs", "--help"])
        assert result.exit_code == 0
        for cmd in EXPECTED_COMMANDS:
            assert cmd in result.output, f"Command '{cmd}' missing from --help output"
