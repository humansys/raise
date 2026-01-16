# Tasks: Simplificar Exposición de Jidoka

**Input**: Design documents from `/specs/003-simplify-jidoka/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, quickstart.md ✅

**Type**: Trabajo de documentación conceptual (no desarrollo de software tradicional)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1)
- Include exact file paths in descriptions

## Path Conventions

- **Feature directory**: `specs/003-simplify-jidoka/`
- **Source documents**: `docs/framework/v2.1/model/20-glossary-v2.1.md`, `docs/framework/v2.1/model/25-ontology-bundle-v2_1.md`
- **No new files created**: All tasks modify existing documents

---

## Phase 1: Setup (Context Loading)

**Purpose**: Load and verify access to all source documents, understand current state

- [x] T001 Read current Jidoka entry in docs/framework/v2.1/model/20-glossary-v2.1.md
- [x] T002 [P] Search for all Jidoka references in docs/framework/v2.1/model/25-ontology-bundle-v2_1.md
- [x] T003 [P] Verify access to research.md decisions at specs/003-simplify-jidoka/research.md
- [x] T004 Review data-model.md template structure at specs/003-simplify-jidoka/data-model.md

---

## Phase 2: Foundational (No foundational tasks for this feature)

**Purpose**: This feature has no blocking prerequisites - can proceed directly to User Story 1

**⚠️ Note**: Typically, foundational tasks include shared infrastructure. For documentation work, we proceed directly to implementation.

**Checkpoint**: Ready to implement User Story 1

---

## Phase 3: User Story 1 - Simplificar Jidoka para Nuevos Aprendices (Priority: P1) 🎯 MVP

**Goal**: Update glossary v2.1 entry for Jidoka with staged structure (Stage 0-1 simple + Stage 3 formal), update ontology bundle references for consistency, validate against all gates and success criteria.

**Independent Test**: The Jidoka entry in glossary v2.1 has two clearly separated sections (Stage 0-1 with "Parar si algo falla" + Stage 3 with 4-step cycle). Stage 0-1 section passes SC-002 (zero TPS terms). Ontology bundle uses appropriate reference type per section stage. All 6 success criteria pass.

**Acceptance Criteria**:
1. Glossary entry has Stage 0-1 section with ≤10-word simplified definition
2. Glossary entry has Stage 3 section with formal 4-step TPS cycle
3. Stage 0-1 section contains ZERO prohibited terms (TPS, Toyota, Lean, 自働化)
4. Ontology bundle Stage 0-1 sections use simplified reference
5. Ontology bundle Stage 3 sections may use formal reference
6. Gate-Terminología and Gate-Coherencia pass

### Implementation for User Story 1

- [x] T005 [US1] Create backup of current glossary: cp docs/framework/v2.1/model/20-glossary-v2.1.md docs/framework/v2.1/model/20-glossary-v2.1.md.backup
- [x] T006 [P] [US1] Create backup of ontology bundle: cp docs/framework/v2.1/model/25-ontology-bundle-v2_1.md docs/framework/v2.1/model/25-ontology-bundle-v2_1.md.backup
- [x] T007 [US1] Locate Jidoka entry in glossary (grep -n "^### Jidoka" docs/framework/v2.1/model/20-glossary-v2.1.md)
- [x] T008 [US1] Replace Jidoka entry with staged structure per data-model.md template in docs/framework/v2.1/model/20-glossary-v2.1.md
- [x] T009 [US1] Verify simplified definition word count: echo "Parar si algo falla" | wc -w (expect: 4, ≤10 ✅)
- [x] T010 [US1] Validate SC-002 (zero TPS in Stage 0-1): sed -n '/^### Jidoka$/,/^---$/p' docs/framework/v2.1/model/20-glossary-v2.1.md | grep -iE "TPS|Toyota|Lean|自働化" (expect: 0 matches)
- [x] T011 [US1] Identify Jidoka references in ontology bundle and classify by section stage using grep -n "Jidoka\|jidoka" docs/framework/v2.1/model/25-ontology-bundle-v2_1.md
- [x] T012 [US1] Update Stage 0-1 section references in ontology bundle to use simplified form per D3 decision in docs/framework/v2.1/model/25-ontology-bundle-v2_1.md
- [x] T013 [US1] Update Stage 3 section references in ontology bundle (optional: can keep formal) per D3 decision in docs/framework/v2.1/model/25-ontology-bundle-v2_1.md
- [x] T014 [US1] Cross-validate consistency: compare Jidoka terminology between glossary and bundle (manual review)
- [x] T015 [US1] Validate Gate-Terminología: verify "Jidoka" is canonical term, no aliases created (grep -E "### Jidoka|Jidoka-simple|Jidoka-avanzado" docs/framework/v2.1/model/20-glossary-v2.1.md)
- [x] T016 [US1] Validate Gate-Coherencia: compare Stage 0-1 vs Stage 3 definitions for contradictions (manual review against Constitution §4, §8)
- [x] T017 [US1] Verify SC-001: Simplified definition ≤10 words (from T009 result)
- [x] T018 [US1] Verify SC-002: Zero prohibited terms in Stage 0-1 (from T010 result)
- [x] T019 [US1] Verify SC-003: Gate-Terminología passes (from T015 result)
- [x] T020 [US1] Verify SC-004: Gate-Coherencia passes (from T016 result)
- [x] T021 [US1] Verify SC-005: Complexity reduction 5% (prerequisite count 1→0: TPS no longer required)
- [x] T022 [US1] Verify SC-006: Comprehension time <30s (proxy: 4 words @ 200wpm ≈ 11s)

**Checkpoint**: At this point, User Story 1 should be fully functional - glossary entry is restructured, ontology bundle is consistent, all gates pass

---

## Phase 4: Polish & Cross-Cutting Validation

**Purpose**: Final validation and cleanup

- [x] T023 Remove backup files: rm docs/framework/v2.1/model/20-glossary-v2.1.md.backup docs/framework/v2.1/model/25-ontology-bundle-v2_1.md.backup
- [x] T024 Final visual inspection: read both Stage 0-1 and Stage 3 sections aloud to verify coherence
- [x] T025 Search for any other Jidoka references in docs/ that might need updating: grep -r "Jidoka" docs/ --exclude-dir=archive
- [x] T026 Update checklists/requirements.md with implementation completion status at specs/003-simplify-jidoka/checklists/requirements.md

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
T002, T003 — Can run in parallel (different documents, read-only)
```

