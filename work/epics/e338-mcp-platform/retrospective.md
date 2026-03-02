# Epic Retrospective: E338 — MCP Platform

## Summary

Exposed McpBridge as independent infrastructure so developers can register, manage, and invoke any MCP server from RaiSE — with telemetry, health monitoring, and conversational skills — without coupling to domain adapters.

**Duration:** ~3 sessions (2026-03-01 to 2026-03-02)
**Stories:** 10 (3M + 6S + 1XS)
**Average velocity:** 1.48x
**Tests added:** 73 (total suite: 3345)
**Files created:** 17 MCP-specific (code + skills + governance)
**Lines added:** 1,688 (MCP-specific)

## Deliverables

| Milestone | Stories | Status |
|-----------|---------|--------|
| M1: Walking Skeleton | S338.1, S338.3 | Done |
| M2: CLI Complete | S338.2, S338.4, S338.5 | Done |
| M3: Full Platform | S338.6, S338.7 | Done |
| M4: Developer Experience | S338.8, S338.9, S338.10 | Done |

### Key Capabilities Delivered

- `rai mcp list/health/tools/call/install/scaffold` — full CLI surface
- `.raise/mcp/*.yaml` registry with `discover_mcp_servers()`
- McpBridge at `rai_cli.mcp.bridge` with backwards-compat shim
- Telemetry: `McpCallEvent` emitted on every bridge call
- Declarative adapter `server.ref` resolution from registry
- `/rai-mcp-add`, `/rai-mcp-remove`, `/rai-mcp-status` — conversational skills
- Stack-aware MCP recommendations from governance catalog
- MCP health visibility at session start
- Governance catalog (`.raise/mcp/catalog.yaml`) with DevSecOps servers

## Story Velocity

| # | Story | Size | Velocity |
|---|-------|------|----------|
| S338.1 | MCP infrastructure + registry | M | 1.0x |
| S338.2 | `rai mcp list/health/tools` | S | 2.25x |
| S338.3 | `rai mcp call` | S | 1.8x |
| S338.4 | Telemetry hooks | S | 1.5x |
| S338.5 | Declarative adapter `server.ref` | S | 1.25x |
| S338.6 | `rai mcp install` | M | 1.2x |
| S338.7 | `rai mcp scaffold` | S | 1.33x |
| S338.8 | MCP Skills (add/remove/status) | M | 1.8x |
| S338.9 | Stack-aware MCP recommendations | S | 1.4x |
| S338.10 | MCP health in session start | XS | 1.25x |

## What Went Well

1. **Walking skeleton strategy validated** — S338.1 (foundation) + S338.3 (E2E call) proved the architecture before layering CLI, telemetry, and DX. Risk was front-loaded correctly.

2. **Pattern replication compounding** — S338.3 established the CLI command pattern, S338.2 mechanically replicated 3 commands at 2.25x velocity. PAT-E-442 confirmed again.

3. **Backwards compatibility preserved** — Bridge move (S338.1) and server.ref (S338.5) maintained 100% compat through re-export shims and fallback resolution. Zero consumer breakage.

4. **Skills-only stories are fast** — S338.8/9/10 (no Python code, just SKILL.md) ranged 1.25x–1.8x. No TDD overhead when deliverable is pure governance/documentation.

5. **Smoke test caught real bug** — Running `/rai-mcp-status` before epic close discovered `catalog.yaml` being parsed as server config. Fixed in-session.

## What Could Improve

1. **S338.1 velocity (1.0x)** — Foundation story was correctly sized M but didn't exceed estimate. Bridge move required updating 6 consumers + mock.patch targets (PAT-E-606). Next time: budget extra for mock.patch grep when moving modules.

2. **M4 stories added mid-epic** — S338.8/9/10 were scoped after M3 completion. While they fit naturally, earlier scoping would have allowed parallel planning.

3. **catalog.yaml schema collision** — Adding governance data to `.raise/mcp/` created a naming conflict with the server discovery glob. Should have anticipated from the start that not all YAML in the dir would be server configs.

## Patterns Captured

| Pattern | Description | Story |
|---------|-------------|-------|
| PAT-E-606 | Module move + mock.patch — grep for patch targets, not just imports | S338.1 |
| PAT-E-607 | Infrastructure decoupling via own models — break import dependency at boundary | S338.1 |
| PAT-E-608 | CLI flags collisions — check global flags before adding short forms | S338.4 |
| PAT-E-609 | Validators + assert for type-safety without `type: ignore` | S338.5 |
| PAT-E-610 | Shared helpers need independent test coverage per consumer | S338.6 |
| PAT-E-611 | Capability-impacting data is governance — put in `.raise/`, not skill markdown | S338.9 |

## Architecture Decisions Validated

| ID | Decision | Outcome |
|----|----------|---------|
| AR-Q1 | McpBridge to `rai_cli.mcp.bridge` | Clean separation, re-export works |
| AR-Q2 | Two config dirs (mcp/ + adapters/) | Distinct concepts, no confusion |
| AR-Q3 | No static tool filtering | `rai mcp call` is inherently zero-overhead |
| AR-C1 | Bridge returns own `McpHealthResult` | No inverse coupling to domain |
| AR-C2 | `ServerConnection` shared between schemas | Zero semantic duplication |
| AR-R3 | Explicit `--type` flag on install | Simple, no auto-detection complexity |

## Risks That Materialized

| Risk | What Happened | Impact |
|------|---------------|--------|
| catalog.yaml parsed as server config | `discover_mcp_servers()` glob matched governance file | Low — graceful skip, noisy warning. Fixed in 10 min. |

## Risks That Didn't Materialize

- Bridge move breaking consumers (re-export shim prevented)
- MCP server install diversity issues (explicit --type solved)
- Bridge subprocess lifecycle problems (E301 patterns reused)
