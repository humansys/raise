# ADR-003: MCP como Protocolo de Contexto

**Estado:** ✅ Accepted  
**Fecha:** 2025-12-26  
**Actualizado:** 2025-12-28 (raise-mcp promovido a CORE)  
**Autores:** Emilio (HumanSys.ai)

---

## Contexto

Necesitamos servir contexto estructurado a agentes AI. Opciones:
- Custom API REST
- Language Server Protocol (LSP)
- Model Context Protocol (MCP)

## Decisión

Usar **MCP (Model Context Protocol)** de Anthropic para servir contexto. 

**Actualización v2.0:** raise-mcp se promueve a **componente CORE** del framework basado en:
- 11,000+ MCP servers registrados (estándar de facto)
- Soporte nativo en Claude, Cursor, Windsurf
- Primitivos bien definidos para Context Engineering

## Consecuencias

### Positivas
- Estándar de facto con 11,000+ servers registrados
- Soporte nativo en Claude, Cursor, Windsurf
- Extensible (Resources + Tools + Prompts + Sampling)
- Comunidad enterprise activa
- Primitivos bien definidos para Context Engineering

### Negativas
- Requiere agente MCP-compatible
- Dependencia de evolución del protocolo

### Neutras
- Fallback disponible a `.cursorrules` / `.claude.md` para agentes legacy

## Alternativas Consideradas

1. **Custom REST** - Control total. Rechazado por: reinventar la rueda, sin soporte nativo en agentes.
2. **LSP** - Estándar maduro de IDEs. Rechazado por: diseñado para code intelligence, no para contexto AI.

## Referencias

- [MCP Specification](https://modelcontextprotocol.io/)
- [10-system-architecture-v2.md](../10-system-architecture-v2.md) — Arquitectura raise-mcp

---

*Ver [README.md](./README.md) para índice completo de ADRs.*
