"""Tests for `rai mcp call` command."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

from typer.testing import CliRunner

from raise_cli.cli.main import app
from raise_cli.mcp.models import McpToolResult
from raise_cli.mcp.schema import McpServerConfig, ServerConnection

runner = CliRunner()

_FAKE_SERVER = McpServerConfig(
    name="test-server",
    description="A test server",
    server=ServerConnection(command="echo", args=["server"]),
)


class TestMcpCallServerNotFound:
    """Server not in registry → exit 1 + error."""

    def test_server_not_found(self) -> None:
        with patch("raise_cli.cli.commands.mcp.discover_mcp_servers", return_value={}):
            result = runner.invoke(app, ["mcp", "call", "nonexistent", "tool"])
        assert result.exit_code != 0
        assert "nonexistent" in result.output
        assert "not found" in result.output.lower()


class TestMcpCallInvalidJson:
    """Invalid --args JSON → exit 1 + error."""

    def test_invalid_args_json(self) -> None:
        with patch(
            "raise_cli.cli.commands.mcp.discover_mcp_servers",
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
                "raise_cli.cli.commands.mcp.discover_mcp_servers",
                return_value={"test-server": _FAKE_SERVER},
            ),
            patch(
                "raise_cli.mcp.bridge.McpBridge",
                return_value=mock_bridge,
            ),
        ):
            result = runner.invoke(
                app,
                [
                    "mcp",
                    "call",
                    "test-server",
                    "some-tool",
                    "--args",
                    '{"query": "test"}',
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
                "raise_cli.cli.commands.mcp.discover_mcp_servers",
                return_value={"test-server": _FAKE_SERVER},
            ),
            patch(
                "raise_cli.mcp.bridge.McpBridge",
                return_value=mock_bridge,
            ),
        ):
            result = runner.invoke(app, ["mcp", "call", "test-server", "ping"])
        assert result.exit_code == 0
        output = json.loads(result.output)
        assert output["text"] == "ok"
        # Called with empty dict when no --args
        mock_bridge.call.assert_called_once_with("ping", {})


class TestMcpCallToolError:
    """Tool returns is_error=True → exit 0 + JSON with is_error flag."""

    def test_tool_error_in_result(self) -> None:
        mock_result = McpToolResult(
            text="",
            data={},
            is_error=True,
            error_message="Library not found",
        )
        mock_bridge = AsyncMock()
        mock_bridge.call.return_value = mock_result
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
            result = runner.invoke(
                app, ["mcp", "call", "test-server", "query-docs", "--args", "{}"]
            )
        assert result.exit_code == 0
        output = json.loads(result.output)
        assert output["is_error"] is True
        assert output["error_message"] == "Library not found"


class TestMcpCallBridgeError:
    """Bridge error → exit 1 + error message."""

    def test_bridge_error(self) -> None:
        mock_bridge = AsyncMock()
        mock_bridge.call.side_effect = Exception("Connection refused")
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
            result = runner.invoke(app, ["mcp", "call", "test-server", "tool"])
        assert result.exit_code != 0
        assert "Connection refused" in result.output


class TestMcpCallEmitsEvent:
    """McpCallEvent emitted on success and failure."""

    def test_emits_event_on_success(self) -> None:
        mock_result = McpToolResult(text="ok", data={})
        mock_bridge = AsyncMock()
        mock_bridge.call.return_value = mock_result
        mock_bridge.aclose.return_value = None
        mock_emitter = MagicMock()

        with (
            patch(
                "raise_cli.cli.commands.mcp.discover_mcp_servers",
                return_value={"test-server": _FAKE_SERVER},
            ),
            patch(
                "raise_cli.mcp.bridge.McpBridge",
                return_value=mock_bridge,
            ),
            patch(
                "raise_cli.cli.commands.mcp.create_emitter",
                return_value=mock_emitter,
            ),
        ):
            result = runner.invoke(app, ["mcp", "call", "test-server", "ping"])
        assert result.exit_code == 0
        mock_emitter.emit.assert_called_once()
        event = mock_emitter.emit.call_args[0][0]
        assert event.event_name == "mcp:call"
        assert event.server == "test-server"
        assert event.tool == "ping"
        assert event.success is True
        assert event.latency_ms >= 0

    def test_emits_event_on_failure(self) -> None:
        mock_bridge = AsyncMock()
        mock_bridge.call.side_effect = Exception("timeout")
        mock_bridge.aclose.return_value = None
        mock_emitter = MagicMock()

        with (
            patch(
                "raise_cli.cli.commands.mcp.discover_mcp_servers",
                return_value={"test-server": _FAKE_SERVER},
            ),
            patch(
                "raise_cli.mcp.bridge.McpBridge",
                return_value=mock_bridge,
            ),
            patch(
                "raise_cli.cli.commands.mcp.create_emitter",
                return_value=mock_emitter,
            ),
        ):
            result = runner.invoke(app, ["mcp", "call", "test-server", "bad-tool"])
        assert result.exit_code != 0
        mock_emitter.emit.assert_called_once()
        event = mock_emitter.emit.call_args[0][0]
        assert event.success is False
        assert "timeout" in event.error


class TestMcpCallVerbose:
    """--verbose flag shows call details on stderr."""

    def test_verbose_success(self) -> None:
        mock_result = McpToolResult(text="ok", data={})
        mock_bridge = AsyncMock()
        mock_bridge.call.return_value = mock_result
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
            patch(
                "raise_cli.cli.commands.mcp.create_emitter",
                return_value=MagicMock(),
            ),
        ):
            result = runner.invoke(
                app, ["mcp", "call", "test-server", "ping", "--verbose"]
            )
        assert result.exit_code == 0
        assert "test-server" in result.output
        assert "ping" in result.output
        assert "ok" in result.output.lower() or "ms" in result.output

    def test_verbose_failure(self) -> None:
        mock_bridge = AsyncMock()
        mock_bridge.call.side_effect = Exception("Connection refused")
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
            patch(
                "raise_cli.cli.commands.mcp.create_emitter",
                return_value=MagicMock(),
            ),
        ):
            result = runner.invoke(
                app, ["mcp", "call", "test-server", "tool", "--verbose"]
            )
        assert result.exit_code != 0
        assert "test-server" in result.output
