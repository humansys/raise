---
id: "ADR-041"
title: "Declarative MCP Adapter via YAML + Mini Expression Evaluator"
date: "2026-03-01"
status: "Accepted"
---

# ADR-041: Declarative MCP Adapter via YAML + Mini Expression Evaluator

## Contexto

Cada nuevo MCP adapter (Jira, Confluence) requiere ~400 LOC de Python: arg building, response parsing, config. Esto bloquea la integración de nuevos MCP servers (GitHub, Linear, GitLab) — requiere trabajo de framework developer, no de usuario. Necesitamos una forma declarativa de mapear protocol methods a MCP tool calls.

Fuerzas en tensión: simplicidad del evaluador vs poder expresivo, zero-deps vs reutilizar Jinja2, descubrimiento automático vs explícito.

## Decisión

Usar YAML declarativo en `.raise/adapters/*.yaml` con un mini expression evaluator propio (~100 LOC, zero external deps). El evaluador soporta: dot-access (`{{ data.field }}`), type coercion (`| str`), defaults (`| default('x')`), pluck (`| pluck('name')`), y JSON serialize (`| json`). Entry points (Python adapters) tienen prioridad sobre YAML adapters.

## Consecuencias

| Tipo | Impacto |
|------|---------|
| ✅ Positivo | Nuevo adapter en ~50-80 líneas YAML vs ~400 LOC Python |
| ✅ Positivo | Zero new dependencies (no Jinja2) |
| ✅ Positivo | Adapters existentes (Jira, Confluence, Filesystem) sin cambios |
| ✅ Positivo | Validación estática via Pydantic schema |
| ⚠️ Negativo | Expresiones limitadas a 4 filters — si se necesita más, hay que extender el evaluador |
| ⚠️ Negativo | No hay auto-discovery de tools del MCP server (Level 3, futuro) |

## Alternativas Consideradas

| Alternativa | Razón de Rechazo |
|-------------|------------------|
| Jinja2 template engine | Dependencia pesada para solo 4 filters. Overkill. |
| Raw McpBridge (Level 1 only) | Ya existe como escape hatch, pero no ofrece typed protocol compliance |
| Auto-discovery + BM25 (Level 3) | Complejidad alta, premature — Level 2 cubre el 80% de casos |
| Code generation (MCPorter style) | Genera código estático que hay que mantener — YAML es más declarativo |

---

<details>
<summary><strong>Referencias</strong></summary>

- Research: `dev/research/declarative-mcp-adapter-design.md`
- Protocols: `src/rai_cli/adapters/protocols.py` (ADR-033)
- Registry: `src/rai_cli/adapters/registry.py`
- McpBridge: `src/rai_cli/adapters/mcp_bridge.py` (E301)

</details>
