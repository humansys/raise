# Problem Brief: MCP Bridge Independence

> **Date:** 2026-03-01
> **Stakeholder:** Emilio (equipo de desarrollo)
> **Domain:** Calidad / retrabajo
> **Status:** Ready for `/rai-epic-design`

---

## 1. Domain

**Calidad / retrabajo** — el diseño actual acopla infraestructura genérica (McpBridge) a abstracciones de dominio (PM/Docs adapters), forzando retrabajo para cada MCP server que no encaje en esos protocolos.

## 2. Stakeholder

**Equipo de desarrollo** — devs que quieren integrar herramientas de su stack (Snyk, Sonar, Context7, etc.) via MCP sin estar limitados a los protocolos de dominio de RaiSE.

## 3. Gap

El equipo de desarrollo no puede usar MCPs de forma eficiente porque el McpBridge está acoplado a los RaiSE adapters (PM/Docs), impidiendo registrar y usar MCP servers que no encajan en esos protocolos de dominio.

## 4. Root Cause (3 Whys)

1. **Why 1:** El diseño de E337 fusionó dos capas que debían ser independientes — distracción durante el diseño, no debió estar así.
2. **Why 2:** Los devs necesitan integrar skills con herramientas complementarias de su stack (Snyk, Sonar, devsecops) via MCP como mecanismo universal de integración.
3. **Why 3:** El protocolo MCP es demasiado verbose e introduce ruido y costos innecesarios en el contexto del agente. Al gestionar MCPs via bridge, RaiSE puede agregar hooks de telemetría, economía de tokens, y confiabilidad que los IDEs no ofrecen.

**Raíz:** Los MCP servers inyectan definiciones verbosas de tools en el contexto del agente (token bloat), no tienen observabilidad, y cada IDE los gestiona de forma aislada. RaiSE tiene el bridge genérico para resolver esto (economía de tokens, telemetría, confiabilidad), pero lo ató al dominio PM/Docs en lugar de exponerlo como infraestructura independiente.

## 5. Early Signal (4 semanas)

**Métrica:** Reducción de tokens consumidos por sesión al usar MCPs via bridge vs directo en IDE.

## 6. Hypothesis (SAFe)

Si desacoplamos el McpBridge de los adapters de dominio y lo exponemos como infraestructura genérica de RaiSE, entonces se reducirán los tokens consumidos por sesión al usar MCPs (bridge vs directo en IDE) para el equipo de desarrollo, medido por comparación de token usage en sesiones con MCP nativo vs MCP via bridge.

---

## Context (for epic design)

### What exists today

- **McpBridge** (`src/rai_cli/adapters/mcp_bridge.py`): Genérico — `call()`, `list_tools()`, `health()`. Ya funciona con cualquier MCP server.
- **DeclarativeMcpAdapter** (`src/rai_cli/adapters/declarative/`): YAML config que mapea tools MCP → protocolos `pm` o `docs` exclusivamente.
- **Discovery** (`discovery.py`): Solo descubre adapters que declaran `pm` o `docs`.

### What's missing

- **MCP Registry**: Registrar cualquier MCP server sin atarlo a un protocolo de dominio.
- **Generic CLI**: `rai mcp list`, `rai mcp health`, `rai mcp call <server> <tool>` — acceso directo al bridge.
- **Token economy layer**: Filtrado/curación de tool definitions para reducir context bloat.
- **Telemetry hooks**: Observabilidad sobre uso de MCP tools (ya parcialmente en bridge via logfire).

### Analogies

- **MCP Porter**: Gestión genérica de MCP servers (registro, health, discovery).
- **Docker analogy**: Bridge = container runtime, Adapters = application layer on top.

### Key architectural decision

Dos capas separadas:
1. **MCP Infrastructure** (genérica): registry, bridge, CLI, telemetry — cualquier MCP server.
2. **RaiSE Protocol Adapters** (dominio): PM, Docs, Governance — usan bridge internamente pero son capa de dominio.
