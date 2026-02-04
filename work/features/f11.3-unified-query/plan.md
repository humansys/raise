# Implementation Plan: F11.3 Unified Context Query

## Overview
- **Feature:** F11.3
- **Epic:** E11 Unified Context Architecture
- **Story Points:** 2 SP
- **Feature Size:** S
- **Created:** 2026-02-03

## Tasks

### Task 1: Query Module (Models + Engine)
- **Description:** Create `src/raise_cli/context/query.py` with:
  - `UnifiedQuery` model (query, strategy, max_depth, types)
  - `UnifiedQueryResult` model (concepts, metadata)
  - `UnifiedQueryMetadata` model (query, total, tokens, time, types_found)
  - `UnifiedQueryEngine` class with `from_file()` and `query()` methods
  - `keyword_search` strategy: case-insensitive content matching, relevance scoring
  - `concept_lookup` strategy: direct ID lookup + BFS via `get_neighbors()`
- **Files:**
  - `src/raise_cli/context/query.py` (create)
  - `src/raise_cli/context/__init__.py` (export new classes)
  - `tests/context/test_query.py` (create)
- **TDD Cycle:**
  - RED: Test `UnifiedQuery` model validation
  - GREEN: Implement model
  - RED: Test `keyword_search` returns matching concepts
  - GREEN: Implement keyword search with scoring
  - RED: Test `concept_lookup` with BFS neighbors
  - GREEN: Implement concept lookup using `get_neighbors()`
  - RED: Test type filtering
  - GREEN: Implement `types` filter
  - REFACTOR: Extract common scoring logic
- **Verification:** `pytest tests/context/test_query.py -v`
- **Size:** M
- **Dependencies:** None

### Task 2: CLI Integration
- **Description:** Add `--unified` flag to `raise context query` command:
  - When `--unified` is set, use `UnifiedQueryEngine` instead of `ContextQueryEngine`
  - Load graph from `.raise/graph/unified.json`
  - Reuse existing `--format`, `--max-depth` options
  - Add human-readable formatter for unified results
- **Files:**
  - `src/raise_cli/cli/commands/context.py` (modify)
  - `tests/cli/commands/test_context.py` (extend or create)
- **TDD Cycle:**
  - RED: Test `--unified` flag routes to unified engine
  - GREEN: Implement conditional engine selection
  - RED: Test human output format includes type grouping
  - GREEN: Implement unified result formatter
  - REFACTOR: Share formatting logic where possible
- **Verification:** `pytest tests/cli/commands/test_context.py -v`
- **Size:** S
- **Dependencies:** Task 1

### Task 3 (Final): Manual Integration Test
- **Description:** Validate feature works end-to-end:
  1. Build unified graph: `uv run raise graph build --unified`
  2. Query with keywords: `uv run raise context query "planning" --unified`
  3. Query with type filter: `uv run raise context query "pattern" --unified --types pattern`
  4. Query specific concept: `uv run raise context query "PAT-001" --unified --max-depth 2`
  5. JSON output: `uv run raise context query "skill" --unified --format json`
  6. Verify existing behavior unchanged: `uv run raise context query "req-rf-05"`
- **Verification:** All commands return expected results, no regressions
- **Size:** XS
- **Dependencies:** Task 1, Task 2

## Execution Order

1. **Task 1** — Query module (foundation, no dependencies)
2. **Task 2** — CLI integration (depends on Task 1)
3. **Task 3** — Manual integration test (validates everything)

## Risks

| Risk | Likelihood | Mitigation |
|------|:----------:|------------|
| Keyword search too slow | Low | Our graph is <200 nodes; optimize later if needed |
| Existing CLI tests break | Low | Isolated change with `--unified` flag |

## Duration Tracking

| Task | Size | Estimated | Actual | Notes |
|------|:----:|:---------:|:------:|-------|
| 1 | M | 30-45m | -- | |
| 2 | S | 15-25m | -- | |
| 3 | XS | 5-10m | -- | |
| **Total** | **S** | **50-80m** | -- | |
