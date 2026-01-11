# Tasks: Evaluación Ontológica para Disclosure Progresivo Heutagógico

**Input**: Design documents from `/specs/001-heutagogy-progressive-disclosure/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, quickstart.md ✅

**Type**: Trabajo de análisis ontológico (no desarrollo de software tradicional)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Feature directory**: `specs/001-heutagogy-progressive-disclosure/`
- **Source documents**: `docs/framework/v2.1/model/`, `docs/framework/v2.1/adrs/`
- **Output artifacts**: Feature directory until validated, then `docs/framework/v2.1/`

---

## Phase 1: Setup (Context Loading)

**Purpose**: Load and verify access to all source documents

- [x] T001 Verify access to constitution at docs/framework/v2.1/model/00-constitution-v2.md
- [x] T002 [P] Verify access to glossary at docs/framework/v2.1/model/20-glossary-v2.1.md
- [x] T003 [P] Verify access to methodology at docs/framework/v2.1/model/21-methodology-v2.md
- [x] T004 [P] Verify access to learning philosophy at docs/framework/v2.1/model/05-learning-philosophy-v2.md
- [x] T005 [P] Verify access to ontology bundle at docs/framework/v2.1/model/25-ontology-bundle-v2_1.md
- [x] T006 [P] Verify access to ADR-009 ShuHaRi at docs/framework/v2.1/adrs/adr-009-shuhari-hybrid.md
- [x] T007 Review data-model.md to confirm entity schemas at specs/001-heutagogy-progressive-disclosure/data-model.md

---

## Phase 2: Foundational (Analysis Framework)

**Purpose**: Establish analysis criteria before auditing — MUST complete before User Stories

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T008 Extract complete term list from glossary v2.1 (~35 términos) from docs/framework/v2.1/model/20-glossary-v2.1.md
- [x] T009 Define complexity classification rubric (basic/intermediate/advanced criteria) using data-model.md schema
- [x] T010 [P] Define ShuHaRi phase assignment rubric (shu/ha/ri criteria) based on research.md Decision 3
- [x] T011 [P] Define novice utility scoring rubric (high/medium/low criteria) per FR-002
- [x] T012 Establish Lean analysis template (Muda/Mura/Muri categories) per FR-004
- [x] T013 Confirm 7 seed concepts from research.md align with Ley de Miller (7±2) per SC-002

**Checkpoint**: Analysis framework ready — User Story implementation can now begin

---

## Phase 3: User Story 1 — Auditoría de Complejidad Ontológica (Priority: P1) 🎯 MVP

**Goal**: Generate audit-report.md with complete concept inventory, complexity classifications, dependency graph, and barriers identified.

**Independent Test**: audit-report.md contains 100% of glosario terms classified, with dependency graph and barriers mapped.

**Acceptance Criteria**:
1. Each concept has complexity level (basic/intermediate/advanced)
2. Each concept has dependency list mapped
3. Each concept has ShuHaRi phase assigned (shu/ha/ri)
4. Seed concepts (5-9) are identified
5. Barriers are classified by type (conceptual/terminological/structural)

### Implementation for User Story 1

- [x] T014 [US1] Create audit-report.md skeleton with sections per quickstart.md at specs/001-heutagogy-progressive-disclosure/audit-report.md
- [x] T015 [P] [US1] Classify Core Philosophy concepts (~8 terms) with complexity and dependencies in audit-report.md
- [x] T016 [P] [US1] Classify Workflow Entities concepts (~10 terms) with complexity and dependencies in audit-report.md
- [x] T017 [P] [US1] Classify Agent Ecosystem concepts (~6 terms) with complexity and dependencies in audit-report.md
- [x] T018 [P] [US1] Classify Kata System concepts (~5 terms) with complexity and dependencies in audit-report.md
- [x] T019 [P] [US1] Classify Roles & Actions concepts (~6 terms) with complexity and dependencies in audit-report.md
- [x] T020 [US1] Generate concept dependency graph (text-based or mermaid) in audit-report.md
- [x] T021 [US1] Assign ShuHaRi phase to each concept in audit-report.md
- [x] T022 [US1] Confirm and document seed concepts (5-9) in audit-report.md
- [x] T023 [US1] Identify and document barriers of entry (conceptual, terminological, structural) in audit-report.md
- [x] T024 [US1] Apply Lean analysis (Muda/Mura/Muri) to identified barriers in audit-report.md
- [x] T025 [US1] Validate audit-report.md passes Gate-Terminología (canonical terms used)
- [x] T026 [US1] Validate audit-report.md passes Gate-Coherencia (no contradictions with Constitution)

**Checkpoint**: audit-report.md complete and independently validated — MVP deliverable ready

---

## Phase 4: User Story 2 — Propuesta de Camino de Aprendizaje Gradual (Priority: P2)

**Goal**: Generate learning-path.md with 4 stages of progressive disclosure, each with concepts exposed, transition criteria, and heutagogic checkpoints.

**Independent Test**: learning-path.md defines 3-5 stages where Stage 0 exposes ≤5 concepts and each stage has explicit transition criteria.

**Acceptance Criteria**:
1. 3-5 stages defined with names and ShuHaRi phase alignment
2. Each stage exposes ≤7 new concepts (Ley de Miller)
3. Each stage has explicit transition criteria (observable indicators)
4. Each stage has heutagogic checkpoint question (§5 aligned)
5. Kata accessibility mapped by stage

### Implementation for User Story 2

**Prerequisite**: audit-report.md (T026) complete — provides concept classifications

- [x] T027 [US2] Create learning-path.md skeleton with 4-stage structure at specs/001-heutagogy-progressive-disclosure/learning-path.md
- [x] T028 [US2] Define Stage 0 (Primer Contacto): concepts, criteria, checkpoint in learning-path.md
- [x] T029 [US2] Define Stage 1 (Operacional/Shu): concepts, criteria, checkpoint in learning-path.md
- [x] T030 [US2] Define Stage 2 (Táctico/Ha): concepts, criteria, checkpoint in learning-path.md
- [x] T031 [US2] Define Stage 3 (Estratégico/Ri): concepts, criteria, checkpoint in learning-path.md
- [x] T032 [P] [US2] Map Kata accessibility by stage (none → flujo → patrón → all) in learning-path.md
- [x] T033 [P] [US2] Add concept-to-stage mapping table for 80%+ coverage per SC-004 in learning-path.md
- [x] T034 [US2] Verify each stage introduces ≤7 new concepts (Ley de Miller compliance)
- [x] T035 [US2] Validate heutagogic checkpoints align with §5 Heutagogía principle
- [x] T036 [US2] Validate learning-path.md passes Gate-Coherencia (aligned with Constitution)

**Checkpoint**: learning-path.md complete and independently validated

---

## Phase 5: User Story 3 — Identificación de Mejoras Pre-Avance (Priority: P3)

**Goal**: Generate improvement-proposals.md with prioritized improvements in ADR-lite format that reduce Stage 0 complexity by ≥30%.

**Independent Test**: improvement-proposals.md contains ≥3 Quick Wins, each with rationale, affected documents, and complexity reduction estimate.

**Acceptance Criteria**:
1. Each improvement has type (quick_win/structural/fundamental)
2. Each improvement has rationale (which barrier it eliminates)
3. Each improvement has affected documents listed
4. Quick Wins require no Constitution changes
5. Total improvements reduce Stage 0 complexity by ≥30%

### Implementation for User Story 3

**Prerequisites**: audit-report.md (T026) and learning-path.md (T036) complete — provide barriers and stage structure

- [x] T037 [US3] Create improvement-proposals.md skeleton with ADR-lite format at specs/001-heutagogy-progressive-disclosure/improvement-proposals.md
- [x] T038 [US3] Identify and document Quick Wins (≥3) based on barriers from audit-report.md
- [x] T039 [US3] Identify and document Structural Improvements based on learning-path.md gaps
- [x] T040 [US3] Identify and document Fundamental Improvements (may need ADR)
- [x] T041 [P] [US3] For each improvement: add rationale linking to specific barrier in improvement-proposals.md
- [x] T042 [P] [US3] For each improvement: list affected documents in improvement-proposals.md
- [x] T043 [US3] Estimate complexity reduction per improvement in improvement-proposals.md
- [x] T044 [US3] Calculate total Stage 0 reduction (must be ≥30% per SC-005) in improvement-proposals.md
- [x] T045 [US3] Validate no improvement violates Constitution principles §1-§8
- [x] T046 [US3] Validate improvement-proposals.md passes Gate-Coherencia
- [x] T047 [US3] Validate improvement-proposals.md passes Gate-Trazabilidad (rationale documented)

**Checkpoint**: improvement-proposals.md complete — all deliverables ready

---

## Phase 6: Polish & Cross-Cutting Validation

**Purpose**: Final validation across all artifacts

- [x] T048 [P] Cross-reference audit-report.md with learning-path.md (concept assignments match)
- [x] T049 [P] Cross-reference learning-path.md with improvement-proposals.md (improvements address right barriers)
- [x] T050 Verify all 3 artifacts use canonical terminology from glossary v2.1
- [x] T051 Update checklists/requirements.md with completion status at specs/001-heutagogy-progressive-disclosure/checklists/requirements.md
- [x] T052 Final Gate-Terminología validation across all artifacts
- [x] T053 Final Gate-Coherencia validation across all artifacts
- [x] T054 Final Gate-Trazabilidad validation (all decisions have rationale)
- [x] T055 Prepare summary for stakeholder review

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1: Setup ──────────────────────────────────────────────────────────┐
    │                                                                    │
    ▼                                                                    │
Phase 2: Foundational ───────────────────────────────────────────────────┤
    │ (BLOCKS all User Stories)                                          │
    ▼                                                                    │
Phase 3: User Story 1 (P1) ─── MVP ───────────────────────────────────┐  │
    │                                                                  │  │
    ▼                                                                  │  │
Phase 4: User Story 2 (P2) ───────────────────────────────────────────┤  │
    │                                                                  │  │
    ▼                                                                  │  │
Phase 5: User Story 3 (P3) ───────────────────────────────────────────┤  │
    │                                                                  │  │
    ▼                                                                  │  │
Phase 6: Polish ◄──────────────────────────────────────────────────────┘  │
                                                                          │
```

