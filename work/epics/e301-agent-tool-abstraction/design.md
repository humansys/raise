# Epic E301: Agent Tool Abstraction — Design

> **Version:** v3 (MCP Python SDK bridge, research-grounded)
> **Date:** 2026-02-27 (SES-298)
> **Research:** `work/research/mcp-bridge-strategy/evidence-catalog.md` (16 sources)

## Gemba (Current State)

### What exists

```
src/rai_cli/adapters/
  __init__.py
  models.py          ← 9 Pydantic models (IssueSpec, IssueRef, IssueDetail, etc.)
  protocols.py       ← 4 protocols (sync + async PM and Docs), runtime_checkable
  registry.py        ← entry point discovery (_discover, get_pm_adapters, get_doc_targets)
  sync.py            ← SyncPMAdapter, SyncDocsAdapter wrappers, _run_sync() helper

src/rai_cli/cli/commands/
  _adapter_resolve.py  ← resolve_adapter() — auto-detect singleton pattern (PAT-E-554)
  backlog.py           ← 7 commands (create, transition, update, link, comment, search, batch-transition)
  adapters.py          ← placeholder (rai adapters group)
```

### What's missing

1. **No `rai.adapters.pm` entry points in pyproject.toml** — registry discovers nothing
2. **No concrete adapter implementation** — only protocols and CLI surface
3. **No McpBridge** — the generic infrastructure to call MCP server tools
4. **No `rai docs` CLI group** — commands not created yet
5. **No `rai.docs.targets` entry points** — same gap as PM
6. **No auto-sync hooks** — lifecycle skills don't emit Jira transitions

### Dependencies already in project

- `atlassian-python-api>=3.41.0` (in pyproject.toml — used by legacy code, not by new adapters)
- `mcp` SDK: **not installed yet** — needs adding to pyproject.toml
- `mcp-atlassian`: **not installed yet** — consumed as external MCP server process, not as pip dependency

## Target Architecture

### Component Map

```
src/rai_cli/
  adapters/
    __init__.py
    models.py              ← exists (no changes)
    protocols.py           ← exists (no changes)
    registry.py            ← exists (no changes)
    sync.py                ← exists (no changes)
    mcp_bridge.py          ← NEW: McpBridge (generic MCP SDK client with telemetry)
    mcp_jira.py            ← NEW: McpJiraAdapter (11 methods → mcp-atlassian Jira tools)
    mcp_confluence.py      ← NEW: McpConfluenceAdapter (5 methods → mcp-atlassian Confluence tools)
  cli/commands/
    _adapter_resolve.py    ← exists (no changes)
    _docs_resolve.py       ← NEW: resolve_docs_target() — same pattern as _adapter_resolve
    backlog.py             ← exists (no changes)
    docs.py                ← NEW: rai docs CLI group (publish, get, search)
  hooks/builtin/
    jira_sync.py           ← NEW: auto-sync hook (lifecycle → Jira transitions)
```

### McpBridge — Key Contract

```python
class McpBridge:
    """Generic async bridge to any MCP server via official Python SDK.

    Manages server process lifecycle, session, and RaiSE telemetry.
    """

    def __init__(self, server_command: str, server_args: list[str] | None = None,
                 env: dict[str, str] | None = None) -> None:
        """Configure bridge for a specific MCP server.

        Args:
            server_command: Command to start MCP server (e.g. "mcp-atlassian")
            server_args: Optional args for the server command
            env: Optional environment variables (auth tokens, config)
        """
        ...

    async def call(self, tool_name: str, arguments: dict[str, Any]) -> McpToolResult:
        """Call a tool on the MCP server.

        Wraps ClientSession.call_tool() with:
        - Telemetry: timing, success/fail, tool name, argument summary
        - Error handling: connection failures, tool errors, timeouts
        - Result parsing: extract text/structured content from MCP response
        """
        ...

    async def list_tools(self) -> list[McpToolInfo]:
        """List available tools on the server (for health/discovery)."""
        ...

    async def health(self) -> AdapterHealth:
        """Check server connectivity and tool availability."""
        ...
```

### McpToolResult — Bridge Response Model

```python
class McpToolResult(BaseModel):
    """Parsed result from an MCP tool call."""
    text: str = ""                    # Primary text content
    data: dict[str, Any] = {}        # Parsed JSON if available
    is_error: bool = False            # Whether the tool reported an error
    error_message: str = ""           # Error description if is_error

class McpToolInfo(BaseModel):
    """Tool metadata from server discovery."""
    name: str
    description: str = ""
```

