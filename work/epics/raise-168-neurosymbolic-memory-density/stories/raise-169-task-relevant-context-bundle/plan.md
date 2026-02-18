# Implementation Plan: RAISE-169 — Task-relevant context bundle

## Overview
- **Story:** RAISE-169
- **Size:** M
- **Tasks:** 7
- **Created:** 2026-02-18

## Tasks

### Task 1: Define section registry and manifest model
- **Description:** Create `SECTION_REGISTRY` dict mapping section names to format functions. Add `SectionManifest` Pydantic model with section name, item count, and token estimate. Add `_count_*` helpers per section type that inspect data sources without formatting.
- **Files:**
  - Modify: `src/rai_cli/session/bundle.py`
  - Modify: `tests/session/test_bundle.py`
- **TDD Cycle:**
  - RED: test registry has all 5 sections (governance, behavioral, coaching, deadlines, progress); test manifest model validates; test count helpers return correct counts
  - GREEN: implement registry dict, manifest model, count helpers
  - REFACTOR: ensure count helpers reuse existing data loading functions
- **Verification:** `pytest tests/session/test_bundle.py -v`
- **Size:** S
- **Dependencies:** None

### Task 2: Extract `assemble_orientation()` function
- **Description:** Extract the always-on sections (developer, session ID, work context, last session, recent sessions, narrative, next prompt, pending) from `assemble_context_bundle()` into a standalone `assemble_orientation()` function. Add `_format_manifest()` that uses count helpers to generate the `# Available Context` block. `assemble_context_bundle()` still produces full output (calls orientation + priming) — no breaking change yet.
- **Files:**
  - Modify: `src/rai_cli/session/bundle.py`
  - Modify: `tests/session/test_bundle.py`
- **TDD Cycle:**
  - RED: test `assemble_orientation()` contains always-on sections but NOT governance/behavioral/coaching/deadlines/progress; test `_format_manifest()` output format with counts and token estimates
  - GREEN: extract function, implement manifest formatter
  - REFACTOR: ensure `assemble_context_bundle()` delegates to `assemble_orientation()` — existing tests still pass
- **Verification:** `pytest tests/session/test_bundle.py -v` (all existing tests must pass)
- **Size:** M
- **Dependencies:** Task 1

### Task 3: Add `assemble_sections()` function
- **Description:** New function that takes a list of section names, loads each section's data source independently (graph, profile, or state), formats using the corresponding `_format_*` function via the registry, and returns joined output. Validates section names against registry keys.
- **Files:**
  - Modify: `src/rai_cli/session/bundle.py`
  - Modify: `tests/session/test_bundle.py`
- **TDD Cycle:**
  - RED: test `assemble_sections(["governance", "behavioral"])` returns formatted governance + behavioral; test unknown section name raises ValueError; test empty sections list returns empty string; test single section works
  - GREEN: implement function using SECTION_REGISTRY dispatch
  - REFACTOR: ensure each section loader is self-contained (loads own data)
- **Verification:** `pytest tests/session/test_bundle.py -v`
- **Size:** S
- **Dependencies:** Task 1

### Task 4: Add `rai session context` CLI subcommand
- **Description:** New Typer command under `session_app` with `--sections` (comma-separated string, required) and `--project` (path, required). Loads profile and session state, calls `assemble_sections()`, outputs result. Validates section names and returns helpful error for unknown sections.
- **Files:**
  - Modify: `src/rai_cli/cli/commands/session.py`
  - Modify: `tests/cli/commands/test_session.py`
- **TDD Cycle:**
  - RED: test `rai session context --sections governance,behavioral --project .` returns formatted output; test unknown section returns error with available names; test `--sections` is required
  - GREEN: implement Typer command, wire to `assemble_sections()`
  - REFACTOR: ensure error messages list valid section names
- **Verification:** `pytest tests/cli/commands/test_session.py -v`
- **Size:** S
- **Dependencies:** Task 3

### Task 5: Make `assemble_context_bundle()` emit lean output
- **Description:** Change `assemble_context_bundle()` to emit orientation + manifest instead of full bundle. Remove priming sections (governance, behavioral, coaching, deadlines, progress) from the function's output. Update all existing tests that assert on priming content in the full bundle. This is the breaking change — coordinated with Task 6 (skill update).
- **Files:**
  - Modify: `src/rai_cli/session/bundle.py`
  - Modify: `tests/session/test_bundle.py`
- **TDD Cycle:**
  - RED: test `assemble_context_bundle()` does NOT contain `# Governance Primes`, `# Behavioral Primes`, `# Coaching`, `# Deadlines`; test it DOES contain `# Available Context` manifest
  - GREEN: replace priming assembly with manifest in `assemble_context_bundle()`
  - REFACTOR: update/remove tests that expected priming sections in bundle; ensure remaining assertions on orientation sections still pass
- **Verification:** `pytest tests/session/test_bundle.py -v && pytest tests/cli/commands/test_session.py -v`
- **Size:** M
- **Dependencies:** Task 2, Task 3

### Task 6: Update session-start skill
- **Description:** Update the session-start skill markdown to implement two-phase flow: Phase 1 calls `rai session start --context`, Phase 2 calls `rai session context --sections X,Y`. Add heuristic guidance for section selection per focus type. Add grounding check instruction (empty manifest counts → flag it).
- **Files:**
  - Modify: `.claude/skills/rai-session-start/instructions.md`
- **TDD Cycle:** N/A (markdown skill, no code tests)
- **Verification:** Manual review — skill instructions are clear and complete
- **Size:** S
- **Dependencies:** Task 4, Task 5

### Task 7: Manual integration test
- **Description:** Run the full two-phase flow end-to-end:
  1. `rai session start --context --project .` → verify lean output with manifest
  2. `rai session context --sections governance,behavioral --project .` → verify formatted primes
  3. Verify section counts in manifest match actual section output
  4. Verify unknown section name gives helpful error
- **Verification:** Demo the story working interactively
- **Size:** XS
- **Dependencies:** All previous tasks

## Execution Order
1. Task 1 (foundation — models and registry)
2. Task 2, Task 3 (parallel — both depend on Task 1, independent of each other)
3. Task 4 (depends on Task 3)
4. Task 5 (depends on Task 2 and Task 3 — the breaking change)
5. Task 6 (depends on Task 4 and Task 5)
6. Task 7 (final validation)

## Risks
- **Existing test breakage in Task 5:** Many tests assert on priming sections in `assemble_context_bundle()`. Mitigation: Task 2 preserves backward compat, Task 5 is the coordinated breaking change with test updates.
- **Section data loading duplication:** `assemble_sections()` needs to load graph/profile/state per section. Mitigation: reuse existing loader functions, pass preloaded data where possible.

## Duration Tracking
| Task | Size | Actual | Notes |
|------|------|--------|-------|
| 1 | S | -- | |
| 2 | M | -- | |
| 3 | S | -- | |
| 4 | S | -- | |
| 5 | M | -- | |
| 6 | S | -- | |
| 7 | XS | -- | Integration test |
