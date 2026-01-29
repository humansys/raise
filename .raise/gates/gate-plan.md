---
id: gate-plan
fase: 5
titulo: "Gate-Plan: Validación del Implementation Plan"
blocking: true
version: 1.0.0
---

# Gate-Plan: Validación del Implementation Plan

## Propósito

Verificar que el Plan de Implementación es completo, tiene tareas atómicas verificables, y puede ser ejecutado por el agente de manera determinista.

## Cuándo Aplicar

- Después de completar `flujo-04-implementation-plan`
- Antes de iniciar `flujo-06-development`
- Para cada User Story antes de implementar

---

## Criterios de Validación

### Criterios Obligatorios (Must Pass)

| # | Criterio | Verificación |
|---|----------|--------------|
| 1 | **Contexto cargado** | US, Tech Design y guardrails referenciados |
| 2 | **Componentes mapeados** | Cada componente afectado identificado |
| 3 | **Tareas atómicas** | Cada tarea completable en <2 horas |
| 4 | **Tareas verificables** | Cada tarea tiene criterio de done claro |
| 5 | **Orden por dependencias** | Dependencias satisfechas en secuencia |
| 6 | **Testing incluido** | Tareas de testing explícitas |
| 7 | **Orquestador approval** | Plan revisado y aprobado |

### Criterios Recomendados (Should Pass)

| # | Criterio | Verificación |
|---|----------|--------------|
| 8 | Verificaciones intermedias | Checkpoint cada 3-5 tareas |
| 9 | Rollback documentado | Tareas de riesgo tienen plan de recovery |
| 10 | Sin scope creep | Tareas implementan exactamente los AC de la US |

---

## Checklist Rápido

```markdown
## Gate-Plan Checklist

**User Story:** {US-ID}
**Total Tareas:** ___
**Fecha:** YYYY-MM-DD

### Obligatorios
- [ ] 1. US y Tech Design referenciados
- [ ] 2. Componentes afectados listados
- [ ] 3. Tareas atómicas (<2h cada una)
- [ ] 4. Cada tarea tiene criterio de verificación
- [ ] 5. Orden respeta dependencias
- [ ] 6. Tareas de testing presentes
- [ ] 7. Orquestador aprueba el plan

### Recomendados
- [ ] 8. Checkpoints de verificación cada 3-5 tareas
- [ ] 9. Plan de rollback para tareas de riesgo
- [ ] 10. Tareas alineadas a AC de US (sin scope creep)

### Trazabilidad
- [ ] Todos los AC de la US tienen tareas asociadas
- [ ] Guardrails aplicables identificados

### Resultado
- [ ] **PASS** - Listo para ejecutar
- [ ] **FAIL** - Criterios fallidos: _______________

**Validado por:** _______________
```

---

## Referencias

- Kata asociada: [`flujo-04-implementation-plan`](../katas-v2.1/flujo/04-implementation-plan.md)
- Gate previo: [`gate-backlog`](./gate-backlog.md)
- Siguiente gate: [`gate-code`](./gate-code.md)
