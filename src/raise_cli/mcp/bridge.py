"""Generic MCP server bridge using the official MCP Python SDK.

Manages server process lifecycle, async session, and RaiSE telemetry.
Works with any MCP server via stdio transport.

Architecture: E301 epic design (D1, D3, D4), moved to raise_cli.mcp (ADR-042, E338)
"""

from __future__ import annotations

import contextlib
import json
import logging
import subprocess
import time
from contextlib import AsyncExitStack
from typing import TYPE_CHECKING, Any

try:
    import logfire_api as logfire
except ModuleNotFoundError:  # pragma: no cover
    logfire = None  # type: ignore[assignment]

from raise_cli.mcp.models import McpHealthResult, McpToolInfo, McpToolResult

_MCP_AVAILABLE = False

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    from mcp.types import TextContent

    _MCP_AVAILABLE = True  # pyright: ignore[reportConstantRedefinition]
except ModuleNotFoundError:  # pragma: no cover
    if TYPE_CHECKING:
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
        from mcp.types import TextContent

logger = logging.getLogger(__name__)


class McpBridgeError(Exception):
    """Raised when MCP bridge operations fail."""


class McpBridge:
    """Generic async bridge to any MCP server via official Python SDK.

    Manages server process lifecycle, session, and RaiSE telemetry.
    Session is lazy — created on first call, reused if alive,
    reconnected if dead.

    Args:
        server_command: Command to start MCP server (e.g. "mcp-atlassian").
        server_args: Optional args for the server command.
        env: Optional environment variables. None = inherit parent env.
    """

    def __init__(
        self,
        server_command: str,
        server_args: list[str] | None = None,
        env: dict[str, str] | None = None,
    ) -> None:
        if not _MCP_AVAILABLE:
            raise McpBridgeError(
                "The 'mcp' package is required but not installed. "
                "Install it with: pip install raise-cli[mcp]"
            )
        self._server_command = server_command
        self._server_args = server_args or []
        self._env = env  # None = subprocess inherits os.environ
        self._session: ClientSession | None = None
        self._cm_stack: AsyncExitStack | None = None

    async def call(self, tool_name: str, arguments: dict[str, Any]) -> McpToolResult:
        """Call a tool on the MCP server.

        Wraps ClientSession.call_tool() with telemetry and error handling.

        Args:
            tool_name: MCP tool name (e.g. "jira_get_issue").
            arguments: Tool arguments dict.

        Returns:
            Parsed McpToolResult.

        Raises:
            McpBridgeError: On connection or tool call failure.
        """
        span_cm = (
            logfire.span(
                "mcp.tool_call",
                mcp_server=self._server_command,
                mcp_tool=tool_name,
            )
            if logfire is not None
            else contextlib.nullcontext()
        )
        with span_cm as span:
            start = time.monotonic()
            session = await self._ensure_session()
            try:
                result = await session.call_tool(tool_name, arguments)
                elapsed_ms = int((time.monotonic() - start) * 1000)
                if span is not None:
                    span.set_attribute("duration_ms", elapsed_ms)
                    span.set_attribute("success", not result.isError)
                return self._parse_result(result)
            except Exception as exc:
                elapsed_ms = int((time.monotonic() - start) * 1000)
                if span is not None:
                    span.set_attribute("duration_ms", elapsed_ms)
                    span.set_attribute("success", False)
                raise McpBridgeError(f"Tool call '{tool_name}' failed: {exc}") from exc

    async def list_tools(self) -> list[McpToolInfo]:
        """List available tools on the server."""
        session = await self._ensure_session()
        result = await session.list_tools()
        return [
            McpToolInfo(name=t.name, description=t.description or "")
            for t in result.tools
        ]

    async def health(self) -> McpHealthResult:
        """Check server connectivity and tool availability."""
        start = time.monotonic()
        try:
            tools = await self.list_tools()
            elapsed_ms = int((time.monotonic() - start) * 1000)
            return McpHealthResult(
                server_name=self._server_command,
                healthy=True,
                message=f"OK, {len(tools)} tools",
                latency_ms=elapsed_ms,
                tool_count=len(tools),
            )
        except Exception as exc:
            elapsed_ms = int((time.monotonic() - start) * 1000)
            return McpHealthResult(
                server_name=self._server_command,
                healthy=False,
                message=str(exc),
                latency_ms=elapsed_ms,
            )

    async def _ensure_session(self) -> ClientSession:
        """Lazy connect. Reconnects if session is closed/dead."""
        if self._session is not None:
            try:
                await self._session.list_tools()
                return self._session
            except Exception:
                await self._cleanup()

        params = StdioServerParameters(
            command=self._server_command,
            args=self._server_args,
            env=self._env,
        )
        stack = AsyncExitStack()
        try:
            # Redirect MCP server stderr to devnull to suppress banner/warning noise.
            # Server errors are captured via MCP protocol (isError), not stderr.
            # subprocess.DEVNULL is an int constant (-3) accepted by anyio.open_process;
            # avoids sync open() in async context — asyncio forbids blocking I/O in event loop.
            read, write = await stack.enter_async_context(
                stdio_client(params, errlog=subprocess.DEVNULL)  # type: ignore[arg-type]
            )
            session = await stack.enter_async_context(ClientSession(read, write))
            await session.initialize()
        except FileNotFoundError as exc:
            await stack.aclose()
            raise McpBridgeError(
                f"MCP server '{self._server_command}' not found. "
                f"Install the server and ensure it's on PATH."
            ) from exc
        except Exception as exc:
            await stack.aclose()
            raise McpBridgeError(
                f"Failed to connect to MCP server '{self._server_command}': {exc}"
            ) from exc

        self._session = session
        self._cm_stack = stack
        return session

    async def aclose(self) -> None:
        """Close session and exit stack.

        Must be called within the same event loop that created the session.
        Prevents asyncgen finalizer tracebacks from stdio_client.
        """
        if self._cm_stack:
            with contextlib.suppress(Exception):
                await self._cm_stack.aclose()
        self._session = None
        self._cm_stack = None

    async def _cleanup(self) -> None:
        """Alias for aclose() — used internally by _ensure_session."""
        await self.aclose()

    @staticmethod
    def _parse_result(result: Any) -> McpToolResult:
        """Parse CallToolResult into McpToolResult.

        Handles: empty content, multiple text items, non-text content,
        isError flag, and JSON auto-parsing.
        """
        if result.isError:
            texts = [c.text for c in result.content if isinstance(c, TextContent)]
            error_text = "\n".join(texts) if texts else "Unknown error"
            return McpToolResult(is_error=True, error_message=error_text)

        # Collect all text content, ignore non-text
        texts = [c.text for c in result.content if isinstance(c, TextContent)]
        text = "\n".join(texts) if texts else ""

        # Try parse as JSON for structured access
        data: dict[str, Any] = {}
        if text:
            try:
                parsed: Any = json.loads(text)
                if isinstance(parsed, dict):
                    data = parsed  # type: ignore[assignment]
                elif isinstance(parsed, list):
                    data = {"items": parsed}
            except json.JSONDecodeError:
                pass

        return McpToolResult(text=text, data=data)
