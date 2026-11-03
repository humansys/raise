"""Transport-aware and scope-aware MCP tool decorators.

MCP has no "hidden" concept: an introspecting client receives the whole tool
list, so the only lever for keeping a tool out of discovery is *not registering
it*. These decorators are that lever.

Out of scope for both: removing code from the wheel. A non-registered tool is
still importable and still callable in-process — this is concealment, not
removal. Real removal is a product decision.
"""

from __future__ import annotations

import os
from collections.abc import Callable
from typing import Any

from raise_cli.pipeline._mcp_instance import mcp

# Opt-in flag for the experimental tool surface. Absent/falsy = tools not
# registered. Documented in dev/docs/mcp-pipeline-architecture.md §6.1 and
# docs/concepts/fleet.md#experimental-status.
EXPERIMENTAL_ENV_VAR = "RAISE_EXPERIMENTAL"

_TRUTHY = frozenset({"1", "true", "yes", "on"})


def _experimental_enabled() -> bool:
    """True when THIS process opted into experimental MCP tools.

    Private on purpose. Registration happens at import time in the MCP server,
    a long-lived process that inherits its env from the client launch config
    (``.mcp.json``). Any other process reading this — a CLI command, a hook —
    is guessing about a environment it does not share, so exposing it invites
    exactly the cross-process false claim RAISE-15618 removes.
    """
    return os.environ.get(EXPERIMENTAL_ENV_VAR, "").strip().lower() in _TRUTHY


def local_only(fn: Callable[..., Any]) -> Callable[..., Any]:
    """Register as MCP tool only on stdio transport (not HTTP)."""
    if os.environ.get("RAISE_MCP_TRANSPORT", "").lower() == "http":
        return fn
    return mcp.tool()(fn)


def experimental(fn: Callable[..., Any]) -> Callable[..., Any]:
    """Register as MCP tool only when ``RAISE_EXPERIMENTAL`` opts in (stdio only).

    For tools that exist in the codebase but are outside the shipped scope of the
    current release (RAISE-15618). Without the opt-in the tool never reaches the
    tool list, so an evaluator's discovery matches the published scope instead of
    contradicting it.

    Experimental implies :func:`local_only`: the opt-in never widens the HTTP
    surface. An unshipped tool has no business being reachable from a remote
    transport, and the fleet tools it currently guards read in-process state that
    is meaningless across process boundaries anyway.
    """
    if not _experimental_enabled():
        return fn
    return local_only(fn)
