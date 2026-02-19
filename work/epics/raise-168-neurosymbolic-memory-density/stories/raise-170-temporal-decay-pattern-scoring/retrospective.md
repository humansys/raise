# Retrospective: RAISE-170 — Temporal Decay and Pattern Scoring

## Summary
- **Story:** RAISE-170
- **Epic:** RAISE-168 (Neurosymbolic Memory Density)
- **Size:** M (planned) / M (actual)
- **Started:** 2026-02-19
- **Completed:** 2026-02-19
- **Commits:** 8 (plan → design → implement × 5 → fix → docs)
- **Tests added:** 38 new (21 query, 9 writer, 8 CLI)
- **Coverage:** 90.59% (suite completa)

## What Went Well

- **Design como grounding** — El design.md de SES-216 fue la fuente de verdad para las 6 tareas. Zero ambigüedad durante implementación.
- **TDD estricto** — RED-GREEN-REFACTOR en cada task. Los tests detectaron el issue del `-- -1` antes de llegar a producción.
- **Descubrimiento en Gemba** — Leer `builder.py._memory_record_to_node()` antes de implementar eliminó una tarea entera (el "loader update" del plan resultó innecesario — builder ya copia todos los campos genéricamente).
- **Backward compat correcta** — Dual-check `foundational/base` implementado desde el principio. 378 patrones existentes sin impacto.
- **Suite limpia para demo** — Identificamos y corregimos un test pre-existente roto (`test_version`) antes del demo de Kurigage.

## What Could Improve

- **Click/Typer negatives no estaba en el design** — El issue con `-1` como arg posicional debería haberse anticipado en el plan (o en el design). Se detectó en tests, pero costo un ciclo de refactor.
- **"bundle.py ordering" en el plan era vago** — El next-session prompt decía "bundle.py ordering" pero no había bundle.py. El término ambiguo generó una falsa tarea; la lectura de código la disolvió rápido. Mejor nombrar el artefacto real en el plan.

## Heutagogical Checkpoint

### What did you learn?
- `builder.py` copia todos los campos JSONL a metadata genéricamente — no hay que actualizar loaders por separado cuando se añaden campos nuevos al JSONL. Esto es arquitectura correcta.
- Wilson lower bound con N=1 da ~0.21 — conservador por diseño. Con N=2 positivos da ~0.34. El sistema necesita ~5 evaluaciones para dar señal fiable. Es el comportamiento esperado y documentado en RES-TEMPORAL-001.
- Click/Typer: los argumentos posicionales no aceptan enteros negativos sin `--`. La solución Pythónica es `typer.Option` nombrado.
- `"foundational"` en JSONL vs `"base"` en writer.py es deuda técnica pre-existente. PAT-E-153 (backward compat) la convirtió en una solución de dos líneas en lugar de un bug.

### What would you change about the process?
- En el plan, referenciar el archivo/función exacta cuando se habla de "ordering" — no el módulo hipotético. "Verify `_keyword_search()` sort order" es más preciso que "bundle.py ordering".
- Para comandos CLI con valores numéricos (especialmente negativos), marcar en el design que debe ser `--option`, no arg posicional.

### Are there improvements for the framework?
- **rai-story-review Step 4.6** — ya implementado en esta story. El loop de evaluación de patrones está ahora integrado en el ciclo.
- **PAT-E-364** — Click/Typer named options para enteros que pueden ser negativos.
- **PAT-E-365** — Field name drift en JSONL: el consumidor debe verificar ambas claves.

### What are you more capable of now?
- Implementar scoring estadístico (Wilson lower bound) con garantías de correctness matemático vía TDD.
- Detectar arquitectura implícita en el codebase (builder.py generic copy) que elimina trabajo antes de hacerlo.
- Diseñar CLIs con Typer que manejan todos los edge cases de parsing desde el inicio.

## Improvements Applied

- `rai-story-review` skill v1.2.0 — Step 4.6 (pattern evaluation loop)
- PAT-E-364 — Click/Typer option para negativos
- PAT-E-365 — JSONL field name drift pattern
- `test_version.py` — fixed hardcoded version (bonus, unrelated to story)

## Action Items
- [ ] Curación de patrones AI-driven — identificar foundational no marcados + duplicados (parking lot, trigger: después de varios ciclos de reinforcement con datos reales)
- [ ] `rai memory health` — dashboard de scores (deferred RAISE-171)
- [ ] Corregir writer.py para usar `"foundational"` en lugar de `"base"` (deuda técnica menor, no urgente)
