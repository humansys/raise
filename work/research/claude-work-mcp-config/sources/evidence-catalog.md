# Evidence Catalog — Claude Work/Cowork MCP Configuration

**Research question:** ¿Qué mecanismos de configuración usa Claude Work/Cowork y los comparte con Claude Code?
**Verification question:** ¿El bridge automático `claude_desktop_config.json` → Cowork VM existe y funciona para MCPs locales stdio?
**Date:** 2026-03-27
**Depth:** Quick scan (Phase 1) + Verification (Phase 2)

---

## Phase 1 Sources (background)

| # | Source | Type | Evidence Level | Key Finding |
|---|--------|------|---------------|-------------|
| S1 | [dev.to/murat-a-a — MCP Servers in Claude Cowork](https://dev.to/murat-a-a/how-we-got-local-mcp-servers-working-in-claude-cowork-the-missing-guide-nbc) | Secondary (practitioner) | Low-Medium | Claim: SDK bridge automático para MCPs en claude_desktop_config.json. **NO verificado independientemente.** La "solución real" requiere supergateway (HTTP) para stdio MCPs |
| S2 | [composio.dev — Claude CoWork MCPs](https://composio.dev/content/how-to-better-your-claude-cowork-experience-with-mcps) | Secondary | Medium | Setup vía GUI; no menciona bridge automático |
| S3 | [inventivehq.com — Claude config files](https://inventivehq.com/knowledge-base/claude/where-configuration-files-are-stored) | Secondary | Medium | Paths completos Code vs Desktop; productos con configs distintas |
| S4 | [productcompass.pm — Claude Cowork guide](https://www.productcompass.pm/p/claude-cowork-guide) | Secondary | Medium | Plugins/MCPs aislados entre modos de Claude Desktop |
| S5 | [github.com/johnzfitch/claude-cowork-linux](https://github.com/johnzfitch/claude-cowork-linux) | Primary (código) | High | Paths: `~/.config/Claude/`; Cowork ejecuta Claude Code CLI directamente en host (Linux) |
| S6 | [code.claude.com/docs/en/settings](https://code.claude.com/docs/en/settings) | Primary (docs oficiales) | Very High | Claude Code: MCP user-level en `~/.claude.json`, project en `.mcp.json` |
| S7 | [claude.com/docs/connectors/mcp-apps](https://claude.com/docs/connectors/building/mcp-apps/getting-started) | Primary (docs oficiales) | Very High | Claude Desktop: MCP en `claude_desktop_config.json` vía Settings > Developer |

---

## Phase 2 Sources (verificación bridge claim)

| # | Source | Type | Evidence Level | Key Finding | Confirma/Niega bridge? |
|---|--------|------|---------------|-------------|------------------------|
| S8 | [pvieito.com — Inside Claude Cowork](https://pvieito.com/2026/01/inside-claude-cowork) | Primary (reverse engineering) | High | MCPs pasados al VM via `--mcp-config '{"mcpServers":{...}}'`. Solo `"type":"sdk"` observado en análisis | **Confirma parcialmente** — passthrough existe pero solo SDK-type |
| S9 | [github.com/anthropics/claude-code#26259](https://github.com/anthropics/claude-code/issues/26259) | Primary (bug report, OPEN) | Very High | `--mcp-config` solo incluye SDK-type (`Claude in Chrome`). Desktop Extensions stdio **NO son pasados**. Bug abierto Mar 2026 | **NIEGA** bridge para stdio MCPs locales |
| S10 | [github.com/anthropics/claude-code#39669](https://github.com/anthropics/claude-code/issues/39669) | Primary (bug report, OPEN) | High | Usuario reporta problemas con "local stdio MCP servers (configured in claude_desktop_config.json)" en Cowork — mounts se pierden en restart | **Confirma** que se esperaba que funcionara; el bug indica comportamiento frágil |
| S11 | [support.claude.com — remote MCP](https://support.claude.com/en/articles/11503834-building-custom-connectors-via-remote-mcp-servers) | Primary (docs oficiales) | Very High | Remote MCPs vía GUI → disponibles en "Claude, Cowork, y Claude Desktop". stdio NO mencionado para Cowork | **Confirma** GUI connectors para Cowork; silencio sobre stdio |
| S12 | [anthropic.com/engineering/desktop-extensions](https://www.anthropic.com/engineering/desktop-extensions) | Primary (docs oficiales) | Very High | Desktop Extensions (.mcpb) documentadas; **no menciona Cowork** como destino | **Neutral** — silencio notable |
| S13 | [aaddrick.com — Reverse engineering Cowork](https://aaddrick.com/blog/reverse-engineering-claude-desktops-cowork-mode-a-deep-dive-into-vm-isolation-and-linux-possibilities) | Secondary (análisis técnico) | Medium | Cowork = Claude Code CLI dentro de VM aislada del host | **Niega implícitamente** — aislamiento VM implica que stdio host-processes no son accesibles |
| S14 | [github.com/bKNNNNN/claude-cowork-rs](https://github.com/bKNNNNN/claude-cowork-rs) | Primary (código) | High | Daemon implementa protocolo Unix socket VM; documenta cómo Cowork se comunica con VM | **Neutral** — confirma arquitectura VM aislada |

---

## Evidence Rating Criteria

| Level | Criteria |
|-------|----------|
| Very High | Docs oficiales Anthropic / Bug reports en repo oficial |
| High | Reverse engineering verificable / Código fuente |
| Medium | Practitioners con implementación documentada |
| Low | Artículos de blog sin detalles técnicos verificables |