**Phase 3 (User Story 1)**:
```
T005, T006 — Can run in parallel (different file backups)
```

**Note**: Most tasks in Phase 3 are sequential (edit glossary → validate → edit bundle → validate). Parallelization limited by file modification dependencies.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T004)
2. Complete Phase 3: User Story 1 (T005-T022)
3. **STOP and VALIDATE**: Jidoka entry is restructured, gates pass
4. Complete Phase 4: Polish (T023-T026)

### Incremental Delivery

| Milestone | Deliverable | Independent Value |
|-----------|-------------|-------------------|
| MVP | Glossary v2.1 + Ontology Bundle v2.1 updated | New learners see simplified Jidoka (4 words), advanced learners access formal definition. Barriers B-01/B-02 eliminated. |

### Execution Recommendation

**Solo Orquestador**: Execute sequentially T001 → T026. Stop at T022 checkpoint to validate all gates pass before polish.

**Pair/Team**: After Setup phase, one person can work on glossary (T008-T010), another on ontology bundle research (T011), then converge for validation (T014-T022).

---

## Validation Gates Summary

| Gate | Applied To | Criteria |
|------|------------|----------|
| Gate-Terminología | Glossary entry | "Jidoka" is canonical term, no aliases (T015) |
| Gate-Coherencia | Both documents | No contradictions Stage 0-1 vs Stage 3, aligns with Constitution (T016) |
| SC-001 | Simplified definition | ≤10 words (T009, T017) |
| SC-002 | Stage 0-1 section | Zero TPS/Toyota/Lean/自働化 (T010, T018) |
| SC-003 | Glossary | Gate-Terminología passes (T019) |
| SC-004 | Both documents | Gate-Coherencia passes (T020) |
| SC-005 | Conceptual | Prerequisite reduction 1→0 (T021) |
| SC-006 | User experience | <30s comprehension proxy (T022) |

---

## Notes

- [P] tasks = different files/read-only operations, no dependencies
- [US1] label maps all tasks to User Story 1 (only story in this feature)
- Total tasks: 26 (Quick Win feature, single story)
- Commit after Phase 3 checkpoint (T022) or after full completion (T026)
- All validation is text-based (grep, wc, manual review) - no code tests

---

## Task Count Summary

- **Phase 1 (Setup)**: 4 tasks
- **Phase 2 (Foundational)**: 0 tasks (skipped)
- **Phase 3 (User Story 1)**: 18 tasks
- **Phase 4 (Polish)**: 4 tasks
- **Total**: 26 tasks

**Parallel Opportunities**: 3 tasks can run in parallel (T002-T003, T005-T006)

**Critical Path**: T001 → T007 → T008 → T010 → T011 → T012 → T014 → T016 → T022 → T026
