# Normalization Report: flujo/06-implementacion-hu-asistida-por-ia.md

**Processed**: 2026-01-12
**Coherence**: aligned
**Orquestador Approval**: approved

## Semantic Coherence Check

**Level**: flujo
**Guiding Question**: ¿Cómo fluye?
**Assessment**: Content primarily answers the guiding question: **YES**

The document describes the flow for implementing a User Story with AI assistance. It guides HOW the process flows from loading the implementation plan, through iterating tasks with validation pauses, to finalization. This is a workflow kata correctly placed in `flujo/`.

## Jidoka Inline Changes

This kata has 3 main steps (with step 2 having 5 sub-steps) that now include Jidoka Inline verification and correction guidance:

| Step | Header | Verification Added | Correction Added |
|------|--------|-------------------|------------------|
| 1 | Inicio y Carga del Plan | ✅ Yes | ✅ Yes |
| 2 | Iteración de Tareas (a-e) | ✅ Yes | ✅ Yes |
| 3 | Finalización del Plan | ✅ Yes | ✅ Yes |

**Total Steps**: 3 (with 5 sub-steps in step 2)
**Steps Modified**: 3

### Jidoka Content Added

**Paso 1 - Inicio y Carga:**
- **Verificación:** El Asistente ha cargado el Plan de Implementación y el Orquestador ha confirmado la interpretación de las tareas.
- **Si no puedes continuar:** Plan no encontrado o no legible → Solicitar al Orquestador la ruta correcta o ejecutar primero la kata flujo-04.

**Paso 2 - Iteración de Tareas:**
- **Verificación:** Cada tarea del bucle tiene: (a) kata/guardrail identificado, (b) código generado y validado por el Orquestador, (c) permiso explícito si hubo edición de código existente, (d) pruebas generadas si aplica, (e) tarea marcada como completada en el plan.
- **Si no puedes continuar:** Orquestador rechaza el código generado → Iterar con feedback específico del Orquestador hasta obtener aprobación. Si requiere edición de código existente sin permiso → Documentar la consecuencia y buscar alternativa.

**Paso 3 - Finalización:**
- **Verificación:** Todas las tareas del Plan de Implementación están marcadas como completadas y el Orquestador ha confirmado que no hay ajustes pendientes.
- **Si no puedes continuar:** Tareas pendientes en el plan → Regresar al paso 2 para completar las tareas faltantes antes de declarar la HU como implementada.

## Terminology Changes

| Location | Before | After | Context |
|----------|--------|-------|---------|
| Title | `(L1-06)` | removed | Remove L prefix |
| Frontmatter ID | `L1-06` | `flujo-06` | ID format |
| Descripción | `Practicante` | `Orquestador` | Role naming |
| Objetivo | `Practicante` | `Orquestador` | Role naming |
| Objetivo | `Katas L2/L3` | `Katas de patrón/técnica` | Level naming |
| Dependencias | `L0-01: Meta-Kata` | `Kata de principios: Meta-Kata` | Level naming |
| Dependencias | `L1-04: Generación de Plan` | `Kata de flujo: Generación de Plan (flujo-04)` | Level naming |
| Dependencias | `generado por L1-04` | `generado por flujo-04` | Level naming |
| Dependencias | `Katas L2 (Componentes) y L3 (Técnicas)` | `Katas de patrón y técnica` | Level naming |
| Header | `Reglas Cursor Relacionadas` | `Guardrails Cursor Relacionados` | Governance term |
| Paso 1 | `al Practicante` | `al Orquestador` | Role naming |
| Paso 1 | `generado por L1-04` | `generado por flujo-04` | Level naming |
| Paso 1 | `Katas L2/L3` | `Katas de patrón/técnica` | Level naming |
| Paso 2a | `Kata L2/L3` (x2) | `Kata de patrón/técnica` | Level naming |
| Paso 2a | `reglas Cursor` | `guardrails Cursor` | Governance term |
| Paso 2b | `del Practicante` | `del Orquestador` | Role naming |
| Paso 2c | `del Practicante` | `del Orquestador` | Role naming |
| Paso 2d | `la Kata` | `los guardrails` | Reference format |

**Total Replacements**: ~18 terminology changes

## Notes

1. **Full Jidoka coverage**: All 3 main steps now have explicit verification criteria. Step 2's Jidoka covers the entire iteration loop including all 5 sub-steps.

2. **Heavy Practicante → Orquestador replacement**: This kata had 5 occurrences of "Practicante" which is not the canonical term.

3. **L0/L1 → principios/flujo**: All level references normalized.

4. **Reglas → Guardrails**: "Reglas Cursor Relacionadas" section header and inline references updated.

5. **Existing "Pausa para Validación" preserved**: This kata already had a strong validation-pause pattern at each step. Jidoka Inline complements this with formal verification criteria and correction guidance.

6. **Add-only principle preserved**: The kata's core principle of preferring new code over modifications was preserved and is now reinforced by Jidoka verification.

7. **Extensive guardrails list**: The kata references ~40 `.mdc` guardrails files. These were preserved as-is since they're specific file references.

---

**Report Generated**: 2026-01-12T00:55:00
