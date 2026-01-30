---
id: gate-discovery
work_cycle: project
titulo: "Gate-Discovery: Validación del PRD"
blocking: true
version: 2.0.0
---

# Gate-Discovery: Validación del PRD

## Propósito

Verificar que el PRD (Product Requirements Document) está completo y tiene la calidad necesaria para proceder a la siguiente kata (project/vision).

Este gate implementa el principio **Jidoka**: si los criterios no se cumplen, el proceso se detiene hasta corregir.

## Cuándo Aplicar

- Después de completar `katas/project/discovery.md`
- Antes de iniciar `katas/project/vision.md`
- El PRD debe existir en `governance/projects/{project}/prd.md`

---

## Criterios de Validación

### Criterios Obligatorios (Must Pass)

| # | Criterio | Verificación |
|---|----------|--------------|
| 1 | **Problema articulado** | La sección Problem Statement responde: quién, qué impacto, por qué ahora |
| 2 | **Metas cuantificables** | Cada meta tiene al menos una métrica con target numérico |
| 3 | **Alcance explícito** | Existen listas In-Scope y Out-of-Scope no vacías |
| 4 | **Requisitos testeables** | Cada requisito funcional puede expresarse como Dado/Cuando/Entonces |
| 5 | **NFRs cuantificados** | Requisitos no funcionales tienen números (tiempo, %, usuarios) |
| 6 | **Riesgos documentados** | Al menos 3 riesgos con estrategia de mitigación |
| 7 | **Stakeholder approval** | Evidencia de aprobación (email, firma, comentario) |

### Criterios Recomendados (Should Pass)

| # | Criterio | Verificación |
|---|----------|--------------|
| 8 | Supuestos documentados | Al menos 3 supuestos explícitos |
| 9 | Priorización MoSCoW | Requisitos clasificados como Must/Should/Could/Won't |
| 10 | Sin ambigüedades | No hay secciones con "TBD", "pendiente", o placeholders |

---

## Proceso de Validación

### Paso 1: Revisar PRD contra checklist

Para cada criterio obligatorio:
1. Abrir el PRD
2. Localizar la sección correspondiente
3. Verificar que cumple el criterio
4. Marcar como PASS o FAIL

**Verificación:** Todos los criterios revisados y documentados.

> **Si no puedes continuar:** Criterio no localizable → Revisar estructura del PRD contra template.

### Paso 2: Evaluar resultado

```
Si TODOS los criterios obligatorios = PASS:
    → Gate PASSED
    → Proceder a katas/project/vision.md

Si ALGÚN criterio obligatorio = FAIL:
    → Gate FAILED
    → Documentar criterios fallidos
    → Regresar a katas/project/discovery.md para corregir
```

### Paso 3: Documentar decisión

Registrar en el PRD o en archivo separado:
```markdown
## Gate-Discovery Status

**Fecha:** YYYY-MM-DD
**Resultado:** PASSED | FAILED
**Criterios fallidos:** [lista si aplica]
**Validado por:** [Orquestador]
**Notas:** [observaciones]
```

---

## Escalation Gate

Si el gate falla repetidamente (>2 intentos), escalar:

| Condición | Escalación |
|-----------|------------|
| Stakeholder no disponible para aprobar | Escalar a Project Manager |
| Requisitos contradictorios | Escalar a Product Owner para decisión |
| Alcance no claro después de 2 sesiones | Escalar a sponsor del proyecto |

---

## Checklist Rápido

```markdown
## Gate-Discovery Checklist

**PRD:** {nombre del archivo}
**Fecha:** YYYY-MM-DD

### Obligatorios
- [ ] 1. Problem Statement completo (quién, impacto, urgencia)
- [ ] 2. Metas con métricas numéricas
- [ ] 3. Scope In/Out definido
- [ ] 4. Requisitos funcionales testeables
- [ ] 5. NFRs cuantificados
- [ ] 6. ≥3 riesgos con mitigación
- [ ] 7. Aprobación de stakeholder

### Recomendados
- [ ] 8. ≥3 supuestos documentados
- [ ] 9. Priorización MoSCoW
- [ ] 10. Sin placeholders/TBD

### Resultado
- [ ] **PASS** - Todos los obligatorios cumplidos
- [ ] **FAIL** - Criterios fallidos: _______________

**Validado por:** _______________
```

---

## Referencias

- Kata asociada: `katas/project/discovery.md`
- Template PRD: `templates/solution/project_requirements.md`
- Siguiente kata: `katas/project/vision.md`
- Siguiente gate: `gates/gate-vision.md`
