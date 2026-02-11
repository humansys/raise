---
type: module
name: cli
purpose: "Typer-based CLI commands — the user-facing entry point that orchestrates all other modules"
status: current
depends_on: [config, context, discovery, governance, memory, onboarding, output, rai_base, session, skills, telemetry]
depended_by: []
entry_points:
  - "raise init"
  - "raise discover scan|analyze|drift|build|describe"
  - "raise memory build|query|add|emit|emit-work"
  - "raise profile show"
  - "raise session start"
  - "raise skill list|show|validate|create"
public_api:
  - "app (Typer main app)"
components: 54
constraints:
  - "Nothing depends on cli — it's the outermost layer"
  - "CLI commands are thin wrappers — logic lives in domain modules"
  - "All output goes through the output module formatters"
---

## Purpose

The CLI module is the **application shell** — it parses user input, calls the appropriate domain module, and formats the output. It uses [Typer](https://typer.tiangolo.com/) with subcommand groups (`rai discover ...`, `rai memory ...`, `rai skill ...`). Each command is intentionally thin: validate arguments, call a domain function, format the result.

This is the only module that depends on everything else, and nothing depends on it. If you're adding a new CLI command, this is where it goes. If you're adding logic, it belongs in a domain module instead.

## Architecture

```
User → raise <command> → Typer router → command function → domain module
                                                              ↓
                                                         result model
                                                              ↓
                                                    output formatter → stdout
```

Commands are organized by domain as Typer sub-apps:
- `discover_app` — discovery pipeline commands
- `memory_app` — memory and graph commands
- `skill_app` — skill management commands
- Top-level: `init`, `profile`, `session`

## Key Files

- **`main.py`** — Typer app definition and sub-app registration. Global options (`--output`, `--verbose`).
- **`commands/discover.py`** — `scan`, `analyze`, `drift`, `build` commands for the discovery pipeline.
- **`commands/memory.py`** — `build`, `query`, `add`, `emit`, `emit-work` commands for memory and graph operations.
- **`commands/init.py`** — `rai init` command for project bootstrapping (onboarding flow).
- **`commands/skill.py`** — `list`, `show`, `validate`, `create` commands for skill management.
- **`commands/profile.py`** — `rai profile show` for developer profile display.
- **`commands/session.py`** — `rai session start` for session tracking.
- **`error_handler.py`** — Maps exceptions to exit codes and user-friendly error messages.

## Dependencies

| Depends On | Why |
|-----------|-----|
| `config` | Settings and output format |
| `context` | Graph building and querying |
| `discovery` | Scanner, analyzer, drift detection |
| `governance` | Governance extraction |
| `memory` | Pattern/calibration/session writing |
| `onboarding` | Project initialization, profile management |
| `output` | Format-aware output (human/JSON/table) |
| `rai_base` | Base identity and patterns for init |
| `schemas` | Pydantic models for session state |
| `session` | Session bundle assembly and close logic |
| `skills` | Skill listing, validation, scaffolding |
| `telemetry` | Signal emission on command usage |

## Conventions

- Commands are thin — 10-30 lines of argument parsing + one domain call + output formatting
- Use `get_console()` for all output, never raw `print()`
- Error handling goes through `error_handler.py`, not try/except in commands
- Each command group is a separate Typer sub-app mounted on the main app
