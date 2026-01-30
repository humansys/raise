# Tasks: Public Repository Readiness

**Input**: Design documents from `/specs/007-public-repo-readiness/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, quickstart.md ✅

**Tests**: Not requested - this is a documentation-focused feature.

**Organization**: Tasks organized by work package (WP0-WP4) to enable phased execution, with user stories mapped to appropriate phases.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[WPx]** / **[USx]**: Work Package or User Story this task belongs to
- Include exact file paths in descriptions

## Path Conventions

- **Documentation root**: Repository root for README.md, LICENSE, CONTRIBUTING.md
- **Framework docs**: `docs/framework/v2.1/model/`
- **ADRs**: `docs/framework/v2.1/adrs/`
- **Katas**: `src/katas-v2.1/` (canonical) + `docs/framework/v2.1/katas/` (duplicate)
- **Templates**: `src/templates/`

---

## Phase 1: Setup (Analysis Environment)

**Purpose**: Prepare environment and gather baseline data for deep audit

**🤖 RECOMMENDED MODEL: Haiku**
- **Why**: All tasks are mechanical data gathering (bash, grep, file operations)
- **Complexity**: Low - no decisions or reasoning required
- **Cost**: ~$0.10 vs $2-3 with Opus
- **Time**: 15-20 minutes
- **Quality**: No loss using Haiku for these operations

- [x] T001 Generate complete file inventory of repository → 254 .md files inventoried ✅
- [x] T002 [P] Create structure-analysis.md with CORRECT analysis in specs/007-public-repo-readiness/structure-analysis.md ✅
- [x] T003 [P] Document current link structure → Documented in structure-analysis.md Part A-B ✅

---

## Phase 2: WP0 - Deep Content & Structure Audit (INTERACTIVE)

**Purpose**: Audit EVERY document to determine what belongs in a public conceptual repository

**⚠️ CRITICAL**: This phase requires interactive decisions with Orquestador. No user story work can begin until structure is finalized.

**🤖 RECOMMENDED MODEL: Opus** ⚠️
- **Why**: Strategic decisions that block all downstream work
- **Complexity**: Very High - requires judgment, ontological thinking, trade-off analysis
- **Interactive**: Must present options and await Orquestador approval
- **Stakes**: Wrong structure decision requires rework of all subsequent phases
- **Reasoning needed**:
  - Audience analysis (who is this repo for?)
  - Content classification (what belongs publicly?)
  - Architecture evaluation (navigability vs depth vs conventions)
  - Constitution alignment (Simplicidad, Coherencia principles)
- **Cost justified**: ~$10-15 for Opus vs potential wasted effort with wrong decisions

### Part A: Content Audit (Document-by-Document)

- [ ] T004 [WP0] Audit business documents for public suitability:
  - `docs/framework/v2.1/model/02-business-model-v2.md`
  - `docs/framework/v2.1/model/03-market-context-v2.md`
  - `docs/framework/v2.1/model/04-stakeholder-map-v2.md`
- [ ] T005 [WP0] Audit internal planning documents:
  - `docs/framework/v2.1/model/30-roadmap-v2.1.md`
  - `docs/framework/v2.1/model/31-current-state-v2.1.md`
  - `docs/framework/v2.1/model/36-roadmap-tecnico-mvp.md`
  - `docs/framework/v2.1/model/37-roadmap-tecnico-mvp-legacy.md`
- [ ] T006 [WP0] Audit work artifacts and logs:
  - `docs/framework/v2.1/model/32-session-log-v2.md`
  - `docs/framework/v2.1/model/33-issues-decisions-v2.md`
  - `docs/framework/v2.1/model/34-dependencies-blockers-v2.md`
  - `docs/framework/v2.1/model/35-ontology-backlog-v2.md`
- [ ] T007 [WP0] Audit reportes directory for public suitability in docs/framework/v2.1/reportes/
- [ ] T008 [WP0] Audit specs/ directory - determine if active development work should be public
- [ ] T009 [WP0] Review CLAUDE.md for internal-only content that shouldn't be public
- [ ] T010 [WP0] Document audit decisions (keep/remove/relocate) in specs/007-public-repo-readiness/structure-analysis.md

### Part B: Structure Analysis

- [ ] T011 [WP0] Resolve Kata duplication: decide canonical location between docs/framework/v2.1/katas/ and src/katas-v2.1/
- [ ] T012 [WP0] Evaluate `src/` directory naming for conceptual repository (keep/rename/eliminate)
- [ ] T013 [WP0] Evaluate versioning in paths (keep `v2.1` vs flatten)
- [ ] T014 [WP0] Decide final repository structure (Option A/B/C from data-model.md or hybrid)
- [ ] T015 [WP0] Create ADR if significant structural changes decided in docs/framework/v2.1/adrs/adr-0XX-public-repo-structure.md

### Part C: Content Destination Decisions

- [ ] T016 [WP0] Define destination for each removed document (private repo/archive/delete)
- [ ] T017 [WP0] Update structure-analysis.md with final decisions and migration plan

**Checkpoint**: Structure decisions finalized - WP1 restructuring can begin

---

## Phase 3: WP1 - Repository Restructuring (INTERACTIVE)

**Purpose**: Execute directory reorganization based on WP0 decisions

**⚠️ CRITICAL**: Execute moves interactively with Orquestador review before each action

**🤖 RECOMMENDED MODEL: Sonnet**
- **Why**: Execution tasks requiring verification and careful link updates
- **Complexity**: Medium - needs context awareness and validation
- **Interactive**: Review before destructive operations (file moves/deletes)
- **Reasoning needed**:
  - Track which links are affected by moves
  - Validate no broken references after changes
  - Apply WP0 decisions correctly across multiple files
- **Not Haiku**: Too risky for destructive operations without verification
- **Not Opus**: Decisions already made in WP0, this is execution

### Content Removal/Relocation

- [ ] T018 [WP1] Remove or relocate business documents per WP0 decision
- [ ] T019 [WP1] Remove or relocate internal planning documents per WP0 decision
- [ ] T020 [WP1] Remove or relocate work artifacts per WP0 decision
- [ ] T021 [WP1] Handle reportes/ directory per WP0 decision
- [ ] T022 [WP1] Handle specs/ directory visibility per WP0 decision

### Structure Changes (if applicable)

- [ ] T023 [WP1] Consolidate Katas to canonical location per WP0 decision
- [ ] T024 [WP1] Execute directory structure changes per WP0 decision
- [ ] T025 [WP1] Update internal links affected by moves (grep + manual fix)
- [ ] T026 [WP1] Add DEPRECATED.md markers to any archived content
- [ ] T027 [WP1] Verify no broken references post-restructure with link audit

**Checkpoint**: Repository structure ready for entry point files

---

## Phase 4: WP2 - Entry Point Files (US1, US2, US5)

**Purpose**: Create README.md, LICENSE, CONTRIBUTING.md for public access

**Goal (US1)**: First-time visitor can understand RaiSE within 5 minutes
**Goal (US2)**: Clear navigation to all documentation sections
**Goal (US5)**: Contributors can find guidelines and submit feedback

**🤖 RECOMMENDED MODEL: Sonnet**
- **Why**: Public-facing content where quality and tone matter
- **Complexity**: Medium - requires understanding RaiSE ontology and audience needs
- **Stakes**: README is first impression - poor quality damages credibility
- **Reasoning needed**:
  - Concise but complete explanations (Principle IV: Simplicidad)
  - Correct canonical terminology (v2.1 glossary)
  - Navigation that serves multiple personas
  - Professional tone for F&F audience
- **Not Haiku**: README quality is critical for US1 success
- **Not Opus**: Template-guided content creation doesn't need highest reasoning

### README.md (FR-001, FR-002, FR-010, FR-011)

- [ ] T028 [US1] Create README.md at repository root with RaiSE purpose and value proposition
- [ ] T029 [P] [US2] Add Quick Start navigation table to README.md with links to:
  - Constitution: docs/framework/v2.1/model/00-constitution-v2.md
  - Glossary: docs/framework/v2.1/model/20-glossary-v2.1.md
  - Methodology: docs/framework/v2.1/model/21-methodology-v2.md
  - ADRs: docs/framework/v2.1/adrs/adr-000-index.md
  - Katas: [canonical location per WP0]
  - Templates: src/templates/
- [ ] T030 [P] [US1] Add Repository Structure section to README.md reflecting final structure
- [ ] T031 [P] [US1] Add RaiSE Ecosystem acknowledgment section to README.md
- [ ] T032 [P] [US2] Add Key Concepts section with canonical terminology summary to README.md

### LICENSE (FR-003)

- [ ] T033 [P] [US5] Create LICENSE file at repository root with Apache 2.0 full text

### CONTRIBUTING.md (FR-008, FR-015)

- [ ] T034 [US5] Create CONTRIBUTING.md at repository root with:
  - Clarification this is conceptual repository
  - GitLab Issues link for feedback
  - Contribution process
  - Terminology guidelines linking to glossary

**Checkpoint**: Entry point files complete - US1, US2, US5 testable

**Independent Test (US1)**: Developer can read README and explain RaiSE purpose in 5 minutes
**Independent Test (US2)**: User can navigate from README to any core doc in ≤2 clicks
**Independent Test (US5)**: Contributor can find CONTRIBUTING.md and GitLab Issues within 1 minute

---

## Phase 5: WP3 - Content Audits (US3, US4)

**Purpose**: Terminology audit, link audit, and security scan

**Goal (US3)**: Examples and Katas are accessible and demonstrate RaiSE principles
**Goal (US4)**: Zero deprecated terminology in user-facing documentation

**🤖 RECOMMENDED MODEL: Haiku**
- **Why**: Pattern-matching and mechanical fixes
- **Complexity**: Low - grep audits and simple replacements
- **Tasks breakdown**:
  - Grep audits (T035-T038, T041, T045-T047): Pure mechanical search
  - Fixing deprecated terms (T039): Simple find/replace once identified
  - Verification tasks (T050-T054): Checklist-based validation
- **Exception**: If fixes require nuanced rewording, switch to Sonnet
- **Cost**: ~$0.20 vs $5-7 with Opus for audit work

### Terminology Audit (FR-004, US4)

- [ ] T035 [US4] Run grep audit for "DoD" in docs/framework/v2.1/ (must be 0 in user-facing docs)
- [ ] T036 [P] [US4] Run grep audit for deprecated "Rule" usage (distinguish from Guardrail)
- [ ] T037 [P] [US4] Run grep audit for "Developer" as role (should be Orquestador)
- [ ] T038 [P] [US4] Run grep audit for L0/L1/L2/L3 kata levels in docs/framework/v2.1/
- [ ] T039 [US4] Fix any deprecated terminology found in user-facing documents
- [ ] T040 [US4] Document terminology audit results in specs/007-public-repo-readiness/audit-results.md

### Link Audit (FR-005)

- [ ] T041 [P] Extract all internal markdown links from docs/framework/v2.1/
- [ ] T042 Verify each linked file exists (manual or scripted)
- [ ] T043 Fix any broken internal links discovered
- [ ] T044 Document link audit results in specs/007-public-repo-readiness/audit-results.md

### Security Scan (FR-009)

- [ ] T045 [P] Run grep for API key patterns (sk-, api_key, apikey, API_KEY)
- [ ] T046 [P] Run grep for credential patterns (password, secret, token=)
- [ ] T047 [P] Run grep for private paths (/Users/, /home/, C:\\Users)
- [ ] T048 Remove any sensitive information found
- [ ] T049 Document security scan results in specs/007-public-repo-readiness/audit-results.md

### Katas Verification (FR-012, US3)

- [ ] T050 [US3] Verify all Katas use v2.1 taxonomy (Principio/Flujo/Patrón/Técnica)
- [ ] T051 [P] [US3] Verify Katas have clear learning objectives and demonstrate RaiSE principles
- [ ] T052 [US3] Ensure at least one complete example demonstrates RaiSE principles in practice (FR-014)

### ADRs Verification (FR-013)

- [ ] T053 [P] Verify ADR index exists and is complete at docs/framework/v2.1/adrs/adr-000-index.md
- [ ] T054 Verify all ADRs are listed in index

**Checkpoint**: All audits complete - US3, US4 testable

**Independent Test (US3)**: Developer can find Katas and understand which principles they demonstrate
**Independent Test (US4)**: Grep for deprecated terms returns 0 matches in user-facing docs

---

## Phase 6: WP4 - Final Validation (All User Stories)

**Purpose**: Execute all Validation Gates and final review

**🤖 RECOMMENDED MODEL: Sonnet**
- **Why**: Final validation requires judgment and fresh perspective
- **Complexity**: Medium - verification tasks with success criteria evaluation
- **Critical tasks**:
  - T067: Fresh eyes review (needs quality assessment)
  - T068: Incorporate feedback (requires understanding intent)
  - Gate validations: Need to evaluate "self-explanatory" and "clear distinction"
- **Not Haiku**: Gates require interpretation of subjective criteria (e.g., "90% can find without assistance")
- **Not Opus**: Validation doesn't need strategic thinking, just thorough checking

### Gate-Structure (FR-006, FR-007)

- [ ] T055 Verify README.md exists at repository root
- [ ] T056 [P] Verify LICENSE exists at repository root
- [ ] T057 [P] Verify CONTRIBUTING.md exists at repository root
- [ ] T058 Verify directory structure is self-explanatory (90% test)
- [ ] T059 Verify current vs archived content is clearly distinguished

### Gate-Navigation (SC-004)

- [ ] T060 Test: Constitution accessible in ≤2 clicks from README
- [ ] T061 [P] Test: Glossary accessible in ≤2 clicks from README
- [ ] T062 [P] Test: Methodology accessible in ≤2 clicks from README
- [ ] T063 [P] Test: ADRs accessible in ≤2 clicks from README

### Gate-Terminology (SC-003)

- [ ] T064 Final verification: 0% deprecated terms in user-facing docs

### Gate-Secrets (SC-008)

- [ ] T065 Final verification: 0 exposed secrets or sensitive information

### Gate-Links (SC-002)

- [ ] T066 Final verification: 0% broken internal links

### Fresh Eyes Review

- [ ] T067 User test: Someone unfamiliar with RaiSE reviews README and provides feedback
- [ ] T068 Incorporate feedback from fresh eyes review

### Final Commit

- [ ] T069 Create final commit with all changes for public readiness
- [ ] T070 Update specs/007-public-repo-readiness/ with completion status

**Checkpoint**: All Validation Gates passed - Ready for F&F release 🎉

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1: Setup
    ↓
Phase 2: WP0 - Deep Audit (INTERACTIVE - BLOCKS ALL)
    ↓
Phase 3: WP1 - Restructure (INTERACTIVE)
    ↓
Phase 4: WP2 - Entry Files ←──┐
    ↓                         │ Can run in parallel
Phase 5: WP3 - Audits    ←────┘ (after WP1)
    ↓
Phase 6: WP4 - Validation
```

