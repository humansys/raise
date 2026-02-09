# Implementation Plan: S16.2 Graph Diff Engine

## Overview
- **Story:** S16.2
- **Size:** M
- **Created:** 2026-02-09
- **Design:** `work/epics/e16-incremental-coherence/stories/s16.2-graph-diff-engine/design.md`

## Tasks

### Task 1: Models + Pure diff function
- **Description:** Create `context/diff.py` with `NodeChange`, `GraphDiff` Pydantic models and `diff_graphs(old, new)` pure function. Compare nodes by `content`, `type`, `metadata` only. Derive `affected_modules` from module-type changes. Classify impact as `none`/`module`/`architectural`. Generate deterministic summary string.
- **Files:**
  - Create: `src/raise_cli/context/diff.py`
  - Create: `tests/context/test_diff.py`
- **TDD Cycle:**
  - RED: Tests for added/removed/modified nodes, impact classification, affected_modules derivation, empty graphs, identical graphs
  - GREEN: Implement models and `diff_graphs()`
  - REFACTOR: Clean up
- **Verification:** `pytest tests/context/test_diff.py -v`
- **Size:** M
- **Dependencies:** None

### Task 2: CLI integration (`--no-diff` flag + build wiring)
- **Description:** Modify `raise memory build` to: (1) load old graph before building, (2) diff after build, (3) save diff to `.raise/rai/personal/last-diff.json`, (4) print summary. Add `--no-diff` flag to skip. Update `_format_build_result` or add new output for diff summary.
- **Files:**
  - Modify: `src/raise_cli/cli/commands/memory.py`
  - Create: `tests/cli/commands/test_memory_build_diff.py`
- **TDD Cycle:**
  - RED: Test build with diff (mocked builder), test `--no-diff` skips, test first build (no old graph), test diff persisted to correct path
  - GREEN: Wire into build command
  - REFACTOR: Clean up
- **Verification:** `pytest tests/cli/commands/test_memory_build_diff.py -v`
- **Size:** S
- **Dependencies:** Task 1

### Task 3: Export from context module
- **Description:** Add `diff_graphs`, `GraphDiff`, `NodeChange` to `context/__init__.py` `__all__` exports.
- **Files:**
  - Modify: `src/raise_cli/context/__init__.py`
- **TDD Cycle:** N/A — wiring only
- **Verification:** `python -c "from raise_cli.context import diff_graphs, GraphDiff, NodeChange"`
- **Size:** XS
- **Dependencies:** Task 1

### Task 4: Integration test against real graph
- **Description:** Build the real raise-commons graph, make a minor change (add a fake node), rebuild, verify diff detects it accurately. This validates against real data, not mocked fixtures.
- **Files:**
  - Create: `tests/context/test_diff_integration.py`
- **TDD Cycle:**
  - RED: Test that diffing two real graphs produces correct change detection
  - GREEN: Should pass with existing implementation
  - REFACTOR: N/A
- **Verification:** `pytest tests/context/test_diff_integration.py -v`
- **Size:** S
- **Dependencies:** Task 1

### Task 5: Quality gates + manual integration test
- **Description:** Run full quality suite. Then manually run `raise memory build` twice — once to establish baseline, once after a trivial change — verify diff output and persisted file.
- **Verification:**
  - `uv run ruff check src/raise_cli/context/diff.py`
  - `uv run pyright src/raise_cli/context/diff.py`
  - `uv run pytest tests/context/test_diff.py tests/context/test_diff_integration.py tests/cli/commands/test_memory_build_diff.py --cov=raise_cli.context.diff -v`
  - Manual: `uv run raise memory build` end-to-end
- **Size:** S
- **Dependencies:** Tasks 1-4

## Execution Order
1. Task 1 — models + diff function (foundation)
2. Task 3 — module exports (trivial, unblocks imports)
3. Task 2 — CLI wiring (depends on Task 1)
4. Task 4 — integration test (depends on Task 1)
5. Task 5 — quality gates + manual validation (final)

## Risks
- **Metadata comparison noise:** `dict` comparison may be sensitive to key ordering → Pydantic `model_dump()` should produce consistent ordering, but test with real data (Task 4) validates this.
- **Large graph performance:** 345 nodes is small, but test anyway — `diff_graphs` should complete in <100ms.

## Duration Tracking
| Task | Size | Actual | Notes |
|------|------|--------|-------|
| 1 | M | -- | |
| 2 | S | -- | |
| 3 | XS | -- | |
| 4 | S | -- | |
| 5 | S | -- | |
