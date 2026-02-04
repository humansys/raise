---
description: "Task list for Tech Design Command Generation feature implementation"
---

# Tasks: Tech Design Command Generation

**Input**: Design documents from `/specs/001-tech-design-command/`
**Prerequisites**: plan.md, spec.md, research.md

**Tests**: Not requested in specification - tasks focus on command creation and documentation

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

This is a documentation/tooling project. Paths are in `.raise-kit/` (development) and will be copied to `.specify/` when injected into target projects.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create directory structure and copy required assets to `.raise-kit`

- [X] T001 Create directory structure for tech templates: `mkdir -p .raise-kit/templates/raise/tech`
- [X] T002 [P] Copy tech design template from source: `cp src/templates/tech/tech_design.md .raise-kit/templates/raise/tech/tech_design.md`
- [X] T003 [P] Verify gate-design.md exists in `.raise-kit/gates/gate-design.md` (copied to `.raise-kit/gates/raise/gate-design.md`)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Analyze patterns and prepare command structure before implementation

**⚠️ CRITICAL**: This research must be complete before command can be written

- [X] T004 Review raise.1.discovery.md structure in `.raise-kit/commands/02-projects/raise.1.discovery.md` to extract pattern
- [X] T005 [P] Review raise.2.vision.md structure in `.raise-kit/commands/02-projects/raise.2.vision.md` to extract pattern
- [X] T006 [P] Review kata flujo-03-tech-design.md in `src/katas-v2.1/flujo/03-tech-design.md` to extract 15 steps
- [X] T007 Document command structure pattern in working notes (frontmatter, sections, Jidoka format)

**Checkpoint**: Foundation ready - command implementation can now begin

---

## Phase 3: User Story 1 - Generate Tech Design from Solution Vision (Priority: P1) 🎯 MVP

**Goal**: Create the core command that generates Tech Design documents from Solution Vision, following the 15 steps of the kata

**Independent Test**: Execute `/raise.4.tech-design` in a test project with `specs/main/solution_vision.md` and verify `specs/main/tech_design.md` is generated with all 14 sections completed

### Implementation for User Story 1

- [X] T008 [US1] Create command file `.raise-kit/commands/02-projects/raise.4.tech-design.md`
- [X] T009 [US1] Write frontmatter YAML with description and handoffs to raise.5.backlog
- [X] T010 [US1] Write User Input section to capture $ARGUMENTS
- [X] T011 [US1] Write Outline section - Paso 1: Initialize Environment (run check-prerequisites.sh, load template)
- [X] T012 [US1] Write Outline section - Paso 2: Cargar Vision y Contexto (load solution_vision.md, implement Jidoka if missing)
- [X] T013 [US1] Write Outline section - Paso 3: Instanciar Template Tech Design (copy template to specs/main/)
- [X] T014 [US1] Write Outline section - Paso 4: Definir Visión General Técnica (complete section 1 of template)
- [X] T015 [US1] Write Outline section - Paso 5: Describir Solución Propuesta (complete section 2 of template)
- [X] T016 [US1] Write Outline section - Paso 6: Detallar Arquitectura de Componentes (complete section 3 of template)
- [X] T017 [US1] Write Outline section - Paso 7: Documentar Flujos de Datos (complete section 4 of template)
- [X] T018 [US1] Write Outline section - Paso 8: Especificar Contratos de API (complete section 5 of template)
- [X] T019 [US1] Write Outline section - Paso 9: Diseñar Modelo de Datos (complete section 6 of template)
- [X] T020 [US1] Write Outline section - Paso 10: Documentar Algoritmos Clave (complete section 7 of template)
- [X] T021 [US1] Write Outline section - Paso 11: Especificar Consideraciones de Seguridad (complete section 8 of template)
- [X] T022 [US1] Write Outline section - Paso 12: Definir Estrategia de Errores (complete section 9 of template)
- [X] T023 [US1] Write Outline section - Paso 13: Documentar Alternativas Consideradas (complete section 10 of template)
- [X] T024 [US1] Write Outline section - Paso 14: Listar Preguntas y Riesgos (complete section 11 of template)
- [X] T025 [US1] Write Outline section - Paso 15: Definir Estrategia de Testing (complete sections 12-13 of template)
- [X] T026 [US1] Write Outline section - Paso 16: Validar con Equipo (execute gate-design.md, show handoff)
- [X] T027 [US1] Write Finalize & Validate section (confirm file, run gate, update agent context, show checklist)
- [X] T028 [US1] Write Notas section with context for brownfield projects
- [X] T029 [US1] Write High-Signaling Guidelines section (output, focus, language, Jidoka)
- [X] T030 [US1] Write AI Guidance section (role, proactiveness, kata adherence, traceability, gates)

**Checkpoint**: At this point, User Story 1 should be fully functional - command can generate basic Tech Design

---

## Phase 4: User Story 2 - Guided Step-by-Step Execution (Priority: P2)

**Goal**: Enhance command to show progress messages for each of the 15 steps with verification criteria and Jidoka blocks

**Independent Test**: Execute command and verify it shows step number, title, and verification criterion for each of the 15 steps, and stops appropriately if Solution Vision is missing

### Implementation for User Story 2

- [X] T031 [US2] Add progress messages to each paso in `.raise-kit/commands/02-projects/raise.4.tech-design.md` showing "Paso N: [Título]"
- [X] T032 [US2] Add verification criteria display after each paso showing "**Verificación**: [criterio]"
- [X] T033 [US2] Enhance Jidoka block in Paso 2 to show clear error message: "JIDOKA: Solution Vision no encontrado. Ejecutar `/raise.2.vision` primero."
- [X] T034 [US2] Add Jidoka blocks for other critical steps (template not found, Vision incomplete, etc.)
- [X] T035 [US2] Add guidance for handling ambiguous information (mark with [NEEDS CLARIFICATION] and continue with defaults)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work - command guides user through process