### User Story to Work Package Mapping

| User Story | Primary WP | Tasks |
|------------|------------|-------|
| US1: First-Time Visitor (P1) | WP2 | T028, T030, T031 |
| US2: Documentation Navigation (P1) | WP2 | T029, T032 |
| US3: Examples/Katas (P2) | WP3 | T050, T051, T052 |
| US4: Terminology Consistency (P1) | WP3 | T035-T040 |
| US5: Contribution Readiness (P3) | WP2 | T033, T034 |

### Critical Path

1. **T001-T003** → Setup baseline
2. **T004-T017** → WP0 audit decisions (INTERACTIVE - BLOCKS EVERYTHING)
3. **T018-T027** → WP1 restructure (INTERACTIVE)
4. **T028-T034** → Entry files (unblocks US1, US2, US5)
5. **T035-T054** → Audits (unblocks US3, US4)
6. **T055-T070** → Final validation

### Parallel Opportunities

**Within Phase 1:**
- T002 and T003 can run in parallel

**Within Phase 4 (WP2):**
- T029, T030, T031, T032 can run in parallel after T028
- T033 can run in parallel with README tasks

**Within Phase 5 (WP3):**
- T036, T037, T038 can run in parallel
- T041, T045, T046, T047 can run in parallel
- T051, T053 can run in parallel

