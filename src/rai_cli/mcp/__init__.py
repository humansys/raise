"""MCP infrastructure layer — independent of domain adapters.

Provides generic MCP server management: bridge, models, schema, registry.
Domain adapters (PM, Docs) live in ``rai_cli.adapters`` and consume this layer.

Architecture: ADR-042, E338
"""

from rai_cli.mcp.bridge import McpBridge, McpBridgeError
from rai_cli.mcp.models import McpHealthResult, McpToolInfo, McpToolResult
from rai_cli.mcp.schema import McpServerConfig, ServerConnection

__all__ = [
    "McpBridge",
    "McpBridgeError",
    "McpHealthResult",
    "McpServerConfig",
    "McpToolInfo",
    "McpToolResult",
    "ServerConnection",
]
