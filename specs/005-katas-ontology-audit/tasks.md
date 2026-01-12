# Tasks: Katas Ontology Alignment Audit

**Input**: Design documents from `/specs/005-katas-ontology-audit/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

**Note**: This is a documentation-centric analysis feature. The "implementation" consists of analyzing kata files and generating structured output documents—no production code is created.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

All outputs go to: `specs/005-katas-ontology-audit/outputs/`

---

## Phase 1: Setup

**Purpose**: Prepare output directory and validate input sources

- [x] T001 Verify ontology source files exist at `docs/framework/v2.1/model/20-glossary-v2.1.md` and `docs/framework/v2.1/model/21-methodology-v2.md`
- [x] T002 [P] List all kata files in `src/katas/` directory (found 21 kata files + README)
- [x] T003 [P] Create output directory structure at `specs/005-katas-ontology-audit/outputs/`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Create reusable reference data needed by all user stories

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Create ontology slots reference table (10 slots from research.md §2) in working notes
- [x] T005 [P] Create deprecated terminology mapping reference (6 terms from research.md §4) in working notes
- [x] T006 [P] Create project markers detection list (5 markers from research.md §5) in working notes
- [x] T007 [P] Create Jidoka Inline validation checklist (format from research.md §3) in working notes

**Checkpoint**: Reference data ready - user story implementation can begin

---

## Phase 3: User Story 1 - Ontology Target State Definition (Priority: P1) 🎯 MVP

**Goal**: Define what katas SHOULD exist for v0 RaiSE framework based on ontology

**Independent Test**: Produce a document listing all 10 ontology slots with level, topic, and source reference

### Implementation for User Story 1

- [x] T008 [US1] Create `specs/005-katas-ontology-audit/outputs/kata-coverage-matrix.md` header and metadata section
- [x] T009 [US1] Document Principios level slots (PRIN-001, PRIN-002) with expected topics in `outputs/kata-coverage-matrix.md`
- [x] T010 [US1] Document Flujo level slots (FLUJO-001, FLUJO-002, FLUJO-003) with expected topics in `outputs/kata-coverage-matrix.md`
- [x] T011 [US1] Document Patrón level slots (PATRON-001, PATRON-002, PATRON-003) with expected topics in `outputs/kata-coverage-matrix.md`
- [x] T012 [US1] Document Técnica level slots (TEC-001, TEC-002) with expected topics in `outputs/kata-coverage-matrix.md`

**Checkpoint**: Target state document shows all 10 expected kata slots - US1 complete

---

## Phase 4: User Story 2 - Kata Ontology Mapping (Priority: P1)

**Goal**: Map each of the 23 existing katas to an ontology slot (Mapped) or classify as Orphan

**Independent Test**: Every kata has a classification with rationale; every slot shows filled/gap status

**Depends On**: US1 (target state must be defined first)

### Principios Level (L0) Katas

- [ ] T013 [P] [US2] Analyze `src/katas/L0-00-raise-katas-documentation.md`: check Jidoka compliance, deprecated terms, project markers → classify in `outputs/kata-coverage-matrix.md`
- [ ] T014 [P] [US2] Analyze `src/katas/L0-01-raise-kata-execution-protocol.md`: check Jidoka compliance, deprecated terms, project markers → classify in `outputs/kata-coverage-matrix.md`

### Flujo Level (L1) Katas

- [ ] T015 [P] [US2] Analyze `src/katas/L1-01-proceso-estimacion.md`: check Jidoka compliance, deprecated terms, project markers → classify in `outputs/kata-coverage-matrix.md`
- [ ] T016 [P] [US2] Analyze `src/katas/L1-02-analisis-repositorio-backend.md`: check Jidoka compliance, deprecated terms, project markers → classify in `outputs/kata-coverage-matrix.md`
- [ ] T017 [P] [US2] Analyze `src/katas/L1-03-analisis-repositorio-frontend.md`: check Jidoka compliance, deprecated terms, project markers → classify in `outputs/kata-coverage-matrix.md`
- [ ] T018 [P] [US2] Analyze `src/katas/L1-04-generacion-plan-implementacion-hu.md`: check Jidoka compliance, deprecated terms, project markers → classify in `outputs/kata-coverage-matrix.md`
- [ ] T019 [P] [US2] Analyze `src/katas/L1-05-generacion-plan-estimacion.md`: check Jidoka compliance, deprecated terms, project markers → classify in `outputs/kata-coverage-matrix.md`
- [ ] T020 [P] [US2] Analyze `src/katas/L1-06-analisis-backlog-y-refinamiento.md`: check Jidoka compliance, deprecated terms, project markers → classify in `outputs/kata-coverage-matrix.md`
- [ ] T021 [P] [US2] Analyze `src/katas/L1-07-Generacion-Documentacion-Esencial-SAR.md`: check Jidoka compliance, deprecated terms, project markers → classify in `outputs/kata-coverage-matrix.md`
- [ ] T022 [P] [US2] Analyze `src/katas/L1-08-Diseño-Feature-Backend-Microservicios-Jafra.md`: check Jidoka compliance, deprecated terms, project markers → classify in `outputs/kata-coverage-matrix.md`
- [ ] T023 [P] [US2] Analyze `src/katas/L1-09-Documentacion-Completa-Microservicio-RAG.md`: check Jidoka compliance, deprecated terms, project markers → classify in `outputs/kata-coverage-matrix.md`
- [ ] T024 [P] [US2] Analyze `src/katas/L1-10-Kata-Diseño-US.md`: check Jidoka compliance, deprecated terms, project markers → classify in `outputs/kata-coverage-matrix.md`

### Patrón Level (L2) Katas

- [ ] T025 [P] [US2] Analyze `src/katas/L2-01-analisis-ecosistema-proyecto.md`: check Jidoka compliance, deprecated terms, project markers → classify in `outputs/kata-coverage-matrix.md`
- [ ] T026 [P] [US2] Analyze `src/katas/L2-02-arquitectura-existente.md`: check Jidoka compliance, deprecated terms, project markers → classify in `outputs/kata-coverage-matrix.md`
- [ ] T027 [P] [US2] Analyze `src/katas/L2-03-stack-tecnologico.md`: check Jidoka compliance, deprecated terms, project markers → classify in `outputs/kata-coverage-matrix.md`
- [ ] T028 [P] [US2] Analyze `src/katas/L2-04-patrones-de-codigo.md`: check Jidoka compliance, deprecated terms, project markers → classify in `outputs/kata-coverage-matrix.md`
- [ ] T029 [P] [US2] Analyze `src/katas/L2-05-documentacion-tecnica.md`: check Jidoka compliance, deprecated terms, project markers → classify in `outputs/kata-coverage-matrix.md`
- [ ] T030 [P] [US2] Analyze `src/katas/L2-06-infra-dependencias.md`: check Jidoka compliance, deprecated terms, project markers → classify in `outputs/kata-coverage-matrix.md`

### Técnica Level (L3) Katas

- [ ] T031 [P] [US2] Analyze all L3-* katas in `src/katas/` (if any): check Jidoka compliance, deprecated terms, project markers → classify in `outputs/kata-coverage-matrix.md`

### Special/Other Katas

- [ ] T032 [P] [US2] Analyze `src/katas/zc-kata-tech-design.md`: check Jidoka compliance, deprecated terms, project markers → classify in `outputs/kata-coverage-matrix.md`

### US2 Consolidation

- [ ] T033 [US2] Update slot status (filled/gap) for all 10 ontology slots in `outputs/kata-coverage-matrix.md`
- [ ] T034 [US2] Create detailed orphan analysis in `specs/005-katas-ontology-audit/outputs/orphan-katas.md` with rationale for each orphan
- [ ] T035 [US2] Generate `specs/005-katas-ontology-audit/outputs/kata-coverage-matrix.json` matching schema in `contracts/coverage-matrix.schema.json`

**Checkpoint**: All 23 katas classified (mapped or orphan); all 10 slots show filled/gap - US2 complete

---

## Phase 5: User Story 3 - Migration Roadmap Generation (Priority: P2)

**Goal**: Create actionable roadmap showing how to align kata ecosystem with ontology

**Independent Test**: Roadmap contains specific tasks (rename, restructure, archive) for each non-compliant kata

**Depends On**: US2 (kata mapping must be complete first)

### Implementation for User Story 3

- [ ] T036 [US3] Create `specs/005-katas-ontology-audit/outputs/migration-roadmap.md` with header and priority sections
- [ ] T037 [US3] Generate High Priority tasks (rename-only) for mapped katas with deprecated L0-L3 naming in `outputs/migration-roadmap.md`
- [ ] T038 [US3] Generate Medium Priority tasks (restructure) for katas missing Jidoka Inline in `outputs/migration-roadmap.md`
- [ ] T039 [US3] Generate Low Priority tasks (archive) for orphan katas in `outputs/migration-roadmap.md`
- [ ] T040 [US3] Add Gap-Filling recommendations for unfilled ontology slots in `outputs/migration-roadmap.md`
- [ ] T041 [US3] Generate `specs/005-katas-ontology-audit/outputs/migration-roadmap.json` with structured task list

**Checkpoint**: Migration roadmap shows all tasks with priority, effort, and before/after specifications - US3 complete

---

## Phase 6: User Story 4 - Kata Coverage Report (Priority: P3)

**Goal**: Provide executive summary of v0 framework readiness with coverage percentages

**Independent Test**: Report shows coverage % per level and overall; stakeholders can assess readiness without reading all katas

**Depends On**: US2 (mapping data needed for statistics)

### Implementation for User Story 4

- [ ] T042 [US4] Add Summary section to `outputs/kata-coverage-matrix.md` with total counts and percentages
- [ ] T043 [US4] Add By-Level breakdown showing filled/gap ratio per level in `outputs/kata-coverage-matrix.md`
- [ ] T044 [US4] Add Jidoka Compliance summary (% of katas with proper Jidoka Inline) in `outputs/kata-coverage-matrix.md`
- [ ] T045 [US4] Add Recommendations section prioritizing gap-filling and migration work in `outputs/kata-coverage-matrix.md`
- [ ] T046 [US4] Update JSON metadata with summary statistics in `outputs/kata-coverage-matrix.json`

**Checkpoint**: Coverage report provides clear v0 readiness assessment - US4 complete

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Validate outputs and ensure quality

- [ ] T047 Validate `outputs/kata-coverage-matrix.json` against `contracts/coverage-matrix.schema.json`
- [ ] T048 [P] Verify SC-001: 100% of katas classified (totalKatas == mappedKatas + orphanKatas)
- [ ] T049 [P] Verify SC-002: 100% of slots assessed (totalSlots == filledSlots + gapSlots)
- [ ] T050 [P] Cross-check orphan-katas.md entries match orphanKatas count in JSON
- [ ] T051 [P] Cross-check migration-roadmap.md tasks match migrationTasks in JSON
- [ ] T052 Review all outputs for deprecated terminology (must use canonical terms)
- [ ] T053 Run quickstart.md validation checklist against all outputs

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1: Setup
    ↓
Phase 2: Foundational (creates reference data)
    ↓
Phase 3: US1 - Target State (defines ontology slots)
    ↓
Phase 4: US2 - Kata Mapping (requires US1 for slot definitions)
    ↓
┌───────────────────┬───────────────────┐
↓                   ↓                   ↓
Phase 5: US3        Phase 6: US4        (can run in parallel)
Migration Roadmap   Coverage Report
    ↓                   ↓
    └───────────────────┘
            ↓
    Phase 7: Polish
```