**Within Phase 6 (WP4):**
- T056, T057 can run in parallel after T055
- T061, T062, T063 can run in parallel after T060

---

## Parallel Example: Phase 5 Audits

```bash
# Launch all terminology grep audits together:
Task: "Run grep audit for deprecated 'Rule' usage"
Task: "Run grep audit for 'Developer' as role"
Task: "Run grep audit for L0/L1/L2/L3 kata levels"

# Launch all security scans together:
Task: "Run grep for API key patterns"
Task: "Run grep for credential patterns"
Task: "Run grep for private paths"
```

---

## Implementation Strategy

### MVP First (US1 + US4 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: WP0 Deep Audit (CRITICAL - interactive decisions)
3. Complete Phase 3: WP1 Restructure (interactive execution)
4. Complete Phase 4: WP2 Entry Files (README, LICENSE, CONTRIBUTING)
5. Complete T035-T040: Terminology audit
6. **STOP and VALIDATE**: Test US1 (README comprehension) and US4 (terminology clean)
7. Ready for minimal F&F launch if time-constrained

### Full Delivery

1. Setup + WP0 + WP1 → Structure ready
2. WP2 → Entry files ready (US1, US2, US5 testable)
3. WP3 → Audits complete (US3, US4 testable)
4. WP4 → All gates passed
5. Ready for F&F release 🎉