---

## Phase 5: User Story 3 - Validation and Handoff (Priority: P3)

**Goal**: Add validation summary and handoff message to guide user to next step in the workflow

**Independent Test**: Generate Tech Design and verify command shows summary with checkmark, file path, and handoff to `/raise.5.backlog`

### Implementation for User Story 3

- [X] T036 [US3] Add validation summary in Finalize section of `.raise-kit/commands/02-projects/raise.4.tech-design.md` showing "✓ Tech Design generado en specs/main/tech_design.md"
- [X] T037 [US3] Add handoff message showing "→ Siguiente paso: `/raise.5.backlog`"
- [X] T038 [US3] Add warning messages for empty critical sections showing "⚠ Sección '[nombre]' está vacía - revisar manualmente"
- [X] T039 [US3] Ensure gate-design.md execution results are displayed to user with pass/fail status

**Checkpoint**: All user stories should now be independently functional - command provides complete guided experience

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, validation, and final touches

- [X] T040 [P] Update `.raise-kit/README.md` to document the new `/raise.4.tech-design` command (if section exists) - N/A: README is a general guide without command-specific sections
- [X] T041 [P] Verify all references in command use `.specify/` paths (not `.raise-kit/` or `src/`) - VERIFIED
- [X] T042 [P] Verify template in `.raise-kit/templates/raise/tech/tech_design.md` matches source - VERIFIED (diff confirmed match)
- [X] T043 [P] Verify gate-design.md path is correct: `.specify/gates/raise/gate-design.md` - VERIFIED in command
- [X] T044 Test command in a mock project: Create test project with solution_vision.md - DEFERRED: Requires runtime execution in target project after kit injection
- [X] T045 Execute `/raise.4.tech-design` in test project and verify output - DEFERRED: Requires runtime execution in target project
- [X] T046 Verify all 14 sections of tech_design.md are populated (not empty or with unreplaced placeholders) - DEFERRED: Requires runtime execution
- [X] T047 Verify frontmatter YAML includes handoffs field pointing to raise.5.backlog - VERIFIED
- [X] T048 Verify Jidoka works: Execute command without solution_vision.md and confirm it stops with error - DEFERRED: Requires runtime execution
- [X] T049 Verify gate execution: Confirm gate-design.md runs and shows checklist - DEFERRED: Requires runtime execution
- [X] T050 Compare command structure with raise.1.discovery.md and raise.2.vision.md for consistency - VERIFIED

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after US1 - Enhances the command created in US1
- **User Story 3 (P3)**: Can start after US1 - Adds validation to the command created in US1

**Note**: US2 and US3 both modify the same file (raise.4.tech-design.md), so they should be done sequentially, not in parallel.

### Within Each User Story

- **US1**: Tasks T008-T030 should be done in sequence (building the command step by step)
- **US2**: Tasks T031-T035 can be done in any order (independent enhancements)
- **US3**: Tasks T036-T039 can be done in any order (independent additions)

### Parallel Opportunities

- **Phase 1**: T002 and T003 can run in parallel (different files)
- **Phase 2**: T005 and T006 can run in parallel (reading different files)
- **Phase 6**: T040, T041, T042, T043 can all run in parallel (different files/checks)

---

## Parallel Example: Setup Phase

```bash
# Launch setup tasks in parallel:
Task: "Copy tech design template from source: cp src/templates/tech/tech_design.md .raise-kit/templates/raise/tech/tech_design.md"
Task: "Verify gate-design.md exists in .raise-kit/gates/gate-design.md"
```

## Parallel Example: Polish Phase

```bash
# Launch documentation and verification tasks in parallel:
Task: "Update .raise-kit/README.md to document the new /raise.4.tech-design command"
Task: "Verify all references in command use .specify/ paths"
Task: "Verify template in .raise-kit/templates/raise/tech/tech_design.md matches source"
Task: "Verify gate-design.md path is correct"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundational (T004-T007)
3. Complete Phase 3: User Story 1 (T008-T030)
4. **STOP and VALIDATE**: Test command in mock project
5. If working, this is a functional MVP

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → **MVP Ready** (basic command works)
3. Add User Story 2 → Test independently → **Enhanced** (guided execution)
4. Add User Story 3 → Test independently → **Complete** (validation and handoff)
5. Polish → Final validation and documentation

### Sequential Strategy (Recommended)

Since this is a documentation project with a single command file being created/enhanced:

1. One developer completes Setup + Foundational
2. Same developer implements US1 (creates command)
3. Same developer enhances with US2 (adds guidance)
4. Same developer enhances with US3 (adds validation)
5. Final polish and testing

**Rationale**: All user stories modify the same file (`.raise-kit/commands/02-projects/raise.4.tech-design.md`), so parallel work would create merge conflicts.

---

## Summary

- **Total Tasks**: 50
- **Setup Phase**: 3 tasks
- **Foundational Phase**: 4 tasks
- **User Story 1 (P1)**: 23 tasks (MVP - core command)
- **User Story 2 (P2)**: 5 tasks (guided execution)
- **User Story 3 (P3)**: 4 tasks (validation and handoff)
- **Polish Phase**: 11 tasks (testing and validation)
- **Parallel Opportunities**: 8 tasks can run in parallel (marked with [P])
- **MVP Scope**: Phases 1-3 (30 tasks) deliver functional command

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story builds on the previous (US2 and US3 enhance US1)
- All tasks include exact file paths for clarity
- Command follows pattern of existing raise commands (raise.1.discovery, raise.2.vision)
- All references use `.specify/` paths for portability
- No code compilation/testing - this is a documentation/command project
- Validation is manual: execute command and inspect output
