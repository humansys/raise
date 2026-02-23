# Implementation Plan: Create `graph` group

## Overview
- **Story:** S247.1
- **Size:** M
- **Tasks:** 5
- **Derived from:** design.md § Target Interfaces + § Gemba
- **Created:** 2026-02-23

## Tasks

### Task 1: Create graph.py with 7 commands + helpers

**Objective:** Extract the 7 graph commands and all 10 private helpers from memory.py into a new graph.py file. Update hint messages to say `rai graph`.

**RED — Write Failing Test:**
- **File:** `tests/cli/commands/test_graph.py`
- **Test function:** `test_graph_build_basic`, `test_graph_query_basic`
- **Setup:** Given a tmp project with a valid memory index
- **Action:** When I invoke `["graph", "build"]` or `["graph", "query", "testing"]`
- **Assertion:** Then exit_code == 0 and output contains expected content
```python
def test_graph_build_basic(self, tmp_path: Path) -> None:
    """Graph build works via new group."""
    result = runner.invoke(app, ["graph", "build", "--output", str(output)])
    assert result.exit_code == 0

def test_graph_query_basic(self, sample_unified_graph: Path, tmp_path: Path) -> None:
    """Graph query works via new group."""
    result = runner.invoke(app, ["graph", "query", "testing", "--index", str(graph)])
    assert result.exit_code == 0
```

**GREEN — Implement:**
- **File:** `src/rai_cli/cli/commands/graph.py`
- **Functions:** `graph_app`, `query()`, `context_cmd()`, `build()`, `validate()`, `extract()`, `list_graph()`, `viz()`
- **Helpers:** `_get_default_index_path()`, `_format_markdown()`, `_format_compact()`, `_format_json()`, `_format_build_result()`, `_detect_cycles()`, `_format_concepts_markdown()`, `_print_concepts_table()`, `_format_context_json()`, `_print_context_human()`
- **Details:**
  - Move all functions intact (same signatures, same logic)
  - `MEMORY_TYPES` inlined in `list_graph()` as literal `["pattern", "calibration", "session"]`
  - `INDEX_FILE` and `_get_default_index_path()` move to graph.py
  - Own `console = Console()` instance
  - Update all hint messages: `'raise memory build'` → `'rai graph build'`, etc.
  - Register `graph_app` in `main.py`

**Verification:**
```bash
pytest tests/cli/commands/test_graph.py -v
```

**Size:** M
**Dependencies:** None
**AC Reference:** Scenario "Graph commands work under new group" + "All 7 graph commands are available"

---

### Task 2: Replace extracted commands in memory.py with deprecation wrappers

**Objective:** Remove the 7 command implementations and 10 helpers from memory.py. Replace with thin wrappers that print deprecation warning to stderr and forward args to graph.py.

**RED — Write Failing Test:**
- **File:** `tests/cli/commands/test_memory.py` (modify existing)
- **Test function:** `test_memory_build_deprecated`, `test_memory_query_deprecated`
- **Setup:** Given a tmp project with a valid memory index
- **Action:** When I invoke `["memory", "build"]` or `["memory", "query", "testing"]`
- **Assertion:** Then exit_code == 0 AND output contains "DEPRECATED"
```python
class TestMemoryDeprecationWrappers:
    def test_memory_build_deprecated(self, tmp_path: Path) -> None:
        result = runner.invoke(app, ["memory", "build", "--output", str(out)])
        assert result.exit_code == 0
        assert "DEPRECATED" in result.output

    def test_memory_query_deprecated(self, sample_unified_graph, tmp_path) -> None:
        result = runner.invoke(app, ["memory", "query", "testing", "--index", str(g)])
        assert result.exit_code == 0
        assert "DEPRECATED" in result.output
```

**GREEN — Implement:**
- **File:** `src/rai_cli/cli/commands/memory.py`
- **Functions:**
  - Add `_deprecation_warning(old_cmd: str, new_group: str = "graph") -> None`
  - 7 thin wrappers with same Typer signatures, each calls `_deprecation_warning()` then lazy-imports and delegates to graph.py
- **Remove:** All 10 private helpers, all graph command implementations
- **Keep:** `generate`, `add-pattern`, `reinforce`, `add-calibration`, `add-session`, `emit-work`, `emit-session`, `emit-calibration` + their imports

**Verification:**
```bash
pytest tests/cli/commands/test_memory.py -v
```

**Size:** M
**Dependencies:** Task 1
**AC Reference:** Scenario "Backward-compat alias with deprecation warning"

---

### Task 3: Rename and update dedicated test files

**Objective:** Rename test files from `test_memory_*` to `test_graph_*` and update CLI invocations from `["memory", ...]` to `["graph", ...]`.

**RED — Already covered:** Renamed files test the graph commands directly via `["graph", ...]` invocation.

**GREEN — Implement:**
- `tests/cli/commands/test_memory_context.py` → `test_graph_context.py`
  - Update all `["memory", "context", ...]` → `["graph", "context", ...]`
  - Update class name `TestMemoryContextCommand` → `TestGraphContextCommand`
- `tests/cli/commands/test_memory_viz.py` → `test_graph_viz.py`
  - Update all `["memory", "viz", ...]` → `["graph", "viz", ...]`
  - Update class name `TestMemoryVizCommand` → `TestGraphVizCommand`
