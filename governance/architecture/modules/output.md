---
type: module
name: output
purpose: "Format-aware output system — human-readable, JSON, and table formats through a single console interface"
status: current
depends_on: [skills]
depended_by: [cli]
entry_points: []
public_api:
  - "OutputConsole"
  - "OutputFormat"
  - "configure_console"
  - "get_console"
  - "set_console"
components: 28
constraints:
  - "All CLI output must go through OutputConsole, never raw print()"
  - "Formatters are domain-specific — each command group has its own formatter"
---

## Purpose

The output module decouples **what** to display from **how** to display it. Every CLI command produces a result model; the output module formats that model for the active output mode (`--output human|json|table`). This means adding JSON output to any command is free — you just need a formatter function that maps the result model to the right format.

The `OutputConsole` singleton manages output format, color support, and verbosity. Commands call `get_console()` and use methods like `print_success()`, `print_table()`, or `print_json()`.

## Key Files

- **`console.py`** — `OutputConsole` class with format-aware output methods. Singleton via `get_console()`/`set_console()`. Handles color detection and format switching.
- **`formatters/discover.py`** — Formatters for discovery commands (scan results, analysis, drift warnings). Maps discovery result models to human/JSON/table output.
- **`formatters/skill.py`** — Formatters for skill commands (list, show, validate). Maps skill models to formatted output.

## Dependencies

| Depends On | Why |
|-----------|-----|
| `skills` | Type imports for skill result formatters |

## Conventions

- One formatter file per command group (e.g., `formatters/discover.py` for all `raise discover *` commands)
- Formatters are pure functions: take a result model, return formatted output
- Human format uses Unicode box drawing and color; JSON format is raw Pydantic `.model_dump()`
- New commands need a corresponding formatter added to `formatters/`
