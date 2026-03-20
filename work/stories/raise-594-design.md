# RAISE-594: Design — CLI Extension Mechanism

## Problem & Value

External packages (rai-agent) cannot register CLI commands under `rai` without modifying raise-commons. This blocks `rai knowledge` (E3 ScaleUp) and any future extension package.

## Approach

Dedicated `cli/extensions.py` module with a `discover_cli_extensions()` function following the project's established entry point discovery idiom (hooks/registry.py, gates/registry.py).

**Not** inline in `main.py` — consistency with project architecture, testability, and observability outweigh the simplicity of 6 inline lines.

**Not** a class — no state to maintain. `app.add_typer()` mutates the Typer app directly.

## Components

| Component | Change | Purpose |
|---|---|---|
| `src/raise_cli/cli/extensions.py` | **create** | Discovery function + ExtensionInfo return type |
| `src/raise_cli/cli/main.py` | **modify** | 2 lines: import + call |
| `tests/cli/test_extensions.py` | **create** | Unit tests for discovery |

## Design Decisions

### D1: Module-level function, not class

**Choice:** `discover_cli_extensions(app) -> list[ExtensionInfo]`
**Rationale:** No state to maintain — unlike hooks (priority, event filtering) or gates (lookup by ID), CLI extensions are fire-and-forget registration. A function is the simplest construct that serves the purpose.
**Alternatives:** Class registry (over-engineered for stateless registration), inline in main.py (untestable, inconsistent with project idiom).

### D2: Built-in name collision protection

**Choice:** Maintain `BUILTIN_COMMANDS` frozenset, reject extensions that conflict.
**Rationale:** Typer silently overwrites on duplicate `add_typer(name=...)`. A malicious or careless package could replace `rai session` or `rai backlog`. Detection + warning is the minimum safety net.
**Alternatives:** No protection (unsafe), runtime allow-list config (YAGNI).

### D3: Duplicate extension detection

**Choice:** Track registered names, first-wins with warning on duplicates.
**Rationale:** Follows GateRegistry pattern. Two packages registering `knowledge` should not silently race.
**Alternatives:** Last-wins (unpredictable), error/crash (too strict for extensions).

### D4: ExtensionInfo return type for observability

**Choice:** Return `list[ExtensionInfo]` with name, dist, status, reason.
**Rationale:** Enables future `rai doctor` integration and `rai info` reporting without re-discovery. Frozen dataclass — zero overhead, no coupling to consumer.
**Alternatives:** Return None (loses information), logging only (not programmatically consumable).

### D5: isinstance(ext_app, typer.Typer) type check

**Choice:** Validate loaded object is a Typer instance before registration.
**Rationale:** `add_typer` with a non-Typer object produces cryptic errors. Explicit check + warning follows PAT-E-598 (bare except hiding bugs).
**Alternatives:** No check (cryptic failures), Protocol (unnecessary — Typer is the contract).

## Examples

### Consumer registration (rai-agent/pyproject.toml)

```toml
[project.entry-points."rai.cli.commands"]
knowledge = "rai_agent.knowledge.cli:app"
```

### Successful load

```
$ rai knowledge validate ./nodes/
# Works — extension discovered and registered

$ RAI_LOG_LEVEL=DEBUG rai --help
# DEBUG: Loaded CLI extension 'knowledge' from 'rai-agent'
```

### Broken extension

```
$ rai --help
# CLI loads normally, broken extension skipped
# WARNING (in debug): Skipping CLI extension 'broken' from 'bad-pkg': ImportError ...
```

### Name collision

```
$ rai --help
# WARNING: Skipping CLI extension 'session' from 'rogue-pkg': conflicts with built-in command
```

## Acceptance Criteria

- **MUST:** Entry points in `rai.cli.commands` group are discovered and registered as Typer sub-apps
- **MUST:** `rai --help` shows extension commands alongside built-ins
- **MUST:** Broken extensions are skipped with `logger.warning` (no crash, no user-visible output at default verbosity)
- **MUST:** Extensions conflicting with built-in command names are rejected with warning
- **MUST:** Duplicate extension names are detected (first-wins, warning on duplicate)
- **MUST:** `discover_cli_extensions()` returns `list[ExtensionInfo]` with load status
- **MUST NOT:** Add new dependencies
- **MUST NOT:** Change behavior of existing commands
- **SHOULD:** Type validation — reject non-Typer objects with warning
