# Tasks: Comando raise.5.backlog

**Input**: Design documents from `/specs/009-backlog-command/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, quickstart.md

**Tests**: No automated tests for this feature (Markdown command orchestration - manual validation only)

**Organization**: Tasks organized by user story to enable independent implementation of command sections

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare .raise-kit structure and copy required dependencies

- [X] T001 Create directory `.raise-kit/templates/raise/backlog/` if not exists
- [X] T002 [P] Copy template from `src/templates/backlog/project_backlog.md` to `.raise-kit/templates/raise/backlog/project_backlog.md`
- [X] T003 [P] Create directory `.raise-kit/gates/raise/` if not exists
- [X] T004 [P] Copy gate from `src/gates/gate-backlog.md` to `.raise-kit/gates/raise/gate-backlog.md`
- [X] T005 Verify kata exists at `src/katas-v2.1/flujo/05-backlog-creation.md` (read-only reference, no copy needed)

---

## Phase 2: Foundational (Command File Structure)

**Purpose**: Create base command file with frontmatter and standard sections

**⚠️ CRITICAL**: This phase must be complete before any user story sections can be written

- [X] T006 Create empty command file at `.raise-kit/commands/02-projects/raise.5.backlog.md`
- [X] T007 Write YAML frontmatter with description and handoff to raise.6.estimation in `.raise-kit/commands/02-projects/raise.5.backlog.md`
- [X] T008 Write "User Input" section with $ARGUMENTS placeholder in `.raise-kit/commands/02-projects/raise.5.backlog.md`
- [X] T009 Write "Outline" goal statement in `.raise-kit/commands/02-projects/raise.5.backlog.md`

**Checkpoint**: Command file structure ready - user story steps can now be written

---

## Phase 3: User Story 1 - Generate Backlog from Tech Design (Priority: P1) 🎯 MVP

**Goal**: Command can load Tech Design, identify Epics/Features/User Stories, and generate structured backlog document

**Independent Test**: Execute `/raise.5.backlog` with a Tech Design and verify `project_backlog.md` is created with Epics, Features, and User Stories following template structure

### Implementation for User Story 1

**Step 1: Initialize Environment**

- [X] T010 [US1] Write Step 1 "Initialize Environment" in `.raise-kit/commands/02-projects/raise.5.backlog.md` with actions: run check-prerequisites.sh, load template, prepare output path
- [X] T011 [US1] Add Step 1 verification: "Template loaded, paths confirmed" in `.raise-kit/commands/02-projects/raise.5.backlog.md`
- [X] T012 [US1] Add Step 1 Jidoka block: "Template not found → Check .raise-kit setup" in `.raise-kit/commands/02-projects/raise.5.backlog.md`

**Step 2: Cargar Tech Design y Contexto**

- [X] T013 [US1] Write Step 2 "Cargar Tech Design y Contexto" in `.raise-kit/commands/02-projects/raise.5.backlog.md` with actions: load tech_design.md, load PRD, load vision, identify components
- [X] T014 [US1] Add Step 2 verification: "Tech Design exists and contains components/architecture sections" in `.raise-kit/commands/02-projects/raise.5.backlog.md`
- [X] T015 [US1] Add Step 2 Jidoka block: "Tech Design missing → Execute /raise.4.tech-design first" in `.raise-kit/commands/02-projects/raise.5.backlog.md`

**Step 3: Instanciar Template Backlog**

- [X] T016 [US1] Write Step 3 "Instanciar Template Backlog" in `.raise-kit/commands/02-projects/raise.5.backlog.md` with actions: copy template, fill frontmatter, add related_docs, set status Draft
- [X] T017 [US1] Add Step 3 verification: "File exists with complete metadata" in `.raise-kit/commands/02-projects/raise.5.backlog.md`
- [X] T018 [US1] Add Step 3 Jidoka block: "Write permission error → Check file system permissions" in `.raise-kit/commands/02-projects/raise.5.backlog.md`

**Step 4: Identificar Epics**

- [X] T019 [US1] Write Step 4 "Identificar Epics" in `.raise-kit/commands/02-projects/raise.5.backlog.md` with actions: analyze components, group into 3-7 Epics, assign IDs
- [X] T020 [US1] Add Step 4 verification: "3-7 Epics identified, each with clear value proposition" in `.raise-kit/commands/02-projects/raise.5.backlog.md`
- [X] T021 [US1] Add Step 4 Jidoka block: "Too many Epics → Consolidate. Too few → Decompose" in `.raise-kit/commands/02-projects/raise.5.backlog.md`

**Step 5: Descomponer Epics en Features**

- [X] T022 [US1] Write Step 5 "Descomponer Epics en Features" in `.raise-kit/commands/02-projects/raise.5.backlog.md` with actions: identify Features per Epic, ensure independent value, size 1-4 weeks, assign IDs
- [X] T023 [US1] Add Step 5 verification: "Each Epic has 2-5 Features with name, description, criteria" in `.raise-kit/commands/02-projects/raise.5.backlog.md`
- [X] T024 [US1] Add Step 5 Jidoka block: "Features too large → Vertical slicing. Too small → Combine" in `.raise-kit/commands/02-projects/raise.5.backlog.md`

**Step 7: Descomponer Features en User Stories**

- [X] T025 [US1] Write Step 7 "Descomponer Features en User Stories" in `.raise-kit/commands/02-projects/raise.5.backlog.md` with actions: create 3-8 US per Feature, format "Como/Quiero/Para", apply INVEST, assign IDs
- [X] T026 [US1] Add Step 7 verification: "Each Feature has 3-8 US, all follow standard format, fit in 1 sprint" in `.raise-kit/commands/02-projects/raise.5.backlog.md`
- [X] T027 [US1] Add Step 7 Jidoka block: "Stories too large → INVEST splitting. Lack benefit → Revisit para clause" in `.raise-kit/commands/02-projects/raise.5.backlog.md`

**Step 8: Escribir Criterios de Aceptación BDD**

- [X] T028 [US1] Write Step 8 "Escribir Criterios de Aceptación BDD" in `.raise-kit/commands/02-projects/raise.5.backlog.md` with actions: write 2-3 BDD scenarios per US, format Dado/Cuando/Entonces, cover happy path + edge cases
- [X] T029 [US1] Add Step 8 verification: "Each US has ≥2 scenarios in BDD format, scenarios are specific" in `.raise-kit/commands/02-projects/raise.5.backlog.md`
- [X] T030 [US1] Add Step 8 Jidoka block: "Vague criteria → Ask how would I write automated test" in `.raise-kit/commands/02-projects/raise.5.backlog.md`

**Step 9: Añadir Detalles Técnicos**

- [X] T031 [US1] Write Step 9 "Añadir Detalles Técnicos" in `.raise-kit/commands/02-projects/raise.5.backlog.md` with actions: add Tech Design references per US (components, endpoints, data model), document dependencies
- [X] T032 [US1] Add Step 9 verification: "Each US has Detalles Técnicos section linking to Tech Design components" in `.raise-kit/commands/02-projects/raise.5.backlog.md`
- [X] T033 [US1] Add Step 9 Jidoka block: "US not mappable → Review if in scope, may need Tech Design update" in `.raise-kit/commands/02-projects/raise.5.backlog.md`

**Checkpoint**: At this point, User Story 1 section (backlog generation) should be complete and command can generate basic backlog

---

## Phase 4: User Story 2 - Priorización y Estimación del Backlog (Priority: P2)

**Goal**: Command guides user through Feature prioritization and US estimation with Story Points

**Independent Test**: Execute command and verify backlog includes prioritized Features (Alta/Media/Baja), estimated US (Story Points), and identified MVP (≤50%)

### Implementation for User Story 2

**Step 6: Priorizar Features**

- [X] T034 [US2] Write Step 6 "Priorizar Features" in `.raise-kit/commands/02-projects/raise.5.backlog.md` with actions: apply prioritization matrix, consider dependencies, mark MVP, document justification
- [X] T035 [US2] Add Step 6 verification: "All Features have priority with justification, MVP clearly marked" in `.raise-kit/commands/02-projects/raise.5.backlog.md`
- [X] T036 [US2] Add Step 6 Jidoka block: "Unclear priorities → Session with PO. Use default: Core=Alta, Nice-to-have=Baja" in `.raise-kit/commands/02-projects/raise.5.backlog.md`

**Step 10: Estimar User Stories**

- [X] T037 [US2] Write Step 10 "Estimar User Stories" in `.raise-kit/commands/02-projects/raise.5.backlog.md` with actions: assign Story Points (Fibonacci), consider complexity/uncertainty/dependencies, propose defaults, signal team validation needed
- [X] T038 [US2] Add Step 10 verification: "All US have estimations, no US > 8 points" in `.raise-kit/commands/02-projects/raise.5.backlog.md`
- [X] T039 [US2] Add Step 10 Jidoka block: "US > 8 points → Subdivide. Disparate estimates → Document assumptions" in `.raise-kit/commands/02-projects/raise.5.backlog.md`

**Step 11: Completar Backlog y Calcular Totales**

- [X] T040 [US2] Write Step 11 "Completar Backlog y Calcular Totales" in `.raise-kit/commands/02-projects/raise.5.backlog.md` with actions: order backlog, calculate totals per Epic, generate distribution by complexity, identify MVP slice ≤50%, complete Resumen section
- [X] T041 [US2] Add Step 11 verification: "Backlog ordered, MVP identified and ≤50% of total, summary section complete" in `.raise-kit/commands/02-projects/raise.5.backlog.md`
- [X] T042 [US2] Add Step 11 Jidoka block: "MVP > 50% → Apply 'What can I defer and still deliver value' iteratively" in `.raise-kit/commands/02-projects/raise.5.backlog.md`

**Checkpoint**: User Stories 1 AND 2 sections complete - command can now generate fully prioritized and estimated backlog

---

## Phase 5: User Story 3 - Validación y Handoff (Priority: P3)

**Goal**: Command executes gate validation and offers handoff to next command in estimation flow

**Independent Test**: Execute command and verify gate runs, shows validation results (pass/fail with details), and displays handoff to `/raise.6.estimation`

### Implementation for User Story 3

**Step 12: Finalize & Validate**

- [X] T043 [US3] Write Step 12 "Finalize & Validate" in `.raise-kit/commands/02-projects/raise.5.backlog.md` with actions: confirm file existence, execute gate, show validation results
- [X] T044 [US3] Add Step 12 gate execution logic in `.raise-kit/commands/02-projects/raise.5.backlog.md`: run `.specify/gates/raise/gate-backlog.md`, capture output
- [X] T045 [US3] Add Step 12 failure handling in `.raise-kit/commands/02-projects/raise.5.backlog.md`: if failed, list issues and suggest corrections
- [X] T046 [US3] Add Step 12 success handling in `.raise-kit/commands/02-projects/raise.5.backlog.md`: if passed, show summary (# Epics, # Features, # US, Total SP, MVP SP)
- [X] T047 [US3] Add Step 12 agent context update in `.raise-kit/commands/02-projects/raise.5.backlog.md`: run `.specify/scripts/bash/update-agent-context.sh`
- [X] T048 [US3] Add Step 12 handoff display in `.raise-kit/commands/02-projects/raise.5.backlog.md`: show "→ Siguiente paso: /raise.6.estimation"
- [X] T049 [US3] Add Step 12 verification: "Gate executed, results shown, handoff offered" in `.raise-kit/commands/02-projects/raise.5.backlog.md`
- [X] T050 [US3] Add Step 12 Jidoka block: "Gate failures → Iterate on failed criteria before proceeding" in `.raise-kit/commands/02-projects/raise.5.backlog.md`

**Checkpoint**: All user stories complete - command is fully functional with validation and handoff

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Complete standard command sections and validate structure

- [X] T051 [P] Write "Notes" section (optional) in `.raise-kit/commands/02-projects/raise.5.backlog.md` with guidance for different scenarios if needed
- [X] T052 [P] Write "High-Signaling Guidelines" section in `.raise-kit/commands/02-projects/raise.5.backlog.md` with: Output (project_backlog.md), Focus (backlog generation), Language (English/Spanish), Jidoka (when to stop)
- [X] T053 [P] Write "AI Guidance" section in `.raise-kit/commands/02-projects/raise.5.backlog.md` with: Role (orquestador de backlog), Proactive (propose defaults), Follow Katas (flujo-05), Traceability (link decisions to Tech Design), Gates (run gate-backlog)
- [X] T054 Validate command structure against reference command `.raise-kit/commands/02-projects/raise.4.tech-design.md` for consistency
- [X] T055 Validate command structure against pattern documentation `.agent/rules/110-raise-kit-command-creation.md` checklist
- [X] T056 [P] Manual test: Execute command with sample Tech Design from specs/001-tech-design-command and verify backlog generation
- [X] T057 [P] Manual test: Verify all gate criteria pass for generated backlog
- [X] T058 [P] Manual test: Verify handoff to raise.6.estimation is displayed correctly
- [X] T059 Final review: Check all references use `.specify/` not `.raise-kit/` (portability requirement)
- [X] T060 Final review: Check content is in Spanish and instructions are in English (bilingual requirement)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user story sections
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - US1 (Phase 3): Can start after Foundational - No dependencies on other stories
  - US2 (Phase 4): Depends on US1 completion (builds on backlog structure from US1)
  - US3 (Phase 5): Depends on US1+US2 completion (validates full backlog with estimates)
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Independent - can complete alone (generates basic backlog without priorities/estimates)
- **User Story 2 (P2)**: Depends on US1 (adds prioritization and estimation to existing backlog structure)
- **User Story 3 (P3)**: Depends on US1+US2 (validates complete backlog)

**NOTE**: Unlike typical features, these user stories are SEQUENTIAL - each builds on the previous. The command is a single file with 12 sequential steps.

### Within Each User Story

- Steps must be written in order (Step 1 → Step 2 → ... → Step 12)
- Each step includes: Title → Actions → Verification → Jidoka block
- Tasks within a step can be parallel [P] if editing different parts of the same file

### Parallel Opportunities

- Phase 1 Setup: T002 and T003+T004 can run in parallel (different directories)
- Phase 2 Foundational: T007-T009 can run in parallel (different sections of same file, no conflicts)
- Phase 6 Polish: T051, T052, T053 can run in parallel (different sections of same file)
- Phase 6 Testing: T056, T057, T058 can run in parallel (independent validation checks)

---

## Parallel Example: Phase 1 Setup

```bash
# Launch setup tasks together:
Task: "Copy template from src/templates/backlog/project_backlog.md to .raise-kit/templates/raise/backlog/project_backlog.md"
Task: "Create directory .raise-kit/gates/raise/ and copy gate from src/gates/gate-backlog.md"
```

## Parallel Example: Phase 6 Polish

```bash
# Launch polish tasks together:
Task: "Write High-Signaling Guidelines section in .raise-kit/commands/02-projects/raise.5.backlog.md"
Task: "Write AI Guidance section in .raise-kit/commands/02-projects/raise.5.backlog.md"
Task: "Write Notes section in .raise-kit/commands/02-projects/raise.5.backlog.md"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (copy template + gate)
2. Complete Phase 2: Foundational (create command file structure)
3. Complete Phase 3: User Story 1 (Steps 1-3, 4-5, 7-9)
4. **STOP and VALIDATE**: Execute command, verify basic backlog generation works
5. **Result**: Command can generate Epics, Features, and User Stories (without priorities/estimates)

