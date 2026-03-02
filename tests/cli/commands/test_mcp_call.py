"""Tests for `rai mcp call` command."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, patch

from typer.testing import CliRunner

from rai_cli.cli.main import app
from rai_cli.mcp.models import McpToolResult
from rai_cli.mcp.schema import McpServerConfig, ServerConnection

runner = CliRunner()

_FAKE_SERVER = McpServerConfig(
    name="test-server",
    description="A test server",
    server=ServerConnection(command="echo", args=["server"]),
)


class TestMcpCallServerNotFound:
    """Server not in registry → exit 1 + error."""

    def test_server_not_found(self) -> None:
        with patch(
            "rai_cli.cli.commands.mcp.discover_mcp_servers", return_value={}
        ):
            result = runner.invoke(app, ["mcp", "call", "nonexistent", "tool"])
        assert result.exit_code != 0
        assert "nonexistent" in result.output
        assert "not found" in result.output.lower()


class TestMcpCallInvalidJson:
    """Invalid --args JSON → exit 1 + error."""

    def test_invalid_args_json(self) -> None:
        with patch(
            "rai_cli.cli.commands.mcp.discover_mcp_servers",
            return_value={"test-server": _FAKE_SERVER},
        ):
            result = runner.invoke(
                app, ["mcp", "call", "test-server", "tool", "--args", "{bad}"]
            )
        assert result.exit_code != 0
        assert "invalid" in result.output.lower() or "json" in result.output.lower()


class TestMcpCallSuccess:
    """Successful tool call → exit 0 + JSON output."""

    def test_call_success_json_output(self) -> None:
        mock_result = McpToolResult(
            text='{"answer": 42}',
            data={"answer": 42},
            is_error=False,
            error_message="",
        )
        mock_bridge = AsyncMock()
        mock_bridge.call.return_value = mock_result
        mock_bridge.aclose.return_value = None

        with (
            patch(
                "rai_cli.cli.commands.mcp.discover_mcp_servers",
                return_value={"test-server": _FAKE_SERVER},
            ),
            patch(
                "rai_cli.cli.commands.mcp.McpBridge",
                return_value=mock_bridge,
            ),
        ):
            result = runner.invoke(
                app,
                [
                    "mcp", "call", "test-server", "some-tool",
                    "--args", '{"query": "test"}',
                ],
            )
        assert result.exit_code == 0
        output = json.loads(result.output)
        assert output["data"] == {"answer": 42}
        assert output["is_error"] is False

    def test_call_without_args(self) -> None:
        mock_result = McpToolResult(text="ok", data={})
        mock_bridge = AsyncMock()
        mock_bridge.call.return_value = mock_result
        mock_bridge.aclose.return_value = None

        with (
            patch(
                "rai_cli.cli.commands.mcp.discover_mcp_servers",
                return_value={"test-server": _FAKE_SERVER},
            ),
            patch(
                "rai_cli.cli.commands.mcp.McpBridge",
                return_value=mock_bridge,
            ),
        ):
            result = runner.invoke(
                app, ["mcp", "call", "test-server", "ping"]
            )
        assert result.exit_code == 0
        output = json.loads(result.output)
        assert output["text"] == "ok"
        # Called with empty dict when no --args
        mock_bridge.call.assert_called_once_with("ping", {})


class TestMcpCallBridgeError:
    """Bridge error → exit 1 + error message."""

    def test_bridge_error(self) -> None:
        mock_bridge = AsyncMock()
        mock_bridge.call.side_effect = Exception("Connection refused")
        mock_bridge.aclose.return_value = None

        with (
            patch(
                "rai_cli.cli.commands.mcp.discover_mcp_servers",
                return_value={"test-server": _FAKE_SERVER},
            ),
            patch(
                "rai_cli.cli.commands.mcp.McpBridge",
                return_value=mock_bridge,
            ),
        ):
            result = runner.invoke(
                app, ["mcp", "call", "test-server", "tool"]
            )
        assert result.exit_code != 0
        assert "Connection refused" in result.output
