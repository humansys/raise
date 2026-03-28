# Research Report: Claude Work/Cowork — Configuración MCP y compatibilidad con Claude Code

**Pregunta primaria:** ¿Qué mecanismos de configuración usa Claude Work/Cowork y los comparte con Claude Code en la misma máquina?
**Fecha:** 2026-03-27
**Depth:** Quick scan (8 fuentes)
**Confianza general:** MEDIUM — evidencia de docs oficiales + practitioners, pero Cowork es producto reciente (Feb 2026) con documentación escasa

---

## 1. ¿Qué es "Claude Work"?

El nombre oficial es **Claude Cowork** (lanzado Feb 2026). Es un **modo autónomo de agente** dentro de la app **Claude Desktop** — no es un producto separado ni una interfaz web. Incluye:

- Sandbox Linux VM local donde Claude ejecuta código, crea archivos, usa herramientas
- Interfaz similar a Claude Code pero sin CLI — orientada a usuarios no-técnicos
- Disponible en macOS (Intel/Apple Silicon) y Windows; **Linux solo vía reverse-engineering** (no oficial)

Los tres modos de Claude Desktop son: **Chat**, **Cowork**, y **Code Tab** — comparten la sesión de usuario pero tienen configs aisladas entre sí.

---

## 2. Mecanismos de Configuración

### Claude Cowork (dentro de Claude Desktop)

| Mecanismo | Descripción | Path |
|-----------|-------------|------|
| GUI — Connectors | MCPs web (OAuth, URL), instalados vía Settings > Connectors | Almacenado internamente por Claude Desktop |
| GUI — Extensions | Desktop Extensions (.dxt), instalados vía Settings > Extensions | Almacenado internamente |
| JSON manual | MCPs custom vía Menu > Developer > App Config File | `claude_desktop_config.json` (ver paths abajo) |

**Paths de `claude_desktop_config.json`:**
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- Linux (no oficial): `~/.config/Claude/`

**Formato:**
```json
{
  "mcpServers": {
    "mi-server": {
      "command": "npx",
      "args": ["-y", "@mi-paquete/mcp"]
    }
  }
}
```

### Claude Code (CLI)

| Scope | Path | Compartido |
|-------|------|-----------|
| User MCP | `~/.claude.json` | No (personal) |
| Project MCP | `.mcp.json` | Sí (git) |
| User settings | `~/.claude/settings.json` | No |
| Project settings | `.claude/settings.json` | Sí (git) |
| CLAUDE.md global | `~/.claude/CLAUDE.md` | No |

---

## 3. ¿Comparten configuración?

**Respuesta corta: NO de forma nativa. SÍ en una dirección vía bridge no documentado.**

| Dirección | ¿Funciona? | Mecanismo | Confianza |
|-----------|-----------|-----------|-----------|
| Claude Code → Cowork | ❌ No | `~/.claude.json` no es leído por Cowork | MEDIUM |
| Claude Desktop → Cowork | ✅ Sí (automático) | SDK bridge: Desktop bridgea `claude_desktop_config.json` a la VM de Cowork | MEDIUM (fuente: dev.to S1, no confirmado en docs oficiales) |
| Cowork → Claude Code | ❌ No | Configs aisladas por diseño (S4) | HIGH |

**Diagrama:**
```
~/.claude.json          (Claude Code MCP)    ←─── NO lee Cowork
claude_desktop_config.json (Claude Desktop)  ───→ SÍ bridgeado a Cowork automáticamente
```

---

## 4. Implicaciones para RaiSE

RaiSE configura sus MCP servers en `.raise/mcp/*.yaml` y los registra vía `rai mcp install` → escribe en `~/.claude.json` (formato Claude Code). **Estos MCP servers NO están disponibles automáticamente en Claude Cowork.**

Para usar los MCP servers de RaiSE en Cowork, hay **dos caminos**:

### Opción A: Duplicar en `claude_desktop_config.json` (manual, frágil)
Copiar cada entry de `~/.claude.json` a `claude_desktop_config.json`. Problema: desincronización, doble mantenimiento.

### Opción B: `rai mcp install --target desktop` (no existe aún, candidato a implementar)
Un nuevo flag en `rai mcp install` que escriba simultáneamente en `~/.claude.json` Y en `claude_desktop_config.json`. Mantiene una sola fuente de verdad en `.raise/mcp/` con dos destinos.

### Opción C: Remote MCP over HTTP (más limpia, más trabajo)
Exponer los MCP servers de RaiSE como servidores HTTP/SSE locales. Cowork puede conectarse via URL. Elimina el problema de paths de config.

---

## 5. Evidencia contraria / gaps

- **Gap importante:** No hay documentación oficial de Anthropic sobre el SDK bridge Desktop→Cowork. La fuente (S1) es un artículo de dev.to, no verificable en docs primarias.
- **Linux no soportado oficialmente:** Cowork en Linux requiere reverse-engineering (S5). Las paths pueden diferir.
- **Producto nuevo:** Cowork tiene ~1 mes de vida (Feb 2026). La documentación evoluciona rápido.
- **Isolation claim:** S4 dice "plugins/MCPs aislados entre modos" pero S1 dice que Desktop los bridgea a Cowork. Contradicción aparente — puede que S4 se refiera a GUI Extensions, no a `claude_desktop_config.json`.

---

## 6. Recomendación

**Confianza: MEDIUM**

Implementar **Opción B** como historia en el backlog: `rai mcp install --target [code|desktop|both]`.

Justificación:
- Mantiene `.raise/mcp/*.yaml` como source of truth
- Escribe a ambos destinos desde un comando
- No requiere que el usuario mantenga dos configs
- Inversión mínima (modificar el comando existente)

**Prerequisito:** Verificar empíricamente el SDK bridge en una máquina con Claude Desktop instalado. Si el bridge no funciona (fuente no oficial), la Opción C (remote MCP) es la alternativa robusta.

---

## 7. Próximos pasos

- [ ] Verificar SDK bridge: instalar Claude Desktop, configurar un MCP en `claude_desktop_config.json`, abrir Cowork, confirmar que el servidor aparece
- [ ] Crear issue en backlog: `rai mcp install --target desktop|both`
- [ ] Si bridge no funciona → evaluar Opción C (HTTP MCP)

---

## Referencias
- [Evidence catalog](sources/evidence-catalog.md)
- [Claude Code settings docs](https://code.claude.com/docs/en/settings)
- [Claude Desktop MCP docs](https://claude.com/docs/connectors/building/mcp-apps/getting-started)
- [Cowork Linux reverse-engineering](https://github.com/johnzfitch/claude-cowork-linux)
