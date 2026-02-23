---
epic_id: "RAISE-247"
grounded_in: "Gemba of src/rai_cli/cli/main.py, src/rai_cli/cli/commands/memory.py (1797 lines), publish.py, release.py, base.py, discover.py"
---

# Epic Design: CLI Ontology Restructuring

## Affected Surface (Gemba)

| Module/File | Current State | Changes | Stays |
|-------------|--------------|---------|-------|
| `cli/main.py` (145 lines) | 10 group registrations + init | Add graph/pattern/signal groups, remove base/publish, add info/profile top-level | app callback, settings, version |
| `cli/commands/memory.py` (1797 lines) | 15 commands in one file | Split into graph.py (~1200 lines), pattern.py (~200 lines), signal.py (~150 lines). memory.py becomes backward-compat shim | All business logic (just re-routed) |
| `cli/commands/publish.py` (264 lines) | check + release commands | Merge into release.py | Logic moves, not deleted |
| `cli/commands/release.py` (89 lines) | list command only | Absorb publish commands → check + publish + list | list command |
| `cli/commands/base.py` (101 lines) | show command | Replace with top-level `rai info` | Package info logic |
| `cli/commands/profile.py` | show subcommand | Flatten to `rai profile` (no subcommand) | Profile loading logic |
| `cli/commands/discover.py` (532 lines) | scan + analyze + build + drift | Remove `build` (absorbed into graph build) | scan, analyze, drift |
| `cli/commands/adapters.py` | list + check | **UNCHANGED** | Everything |
| `cli/commands/session.py` | start + context + close | **UNCHANGED** | Everything |
| `cli/commands/skill.py` | list + validate + check-name + scaffold | **UNCHANGED** (registry integration in S7) | Commands |
| `cli/commands/backlog.py` | auth + pull + push + status | **UNCHANGED** | Everything |
| `skills_base/*.md` (22 skills) | Reference `rai memory *` | Mechanical find-replace to new commands | Skill logic |
| `CLAUDE.md` | CLI Quick Reference | Regenerate from `.raise/` source | Everything else |

## Target Components

| Component | Responsibility | Key Interface | Consumes | Produces |
|-----------|---------------|---------------|----------|----------|
| `graph.py` | Knowledge graph structure | `graph_app: typer.Typer` (7 commands) | memory module internals | Graph operations |
| `pattern.py` | Learned knowledge capture | `pattern_app: typer.Typer` (2 commands) | patterns.jsonl | Pattern records |
| `signal.py` | Process telemetry | `signal_app: typer.Typer` (1 unified command) | signal type + args | signals.jsonl entries |
| `memory.py` (shim) | Backward-compat aliases | `memory_app: typer.Typer` (deprecated) | User invocation | Deprecation warning + delegation |
| `release.py` (merged) | Release management | `release_app: typer.Typer` (3 commands) | Quality gates, changelog | Published releases |
| `SkillRegistry` | Skill ownership tracking | `load/save/register/diff` | `.raise/rai/skills/registry.json` | Registry state |

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

# signal.py — unified emit
signal_app = typer.Typer(name="signal", help="Process telemetry signals")

@signal_app.command("emit")
def emit_signal(
    signal_type: Annotated[str, typer.Argument(help="Signal type: work|session|calibration")],
    # ... rest of args vary by type, same as current emit-* commands
) -> None: ...

# memory.py (shim) — backward compatibility
@memory_app.command("query")
def memory_query_compat(*args, **kwargs):
    """Deprecated: use 'rai graph query' instead."""
    console.print("[yellow]DEPRECATED: use 'rai graph query'[/yellow]", stderr=True)
    return graph_query(*args, **kwargs)  # delegate

# Skill Registry (S7)
class RegistryEntry(BaseModel):
    name: str
    version: str
    ownership: Literal["framework", "custom", "org"]
    work_cycle: str | None = None
    path: Path
    installed_at: datetime

class SkillRegistry(BaseModel):
    entries: dict[str, RegistryEntry] = {}

    def register(self, name: str, entry: RegistryEntry) -> None: ...
    def unregister(self, name: str) -> None: ...
    def diff_against_base(self, base_dir: Path) -> list[SkillDrift]: ...

# main.py — registration changes
app.add_typer(graph_app, name="graph")        # NEW
app.add_typer(pattern_app, name="pattern")    # NEW
app.add_typer(signal_app, name="signal")      # NEW
app.add_typer(memory_app, name="memory")      # KEPT (backward compat shim)
# REMOVED: base_app, publish_app
# ADDED: app.command("info")(...), app.command("profile")(...)
```

## Migration Path

- **Backward compat:** All renamed commands get aliases in `memory_app` shim that print deprecation warning to stderr then delegate. Pattern: PAT-E-153.
- **Consumer changes:** Skills update via S8 mechanical sweep. `rai init` propagates to all IDE skill dirs.
- **Internal paths unchanged:** `.raise/rai/memory/index.json` keeps its path. CLI surface rename only.
- **Historical artifacts:** `work/`, `dev/`, `governance/` files keep old command names — they're records.

## What Does NOT Change

- `cli/commands/adapters.py` — E211, already well-bounded
- `cli/commands/session.py` — clean, single responsibility
- `cli/commands/skill.py` — clean (registry adds to it in S7, doesn't restructure)
- `cli/commands/backlog.py` — clean, single responsibility
- `.raise/rai/memory/` directory structure — internal storage paths unchanged
- All business logic in memory module — just re-routed to new command files
