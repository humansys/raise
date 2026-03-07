# RAISE-483: Root Cause Analysis

## Method: 5 Whys

**Problem:** `rai session start --context` fails with "No module named 'mcp'" on installations without `[mcp]` extra.

1. **Why does BacklogHook fail?**
   Because `resolve_adapter()` triggers PM adapter discovery which loads `McpJiraAdapter`.

2. **Why does loading McpJiraAdapter fail?**
   Because `McpJiraAdapter` (registered as `rai.adapters.pm` entry point) imports `raise_cli.mcp.bridge` at module level.

3. **Why does that import fail?**
   Because `raise_cli.mcp.bridge` has `from mcp import ClientSession, StdioServerParameters` at module level (line 23).

4. **Why is `mcp` not available?**
   Because `mcp` is declared as an optional dependency (`[project.optional-dependencies] mcp = ["mcp>=1.26,<2"]`), not a base dependency.

5. **Why doesn't the entry point discovery catch the error?**
   It DOES — `registry._discover()` catches ImportError at L46 and logs a warning. But the error surfaces as a confusing "Backlog query error" in session context, not as a clear "MCP adapter unavailable" message.

## Root Cause

`mcp` package is imported at module level in `raise_cli.mcp.bridge` (L23), but the entry points `jira` and `confluence` that depend on it are unconditionally registered in `pyproject.toml`. When `mcp` is not installed, `ep.load()` fails with ImportError. The registry skips them (correct), but the BacklogHook gets no adapter and reports a confusing error.

**Two issues:**
1. **Primary:** `mcp.bridge` imports `mcp` at module level — no guard for optional dependency
2. **Secondary:** Error message is confusing — user sees "No module named 'mcp'" instead of actionable guidance

## Fix Approach

Guard the `mcp` import in `raise_cli/mcp/bridge.py` with a try/except that raises a clear error at instantiation time (not import time). This lets the entry point load the class successfully, and the error only surfaces when someone actually tries to USE the MCP bridge without the package installed.

Alternatively (simpler): the current behavior where `registry._discover()` skips broken entry points is actually correct by design. The real fix is ensuring the BacklogHook handles the "no adapter available" case gracefully instead of propagating a confusing error.

**Decision:** Guard `mcp` import in bridge.py — this is the minimal fix that addresses the root cause cleanly.