**MVP Limitation**: Backlog has no priorities, no Story Point estimates, no MVP identification, no gate validation

### Incremental Delivery

1. MVP: US1 only → Can generate basic backlog structure
2. Add US2 → Can generate prioritized and estimated backlog with MVP
3. Add US3 → Can validate backlog and offer handoff
4. Each increment adds value without breaking previous functionality

### Sequential Strategy (Single Developer)

This is the recommended approach since the command is a single file:

1. Complete Setup + Foundational → File ready
2. Write US1 steps (T010-T033) → Test basic generation
3. Write US2 steps (T034-T042) → Test with priorities/estimates
4. Write US3 steps (T043-T050) → Test with validation
5. Polish (T051-T060) → Final validation
6. Each phase builds on previous, testing incrementally

### Parallel Team Strategy

Limited parallelization (single file, sequential steps), but possible:

1. Team completes Setup + Foundational together
2. Once Foundational done:
   - Developer A: Write Steps 1-5 (US1 part 1)
   - Developer B: Write Steps 7-9 (US1 part 2)
   - **Merge**: US1 complete
3. Developer A: Write Steps 6, 10-11 (US2)
4. Developer B: Write Step 12 (US3)
5. Team: Polish together (parallel sections)

---

## Notes

- [P] tasks = different files/sections, no write conflicts
- [Story] label maps task to specific user story for traceability
- This is a Markdown orchestration file, not traditional code
- No automated tests - validation is manual execution against gate criteria
- Each step must have: actions, verification, Jidoka block
- All file references must use `.specify/` for portability
- Content in Spanish (orchestrated output), instructions in English (for AI)
- Command file is ~300-400 lines total
- Commit after completing each step or logical group
- Reference commands for structure: raise.1.discovery, raise.2.vision, raise.4.tech-design

---

## Task Summary

**Total Tasks**: 60
- Phase 1 (Setup): 5 tasks
- Phase 2 (Foundational): 4 tasks
- Phase 3 (US1 - MVP): 24 tasks
- Phase 4 (US2): 9 tasks
- Phase 5 (US3): 8 tasks
- Phase 6 (Polish): 10 tasks

**Parallel Opportunities**: 11 tasks marked [P]

**User Story Distribution**:
- US1 (Generate Backlog): 24 tasks (Steps 1-5, 7-9)
- US2 (Prioritization & Estimation): 9 tasks (Steps 6, 10-11)
- US3 (Validation & Handoff): 8 tasks (Step 12)

**MVP Scope**: Phase 1 + Phase 2 + Phase 3 (US1 only) = 33 tasks for basic backlog generation

**Independent Test Criteria**:
- **US1**: Execute `/raise.5.backlog` → Verify `project_backlog.md` created with Epics/Features/US structure
- **US2**: Execute command → Verify Features have priorities, US have Story Points, MVP identified ≤50%
- **US3**: Execute command → Verify gate runs, shows pass/fail, displays handoff

**Critical Path**: Setup → Foundational → US1 → US2 → US3 → Polish (fully sequential for command file creation)