- `tests/cli/commands/test_memory_build_diff.py` → `test_graph_build_diff.py`
  - Update all `["memory", "build", ...]` → `["graph", "build", ...]`
  - Update mock path `rai_cli.cli.commands.memory.` → `rai_cli.cli.commands.graph.`
  - Update class names

**Verification:**
```bash
pytest tests/cli/commands/test_graph_context.py tests/cli/commands/test_graph_viz.py tests/cli/commands/test_graph_build_diff.py -v
```

**Size:** S
**Dependencies:** Task 1
**AC Reference:** Scenario "Graph commands work under new group"

---

### Task 4: Update test_memory.py — move graph tests to test_graph.py, keep non-graph tests

**Objective:** Move graph-specific test classes from test_memory.py to test_graph.py (updating invocations to `["graph", ...]`). Keep non-graph test classes in test_memory.py. Add deprecation wrapper tests.

**RED — Already covered:** Deprecation wrapper tests from Task 2. Graph tests moved to test_graph.py from Task 1.

**GREEN — Implement:**
- **Move to test_graph.py** (update invocations `"memory"` → `"graph"`):
  - `TestMemoryQueryCommand` → `TestGraphQueryCommand` (10 tests)
  - `TestMemoryListCommand` → `TestGraphListCommand` (6 tests)
  - `TestMemoryBuildCommand` → `TestGraphBuildCommand` (1 test)
  - `TestMemoryValidateCommand` → `TestGraphValidateCommand` (4 tests)
  - `TestMemoryQueryEdgeCases` → `TestGraphQueryEdgeCases` (1 test)
  - `TestMemoryListEdgeCases` → `TestGraphListEdgeCases` (1 test)
  - `TestMemoryQueryEdgeTypeFilter` → `TestGraphQueryEdgeTypeFilter` (3 tests)
  - Graph-related tests from `TestMemoryHelp` (build, validate, extract, list, query)
- **Keep in test_memory.py:**
  - `TestMemoryAddPatternCommand` (7 tests)
  - `TestMemoryAddCalibrationCommand` (6 tests)
  - `TestMemoryAddSessionCommand` (2 tests)
  - `TestMemoryEmitWorkCommand` (6 tests)
  - `TestEmitSessionRouting` (5 tests)
  - `TestMemoryEmitSessionCommand` (3 tests)
  - `TestMemoryEmitCalibrationCommand` (6 tests)
  - `TestMemoryGenerateCommand` (3 tests)
  - `sample_unified_graph` fixture (shared — duplicate in test_graph.py)
- **Add to test_memory.py:**
  - `TestMemoryDeprecationWrappers` (7 tests — one per wrapper)

**Verification:**
```bash
pytest tests/cli/commands/test_graph.py tests/cli/commands/test_memory.py -v
```

**Size:** M
**Dependencies:** Task 1, Task 2
**AC Reference:** All scenarios

---

### Task 5 (Final): Integration Verification

**Objective:** Validate story works end-to-end: full test suite passes, all 7 graph commands work, all 7 deprecation wrappers work, types + lint clean.

**Verification:**
```bash
# All tests pass
pytest tests/ -v

# Types clean
pyright src/rai_cli/cli/commands/graph.py src/rai_cli/cli/commands/memory.py

# Lint clean
ruff check src/rai_cli/cli/commands/graph.py src/rai_cli/cli/commands/memory.py

# Manual smoke test
rai graph --help
rai graph build --help
```

**Size:** S
**Dependencies:** All previous tasks

## Execution Order

1. **Task 1** — Create graph.py (foundation — all other tasks depend on this)
2. **Task 2** — Replace memory.py commands with wrappers (depends on T1)
3. **Task 3** — Rename dedicated test files (depends on T1, parallel with T2)
4. **Task 4** — Reorganize test_memory.py (depends on T1 + T2)
5. **Task 5** — Integration verification (final)

```
T1 (graph.py) → T2 (wrappers) → T4 (test reorg) → T5 (verify)
              ↘ T3 (rename tests) ↗
```

## Traceability

| AC Scenario | Task(s) | Design § |
|-------------|---------|----------|
| "Graph commands work under new group" | T1, T3, T4 | Target Interfaces → graph.py |
| "All 7 graph commands are available" | T1 | Target Interfaces → graph_app |
| "Backward-compat alias with deprecation warning" | T2, T4 | Target Interfaces → memory.py wrappers |
| "Registration in main CLI" | T1 | Target Interfaces → main.py |

## Risks

| Risk | Mitigation |
|------|-----------|
| Mock paths in test_memory_build_diff.py break after move | Update `@patch("rai_cli.cli.commands.memory.X")` → `"...graph.X"` in T3 |
| Shared fixture `sample_unified_graph` needed in both test files | Duplicate fixture in test_graph.py (simple, self-contained) |
| Import cleanup in memory.py — removing unused imports | pyright + ruff will catch unused imports in T5 |

## Duration Tracking

| Task | Size | Actual | Notes |
|------|------|--------|-------|
| T1: Create graph.py | M | -- | |
| T2: Deprecation wrappers | M | -- | |
| T3: Rename test files | S | -- | |
| T4: Reorganize test_memory.py | M | -- | |
| T5: Integration verification | S | -- | |
