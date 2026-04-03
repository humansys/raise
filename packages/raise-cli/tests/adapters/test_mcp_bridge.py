"""Tests for McpBridge — generic MCP server bridge.

Mocks at ClientSession level. Does NOT require mcp-atlassian installed.
Uses asyncio.run() for async tests (no pytest-asyncio dependency).
"""

from __future__ import annotations

import asyncio
import json
from contextlib import asynccontextmanager
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

mcp_types = pytest.importorskip("mcp.types", reason="mcp extra not installed")
TextContent = mcp_types.TextContent

from raise_cli.adapters.mcp_bridge import (  # noqa: E402
    McpBridge,
    McpBridgeError,
    McpToolInfo,
    McpToolResult,
)

# --- Helpers ---


def _run(coro: Any) -> Any:
    """Run async test coroutine synchronously."""
    return asyncio.run(coro)


def _make_text_content(text: str) -> TextContent:
    """Create a real TextContent instance."""
    return TextContent(type="text", text=text)


def _make_call_result(
    texts: list[str] | None = None,
    is_error: bool = False,
) -> Any:
    """Create a mock CallToolResult."""
    result = MagicMock()
    result.isError = is_error
    if texts is not None:
        result.content = [_make_text_content(t) for t in texts]
    else:
        result.content = []
    return result


def _make_tool(name: str, description: str = "") -> Any:
    """Create a mock Tool for list_tools response."""
    tool = MagicMock()
    tool.name = name
    tool.description = description
    return tool


def _make_list_tools_result(tools: list[Any]) -> Any:
    """Create a mock ListToolsResult."""
    result = MagicMock()
    result.tools = tools
    return result


@asynccontextmanager
async def _mock_stdio_client(params: Any, **kwargs: Any):
    """Mock stdio_client context manager yielding (read, write) streams."""
    yield (MagicMock(), MagicMock())


def _mock_session_class(
    call_tool_return: Any | None = None,
    list_tools_return: Any | None = None,
) -> tuple[Any, AsyncMock]:
    """Create a mock ClientSession class that works as async context manager."""
    session = AsyncMock()
    if call_tool_return is not None:
        session.call_tool.return_value = call_tool_return
    if list_tools_return is not None:
        session.list_tools.return_value = list_tools_return
    else:
        session.list_tools.return_value = _make_list_tools_result([])
    session.initialize = AsyncMock()

    @asynccontextmanager
    async def session_cm(read: Any, write: Any, **kwargs: Any):
        yield session

    return session_cm, session


def _patched_bridge(
    server: str = "mcp-test",
    call_tool_return: Any | None = None,
    list_tools_return: Any | None = None,
) -> tuple[McpBridge, Any, Any]:
    """Create bridge + patch context managers for stdio_client and ClientSession."""
    session_cm, session = _mock_session_class(
        call_tool_return=call_tool_return,
        list_tools_return=list_tools_return,
    )
    bridge = McpBridge(server_command=server)
    p1 = patch(
        "raise_cli.mcp.bridge.stdio_client",
        side_effect=_mock_stdio_client,
    )
    p2 = patch(
        "raise_cli.mcp.bridge.ClientSession",
        side_effect=session_cm,
    )
    return bridge, p1, p2, session  # type: ignore[return-value]


# =============================================================================
# McpToolResult model tests
# =============================================================================


class TestMcpToolResult:
    def test_defaults(self) -> None:
        r = McpToolResult()
        assert r.text == ""
        assert r.data == {}
        assert r.is_error is False
        assert r.error_message == ""

    def test_error_result(self) -> None:
        r = McpToolResult(is_error=True, error_message="auth failed")
        assert r.is_error is True
        assert r.error_message == "auth failed"

    def test_with_data(self) -> None:
        r = McpToolResult(text='{"key": "RAISE-1"}', data={"key": "RAISE-1"})
        assert r.data["key"] == "RAISE-1"


