---
description: "Task list for raise.6.estimation command implementation"
---

# Tasks: Comando raise.6.estimation

**Input**: Design documents from `/specs/010-estimation-command/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅, quickstart.md ✅

**Tests**: Not applicable - this is a documentation transformation command (no code tests needed)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

This feature creates command files in `.raise-kit/` directory structure:
- **Commands**: `.raise-kit/commands/02-projects/`
- **Gates**: `.raise-kit/gates/raise/`
- **Templates**: Already exist in `src/templates/solution/`

---

## Phase 1: Setup (Command Infrastructure)

**Purpose**: Create gate validation file and prepare command structure

- [x] T001 Create gate validation file `.raise-kit/gates/raise/gate-estimation.md` based on `contracts/gate-estimation-criteria.md`
- [x] T002 [P] Verify template exists at `src/templates/solution/estimation_roadmap.md` (should already exist)
- [x] T003 [P] Create command file skeleton `.raise-kit/commands/02-projects/raise.6.estimation.md` with frontmatter YAML

**Checkpoint**: Gate file complete, command skeleton ready

---

## Phase 2: User Story 1 - Generar Roadmap desde Backlog (Priority: P1) 🎯 MVP

**Goal**: Generate complete Estimation Roadmap from Project Backlog with SP projections, team capacity, and iteration timeline

**Independent Test**: Execute `/raise.6.estimation` with a valid backlog → generates `specs/main/estimation_roadmap.md` with all 5 sections complete, gate passes

### Implementation for User Story 1

- [x] T004 [US1] Implement Step 1 (Initialize Environment) in command outline - load template, run prerequisites, prepare output path
- [x] T005 [US1] Implement Step 2 (Load Backlog and Extract SP) - parse backlog markdown, extract Epics/Features/US with SP estimates, calculate total_sp
- [x] T006 [US1] Implement Step 3 (Instantiate Template) - fill metadata YAML frontmatter with project info, create output file
- [x] T007 [US1] Implement Step 5 (Generate Estimation Table) - consolidate all backlog items into Section 2 table with ID, Elemento, SP, Notas, Referencia
- [x] T008 [US1] Implement Step 6 (Calculate Roadmap Projection) - calculate iterations (Total SP / Capacity), generate Section 4 table with iterations, dates, objectives, SP
- [x] T009 [US1] Implement Step 7 (Identify MVP Scope) - mark MVP iterations in roadmap table, calculate MVP SP and ratio
- [x] T010 [US1] Implement Step 9 (Add Disclaimers and Assumptions) - document projection nature, assumptions, disclaimers in roadmap
- [x] T011 [US1] Implement Step 10 (Generate Summary Metrics) - calculate and display total SP, iterations, MVP ratio, backlog coverage
- [x] T012 [US1] Implement Step 11 (Finalize & Validate) - execute gate-estimation.md, show results, offer handoff to raise.7.sow if pass

**Checkpoint**: At this point, User Story 1 should be fully functional - command generates complete roadmap with default team parameters and passes gate validation

---

## Phase 3: User Story 2 - Configurar Parámetros de Equipo (Priority: P2)

**Goal**: Allow users to specify custom team structure (roles, dedication, sprint duration) so roadmap reflects actual team capacity

**Independent Test**: Execute `/raise.6.estimation "2 engineers full-time, 1 QA 50%, sprints 1 week"` → roadmap uses custom capacity (20 SP/sprint), documents custom team structure

### Implementation for User Story 2

- [x] T013 [US2] Implement Step 4 (Configure Team Parameters) - parse $ARGUMENTS for custom team structure OR use defaults (16 SP/sprint, 2 weeks), validate capacity range (8-40 SP/sprint)
- [x] T014 [US2] Add Jidoka blocks for capacity validation - alert if capacity < 8 SP/sprint (too slow) or > 40 SP/sprint (unrealistic)
- [x] T015 [US2] Document team parameters in Section 3 of roadmap - sprint duration, team structure with roles/dedication, capacity calculation shown, velocity measurement note

**Checkpoint**: At this point, User Stories 1 AND 2 should both work - command supports both default and custom team parameters

---

## Phase 4: User Story 3 - Vincular con Modelo de Costos (Priority: P3)

**Goal**: Include cost model section in roadmap explaining SP → hours → cost relationship for SoW preparation

**Independent Test**: Verify generated roadmap has Section 5 "Vinculación con Modelo de Costos" with SP-to-effort explanation, impact of changes, and cost assumptions

### Implementation for User Story 3

- [x] T016 [US3] Implement Step 8 (Document Cost Model Linkage) - generate Section 5 with SP-to-hours conversion (1 SP ≈ 4-6 hours), impact statement, key cost assumptions

**Checkpoint**: All user stories complete - roadmap includes cost model section ready for SoW generation

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Finalize command quality and documentation

- [x] T017 [P] Add High-Signaling Guidelines section to command file - output files, focus, language (English instructions, Spanish content), Jidoka conditions
- [x] T018 [P] Add AI Guidance section to command file - role, be_proactive, follow_katas (L1-04 Step 6), traceability, gates, heutagogy
- [x] T019 Validate command structure against rule 110 checklist - verify all 6 mandatory sections present (frontmatter, user input, outline, high-signaling, AI guidance)
- [x] T020 [P] Update handoff configuration in frontmatter - set handoff to raise.7.sow with auto-send: true
- [ ] T021 Manual test: Execute command with sample backlog, verify gate execution, validate roadmap output quality
- [x] T022 [P] Update main README or command index with raise.6.estimation entry (if applicable)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **User Story 1 (Phase 2)**: Depends on Setup (T001 gate file, T003 command skeleton) - CORE MVP
- **User Story 2 (Phase 3)**: Depends on US1 Step 4 implementation (T013 extends T004-T012)
- **User Story 3 (Phase 4)**: Independent of US2 - only depends on US1 core structure
- **Polish (Phase 5)**: Depends on all user stories complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Setup (Phase 1) - No dependencies on other stories ✅ MVP
- **User Story 2 (P2)**: Extends US1 Step 4 (team parameters) - Must have US1 core complete
- **User Story 3 (P3)**: Independent story - Can start after US1 core, parallel with US2

### Within Each User Story

- **US1**: Steps 1-3 (setup) → Steps 5-7 (core generation) → Steps 9-11 (finalization)
- **US2**: Step 4 (parameters) integrates into US1 flow
- **US3**: Step 8 (cost model) integrates into US1 flow

### Parallel Opportunities

- **Setup Phase**: T002 and T003 can run in parallel (different files)
- **US1 Implementation**: Steps are sequential (each depends on previous data)
- **US2 and US3**: Can be implemented in parallel after US1 core (T004-T012) complete
- **Polish Phase**: T017, T018, T020, T022 can run in parallel (different sections/files)

---

## Parallel Example: User Story 1

```bash
# US1 tasks are mostly sequential due to data flow:
# T004 (Initialize) → T005 (Load Backlog) → T006 (Instantiate) → 
# T007 (Estimation Table) → T008 (Calculate Roadmap) → T009 (MVP) → 
# T010 (Disclaimers) → T011 (Summary) → T012 (Validate)