### User Story Dependencies

- **US1 (P1)**: Can start after Foundational - No dependencies on other stories
- **US2 (P1)**: Depends on US1 (needs slot definitions to map against)
- **US3 (P2)**: Depends on US2 (needs mapping results for roadmap)
- **US4 (P3)**: Depends on US2 (needs mapping results for statistics)
- **US3 and US4 can run in parallel** after US2 completes

### Within User Story 2

All kata analysis tasks (T013-T032) are marked [P] and can run in parallel since they analyze different files and write to different sections.

### Parallel Opportunities

**Phase 2** - All [P] tasks can run in parallel:
```
T005: Deprecated terminology mapping
T006: Project markers list
T007: Jidoka Inline checklist
```

**Phase 4 (US2)** - All kata analysis tasks can run in parallel:
```
T013-T032: Each kata analyzed independently
```

**After US2 completes** - US3 and US4 can run in parallel:
```
Phase 5 (US3): Migration roadmap
Phase 6 (US4): Coverage report
```

---

## Implementation Strategy

### MVP First (US1 + US2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational reference data
3. Complete Phase 3: US1 - Define target state
4. Complete Phase 4: US2 - Map all katas
5. **STOP and VALIDATE**: Coverage matrix shows all mappings
6. Deliver kata-coverage-matrix.md + orphan-katas.md + JSON

### Full Delivery

1. Complete MVP (US1 + US2)
2. Add US3: Migration roadmap
3. Add US4: Coverage report with statistics
4. Polish: Validate all outputs
5. Deliver complete audit package

### Parallel Execution (if team capacity)

With multiple analysts:
- Analyst A: L0 + L1 katas (T013-T024)
- Analyst B: L2 + L3 katas (T025-T032)
- Then converge for consolidation (T033-T035)

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit outputs to Git after each phase completion
- Stop at any checkpoint to validate story independently
- All outputs are Markdown + JSON (no production code)

---

## Summary

| Phase | Tasks | Parallel | Description |
|-------|-------|----------|-------------|
| Setup | 3 | 2 | Validate inputs, create directories |
| Foundational | 4 | 3 | Create reference data |
| US1 (P1) | 5 | 0 | Define target state |
| US2 (P1) | 23 | 20 | Map all katas |
| US3 (P2) | 6 | 0 | Migration roadmap |
| US4 (P3) | 5 | 0 | Coverage report |
| Polish | 7 | 4 | Validate outputs |
| **Total** | **53** | **29** | |

**MVP Scope**: Phases 1-4 (35 tasks) deliver US1 + US2 with complete kata coverage matrix
