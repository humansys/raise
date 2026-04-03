"""Backwards-compat re-export. Import from raise_cli.mcp.bridge instead.

Architecture: ADR-042, E338 — McpBridge moved to raise_cli.mcp.bridge.
This shim exists for backwards compatibility with external consumers.
"""

from raise_cli.mcp.bridge import McpBridge, McpBridgeError  # noqa: F401
from raise_cli.mcp.models import McpToolInfo, McpToolResult  # noqa: F401

__all__ = ["McpBridge", "McpBridgeError", "McpToolInfo", "McpToolResult"]
