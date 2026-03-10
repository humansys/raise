---
story_id: "S247.3"
title: "Create signal group"
epic_ref: "RAISE-247"
phase: "plan"
status: "approved"
created: "2026-02-23"
---

# Implementation Plan: S247.3 — Create `signal` group

## Overview

- **Story:** S247.3
- **Size:** S
- **Tasks:** 3 (T1 canonical, T2 shims, T3 integration)
- **Derived from:** `design.md` § Target Interfaces + Gemba
- **Created:** 2026-02-23

---

## Tasks

### Task 1: Create `signal.py` with 3 canonical commands + tests

**Objective:** New `cli/commands/signal.py` with `emit_work`, `emit_session`, `emit_calibration` — canonical home for telemetry signals.

**RED — Write Failing Tests:**
- **File:** `tests/cli/commands/test_signal.py` (CREATE)
- **Test class:** `TestSignalEmitWork`, `TestSignalEmitSession`, `TestSignalEmitCalibration`
- **Key scenarios (from story.md § AC):**

```python
# emit-work happy path
def test_emit_work_start(tmp_path):
    # Given: telemetry dir exists
    # When: runner.invoke(app, ["signal", "emit-work", "story", "S247.3", "-e", "start"])
    # Then: exit_code == 0, "started" in result.stdout, "Story S247.3" in result.stdout

# emit-session happy path
def test_emit_session_basic(tmp_path):
    # When: runner.invoke(app, ["signal", "emit-session", "--type", "story", "--outcome", "success"])
    # Then: exit_code == 0, "Session event recorded" in result.stdout

# emit-calibration happy path
def test_emit_calibration_basic(tmp_path):
    # When: runner.invoke(app, ["signal", "emit-calibration", "S247.3", "--size", "S", "--estimated", "30", "--actual", "22"])
    # Then: exit_code == 0, "Calibration event recorded" in result.stdout
```

**GREEN — Implement:**
- **File:** `src/rai_cli/cli/commands/signal.py` (CREATE)
- **Signatures (from design.md § Target Interfaces):**

```python
signal_app = typer.Typer(name="signal", help="Emit lifecycle and telemetry signals", no_args_is_help=True)

def emit_work(work_type: str, work_id: str, event_type: str = "start",
              phase: str = "design", blocker: str = "", session: str | None = None) -> None: ...

def emit_session(session_type: str = "story", outcome: str = "success",
                 duration: int = 0, stories: str = "",
                 session: str | None = None) -> None: ...

def emit_calibration(story: str, size: str = "S", estimated: int = 0,
                     actual: int = 0, session: str | None = None) -> None: ...
```

- **Imports:** `cli_error`, `resolve_session_id_optional`, `CalibrationEvent`, `SessionEvent`, `WorkLifecycle`, `emit`
- **MUST NOT import** `get_memory_dir_for_scope` — not needed (design.md § Constraints)
- **Body:** copy from `memory.py:549–998`, rename Python functions, point decorators at `signal_app`

**Verification:**
```bash
pytest tests/cli/commands/test_signal.py -v
ruff check src/rai_cli/cli/commands/signal.py
pyright src/rai_cli/cli/commands/signal.py
```

**Size:** S
**Dependencies:** None
**AC Reference:** Scenarios "emit-work via new canonical command", "emit-session", "emit-calibration" (story.md)

---

### Task 2: Register `signal_app` in `main.py` + convert `memory.py` emit-* to shims

**Objective:** `rai signal` group live in CLI; `rai memory emit-*` delegate with deprecation warning. Tests verify message format (PAT from S247.2 retro).

**RED — Write Failing Tests (shims):**
- **File:** `tests/cli/commands/test_memory.py` (MODIFY — add class at end)
- **Test class:** `TestMemoryEmitSignalShims`

