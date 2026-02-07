# Guardrails

> **Solution**: {nombre de la solución}
> **Versión**: 1.0.0
> **Última actualización**: {fecha}
> **Derivado de**: `governance/vision.md`

---

## Contexto de la Solución

{Breve descripción de la solución, su propósito, y el contexto técnico/de negocio que informa los guardrails.}

## Principios Rectores

Los siguientes principios guían los guardrails de esta solución:

1. **{Principio 1}**: {descripción}
2. **{Principio 2}**: {descripción}
3. **{Principio 3}**: {descripción}

> Estos principios se derivan de: Solution Vision, RaiSE Constitution

---

## Guardrails Activos

### MUST (Obligatorios - Gates Bloqueantes)

| ID | Categoría | Descripción | Archivo |
|----|-----------|-------------|---------|
| MUST-ARCH-001 | Arquitectura | {descripción} | `.cursor/rules/architecture.mdc` |
| MUST-SEC-001 | Seguridad | {descripción} | `.cursor/rules/security.mdc` |
| ... | ... | ... | ... |

### SHOULD (Recomendados - Gates de Advertencia)

| ID | Categoría | Descripción | Archivo |
|----|-----------|-------------|---------|
| SHOULD-TEST-001 | Testing | {descripción} | `.cursor/rules/testing.mdc` |
| ... | ... | ... | ... |

### MAY (Opcionales - Sin Gate)

| ID | Categoría | Descripción | Archivo |
|----|-----------|-------------|---------|
| MAY-DOC-001 | Documentación | {descripción} | `.cursor/rules/documentation.mdc` |
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
2. **Crear ADR** en `work/proposals/` explicando:
   - Por qué no se puede cumplir
   - Qué alternativa se propone
   - Impacto y riesgos
   - Plan de remediación (si aplica)
3. **Aprobar** por {rol responsable - ej: Tech Lead, Architect}
4. **Registrar** la excepción en la sección de abajo
5. **Promover** ADR a `governance/decisions/` cuando sea aceptado

### Excepciones Activas

| Guardrail | ADR | Razón | Fecha Expiración |
|-----------|-----|-------|------------------|
| {ninguna} | - | - | - |

---

## Gobernanza de los Guardrails

### Cómo Modificar Este Documento

1. Crear propuesta en `work/proposals/`
2. Incluir rationale del cambio
3. Obtener aprobación de {rol}
4. Promover a `governance/guardrails.md`
5. Actualizar `governance/index.yaml`

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

- **ADR-009**: Modelo de Gobernanza Continua
- **ADR-010**: Jerarquía de Tres Niveles
- **ADR-011**: Modelo de Tres Directorios
- **Solution Vision**: `governance/vision.md`
- **RaiSE Constitution**: `framework/reference/constitution.md`

---

*Generado por: `setup/governance` kata*
*Output: `governance/guardrails.md`*
