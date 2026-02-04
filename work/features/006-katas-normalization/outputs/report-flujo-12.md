# Normalization Report: flujo/12-analisis-granularidad-hus-multi-repo.md

**Processed**: 2026-01-12
**Coherence**: aligned
**Orquestador Approval**: approved

## Semantic Coherence Check

**Level**: flujo
**Guiding Question**: ¿Cómo fluye?
**Assessment**: Content primarily answers the guiding question: **YES**

The document describes the flow for analyzing and optimizing User Story granularity in a multi-repository context. It guides HOW the process flows from ecosystem context, through granularity analysis, criteria preservation, division proposals, and validation. This is a workflow kata correctly placed in `flujo/`.

## Jidoka Inline Changes

This kata has 5 numbered steps that now include Jidoka Inline verification and correction guidance:

| Step | Header | Verification Added | Correction Added |
|------|--------|-------------------|------------------|
| 1 | Contexto del Ecosistema por HU | ✅ Yes | ✅ Yes |
| 2 | Análisis de Granularidad Informado | ✅ Yes | ✅ Yes |
| 3 | Preservación y Redistribución de Criterios | ✅ Yes | ✅ Yes |
| 4 | Propuesta de División Optimizada | ✅ Yes | ✅ Yes |
| 5 | Validación Multi-Repo | ✅ Yes | ✅ Yes |

**Total Steps**: 5
**Steps Modified**: 5

### Jidoka Content Added

**Paso 1 - Contexto del Ecosistema:**
- **Verificación:** Existe `contexto_ecosistema_hu` con mapeo de cada HU a su repositorio principal, nivel de cambios y dependencias externas.
- **Si no puedes continuar:** Análisis de ecosistema (flujo-09) incompleto → Ejecutar primero la kata flujo-09 para obtener el mapeo de servicios y dependencias.

**Paso 2 - Análisis de Granularidad:**
- **Verificación:** Cada HU evaluada tiene una `decision_informada` con acción (DIVIDIR/MANTENER) y justificación basada en factores de ecosistema y granularidad.
- **Si no puedes continuar:** Decisión sin justificación → Documentar explícitamente los factores que llevan a la decisión antes de proceder.

**Paso 3 - Preservación de Criterios:**
- **Verificación:** `validacion_completitud` muestra: criterios_originales = criterios_redistribuidos, criterios_perdidos = 0, criterios_inventados = 0.
- **Si no puedes continuar:** Criterios no balanceados → Revisar la redistribución hasta que la suma de criterios en sub-HUs iguale exactamente los criterios originales.

**Paso 4 - División Optimizada:**
- **Verificación:** Cada sub-HU tiene `criterios_originales_preservados` con texto exacto y `criterios_inventados: []` vacío.
- **Si no puedes continuar:** Sub-HU con criterios inventados → Eliminar criterios no originales y redistribuir únicamente los criterios de la HU padre.

**Paso 5 - Validación Multi-Repo:**
- **Verificación:** `validacion_multirepo_con_preservacion` tiene todos los criterios en `true`, especialmente `criterios_inventados: false`.
- **Si no puedes continuar:** Validación fallida → Revisar el paso correspondiente al criterio que falló antes de proceder con los patrones de división.

## Terminology Changes

| Location | Before | After | Context |
|----------|--------|-------|---------|
| Title | `# L1-12: Análisis de...` | `# Análisis de...` | Remove L prefix |
| Header | (none) | `**ID**: flujo-12` | Added ID field |
| Propósito | `(L1-09)` | `(kata flujo-09)` | Level naming |
| Mermaid diagram | `L1-09`, `L1-12` | `flujo-09`, `flujo-12` | Level naming |
| Cuándo Aplicar | `L1-09`, `L1-08` | `flujo-09`, `flujo de Tech Design` | Level naming |
| Reutilización Alta | `Si L1-09 identificó...` | `Si flujo-09 identificó...` | Level naming |
| YAML kata_applied | `"L1-12"` | `"flujo-12"` | Reference format |
| Criterios Calidad | `L1-09` | `flujo-09` | Level naming |

**Total Replacements**: 9 terminology changes

## Notes

1. **Full Jidoka coverage**: All 5 steps now have explicit verification criteria tailored to the specific deliverables (YAML structures) and validation requirements of each step.

2. **Extensive built-in validations preserved**: This kata already had strong validation checklists (CHECKLIST DE PRESERVACIÓN, REGLAS ESTRICTAS, VALIDACIÓN FINAL OBLIGATORIA). Jidoka Inline complements these by adding step-level verification.

3. **L1-XX → flujo-XX**: All numeric level references were updated to semantic naming.

4. **No Practicante/Developer usage**: This kata did not use deprecated role terminology.

5. **No DoD/Reglas usage**: The kata uses "criterios" and "validación" consistently.

6. **Comprehensive kata**: This is one of the most detailed katas in the collection (~620 lines), with extensive YAML examples and patterns. The normalization preserved all domain-specific content.

7. **Critical principle preserved**: The "NUNCA inventar nuevos criterios" principle is central to this kata and was preserved. Jidoka verification reinforces this by checking for `criterios_inventados: 0` at each step.

---

**Report Generated**: 2026-01-12T00:40:00
