---
id: gate-backlog
fase: 4
titulo: "Gate-Backlog: Validación del Backlog"
blocking: true
version: 1.0.0
---

# Gate-Backlog: Validación del Backlog

## Propósito

Verificar que el backlog de User Stories está completo, priorizado, y tiene la calidad necesaria para proceder a Implementation Planning.

## Cuándo Aplicar

- Después de completar `flujo-05-backlog-creation`
- Antes de iniciar `flujo-04-implementation-plan`
- Cuando el backlog está listo para sprint planning

---

## Criterios de Validación

### Criterios Obligatorios (Must Pass)

| # | Criterio | Verificación |
|---|----------|--------------|
| 1 | **Features identificadas** | 3-7 features con nombre y valor claro |
| 2 | **Features priorizadas** | Orden definido con justificación |
| 3 | **MVP identificado** | Subset mínimo para valor marcado |
| 4 | **US formato correcto** | "Como [rol], quiero [acción], para [beneficio]" |
| 5 | **Criterios BDD** | Cada US tiene ≥2 escenarios Dado/Cuando/Entonces |
| 6 | **Estimaciones completas** | Todas las US tienen story points |
| 7 | **Product Owner approval** | Backlog priorizado aprobado |

### Criterios Recomendados (Should Pass)

| # | Criterio | Verificación |
|---|----------|--------------|
| 8 | INVEST compliance | Cada US es Independent, Valuable, Small, Testable |
| 9 | Detalles técnicos | US enlazadas a componentes del Tech Design |
| 10 | Dependencias claras | Orden considera dependencias técnicas |

---

## Checklist Rápido

```markdown
## Gate-Backlog Checklist

**Proyecto:** {nombre}
**Total Features:** ___
**Total User Stories:** ___
**Fecha:** YYYY-MM-DD

### Obligatorios
- [ ] 1. Features 3-7 con valor claro
- [ ] 2. Features priorizadas con justificación
- [ ] 3. MVP slice ≤50% del backlog total
- [ ] 4. Todas las US siguen formato estándar
- [ ] 5. Cada US tiene ≥2 criterios BDD
- [ ] 6. Todas las US estimadas
- [ ] 7. Product Owner aprueba priorización

### Recomendados
- [ ] 8. US cumplen INVEST
- [ ] 9. US conectadas a Tech Design
- [ ] 10. Dependencias sin ciclos

### Métricas
- Story Points MVP: ___
- Story Points Total: ___
- Ratio MVP/Total: ___% (target: 30-50%)

### Resultado
- [ ] **PASS** - Todos los obligatorios cumplidos
- [ ] **FAIL** - Criterios fallidos: _______________

**Product Owner:** _______________ Fecha: ___
**Validado por:** _______________
```

---

## Referencias

- Kata asociada: [`flujo-05-backlog-creation`](../katas-v2.1/flujo/05-backlog-creation.md)
- Template: [`user_story.md`](../templates/backlog/user_story.md)
- Gate previo: [`gate-design`](./gate-design.md)
- Siguiente gate: [`gate-plan`](./gate-plan.md)