# However, after US1 core (T004-T012) is complete:
# US2 (T013-T015) and US3 (T016) can be worked in parallel
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: User Story 1 (T004-T012)
3. **STOP and VALIDATE**: Test command with sample backlog
   - Verify roadmap generated with all sections
   - Verify gate execution works
   - Verify handoff to raise.7.sow offered
4. Deploy/demo if ready (MVP = core roadmap generation with defaults)

### Incremental Delivery

1. Complete Setup → Gate and command skeleton ready
2. Add User Story 1 → Test independently → **MVP COMPLETE** ✅
3. Add User Story 2 → Test with custom parameters → Enhanced version
4. Add User Story 3 → Test cost model section → Full feature complete
5. Polish → Final quality checks → Production ready

### Sequential Implementation (Recommended)

Since this is a single command file with integrated steps:

1. Complete Setup (T001-T003)
2. Implement US1 core (T004-T012) - **CRITICAL PATH**
3. Add US2 parameters (T013-T015) - extends Step 4
4. Add US3 cost model (T016) - extends Step 8
5. Polish (T017-T022) - finalize quality

---

## Task Summary

- **Total Tasks**: 22
- **Setup Phase**: 3 tasks
- **User Story 1 (P1 - MVP)**: 9 tasks ⭐ CORE
- **User Story 2 (P2)**: 3 tasks
- **User Story 3 (P3)**: 1 task
- **Polish Phase**: 6 tasks

### Tasks per User Story

- **US1 (Generar Roadmap)**: T004-T012 (9 tasks) - 41% of implementation
- **US2 (Configurar Parámetros)**: T013-T015 (3 tasks) - 14% of implementation
- **US3 (Vincular Costos)**: T016 (1 task) - 5% of implementation

### Parallel Opportunities Identified

- Setup: 2 tasks can run in parallel (T002, T003)
- US2 + US3: Can be worked in parallel after US1 core
- Polish: 4 tasks can run in parallel (T017, T018, T020, T022)

### Independent Test Criteria

- **US1**: Execute command with valid backlog → roadmap generated with 5 sections, gate passes
- **US2**: Execute command with custom team args → roadmap uses custom capacity, documents team structure
- **US3**: Verify Section 5 exists with SP-to-cost explanation, impact statement, assumptions

### Suggested MVP Scope

**MVP = User Story 1 Only** (T001-T012)

This delivers core value:
- ✅ Generate complete estimation roadmap from backlog
- ✅ Use default team parameters (16 SP/sprint)
- ✅ Calculate iterations and MVP scope
- ✅ Validate via gate
- ✅ Offer handoff to raise.7.sow

User Stories 2 and 3 are enhancements that can be added incrementally.

---

## Notes

- This is a **documentation command** (not code) - tasks create markdown files with AI execution logic
- All paths use `.specify/` prefix for portability (critical for injection to target projects)
- Command follows rule 110 structure: frontmatter, user input, outline (11 steps), high-signaling, AI guidance
- Gate execution is mandatory (Step 11) - implements Jidoka principle
- Language: Instructions in English, generated content in Spanish
- Each user story adds independent value and can be tested separately
- Commit after completing each user story phase for incremental delivery