### McpJiraAdapter — Mapping Layer

```python
class McpJiraAdapter:
    """Maps ProjectManagementAdapter protocol to mcp-atlassian Jira tools.

    Implements AsyncProjectManagementAdapter. Consumed via SyncPMAdapter
    wrapper for CLI, or directly in async contexts.

    Registered as entry point: rai.adapters.pm = "jira"
    """

    def __init__(self) -> None:
        """Read config from .raise/jira.yaml + env vars for auth."""
        self._bridge = McpBridge(
            server_command="mcp-atlassian",  # or uvx/pipx path
            env={...}  # JIRA_URL, JIRA_USERNAME, JIRA_API_TOKEN from env
        )
        self._config = _load_jira_config()  # .raise/jira.yaml

    async def transition_issue(self, key: str, status: str) -> IssueRef:
        """Map status name → transition ID via jira.yaml, call MCP tool."""
        transition_id = self._resolve_transition_id(status)
        result = await self._bridge.call("jira_transition_issue", {
            "issue_key": key,
            "transition_id": str(transition_id),
        })
        return IssueRef(key=key, url=result.data.get("url", ""))
```

### Session Lifecycle — Connection Management

> Revised after arch review AR-2: `_run_sync()` creates a new event loop per call
> via `asyncio.run()`. A cached session belongs to the previous (dead) loop.
> Lazy session is a fiction in sync CLI context.

**Reality by context:**

| Context | What happens | Session behavior |
|---------|-------------|-----------------|
| **CLI (sync)** | `_run_sync()` → `asyncio.run()` per call → loop created and destroyed | Per-call: connect → call → disconnect each time |
| **CLI batch** | `_run_sync()` → `asyncio.run(batch_transition())` → single loop for N calls | One session for the batch, bridge connects once |
| **Async (server)** | Caller owns the event loop, adapter lives across calls | Lazy session with auto-reconnect (true D3) |

**Bridge implementation:** The bridge always attempts lazy caching, but in CLI context
`asyncio.run()` destroys the loop after each top-level call, so the cached session is
invalidated. The bridge detects this (closed transport) and reconnects. Net effect:
per-call in CLI, lazy in async — same code, different runtime behavior.

**Batch optimization:** `batch_transition` groups N calls inside one async method,
so `_run_sync()` creates one loop for all N calls — one connection, N tool calls:
```python
async def batch_transition(self, keys: list[str], status: str) -> BatchResult:
    # Single asyncio.run() wraps this whole method → one session for N calls
    results = []
    for key in keys:
        result = await self._bridge.call("jira_transition_issue", {...})
        results.append(result)
    return BatchResult(succeeded=results)
```

**Overhead:** ~200-500ms per connection. CLI commands do 1-3 calls typically.
Imperceptible at human speed.

### Entry Points Registration

```toml
# pyproject.toml additions
[project.entry-points."rai.adapters.pm"]
jira = "rai_cli.adapters.mcp_jira:McpJiraAdapter"

[project.entry-points."rai.docs.targets"]
confluence = "rai_cli.adapters.mcp_confluence:McpConfluenceAdapter"
```

Note: entry points register the **class**, not an instance. `resolve_adapter()` calls
`cls()` (no-arg constructor). The adapter reads its own config in `__init__`.

**Auto-wrap for sync consumption (AR-1):** Entry points register async adapter classes
(e.g., `McpJiraAdapter` implements `AsyncProjectManagementAdapter`). `resolve_adapter()`
detects async instances and auto-wraps with `SyncPMAdapter` for CLI consumption:

```python
# In resolve_adapter() — ~3 lines added
from rai_cli.adapters.protocols import AsyncProjectManagementAdapter
from rai_cli.adapters.sync import SyncPMAdapter

instance = cls()
if isinstance(instance, AsyncProjectManagementAdapter):
    instance = SyncPMAdapter(instance)
return instance
```

This keeps entry points clean (register the real adapter class) and the CLI unaware
of async/sync distinction. Async consumers (rai-server) use the adapter directly.

### MCP Server Discovery — How does the bridge find mcp-atlassian?

```
Priority order:
1. Explicit config in .raise/adapters.yaml (if exists):
     mcp_servers:
       atlassian:
         command: "mcp-atlassian"
         env_file: ".env"

2. Well-known command names:
     - "mcp-atlassian" (pip install mcp-atlassian)
     - "uvx mcp-atlassian" (uvx ephemeral)
     - "pipx run mcp-atlassian" (pipx)

3. Which available on PATH → auto-detect
```