### Time-Constrained Strategy (2-day timeline)

**Day 1:**
- Morning: Phase 1 + Phase 2 (WP0 audit decisions)
- Afternoon: Phase 3 (WP1 restructure)

**Day 2:**
- Morning: Phase 4 (WP2 entry files) + Phase 5 terminology audit (T035-T040)
- Afternoon: Remaining Phase 5 audits + Phase 6 validation
- End of day: Ready for F&F 🚀

---

## Notes

- **[P]** tasks = different files, no dependencies
- **[WPx]** / **[USx]** labels map tasks to work packages and user stories
- **Interactive phases (WP0, WP1)** require Orquestador decisions - DO NOT proceed without review
- Commit after each logical group of tasks
- Stop at any checkpoint to validate independently
- **2-day timeline is tight** - prioritize WP0 decisions and entry files over comprehensive audits
- Deferred audits can be completed post-launch if needed

---

## Model Selection Quick Reference

**🎯 Choose the right model for each phase to optimize cost and quality:**

| Phase | Model | Cost Est. | Why |
|-------|-------|-----------|-----|
| **Phase 1: Setup** | **Haiku** ✅ | ~$0.10 | Mechanical data gathering |
| **Phase 2: WP0 Audit** | **Opus** ⚠️ | ~$10-15 | Strategic decisions blocking all work |
| **Phase 3: WP1 Restructure** | **Sonnet** | ~$3-5 | Execution with verification |
| **Phase 4: WP2 Entry Files** | **Sonnet** | ~$3-5 | Public content quality matters |
| **Phase 5: WP3 Audits** | **Haiku** ✅ | ~$0.20 | Grep + pattern matching |
| **Phase 6: WP4 Validation** | **Sonnet** | ~$2-3 | Subjective criteria evaluation |

