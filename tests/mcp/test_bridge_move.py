"""Tests for McpBridge move to raise_cli.mcp.bridge (T1).

Verifies canonical import path and backwards-compat shim.
"""

from __future__ import annotations


def test_canonical_import_mcpbridge() -> None:
    """McpBridge importable from new canonical path."""
    from raise_cli.mcp.bridge import McpBridge

    assert McpBridge is not None


def test_canonical_import_error() -> None:
    """McpBridgeError importable from new canonical path."""
    from raise_cli.mcp.bridge import McpBridgeError

    assert issubclass(McpBridgeError, Exception)


def test_canonical_import_tool_result() -> None:
    """McpToolResult importable from new canonical path."""
    from raise_cli.mcp.bridge import McpToolResult

    result = McpToolResult(text="hello", data={"key": "val"})
    assert result.text == "hello"


def test_canonical_import_tool_info() -> None:
    """McpToolInfo importable from new canonical path."""
    from raise_cli.mcp.bridge import McpToolInfo

    info = McpToolInfo(name="test_tool", description="A test tool")
    assert info.name == "test_tool"


def test_shim_import_mcpbridge() -> None:
    """McpBridge still importable from old path (backwards compat shim)."""
    from raise_cli.adapters.mcp_bridge import McpBridge

    assert McpBridge is not None


def test_shim_import_error() -> None:
    """McpBridgeError still importable from old path."""
    from raise_cli.adapters.mcp_bridge import McpBridgeError

    assert issubclass(McpBridgeError, Exception)


def test_shim_import_tool_result() -> None:
    """McpToolResult still importable from old path."""
    from raise_cli.adapters.mcp_bridge import McpToolResult

    assert McpToolResult is not None


def test_shim_import_tool_info() -> None:
    """McpToolInfo still importable from old path."""
    from raise_cli.adapters.mcp_bridge import McpToolInfo

    assert McpToolInfo is not None


def test_canonical_and_shim_are_same_class() -> None:
    """Both import paths resolve to the same class."""
    from raise_cli.adapters.mcp_bridge import McpBridge as ShimBridge
    from raise_cli.mcp.bridge import McpBridge as CanonicalBridge

    assert CanonicalBridge is ShimBridge
