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
from rich.table import Table

from rai_cli.mcp.bridge import McpBridge, McpBridgeError
from rai_cli.mcp.models import McpHealthResult
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


def _lookup_server(
    server_name: str, servers: dict[str, McpServerConfig]
) -> McpServerConfig:
    """Look up server in registry or exit with error."""
    if server_name not in servers:
        console.print(f"Error: Server '{server_name}' not found in registry.")
        available = ", ".join(sorted(servers)) if servers else "(none)"
        console.print(f"Available servers: {available}")
        raise typer.Exit(1)
    return servers[server_name]


@mcp_app.command("list")
def list_servers() -> None:
    """List all registered MCP servers.

    Shows servers configured in .raise/mcp/*.yaml with their names,
    descriptions, and commands.
    """
    servers = discover_mcp_servers()
    if not servers:
        console.print("No MCP servers registered in .raise/mcp/")
        return

    table = Table(title="MCP Servers (.raise/mcp/)")
    table.add_column("Name", style="bold")
    table.add_column("Description")
    table.add_column("Command")

    for config in servers.values():
        cmd = f"{config.server.command} {' '.join(config.server.args)}"
        table.add_row(
            config.name,
            config.description or "",
            cmd[:50] + "..." if len(cmd) > 50 else cmd,
        )

    Console().print(table)


@mcp_app.command()
def health(
    server: Annotated[str, typer.Argument(help="Registered MCP server name")],
) -> None:
    """Check connectivity of a registered MCP server.

    Connects to the server, lists tools, and reports status, latency,
    and tool count.
    """
    servers = discover_mcp_servers()
    config = _lookup_server(server, servers)

    async def _check() -> McpHealthResult:
        bridge = McpBridge(
            server_command=config.server.command,
            server_args=config.server.args,
            env=_resolve_env(config),
        )
        try:
            return await bridge.health()
        finally:
            await bridge.aclose()

    result = asyncio.run(_check())
    if result.healthy:
        Console().print(
            f"[green]{config.name}[/green]: healthy "
            f"({result.tool_count} tools, {result.latency_ms}ms)"
        )
    else:
        console.print(
            f"[red]{config.name}[/red]: unhealthy — {result.message}"
        )
        raise typer.Exit(1)


@mcp_app.command()
def tools(
    server: Annotated[str, typer.Argument(help="Registered MCP server name")],
) -> None:
    """List available tools on a registered MCP server.

    Connects to the server and retrieves the list of tools with their
    names and descriptions.
    """
    servers = discover_mcp_servers()
    config = _lookup_server(server, servers)

    async def _list() -> list[tuple[str, str]]:
        bridge = McpBridge(
            server_command=config.server.command,
            server_args=config.server.args,
            env=_resolve_env(config),
        )
        try:
            tool_list = await bridge.list_tools()
            return [(t.name, t.description) for t in tool_list]
        finally:
            await bridge.aclose()

    try:
        tool_info = asyncio.run(_list())
    except McpBridgeError as exc:
        console.print(f"Error: {exc}")
        raise typer.Exit(1) from exc

    if not tool_info:
        Console().print(f"No tools found on {config.name}")
        return

    table = Table(title=f"Tools for {config.name}")
    table.add_column("Tool", style="bold")
    table.add_column("Description")
    for name, desc in tool_info:
        table.add_row(name, desc)
    Console().print(table)


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
    config = _lookup_server(server, servers)

    # Parse arguments
    try:
        arguments: dict[str, Any] = json.loads(args)
    except json.JSONDecodeError as exc:
        console.print(f"Error: Invalid JSON in --args: {exc}")
        raise typer.Exit(1) from exc
    try:
        result = asyncio.run(_call_tool(config, tool, arguments))
    except Exception as exc:
        console.print(f"Error: {exc}")
        raise typer.Exit(1) from exc

    # Output JSON to stdout (not stderr console)
    stdout = Console()
    stdout.print_json(json.dumps(result))
