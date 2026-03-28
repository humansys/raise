# Addendum: Verificación del Bridge Claim

**Claim verificada:** "Claude Desktop automáticamente bridgea MCP servers de `claude_desktop_config.json` a la Cowork VM vía SDK layer."
**Fuente original del claim:** dev.to/murat-a-a (S1 en catálogo)
**Date:** 2026-03-27
**Veredicto: CLAIM FALSA en su forma simple — requiere matiz crítico**

---

## Triangulación de evidencia

### Claim: "stdio MCPs en claude_desktop_config.json → disponibles en Cowork automáticamente"

| Fuente | Dice | Confirma/Niega | Nivel |
|--------|------|---------------|-------|
| S9: GitHub #26259 (OPEN) | `--mcp-config` solo pasa `"type":"sdk"`. Desktop Extensions (stdio) NO incluidos. Bug abierto Mar 2026 | **NIEGA** | Very High |
| S8: pvieito.com (reverse eng.) | Passthrough vía `--mcp-config` existe, pero solo observa `"type":"sdk"` en el análisis | **NIEGA parcialmente** | High |
| S13: aaddrick.com | Cowork VM completamente aislada del host — stdio child processes inaccesibles desde VM | **NIEGA implícitamente** | Medium |
| S1: dev.to/murat-a-a | Claim de bridge automático, pero la "solución real" para stdio usa supergateway HTTP | **Fuente ambigua** | Low-Medium |
| S10: GitHub #39669 (OPEN) | Usuario espera que stdio MCPs funcionen en Cowork, reporta bug de lifecycle | **Confirma expectativa, no realidad** | High |

**Veredicto claim 1: FALSA. Confianza: HIGH.**

Los stdio MCPs locales (como los de RaiSE: `npx`, `uvx`) configurados en `claude_desktop_config.json` **NO son pasados a la VM de Cowork** por defecto. El mecanismo SDK-type bridge existe pero solo cubre servers internos de Anthropic (`Claude in Chrome`, etc.).

---

### Claim: "Connectors configurados vía GUI → disponibles en Cowork"

| Fuente | Dice | Confirma/Niega | Nivel |
|--------|------|---------------|-------|
| S11: support.claude.com | Remote MCP connectors disponibles en "Claude, Cowork, y Claude Desktop" | **CONFIRMA** | Very High |
| S4: productcompass.pm | Connectors GUI instalados en Settings > Connectors | **CONFIRMA** | Medium |
| S9: GitHub #26259 | SDK-type servers (internos) sí pasan. Connectors remotos vía GUI son de tipo diferente | **Neutral** | Very High |

**Veredicto claim 2: VERDADERA. Confianza: HIGH.**

Los connectors **remotos** (HTTP/SSE, configurados vía Settings > Connectors en la GUI) sí están disponibles en Cowork. Esto incluye connectors web como Slack, Google Drive, etc. — pero NO los stdio locales.

---

### Claim: "supergateway como workaround viable para stdio MCPs en Cowork"

| Fuente | Dice | Confirma/Niega | Nivel |
|--------|------|---------------|-------|
| S1: dev.to/murat-a-a | Layer 2: convertir stdio → HTTP con supergateway, configurar en `.mcp.json` | **CONFIRMA** mecanismo | Low-Medium |
| S11: support.claude.com | Remote MCP (HTTP/SSE) funciona en Cowork | **CONFIRMA** que HTTP es el camino | Very High |
| S9: GitHub #26259 workarounds | Mencionan proxy para MCPs con >40 tools | **Confirma** viabilidad de proxy | Very High |

**Veredicto claim 3: PLAUSIBLE. Confianza: MEDIUM.**

Convertir stdio MCPs a HTTP/SSE endpoints (via supergateway u equivalente) y registrarlos como Remote Connectors es un workaround viable. La arquitectura soporta HTTP MCPs en Cowork (S11), pero el proceso exacto para supergateway no está validado por más de 1 fuente.

---

## Arquitectura real (síntesis)

