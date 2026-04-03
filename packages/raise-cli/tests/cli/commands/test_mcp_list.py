"""Tests for `rai mcp list` command."""

from __future__ import annotations

from unittest.mock import patch

from typer.testing import CliRunner

from raise_cli.cli.main import app
from raise_cli.mcp.schema import McpServerConfig, ServerConnection

runner = CliRunner()

_SERVERS = {
    "context7": McpServerConfig(
        name="context7",
        description="Library documentation search",
        server=ServerConnection(command="npx", args=["-y", "@upstash/context7-mcp"]),
    ),
    "sonar": McpServerConfig(
        name="sonar",
        description=None,
        server=ServerConnection(command="uvx", args=["mcp-sonar"]),
    ),
}


class TestMcpList:
    """Tests for `rai mcp list`."""

    def test_list_shows_servers(self) -> None:
        with patch(
            "raise_cli.cli.commands.mcp.discover_mcp_servers",
            return_value=_SERVERS,
        ):
            result = runner.invoke(app, ["mcp", "list"])
        assert result.exit_code == 0
        assert "context7" in result.output
        assert "sonar" in result.output
        assert "Library documentation search" in result.output

    def test_list_no_servers(self) -> None:
        with patch(
            "raise_cli.cli.commands.mcp.discover_mcp_servers",
            return_value={},
        ):
            result = runner.invoke(app, ["mcp", "list"])
        assert result.exit_code == 0
        assert "no" in result.output.lower() or "No" in result.output
