# Normalization Report: flujo/04-generacion-plan-implementacion-hu.md

**Processed**: 2026-01-11
**Coherence**: aligned
**Orquestador Approval**: approved

## Semantic Coherence Check

**Level**: flujo
**Guiding Question**: ¿Cómo fluye?
**Assessment**: Content primarily answers the guiding question: **YES**

The document describes the flow for generating a detailed implementation plan for a User Story (HU). It guides HOW the process flows from identifying the HU through analyzing inputs, structuring the plan, breaking down tasks, and finalizing with Orquestador approval. This is a workflow kata correctly placed in `flujo/`.

## Jidoka Inline Changes

This kata has 9 numbered steps that now include Jidoka Inline verification and correction guidance:

| Step | Header | Verification Added | Correction Added |
|------|--------|-------------------|------------------|
| 1 | Inicio y Contexto | ✅ Yes | ✅ Yes |
| 2 | Análisis de Entradas | ✅ Yes | ✅ Yes |
| 3 | Estructuración del Plan | ✅ Yes | ✅ Yes |
| 4 | Desglose Tareas Desarrollo | ✅ Yes | ✅ Yes |
| 5 | Desglose Pruebas Unitarias | ✅ Yes | ✅ Yes |
| 6 | Desglose Tareas Integración | ✅ Yes | ✅ Yes |
| 7 | Mapeo ACs a Pruebas Aceptación | ✅ Yes | ✅ Yes |
| 8 | Tareas Generales | ✅ Yes | ✅ Yes |
| 9 | Revisión y Finalización | ✅ Yes | ✅ Yes |

**Total Steps**: 9
**Steps Modified**: 9

### Jidoka Content Added

**Paso 1 - Inicio y Contexto:**
- **Verificación:** El Orquestador ha identificado claramente la HU, sus ACs, y la ubicación del plan técnico (si existe).
- **Si no puedes continuar:** HU no identificada o ACs no disponibles → Localizar la documentación de la HU antes de proceder.

**Paso 2 - Análisis de Entradas:**
- **Verificación:** El Asistente ha presentado un resumen de componentes/funcionalidades y el Orquestador lo ha validado.
- **Si no puedes continuar:** Resumen incompleto o incorrecto → El Orquestador proporciona contexto adicional sobre la HU para refinar el análisis.

**Paso 3 - Estructuración del Plan:**
- **Verificación:** Existe un archivo `IMPLEMENTATION_PLAN_[ID_JIRA].md` con las 8 secciones de fases estándar en formato checklist.
- **Si no puedes continuar:** Estructura incompleta → Agregar las secciones faltantes antes de continuar con el desglose de tareas.

**Paso 4 - Desglose Desarrollo:**
- **Verificación:** Cada componente identificado en el Paso 2 tiene tareas detalladas con referencias a Katas de patrón o técnica.
- **Si no puedes continuar:** Faltan referencias a Katas → Identificar la kata aplicable consultando el catálogo de katas de patrón y técnica.

**Paso 5 - Pruebas Unitarias:**
- **Verificación:** Cada componente tiene tareas de pruebas unitarias definidas con escenarios clave y casos límite.
- **Si no puedes continuar:** Escenarios de prueba no claros → Revisar los ACs de la HU para derivar casos de prueba.

**Paso 6 - Integración:**
- **Verificación:** Existen tareas de integración que conectan los componentes desarrollados en el Paso 4.
- **Si no puedes continuar:** Puntos de integración no identificados → Revisar el diagrama de dependencias entre componentes.

**Paso 7 - Pruebas de Aceptación:**
- **Verificación:** Cada AC Gherkin de la HU tiene una tarea correspondiente en la sección 'Pruebas de Aceptación'.
- **Si no puedes continuar:** ACs sin mapear → Verificar que los ACs de la HU estén completos y bien definidos antes de continuar.

**Paso 8 - Tareas Generales:**
- **Verificación:** Las secciones 'Preparación', 'Documentación' y 'Refinamiento' contienen tareas relevantes para el ciclo completo.
- **Si no puedes continuar:** Secciones vacías → Añadir al menos las tareas mínimas de preparación (rama, dependencias) y cierre (revisión de código).

**Paso 9 - Revisión y Finalización:**
- **Verificación:** El plan completo ha sido revisado y aprobado explícitamente por el Orquestador.
- **Si no puedes continuar:** Plan no aprobado → Incorporar el feedback del Orquestador y presentar el plan revisado para nueva validación.

## Terminology Changes

