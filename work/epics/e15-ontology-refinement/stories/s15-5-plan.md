# Implementation Plan: Architectural Context Query Helpers

## Overview
- **Story:** S15.5
- **Story Points:** 3 SP
- **Story Size:** S
- **Created:** 2026-02-08
- **Design:** `s15-5-design.md`

## Tasks

### Task 1: ArchitecturalContext model + helper methods on UnifiedQueryEngine
- **Description:** Add `ArchitecturalContext` Pydantic model to `context/query.py`. Add 4 helper methods to `UnifiedQueryEngine`: `find_domain_for()`, `find_layer_for()`, `find_constraints_for()`, `get_architectural_context()`. All use typed BFS via existing `get_neighbors(edge_types=...)`.
- **Files:**
  - `src/rai_cli/context/query.py` (modify — add model + methods)
  - `tests/context/test_query_helpers.py` (create — unit tests)
- **TDD Cycle:**
  - RED: Test `get_architectural_context("mod-memory")` returns populated `ArchitecturalContext`
  - RED: Test `find_domain_for("mod-memory")` returns `bc-ontology`
  - RED: Test `find_constraints_for("mod-memory")` returns guardrail nodes
  - RED: Test graceful None/empty for non-existent modules
  - GREEN: Implement helpers using two-hop traversal (module → BC → guardrails)
  - REFACTOR: Extract shared traversal logic if needed
- **Verification:** `pytest tests/context/test_query_helpers.py -v`
- **Size:** S
- **Dependencies:** None

### Task 2: CLI `rai memory context` subcommand
- **Description:** Add `context` subcommand to `memory_app` in `cli/commands/memory.py`. Accepts module ID argument. Formats output via Rich console (human default, `--format json` option). Calls `engine.get_architectural_context()` from Task 1.
- **Files:**
  - `src/rai_cli/cli/commands/memory.py` (modify — add `context` command)
  - `tests/cli/commands/test_memory_context.py` (create — CLI tests)
- **TDD Cycle:**
  - RED: Test CLI command exits 0 and outputs module/domain/layer/constraints
  - RED: Test `--format json` outputs valid JSON with ArchitecturalContext fields
  - RED: Test non-existent module produces helpful error
  - GREEN: Implement command using `UnifiedQueryEngine.get_architectural_context()`
  - REFACTOR: Ensure output formatting consistent with existing `query` command
- **Verification:** `pytest tests/cli/commands/test_memory_context.py -v`
- **Size:** S
- **Dependencies:** Task 1

### Task 3: Manual Integration Test
- **Description:** Rebuild graph, run `rai memory context mod-memory` against real data. Verify output shows domain (bc-ontology), layer, and constraint guardrails. Test with a module that has no domain to verify graceful handling.
- **Verification:** Demo working command with real graph data
- **Size:** XS
- **Dependencies:** Task 1, Task 2

## Execution Order
1. Task 1 — Helpers + unit tests (foundation)
2. Task 2 — CLI command + tests (depends on Task 1)
3. Task 3 — Integration validation (depends on all)

## Risks
- Two-hop traversal (module → BC → guardrails) may miss modules not linked to a BC: Mitigation — `find_constraints_for` returns empty list, not error
- Graph may not be rebuilt with latest schema: Mitigation — integration test rebuilds first

## Duration Tracking
| Task | Size | Actual | Notes |
|------|------|--------|-------|
| 1 | S | -- | |
| 2 | S | -- | |
| 3 | XS | -- | Integration test |
