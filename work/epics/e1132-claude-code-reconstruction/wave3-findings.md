# E1132 Wave 3: Integration Layer — Deep Dive Findings

**Phase:** 2 (Targeted Deep Dives) per ADR-016
**Wave:** 3 — Integration Layer (MCP, bridge, plugins, entrypoints)
**Source:** `~/Code/claude-code-main/src/`
**Date:** 2026-04-01

---

## Executive Summary

The integration layer reveals **two major strategic insights:**

1. **RaiSE as a CC plugin is the optimal distribution path.** The plugin system is far larger than expected (~65 files). Plugins can provide commands, agents, hooks, MCP servers, user config, and settings. Marketplace distribution is mature.

2. **Bridge is NOT IDE integration** — it's the Remote Control system connecting CLI ↔ claude.ai/code. IDE extensions use NDJSON over stdio (the SDK transport). The SDK's control protocol enables runtime reconfiguration.

---

## Finding F9: MCP Client

**Question:** How does CC manage MCP server connections?

**Files:** `services/mcp/client.ts` (3300 lines), `services/mcp/config.ts` (1580 lines), `services/mcp/useManageMCPConnections.ts` (900 lines), `services/mcp/types.ts`, `services/mcp/normalization.ts`, `services/mcp/officialRegistry.ts`, `services/mcp/envExpansion.ts`, `services/mcp/elicitationHandler.ts`

### Connection Lifecycle

1. **Discovery:** Merge configs from 6 scopes (enterprise > local > project > user > claudeai > dynamic)
2. **Connection:** Parallel via pMap (3 local/stdio, 20 remote/SSE concurrently)
3. **Transport:** StdioClientTransport (subprocess), SSE, StreamableHTTP, WebSocket, SDK (in-process)
4. **Initialization:** MCP SDK Client with 30s timeout, roots handler (CWD)
5. **Reconnection:** Remote transports get exponential backoff (1s-30s, 5 attempts). Stdio fails immediately.

### Configuration Scopes

```
enterprise > local > project > user > claudeai > dynamic
```

Enterprise config is exclusive — blocks all user/project/plugin servers.

### All 3 MCP Primitives Supported

| Primitive | Support | Details |
|-----------|:-------:|---------|
| **Tools** | Full | Namespaced `mcp__<server>__<tool>`, memoized, dynamic refresh |
| **Resources** | Full | `ListMcpResourcesTool` + `ReadMcpResourceTool` added when resources exist |
| **Prompts** | Full | Become slash commands `mcp__<server>__<prompt>` |

### Security

- Enterprise lockdown via `allowManagedMcpServersOnly`
- Allowlist/denylist by server name, command, or URL pattern
- MCP tools default to `passthrough` permission (always prompt unless allow-ruled)
- Full OAuth flow with keychain storage and token refresh

### RaiSE Impact

| Insight | Implication |
|---------|------------|
| 6 config scopes with enterprise override | Deployment must consider enterprise lockdown |
| Resources supported | Could expose knowledge graph as MCP resources |
| Prompts become slash commands | Could expose governance workflows as MCP prompts |
| Dynamic tool refresh works | Our MCP servers can evolve at runtime |
| Remote transport preferred for latency | HTTP > stdio for multi-server setups |

**Confidence:** Alta

---

## Finding F10: Bridge (Remote Control)

**Question:** How does CC integrate with IDEs?

**Files:** `bridge/types.ts`, `bridge/bridgeMain.ts`, `bridge/bridgeMessaging.ts`, `bridge/replBridgeTransport.ts`, `bridge/createSession.ts`, `bridge/sessionRunner.ts`, `bridge/bridgeApi.ts`, `bridge/workSecret.ts`, `bridge/remoteBridgeCore.ts`, `bridge/bridgePointer.ts`

### Key Correction: Bridge ≠ IDE Integration

Bridge connects CLI ↔ **claude.ai/code** (web UI) via Anthropic's Cloud Code Runner (CCR) backend. NOT VS Code/JetBrains integration.

