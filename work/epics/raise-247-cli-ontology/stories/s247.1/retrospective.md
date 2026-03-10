---
story_id: "S247.1"
title: "Create graph group"
phase: "retrospective"
completed: "2026-02-23"
size: "M"
commits: 10
---

# Retrospective: S247.1 — Create `graph` group

## Summary

| Field | Value |
|-------|-------|
| Story | S247.1 |
| Started | 2026-02-23 |
| Completed | 2026-02-23 |
| Size | M |
| Tasks | 5 |
| Commits | 10 (scope, design, arch-review, plan, T1–T5, quality-fixes) |
| Test delta | +75 new tests (29 in test_graph.py, 13 in test_graph_*_dedicated) |
| Suite | 2499 passed, 0 failed |

## What Went Well

- **Arch review pre-implementation caught 3 issues** (R1: helper placement, Q1: MEMORY_TYPES inlining, Q3: hint strings) — coste bajo, evitó reescritura post-implementación.
- **TDD guió la extracción limpiamente** — escribir test_graph.py como RED antes de crear graph.py dejó claros los contratos de los 7 comandos sin ambigüedad.
- **Backward-compat wrappers funcionaron a la primera** — el patrón `_deprecation_warning + lazy import + misma firma` delegó correctamente en todos los casos.
- **Quality review encontró C2 (DFS recursivo)** — la refactorización iterativa es una mejora real de mantenibilidad que los linters no habrían detectado.
- **Separación correcta de preocupaciones** — graph.py no tiene `_deprecation_warning` (arch review R1), memory.py no tiene lógica de graph. La dirección de dependencia es unidireccional.

## What Could Improve

- **T4 fue más trabajo de lo estimado** — mover tests entre archivos + actualizar strings de error + eliminar duplicados tomó más tiempo que "S". El plan subestimó la cantidad de aserciones de texto que cambiarían con los nuevos mensajes.
- **El archivo de test original no se eliminó en T3** — copié en lugar de renombrar, creando duplicados que fallaron en la suite completa. T5 los eliminó pero fue un paso adicional no en el plan.
- **`Console(stderr=True)` no es `console.print(..., stderr=True)`** — el primer intento de `_deprecation_warning` falló porque Rich Console no acepta `stderr` como kwarg de `.print()`. Un test de humo rápido antes de commit habría atrapado esto.

## Heutagogical Checkpoint

### ¿Qué aprendiste?

- **`-> NoReturn` en pyright es suficiente** — `cli_error` es `-> NoReturn` así que no hay riesgo de control flow post-error aunque no haya `return` explícito. El patrón defensivo de agregar `return` (como en `context_cmd`) es ruido, no seguridad.
- **`NodeType = str` hace innecesarios los `type: ignore`** — cuando los type aliases son simplemente `str`, el ignore está mintiendo sobre una discordancia que no existe. Quality review lo detectó, pyright strict no lo marcaba porque el ignore lo silenciaba.
- **DFS recursivo en código de producción es un riesgo latente** — aunque el grafo sea pequeño hoy, la versión iterativa es igual de legible y elimina una clase entera de errores. Vale el cambio proactivo.
- **`cp` vs `mv` en tests** — al hacer T3, copié los archivos en lugar de moverlos con `git mv`. Esto dejó los originales activos y la suite completa los ejecutó con los assertions viejos. Siempre usar `git mv` para renombrar archivos tracked.

### ¿Qué cambiarías del proceso?

- En el plan, separar explícitamente "mover tests" (git mv) de "actualizar invocaciones" — son dos operaciones distintas con riesgo diferente.
- Añadir un smoke test manual de `rai memory build` y `rai graph build` antes del commit de T2, no después de T5.

### ¿Hay mejoras para el framework?

- **PAT nuevo:** `git mv` para renombrar archivos en test reorganizations — `cp` deja los originales activos y crea fallos inesperados en la suite completa.
- **PAT nuevo:** Verificar `-> NoReturn` en `cli_error` antes de añadir `return` defensivos post-error — son ruido si la función es `NoReturn`.
- **PAT existente confirmado:** PAT-E-183 (Grounding over speed) — el arch review pre-implementación pagó su costo.
- **PAT existente confirmado:** PAT-E-186 (Design is not optional) — las 3 decisiones de diseño (wrapper style, helpers location, test strategy) quedaron bien fundamentadas.

### ¿En qué eres más capaz ahora?

- Extraer un God Object CLI con backward-compat completo sin romper consumidores existentes.
- Detectar y corregir `type: ignore` falsos (aquellos que ocultan type aliases, no discordancias reales).
- Refactorizar DFS recursivo a iterativo manteniendo la misma semántica de detección de ciclos.

## Improvements Applied

- `_detect_cycles` refactorizado a iterativo (graph.py)
- `type: ignore[arg-type]` eliminados (no eran necesarios con `NodeType = str`)
- String "Building memory index" → "Building graph index" en `_format_build_result`
- Test `test_memory_build_deprecated` simplificado (mock depth reducido)

## Patterns to Persist

1. **git mv para renombrar test files en reorganizaciones** — evita que los originales queden activos y fallen la suite
2. **NoReturn elimina need de `return` defensivos** — si `cli_error` es `-> NoReturn`, el código posterior es inalcanzable; añadir `return` es ruido que ruff eventualmente marcaría como dead code
3. **DFS iterativo por defecto en código de producción** — misma complejidad O(V+E), elimina RecursionError en grafos grandes
