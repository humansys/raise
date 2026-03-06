"""Tests for `rai mcp tools` command."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

from typer.testing import CliRunner

from raise_cli.cli.main import app
from raise_cli.mcp.models import McpToolInfo
from raise_cli.mcp.schema import McpServerConfig, ServerConnection

runner = CliRunner()

_FAKE_SERVER = McpServerConfig(
    name="test-server",
    description="A test server",
    server=ServerConnection(command="echo", args=["server"]),
)


class TestMcpTools:
    """Tests for `rai mcp tools`."""

    def test_tools_success(self) -> None:
        mock_bridge = AsyncMock()
        mock_bridge.list_tools.return_value = [
            McpToolInfo(name="resolve-library-id", description="Resolve lib ID"),
            McpToolInfo(name="query-docs", description="Query documentation"),
        ]
        mock_bridge.aclose.return_value = None

        with (
            patch(
                "raise_cli.cli.commands.mcp.discover_mcp_servers",
                return_value={"test-server": _FAKE_SERVER},
            ),
            patch(
                "raise_cli.mcp.bridge.McpBridge",
                return_value=mock_bridge,
            ),
        ):
            result = runner.invoke(app, ["mcp", "tools", "test-server"])
        assert result.exit_code == 0
        assert "resolve-library-id" in result.output
        assert "query-docs" in result.output
        assert "Resolve lib ID" in result.output

    def test_tools_server_not_found(self) -> None:
        with patch("raise_cli.cli.commands.mcp.discover_mcp_servers", return_value={}):
            result = runner.invoke(app, ["mcp", "tools", "nonexistent"])
        assert result.exit_code != 0
        assert "not found" in result.output.lower()