class TestMcpToolInfo:
    def test_minimal(self) -> None:
        info = McpToolInfo(name="jira_search")
        assert info.name == "jira_search"
        assert info.description == ""

    def test_with_description(self) -> None:
        info = McpToolInfo(name="jira_search", description="Search issues")
        assert info.description == "Search issues"


# =============================================================================
# McpBridge.call() tests
# =============================================================================


class TestMcpBridgeCall:
    def test_call_returns_parsed_text(self) -> None:
        """call() returns McpToolResult with text from TextContent."""
        data = {"key": "RAISE-301", "summary": "Test issue"}
        bridge, p1, p2, _ = _patched_bridge(
            call_tool_return=_make_call_result(texts=[json.dumps(data)])
        )

        async def run() -> McpToolResult:
            with p1, p2:
                return await bridge.call("jira_get_issue", {"issue_key": "RAISE-301"})

        result = _run(run())
        assert result.text == json.dumps(data)
        assert result.data == data
        assert result.is_error is False

    def test_call_with_error_result(self) -> None:
        """call() returns error McpToolResult when isError=True."""
        bridge, p1, p2, _ = _patched_bridge(
            call_tool_return=_make_call_result(
                texts=["401 Unauthorized"], is_error=True
            )
        )

        async def run() -> McpToolResult:
            with p1, p2:
                return await bridge.call("jira_search", {"jql": "invalid"})

        result = _run(run())
        assert result.is_error is True
        assert "401 Unauthorized" in result.error_message

    def test_call_with_empty_content(self) -> None:
        """call() handles empty content list gracefully."""
        bridge, p1, p2, _ = _patched_bridge(
            call_tool_return=_make_call_result(texts=None)
        )

        async def run() -> McpToolResult:
            with p1, p2:
                return await bridge.call("some_tool", {})

        result = _run(run())
        assert result.text == ""
        assert result.data == {}
        assert result.is_error is False

    def test_call_with_non_json_text(self) -> None:
        """call() keeps text as-is when content is not valid JSON."""
        bridge, p1, p2, _ = _patched_bridge(
            call_tool_return=_make_call_result(texts=["Operation successful"])
        )

        async def run() -> McpToolResult:
            with p1, p2:
                return await bridge.call("some_tool", {})

        result = _run(run())
        assert result.text == "Operation successful"
        assert result.data == {}

    def test_call_with_multiple_text_items(self) -> None:
        """call() joins multiple TextContent items."""
        bridge, p1, p2, _ = _patched_bridge(
            call_tool_return=_make_call_result(texts=["line 1", "line 2"])
        )

        async def run() -> McpToolResult:
            with p1, p2:
                return await bridge.call("some_tool", {})

        result = _run(run())
        assert result.text == "line 1\nline 2"

    def test_call_passes_correct_args_to_session(self) -> None:
        """call() forwards tool_name and arguments to session.call_tool()."""
        bridge, p1, p2, session = _patched_bridge(
            call_tool_return=_make_call_result(texts=["ok"])
        )

        async def run() -> None:
            with p1, p2:
                await bridge.call(
                    "jira_transition_issue",
                    {"issue_key": "RAISE-1", "transition_id": "41"},
                )

        _run(run())
        session.call_tool.assert_called_once_with(
            "jira_transition_issue",
            {"issue_key": "RAISE-1", "transition_id": "41"},
        )


# =============================================================================
# McpBridge._ensure_session error paths
# =============================================================================


