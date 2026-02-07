# Governance Policy

> **Producto**: {nombre del producto}
> **Versión**: 1.0.0
> **Última actualización**: {fecha}

---

## Contexto del Producto

{Breve descripción del producto, su propósito, y el contexto técnico/de negocio que informa las decisiones de gobernanza.}

## Principios Rectores

Los siguientes principios guían las decisiones de gobernanza de este producto:

1. **{Principio 1}**: {descripción}
2. **{Principio 2}**: {descripción}
3. **{Principio 3}**: {descripción}

> Estos principios se derivan de: {fuente - ej: RaiSE Constitution, Solution Vision, decisiones de equipo}

---

## Guardrails Activos

### MUST (Obligatorios - Gates Bloqueantes)

| ID | Categoría | Descripción | Archivo |
|----|-----------|-------------|---------|
| MUST-ARCH-001 | Arquitectura | {descripción} | `guardrails/architecture.mdc` |
| MUST-SEC-001 | Seguridad | {descripción} | `guardrails/security.mdc` |
| ... | ... | ... | ... |

### SHOULD (Recomendados - Gates de Advertencia)

| ID | Categoría | Descripción | Archivo |
|----|-----------|-------------|---------|
| SHOULD-TEST-001 | Testing | {descripción} | `guardrails/testing.mdc` |
| ... | ... | ... | ... |

### MAY (Opcionales - Sin Gate)

| ID | Categoría | Descripción | Archivo |
|----|-----------|-------------|---------|
| MAY-DOC-001 | Documentación | {descripción} | `guardrails/documentation.mdc` |
| ... | ... | ... | ... |

---

## Resumen por Categoría

| Categoría | MUST | SHOULD | MAY | Total |
|-----------|------|--------|-----|-------|
| Arquitectura | 0 | 0 | 0 | 0 |
| Testing | 0 | 0 | 0 | 0 |
| Seguridad | 0 | 0 | 0 | 0 |
| API | 0 | 0 | 0 | 0 |
| Código | 0 | 0 | 0 | 0 |
| Errores | 0 | 0 | 0 | 0 |
| Documentación | 0 | 0 | 0 | 0 |
| **Total** | **0** | **0** | **0** | **0** |

---

## Proceso de Excepción

Cuando un guardrail no puede cumplirse, el proceso es:

1. **Documentar** la necesidad de excepción con rationale
2. **Crear ADR** explicando:
   - Por qué no se puede cumplir
   - Qué alternativa se propone
   - Impacto y riesgos
   - Plan de remediación (si aplica)
3. **Aprobar** por {rol responsable - ej: Tech Lead, Architect}
4. **Registrar** la excepción en la sección de abajo

### Excepciones Activas

| Guardrail | ADR | Razón | Fecha Expiración |
|-----------|-----|-------|------------------|
| {ninguna} | - | - | - |

---

## Gobernanza de la Gobernanza

### Cómo Modificar Este Documento

1. Proponer cambio via MR/PR
2. Incluir rationale del cambio
3. Obtener aprobación de {rol}
4. Actualizar guardrails afectados

### Revisión Periódica

- **Frecuencia**: {trimestral, semestral, anual}
- **Responsable**: {rol}
- **Última revisión**: {fecha}
- **Próxima revisión**: {fecha}

---

## Historial de Cambios

| Versión | Fecha | Cambio | Autor |
|---------|-------|--------|-------|
| 1.0.0 | {fecha} | Versión inicial | {autor} |

---

## Referencias

- **ADR-009**: `dev/decisions/framework/adr-009-continuous-governance-model.md`
- **ADR-010**: `dev/decisions/framework/adr-010-three-level-artifact-hierarchy.md`
- **ADR-011**: `dev/decisions/framework/adr-011-three-directory-model.md`
- **Solution Vision**: `governance/vision.md`
- **RaiSE Constitution**: `framework/reference/constitution.md`

---

*Generado por: `setup/governance` kata*
