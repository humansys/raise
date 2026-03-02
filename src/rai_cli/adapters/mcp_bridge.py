"""Backwards-compat re-export. Import from rai_cli.mcp.bridge instead.

Architecture: ADR-042, E338 — McpBridge moved to rai_cli.mcp.bridge.
This shim exists for backwards compatibility with external consumers.
"""

from rai_cli.mcp.bridge import McpBridge, McpBridgeError, McpToolInfo, McpToolResult

__all__ = ["McpBridge", "McpBridgeError", "McpToolInfo", "McpToolResult"]
