# Normalization Report: principios/00-raise-katas-documentation.md

**Processed**: 2026-01-11
**Coherence**: aligned
**Orquestador Approval**: approved

## Semantic Coherence Check

**Level**: principios
**Guiding Question**: ¿Por qué? ¿Cuándo?
**Assessment**: Content primarily answers the guiding question: **YES**

The document explains WHY the kata system exists (promote reliability, codify engineering culture, guide AI development) and WHEN to use katas (during planning, code generation, onboarding). This is a foundational philosophy document, correctly placed in `principios/`.

## Jidoka Inline Changes

**Note**: This kata is a conceptual/philosophy document, not a step-by-step workflow. It does not contain `### Paso N:` steps, so Jidoka Inline structure is not applicable.

| Step | Header | Verification Added | Correction Added |
|------|--------|-------------------|------------------|
| N/A  | Document is conceptual, no workflow steps | N/A | N/A |

**Total Steps**: 0 (conceptual document)
**Steps Modified**: 0

## Terminology Changes

| Location | Before | After | Context |
|----------|--------|-------|---------|
| §Introducción | "desarrolladores humanos" | "Orquestadores humanos" | Role reference |
| §Propósito.3 | "desarrolladores" | "Orquestadores" | Onboarding context |
| §Jerarquía L0 | "Nivel L0:" | "Nivel Principios:" | Level naming |
| §Jerarquía L1 | "Nivel L1:" | "Nivel Flujo:" | Level naming |
| §Jerarquía L2 | "Nivel L2:" | "Nivel Patrón:" | Level naming |
| §Jerarquía L3 | "Nivel L3:" | "Nivel Técnica:" | Level naming |
| §Flujos IA.1 | "katas L1 (y L0 subyacentes)" | "katas de flujo (y principios subyacentes)" | Level reference |
| §Flujos IA.2 | "katas L2 y L3" | "katas de patrón y técnica" | Level reference |
| §Relación RaiSE | "Reglas Explícitas" | "Guardrails Explícitos" | Governance term |
| §Relación RaiSE | "desarrolladores" | "Orquestadores" | Role reference |
| §Conclusión | "desarrolladores" | "Orquestadores" | Role reference |
| All L0/L1/L2/L3 examples | `L0-01-meta-kata...` etc. | Removed (obsolete file references) | File examples |

**Total Replacements**: 12 terminology changes

## Notes

1. **No Jidoka needed**: This is a **principios** level document that explains philosophy, not a workflow. Jidoka Inline is for step-by-step processes.

2. **Level naming updated**: All `L0/L1/L2/L3` references replaced with semantic level names (`principios/flujo/patrón/técnica`).

3. **Added guiding questions**: Each level section now includes its semantic guiding question for clarity.

4. **Removed obsolete file examples**: The old `L0-01-meta-kata-desarrollo.md` style filenames were removed since the file structure has changed in feature 005.

5. **Developer → Orquestador**: Replaced 4 instances where "desarrollador" referred to the human role in RaiSE.

6. **Reglas → Guardrails**: Changed "Reglas Explícitas y Consistentes" to "Guardrails Explícitos y Consistentes" per ontology v2.1.

---

**Report Generated**: 2026-01-11T23:15:00
