# Tasks: Katas Ontology Normalization

**Input**: Design documents from `/specs/006-katas-normalization/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, quickstart.md

**Organization**: Tasks are grouped by kata batch to enable incremental processing with Orquestador validation after each kata. User story aspects (US1-US4) are labeled within each kata's tasks.

**Note**: This is a documentation-centric feature. The "implementation" is editing Markdown files and generating reports—no production code is created.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story aspect this task addresses:
  - [US1] = Jidoka Inline Structure
  - [US2] = Deprecated Terminology
  - [US3] = Semantic Coherence
  - [US4] = Incremental Validation

## Path Conventions

- **Katas**: `src/katas/{principios,flujo,patron}/*.md`
- **Reports**: `specs/006-katas-normalization/outputs/report-*.md`
- **References**: `docs/framework/v2.1/model/20-glossary-v2.1.md`

---

## Phase 1: Setup

**Purpose**: Verify prerequisites and prepare working environment

- [x] T001 Verify branch is `006-katas-normalization` and working tree is clean
- [x] T002 [P] Verify all 15 kata files exist in `src/katas/{principios,flujo,patron}/`
- [x] T003 [P] Verify reference documents accessible: `20-glossary-v2.1.md`, `migration-roadmap.md`
- [x] T004 Create outputs directory structure at `specs/006-katas-normalization/outputs/`

---

## Phase 2: Foundational (Reference Materials)

**Purpose**: Prepare reference materials and templates for normalization workflow

**⚠️ CRITICAL**: Complete this phase before processing any katas

- [x] T005 Review Jidoka Inline format in `research.md` §1 and create mental model
- [x] T006 [P] Review terminology mapping in `research.md` §2 and `plan.md` §Terminology Mapping Reference
- [x] T007 [P] Review semantic level guiding questions in `research.md` §3
- [x] T008 Create normalization report template based on `data-model.md` §NormalizationReport

**Checkpoint**: Reference materials internalized - kata processing can begin

---

## Phase 3: Principios Level Katas (2 katas)

**Goal**: Normalize the 2 foundational katas that define kata philosophy and execution

**Independent Test**: Each kata in `src/katas/principios/` has Jidoka Inline in every step and zero deprecated terms

### Kata 1: 00-raise-katas-documentation.md

- [x] T009 [US3] Read and analyze `src/katas/principios/00-raise-katas-documentation.md` for semantic coherence with "¿Por qué? ¿Cuándo?"
- [x] T010 [US1] Identify all steps in kata lacking `**Verificación:**` or `> **Si no puedes continuar:**`
- [x] T011 [US2] Scan kata for deprecated terms (DoD, Developer, Rule, L0-L3)
- [x] T012 [US1] Add Jidoka Inline structure to each step in `src/katas/principios/00-raise-katas-documentation.md`
- [x] T013 [US2] Replace deprecated terms with canonical equivalents in `src/katas/principios/00-raise-katas-documentation.md`
- [x] T014 Generate normalization report at `specs/006-katas-normalization/outputs/report-principios-00.md`
- [x] T015 [US4] Present normalized kata to Orquestador for validation (approve/reject/skip)

### Kata 2: 01-raise-kata-execution-protocol.md

- [x] T016 [US3] Read and analyze `src/katas/principios/01-raise-kata-execution-protocol.md` for semantic coherence
- [x] T017 [US1] Identify steps lacking Jidoka Inline structure
- [x] T018 [US2] Scan for deprecated terms
- [x] T019 [US1] Add Jidoka Inline structure to each step in `src/katas/principios/01-raise-kata-execution-protocol.md`
- [x] T020 [US2] Replace deprecated terms in `src/katas/principios/01-raise-kata-execution-protocol.md`
- [x] T021 Generate normalization report at `specs/006-katas-normalization/outputs/report-principios-01.md`
- [x] T022 [US4] Present to Orquestador for validation

**Checkpoint**: Principios level complete - 2/15 katas normalized

---

## Phase 4: Flujo Level Katas - Jidoka Focus (5 katas)

**Goal**: Normalize Flujo katas that primarily need Jidoka Inline structure

**Independent Test**: Each processed kata has complete Jidoka Inline in every step

### Kata 3: 04-generacion-plan-implementacion-hu.md

- [x] T023 [US3] Analyze `src/katas/flujo/04-generacion-plan-implementacion-hu.md` for coherence with "¿Cómo fluye?"
- [x] T024 [US1] [US2] Normalize kata: add Jidoka Inline + replace deprecated terms in `src/katas/flujo/04-generacion-plan-implementacion-hu.md`
- [x] T025 Generate report at `specs/006-katas-normalization/outputs/report-flujo-04.md`
- [x] T026 [US4] Present to Orquestador for validation

### Kata 4: 09-ecosystem-discovery-feature-design.md

- [x] T027 [US3] Analyze `src/katas/flujo/09-ecosystem-discovery-feature-design.md` for semantic coherence
- [x] T028 [US1] [US2] Normalize kata in `src/katas/flujo/09-ecosystem-discovery-feature-design.md`
- [x] T029 Generate report at `specs/006-katas-normalization/outputs/report-flujo-09.md`
- [x] T030 [US4] Present to Orquestador for validation

### Kata 5: 10-alineamiento-convenciones-repositorio.md

- [x] T031 [US3] Analyze `src/katas/flujo/10-alineamiento-convenciones-repositorio.md` for semantic coherence
- [x] T032 [US1] [US2] Normalize kata in `src/katas/flujo/10-alineamiento-convenciones-repositorio.md`
- [x] T033 Generate report at `specs/006-katas-normalization/outputs/report-flujo-10.md`
- [x] T034 [US4] Present to Orquestador for validation

### Kata 6: 12-analisis-granularidad-hus-multi-repo.md

- [x] T035 [US3] Analyze `src/katas/flujo/12-analisis-granularidad-hus-multi-repo.md` for semantic coherence
- [x] T036 [US1] [US2] Normalize kata in `src/katas/flujo/12-analisis-granularidad-hus-multi-repo.md`
- [x] T037 Generate report at `specs/006-katas-normalization/outputs/report-flujo-12.md`
- [x] T038 [US4] Present to Orquestador for validation

### Kata 7: 06-implementacion-hu-asistida-por-ia.md

- [x] T039 [US3] Analyze `src/katas/flujo/06-implementacion-hu-asistida-por-ia.md` for semantic coherence
- [x] T040 [US1] [US2] Normalize kata (Jidoka + terminology including "Developer"→"Orquestador") in `src/katas/flujo/06-implementacion-hu-asistida-por-ia.md`
- [x] T041 Generate report at `specs/006-katas-normalization/outputs/report-flujo-06.md`
- [x] T042 [US4] Present to Orquestador for validation

**Checkpoint**: Flujo Jidoka batch complete - 7/15 katas normalized

---

## Phase 5: Patrón Level Katas (5 katas)

**Goal**: Normalize all Patrón katas for structure and terminology

**Independent Test**: Each kata in `src/katas/patron/` answers "¿Qué forma?" and has complete Jidoka Inline

### Kata 8: 02-analisis-agnostico-codigo-fuente.md

- [ ] T043 [US3] Analyze `src/katas/patron/02-analisis-agnostico-codigo-fuente.md` for coherence with "¿Qué forma?"
- [ ] T044 [US1] [US2] Normalize kata in `src/katas/patron/02-analisis-agnostico-codigo-fuente.md`
- [ ] T045 Generate report at `specs/006-katas-normalization/outputs/report-patron-02.md`
- [ ] T046 [US4] Present to Orquestador for validation

### Kata 9: 03-ecosystem-discovery-agnostico.md

- [ ] T047 [US3] Analyze `src/katas/patron/03-ecosystem-discovery-agnostico.md` for semantic coherence
- [ ] T048 [US1] [US2] Normalize kata in `src/katas/patron/03-ecosystem-discovery-agnostico.md`
- [ ] T049 Generate report at `specs/006-katas-normalization/outputs/report-patron-03.md`
- [ ] T050 [US4] Present to Orquestador for validation

### Kata 10: 04-analisis-intercomunicacion-ecosistema.md

- [ ] T051 [US3] Analyze `src/katas/patron/04-analisis-intercomunicacion-ecosistema.md` for semantic coherence
- [ ] T052 [US1] [US2] Normalize kata in `src/katas/patron/04-analisis-intercomunicacion-ecosistema.md`
- [ ] T053 Generate report at `specs/006-katas-normalization/outputs/report-patron-04.md`
- [ ] T054 [US4] Present to Orquestador for validation

### Kata 11: 07-validacion-tecnica-dependencias.md

- [ ] T055 [US3] Analyze `src/katas/patron/07-validacion-tecnica-dependencias.md` for semantic coherence
- [ ] T056 [US1] [US2] Normalize kata in `src/katas/patron/07-validacion-tecnica-dependencias.md`
- [ ] T057 Generate report at `specs/006-katas-normalization/outputs/report-patron-07.md`
- [ ] T058 [US4] Present to Orquestador for validation

### Kata 12: 01-tech-design-stack-aware.md

- [ ] T059 [US3] Analyze `src/katas/patron/01-tech-design-stack-aware.md` for semantic coherence
- [ ] T060 [US1] [US2] Normalize kata in `src/katas/patron/01-tech-design-stack-aware.md`
- [ ] T061 Generate report at `specs/006-katas-normalization/outputs/report-patron-01.md`
- [ ] T062 [US4] Present to Orquestador for validation

**Checkpoint**: Patrón level complete - 12/15 katas normalized

---

## Phase 6: Flujo Level Katas - Terminology Focus (3 katas)

**Goal**: Normalize Flujo katas that have heavy DoD terminology requiring replacement

**Independent Test**: Zero occurrences of "DoD" in these katas; replaced with "Validation Gate"

### Kata 13: 15-protocolo-verificacion-validation-gate.md

- [ ] T063 [US3] Analyze `src/katas/flujo/15-protocolo-verificacion-validation-gate.md` for semantic coherence
- [ ] T064 [US2] Replace all "DoD" occurrences (~15) with "Validation Gate" in `src/katas/flujo/15-protocolo-verificacion-validation-gate.md`
- [ ] T065 [US2] Replace "Developer" (~5 occurrences) with "Orquestador" in same file
- [ ] T066 [US1] Add Jidoka Inline structure to any steps lacking it
- [ ] T067 Generate report at `specs/006-katas-normalization/outputs/report-flujo-15.md`
- [ ] T068 [US4] Present to Orquestador for validation

### Kata 14: 16-validation-gate-historias-usuario.md

- [ ] T069 [US3] Analyze `src/katas/flujo/16-validation-gate-historias-usuario.md` for semantic coherence
- [ ] T070 [US2] Replace all "DoD" occurrences (~30) with "Validation Gate" in `src/katas/flujo/16-validation-gate-historias-usuario.md`
- [ ] T071 [US1] Add Jidoka Inline structure to steps lacking it
- [ ] T072 Generate report at `specs/006-katas-normalization/outputs/report-flujo-16.md`
- [ ] T073 [US4] Present to Orquestador for validation

### Kata 15: 17-validation-gate-epicas.md

- [ ] T074 [US3] Analyze `src/katas/flujo/17-validation-gate-epicas.md` for semantic coherence
- [ ] T075 [US2] Replace all "DoD" occurrences (~20) with "Validation Gate" in `src/katas/flujo/17-validation-gate-epicas.md`
- [ ] T076 [US1] Add Jidoka Inline structure to steps lacking it
- [ ] T077 Generate report at `specs/006-katas-normalization/outputs/report-flujo-17.md`
- [ ] T078 [US4] Present to Orquestador for validation

**Checkpoint**: All 15 katas normalized

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and cleanup

- [ ] T079 Verify SC-001: Run `grep -r "Verificación:" src/katas/{principios,flujo,patron}/` confirms all steps have Jidoka
- [ ] T080 [P] Verify SC-002: Run `grep -rE "DoD|Developer|Rule|L[0-3]" src/katas/{principios,flujo,patron}/` returns only preserved contexts
- [ ] T081 [P] Consolidate all normalization reports into summary at `specs/006-katas-normalization/outputs/summary.md`
- [ ] T082 Update `plan.md` §Processing Priority to mark all items as complete
- [ ] T083 Run `quickstart.md` validation checklist against normalized katas
- [ ] T084 Commit all changes with comprehensive commit message

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1: Setup
    ↓
Phase 2: Foundational (reference materials)
    ↓
Phase 3: Principios katas (2)
    ↓
Phase 4: Flujo katas - Jidoka (5)
    ↓
Phase 5: Patrón katas (5)
    ↓
Phase 6: Flujo katas - Terminology (3)
    ↓
Phase 7: Polish
```

### User Story Dependencies

Within each kata's task sequence:
```
[US3] Coherence check (GATE)
    ├─ If misaligned → STOP, flag for reclassification
    └─ If aligned → continue
        ↓
[US1] + [US2] Normalization (parallel aspects, applied together)
        ↓
Report generation
        ↓
[US4] Orquestador validation (GATE)
    ├─ Approved → proceed to next kata
    ├─ Changes requested → revise and re-validate
    └─ Skip → proceed without changes
```

### Parallel Opportunities

**Phase 2** - Reference review tasks can run in parallel:
```
T006: Review terminology mapping
T007: Review semantic level questions
```

**Within each kata** - Analysis tasks are sequential (read→check→normalize→report→validate)

**Across phases** - Katas MUST be processed sequentially per US4 (incremental validation requirement)

---

## Implementation Strategy

### MVP First (Phase 1-3 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: Principios katas (2 katas)
4. **STOP and VALIDATE**: Review first 2 normalized katas
5. Confirm approach is correct before proceeding

### Incremental Delivery

1. Complete each kata → Orquestador validates → Commit
2. Each kata is an independently deliverable increment
3. Can pause at any checkpoint and resume later
4. Progress tracked in normalization reports

### Batch Strategy (if time-constrained)

Process katas in level batches:
1. All Principios (2) → validate batch
2. All Patron (5) → validate batch
3. All Flujo (8) → validate batch

**Note**: Even in batch mode, generate individual reports for traceability.

---

## Summary

| Phase | Tasks | Katas | Parallel | Description |
|-------|-------|-------|----------|-------------|
| Setup | 4 | 0 | 2 | Verify prerequisites |
| Foundational | 4 | 0 | 2 | Prepare reference materials |
| Principios | 14 | 2 | 0 | Foundation katas |
| Flujo-Jidoka | 20 | 5 | 0 | Structure-focused katas |
| Patrón | 20 | 5 | 0 | Pattern katas |
| Flujo-Term | 16 | 3 | 0 | Terminology-heavy katas |
| Polish | 6 | 0 | 2 | Validation and cleanup |
| **Total** | **84** | **15** | **6** | |

**MVP Scope**: Phases 1-3 (22 tasks) delivers 2 normalized Principios katas as proof of concept

---

## Notes

- Each kata MUST complete [US4] validation before proceeding to next
- [US3] coherence check is a GATE - if failed, kata is flagged and skipped
- Tasks are NOT parallelizable across katas (incremental processing requirement)
- Reports serve as audit trail and learning capture
- Commit after each kata's validation approval
