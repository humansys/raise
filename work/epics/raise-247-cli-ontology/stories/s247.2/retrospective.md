---
story_id: "S247.2"
title: "Create pattern group"
completed: "2026-02-23"
size: "S"
estimated_min: 60
actual_min: 45
velocity_ratio: 1.33
---

# Retrospective: S247.2 — Create pattern group

## Summary

- **Story:** S247.2 — Create `rai pattern` group
- **Completed:** 2026-02-23
- **Size:** S
- **Estimated:** 60 min | **Actual:** ~45 min | **Velocity:** 1.33x
- **Commits:** bd96e80 → b4400a7 (7 commits total)
- **Tests:** 15 canónicos (test_pattern.py) + 2 shim tests (test_memory.py) = 17 nuevos

## What Went Well

- El patrón de extracción establecido en S247.1 funcionó sin fricción — mismos pasos, menor tiempo
- TDD disciplinado: tests fallaron primero, luego implementación los pasó
- Quality review atrapó 1 muda real (test_reinforce_with_from_flag) antes de merge
- Architecture review pre-implementación confirmó que el diseño era proporcional sin cambios

## What Could Improve

- El import de `get_memory_dir_for_scope` fue incorrecto la primera vez (`config.paths` vs `rai_cli.memory`) — la Gemba walk en diseño lo identificó correctamente pero no lo proyecté al código. Un minuto perdido.
- `_deprecation_warning` producía mensaje incorrecto para `add-pattern` → `add` (subcomandos con nombre distinto). Se descubrió en smoke test T3, no en unit tests. Mejorable con un test específico de formato de mensaje, aunque el smoke test lo capturó a tiempo.

## Heutagogical Checkpoint

### What did you learn?
- `story_id` en `reinforce_pattern` es traceability-only y **no se persiste** en JSONL v1 (`noqa: ARG001`). Esto afecta cómo testear el `--from` flag — no se puede verificar persistencia, solo que el score fue actualizado.
- `_deprecation_warning` asume `old_cmd == new_cmd` (heredado de S247.1 donde todos los nombres de graph coinciden). No es un supuesto seguro para extracciones que renombran subcomandos.

### What would you change about the process?
- Agregar al smoke test un check explícito del **formato exacto** del mensaje de deprecación (`rai pattern add`, no `rai pattern add-pattern`) como paso T2, no T3. El bug se detectó por smoke manual, debería ser un test.

### Are there improvements for the framework?
- **Patrón documentado:** cuando el subcomando canónico difiere del legado, pasar `new_cmd` explícito a `_deprecation_warning`.
- **Patrón documentado:** verificar ubicación de imports en Gemba antes de asumir módulo de origen.

### What are you more capable of now?
- El ciclo completo de extracción de god object (new file → register → shim) es ahora completamente fluido. S247.3 (signal group, 3 comandos) debería ser aún más rápida.

## Improvements Applied

- PAT-E-440: `_deprecation_warning new_cmd param` — documentado en memory
- PAT-E-441: `import location trap: get_memory_dir_for_scope` — documentado en memory
- Quality review R1 aplicado: `test_reinforce_with_from_flag` → `test_reinforce_with_from_flag_updates_score` con assertion de comportamiento real

## Action Items

- [ ] S247.3: agregar test de formato de mensaje de deprecación como parte de T2 (no esperar al smoke test manual)
- [ ] S247.9 (kill): eliminar `_deprecation_warning` + todos los shims cuando se complete el cleanup

## Velocity Comparison

| Story | Size | Estimated | Actual | Velocity |
|-------|------|-----------|--------|----------|
| S247.1 (graph group, 7 cmds) | M | ~90 min | ~55 min | 1.6x |
| S247.2 (pattern group, 2 cmds) | S | 60 min | ~45 min | 1.33x |

S247.1 fue más rápida en ratio porque el patrón era nuevo y el ciclo TDD estaba en aprendizaje. S247.2 tuvo un fix adicional de bug (mensaje deprecación) que consumió tiempo extra. S247.3 debería estar ≥1.33x.
