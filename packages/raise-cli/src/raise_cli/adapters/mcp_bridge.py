"""Backwards-compat re-export. Import from raise_cli.mcp.bridge instead.

Architecture: ADR-042, E338 — McpBridge moved to raise_cli.mcp.bridge.
This shim exists for backwards compatibility with external consumers.
"""

from raise_cli.mcp.bridge import McpBridge, McpBridgeError
from raise_cli.mcp.models import McpToolInfo, McpToolResult

__all__ = ["McpBridge", "McpBridgeError", "McpToolInfo", "McpToolResult"]
