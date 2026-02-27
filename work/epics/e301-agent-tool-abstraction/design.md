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

```
Option A: Per-call session (simple, some overhead)
  Each adapter method: connect → initialize → call_tool → disconnect

Option B: Shared session per adapter instance (efficient, complex)
  __init__: connect + initialize (keep session alive)
  methods: call_tool (reuse session)
  __del__ or context manager: disconnect

Option C: Lazy session with auto-reconnect (balanced)
  First call: connect + initialize + cache session
  Subsequent calls: reuse cached session
  On error: reconnect once, then raise
```

**Recommendation:** Option C (lazy with auto-reconnect). Avoids overhead of per-call
connections while handling disconnects gracefully. The bridge manages this internally —
adapters don't see it.

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

### Telemetry Layer

Each `McpBridge.call()` emits:

```python
@dataclass
class McpCallTelemetry:
    server: str          # "mcp-atlassian"
    tool: str            # "jira_transition_issue"
    success: bool
    duration_ms: int
    error: str | None
    timestamp: str       # ISO 8601
```

For MVP: log to structured logger. Phase 2: emit as RaiSE telemetry event
(rai signal emit-work), align with OTel when conventions stabilize.

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

### D3: Lazy session with auto-reconnect

**Context:** Options A (per-call), B (shared), C (lazy) for session lifecycle.
**Decision:** Option C — lazy initialization on first call, cache session, auto-reconnect on error.
**Rationale:** Balances simplicity (adapters don't manage connections) with efficiency
(single connection per adapter lifetime). Auto-reconnect handles transient failures.

### D4: Telemetry as structured logging (MVP)

**Context:** OTel semantic conventions for agents are emerging but not stable (F9).
**Decision:** Log `McpCallTelemetry` via Python structured logging. Phase 2: OTel.
**Rationale:** Ship telemetry now, standardize later. Logs are queryable and sufficient
for MVP observability. Avoids premature commitment to unstable OTel conventions.

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
   → wraps in SyncPMAdapter

2. SyncPMAdapter.transition_issue("RAISE-301", "done")
   → _run_sync(async_adapter.transition_issue("RAISE-301", "done"))

3. McpJiraAdapter.transition_issue("RAISE-301", "done")
   → map "done" → transition_id 41 via jira.yaml lifecycle_mapping
   → self._bridge.call("jira_transition_issue", {"issue_key": "RAISE-301", "transition_id": "41"})

4. McpBridge.call(...)
   → lazy: if no session, start mcp-atlassian via stdio, initialize ClientSession
   → telemetry: start timer
   → session.call_tool("jira_transition_issue", {...})
   → telemetry: record duration, success
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

## Open Questions (for story-level design)

1. **`mcp` SDK as dependency or optional?** Adding `mcp>=1.26,<2` to pyproject.toml
   makes it mandatory. Alternative: optional dependency group `[mcp]`.
   Recommendation: optional group — keeps base install light, adapters are opt-in.

2. **How to handle `mcp-atlassian` env vars?** The MCP server reads `JIRA_URL`,
   `JIRA_USERNAME`, `JIRA_API_TOKEN` from env. Bridge passes env to subprocess.
   Should we read from `.env` file? From `.raise/jira.yaml`? Both?
   Recommendation: env vars (standard), with `.env` file loading as convenience.

3. **Batch operations via bridge?** `batch_transition` calls 1 MCP tool per key.
   Should bridge support concurrent calls within a session?
   Recommendation: sequential for MVP, concurrent for Phase 2.

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
| `src/rai_cli/adapters/mcp_confluence.py` | NEW: McpConfluenceAdapter (~150 LOC) | S301.5 |
| `src/rai_cli/cli/commands/_docs_resolve.py` | NEW: resolve_docs_target() | S301.4 |
| `src/rai_cli/cli/commands/docs.py` | NEW: rai docs CLI group | S301.4 |
| `src/rai_cli/hooks/builtin/jira_sync.py` | NEW: JiraSyncHook | S301.6 |
| `tests/adapters/test_mcp_bridge.py` | NEW: bridge unit tests | S301.3 |
| `tests/adapters/test_mcp_jira.py` | NEW: Jira adapter tests | S301.3 |
| `tests/adapters/test_mcp_confluence.py` | NEW: Confluence adapter tests | S301.5 |
| `tests/cli/test_docs_smoke.py` | NEW: docs CLI smoke tests | S301.4 |
| `tests/hooks/test_jira_sync.py` | NEW: auto-sync hook tests | S301.6 |
