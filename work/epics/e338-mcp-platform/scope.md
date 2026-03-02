# Epic Scope: E338 — MCP Platform

## Problem Brief

`work/problem-briefs/mcp-bridge-independence-2026-03-01.md`

## Objective

Expose McpBridge as independent infrastructure so developers can register, manage, and invoke any MCP server from RaiSE — with telemetry and reliability — without coupling to domain adapters (PM/Docs).

**Value:** Developers integrate any MCP server (Context7, Snyk, Sonar, custom) via `rai mcp` commands. Skills become agent-agnostic (MCP config lives in rai, not per-IDE). Token overhead eliminated by design — `rai mcp call` as CLI command means zero tool schema tokens injected into agent context.

## Architecture Review Decisions (AR-*)

| ID | Decision | Rationale |
|----|----------|-----------|
| AR-Q1 | Move McpBridge to `rai_cli.mcp.bridge` | Bridge is infrastructure, not a domain adapter. Re-export from old path for backwards compat. |
| AR-Q2 | Two config directories (`.raise/mcp/` + `.raise/adapters/`) | Genuinely distinct concepts: MCP server registration vs domain protocol mapping. Location communicates intent. |
| AR-Q3 | No static tool filtering (include/exclude) | Token savings come from not using MCP natively in IDE, not from filtering tools. `rai mcp call` is inherently zero-overhead. |
| AR-C1 | Bridge returns own `McpHealthResult`, not `AdapterHealth` | Breaks inverse coupling — infrastructure must not import from domain layer. |
| AR-C2 | `ServerConnection` shared between MCP schema and declarative adapter schema | Eliminates semantic duplication of command/args/env fields. |
| AR-R1 | No `catalog.py` cache module in M1 | `list_tools()` is fast enough. Cache deferred until proven necessary. |
| AR-R2 | No `rai mcp stats` CLI | Requires event persistence that doesn't exist. Events emitted via hooks, stats deferred. |
| AR-R3 | `rai mcp install` uses explicit `--type` flag | Auto-detection adds complexity without clear value. Dev already knows the package type. |

## In Scope (MUST)