class TestMcpBridgeSessionErrors:
    def test_server_not_found_raises_bridge_error(self) -> None:
        """FileNotFoundError from subprocess → McpBridgeError with install guidance."""

        @asynccontextmanager
        async def failing_stdio(params: Any, **kwargs: Any):
            raise FileNotFoundError("mcp-nonexistent")
            yield  # pragma: no cover  # noqa: E115

        bridge = McpBridge(server_command="mcp-nonexistent")

        async def run() -> None:
            with patch("raise_cli.mcp.bridge.stdio_client", side_effect=failing_stdio):
                await bridge.call("any_tool", {})

        with pytest.raises(McpBridgeError, match="not found"):
            _run(run())

    def test_connection_failure_raises_bridge_error(self) -> None:
        """Generic connection error → McpBridgeError with server name."""

        @asynccontextmanager
        async def failing_stdio(params: Any):
            raise ConnectionError("Connection refused")
            yield  # pragma: no cover  # noqa: E115

        bridge = McpBridge(server_command="mcp-broken")

        async def run() -> None:
            with patch("raise_cli.mcp.bridge.stdio_client", side_effect=failing_stdio):
                await bridge.call("any_tool", {})

        with pytest.raises(McpBridgeError, match="mcp-broken"):
            _run(run())

    def test_tool_call_exception_raises_bridge_error(self) -> None:
        """Exception during call_tool → McpBridgeError wrapping original."""
        bridge, p1, p2, session = _patched_bridge()
        session.call_tool.side_effect = RuntimeError("protocol error")

        async def run() -> None:
            with p1, p2:
                await bridge.call("failing_tool", {})

        with pytest.raises(McpBridgeError, match="protocol error"):
            _run(run())


# =============================================================================
# McpBridge.health() and list_tools()
# =============================================================================


class TestMcpBridgeHealth:
    def test_health_returns_healthy(self) -> None:
        """health() returns McpHealthResult with tool count when server responds."""
        tools = [_make_tool("tool_a", "desc A"), _make_tool("tool_b", "desc B")]
        bridge, p1, p2, _ = _patched_bridge(
            list_tools_return=_make_list_tools_result(tools)
        )

        async def run():  # type: ignore[return]
            with p1, p2:
                return await bridge.health()

        health = _run(run())
        assert health.healthy is True
        assert health.server_name == "mcp-test"
        assert "2 tools" in health.message
        assert health.latency_ms is not None
        assert health.latency_ms >= 0
        assert health.tool_count == 2

    def test_health_returns_unhealthy_on_error(self) -> None:
        """health() returns unhealthy McpHealthResult when connection fails."""

        @asynccontextmanager
        async def failing_stdio(params: Any, **kwargs: Any):
            raise FileNotFoundError("mcp-test")
            yield  # pragma: no cover  # noqa: E115

        bridge = McpBridge(server_command="mcp-test")

        async def run():  # type: ignore[return]
            with patch("raise_cli.mcp.bridge.stdio_client", side_effect=failing_stdio):
                return await bridge.health()

        health = _run(run())
        assert health.healthy is False
        assert "not found" in health.message.lower()

    def test_list_tools_returns_tool_info(self) -> None:
        """list_tools() returns list of McpToolInfo."""
        tools = [_make_tool("jira_search", "Search Jira"), _make_tool("jira_get_issue")]
        bridge, p1, p2, _ = _patched_bridge(
            list_tools_return=_make_list_tools_result(tools)
        )

        async def run():  # type: ignore[return]
            with p1, p2:
                return await bridge.list_tools()

        result = _run(run())
        assert len(result) == 2
        assert result[0].name == "jira_search"
        assert result[0].description == "Search Jira"
        assert result[1].name == "jira_get_issue"
        assert result[1].description == ""


# =============================================================================
# Telemetry (logfire spans)
# =============================================================================


# =============================================================================
# _parse_result — JSON array handling (D6, S301.5)
# =============================================================================


class TestParseResultArrays:
    def test_json_array_wrapped_in_items(self) -> None:
        """JSON array response is wrapped in {"items": [...]} for dict access."""
        pages = [
            {"id": "123", "title": "Page A"},
            {"id": "456", "title": "Page B"},
        ]
        bridge, p1, p2, _ = _patched_bridge(
            call_tool_return=_make_call_result(texts=[json.dumps(pages)])
        )

        async def run() -> McpToolResult:
            with p1, p2:
                return await bridge.call("confluence_search", {"query": "test"})

        result = _run(run())
        assert result.data["items"] == pages
        assert len(result.data["items"]) == 2
        assert result.data["items"][0]["title"] == "Page A"

    def test_json_dict_still_works(self) -> None:
        """Regression: dict responses remain unchanged after array support."""
        data = {"key": "RAISE-1", "summary": "Test"}
        bridge, p1, p2, _ = _patched_bridge(
            call_tool_return=_make_call_result(texts=[json.dumps(data)])
        )

        async def run() -> McpToolResult:
            with p1, p2:
                return await bridge.call("jira_get_issue", {"issue_key": "RAISE-1"})

        result = _run(run())
        assert result.data == data
        assert "items" not in result.data

    def test_empty_array_wrapped(self) -> None:
        """Empty JSON array is wrapped as {"items": []}."""
        bridge, p1, p2, _ = _patched_bridge(
            call_tool_return=_make_call_result(texts=["[]"])
        )

        async def run() -> McpToolResult:
            with p1, p2:
                return await bridge.call("confluence_search", {"query": "nothing"})

        result = _run(run())
        assert result.data == {"items": []}


