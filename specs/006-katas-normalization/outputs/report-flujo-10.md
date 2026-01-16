# Normalization Report: flujo/10-alineamiento-convenciones-repositorio.md

**Processed**: 2026-01-12
**Coherence**: aligned
**Orquestador Approval**: approved

## Semantic Coherence Check

**Level**: flujo
**Guiding Question**: ¿Cómo fluye?
**Assessment**: Content primarily answers the guiding question: **YES**

The document describes the flow for aligning new code with existing repository conventions. It guides HOW the process flows from identifying archetypes, through extracting conventions via checklist, to applying those conventions in new code. This is a workflow kata correctly placed in `flujo/`.

## Jidoka Inline Changes

This kata has 3 steps that now include Jidoka Inline verification and correction guidance:

| Step | Header | Verification Added | Correction Added |
|------|--------|-------------------|------------------|
| 1 | Identificar el Arquetipo | ✅ Yes | ✅ Yes |
| 2 | Extraer las Convenciones Clave | ✅ Yes | ✅ Yes |
| 3 | Aplicar las Convenciones Extraídas | ✅ Yes | ✅ Yes |

**Total Steps**: 3
**Steps Modified**: 3

### Jidoka Content Added

**Paso 1 - Identificar el Arquetipo:**
- **Verificación:** Se han identificado 1-2 archivos arquetipo del mismo tipo que el componente a crear, y estos archivos son representativos del estándar del proyecto.
- **Si no puedes continuar:** No se encuentran arquetipos → Buscar en otras features o módulos del proyecto; si no existen, documentar que se está creando el primer ejemplar de este tipo.

**Paso 2 - Extraer las Convenciones Clave:**
- **Verificación:** El checklist correspondiente al tipo de componente está completado con respuestas concretas extraídas del arquetipo (no asunciones).
- **Si no puedes continuar:** Checklist incompleto → El arquetipo no cubre todos los aspectos; buscar un segundo arquetipo complementario o consultar con el Orquestador.

**Paso 3 - Aplicar las Convenciones Extraídas:**
- **Verificación:** El nuevo código sigue las convenciones extraídas del checklist. Cualquier desviación está documentada con justificación explícita.
- **Si no puedes continuar:** Desviación no justificable → Revisar el arquetipo nuevamente para entender el patrón correcto, o escalar al Orquestador si se requiere una excepción arquitectónica.

## Terminology Changes

| Location | Before | After | Context |
|----------|--------|-------|---------|
| Title | `# L1-10: Kata de...` | `# Kata de...` | Remove L prefix |
| Header | (none) | `**ID**: flujo-10` | Added ID field |
| Propósito | `desarrollador (o al agente IA)` | `Orquestador (o al Agente IA)` | Role naming |

**Total Replacements**: 3 terminology changes

## Notes

1. **Compact kata, full Jidoka coverage**: Despite having only 3 steps, each now has explicit verification criteria aligned with the kata's core principle of "verificar antes de codificar".

2. **Developer → Orquestador**: One instance of "desarrollador" was replaced with "Orquestador" in the purpose statement.

3. **No Reglas/DoD/L0-L3 references**: This kata was relatively clean of deprecated terminology. No "Reglas", "DoD", or numeric level references were present.

4. **Preserved domain-specific checklists**: The detailed checklists for Controllers, Handlers, Tests, and Services were preserved as-is since they contain valuable domain knowledge specific to .NET/C# projects.

5. **Added ID field**: The kata lacked an explicit ID field in the header, so `**ID**: flujo-10` was added for consistency with other normalized katas.

6. **Practical kata**: This is a very actionable kata focused on preventing "hallucination" errors by forcing verification against existing code before writing new code.

---

**Report Generated**: 2026-01-12T00:25:00
