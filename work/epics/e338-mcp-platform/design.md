# Epic Design: E338 — MCP Platform

## Gemba (Current State)

### What exists

```
src/rai_cli/adapters/
├── mcp_bridge.py          # Generic bridge — call(), list_tools(), health()
├── mcp_jira.py            # McpJiraAdapter (hardcoded server config)
├── mcp_confluence.py      # McpConfluenceAdapter (hardcoded server config)
├── declarative/
│   ├── adapter.py         # YAML→Protocol adapter (PM/Docs only)
│   ├── schema.py          # DeclarativeAdapterConfig (protocol: pm|docs)
│   ├── discovery.py       # discover_yaml_adapters() — filters by protocol
│   ├── expressions.py     # Mini expression evaluator
│   └── reference/github.yaml
├── protocols.py           # PM, Docs, Governance protocols
├── registry.py            # Entry point discovery
├── models.py              # Shared boundary models (includes AdapterHealth)
└── sync.py                # Sync wrappers
```

### Coupling points (what to fix)

1. McpBridge lives in `adapters/` but is generic infrastructure (AR-Q1)
2. McpBridge.health() returns `AdapterHealth` — infrastructure depends on domain model (AR-C1)
3. `ServerConfig` in declarative schema duplicates connection fields (AR-C2)
4. No CLI path to interact with MCPs outside PM/Docs domain
5. No registry of "what MCP servers are available" independent of domain adapters

## Target Architecture

```
src/rai_cli/
├── mcp/                              # NEW — MCP infrastructure layer
│   ├── __init__.py                   # Public API: McpBridge, McpServerConfig, etc.
│   ├── bridge.py                     # MOVED from adapters/mcp_bridge.py (AR-Q1)
│   ├── models.py                     # McpHealthResult, McpToolResult, McpToolInfo
│   ├── schema.py                     # McpServerConfig, ServerConnection (AR-C2)
│   ├── registry.py                   # discover_mcp_servers() — scans .raise/mcp/*.yaml
│   ├── telemetry.py                  # McpCallEvent (S338.4)
│   └── installer.py                  # Package install logic (S338.6)
├── cli/commands/
│   └── mcp.py                        # NEW — rai mcp list/health/call/tools/install/scaffold
├── adapters/
│   ├── mcp_bridge.py                 # KEPT as re-export shim (backwards compat)
│   ├── models.py                     # AdapterHealth stays (domain model)
│   ├── declarative/
│   │   ├── schema.py                 # UPDATED — server uses ServerConnection or ref (AR-C2)
│   │   └── ...                       # Rest unchanged
│   └── ...
```

### Two registries, two concerns

```
rai_cli.mcp.registry      →  "What MCP servers are available?"    (infrastructure)
rai_cli.adapters.registry  →  "What domain adapters are available?" (application)
```

## Key Design Decisions

### D1: McpBridge move (AR-Q1)

Move `mcp_bridge.py` → `rai_cli.mcp.bridge`. Old path becomes a re-export shim:

```python
# src/rai_cli/adapters/mcp_bridge.py (shim)
"""Backwards-compat re-export. Import from rai_cli.mcp.bridge instead."""
from rai_cli.mcp.bridge import McpBridge, McpBridgeError, McpToolInfo, McpToolResult

__all__ = ["McpBridge", "McpBridgeError", "McpToolInfo", "McpToolResult"]
```

Consumers migrated incrementally. Shim stays until next major version.

### D2: Own health model (AR-C1)

Bridge returns `McpHealthResult` (lives in `rai_cli.mcp.models`), not `AdapterHealth`:

```python
class McpHealthResult(BaseModel):
    server_name: str
    healthy: bool
    message: str = ""
    latency_ms: int | None = None
    tool_count: int = 0
```

Domain adapters convert: `AdapterHealth(name=result.server_name, ...)`.

### D3: Shared `ServerConnection` (AR-C2)

