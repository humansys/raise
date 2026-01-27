# Tasks: Transform Commands Script

**Input**: Design documents from `/specs/007-transform-commands/`
**Prerequisites**: plan.md (complete), spec.md (complete), research.md (complete)

**Tests**: Manual verification only (no automated tests requested)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Script location**: `template/.specify/scripts/bash/raise/transform-commands.sh`

---

## Phase 1: Setup

**Purpose**: Create directory structure and script skeleton

- [x] T001 Create directory `template/.specify/scripts/bash/raise/` if not exists
- [x] T002 Create script file `template/.specify/scripts/bash/raise/transform-commands.sh` with shebang and header comments

---

## Phase 2: Foundational (Script Infrastructure)

**Purpose**: Helper functions and configuration that all user stories depend on

**CRITICAL**: These must be complete before any user story can work

- [x] T003 Add FILE_MAP array asociativo con los 9 mapeos de archivos en `transform-commands.sh`
- [x] T004 [P] Add REF_MAP array asociativo con los 9 mapeos de referencias en `transform-commands.sh`
- [x] T005 [P] Add SRC_DIR and DEST_DIR variables con rutas configurables en `transform-commands.sh`
- [x] T006 Add helper functions (error, warn, info) en `transform-commands.sh`

**Checkpoint**: Infrastructure ready - user story implementation can begin

---

## Phase 3: User Story 1 - Transformación Completa (Priority: P1)

**Goal**: Ejecutar script y transformar 9 archivos con nombres y referencias actualizadas

**Independent Test**: Ejecutar script con carpeta origen poblada, verificar 9 archivos en destino con nombres correctos y referencias actualizadas

### Implementation for User Story 1

- [x] T007 [US1] Implement transform_file() function that reads file, applies REF_MAP replacements, writes to destination in `transform-commands.sh`
- [x] T008 [US1] Implement create_directories() function to create `01-onboarding/` and `03-feature/` subdirectories in `transform-commands.sh`
- [x] T009 [US1] Implement main transformation loop iterating FILE_MAP and calling transform_file() in `transform-commands.sh`
- [x] T010 [US1] Add check for existing destination file - skip and warn if exists in `transform-commands.sh`
- [x] T011 [US1] Add success/error counter variables and increment logic in `transform-commands.sh`

**Checkpoint**: Script transforms files correctly. Ready for User Story 2.

---

## Phase 4: User Story 2 - Reporte de Resultado (Priority: P2)

**Goal**: Mostrar resumen de ejecución con conteo de archivos procesados y errores

**Independent Test**: Ejecutar script y verificar que output incluye "X archivos transformados exitosamente"

### Implementation for User Story 2

- [ ] T012 [US2] Implement print_summary() function showing success count and error list in `transform-commands.sh`
- [ ] T013 [US2] Add error collection array to track failed files with reasons in `transform-commands.sh`
- [ ] T014 [US2] Call print_summary() at end of main() and set appropriate exit code in `transform-commands.sh`

**Checkpoint**: Script shows clear summary. Ready for User Story 3.

---

## Phase 5: User Story 3 - Validación Pre-ejecución (Priority: P3)

**Goal**: Validar carpeta origen existe y tiene archivos antes de procesar

**Independent Test**: Ejecutar script con carpeta origen inexistente, verificar mensaje de error claro y exit code 1

### Implementation for User Story 3

- [ ] T015 [US3] Implement validate_source() function checking if SRC_DIR exists in `transform-commands.sh`
- [ ] T016 [US3] Add check for empty source directory (no .md files) in validate_source() in `transform-commands.sh`
- [ ] T017 [US3] Call validate_source() at start of main() before any processing in `transform-commands.sh`

**Checkpoint**: Script validates environment before processing.

---

## Phase 6: Polish & Edge Cases

**Purpose**: Handle edge cases and make script executable

- [ ] T018 [P] Add handling for unrecognized files (not in FILE_MAP) - ignore and warn in `transform-commands.sh`
- [ ] T019 [P] Make script executable with `chmod +x template/.specify/scripts/bash/raise/transform-commands.sh`
- [ ] T020 Run manual verification using quickstart.md test scenarios
- [ ] T021 Update spec.md feature branch reference from 001 to 007 in `specs/007-transform-commands/spec.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational - core transformation
- **User Story 2 (Phase 4)**: Depends on US1 completion (needs counters from US1)
- **User Story 3 (Phase 5)**: Can start after Foundational (independent of US1/US2)
- **Polish (Phase 6)**: Depends on all user stories

### User Story Dependencies

- **User Story 1 (P1)**: Foundational complete, no other story dependencies
- **User Story 2 (P2)**: Uses counters from US1, so depends on US1 structure
- **User Story 3 (P3)**: Independent - only needs Foundational

### Within Each User Story

- Helper functions before main logic
- Core functionality before error handling
- Single file so no parallel within story

### Parallel Opportunities

- **Phase 2**: T003, T004, T005 can run in parallel (different sections of same file)
- **Phase 6**: T018, T019 can run in parallel (different concerns)
- **Stories**: US3 can be implemented in parallel with US1/US2 (independent validation)

---

## Parallel Example: Foundational Phase

```bash
# Can be written simultaneously (different sections):
Task: "T003 - Add FILE_MAP array"
Task: "T004 - Add REF_MAP array"
Task: "T005 - Add SRC_DIR/DEST_DIR variables"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T002)
2. Complete Phase 2: Foundational (T003-T006)
3. Complete Phase 3: User Story 1 (T007-T011)
4. **STOP and VALIDATE**: Test transformation with real files
5. Script is functional for basic use

### Incremental Delivery

1. Setup + Foundational → Script skeleton ready
2. Add User Story 1 → Core transformation works (MVP!)
3. Add User Story 2 → Better user feedback
4. Add User Story 3 → Safer execution with validation
5. Polish → Production ready

---

## Notes

- All implementation is in a single file: `template/.specify/scripts/bash/raise/transform-commands.sh`
- No automated tests - use manual verification from quickstart.md
- Bash 4.0+ required for associative arrays
- Test on Git Bash (Windows) for cross-platform validation