| Location | Before | After | Context |
|----------|--------|-------|---------|
| Frontmatter ID | `L1-04` | `flujo-04` | ID format |
| Header | `(L1-04)` | removed | Remove L prefix |
| Dependencias | `Kata L0` | `Kata de principios` | Level naming |
| Dependencias | `Katas de Componentes y Técnicas` | `Katas de patrón y técnica` | Level naming |
| Guardrails section | `Guardrails Relacionados` | preserved (already canonical) | Governance term |
| Header pasos | `Practicante y Asistente` | `Orquestador y Asistente` | Role naming |
| Paso 1 | `(Practicante)` (x2) | `(Orquestador)` | Role naming |
| Paso 2 | `instruido por Practicante` | `instruido por Orquestador` | Role naming |
| Paso 2 | `Instrucción (Practicante)` | `Instrucción (Orquestador)` | Role naming |
| Paso 2 | `Validación (Practicante)` | `Validación (Orquestador)` | Role naming |
| Paso 3 | `(Practicante y Asistente)` | `(Orquestador y Asistente)` | Role naming |
| Paso 3 | `Instrucción (Practicante)` | `Instrucción (Orquestador)` | Role naming |
| Paso 3 | `Validación (Practicante)` | `Validación (Orquestador)` | Role naming |
| Paso 4 | `(Practicante y Asistente` | `(Orquestador y Asistente` | Role naming |
| Paso 4 | `Instrucción (Practicante)` | `Instrucción (Orquestador)` | Role naming |
| Paso 4 | `Kata L2 o L3` | `Kata de patrón o técnica` | Level naming |
| Paso 4 | `Validación (Practicante)` | `Validación (Orquestador)` | Role naming |
| Paso 4 | `Katas L2/L3` | `Katas de patrón/técnica` | Level naming |
| Paso 5 | `(Practicante y Asistente` | `(Orquestador y Asistente` | Role naming |
| Paso 5 | `Instrucción (Practicante)` | `Instrucción (Orquestador)` | Role naming |
| Paso 5 | `Kata L3-05` | `Kata de técnica de Testing Estratégico` | Level naming |
| Paso 5 | `Ref: L3-05` | `Ref: técnica-testing-estratégico` | Reference format |
| Paso 5 | `Validación (Practicante)` | `Validación (Orquestador)` | Role naming |
| Paso 6 | `(Practicante y Asistente)` | `(Orquestador y Asistente)` | Role naming |
| Paso 6 | `Instrucción (Practicante)` | `Instrucción (Orquestador)` | Role naming |
| Paso 6 | `Validación (Practicante)` | `Validación (Orquestador)` | Role naming |
| Paso 7 | `(Practicante y Asistente)` | `(Orquestador y Asistente)` | Role naming |
| Paso 7 | `Instrucción (Practicante)` | `Instrucción (Orquestador)` | Role naming |
| Paso 7 | `Kata L3-05` | `Kata de técnica de Testing Estratégico` | Level naming |
| Paso 7 | `L3-05 Testing Estratégico` | `técnica-testing-estratégico` | Reference format |
| Paso 7 | `Validación (Practicante)` | `Validación (Orquestador)` | Role naming |
| Paso 8 | `(Practicante y Asistente)` | `(Orquestador y Asistente)` | Role naming |
| Paso 8 | `Instrucción (Practicante)` | `Instrucción (Orquestador)` | Role naming |
| Paso 8 | `Validación (Practicante)` | `Validación (Orquestador)` | Role naming |
| Paso 9 | `(Practicante y Asistente)` | `(Orquestador y Asistente)` | Role naming |
| Paso 9 | `Instrucción (Practicante)` | `Instrucción (Orquestador)` | Role naming |
| Paso 9 | `Validación (Practicante)` | `Validación (Orquestador)` | Role naming |
| Paso 9 | `Confirmación (Practicante)` | `Confirmación (Orquestador)` | Role naming |
| Paso 9 | `Kata L1-03` | `Kata de flujo de Implementación de HU` | Level naming |
| Paso 9 | `Katas L2/L3` | `Katas de patrón/técnica` | Level naming |
| Resultado | `Katas L2 y L3` | `Katas de patrón y técnica` | Level naming |
| Resultado | `Kata L1-03` | `Kata de flujo de Implementación de HU` | Level naming |

**Total Replacements**: ~40 terminology changes

## Notes

1. **Full Jidoka coverage**: All 9 steps now have explicit verification criteria and correction guidance, transforming this workflow kata into an active quality sensor at each step.

2. **Heavy Practicante → Orquestador replacement**: This kata had extensive use of "Practicante" which is not the canonical term. "Orquestador" is the correct role name per ontology v2.1.

3. **L0/L1/L2/L3 → principios/flujo/patrón/técnica**: All level references normalized to semantic naming.

4. **References to specific katas updated**: `L1-03`, `L3-05` references were updated to use descriptive names with semantic level prefix.

5. **Guardrails section preserved**: The kata already used "Guardrails Relacionados" which is canonical.

6. **No DoD occurrences**: This kata did not use "DoD" terminology.

---

**Report Generated**: 2026-01-11T23:55:00