### User Story Dependencies

- **User Story 1 (P1)**: Depends on Phase 2 (Foundational) — No dependencies on other stories
- **User Story 2 (P2)**: Depends on Phase 2 + User Story 1 (needs concept classifications)
- **User Story 3 (P3)**: Depends on Phase 2 + User Stories 1 & 2 (needs audit + learning path)

### Parallel Opportunities Per Phase

**Phase 1 (Setup)**:
```
T002, T003, T004, T005, T006 — All can run in parallel (different source documents)
```

**Phase 2 (Foundational)**:
```
T010, T011 — Can run in parallel (different rubric types)
```

**Phase 3 (User Story 1)**:
```
T015, T016, T017, T018, T019 — All can run in parallel (different concept categories)
```

**Phase 4 (User Story 2)**:
```
T032, T033 — Can run in parallel (different sections)
```

**Phase 5 (User Story 3)**:
```
T041, T042 — Can run in parallel (different improvement attributes)
```

**Phase 6 (Polish)**:
```
T048, T049 — Can run in parallel (different cross-references)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T007)
2. Complete Phase 2: Foundational (T008-T013)
3. Complete Phase 3: User Story 1 (T014-T026)
4. **STOP and VALIDATE**: audit-report.md independently usable
5. Review with stakeholders before proceeding

### Incremental Delivery

| Milestone | Deliverable | Independent Value |
|-----------|-------------|-------------------|
| MVP | audit-report.md | Inventory of complexity — actionable for prioritization |
| +US2 | learning-path.md | Structured onboarding plan — usable for new Orquestadores |
| +US3 | improvement-proposals.md | Roadmap of improvements — actionable for v2.2 planning |

### Execution Recommendation

**Solo Orquestador**: Execute sequentially P1 → P2 → P3, stopping at each checkpoint to validate.

**Pair/Team**: After Foundational phase, US1 can proceed while US2/US3 prep work begins in parallel (conceptual alignment).

---

## Validation Gates Summary

| Gate | Applied To | Criteria |
|------|------------|----------|
| Gate-Terminología | All artifacts | Uses canonical terms from glossary v2.1 |
| Gate-Coherencia | All artifacts | No contradictions with Constitution §1-§8 |
| Gate-Trazabilidad | improvement-proposals.md | Each improvement has documented rationale |
| Ley de Miller | learning-path.md | Each stage introduces ≤7 new concepts |
| SC-005 | improvement-proposals.md | Stage 0 complexity reduced by ≥30% |

---

## Notes

- [P] tasks = different files/sections, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story produces an independently validated artifact
- Validation is via Validation Gates, not traditional tests
- Commit after each task or logical group
- Stop at any checkpoint to validate artifact independently