```python
# rai_cli.mcp.schema
class ServerConnection(BaseModel):
    command: str                    # e.g. "uvx", "npx"
    args: list[str] = []           # e.g. ["mcp-github"]
    env: list[str] | None = None   # Env var names to forward
```

Used by both `McpServerConfig` (generic) and `DeclarativeAdapterConfig` (domain).
Declarative schema updated:

```python
class ServerRef(BaseModel):
    """Server config: reference registry OR inline connection."""
    ref: str | None = None          # Name in .raise/mcp/ registry
    # Inline fields (backwards compat, used if ref is None):
    command: str | None = None
    args: list[str] = []
    env: list[str] | None = None
```

### D4: `.raise/mcp/*.yaml` config format

```yaml
# .raise/mcp/context7.yaml
name: context7
description: "Library documentation search via Context7"
server:
  command: npx
  args: ["-y", "@upstash/context7-mcp"]
```

Minimal: identity + connection. No protocol, no methods, no filtering.

### D5: Token economy by architecture (AR-Q3)

No static filtering. Token savings are structural:

| Approach | Tool schema tokens per turn |
|----------|---------------------------|
| MCP nativo en IDE (50 tools) | ~5000 tokens |
| `rai mcp call` via Bash | 0 tokens |

The saving comes from the skill calling `rai mcp call` as a CLI command, not from filtering tool definitions. Tools are listed on-demand via `rai mcp tools <server>`.

### D6: Telemetry via hooks (AR-R2)

```python
@dataclass(frozen=True)
class McpCallEvent(HookEvent):
    event_name: str = field(init=False, default="mcp.tool_call")
    server: str = ""
    tool: str = ""
    success: bool = True
    latency_ms: int = 0
    error: str | None = None
```

Emitted from bridge on every `call()`. No aggregation/persistence in this epic.
`rai mcp call --verbose` shows latency and status inline.

### D7: Install with explicit type (AR-R3)

```bash
rai mcp install @upstash/context7-mcp --type npx
# → runs: npx -y @upstash/context7-mcp (verify starts)
# → generates: .raise/mcp/context7.yaml
```

No auto-detection. Dev specifies `--type uvx|npx|pip`.

## CLI Commands

```
rai mcp list                                      # All registered servers + tool counts
rai mcp health [SERVER]                            # Ping one or all servers
rai mcp tools SERVER                               # List available tools on a server
rai mcp call SERVER TOOL [--args JSON]             # Invoke tool, JSON output
rai mcp install PACKAGE --type uvx|npx|pip [--name NAME]  # Install + generate config
rai mcp scaffold SERVER                            # Introspect → generate config YAML
```

## Components Touched

| Component | Change | Story |
|-----------|--------|-------|
| `src/rai_cli/mcp/` (NEW) | New package: bridge (moved), models, schema, registry, telemetry, installer | S338.1-S338.7 |
| `src/rai_cli/adapters/mcp_bridge.py` | Becomes re-export shim | S338.1 |
| `src/rai_cli/adapters/declarative/schema.py` | Add `ServerRef` with `ref` field | S338.5 |
| `src/rai_cli/adapters/declarative/adapter.py` | Resolve `server.ref` via MCP registry | S338.5 |
| `src/rai_cli/cli/commands/mcp.py` (NEW) | New CLI command group | S338.2, S338.3 |
| `src/rai_cli/hooks/events.py` | Add `McpCallEvent` | S338.4 |
| `.raise/mcp/` (NEW) | User config directory for MCP servers | S338.1 |

## Parking Lot (deferred from this epic)

- Static tool filtering (include/exclude) — if proven needed by real usage
- Tool catalog cache — if `list_tools()` latency becomes an issue
- `rai mcp stats` — needs event persistence infrastructure
- BM25 semantic tool search (Level 3)
- Remote MCP transports (SSE/HTTP)
- Agent config export (claude_desktop_config.json, .cursor/, .roo/)
