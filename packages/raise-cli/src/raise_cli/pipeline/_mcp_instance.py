"""Shared FastMCP instance for rai-workspace MCP server.

All domain modules import this instance and register tools via @mcp.tool().
The entrypoint (mcp_server.py) imports all domain modules and calls mcp.run().

RAISE-17624 — why this is a *subclass* and not a wrapper or a monkeypatch:
every rai-workspace tool reports failure as a normal return value
(``json.dumps({"status": "error", ...})``, 65 sites across 10 modules), so
FastMCP — which only sets protocol-level ``isError=True`` when a tool
*raises* — hands the client a success envelope around an error payload.
``FastMCP._setup_handlers()`` binds ``self.call_tool`` to the lowlevel
handler during ``__init__``, so assigning ``mcp.call_tool = ...`` afterwards
is silently ignored, and ``@mcp.tool()`` returns the undecorated function so
registration cannot see return values either. Overriding ``call_tool`` on a
subclass is the only seam that covers all registered tools. Do not
"simplify" this back to ``FastMCP("rai-workspace")``.
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from typing import Any, cast

from mcp.server.fastmcp import FastMCP
from mcp.types import CallToolResult, ContentBlock, TextContent


def _split(
    result: Sequence[ContentBlock] | dict[str, Any],
) -> tuple[Sequence[ContentBlock], dict[str, Any] | None]:
    """Split ``FastMCP.call_tool``'s result into unstructured/structured halves.

    Tools annotated ``-> str`` (all of ours) go through ``wrap_output``, so
    the base class returns a 2-tuple ``(content_blocks, {"result": json})``.
    Older/other shapes — a bare content sequence, or a bare dict — are
    handled so the override never assumes more than it has seen.
    """
    if isinstance(result, tuple):
        # A tuple also satisfies `Sequence[ContentBlock]` structurally, so
        # the narrowed element type is wrong here; the cast records the
        # runtime contract FastMCP's own annotation omits.
        pair = cast("tuple[Sequence[ContentBlock], dict[str, Any] | None]", result)
        return pair[0], pair[1]
    if isinstance(result, dict):
        return [], result
    return result, None


class _RaiFastMCP(FastMCP):
    """FastMCP whose envelope defers to the payload's own ``status``.

    Promotes a top-level ``{"status": "error", ...}`` payload to a protocol
    level ``isError=True`` (RAISE-17624). Every other domain outcome —
    ``rejected``, ``gate_failed``, ``deterministic_failed``, a top-level
    list, a nested ``status``, unparsable text — is returned *as the very
    object the base class produced*, byte-identical on the wire.
    """

    async def call_tool(  # pyright: ignore[reportIncompatibleMethodOverride]
        self, name: str, arguments: dict[str, Any]
    ) -> Sequence[ContentBlock] | dict[str, Any] | CallToolResult:
        # The base annotation (`Sequence[ContentBlock] | dict[str, Any]`) is
        # already narrower than its own runtime behaviour (it returns a
        # 2-tuple for every `-> str` tool). The lowlevel call_tool decorator
        # explicitly admits `types.CallToolResult` from the handler and
        # passes it through verbatim (mcp/server/lowlevel/server.py), so the
        # runtime contract holds; only the annotation needs widening.
        result = await super().call_tool(name, arguments)
        unstructured, structured = _split(result)

        text = next((c.text for c in unstructured if isinstance(c, TextContent)), None)
        if text is None:
            return result
        try:
            payload: Any = json.loads(text)
        except json.JSONDecodeError:
            return result
        if isinstance(payload, dict) and payload.get("status") == "error":
            return CallToolResult(
                content=list(unstructured),
                structuredContent=structured,
                isError=True,
            )
        return result


mcp = _RaiFastMCP("rai-workspace")