**For MVP:** hardcode `mcp-atlassian` as the server command in adapter `__init__`.
Config-based discovery is a SHOULD, not MUST.

### Telemetry Layer — Logfire/OTel

Telemetry uses `logfire-api` (Pydantic's OTel wrapper). Zero overhead when `logfire`
is not installed (no-op shim). Full OTel export when user installs `logfire`.

```python
import logfire

class McpBridge:
    async def call(self, tool_name: str, arguments: dict[str, Any]) -> McpToolResult:
        with logfire.span("mcp.tool_call",  # AR-5: single span, no decorator
                          mcp_server=self._server_command,
                          mcp_tool=tool_name,
                          _tags=["mcp", "adapter"]) as span:
            start = time.monotonic()
            try:
                result = await self._session.call_tool(tool_name, arguments)
                elapsed = int((time.monotonic() - start) * 1000)
                span.set_attribute("duration_ms", elapsed)
                span.set_attribute("success", True)
                logfire.info("MCP call {tool} OK ({ms}ms)",
                            tool=tool_name, ms=elapsed)
                return self._parse_result(result)
            except Exception as exc:
                elapsed = int((time.monotonic() - start) * 1000)
                span.set_attribute("duration_ms", elapsed)
                span.set_attribute("success", False)
                span.record_exception(exc)
                logfire.error("MCP call {tool} FAILED: {err}",
                             tool=tool_name, err=str(exc))
                raise
```

**Dependency strategy:**
```toml
# pyproject.toml
dependencies = [
    "logfire-api>=4.0",          # no-op shim, MIT, zero weight (~no deps)
]

[project.optional-dependencies]
observability = [
    "logfire>=4.0",              # full SDK, MIT, OTel export to any backend
]
```

**User experience:**
- `pip install rai-cli` → telemetry calls are no-ops, zero overhead
- `pip install rai-cli[observability]` → full OTel spans, export to any OTLP backend
- `send_to_logfire=False` → no data goes to Pydantic's cloud, ever
- Logfire Cloud is optional SaaS with free tier — not required

**No custom telemetry model needed.** The `McpCallTelemetry` dataclass from the
original design is eliminated. Logfire spans capture the same data as OTel attributes
(server, tool, duration_ms, success, error). Standard, queryable, exportable.

### Auto-Sync Hook (S301.6)

```python
class JiraSyncHook:
    """Hook: lifecycle events → Jira transitions via adapter.

    Registered as entry point: rai.hooks = "jira-sync"
    Reads lifecycle_mapping from .raise/jira.yaml:
      lifecycle_mapping:
        story_start: 31    # → In Progress
        story_close: 41    # → Done
    """

    def on_signal(self, signal: WorkSignal) -> None:
        if signal.work_type == "story" and signal.event == "start":
            adapter = resolve_adapter(None)
            adapter.transition_issue(signal.work_id, "In Progress")
```

## Key Design Decisions

### D1: MCP Python SDK over MCPorter (Node.js)

**Context:** Initial design (v2) proposed MCPorter as subprocess bridge.
**Decision:** Use official MCP Python SDK `ClientSession.call_tool()` via stdio transport.
**Rationale:**
- Pure Python — no Node.js dependency in a Python project
- Official SDK (v1.26.0, 21K stars) — highest stability guarantee
- Async-native — aligns with existing async protocols
- Generic — works with any MCP server
- Evidence: 16 sources triangulated (see evidence catalog)
**Trade-off:** Must manage async session lifecycle (mitigated by `_run_sync()` already proven).

### D2: mcp-atlassian as external process, not library import

**Context:** Research found `mcp-atlassian` wraps `atlassian-python-api` internally.
Could import `JiraFetcher` directly.
**Decision:** Consume as MCP server process via stdio transport.
**Rationale:**
- MCP protocol is the stability contract — internal API is undocumented
- Same bridge code works for ANY MCP server (not just Atlassian)
- Aligns with the generic bridge vision (future GitHub, Grafana, etc. adapters)
- `mcp-atlassian` is not a pip dependency — installed separately by the user
**Trade-off:** Subprocess overhead per session. Acceptable for CLI (human-speed).
**Fallback:** If MCP bridge proves fundamentally broken, `atlassian-python-api` direct
path exists (already a project dependency).

### D3: Context-dependent session lifecycle (revised, AR-2)

**Context:** Options A (per-call), B (shared), C (lazy) for session lifecycle.
`_run_sync()` in CLI creates/destroys event loop per call, invalidating cached sessions.
**Decision:** Bridge implements lazy caching internally. Behavior varies by runtime:
- CLI sync: effectively per-call (loop destroyed, session invalidated, bridge reconnects)
- CLI batch: one session per batch (single `asyncio.run()` wraps N calls)
- Async server: true lazy session with auto-reconnect across calls
**Rationale:** Same bridge code, no branching. CLI overhead (~200-500ms/connection) is
imperceptible at human speed. Batch operations are optimized by grouping calls.
The lazy session's value materializes in async contexts (rai-server, future hooks).

### D4: Telemetry via logfire-api (OTel-native from day 1)

**Context:** OTel semantic conventions for agents are emerging (F9). Pydantic's `logfire`
is an opinionated OTel wrapper with a no-op shim (`logfire-api`) for library authors.
**Decision:** Use `logfire-api` as base dependency (no-op, zero weight). Full `logfire`
SDK as optional `[observability]` extra. All telemetry is OTel-native from day 1.
**Rationale:**
- `logfire-api` is MIT, zero dependencies, no-op when `logfire` not installed
- When `logfire` is installed, spans are standard OTel — export to any OTLP backend
- No vendor lock-in: `send_to_logfire=False` disables Pydantic's cloud entirely
- Eliminates need for custom `McpCallTelemetry` model — OTel attributes suffice
- Aligns with PydanticAI ecosystem (future `instrument_pydantic_ai()` integration)
- No Phase 2 migration needed — we're OTel from the start
**Trade-off:** `logfire` full SDK pulls in OTel dependencies (~15MB). Acceptable as
optional extra. Users who don't want observability pay zero cost via no-op shim.

### D5: Server command hardcoded per adapter (MVP)

**Context:** Could build config-based MCP server discovery from day 1.
**Decision:** Each adapter hardcodes its server command (`mcp-atlassian`).
Config-based discovery is parking lot.
**Rationale:** YAGNI for MVP — we have exactly one MCP server. Don't build a discovery
system for a single entry. When second adapter arrives (S301.5), evaluate if pattern repeats.

## Data Flow

### Happy Path: `rai backlog transition RAISE-301 done`

```
1. CLI (backlog.py)
   → resolve_adapter(None)
   → registry discovers McpJiraAdapter via entry point "rai.adapters.pm"
   → instantiates McpJiraAdapter() (reads .raise/jira.yaml + env vars)
   → AR-1: detects AsyncProjectManagementAdapter → auto-wraps in SyncPMAdapter

2. SyncPMAdapter.transition_issue("RAISE-301", "done")
   → _run_sync(async_adapter.transition_issue("RAISE-301", "done"))

3. McpJiraAdapter.transition_issue("RAISE-301", "done")
   → map "done" → transition_id 41 via jira.yaml lifecycle_mapping
   → self._bridge.call("jira_transition_issue", {"issue_key": "RAISE-301", "transition_id": "41"})

4. McpBridge.call(...)
   → lazy: if no session, start mcp-atlassian via stdio, initialize ClientSession
   → logfire.span("mcp.tool_call", server="mcp-atlassian", tool="jira_transition_issue")
   → session.call_tool("jira_transition_issue", {...})
   → span records: duration_ms, success=True
   → parse CallToolResult → McpToolResult

5. McpJiraAdapter
   → transform McpToolResult → IssueRef(key="RAISE-301", url="...")

6. CLI
   → print compact: "✓ RAISE-301 → Done (245ms)"
```

### Error Path: MCP server not installed

```
1. McpJiraAdapter.__init__()
   → McpBridge(server_command="mcp-atlassian")

2. First call → McpBridge.call(...)
   → stdio_client fails: FileNotFoundError("mcp-atlassian")
   → McpBridgeError("MCP server 'mcp-atlassian' not found. Install: pip install mcp-atlassian")

3. SyncPMAdapter → _run_sync raises McpBridgeError

4. CLI → catch, print:
   "Error: MCP server 'mcp-atlassian' not found.
    Install: pip install mcp-atlassian
    Then configure: export JIRA_URL=... JIRA_USERNAME=... JIRA_API_TOKEN=..."
```

## Architecture Review Findings (SES-298)

| ID | Finding | Severity | Resolution |
|----|---------|----------|------------|
| AR-1 | resolve_adapter() returns sync, adapter is async | High | Auto-wrap with SyncPMAdapter in resolver (~3 lines). See Entry Points section. |
| AR-2 | _run_sync + lazy session = per-call in CLI | Medium | Accept per-call as CLI reality. Batch ops optimized via single asyncio.run(). See Session Lifecycle section. |
| AR-3 | JiraSyncHook doesn't satisfy LifecycleHook protocol | Low | Fix in S301.6 story design. Hook must use `handle(event: HookEvent)`, not `on_signal()`. |
| AR-4 | mcp optional dep + entry point imports | Medium | Registry try/except already handles this. Entry point fails gracefully, resolver shows "No adapter installed." |
| AR-5 | Double span in telemetry (decorator + context manager) | Low | Removed decorator, keep only `with logfire.span()`. See Telemetry section. |
| AR-6 | Status name vs transition ID mapping gap | Low | Add `status_mapping` to jira.yaml. Resolve in S301.3 story design. |

### AR-6 Resolution: Status Mapping in jira.yaml

The protocol receives human-readable status names (`"done"`, `"in-progress"`).
The MCP tool needs Jira transition IDs. Add explicit mapping to `.raise/jira.yaml`:

```yaml
# Existing lifecycle_mapping (hook → transition ID for auto-sync S301.6)
lifecycle_mapping:
    story_start: 31
    story_close: 41

# NEW: status_mapping (CLI status name → transition ID for rai backlog)
status_mapping:
    backlog: 11
    selected: 21
    in-progress: 31
    done: 41
```

`McpJiraAdapter._resolve_transition_id(status)` reads `status_mapping`.
`JiraSyncHook` (S301.6) reads `lifecycle_mapping`. Different consumers, different maps.

## Open Questions (for story-level design)

1. **`mcp` SDK as dependency or optional?** Adding `mcp>=1.26,<2` to pyproject.toml
   makes it mandatory. Alternative: optional dependency group `[mcp]`.
   Recommendation: optional group — keeps base install light, adapters are opt-in.
   AR-4 confirms registry handles missing import gracefully.

2. **How to handle `mcp-atlassian` env vars?** The MCP server reads `JIRA_URL`,
   `JIRA_USERNAME`, `JIRA_API_TOKEN` from env. Bridge passes env to subprocess.
   Should we read from `.env` file? From `.raise/jira.yaml`? Both?
   Recommendation: env vars (standard), with `.env` file loading as convenience.

3. **Batch operations via bridge?** `batch_transition` groups N calls in one
   `asyncio.run()` — one session, N sequential calls (AR-2 resolution).
   Concurrent calls within a session → Phase 2.

4. **Test strategy for McpBridge?** Can't easily mock an MCP server process in unit tests.
   Options: (a) mock at ClientSession level, (b) use FastMCP in-process test server,
   (c) integration tests only.
   Recommendation: (a) for unit tests, (b) for integration tests.

## File Change Summary

| File | Action | Story |
|------|--------|-------|
| `pyproject.toml` | Add optional `[mcp]` dep group + entry points | S301.3 |
| `src/rai_cli/adapters/mcp_bridge.py` | NEW: McpBridge (~150 LOC) | S301.3 |
| `src/rai_cli/adapters/mcp_jira.py` | NEW: McpJiraAdapter (~200 LOC) | S301.3 |
| `src/rai_cli/cli/commands/_adapter_resolve.py` | MODIFY: auto-wrap async→sync (AR-1, ~3 lines) | S301.3 |
| `.raise/jira.yaml` | ADD: status_mapping section (AR-6) | S301.3 |
| `src/rai_cli/adapters/mcp_confluence.py` | NEW: McpConfluenceAdapter (~150 LOC) | S301.5 |
| `src/rai_cli/cli/commands/_docs_resolve.py` | NEW: resolve_docs_target() | S301.4 |
| `src/rai_cli/cli/commands/docs.py` | NEW: rai docs CLI group | S301.4 |
| `src/rai_cli/hooks/builtin/jira_sync.py` | NEW: JiraSyncHook | S301.6 |
| `tests/adapters/test_mcp_bridge.py` | NEW: bridge unit tests | S301.3 |
| `tests/adapters/test_mcp_jira.py` | NEW: Jira adapter tests | S301.3 |
| `tests/adapters/test_mcp_confluence.py` | NEW: Confluence adapter tests | S301.5 |
| `tests/cli/test_docs_smoke.py` | NEW: docs CLI smoke tests | S301.4 |
| `tests/hooks/test_jira_sync.py` | NEW: auto-sync hook tests | S301.6 |
