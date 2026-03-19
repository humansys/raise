## Analysis: RAISE-598

### Root Cause (5 Whys)

Problem → `doctor()` tiene cognitive complexity 47 (S3776)
Why1 → Renderizado JSON y humano viven inline con 3+ niveles de anidamiento
Why2 → Cada feature (--json, --verbose, --fix) se agregó directamente al callback
Why3 → CLI callbacks se sienten "self-contained" — la tentación es agregar inline
Why4 → No hubo guarda de responsabilidad única al reviewar CLI commands
Root cause → Ausencia de extracción de concerns en CLI callbacks — se tolera complejidad creciente porque "es solo output"

### Concerns identificados en doctor()

| Concern | Líneas | Complexity |
|---------|--------|-----------|
| Validación + setup | 66-84 | bajo — queda en `doctor()` |
| Render JSON | 87-105 | contribuye ~12 pts |
| Render humano | 106-131 | contribuye ~20 pts |
| Apply fixes | 133-144 | contribuye ~8 pts |
| Exit code | 146-147 | trivial |

### Fix approach

Extraer 3 sub-funciones privadas:
1. `_render_json_output(results, passes, warns, errors)` → None
2. `_render_human_output(results, passes, warns, errors, verbose)` → None
3. `_apply_fixes(results)` → None

`doctor()` queda como orquestador delgado (complexity estimada: ~8).
Tests existentes en test_cli.py cubren los paths — sirven como regression tests.
