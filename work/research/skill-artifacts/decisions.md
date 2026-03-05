# Skill Artifacts: Design Decisions

> Date: 2026-03-03
> Status: Decided (ideation session)
> Participants: Emilio, Rai

---

## Decisions

### D1: Narrativa en YAML denso, docs humanos generados
- YAML captura toda la información con texto acotado (sin pérdida de señal)
- Docs humanos (Markdown/Confluence) son derivados generados
- Test de calidad: si generas docs desde el YAML y no falta nada sustantivo, no hubo pérdida

### D2: Un artefacto por ejecución de skill
- Cada skill produce exactamente un YAML tipado
- Schema aislado por tipo, validación independiente
- Relaciones vía `refs`, no colocación en archivo compuesto

### D3: Migración incremental bajo demanda
- `work/epics/` históricos permanecen (read-only)
- `.raise/artifacts/` para todo lo nuevo
- Solo se migra un artefacto histórico si se reabre activamente

### D4: Ingesta directa al grafo
- `rai graph build` lee `.raise/artifacts/*.yaml` como fuente adicional
- Cada artefacto = nodo, `refs` = edges
- Sin paso intermedio ni índice redundante

### D5: Schema evolution aditivo (backward-compatible only)
- Cambios solo agregan campos opcionales, nunca eliminan ni renombran
- Field `version` presente como escape hatch para breaking changes futuros
- No se escriben migraciones hasta que sea estrictamente necesario

### D6: Rollout piloto → path crítico
- Piloto con `story-design` (end-to-end: schema, validación, generación, grafo)
- Luego expandir al lifecycle path crítico: design → plan → implement → review → close
- PAT-E-442: 1ro establece patrón, 2do refina, 3ro es mecánico

---

## Model Summary

```
Skill execution
  → produces .raise/artifacts/{id}-{type}.yaml (YAML tipado)
  → Pydantic validates structure (schema per type)
  → Governance rules validate content (semantic linting)
  → References validated (integrity)
  → rai graph build ingests as nodes + edges
  → Human docs generated on demand (Markdown / Confluence)
```

## Storage Model

```
.raise/artifacts/     ← YAML tipado (source of truth, always in repo)
.raise/schemas/       ← Pydantic-derived JSON Schemas (optional, for external tools)
work/docs/            ← Generated human-readable Markdown (disposable)
work/epics/           ← Historical artifacts (read-only, migrate on reopen)
```

## Pro/Enterprise Path

- Definitions stay in `.raise/` (Terraform pattern)
- `rai login` switches backend for state/aggregation
- Service adds: cross-repo patterns, team dashboards, RBAC, audit
- Same CLI, same artifact format, different backend

## Next Steps

- [ ] Shape as epic (E354 or similar)
- [ ] Define Pydantic schema for `story-design` artifact type
- [ ] Implement pilot in `rai-story-design` skill
- [ ] Validate end-to-end: produce → validate → graph → generate docs
