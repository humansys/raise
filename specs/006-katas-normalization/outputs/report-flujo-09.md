# Normalization Report: flujo/09-ecosystem-discovery-feature-design.md

**Processed**: 2026-01-11
**Coherence**: aligned
**Orquestador Approval**: approved

## Semantic Coherence Check

**Level**: flujo
**Guiding Question**: ¿Cómo fluye?
**Assessment**: Content primarily answers the guiding question: **YES**

The document describes the flow for ecosystem discovery and zero-duplication feature design. It guides HOW the process flows from comprehensive ecosystem inventory through overlap analysis, impact assessment, technical design, and validation documentation. This is a workflow kata correctly placed in `flujo/`.

## Jidoka Inline Changes

This kata has 9 steps organized in 4 phases that now include Jidoka Inline verification and correction guidance:

| Step | Header | Verification Added | Correction Added |
|------|--------|-------------------|------------------|
| 0.1 | Exhaustive Service Inventory | ✅ Yes | ✅ Yes |
| 0.2 | Zero-Duplication Overlap Analysis | ✅ Yes | ✅ Yes |
| 0.3 | Architecture Continuity Validation | ✅ Yes | ✅ Yes |
| 1.1 | Service-Specific Impact Matrix | ✅ Yes | ✅ Yes |
| 1.2 | Reuse-First Design Options | ✅ Yes | ✅ Yes |
| 2.1 | Minimal Viable Changes Design | ✅ Yes | ✅ Yes |
| 2.2 | Contract Extensions Design | ✅ Yes | ✅ Yes |
| 3.1 | Zero-Duplication Evidence | ✅ Yes | ✅ Yes |
| 3.2 | Implementation Roadmap | ✅ Yes | ✅ Yes |

**Total Steps**: 9
**Steps Modified**: 9

### Jidoka Content Added

**Paso 0.1 - Service Inventory:**
- **Verificación:** Existe `capability-matrix.yaml` con mapeo de ≥90% de los servicios del ecosistema y sus capacidades.
- **Si no puedes continuar:** Documentación esencial faltante → Ejecutar primero la kata de flujo de Generación de Documentación Esencial para los servicios sin documentar.

**Paso 0.2 - Overlap Analysis:**
- **Verificación:** Existe `overlap-analysis.yaml` con clasificación de risk levels (CRITICAL/HIGH/MEDIUM) para cada overlap detectado.
- **Si no puedes continuar:** Overlap ≥90% detectado sin estrategia → STOP y documentar justificación de por qué no se puede reutilizar el servicio existente.

**Paso 0.3 - Architecture Validation:**
- **Verificación:** Existe `architecture-validation.yaml` con status "APPROVED" y score de continuity ≥80%.
- **Si no puedes continuar:** Architecture compromised → Revisar propuesta de cambios para eliminar breaking changes y preservar patrones existentes.

**Paso 1.1 - Impact Matrix:**
- **Verificación:** Existe `impact-matrix.yaml` con análisis de impacto para cada servicio del ecosistema y executive summary con métricas de reutilización.
- **Si no puedes continuar:** Servicios sin análisis de impacto → Completar el análisis para cada servicio antes de continuar con las opciones de diseño.

**Paso 1.2 - Design Options:**
- **Verificación:** Opción A documentada con reuse_percentage ≥80% y justificación basada en el análisis del ecosistema.
- **Si no puedes continuar:** Opción A con reuse <80% → Revisar capability-matrix.yaml para identificar más oportunidades de reutilización antes de proceder.

**Paso 2.1 - Minimal Changes:**
- **Verificación:** Extension points definidos con lista explícita de componentes reutilizados vs nuevos, y diagrama de flujo de integración.
- **Si no puedes continuar:** Integration flow con servicios no analizados → Regresar a Fase 0 para completar el discovery de esos servicios.

**Paso 2.2 - Contract Extensions:**
- **Verificación:** Extensiones de contrato diseñadas son 100% backward compatible (solo operaciones aditivas, sin modificar existentes).
- **Si no puedes continuar:** Breaking changes detectados → Rediseñar extensiones para que sean aditivas, o crear versión v2 del contrato si es absolutamente necesario.

**Paso 3.1 - Evidence Generation:**
- **Verificación:** Evidence matrix documenta que cada funcionalidad requerida está cubierta por REUSE o marcada explícitamente como NEW con justificación.
- **Si no puedes continuar:** Funcionalidad sin clasificar → Revisar capability-matrix.yaml y overlap-analysis.yaml para determinar si es reutilización o nueva.

**Paso 3.2 - Implementation Roadmap:**
- **Verificación:** Roadmap incluye fases con duración, entregables específicos, y validation gate por fase con criterios medibles.
- **Si no puedes continuar:** Validation gates no definidos → Agregar criterios de validación específicos para cada fase antes de iniciar implementación.

## Terminology Changes

| Location | Before | After | Context |
|----------|--------|-------|---------|
| Title | `(L1-09)` | removed | Remove L prefix |
| Frontmatter ID | `L1-09` | `flujo-09` | ID format |
| Dependencias | `L1-07: Generación de...` | `Kata de flujo: Generación de...` | Level naming |
| Dependencias | `L0-03: Meta-Kata del...` | `Kata de principios: Meta-Kata del...` | Level naming |
| Header | `Reglas Cursor Relacionadas` | `Guardrails Cursor Relacionados` | Governance term |
| Guardrails | `Reglas de DRY, KISS, YAGNI` | `Guardrails de DRY, KISS, YAGNI` | Governance term |
| Guardrails | `Reglas de zero-duplication` | `Guardrails de zero-duplication` | Governance term |

**Total Replacements**: 7 terminology changes

## Notes

1. **Full Jidoka coverage**: All 9 steps across 4 phases now have explicit verification criteria and correction guidance tailored to the specific deliverables of each step.

2. **Already used "Orquestador"**: This kata was already using the canonical term "Orquestador" in its instructions, so no role replacements were needed.

3. **Reglas → Guardrails**: The "Reglas Cursor Relacionadas" section and its content were updated to use "Guardrails".

4. **Strong existing structure**: This kata already had a "VALIDATION GATES MANDATORIOS" section, which aligns well with Jidoka principles. The inline Jidoka additions complement these gates by providing step-level verification.

5. **No Practicante/Developer usage**: This kata consistently used "Orquestador" and "Agente IA" as role names.

6. **Quantitative thresholds preserved**: The kata's specific numeric thresholds (≥90% coverage, ≥80% reuse, etc.) were preserved and referenced in the Jidoka verification criteria.

---

**Report Generated**: 2026-01-12T00:15:00
