# Implementation Plan: S247.2 — Create pattern group

## Overview
- **Story:** S247.2
- **Size:** S
- **Tasks:** 3
- **Derived from:** design.md § Target Interfaces + Gemba
- **Created:** 2026-02-23

---

## Tasks

### Task 1: Create test_pattern.py + canonical pattern.py (TDD)

**Objective:** Create `tests/cli/commands/test_pattern.py` (RED), then implement `src/rai_cli/cli/commands/pattern.py` (GREEN).

**RED — Write Failing Tests:**
- **File:** `tests/cli/commands/test_pattern.py`
- **Test classes:**
  - `TestPatternAddCommand` — canonical `rai pattern add`
  - `TestPatternReinforceCommand` — canonical `rai pattern reinforce`

```python
# Test sketch — add
def test_add_pattern_basic(tmp_path):
    # Given: patterns dir exists
    # When: rai pattern add "some insight" --context "testing" --type technical
    # Then: exit_code == 0, output contains pattern ID, JSONL file created

def test_add_pattern_invalid_type(tmp_path):
    # When: --type invalid
    # Then: exit_code != 0, error message

def test_add_pattern_invalid_scope(tmp_path):
    # When: --scope invalid
    # Then: exit_code != 0, error message

# Test sketch — reinforce
def test_reinforce_pattern_basic(tmp_path):
    # Given: patterns.jsonl with PAT-E-001
    # When: rai pattern reinforce PAT-E-001 --vote 1
    # Then: exit_code == 0, output contains positives/evaluations

def test_reinforce_invalid_vote(tmp_path):
    # When: --vote 2
    # Then: exit_code != 0

def test_reinforce_pattern_not_found(tmp_path):
    # When: PAT-NOT-EXIST --vote 1
    # Then: exit_code != 0

def test_reinforce_not_counted(tmp_path):
    # When: --vote 0 (N/A)
    # Then: exit_code == 0, "N/A (not counted)" in output
```

**GREEN — Implement:**
- **File:** `src/rai_cli/cli/commands/pattern.py`
- **Typer app:**
  ```python
  pattern_app = typer.Typer(name="pattern", help="Manage learned patterns", no_args_is_help=True)
  ```
- **Functions:**
  ```python
  @pattern_app.command("add")
  def add_pattern(content, context, sub_type, learned_from, scope, memory_dir) -> None: ...

  @pattern_app.command("reinforce")
  def reinforce_cmd(pattern_id, vote, story_id, scope, memory_dir) -> None: ...
  ```
- **Logic:** Move bodies of `memory.add_pattern` and `memory.reinforce_cmd` verbatim into pattern.py (same imports: `PatternInput`, `PatternSubType`, `ReinforceResult`, `append_pattern`, `reinforce_pattern`, `MemoryScope`, etc.)

**Verification:**
```bash
pytest tests/cli/commands/test_pattern.py -v
```

**Size:** S
**Dependencies:** None
**AC Reference:** Scenarios "Add pattern via new group", "Reinforce pattern via new group"

---

### Task 2: Register pattern_app in main.py + convert memory.py to shims

**Objective:** Wire `pattern_app` into the CLI and replace canonical bodies in `memory.py` with deprecation shims.

**No new tests needed:** Existing `TestMemoryAddPatternCommand` in `test_memory.py` validates delegation (shim passes through to canonical). Add 2 minimal shim tests to verify the deprecation warning appears on stderr.

**File 1:** `src/rai_cli/cli/main.py`
```python
from rai_cli.cli.commands.pattern import pattern_app   # add import
# ...
app.add_typer(pattern_app, name="pattern")  # after graph_app line
```

**File 2:** `src/rai_cli/cli/commands/memory.py`
- Replace `add_pattern` body (L449-502) with:
  ```python
  """Deprecated: use 'rai pattern add'."""
  _deprecation_warning("add-pattern", "pattern")
  from rai_cli.cli.commands.pattern import add_pattern as _add
  _add(content=content, context=context, sub_type=sub_type,
       learned_from=learned_from, scope=scope, memory_dir=memory_dir)
  ```
- Replace `reinforce_cmd` body (L334-398) with:
  ```python
  """Deprecated: use 'rai pattern reinforce'."""
  _deprecation_warning("reinforce", "pattern")
  from rai_cli.cli.commands.pattern import reinforce_cmd as _reinforce
  _reinforce(pattern_id=pattern_id, vote=vote, story_id=story_id,
             scope=scope, memory_dir=memory_dir)
  ```

**Shim tests to add in `test_memory.py`:**
```python
def test_add_pattern_deprecated_warning(tmp_path):
    # When: rai memory add-pattern "x"
    # Then: stderr contains "DEPRECATED" and "rai pattern add"

def test_reinforce_deprecated_warning(tmp_path):
    # Given: patterns.jsonl with PAT-E-001
    # When: rai memory reinforce PAT-E-001 --vote 1
    # Then: stderr contains "DEPRECATED" and "rai pattern reinforce"
```

**Verification:**
```bash
pytest tests/cli/commands/test_memory.py -v -k "deprecated"
pytest tests/cli/commands/test_pattern.py -v
pytest --tb=short
```

**Size:** S
**Dependencies:** T1
**AC Reference:** Scenarios "Backward compat for add-pattern", "Backward compat for reinforce"

---

### Task 3: Integration Verification

**Objective:** Validate full story end-to-end with running software.

**Manual smoke tests:**
```bash
# Canonical commands work
rai pattern add "test pattern S247.2" --context "cli,extraction" --type technical --from S247.2
rai pattern reinforce PAT-E-001 --vote 1 --from S247.2   # use a real PAT ID

# Backward compat works with warning
rai memory add-pattern "shim test" --context "test"   # should show DEPRECATED → rai pattern add
rai memory reinforce PAT-E-001 --vote 0               # should show DEPRECATED → rai pattern reinforce

# Help text correct
rai pattern --help
rai pattern add --help
rai pattern reinforce --help
```

**Gate:**
```bash
pytest --tb=short -q
ruff check .
pyright
```

**Size:** XS
**Dependencies:** T1, T2
**AC Reference:** All 4 scenarios

---

## Execution Order
1. T1 — Create test_pattern.py + pattern.py (TDD)
2. T2 — Register in main.py + shim memory.py (depends on T1)
3. T3 — Integration verification (depends on T1, T2)

## Risks
- `add_pattern` body in memory.py has different variable names at call sites — verify keyword delegation covers all params
- `reinforce_cmd` imports `wilson_lower_bound` and `SCORING_LOW_WILSON_THRESHOLD` — move these imports to pattern.py too

## Duration Tracking
| Task | Size | Actual | Notes |
|------|------|--------|-------|
| T1 | S | -- | |
| T2 | S | -- | |
| T3 | XS | -- | Integration verification |
