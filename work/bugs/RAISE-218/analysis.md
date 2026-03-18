# RAISE-218 Analysis

## Root Cause

**5 Whys:**

1. `ide.type: claude` en el manifest aunque el usuario pasó `--agent cursor`
2. ¿Por qué? — `ProjectManifest` se construye en init.py L574 sin pasar `ide=`
3. ¿Por qué importa? — `IdeManifest` tiene default `type: IdeType = "claude"` (manifest.py L67)
4. ¿Por qué no se propaga el agente elegido? — `valid_agent_types` alimenta `AgentsManifest.types` pero nadie sincroniza `ide`
5. ¿Por qué `ide` existe si es legacy? — backward compat: la migration validator lo lee para proyectos viejos sin `agents` key

**Root cause:** `ide` es un campo legacy que se persiste al YAML pero init nunca lo setea — siempre queda con el default `"claude"`. La inconsistencia es visible en el manifest y podría confundir usuarios que lo lean directamente.

## Fix Approach

En `init.py`, al construir `ProjectManifest`:
- Derivar `ide_type` de `valid_agent_types[0]`
- Usar `IdeManifest(type=ide_type)` si el agente es un builtin conocido
- Fallback a `IdeManifest()` (claude) para agentes custom no en el Literal

Validar que `ide_type` es un builtin via try/except sobre `IdeManifest(type=primary)` — Pydantic rechaza valores fuera del Literal en runtime.