### Two Modes

| Mode | Mechanism |
|------|-----------|
| **Standalone** (`claude remote-control`) | Poll loop → spawn child `claude` process per session |
| **REPL bridge** (in-process) | Attach to running REPL, forward messages bidirectionally |

### Two Transport Versions

| Version | Read | Write |
|---------|------|-------|
| **v1 (env-based)** | WebSocket | HTTP POST to Session-Ingress |
| **v2 (env-less)** | SSE | HTTP POST via CCRClient |

### Spawn Modes

`single-session` (one shot), `worktree` (git isolation per session), `same-dir` (shared cwd)

### Inter-Process Protocol

Child processes communicate via **NDJSON over stdin/stdout** (`--input-format stream-json --output-format stream-json`). This is the same protocol IDE extensions use.

### RaiSE Impact

| Insight | Implication |
|---------|------------|
| Bridge is cloud infra, not local IDE | IDE extensions use SDK/NDJSON transport, not bridge |
| NDJSON over stdio is the universal protocol | Any programmatic consumer speaks this |
| Permission flow via control requests | Web UI handles permissions via `can_use_tool` requests |
| Crash recovery via bridge pointer files | Robust session resume pattern |

**Confidence:** Alta

---

## Finding F11: Plugin System

**Question:** What can a plugin do? What's the API surface?

**Files:** `plugins/builtinPlugins.ts`, `types/plugin.ts`, `utils/plugins/schemas.ts`, `utils/plugins/pluginLoader.ts`, `utils/plugins/validatePlugin.ts`, `utils/plugins/loadPluginCommands.ts`, `utils/plugins/loadPluginAgents.ts`, `utils/plugins/loadPluginHooks.ts`, `utils/plugins/mcpPluginIntegration.ts`, `utils/plugins/pluginPolicy.ts`, `services/plugins/PluginInstallationManager.ts`

### Much Larger Than Expected

The `src/plugins/` directory has 2 files, but the actual system spans **~65 files** across `utils/plugins/` and `services/plugins/`.

### Plugin Manifest (`plugin.json`)

10 capability schemas merged:

| Capability | Format | What It Provides |
|-----------|--------|-----------------|
| **Commands** | Markdown + YAML frontmatter | Slash commands `/plugin:command` |
| **Agents** | Markdown + YAML frontmatter | Agent definitions with optional worktree isolation |
| **Skills** | Directories with SKILL.md | Skills in Skill tool listing |
| **Hooks** | JSON (all 27 events) | Lifecycle hooks |
| **MCP Servers** | JSON, MCPB/DXT bundles | MCP servers added to pool |
| **LSP Servers** | JSON | Language servers |
| **Output Styles** | Markdown | Custom rendering |
| **Settings** | JSON record | Merged into CC settings (allowlisted keys) |
| **User Config** | Schema in manifest | Prompted at enable, stored in keychain |
| **Channels** | MCP + userConfig | Message channels (Telegram, Slack) |

### Distribution

3 source categories:
- **Marketplace** — git, GitHub, npm, URL, file, directory, settings-inline
- **Session-only** — `--plugin-dir` flag
- **Built-in** — `registerBuiltinPlugin()` (currently **zero** registered)

### Enterprise Controls

- `isPluginBlockedByPolicy()` for org-level blocking
- Name impersonation protection
- Global blocklist
- Dependency verification with demotion

### RaiSE Impact

| Insight | Implication |
|---------|------------|
| **RaiSE as CC plugin is fully viable** | Commands + agents + hooks + MCP + user config |
| Marketplace distribution mature | Could publish to marketplace or own registry |
| User config solves onboarding | Jira tokens, Confluence URLs collected at enable |
| 27 hook events available | Full lifecycle coverage for session/work tracking |
| No process sandbox | Hooks run arbitrary commands — powerful but careful |
| Built-in plugin API exists (empty) | Partnership path: RaiSE bundled with CC |
| Settings injection limited | Only `agent` key allowlisted currently |

**Confidence:** Alta

---