class TestMcpBridgeTelemetry:
    def test_span_attributes_on_success(self) -> None:
        """Successful call sets mcp_server, mcp_tool, duration_ms, success."""
        data = {"key": "RAISE-1"}
        bridge, p1, p2, _ = _patched_bridge(
            server="mcp-atlassian",
            call_tool_return=_make_call_result(texts=[json.dumps(data)]),
        )

        async def run() -> None:
            with p1, p2, patch("raise_cli.mcp.bridge.logfire") as mock_logfire:
                mock_span = MagicMock()
                mock_logfire.span.return_value.__enter__ = MagicMock(
                    return_value=mock_span
                )
                mock_logfire.span.return_value.__exit__ = MagicMock(return_value=False)
                await bridge.call("jira_get_issue", {"issue_key": "RAISE-1"})

                mock_logfire.span.assert_called_once()
                call_kwargs = mock_logfire.span.call_args
                assert call_kwargs[0][0] == "mcp.tool_call"
                assert call_kwargs[1]["mcp_server"] == "mcp-atlassian"
                assert call_kwargs[1]["mcp_tool"] == "jira_get_issue"

        _run(run())

    def test_span_attributes_on_failure(self) -> None:
        """Failed call still records span with success=False."""
        bridge, p1, p2, session = _patched_bridge(server="mcp-atlassian")
        session.call_tool.side_effect = RuntimeError("boom")

        async def run() -> None:
            with p1, p2, patch("raise_cli.mcp.bridge.logfire") as mock_logfire:
                mock_span = MagicMock()
                mock_logfire.span.return_value.__enter__ = MagicMock(
                    return_value=mock_span
                )
                mock_logfire.span.return_value.__exit__ = MagicMock(return_value=False)

                with pytest.raises(McpBridgeError):
                    await bridge.call("failing_tool", {})

                mock_span.set_attribute.assert_any_call("success", False)

        _run(run())


# =============================================================================
# McpBridge.aclose() — RAISE-324 fix
# =============================================================================


class TestMcpBridgeAclose:
    def test_aclose_resets_session_and_stack(self) -> None:
        """aclose() clears session and cm_stack."""
        bridge, p1, p2, _ = _patched_bridge(
            call_tool_return=_make_call_result(texts=["ok"])
        )

        async def run() -> None:
            with p1, p2:
                await bridge.call("some_tool", {})
                assert bridge._session is not None
                assert bridge._cm_stack is not None
                await bridge.aclose()
                assert bridge._session is None
                assert bridge._cm_stack is None

        _run(run())

    def test_aclose_idempotent(self) -> None:
        """aclose() is safe to call multiple times."""
        bridge = McpBridge(server_command="mcp-test")

        async def run() -> None:
            await bridge.aclose()  # No session — should not raise
            await bridge.aclose()

        _run(run())

    def test_cleanup_delegates_to_aclose(self) -> None:
        """_cleanup() delegates to aclose()."""
        bridge, p1, p2, _ = _patched_bridge(
            call_tool_return=_make_call_result(texts=["ok"])
        )

        async def run() -> None:
            with p1, p2:
                await bridge.call("some_tool", {})
                assert bridge._session is not None
                await bridge._cleanup()
                assert bridge._session is None

        _run(run())
