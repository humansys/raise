---
story_id: "S247.3"
title: "Create signal group"
epic_ref: "RAISE-247"
phase: "design"
status: "approved"
created: "2026-02-23"
---

# Design: S247.3 — Create `signal` group

## 1. What & Why

**Problem:** The three telemetry emit commands (`emit-work`, `emit-session`, `emit-calibration`) live in the `memory` God Object alongside unrelated graph and pattern commands.

**Value:** Extracting them to `rai signal` completes M1 (God Object Decomposed) of RAISE-247: `memory` has 0 active commands, all commands live in their correct bounded context.

## 2. Approach

Same extraction pattern as S247.1 (graph) and S247.2 (pattern):

1. **Create** `src/rai_cli/cli/commands/signal.py` — canonical home for 3 commands
2. **Convert** memory.py implementations → shims (deprecation warning + delegate)
3. **Register** `signal_app` in `main.py`
4. **Update** tests in `tests/cli/commands/test_signal.py` (new) + shim tests in `test_memory.py`

Components touched:

| File | Change |
|------|--------|
| `src/rai_cli/cli/commands/signal.py` | CREATE — 3 canonical commands |
| `src/rai_cli/cli/commands/memory.py` | MODIFY — convert emit-* to shims |
| `src/rai_cli/cli/main.py` | MODIFY — register signal_app |
| `tests/cli/commands/test_signal.py` | CREATE — canonical command tests |
| `tests/cli/commands/test_memory.py` | MODIFY — add 3 shim tests |

## 3. Gemba: Current State

S-sized → file list + key names.

**Canonical implementations (to move):**
- `memory.py:548` — `emit_work()` → command `emit-work` (2 positional args, 4 options)
- `memory.py:710` — `emit_session_event()` → command `emit-session` (5 options)
- `memory.py:801` — `emit_calibration_event()` → command `emit-calibration` (1 arg, 4 options)

**Shim infrastructure (stays in memory.py):**
- `memory.py:57` — `_deprecation_warning(old_cmd, new_group, new_cmd=None)` — already used by graph and pattern shims

**Imports signal.py will need (confirmed from memory.py source):**
```python
from rai_cli.cli.error_handler import cli_error
from rai_cli.session.resolver import resolve_session_id_optional
from rai_cli.telemetry.schemas import CalibrationEvent, SessionEvent, WorkLifecycle
from rai_cli.telemetry.writer import emit
```

**IMPORTANT:** `get_memory_dir_for_scope` is NOT needed by emit-* commands — confirmed by reading source. (Known trap from S247.2 retro.)

## 4. Target Interfaces

### signal.py — new canonical commands

```python
signal_app = typer.Typer(name="signal", help="Emit lifecycle and telemetry signals", no_args_is_help=True)

@signal_app.command("emit-work")
def emit_work(work_type: str, work_id: str, event_type: str = "start",
              phase: str = "design", blocker: str = "", session: str | None = None) -> None:
    """Emit a work lifecycle event for Lean flow analysis."""

@signal_app.command("emit-session")
def emit_session(session_type: str = "story", outcome: str = "success",
                 duration: int = 0, stories: str = "",
                 session: str | None = None) -> None:
    """Emit a session event to telemetry."""

@signal_app.command("emit-calibration")
def emit_calibration(story: str, size: str = "S", estimated: int = 0,
                     actual: int = 0, session: str | None = None) -> None:
    """Emit a calibration event to telemetry."""
```

**Decision (approved):** Function names normalized — `emit_session` / `emit_calibration` instead of `emit_session_event` / `emit_calibration_event`. Internal names align with command names.

### memory.py shims (replace current implementations)

```python
@memory_app.command("emit-work")
def emit_work(...) -> None:
    """Deprecated: use 'rai signal emit-work'."""
    _deprecation_warning("emit-work", "signal")
    from rai_cli.cli.commands.signal import emit_work as _emit_work
    _emit_work(work_type=work_type, work_id=work_id, ...)

@memory_app.command("emit-session")
def emit_session_event(...) -> None:
    """Deprecated: use 'rai signal emit-session'."""
    _deprecation_warning("emit-session", "signal")
    from rai_cli.cli.commands.signal import emit_session as _emit_session
    _emit_session(...)

@memory_app.command("emit-calibration")
def emit_calibration_event(...) -> None:
    """Deprecated: use 'rai signal emit-calibration'."""
    _deprecation_warning("emit-calibration", "signal")
    from rai_cli.cli.commands.signal import emit_calibration as _emit_calibration
    _emit_calibration(...)
```

### main.py addition

```python
from rai_cli.cli.commands.signal import signal_app
app.add_typer(signal_app, name="signal")
```

## 5. Acceptance Criteria

See: `story.md` § Acceptance Criteria

## 6. Constraints

- **MUST NOT** add `get_memory_dir_for_scope` import to signal.py — not needed, confirmed in Gemba
- **MUST** test deprecation message format in automated tests (PAT from S247.2 retro): `"rai signal emit-work"` must appear in stderr output, not the old command name
- **MUST NOT** remove `add-calibration` / `add-session` from memory.py — deferred to S4
- All guardrails: types, ruff, pyright, coverage ≥90%, tests pass
