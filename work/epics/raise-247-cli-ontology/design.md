---
epic_id: "RAISE-247"
grounded_in: "Gemba of src/rai_cli/cli/main.py, src/rai_cli/cli/commands/memory.py (1797 lines), publish.py, release.py, base.py, discover.py"
---

# Epic Design: CLI Ontology Restructuring

## Affected Surface (Gemba)

| Module/File | Current State | Changes | Stays |
|-------------|--------------|---------|-------|
| `cli/main.py` (145 lines) | 10 group registrations + init | Add graph/pattern/signal groups, remove base/publish, add info/profile top-level | app callback, settings, version |
| `cli/commands/memory.py` (1797 lines) | 15 commands in one file | Split into graph.py (~1200 lines), pattern.py (~200 lines), signal.py (~400 lines). memory.py becomes backward-compat shim | All business logic (just re-routed) |
| `cli/commands/publish.py` (264 lines) | check + release commands | Merge into release.py | Logic moves, not deleted |
| `cli/commands/release.py` (89 lines) | list command only | Absorb publish commands → check + publish + list | list command |
| `cli/commands/base.py` (101 lines) | show command | Replace with top-level `rai info` | Package info logic |
| `cli/commands/profile.py` | show subcommand | Flatten to `rai profile` (no subcommand) | Profile loading logic |
| `cli/commands/discover.py` (532 lines) | scan + analyze + build + drift | **UNCHANGED** (arch review R2: discover build stays) | Everything |
| `cli/commands/adapters.py` | list + check | **UNCHANGED** | Everything |
| `cli/commands/session.py` | start + context + close | **UNCHANGED** | Everything |
| `cli/commands/skill.py` | list + validate + check-name + scaffold | **UNCHANGED** | Commands |
| `cli/commands/backlog.py` | auth + pull + push + status | **UNCHANGED** | Everything |
| `skills_base/*.md` (22 skills) | Reference `rai memory *` | Mechanical find-replace to new commands | Skill logic |
| `CLAUDE.md` | CLI Quick Reference | Regenerate from `.raise/` source | Everything else |

## Target Components

| Component | Responsibility | Key Interface | Consumes | Produces |
|-----------|---------------|---------------|----------|----------|
| `graph.py` | Knowledge graph structure | `graph_app: typer.Typer` (7 commands) | memory module internals | Graph operations |
| `pattern.py` | Learned knowledge capture | `pattern_app: typer.Typer` (2 commands) | patterns.jsonl | Pattern records |
| `signal.py` | Process telemetry | `signal_app: typer.Typer` (3 subcommands) | signal args | signals.jsonl entries |
| `memory.py` (shim) | Backward-compat aliases | `memory_app: typer.Typer` (deprecated) | User invocation | Deprecation warning + delegation |
| `release.py` (merged) | Release management | `release_app: typer.Typer` (3 commands) | Quality gates, changelog | Published releases |

## Key Contracts

```python
# graph.py — commands extracted from memory.py
graph_app = typer.Typer(name="graph", help="Knowledge graph operations")

# Commands: build, validate, query, context, list, viz, extract
# Same signatures as current memory.py equivalents

# pattern.py — extracted from memory.py
pattern_app = typer.Typer(name="pattern", help="Manage learned patterns")

# Commands: add, reinforce
# Same signatures as current memory add-pattern, memory reinforce

# signal.py — 3 subcommands (arch review R1: no unification)
signal_app = typer.Typer(name="signal", help="Process telemetry signals")

@signal_app.command("emit-work")
def emit_work(...) -> None: ...  # Same signature as memory emit-work

@signal_app.command("emit-session")
def emit_session_event(...) -> None: ...  # Same signature as memory emit-session

@signal_app.command("emit-calibration")
def emit_calibration_event(...) -> None: ...  # Same signature as memory emit-calibration

# memory.py (shim) — backward compatibility via decorator helper
def _deprecated(new_group: str, new_cmd: str):
    """Decorator: prints deprecation warning to stderr, then delegates."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            console.print(
                f"[yellow]DEPRECATED: use 'rai {new_group} {new_cmd}'[/yellow]",
                stderr=True,
            )
            return func(*args, **kwargs)
        return wrapper
    return decorator

# main.py — registration changes
app.add_typer(graph_app, name="graph")        # NEW
app.add_typer(pattern_app, name="pattern")    # NEW
app.add_typer(signal_app, name="signal")      # NEW
app.add_typer(memory_app, name="memory")      # KEPT (backward compat shim)
# REMOVED: base_app, publish_app
# ADDED: app.command("info")(...), app.command("profile")(...)
```

## Migration Path

- **Backward compat:** All renamed commands get aliases in `memory_app` shim using `_deprecated()` decorator helper. Pattern: PAT-E-153.
- **Consumer changes:** Skills update via S6 mechanical sweep. `rai init` propagates to all IDE skill dirs.
- **Internal paths unchanged:** `.raise/rai/memory/index.json` keeps its path. CLI surface rename only.
- **Historical artifacts:** `work/`, `dev/`, `governance/` files keep old command names — they're records.

## What Does NOT Change

- `cli/commands/adapters.py` — E211, already well-bounded
- `cli/commands/session.py` — clean, single responsibility
- `cli/commands/skill.py` — clean, single responsibility
- `cli/commands/backlog.py` — clean, single responsibility
- `cli/commands/discover.py` — discover build stays (arch review R2)
- `.raise/rai/memory/` directory structure — internal storage paths unchanged
- All business logic in memory module — just re-routed to new command files
