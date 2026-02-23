---
story_id: "S247.2"
title: "Create pattern group"
epic_ref: "RAISE-247"
size: "S"
status: "draft"
created: "2026-02-23"
phase: "design"
---

# Design: S247.2 — Create pattern group

## 1. What & Why

**Problem:** `rai memory` is a god object mixing graph structure commands (already extracted in S247.1) with pattern-write commands (`add-pattern`, `reinforce`). These live in the wrong namespace — pattern management is a separate concern from graph querying.

**Value:** Users get `rai pattern add` and `rai pattern reinforce` as first-class commands with a coherent namespace. Reduces memory.py by ~200 lines. Pattern from S247.1 repeats without novelty.

## 2. Approach

Same extraction pattern as S247.1:

1. **Create** `src/rai_cli/cli/commands/pattern.py` — canonical `add` + `reinforce` commands (extracted from memory.py)
2. **Register** `pattern_app` in `main.py`
3. **Shim** memory.py: replace `add-pattern` and `reinforce` command bodies with `_deprecation_warning("add-pattern", "pattern")` + delegation to `pattern_app` functions

**Components affected:**
- `src/rai_cli/cli/commands/pattern.py` — CREATE (new canonical home)
- `src/rai_cli/cli/commands/memory.py` — MODIFY (2 commands → 2 shims)
- `src/rai_cli/cli/main.py` — MODIFY (register pattern_app)
- `tests/cli/commands/test_pattern.py` — CREATE (new test file)

## 3. Gemba: Current State

| File | Current Interface | What Changes | What Stays |
|------|------------------|--------------|------------|
| `memory.py:303` | `reinforce_cmd(pattern_id, vote, story_id, scope, memory_dir)` | Body moves to pattern.py; shim stays | Signature, decorator |
| `memory.py:401` | `add_pattern(content, context, sub_type, learned_from, scope, memory_dir)` | Body moves to pattern.py; shim stays | Signature, decorator |
| `memory.py:67` | `_deprecation_warning(old_cmd, new_group="graph")` | Called with `new_group="pattern"` | Function itself stays in memory.py |
| `main.py:51` | `app.add_typer(graph_app, name="graph")` | Add pattern_app line after graph | graph line unchanged |

**Observation:** `_deprecation_warning` is in memory.py and used by graph shims there already. Pattern shims will also call it with `new_group="pattern"`. No need to move or share it — memory.py is the shim layer.

## 4. Target Interfaces

### New file: `pattern.py`

```python
pattern_app = typer.Typer(
    name="pattern",
    help="Manage learned patterns",
    no_args_is_help=True,
)

@pattern_app.command("add")
def add_pattern(
    content: Annotated[str, typer.Argument(...)],
    context: Annotated[str, typer.Option("--context", "-c", ...)] = "",
    sub_type: Annotated[str, typer.Option("--type", "-t", ...)] = "process",
    learned_from: Annotated[str | None, typer.Option("--from", "-f", ...)] = None,
    scope: Annotated[str, typer.Option("--scope", "-s", ...)] = "project",
    memory_dir: Annotated[Path | None, typer.Option("--memory-dir", "-m", ...)] = None,
) -> None: ...

@pattern_app.command("reinforce")
def reinforce_cmd(
    pattern_id: Annotated[str, typer.Argument(...)],
    vote: Annotated[int, typer.Option("--vote", "-v", ...)],
    story_id: Annotated[str | None, typer.Option("--from", "-f", ...)] = None,
    scope: Annotated[str, typer.Option("--scope", "-s", ...)] = "project",
    memory_dir: Annotated[Path | None, typer.Option("--memory-dir", "-m", ...)] = None,
) -> None: ...
```

### Shims in `memory.py`

```python
@memory_app.command("add-pattern")
def add_pattern(...) -> None:
    """Deprecated: use 'rai pattern add'."""
    _deprecation_warning("add-pattern", "pattern")
    from rai_cli.cli.commands.pattern import add_pattern as pattern_add
    pattern_add(content=content, context=context, ...)

@memory_app.command("reinforce")
def reinforce_cmd(...) -> None:
    """Deprecated: use 'rai pattern reinforce'."""
    _deprecation_warning("reinforce", "pattern")
    from rai_cli.cli.commands.pattern import reinforce_cmd as pattern_reinforce
    pattern_reinforce(pattern_id=pattern_id, vote=vote, ...)
```

### Registration in `main.py`

```python
from rai_cli.cli.commands.pattern import pattern_app
# ...
app.add_typer(pattern_app, name="pattern")  # after graph_app line
```

### Integration Points
- `add_pattern()` calls `append_pattern()` from `rai_cli.memory` (same as today)
- `reinforce_cmd()` calls `reinforce_pattern()` from `rai_cli.memory` (same as today)
- `memory.py` shims delegate to `pattern.py` functions (same delegation pattern as graph shims)

## 5. Acceptance Criteria

See: `story.md` § Acceptance Criteria

## 6. Constraints

- `_deprecation_warning` stays in `memory.py` — it is used by all shims there; pattern.py has no need for it
- `pattern list` is explicitly **out of scope** — `graph list --types pattern` covers it
- Shim signatures must be **identical** to canonical signatures (keyword-arg delegation, same as S247.1)
- No business logic in shims — body is: deprecation warning + delegate
