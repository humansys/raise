# Tasks: Glosario Mínimo (Seed) para Stage 0

**Input**: Design documents from `/specs/002-glossary-seed/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, quickstart.md ✅

**Type**: Trabajo de documentación conceptual (no desarrollo de software tradicional)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1)
- Include exact file paths in descriptions

## Path Conventions

- **Feature directory**: `specs/002-glossary-seed/`
- **Source documents**: `docs/framework/v2.1/model/20-glossary-v2.1.md`, `specs/001-heutagogy-progressive-disclosure/learning-path.md`
- **Output artifact**: `docs/framework/v2.1/model/20a-glossary-seed.md`

---

## Phase 1: Setup (Context Loading)

**Purpose**: Load and verify access to all source documents

- [x] T001 Verify access to glosario v2.1 at docs/framework/v2.1/model/20-glossary-v2.1.md
- [x] T002 [P] Verify access to learning-path.md at specs/001-heutagogy-progressive-disclosure/learning-path.md
- [x] T003 [P] Verify access to Constitution at docs/framework/v2.1/model/00-constitution-v2.md
- [x] T004 Review data-model.md to confirm document structure at specs/002-glossary-seed/data-model.md

---

## Phase 2: Foundational (No foundational tasks for this feature)

**Purpose**: This feature has no blocking prerequisites - can proceed directly to User Story 1

**⚠️ Note**: Typically, foundational tasks include shared infrastructure. For documentation work, we proceed directly to implementation.

**Checkpoint**: Ready to implement User Story 1

---

## Phase 3: User Story 1 - Crear Glosario Mínimo para Onboarding (Priority: P1) 🎯 MVP

**Goal**: Generate `20a-glossary-seed.md` with 5 essential concepts (Orquestador, Spec, Agent, Validation Gate, Constitution) using simplified language and concrete examples.

**Independent Test**: The artifact `20a-glossary-seed.md` exists, contains exactly 5 concept sections, has 400-600 words, and passes Gate-Terminología and Gate-Coherencia.

**Acceptance Criteria**:
1. Document has 5 sections (one per concept)
2. Total length is 400-600 words
3. Each concept has definition + example
4. Terminología is canonical (matches glosario v2.1)
5. No contradictions with Constitution or glosario v2.1

### Implementation for User Story 1

- [x] T005 [US1] Create file structure: touch docs/framework/v2.1/model/20a-glossary-seed.md
- [x] T006 [P] [US1] Extract canonical definitions for 5 concepts from docs/framework/v2.1/model/20-glossary-v2.1.md
- [x] T007 [P] [US1] Extract Stage 0 concept list from specs/001-heutagogy-progressive-disclosure/learning-path.md
- [x] T008 [US1] Write introducción section (~50 palabras) explaining purpose of seed glossary in 20a-glossary-seed.md
- [x] T009 [P] [US1] Write Orquestador section (interfaz simple + detalle + ejemplo) in 20a-glossary-seed.md
- [x] T010 [P] [US1] Write Spec section (interfaz simple + detalle + ejemplo) in 20a-glossary-seed.md
- [x] T011 [P] [US1] Write Agent section (interfaz simple + detalle + ejemplo) in 20a-glossary-seed.md
- [x] T012 [P] [US1] Write Validation Gate section (interfaz simple + detalle + ejemplo) in 20a-glossary-seed.md
- [x] T013 [P] [US1] Write Constitution section (interfaz simple + detalle + ejemplo) in 20a-glossary-seed.md
- [x] T014 [US1] Write cierre section (~50 palabras) with link to glosario v2.1 in 20a-glossary-seed.md
- [x] T015 [US1] Verify word count is 400-600: wc -w docs/framework/v2.1/model/20a-glossary-seed.md
- [x] T016 [US1] Verify 5 sections exist: grep -c "^## " docs/framework/v2.1/model/20a-glossary-seed.md (expect: 5)
- [x] T017 [US1] Verify 5 examples exist: grep -c "\*\*Ejemplo\*\*:" docs/framework/v2.1/model/20a-glossary-seed.md (expect: 5)
- [x] T018 [US1] Validate Gate-Terminología: compare terms against docs/framework/v2.1/model/20-glossary-v2.1.md
- [x] T019 [US1] Validate Gate-Coherencia: check for contradictions with docs/framework/v2.1/model/00-constitution-v2.md
- [x] T020 [US1] Update checklists/requirements.md with completion status at specs/002-glossary-seed/checklists/requirements.md

**Checkpoint**: At this point, User Story 1 should be fully functional - the glossary seed document is complete and validated

---

## Phase 4: Polish & Cross-Cutting Validation

**Purpose**: Final validation and documentation updates

- [ ] T021 Cross-reference 20a-glossary-seed.md with learning-path.md (Stage 0 concepts match)
- [ ] T022 Cross-reference 20a-glossary-seed.md with glosario v2.1 (terminology is canonical)
- [ ] T023 Final word count verification: wc -w docs/framework/v2.1/model/20a-glossary-seed.md
- [ ] T024 Final format validation (markdown renders correctly, links work)
- [ ] T025 Update CLAUDE.md if seed glossary should be referenced in onboarding workflow

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1: Setup ────────────────────────────┐
    │                                      │
    ▼                                      │
Phase 2: (Skip - no foundational tasks)    │
    │                                      │
    ▼                                      │
Phase 3: User Story 1 (P1) ─── MVP ────────┤
    │                                      │
    ▼                                      │
Phase 4: Polish ◄──────────────────────────┘
```

### User Story Dependencies

- **User Story 1 (P1)**: No dependencies - standalone feature

### Parallel Opportunities Per Phase

**Phase 1 (Setup)**:
```
T002, T003 — Can run in parallel (different source documents)
```

**Phase 3 (User Story 1)**:
```
T006, T007 — Can run in parallel (different source documents)
T009, T010, T011, T012, T013 — Can run in parallel (different sections of same file, but conceptually independent)
```

**Note on T009-T013 parallelization**: While these tasks write to the same file, they are conceptually independent sections. In practice, execute sequentially or use temporary files that merge later.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T004)
2. Complete Phase 3: User Story 1 (T005-T020)
3. **STOP and VALIDATE**: 20a-glossary-seed.md is complete and independently usable
4. Review with stakeholders before proceeding to polish

### Incremental Delivery

| Milestone | Deliverable | Independent Value |
|-----------|-------------|-------------------|
| MVP | 20a-glossary-seed.md | Reduced onboarding complexity - new Orquestadores can start with 5 concepts instead of 35 |

### Execution Recommendation

**Solo Orquestador**: Execute sequentially T001 → T025, stopping at T020 checkpoint to validate.

**Pair/Team**: After Setup phase, T009-T013 can be divided among team members (each writes 1-2 concept sections), then merge.

---

## Validation Gates Summary

| Gate | Applied To | Criteria |
|------|------------|----------|
| Gate-Terminología | 20a-glossary-seed.md | Uses canonical terms from glosario v2.1 |
| Gate-Coherencia | 20a-glossary-seed.md | No contradictions with Constitution or glosario v2.1 |
| SC-001 | 20a-glossary-seed.md | Exactly 5 sections |
| SC-002 | 20a-glossary-seed.md | 400-600 words |
| SC-003 | 20a-glossary-seed.md | 5 examples present |

---

## Notes

- [P] tasks = different files/sections, no dependencies
- [US1] label maps task to User Story 1 (only story in this feature)
- Total tasks: 25 (small feature, Quick Win)
- Commit after each concept section or after full document completion
- Stop at T020 checkpoint to validate artifact independently
