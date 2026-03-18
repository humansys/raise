# Retrospective: RAISE-218

## Summary
- Root cause: `ProjectManifest` construido sin `ide=` → `IdeManifest` usaba default `type="claude"` siempre
- Fix approach: derivar `ide_manifest` de `valid_agent_types[0]`; try/except para agentes custom fuera de BuiltinAgentType

## Heutagogical Checkpoint
1. **Learned:** `ide` es un campo legacy que se serializa al YAML pero init nunca lo sincronizaba. El campo existe solo para backward-compat (migration validator), pero al persistirlo inconsistente confunde a cualquiera que lea el manifest directamente.
2. **Process change:** Cuando hay fields legacy/legacy-compat en un model, agregar un test que verifique su consistencia con el campo canónico desde el inicio — no esperar a que alguien lo reporte.
3. **Framework improvement:** Ninguna — el lifecycle funcionó bien para un bug XS.
4. **Capability gained:** Entendimiento completo del flujo ide→agents migration: cuándo dispara, cuándo no, por qué ide persiste aunque agents sea el campo canónico.

## Patterns
- Added: none (el insight ya está cubierto por patrones existentes sobre verificación de campos legacy)
- Reinforced: none evaluated
