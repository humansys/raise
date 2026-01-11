# Implementation Plan: Simplificar Exposición de Jidoka

**Branch**: `003-simplify-jidoka` | **Date**: 2026-01-11 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-simplify-jidoka/spec.md`

## Summary

Simplify Jidoka presentation in RaiSE documentation by applying the ADR-009 pattern (Simple Interface + Internal Philosophy). Stage 0-1 learners see "Parar si algo falla" (4 words, accessible), while Stage 3 learners access the formal 4-step TPS cycle (Detectar → Parar → Corregir → Continuar). This eliminates barriers B-01 (terminological) and B-02 (Lean/TPS conceptual cluster), reducing onboarding complexity by 5%.

**Primary Requirement**: Update glossary v2.1 and ontology bundle v2.1 to present Jidoka with progressive disclosure, removing TPS prerequisites from beginner-facing content.

**Technical Approach**: In-place markdown editing using staged content structure (Stage 0-1 | Stage 3), validated with text search and manual gates.

## Technical Context

**Type de Trabajo**: Creación/modificación de documentación conceptual (no desarrollo de software tradicional)
**Language/Version**: Markdown (CommonMark spec)
**Primary Dependencies**: Text editor, Git 2.0+
**Storage**: Git version control (plain text markdown files)
**Testing**: Manual validation + automated text search (grep, wc)
**Target Platform**: Documentation readers (humans) - GitLab web UI, offline markdown viewers, PDF exports
**Project Type**: Documentation
**Performance Goals**: N/A (human-readable documents)
**Constraints**:
- Simplified definition ≤10 words (SC-001)
- Zero TPS/Lean terminology in Stage 0-1 sections (SC-002)
- Preserve canonical term "Jidoka" (FR-007)

**Scale/Scope**:
- 2 documents to modify (~100KB total)
- 1 glossary entry to restructure
- ~3-5 references in ontology bundle (estimated)

**Tools**:
- `grep`: Search for prohibited terms, verify stage separation
- `wc`: Word count validation
- `sed`: Extract sections for validation (Stage 0-1 vs Stage 3)
- Git: Version control, branching, rollback safety

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*
*Reference: `.specify/memory/constitution.md`*

| Principio | Verificación | Estado |
|-----------|--------------|--------|
| I. Coherencia Semántica | Términos alineados con glosario: "Jidoka" preservado como canónico, no se crean aliases. Definiciones Stage 0-1 y Stage 3 son complementarias, no contradictorias. | ✅ |
| II. Governance como Código | Artefactos versionados en Git: Cambios a glossary y ontology bundle en feature branch 003-simplify-jidoka. Commit message con trazabilidad a QW-01. | ✅ |
| III. Validación en Cada Fase | Gates definidos: Gate-Terminología (canonical terms), Gate-Coherencia (no contradictions). 6 Success Criteria medibles (SC-001 a SC-006). | ✅ |
| IV. Simplicidad | Sin abstracciones innecesarias: Usa estructura simple (Stage 0-1 \| Stage 3) sin crear nuevas categorías o taxonomías. Definición simplificada es directa (4 palabras). | ✅ |
| V. Mejora Continua | Feedback loops identificados: Feature 001 audit identificó barreras B-01/B-02. Feature 003 las mitiga. Post-implementación: medir comprensión de nuevos Orquestadores. | ✅ |

**Post-Design Re-Check** (after Phase 1):

| Principio | Re-Verificación | Estado |
|-----------|-----------------|--------|
| I. Coherencia Semántica | Data model confirms single canonical entry, no aliases. Template ensures consistency between simple and formal definitions. | ✅ |
| II. Governance como Código | Research.md, data-model.md, quickstart.md all in Git. Decisions documented with rationale (D1-D5, T1-T2). | ✅ |
| III. Validación en Cada Fase | Validation schema defined in data-model.md. Quickstart includes step-by-step gate checks. | ✅ |
| IV. Simplicidad | Rejected alternatives that added complexity (separate docs, HTML collapsibles, new aliases). Chose simplest viable approach (inline staged sections). | ✅ |
| V. Mejora Continua | Q1, Q2 in research.md identify risks/unknowns. Quickstart includes troubleshooting section for iteration. | ✅ |

**Conclusion**: ✅ ALL GATES PASS - No violations. Feature aligns with all 5 Constitution principles.

## Project Structure

### Documentation (this feature)

```text
specs/003-simplify-jidoka/
├── spec.md              # Feature specification
├── plan.md              # This file (/speckit.plan output)
├── research.md          # Phase 0: Design decisions D1-D5, T1-T2
├── data-model.md        # Phase 1: Entry structure, validation schema
├── quickstart.md        # Phase 1: Step-by-step implementation guide
└── checklists/
    └── requirements.md  # Spec quality validation (already completed)