- Move McpBridge to `rai_cli.mcp.bridge` (AR-Q1) with re-export for backwards compat
- MCP server registry: `.raise/mcp/*.yaml` config (name, command, args, env)
- CLI: `rai mcp list`, `rai mcp health [name]`, `rai mcp call <server> <tool> [args]`
- `rai mcp tools <server>` — list available tools (for skill authors to know what's callable)
- Telemetry: structured events on bridge calls (tool, latency, success) via hooks
- Declarative adapters reference registered MCPs by name via `server.ref` (backwards compat with inline)

## In Scope (SHOULD)

- `rai mcp install <server> --type uvx|npx|pip` — install server, generate config template
- `rai mcp scaffold <server>` — connect, introspect tools, generate `.raise/mcp/<name>.yaml`

## Out of Scope

| Item | Rationale | Deferred To |
|------|-----------|-------------|
| Static tool filtering (include/exclude) | Token savings come from architecture, not config (AR-Q3) | If proven needed |
| Tool catalog cache | `list_tools()` fast enough for M1 (AR-R1) | If latency becomes issue |
| `rai mcp stats` aggregation CLI | Needs event persistence (AR-R2) | Future telemetry epic |
| BM25 tool search (Level 3) | Premature — need 3+ servers first | Future epic |
| MCP server sandboxing | Trust model inherited from pip/uvx | RAISE-142 Enterprise |
| Remote MCP servers (SSE/HTTP) | McpBridge is stdio-only today | Future story |
| Agent-specific MCP config generation | Each agent has own format | RAISE-128 IDE |

## Stories

| # | Story | Size | Description | Depends On |
|---|-------|------|-------------|------------|
| S338.1 | MCP infrastructure + registry | M | Move McpBridge to `rai_cli.mcp.bridge` (AR-Q1), own health model (AR-C1), shared `ServerConnection` (AR-C2), `McpServerConfig` schema, `discover_mcp_servers()`, re-export for backwards compat | — |
| S338.2 | `rai mcp list` + `health` + `tools` | S | CLI commands using registry + bridge. List shows registered servers. Health pings. Tools shows available tools per server. | S338.1 |
| S338.3 | `rai mcp call` | S | Generic tool invocation: `rai mcp call context7 query-docs --args '{...}'`. JSON output. | S338.1 |
| S338.4 | Telemetry hooks | S | `McpCallEvent` emitted from bridge via HookEmitter. `--verbose` flag on `rai mcp call` shows latency/status. | S338.3 |
| S338.5 | Declarative adapter `server.ref` | S | Declarative adapters can reference `.raise/mcp/` servers by name instead of inline config. Backwards compat preserved. | S338.1 |
| S338.6 | `rai mcp install` | M | Install server via explicit `--type uvx|npx|pip` (AR-R3), verify with health, generate config template. | S338.2 |
| S338.7 | `rai mcp scaffold` | S | Connect to running server, introspect tools, generate `.raise/mcp/<name>.yaml`. | S338.2 |

**Critical path:** S338.1 → S338.2 → S338.3 → S338.4
**Parallel after S338.1:** S338.2, S338.3, S338.5
**Parallel after S338.2:** S338.6, S338.7

## Milestones

| Milestone | Stories | Validation |
|-----------|---------|------------|
| M1: Registry + CLI | S338.1, S338.2, S338.3 | `rai mcp call context7 resolve-library-id` works E2E |
| M2: Integration | S338.4, S338.5 | Telemetry events emitted, declarative adapters use `server.ref` |
| M3: Full platform | S338.6, S338.7 | `rai mcp install` + `rai mcp scaffold` generate working config |

## Done Criteria

- [x] McpBridge lives in `rai_cli.mcp.bridge`, all existing consumers unbroken
- [ ] Context7 registered and callable via `rai mcp call` E2E
- [ ] Telemetry events emitted for every bridge call
- [ ] Declarative adapters (E337) can reference registry servers by name
- [ ] `rai mcp list` shows all registered servers with tool counts
- [ ] Retrospective completed

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| McpBridge move breaks consumers | Low | Medium | Re-export from old path, update imports incrementally |
| MCP server install diversity | Medium | Medium | Start with uvx/npx only, explicit --type |
| Bridge subprocess lifecycle | Medium | Medium | Already solved in E301 — reuse patterns |

---

## Implementation Plan

### Sequencing Strategy: Walking Skeleton

Prove the E2E architecture first (bridge move + registry + call), then layer on CLI, telemetry, integration, and DX polish.

### Story Sequence

| Pos | Story | Size | Phase | Rationale |
|-----|-------|------|-------|-----------|
| 1 | S338.1 MCP infrastructure + registry | M | M1 | **Foundation** — bridge move is highest risk (6 consumers). Everything depends on this. |
| 2 | S338.3 `rai mcp call` | S | M1 | **Walking skeleton** — prove E2E with Context7 ASAP. Highest user value. |
| 3 | S338.2 `rai mcp list/health/tools` | S | M2 | **CLI completeness** — informational commands for DX. |
| 4 | S338.4 Telemetry hooks | S | M2 | **Observability** — once call works, add telemetry to bridge. |
| 5 | S338.5 Declarative adapter `server.ref` | S | M2 | **Integration** — connect E337 declarative adapters with MCP registry. |
| 6 | S338.7 `rai mcp scaffold` | S | M3 | **DX polish** — introspect running server → generate config YAML. |
| 7 | S338.6 `rai mcp install` | M | M3 | **Last** — most external variability (package managers). Scaffold informs config format. |

### Parallel Opportunities

```
S338.1 ──→ S338.3 ──→ S338.4
       └──→ S338.2 ──→ S338.6
       └──→ S338.5     S338.7
```

- After S338.1: S338.2, S338.3, S338.5 are independent
- After S338.2: S338.6, S338.7 are independent
- After S338.3: S338.4 is independent of S338.2

Sequential execution recommended (solo developer), but parallel is safe.

### Milestones

#### M1: Walking Skeleton (S338.1 + S338.3)

- [ ] McpBridge lives in `rai_cli.mcp.bridge`
- [ ] All existing tests pass (re-export shim works)
- [ ] `.raise/mcp/context7.yaml` registered via `discover_mcp_servers()`
- [ ] `rai mcp call context7 resolve-library-id --args '{"query":"nextjs","libraryName":"next.js"}'` returns results

#### M2: CLI Complete (S338.2 + S338.4 + S338.5)

- [ ] `rai mcp list` shows registered servers with tool counts
- [ ] `rai mcp health context7` confirms connectivity
- [ ] `rai mcp tools context7` lists available tools
- [ ] `McpCallEvent` emitted on every bridge call
- [ ] Declarative adapter with `server.ref: context7` resolves correctly

#### M3: Full Platform (S338.6 + S338.7)

- [ ] `rai mcp scaffold context7` generates valid `.raise/mcp/context7.yaml`
- [ ] `rai mcp install @upstash/context7-mcp --type npx` installs and generates config
- [ ] Health check passes after install

### Progress Tracking

| # | Story | Size | Status | Velocity |
|---|-------|------|--------|----------|
| S338.1 | MCP infrastructure + registry | M | done | 1.33x |
| S338.3 | `rai mcp call` | S | done | 1.8x |
| S338.2 | `rai mcp list/health/tools` | S | done | 2.25x |
| S338.4 | Telemetry hooks | S | done | 1.5x |
| S338.5 | Declarative adapter `server.ref` | S | done | 1.25x |
| S338.7 | `rai mcp scaffold` | S | pending | — |
| S338.6 | `rai mcp install` | M | pending | — |

### Sequencing Risks

| Risk | Mitigation |
|------|------------|
| Bridge move breaks import chains not covered by tests | Run full test suite after move, before any new code |
| Context7 npx startup slow (cold start) | Already handled by bridge's lazy session + reconnect pattern |
| S338.5 `server.ref` requires registry available at adapter construction time | Registry is sync (YAML parse), no async dependency |
