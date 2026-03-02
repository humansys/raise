"""MCP server management commands.

Provides CLI access to registered MCP servers via the McpBridge.
Token-efficient by design: `rai mcp call` invokes tools without
injecting tool schemas into agent context (ADR-042, E338).
"""

from __future__ import annotations

import asyncio
import json
import os
from typing import Annotated, Any

import typer
from rich.console import Console

from rai_cli.mcp.bridge import McpBridge, McpBridgeError
from rai_cli.mcp.registry import discover_mcp_servers
from rai_cli.mcp.schema import McpServerConfig

mcp_app = typer.Typer(
    name="mcp",
    help="Manage and invoke MCP servers registered in .raise/mcp/",
    no_args_is_help=True,
)

console = Console(stderr=True)


def _resolve_env(config: McpServerConfig) -> dict[str, str] | None:
    """Build env dict from ServerConnection.env var names."""
    env_names = config.server.env
    if not env_names:
        return None
    return {
        **os.environ,
        **{k: os.environ.get(k, "") for k in env_names},
    }


async def _call_tool(
    config: McpServerConfig, tool_name: str, arguments: dict[str, Any]
) -> dict[str, Any]:
    """Connect to MCP server, call tool, return result as dict."""
    bridge = McpBridge(
        server_command=config.server.command,
        server_args=config.server.args,
        env=_resolve_env(config),
    )
    try:
        result = await bridge.call(tool_name, arguments)
        return result.model_dump()
    finally:
        await bridge.aclose()


@mcp_app.command()
def call(
    server: Annotated[str, typer.Argument(help="Registered MCP server name")],
    tool: Annotated[str, typer.Argument(help="Tool name to invoke")],
    args: Annotated[
        str,
        typer.Option("--args", help="Tool arguments as JSON string"),
    ] = "{}",
) -> None:
    """Invoke a tool on a registered MCP server.

    Looks up the server in .raise/mcp/ registry, connects via McpBridge,
    calls the specified tool, and prints the result as JSON to stdout.

    Example:
        rai mcp call context7 resolve-library-id --args '{"query":"next.js","libraryName":"next.js"}'
    """
    # Discover servers
    servers = discover_mcp_servers()
    if server not in servers:
        console.print(f"Error: Server '{server}' not found in registry.")
        available = ", ".join(sorted(servers)) if servers else "(none)"
        console.print(f"Available servers: {available}")
        raise typer.Exit(1)

    # Parse arguments
    try:
        arguments: dict[str, Any] = json.loads(args)
    except json.JSONDecodeError as exc:
        console.print(f"Error: Invalid JSON in --args: {exc}")
        raise typer.Exit(1) from exc

    # Call tool
    config = servers[server]
    try:
        result = asyncio.run(_call_tool(config, tool, arguments))
    except McpBridgeError as exc:
        console.print(f"Error: {exc}")
        raise typer.Exit(1) from exc
    except Exception as exc:
        console.print(f"Error: {exc}")
        raise typer.Exit(1) from exc

    # Output JSON to stdout (not stderr console)
    stdout = Console()
    stdout.print_json(json.dumps(result))