```python
class TestMemoryEmitSignalShims:
    """Tests for rai memory emit-* deprecation shims (extracted to signal group)."""

    def test_emit_work_deprecation_warning(self, tmp_path):
        # Given: telemetry dir, When: rai memory emit-work story S1 -e start
        # Then: exit_code == 0
        #       "DEPRECATED" in result.output
        #       "rai signal emit-work" in result.output  ← format check (not "rai memory")

    def test_emit_session_deprecation_warning(self, tmp_path):
        # When: rai memory emit-session --type story --outcome success
        # Then: "rai signal emit-session" in result.output

    def test_emit_calibration_deprecation_warning(self, tmp_path):
        # When: rai memory emit-calibration S1 --size S --estimated 30 --actual 22
        # Then: "rai signal emit-calibration" in result.output
```

**GREEN — Implement:**
- **`main.py`:** add `from rai_cli.cli.commands.signal import signal_app` + `app.add_typer(signal_app, name="signal")`
- **`memory.py`:** replace the 3 full implementations with thin shims:

```python
@memory_app.command("emit-work")
def emit_work(...) -> None:
    """Deprecated: use 'rai signal emit-work'."""
    _deprecation_warning("emit-work", "signal")
    from rai_cli.cli.commands.signal import emit_work as _f
    _f(work_type=work_type, work_id=work_id, event_type=event_type,
       phase=phase, blocker=blocker, session=session)

# same pattern for emit-session → emit_session, emit-calibration → emit_calibration
```

- **`memory.py` dead imports cleanup (arch review R1):** Remove imports that only the emit-* bodies used:
  - `from datetime import UTC, datetime` → delete line
  - `Literal` from `from typing import Annotated, Literal` → keep only `Annotated`
  - `CalibrationEvent, SessionEvent, WorkLifecycle` from `telemetry.schemas` → delete block
  - `emit` from `telemetry.writer` → delete line
  - `resolve_session_id_optional` from `session.resolver` → delete line
  - **Keep:** `get_personal_dir` (used by add-session), `Annotated` (used by add-calibration/add-session)

**Verification:**
```bash
pytest tests/cli/commands/test_memory.py::TestMemoryEmitSignalShims -v
# confirm existing emit-work/session/calibration tests still pass (they call memory, which delegates)
pytest tests/cli/commands/test_memory.py -k "emit" -v
ruff check src/rai_cli/cli/commands/memory.py src/rai_cli/cli/main.py
pyright src/rai_cli/cli/commands/memory.py src/rai_cli/cli/main.py
```

**Size:** S
**Dependencies:** T1 (signal.py must exist before shims can import from it)
**AC Reference:** Scenarios "backward-compat alias", "deprecation message format" (story.md)

---

### Task 3: Integration Verification

**Objective:** Validate end-to-end: full gate suite passes, `rai signal` works in real CLI.

**Verification:**
```bash
# Full gate
pytest --cov=rai_cli --cov-report=term-missing -q
ruff check .
pyright

# Manual smoke (3 canonical + 3 shims)
rai signal emit-work story S247.3 --event start --phase design
rai signal emit-session --type story --outcome success --duration 30
rai signal emit-calibration S247.3 --size S --estimated 45 --actual 30
rai memory emit-work story S247.3 --event start          # must show DEPRECATED + rai signal emit-work
rai memory emit-session --type story --outcome success   # must show DEPRECATED + rai signal emit-session
rai memory emit-calibration S247.3 -s S -e 45 -a 30     # must show DEPRECATED + rai signal emit-calibration
```

**Size:** XS
**Dependencies:** T1, T2

---

## Execution Order

```
T1 (signal.py canonical) → T2 (main.py + shims) → T3 (integration)
```

Sequential. T2 imports from T1 (shim delegates to signal.py). T3 validates both.

## Duration Tracking

| Task | Size | Actual | Notes |
|------|------|--------|-------|
| T1: signal.py + tests | S | — | |
| T2: main.py + shims + tests | S | — | |
| T3: integration | XS | — | |

## Risks

- **Typer app registration order**: `signal` must appear before `memory` in `main.py` additions? No — Typer order is alphabetical in help output, registration order doesn't matter functionally.
- **`result.output` vs `result.stdout`**: deprecation goes to stderr via `_stderr_console`. Existing shim tests use `result.output` which captures both. Confirm runner is `CliRunner(mix_stderr=True)` (default).
