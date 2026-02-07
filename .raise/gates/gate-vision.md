---
id: gate-vision
work_cycle: project
titulo: "Gate-Vision: Validación de Project Vision"
blocking: true
version: 2.1.0
---

# Gate-Vision: Validación de Project Vision

## Propósito

Verificar que la Project Vision está completa, alinea negocio con técnica, y tiene la calidad necesaria para proceder a la siguiente kata (project/design).

> **Nota ADR-010**: Este gate valida la Project Vision (nivel proyecto). Para validación de Solution Vision (nivel sistema), ver `gate-solution-vision.md`.

## Cuándo Aplicar

- Después de completar `katas/project/vision.md`
- Antes de iniciar `katas/project/design.md`
- El documento debe existir en `work/vision.md` (draft) or `governance/vision.md` (approved)

---

## Criterios de Validación

### Criterios Obligatorios (Must Pass)

| # | Criterio | Verificación |
|---|----------|--------------|
| 1 | **Problem Statement técnico** | Conecta problema de negocio con capacidad técnica faltante |
| 2 | **Visión articulada** | Value proposition, differentiators, y outcomes claros |
| 3 | **Alineamiento explícito** | Cada goal del PRD tiene mecanismo técnico asociado |
| 4 | **MVP acotado** | Must Have contiene 3-5 items máximo |
| 5 | **Métricas técnicas** | Cada métrica de negocio tiene métrica técnica medible |
| 6 | **Constraints específicas** | Restricciones cuantificadas, no genéricas |
| 7 | **Dual approval** | Aprobación de stakeholder de negocio Y técnico |

### Criterios Recomendados (Should Pass)

| # | Criterio | Verificación |
|---|----------|--------------|
| 8 | Componentes de alto nivel | Diagrama con 3-7 componentes principales |
| 9 | User Impact completo | Cada stakeholder del PRD tiene beneficios concretos |
| 10 | Assumptions documentados | Al menos 3 supuestos explícitos |

---

## Proceso de Validación

### Paso 1: Verificar trazabilidad con PRD

Confirmar que:
- Todos los goals del PRD aparecen en el alineamiento
- El scope de la Project Vision es subset o igual al PRD (no añade scope)
- Las métricas de negocio del PRD están traducidas

**Verificación:** No hay goals, scope o métricas "huérfanas" en ningún documento.

> **Si no puedes continuar:** Discrepancias encontradas → Revisar PRD y Project Vision lado a lado. Documentar diferencias.

### Paso 2: Validar factibilidad técnica

Confirmar con equipo técnico:
- Los componentes propuestos son realizables
- Las métricas técnicas son alcanzables
- Las constraints son realistas

**Verificación:** Tech Lead o Arquitecto confirma factibilidad.

> **Si no puedes continuar:** Factibilidad no confirmada → Escalar a Product Owner para re-priorizar.

### Paso 3: Confirmar alineamiento de stakeholders

Verificar aprobaciones:
- Stakeholder de negocio (Product Owner, sponsor)
- Stakeholder técnico (Tech Lead, Arquitecto)

**Verificación:** Evidencia de aprobación dual (emails, firmas, comentarios).

> **Si no puedes continuar:** Aprobación faltante → Agendar sesión de alineamiento antes de continuar.

---

## Checklist Rápido

```markdown
## Gate-Vision Checklist

**Vision Doc:** {nombre del archivo}
**PRD Referencia:** {nombre del PRD}
**Fecha:** YYYY-MM-DD

### Obligatorios
- [ ] 1. Problem Statement conecta negocio ↔ técnica
- [ ] 2. Visión clara (value prop, differentiators, outcomes)
- [ ] 3. Todos los goals del PRD tienen mecanismo técnico
- [ ] 4. MVP ≤ 5 items en Must Have
- [ ] 5. Métricas técnicas para cada métrica de negocio
- [ ] 6. Constraints específicas y cuantificadas
- [ ] 7. Aprobación de negocio Y técnico

### Recomendados
- [ ] 8. Diagrama de componentes (3-7 boxes)
- [ ] 9. User Impact para todos los stakeholders
- [ ] 10. ≥3 assumptions documentados

### Trazabilidad
- [ ] Goals del PRD cubiertos: ___/___
- [ ] Métricas del PRD traducidas: ___/___
- [ ] Scope alineado (no hay scope creep)

### Resultado
- [ ] **PASS** - Todos los obligatorios cumplidos
- [ ] **FAIL** - Criterios fallidos: _______________

**Aprobación Negocio:** _______________ Fecha: ___
**Aprobación Técnico:** _______________ Fecha: ___
**Validado por:** _______________
```

---

## Escalation Triggers

| Condición | Acción |
|-----------|--------|
| Desacuerdo negocio vs técnico | Sesión de facilitación con PM |
| MVP imposible de acotar | Escalar a sponsor para priorización |
| Constraints técnicas bloquean goals | Re-evaluar feasibility con Arquitecto senior |

---

## Referencias

- Kata asociada: `katas/project/vision.md`
- Template: `templates/project/project_vision.md`
- Gate previo: `gates/gate-discovery.md`
- Siguiente kata: `katas/project/design.md`
- Siguiente gate: `gates/gate-design.md`
- ADR: `dev/decisions/framework/adr-010-three-level-artifact-hierarchy.md`

## Post-Gate Action

When this gate passes, promote the artifact:
```
work/vision.md → governance/vision.md
```
Update `governance/index.yaml` with the new approved artifact.
