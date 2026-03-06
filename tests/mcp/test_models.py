"""Tests for MCP infrastructure models (T2).

Verifies McpHealthResult, McpToolResult, McpToolInfo live in raise_cli.mcp.models.
"""

from __future__ import annotations


def test_health_result_fields() -> None:
    """McpHealthResult has all required fields."""
    from raise_cli.mcp.models import McpHealthResult

    result = McpHealthResult(
        server_name="test-server",
        healthy=True,
        message="OK, 5 tools",
        latency_ms=42,
        tool_count=5,
    )
    assert result.server_name == "test-server"
    assert result.healthy is True
    assert result.message == "OK, 5 tools"
    assert result.latency_ms == 42
    assert result.tool_count == 5


def test_health_result_defaults() -> None:
    """McpHealthResult has sensible defaults."""
    from raise_cli.mcp.models import McpHealthResult

    result = McpHealthResult(server_name="x", healthy=False)
    assert result.message == ""
    assert result.latency_ms is None
    assert result.tool_count == 0


def test_tool_result_in_models() -> None:
    """McpToolResult importable from raise_cli.mcp.models."""
    from raise_cli.mcp.models import McpToolResult

    result = McpToolResult(text="hello", data={"k": "v"})
    assert result.text == "hello"
    assert result.is_error is False


def test_tool_info_in_models() -> None:
    """McpToolInfo importable from raise_cli.mcp.models."""
    from raise_cli.mcp.models import McpToolInfo

    info = McpToolInfo(name="my_tool", description="desc")
    assert info.name == "my_tool"


def test_bridge_no_adapter_models_import() -> None:
    """Bridge module must NOT import from raise_cli.adapters.models."""
    import inspect

    from raise_cli.mcp import bridge

    source = inspect.getsource(bridge)
    assert "raise_cli.adapters.models" not in source, (
        "Bridge still imports from adapters.models — must use own models"
    )
