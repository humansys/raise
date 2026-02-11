# Implementation Plan: S15.4 Edge-Type Filtering

## Overview
- **Story:** S15.4
- **Story Points:** 2 SP
- **Story Size:** XS
- **Created:** 2026-02-08
- **Design:** `s15-4-design.md`

## Tasks

### Task 1: Add edge_types to query model + engine
- **Description:** Add `edge_types: list[EdgeType] | None = None` field to `UnifiedQuery`. Thread it through `_concept_lookup()` to `graph.get_neighbors()`. Tests for filtered and unfiltered queries.
- **Files:**
  - `src/rai_cli/context/query.py` — Add field to `UnifiedQuery`, pass in `_concept_lookup()`
  - `tests/context/test_query.py` — Tests for edge-type filtering in concept_lookup
- **TDD Cycle:** RED (test concept_lookup with edge_types filter) → GREEN (add field + thread param) → REFACTOR
- **Verification:** `pytest tests/context/test_query.py -v`
- **Size:** S
- **Dependencies:** None

### Task 2: Add --edge-types CLI option + integration test
- **Description:** Add `--edge-types` option to `rai memory query` command. Parse comma-separated edge types (same pattern as `--types`). Passes to `UnifiedQuery.edge_types`. Integration test with CLI runner.
- **Files:**
  - `src/rai_cli/cli/commands/memory.py` — Add `--edge-types` option to `query` command
  - `tests/cli/commands/test_memory.py` — CLI integration test for `--edge-types`
- **TDD Cycle:** RED (CLI test with --edge-types flag) → GREEN (add option + parsing) → REFACTOR
- **Verification:** `pytest tests/cli/commands/test_memory.py -v -k edge_type`
- **Size:** S
- **Dependencies:** Task 1

## Execution Order
1. Task 1 — model + engine (foundation)
2. Task 2 — CLI (depends on Task 1)

## Risks
- None significant. All three layers (graph, engine, CLI) follow established patterns. Graph layer already tested.

## Duration Tracking
| Task | Size | Actual | Notes |
|------|------|--------|-------|
| 1 | S | -- | |
| 2 | S | -- | |