```
Claude Desktop (host)
│
├── claude_desktop_config.json
│   └── mcpServers (stdio: npx, uvx, etc.)
│       └── ❌ NO son pasados a Cowork VM (bug #26259, abierto)
│
├── Settings > Connectors (GUI)
│   └── Remote MCP servers (HTTP/SSE)
│       └── ✅ SÍ disponibles en Cowork (docs oficiales)
│
└── SDK-type servers (internos Anthropic)
    └── ✅ SÍ disponibles en Cowork via --mcp-config
        └── Claude in Chrome, Scheduled Tasks, etc.
        └── ❌ Desktop Extensions stdio (Context7, etc.) NO — mismo bug
```

```
Claude Code (CLI)
│
├── ~/.claude.json (user MCP)
│   └── ❌ JAMÁS visible para Cowork (sistema separado)
│
└── .mcp.json (project MCP)
    └── ❌ JAMÁS visible para Cowork (sistema separado)
        └── EXCEPCIÓN: si se ejecuta Claude Code dentro de Cowork VM,
            leerá .mcp.json del directorio de trabajo montado
```

---

## Implicaciones corregidas para RaiSE

| Opción | Viabilidad | Confianza | Esfuerzo |
|--------|-----------|-----------|---------|
| A: Duplicar en `claude_desktop_config.json` | ❌ NO funciona — bug #26259 abierto | HIGH | N/A |
| B: `rai mcp install --target desktop` | ❌ NO funciona mientras bug esté abierto | HIGH | N/A |
| C: Remote MCP via HTTP/SSE (supergateway) | ✅ Viable — arquitectura soportada oficialmente | MEDIUM | Alto |
| D: Esperar fix de Anthropic (bug #26259) | ✅ Si se cierra, A/B podrían funcionar | LOW (timing incierto) | Bajo |
| E: Ejecutar Claude Code CLI dentro de Cowork | ✅ Cowork puede invocar `claude` en la VM — lee `.mcp.json` del dir montado | MEDIUM | Mínimo |

**Recomendación revisada (Confianza: HIGH):**

No implementar A ni B. El bug #26259 bloquea ese camino.

**Prioridad 1:** Investigar Opción E — si Cowork puede ejecutar `claude` CLI dentro de la VM con acceso al directorio del proyecto, los `.mcp.json` de RaiSE estarían disponibles sin ningún cambio. Costo: ~0.

**Prioridad 2:** Si E no es suficiente para el caso de uso, evaluar Opción C (remote MCP via HTTP). Requiere una historia de implementación real.

**Prioridad 3:** Watch bug #26259 — si Anthropic lo cierra, B se vuelve trivial.

---

## Evidencia contraria documentada

- La claim del dev.to/murat-a-a (S1) **describe un comportamiento que no corresponde a la realidad actual** (o nunca fue correcto). El artículo usa lenguaje de "Layer 1 automático" pero su solución práctica para stdio es Layer 2 (HTTP). Posible que confunda SDK-type internos con stdio externos.
- El issue #39669 (S10) implica que alguien *esperaba* que los stdio MCPs funcionaran en Cowork, lo que sugiere que o bien funcionaron en versiones anteriores, o bien la expectativa es razonable pero no cumplida actualmente.
- **Regresión documentada** en #26259: antes de Feb 13, 2026, `mcp-registry` (SDK-type) sí se incluía. Múltiples builds han roto y parcialmente restaurado behaviors. El estado es volátil.

---

## Próximos pasos

- [ ] **Verificar Opción E:** En una sesión Cowork, ¿puede Claude ejecutar `claude --version` y luego `claude mcp list`? Si sí, los MCPs del proyecto estarían accesibles.
- [ ] **Watch** anthropics/claude-code#26259 para resolución
- [ ] **Actualizar parking lot:** defer Opción B hasta que #26259 se cierre
- [ ] **Crear backlog item:** "Investigar soporte Cowork via remote MCP HTTP" si Opción E no es viable
