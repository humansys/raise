"""Tests for `rai mcp health` command."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

from typer.testing import CliRunner

from raise_cli.cli.main import app
from raise_cli.mcp.models import McpHealthResult
from raise_cli.mcp.schema import McpServerConfig, ServerConnection

runner = CliRunner()

_FAKE_SERVER = McpServerConfig(
    name="test-server",
    description="A test server",
    server=ServerConnection(command="echo", args=["server"]),
)


class TestMcpHealth:
    """Tests for `rai mcp health`."""

    def test_health_success(self) -> None:
        mock_bridge = AsyncMock()
        mock_bridge.health.return_value = McpHealthResult(
            server_name="test-server",
            healthy=True,
            message="OK, 3 tools",
            latency_ms=245,
            tool_count=3,
        )
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
            result = runner.invoke(app, ["mcp", "health", "test-server"])
        assert result.exit_code == 0
        assert "healthy" in result.output
        assert "3 tools" in result.output
        assert "245ms" in result.output

    def test_health_unhealthy(self) -> None:
        mock_bridge = AsyncMock()
        mock_bridge.health.return_value = McpHealthResult(
            server_name="test-server",
            healthy=False,
            message="Connection refused",
            latency_ms=50,
            tool_count=0,
        )
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
            result = runner.invoke(app, ["mcp", "health", "test-server"])
        assert result.exit_code != 0
        assert "unhealthy" in result.output
        assert "Connection refused" in result.output

    def test_health_server_not_found(self) -> None:
        with patch("raise_cli.cli.commands.mcp.discover_mcp_servers", return_value={}):
            result = runner.invoke(app, ["mcp", "health", "nonexistent"])
        assert result.exit_code != 0
        assert "not found" in result.output.lower()
