---
id: "ADR-042"
title: "MCP Infrastructure as Independent Layer"
date: "2026-03-01"
status: "Proposed"
---

# ADR-042: MCP Infrastructure as Independent Layer

## Contexto

E337 introduced declarative MCP adapters but coupled server configuration to domain protocols (PM/Docs). Developers cannot register or invoke MCP servers (Context7, Snyk, Sonar) that don't map to a RaiSE domain adapter. The MCP protocol is verbose (~100 tokens per tool definition), and IDEs inject ALL tools into agent context without filtering. RaiSE has a generic McpBridge (E301) that already solves connection/lifecycle, but no infrastructure layer exposes it independently.

Forces: generic MCP access vs domain-typed adapters; token economy vs tool completeness; simple registry vs complex orchestration.

## Decisión

Create `rai_cli.mcp` as a new package — independent MCP infrastructure layer. Server configs live in `.raise/mcp/*.yaml` (separate from `.raise/adapters/*.yaml`). Domain adapters (PM/Docs) reference registered servers via `server.ref` or keep inline config (backwards compatible). CLI exposes `rai mcp list|health|call|tools|install|scaffold|stats`.

Two registries, two concerns:
- `rai_cli.mcp.registry` → "What MCP servers are available?" (infrastructure)
- `rai_cli.adapters.registry` → "What domain adapters are available?" (application)

## Consecuencias

| Tipo | Impacto |
|------|---------|
| ✅ Positivo | Any MCP server usable from rai without writing Python or mapping to a protocol |
| ✅ Positivo | Token economy: tool filtering reduces context bloat from verbose MCP definitions |
| ✅ Positivo | Telemetry on all MCP calls — observability the IDE doesn't provide |
| ✅ Positivo | Skills become agent-agnostic — MCP config in rai, not per-IDE |
| ✅ Positivo | Declarative adapters (E337) reuse registered servers — no config duplication |
| ⚠️ Negativo | Two config directories (`.raise/mcp/` + `.raise/adapters/`) — user must understand the distinction |
| ⚠️ Negativo | McpBridge imported from two paths (adapters and mcp) until potential migration |

## Alternativas Consideradas

| Alternativa | Razón de Rechazo |
|-------------|------------------|
| Extend declarative adapter schema with `protocol: generic` | Conflates infrastructure with domain — generic MCPs don't have protocol methods to map |
| Move McpBridge to `rai_cli.mcp` | Too much churn — bridge is stable in `adapters/`, used by Jira/Confluence. Import alias suffices. |
| Use Claude Code / Cursor MCP config directly | No portability across agents, no telemetry, no token filtering |
| Central MCP config in single file (not per-server YAML) | Per-server files are composable, Git-friendly, shareable |

---

<details>
<summary><strong>Referencias</strong></summary>

- Problem Brief: `work/problem-briefs/mcp-bridge-independence-2026-03-01.md`
- Epic Scope: `work/epics/e338-mcp-platform/scope.md`
- McpBridge: `src/rai_cli/adapters/mcp_bridge.py` (E301)
- Declarative adapter: ADR-041
- Parking lot item: `rai mcp call` (E301 SES-300)

</details>
