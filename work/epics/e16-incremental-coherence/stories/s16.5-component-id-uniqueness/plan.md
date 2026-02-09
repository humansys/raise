# Implementation Plan: S16.5 Component ID Uniqueness

## Overview
- **Story:** S16.5
- **Size:** S (3 SP)
- **Created:** 2026-02-09

## Tasks

### Task 1: Fix ID generation in `build_hierarchy()` + update tests
- **Description:** Change `_file_stem()` to `_file_to_module()` in the two ID-generation lines (`analyzer.py:418,442`). The new format: `comp-{dotted.module}-{name}`. Update `test_component_id_format` assertion and any analyze() integration test assertions that check IDs.
- **Files:** `src/raise_cli/discovery/analyzer.py`, `tests/discovery/test_analyzer.py`
- **TDD Cycle:** RED (update test assertion to expect new ID format → fails with old code) → GREEN (change ID generation) → REFACTOR
- **Verification:** `pytest tests/discovery/test_analyzer.py -v`
- **Size:** S
- **Dependencies:** None

### Task 2: Add post-analysis uniqueness assertion
- **Description:** After `build_hierarchy()` returns in `analyze()`, assert all component IDs are unique. If duplicates found, raise `ValueError` with the duplicate IDs (Jidoka — stop on defect). Add test with conflicting files that would produce duplicate IDs under the old scheme but unique IDs under the new scheme, and a test that verifies the assertion fires on actual duplicates.
- **Files:** `src/raise_cli/discovery/analyzer.py`, `tests/discovery/test_analyzer.py`
- **TDD Cycle:** RED (test duplicate ID raises ValueError) → GREEN (add assertion in `analyze()`) → REFACTOR
- **Verification:** `pytest tests/discovery/test_analyzer.py -v`
- **Size:** S
- **Dependencies:** Task 1

### Task 3: Add collision warning in graph builder `load_components()`
- **Description:** In `UnifiedGraphBuilder.load_components()`, after loading all component nodes, check for ID collisions against existing node IDs. Log a warning via `logging.warning()` when a component ID already exists. Add test.
- **Files:** `src/raise_cli/context/builder.py`, `tests/context/test_builder.py`
- **TDD Cycle:** RED (test warning emitted on collision) → GREEN (add warning check) → REFACTOR
- **Verification:** `pytest tests/context/test_builder.py -v`
- **Size:** S
- **Dependencies:** None (parallel with Task 1-2)

### Task 4: Manual integration test — re-run discovery pipeline
- **Description:** Run full discovery pipeline: `raise discover scan` → `raise discover analyze` → verify 345 unique IDs → `raise memory build` → verify 345 components in graph. This validates the fix end-to-end with real data.
- **Verification:** Component count in graph equals validated component count (0 silent drops)
- **Size:** XS
- **Dependencies:** Tasks 1, 2, 3

## Execution Order
1. Task 1 — fix ID generation (foundation)
2. Task 2 — uniqueness assertion (depends on Task 1)
3. Task 3 — graph builder warning (parallel with 1-2, but logically after)
4. Task 4 — manual integration test (final validation)

## Risks
- **Test count:** Existing tests assert on specific ID strings → mitigated by updating assertions in Task 1
- **Downstream consumers:** `components-validated.json` stores old IDs → mitigated: out of scope per scope doc (overwrite is fine, graph rebuilt from scratch)

## Duration Tracking
| Task | Size | Actual | Notes |
|------|------|--------|-------|
| 1 | S | -- | |
| 2 | S | -- | |
| 3 | S | -- | |
| 4 | XS | -- | Integration test |