```

### Source Code (repository root)

**Note**: This feature modifies existing documentation, not source code.

```text
docs/framework/v2.1/model/
├── 20-glossary-v2.1.md         # MODIFIED: Jidoka entry restructured
├── 20a-glossary-seed.md        # NO CHANGE (Feature 002 deliverable)
└── 25-ontology-bundle-v2_1.md  # MODIFIED: Jidoka references updated
```

**Structure Decision**: Documentation-only feature. No src/, tests/, or code directories involved. All changes are markdown text edits in `docs/framework/v2.1/model/`.

## Complexity Tracking

**No Constitution violations** - this table is not needed.

All principles pass both initial and post-design checks. Feature maintains simplicity by reusing established patterns (ADR-009, learning path stages from Feature 001).

## Implementation Phases

### Phase 0: Research & Design Decisions ✅ COMPLETE

**Artifact**: `research.md`

**Decisions Made**:
- **D1**: Glossary entry structure (single entry with staged sections)
- **D2**: Simplified definition wording ("Parar si algo falla")
- **D3**: Ontology bundle consistency (dual-mode refs by section stage)
- **D4**: Stage indicator format (inline markers: "Stage 0-1", "Stage 3")
- **D5**: TPS terminology migration (to "Contexto Histórico" subsection in Stage 3)
- **T1**: Validation approach (grep + wc + manual gates)
- **T2**: Document modification strategy (in-place edit with Git rollback safety)

**Alternatives Considered & Rejected**:
- Separate glossary lite document (Feature 002 already did this)
- HTML collapsible markdown (poor renderer compatibility)
- Remove formal definition entirely (violates Heutagogía §5)

---

### Phase 1: Data Model & Quickstart ✅ COMPLETE

**Artifacts**:
- `data-model.md`: Glossary entry structure, ontology bundle section types, validation schema
- `quickstart.md`: 10-step implementation guide with commands

**Key Design Elements**:
- **Glossary Entry Entity**: 6 attributes (term, simple_interface, simple_definition, example, formal_definition, historical_context)
- **Ontology Bundle Section Entity**: 4 attributes (section_name, section_stage, reference_type, reference_text)
- **Validation Schema**: Gate-Terminología, Gate-Coherencia, SC-001 to SC-006

**Templates Created**:
- Glossary entry markdown template (with filled example)
- Ontology bundle reference templates (Stage 0-1 vs Stage 3)

---

### Phase 2: Tasks Generation (NEXT)

**Command**: `/speckit.tasks`

**Expected Output**: `tasks.md` with atomic implementation tasks

**Estimated Task Count**: ~15-20 tasks
- Setup (read current content, search references)
- Glossary modification (apply template, validate)
- Ontology bundle modification (classify sections, update refs)
- Validation (gates, success criteria)
- Commit

---

### Phase 3: Implementation (FUTURE)

**Command**: `/speckit.implement`

**Executor**: Orquestador or Agent

**Deliverables**:
- Updated `docs/framework/v2.1/model/20-glossary-v2.1.md`
- Updated `docs/framework/v2.1/model/25-ontology-bundle-v2_1.md`
- Git commit with feature message

---

### Phase 4: Analysis (FUTURE)

**Command**: `/speckit.analyze`

**Purpose**: Cross-artifact consistency validation

**Checks**:
- Spec requirements vs implementation
- Success criteria verification
- Gate validation results

---

## Risk Mitigation

| Risk (from spec) | Mitigation (implemented in plan) |
|------------------|----------------------------------|
| Simplified definition loses nuance | Formal definition preserved in Stage 3 (D1). Cross-validation in quickstart Step 8. |
| Advanced users frustrated | Clear stage indicators (D4). Formal definition readily accessible via section navigation. |
| Inconsistency between glossary and bundle | Validation schema in data-model.md. Quickstart Step 6 explicit consistency check. |
| Breaking existing references | Quickstart Step 2 searches all refs. T2 decision: Git rollback if issues found. |

---

## Open Questions (from Research)

### Q1: Other documents referencing "4-step Jidoka cycle"?

**Resolution Path**: Quickstart Step 2 searches `docs/` directory. If found, update per D3 strategy (simplified in Stage 0-1 context, formal in Stage 3 context).

**Status**: To be verified during `/speckit.implement`

### Q2: Should glossary-seed.md reference new Jidoka entry?

**Resolution**: No change needed. Glossary-seed (Feature 002) covers 5 concepts (Orquestador, Spec, Agent, Validation Gate, Constitution). Jidoka is not a Stage 0 concept currently.

**Status**: RESOLVED - out of scope for Feature 003

---

## Success Metrics

**From spec SC-001 to SC-006**:

| Metric | Target | Validation Method |
|--------|--------|-------------------|
| SC-001: Word count | ≤10 words | `wc -w` on simplified definition → 4 |
| SC-002: TPS terms in Stage 0-1 | 0 | `grep -c "TPS\|Toyota\|Lean\|自働化"` → 0 |
| SC-003: Gate-Terminología | PASS | Manual check: canonical term preserved |
| SC-004: Gate-Coherencia | PASS | Manual check: no contradictions |
| SC-005: Complexity reduction | 5% | Prerequisite count: 1 (TPS) → 0 |
| SC-006: Comprehension time | <30s | Proxy: 4 words @ 200wpm ≈ 11s |

**All metrics defined in data-model.md validation schema.**

---

## References

- **Spec**: [spec.md](./spec.md)
- **Research**: [research.md](./research.md)
- **Data Model**: [data-model.md](./data-model.md)
- **Quickstart**: [quickstart.md](./quickstart.md)
- **ADR-009**: Simple Interface + Internal Philosophy pattern
- **Feature 001**: Learning path stages, barriers B-01/B-02
- **Feature 002**: Glossary-seed (similar simplification approach)
- **Constitution**: `.specify/memory/constitution.md` v1.0.0

---

*Implementation plan complete. Ready for `/speckit.tasks` to generate atomic task list.*
