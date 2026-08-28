"""Shared FastMCP instance for rai-workspace MCP server.

All domain modules import this instance and register tools via @mcp.tool().
The entrypoint (mcp_server.py) imports all domain modules and calls mcp.run().
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("rai-workspace")
