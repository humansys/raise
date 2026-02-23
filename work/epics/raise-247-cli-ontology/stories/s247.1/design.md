---
story_id: "S247.1"
title: "Create graph group"
epic_ref: "RAISE-247"
phase: "design"
status: "approved"
created: "2026-02-23"
complexity: "moderate"
---

# Design: Create `graph` group

## 1. What & Why

**Problem:** `rai memory` is a God Object with 15 commands spanning 4 bounded contexts
(graph structure, patterns, signals, deprecated). Agents can't discover commands by domain.

**Value:** Extract the 7 graph-structure commands into `rai graph`, establishing the
extraction pattern that S2-S3 will replicate. Backward-compat aliases ensure zero
breakage until the S6 skill sweep.

## 2. Approach

1. Create `src/rai_cli/cli/commands/graph.py` with 7 commands + all their private helpers
2. Register `graph_app` in `main.py`
3. Replace the 7 commands in `memory.py` with thin wrapper functions that print a
   deprecation warning to stderr and forward all args to the real function in `graph.py`
4. Each wrapper has the **same Typer signature** as the original (type-safe, --help works)
5. A shared `_deprecation_warning(cmd)` helper prints the warning
6. Create new tests in `test_graph.py`; adapt existing memory tests for deprecation verification
7. Rename dedicated test files: `test_memory_context.py` → `test_graph_context.py`, etc.

## 3. Gemba: Current State

| File | Current Interface | What Changes | What Stays |
|------|------------------|--------------|------------|
| `src/rai_cli/cli/commands/memory.py` (1797 lines) | 15 commands on `memory_app`, 10 private helpers | 7 commands + 10 helpers extracted to graph.py; replaced with 7 thin wrappers | 8 commands (add-pattern, reinforce, add-calibration, add-session, emit-work, emit-session, emit-calibration, generate) |
| `src/rai_cli/cli/main.py` | Registers `memory_app` | Add `graph_app` registration | All existing registrations |
| `tests/cli/commands/test_memory.py` | Tests for all memory commands | Remove graph-specific tests, add deprecation wrapper tests | Tests for non-graph commands |
| `tests/cli/commands/test_memory_context.py` | Tests for `memory context` | Rename to `test_graph_context.py`, update invocations | Test logic |
| `tests/cli/commands/test_memory_viz.py` | Tests for `memory viz` | Rename to `test_graph_viz.py`, update invocations | Test logic |
| `tests/cli/commands/test_memory_build_diff.py` | Tests for `memory build` diff | Rename to `test_graph_build_diff.py`, update invocations | Test logic |

### Commands to Extract (7)

| Command | Function | Lines | Private Helpers |
|---------|----------|-------|-----------------|
| `query` | `query()` | 89-219 | `_format_markdown()`, `_format_compact()`, `_format_json()` |
| `context` | `context_cmd()` | 343-441 | `_format_context_json()`, `_print_context_human()` |
| `build` | `build()` | 477-552 | `_format_build_result()` |
| `validate` | `validate()` | 590-689 | `_detect_cycles()` |
| `extract` | `extract()` | 729-857 | — |
| `list` | `list_memory()` | 864-1002 | `_format_concepts_markdown()`, `_print_concepts_table()` |
| `viz` | `viz()` | 1010-1060 | — |

### Shared Utilities

| Utility | Location | Used By |
|---------|----------|---------|
| `_get_default_index_path()` | Moves to graph.py | graph commands + memory wrappers (import from graph) |
| `MEMORY_TYPES` | Inlined in `list_graph()` | Single-use, no constant needed (arch review Q1) |
| `INDEX_FILE` | Moves to graph.py | `_get_default_index_path()` |
| `console` | Both files get own instance | Independent |

## 4. Target Interfaces

### New: `src/rai_cli/cli/commands/graph.py`

```python
graph_app = typer.Typer(
    name="graph",
    help="Build, query, and manage the knowledge graph",
    no_args_is_help=True,
)

# 7 commands — same signatures as current memory.py
# Note: _deprecation_warning lives in memory.py only (arch review R1)
def query(query_str: str, format: str = "human", ...) -> None: ...
def context_cmd(module_id: str, format: str = "human") -> None: ...
def build(output: Path | None = None, no_diff: bool = False) -> None: ...
def validate(index_file: Path | None = None) -> None: ...
def extract(file_path: Path | None = None, format: str = "human") -> None: ...
def list_graph(format: str = "table", ...) -> None: ...  # renamed from list_memory
def viz(output: Path | None = None, ...) -> None: ...

# All 10 private helpers move here intact
```

### Modified: `src/rai_cli/cli/commands/memory.py`

```python
# After extraction: ~400 lines (down from 1797)
# Keeps: generate, add-pattern, reinforce, add-calibration, add-session,
#        emit-work, emit-session, emit-calibration
# Adds: 7 thin deprecation wrappers

def _deprecation_warning(old_cmd: str, new_group: str = "graph") -> None:
    """Print deprecation warning to stderr."""
    console.print(
        f"[yellow]DEPRECATED:[/yellow] 'rai memory {old_cmd}' → "
        f"use 'rai {new_group} {old_cmd}' instead",
        stderr=True,
    )

@memory_app.command()
def build(output: ..., no_diff: ...) -> None:
    """Deprecated: use 'rai graph build'."""
    _deprecation_warning("build")
    from rai_cli.cli.commands.graph import build as graph_build
    graph_build(output=output, no_diff=no_diff)

# ... same pattern for all 7 commands
```

### Modified: `src/rai_cli/cli/main.py`

```python
from rai_cli.cli.commands.graph import graph_app
# Add alongside existing registrations:
app.add_typer(graph_app, name="graph")
```

### Integration Points

- `graph_app` registered in `main.py` → appears in `rai --help`
- `memory_app` wrappers import from `graph.py` → lazy import to avoid circular deps
- `_get_default_index_path()` shared via import from graph.py
- No changes to library layer (`rai_cli.context`, `rai_cli.governance`, etc.)

## 5. Acceptance Criteria

See: `story.md` § Acceptance Criteria

## 6. Constraints

- **MUST** preserve exact CLI behavior (same args, same output, same exit codes)
- **MUST** print deprecation warning to stderr (not stdout) so piped output isn't affected
- **MUST NOT** change any library-layer code — this is purely CLI restructuring
- **SHOULD** keep wrappers minimal (< 5 lines each excluding signature)
- **MUST** update hint messages in graph.py to say `'rai graph ...'` not `'raise memory ...'` (arch review Q3)

## 7. Architecture Review Resolutions

| Finding | Resolution |
|---------|-----------|
| R1: `_deprecation_warning` in graph.py unnecessary | Removed — lives only in memory.py |
| Q1: `MEMORY_TYPES` location | Inlined in `list_graph()` — single-use, no constant needed |
| Q3: Hint messages say `raise memory` | Updated to `rai graph` in graph.py during extraction |
