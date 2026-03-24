"""MCP server management commands.

Provides CLI access to registered MCP servers via the McpBridge.
Token-efficient by design: `rai mcp call` invokes tools without
injecting tool schemas into agent context (ADR-042, E338).
"""

from __future__ import annotations

import asyncio
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Annotated, Any

import typer
import yaml
from rich.console import Console
from rich.table import Table

from raise_cli.hooks.emitter import create_emitter
from raise_cli.hooks.events import McpCallEvent
from raise_cli.mcp.models import McpHealthResult
from raise_cli.mcp.registry import discover_mcp_servers
from raise_cli.mcp.schema import McpServerConfig, ServerConnection

mcp_app = typer.Typer(
    name="mcp",
    help="Manage and invoke MCP servers registered in .raise/mcp/",
    no_args_is_help=True,
)

console = Console(stderr=True)


def _lazy_bridge(
    server_command: str,
    server_args: list[str] | None = None,
    env: dict[str, str] | None = None,
) -> Any:
    """Lazy-import McpBridge and instantiate. Avoids requiring mcp SDK at CLI startup."""
    from raise_cli.mcp.bridge import McpBridge

    return McpBridge(server_command=server_command, server_args=server_args, env=env)


def _lazy_bridge_error() -> type:
    """Lazy-import McpBridgeError."""
    from raise_cli.mcp.bridge import McpBridgeError

    return McpBridgeError


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
    bridge = _lazy_bridge(
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
        bridge = _lazy_bridge(
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
        console.print(f"[red]{config.name}[/red]: unhealthy — {result.message}")
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
        bridge = _lazy_bridge(
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
    except Exception as exc:
        if isinstance(exc, _lazy_bridge_error()):
            console.print(f"Error: {exc}")
            raise typer.Exit(1) from exc
        raise

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
    verbose: Annotated[
        bool,
        typer.Option("--verbose", help="Show call details on stderr"),
    ] = False,
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

    # Call tool with latency measurement
    emitter = create_emitter()
    start = time.monotonic()
    try:
        result = asyncio.run(_call_tool(config, tool, arguments))
        elapsed_ms = int((time.monotonic() - start) * 1000)
        emitter.emit(
            McpCallEvent(
                server=server,
                tool=tool,
                success=True,
                latency_ms=elapsed_ms,
            )
        )
        if verbose:
            console.print(f"mcp:call {server}/{tool} — ok ({elapsed_ms}ms)")
    except Exception as exc:
        elapsed_ms = int((time.monotonic() - start) * 1000)
        emitter.emit(
            McpCallEvent(
                server=server,
                tool=tool,
                success=False,
                latency_ms=elapsed_ms,
                error=str(exc),
            )
        )
        if verbose:
            console.print(f"mcp:call {server}/{tool} — error ({elapsed_ms}ms): {exc}")
        console.print(f"Error: {exc}")
        raise typer.Exit(1) from exc

    # Output JSON to stdout (not stderr console)
    stdout = Console()
    stdout.print_json(json.dumps(result))


def _write_mcp_config(
    *,
    name: str,
    server_command: str,
    server_args: list[str],
    env_list: list[str] | None,
    tool_names: list[str],
    out_dir: Path,
    force: bool,
    source: str = "scaffold",
) -> Path:
    """Write .raise/mcp/<name>.yaml with overwrite protection.

    Shared by ``scaffold`` and ``install`` commands. Returns the written path.

    Raises:
        typer.Exit: If file exists and ``force`` is False.
    """
    out_path = out_dir / f"{name}.yaml"

    if out_path.exists() and not force:
        console.print(f"Error: {out_path} already exists. Use --force to overwrite.")
        raise typer.Exit(1)

    config_data = McpServerConfig(
        name=name,
        server=ServerConnection(command=server_command, args=server_args, env=env_list),
    )

    out_dir.mkdir(parents=True, exist_ok=True)

    header = f"# Generated by: rai mcp {source} {name}\n"
    if tool_names:
        header += f"# Discovered tools: {', '.join(tool_names)}\n"
    yaml_content = yaml.dump(
        config_data.model_dump(exclude_none=True),
        default_flow_style=False,
        sort_keys=False,
    )
    out_path.write_text(header + yaml_content)
    return out_path


@mcp_app.command()
def scaffold(
    name: Annotated[
        str, typer.Argument(help="Server name (used as filename and config name)")
    ],
    command: Annotated[
        str, typer.Option("--command", help="Server command (e.g. 'npx', 'uvx')")
    ],
    args: Annotated[
        str,
        typer.Option("--args", help="Server arguments as space-separated string"),
    ] = "",
    env: Annotated[
        str,
        typer.Option(
            "--env", help="Comma-separated env var names (e.g. 'TOKEN,API_KEY')"
        ),
    ] = "",
    force: Annotated[
        bool,
        typer.Option("--force", help="Overwrite existing config file"),
    ] = False,
    mcp_dir: Annotated[
        str,
        typer.Option("--mcp-dir", help="MCP config directory", hidden=True),
    ] = "",
) -> None:
    """Connect to an MCP server, introspect tools, and generate config.

    Creates a .raise/mcp/<name>.yaml config file by connecting to the
    server, discovering available tools, and writing a valid McpServerConfig.

    Example:
        rai mcp scaffold context7 --command npx --args "-y @upstash/context7-mcp"
    """
    out_dir = Path(mcp_dir) if mcp_dir else Path.cwd() / ".raise" / "mcp"

    # Early overwrite check — fail before connecting to server
    out_path = out_dir / f"{name}.yaml"
    if out_path.exists() and not force:
        console.print(f"Error: {out_path} already exists. Use --force to overwrite.")
        raise typer.Exit(1)

    server_args = args.split() if args else []
    env_list = [e.strip() for e in env.split(",") if e.strip()] or None

    # Connect and introspect
    async def _introspect() -> list[str]:
        bridge = _lazy_bridge(
            server_command=command,
            server_args=server_args,
        )
        try:
            tool_list = await bridge.list_tools()
            return [t.name for t in tool_list]
        finally:
            await bridge.aclose()

    try:
        tool_names = asyncio.run(_introspect())
    except Exception as exc:
        console.print(f"Error: {exc}")
        raise typer.Exit(1) from exc

    out_path = _write_mcp_config(
        name=name,
        server_command=command,
        server_args=server_args,
        env_list=env_list,
        tool_names=tool_names,
        out_dir=out_dir,
        force=force,
        source="scaffold",
    )
    Console().print(f"Created {out_path} ({len(tool_names)} tools discovered)")


# --- Type strategies for install ---

_TYPE_STRATEGIES: dict[str, tuple[str, list[str]]] = {
    "npx": ("npx", ["-y"]),
    "uvx": ("uvx", []),
}


def _build_server_config(
    pkg_type: str,
    package: str,
    module: str | None,
) -> tuple[str, list[str]]:
    """Return (command, args) for the given package type."""
    if pkg_type == "pip":
        assert module is not None  # noqa: S101 -- validated before calling
        return "python", ["-m", module]
    base_cmd, base_args = _TYPE_STRATEGIES[pkg_type]
    return base_cmd, [*base_args, package]


@mcp_app.command()
def install(
    package: Annotated[
        str, typer.Argument(help="Package identifier (e.g. '@upstash/context7-mcp')")
    ],
    pkg_type: Annotated[
        str,
        typer.Option("--type", help="Package type: uvx, npx, or pip"),
    ],
    name: Annotated[str, typer.Option("--name", help="Server name for config file")],
    env: Annotated[
        str,
        typer.Option("--env", help="Comma-separated env var names"),
    ] = "",
    module: Annotated[
        str,
        typer.Option("--module", help="Python module name (required for --type pip)"),
    ] = "",
    force: Annotated[
        bool,
        typer.Option("--force", help="Overwrite existing config file"),
    ] = False,
    mcp_dir: Annotated[
        str,
        typer.Option("--mcp-dir", help="MCP config directory", hidden=True),
    ] = "",
) -> None:
    """Install an MCP server package and generate config.

    Installs the package (pip only), verifies connectivity via health check,
    and generates .raise/mcp/<name>.yaml.

    Examples:
        rai mcp install @upstash/context7-mcp --type npx --name context7
        rai mcp install mcp-github --type uvx --name github --env GITHUB_TOKEN
        rai mcp install mcp-server-fetch --type pip --name fetch --module mcp_server_fetch
    """
    # Validate type
    valid_types: set[str] = {"uvx", "npx", "pip"}
    if pkg_type not in valid_types:
        console.print(
            f"Error: Invalid --type '{pkg_type}'. Must be one of: {', '.join(sorted(valid_types))}"
        )
        raise typer.Exit(1)

    # Validate pip requires --module
    if pkg_type == "pip" and not module:
        console.print("Error: --module is required when --type is pip")
        raise typer.Exit(1)

    out_dir = Path(mcp_dir) if mcp_dir else Path.cwd() / ".raise" / "mcp"

    # Early overwrite check
    out_path = out_dir / f"{name}.yaml"
    if out_path.exists() and not force:
        console.print(f"Error: {out_path} already exists. Use --force to overwrite.")
        raise typer.Exit(1)

    # pip: install package first
    if pkg_type == "pip":
        console.print(f"Installing {package} via pip...")
        pip_result = subprocess.run(
            [sys.executable, "-m", "pip", "install", package],
            capture_output=True,
            text=True,
        )
        if pip_result.returncode != 0:
            console.print(f"Error: pip install failed: {pip_result.stderr}")
            raise typer.Exit(1)

    # Build command/args from type strategy
    server_command, server_args = _build_server_config(
        pkg_type,
        package,
        module or None,
    )
    env_list = [e.strip() for e in env.split(",") if e.strip()] or None

    # Health check — non-fatal
    tool_names: list[str] = []
    health_ok = True

    async def _check() -> list[str]:
        bridge = _lazy_bridge(
            server_command=server_command,
            server_args=server_args,
        )
        try:
            tools = await bridge.list_tools()
            return [t.name for t in tools]
        finally:
            await bridge.aclose()

    try:
        tool_names = asyncio.run(_check())
    except Exception as exc:
        health_ok = False
        console.print(f"Warning: Health check failed: {exc}")

    # Write config
    written = _write_mcp_config(
        name=name,
        server_command=server_command,
        server_args=server_args,
        env_list=env_list,
        tool_names=tool_names,
        out_dir=out_dir,
        force=True,  # already checked above
        source="install",
    )

    status = "healthy" if health_ok else "unhealthy (check config)"
    Console().print(f"Created {written} ({len(tool_names)} tools, {status})")