**Total estimated cost**: ~$19-28 (optimized) vs ~$60-80 (all Opus)

**Key principle**: Use Haiku for mechanical tasks, Sonnet for content quality, Opus for strategic decisions.

---

## Summary

| Metric | Value |
|--------|-------|
| Total Tasks | 70 |
| Phase 1 (Setup) | 3 tasks |
| Phase 2 (WP0 Audit) | 14 tasks (INTERACTIVE) |
| Phase 3 (WP1 Restructure) | 10 tasks (INTERACTIVE) |
| Phase 4 (WP2 Entry Files) | 7 tasks |
| Phase 5 (WP3 Audits) | 20 tasks |
| Phase 6 (WP4 Validation) | 16 tasks |
| Parallel Opportunities | 28 tasks marked [P] |
| MVP Scope | T001-T040 (~40 tasks) |
| Tests Included | No (not requested) |

**User Story Task Counts:**
- US1 (First-Time Visitor): 4 tasks
- US2 (Documentation Navigation): 3 tasks
- US3 (Examples/Katas): 3 tasks
- US4 (Terminology): 6 tasks
- US5 (Contribution): 2 tasks
- Infrastructure/Cross-cutting: 52 tasks

---

*Tasks generated: 2026-01-16 | Ready for `/speckit.implement`*