## Finding F12: Entrypoints & SDK

**Question:** How do external consumers initialize and use CC programmatically?

**Files:** `entrypoints/agentSdkTypes.ts`, `entrypoints/init.ts`, `entrypoints/cli.tsx`, `entrypoints/mcp.ts`, `entrypoints/sandboxTypes.ts`, `entrypoints/sdk/coreTypes.ts`, `entrypoints/sdk/coreSchemas.ts`, `entrypoints/sdk/controlSchemas.ts`

### Two API Surfaces

| API | Status | Model |
|-----|--------|-------|
| **V1 `query()`** | Stable | Single-turn async iterable of SDKMessage |
| **V2 `unstable_v2_*`** | Alpha | Multi-turn persistent sessions |

### V1 query() API

```typescript
query({ prompt, options? }) → Query (AsyncIterable<SDKMessage>)
```

Returns a stream of events: assistant messages, stream chunks, tool progress, results with cost/usage.

### Headless Modes

| Mode | Use Case |
|------|----------|
| `-p` / print | Non-interactive single query |
| Environment runner | BYOC headless worker |
| Self-hosted runner | Headless API-polling worker |
| MCP server mode | Expose CC tools as MCP server |

### Control Protocol (bidirectional)

The SDK transport supports runtime reconfiguration:

| Request | Purpose |
|---------|---------|
| `initialize` | Set hooks, MCP servers, system prompt, agents, JSON schema |
| `set_model` | Change model mid-session |
| `set_permission_mode` | Change permissions |
| `apply_flag_settings` | Inject settings at runtime |
| `get_settings` | Query effective merged settings |
| `interrupt` | Cancel current operation |
| `can_use_tool` | Permission requests to consumer |

### SDKMessage Event Types (20+)

`assistant`, `stream_event`, `user`, `result_success`, `result_error`, `system/init`, `system/status`, `system/compact_boundary`, `hook_started/progress/response`, `tool_progress`, `task_notification`, `prompt_suggestion`, `rate_limit_event`, ...

### Daemon Architecture (emerging)

CC is heading toward a persistent daemon: WebSocket to claude.ai, spawns agents via `query()`, manages scheduled tasks. Functions: `connectRemoteControl()`, `watchScheduledTasks()`.

### RaiSE Impact

| Insight | Implication |
|---------|------------|
| V1 query() is stable programmatic API | Use for subprocess integration |
| Control protocol enables runtime config | Could reconfigure CC mid-session |
| NDJSON over stdio is the wire format | Universal inter-process protocol |
| MCP server mode exists | CC tools exposable to other MCP clients |
| V2 sessions are alpha | Wait for stability before adopting |
| Daemon architecture emerging | Future: persistent RaiSE daemon managing CC |

**Confidence:** Alta

---

## Cross-Cutting: The RaiSE Distribution Strategy

Wave 3 reveals the optimal integration architecture:

```
                    ┌─────────────────┐
                    │  RaiSE Plugin   │
                    │  (plugin.json)  │
                    └───────┬─────────┘
                            │
           ┌────────────────┼────────────────┐
           │                │                │
    ┌──────▼──────┐  ┌──────▼──────┐  ┌─────▼──────┐
    │   Commands   │  │    Hooks    │  │ MCP Server │
    │ /rai-*       │  │ 27 events   │  │ rai-tools  │
    │ (skills)     │  │ (gates,     │  │ (graph,    │
    │              │  │  tracking)  │  │  backlog)  │
    └──────────────┘  └─────────────┘  └────────────┘
```

Three integration surfaces, one plugin package:
1. **Skills as commands** — our 19 `/rai-*` skills become plugin commands
2. **Hooks for lifecycle** — session tracking, gate enforcement, memory
3. **MCP server for tools** — graph queries, backlog operations, discovery

Distribution: marketplace plugin with user config for Jira/Confluence credentials.

---

*Generated by 4 parallel research agents analyzing Claude Code source.*
*Method: ADR-016 Phase 2 — Targeted Deep Dives.*
