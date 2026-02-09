# Implementation Plan: BF-1 Fix Flaky Diff Integration Tests

## Overview
- **Story:** BF-1
- **Size:** XS
- **Created:** 2026-02-09

## Tasks

### Task 1: Replace real graph with fixture graph
- **Description:** Replace `_build_real_graph()` (calls `UnifiedGraphBuilder().build()`) with `_build_fixture_graph()` that constructs a deterministic `UnifiedGraph` with ~5 programmatic `ConceptNode` entries. Update all 4 diff tests to use fixture graph and fixture node IDs. Remove `test_real_graph_has_sufficient_nodes` (tests builder, not diff). Remove unused `UnifiedGraphBuilder` import.
- **Files:** `tests/context/test_diff_integration.py`
- **TDD Cycle:** GREEN (tests already exist — rewrite to use fixtures, verify they pass)
- **Verification:** `uv run pytest tests/context/test_diff_integration.py -v`
- **Size:** S
- **Dependencies:** None

### Task 2: Manual Integration Test
- **Description:** Run full test suite to confirm no regressions. Run the diff tests multiple times to confirm determinism.
- **Verification:** `uv run pytest tests/context/ -v` passes consistently
- **Size:** XS
- **Dependencies:** Task 1

## Execution Order
1. Task 1 (the fix)
2. Task 2 (validation)

## Duration Tracking
| Task | Size | Actual | Notes |
|------|------|--------|-------|
| 1 | S | -- | |
| 2 | XS | -- | |
