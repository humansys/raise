"""Smoke test for rai backlog CLI wiring."""

from __future__ import annotations

from typer.testing import CliRunner

from raise_cli.cli.main import app

runner = CliRunner()

EXPECTED_COMMANDS = [
    "create",
    "get",
    "get-comments",
    "transition",
    "update",
    "link",
    "comment",
    "search",
    "batch-transition",
]


class TestBacklogSmoke:
    def test_help_lists_all_commands(self) -> None:
        """Rai backlog --help shows all 9 commands."""
        result = runner.invoke(app, ["backlog", "--help"])
        assert result.exit_code == 0
        for cmd in EXPECTED_COMMANDS:
            assert cmd in result.output, f"Command '{cmd}' missing from --help output"

    def test_no_demo_commands_registered(self) -> None:
        """Demo commands (auth, pull, push) are not registered as subcommands."""
        # Check each by invoking directly — should get "No such command".
        for cmd in ["auth", "pull", "push"]:
            cmd_result = runner.invoke(app, ["backlog", cmd])
            assert cmd_result.exit_code != 0, f"Demo command '{cmd}' still registered"
