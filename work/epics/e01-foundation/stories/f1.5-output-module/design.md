---
story_id: "F1.5"
title: "Output Module"
epic_ref: "E1 Core Foundation"
story_points: 3
complexity: "simple"
status: "implemented"
version: "1.0"
created: "2026-01-31"
updated: "2026-01-31"
template: "lean-feature-spec-v2"
---

# Feature: Output Module

> **Epic**: E1 - Core Foundation
> **Complexity**: simple | **SP**: 3

---

## 1. What & Why

**Problem**: Commands need consistent output formatting across human-readable, JSON (for scripting), and table (for lists) formats. Currently only error handling has Rich output; success paths need the same consistency.

**Value**: Users get predictable CLI output they can parse programmatically (`--format json`) or read comfortably (default human), enabling both interactive use and CI/CD integration.

---

## 2. Approach

**How we'll solve it**: Create a thin output abstraction over Rich Console that respects the `--format` flag, providing `print_*` functions for common output types (messages, data, lists, success/warning).

**Components affected**:
- **`src/raise_cli/output/`**: Create - new output module with formatters
- **`src/raise_cli/cli/main.py`**: Modify - wire up output console to settings
- **`src/raise_cli/__init__.py`**: Modify - export public API

---

## 3. Interface / Examples

> **IMPORTANT**: Concrete examples for AI code generation accuracy

### API Usage

```python
from raise_cli.output import get_console, OutputConsole

# Get configured console (respects --format flag)
console = get_console()

# Print simple message (human: styled, json: {"message": "..."})
console.print_message("Processing kata...")

# Print success message (human: green checkmark, json: {"status": "success", ...})
console.print_success("Kata completed", details={"duration": "2.3s"})

# Print warning (human: yellow, json: {"status": "warning", ...})
console.print_warning("Config file not found, using defaults")

# Print data structure (human: Rich table/tree, json: raw dict, table: tabulate)
console.print_data({"name": "discovery", "steps": 5, "status": "ready"})

# Print list of items (human: bullet list, json: array, table: rows)
console.print_list([
    {"id": "kata/discovery", "name": "Discovery", "work_cycle": "discovery"},
    {"id": "kata/design", "name": "Design", "work_cycle": "design"},
])
```

### CLI Usage

```bash
# Human output (default)
raise kata list
# ✓ Found 3 katas
#   • kata/discovery - Discovery (discovery)
#   • kata/design - Design (design)
#   • kata/planning - Planning (planning)

# JSON output (for scripting)
raise kata list --format json
# [{"id": "kata/discovery", "name": "Discovery", "work_cycle": "discovery"}, ...]

# Table output (for structured lists)
raise kata list --format table
# ID               NAME        WORK_CYCLE
# kata/discovery   Discovery   discovery
# kata/design      Design      design
```

### Expected Output Examples

**Human format (message)**:
```
Processing kata...
```

**Human format (success)**:
```
✓ Kata completed (duration: 2.3s)
```

**Human format (list)**:
```
Found 3 katas:
  • kata/discovery - Discovery
  • kata/design - Design
  • kata/planning - Planning
```

**JSON format (success)**:
```json
{"status": "success", "message": "Kata completed", "details": {"duration": "2.3s"}}
```

**JSON format (list)**:
```json
[{"id": "kata/discovery", "name": "Discovery"}, {"id": "kata/design", "name": "Design"}]
```

**Table format (list)**:
```
ID               NAME        WORK_CYCLE
kata/discovery   Discovery   discovery
kata/design      Design      design
```

### Data Structures

```python
from typing import Any, Literal
from pydantic import BaseModel

class OutputConsole:
    """Output abstraction that respects --format flag."""

    def __init__(
        self,
        format: Literal["human", "json", "table"] = "human",
        verbosity: int = 0,
        color: bool = True,
    ) -> None: ...

    def print_message(self, message: str, *, style: str | None = None) -> None:
        """Print a simple message."""
        ...

    def print_success(self, message: str, *, details: dict[str, Any] | None = None) -> None:
        """Print a success message with optional details."""
        ...

    def print_warning(self, message: str, *, details: dict[str, Any] | None = None) -> None:
        """Print a warning message."""
        ...

    def print_data(self, data: dict[str, Any], *, title: str | None = None) -> None:
        """Print a data structure (dict becomes table/tree/json)."""
        ...

    def print_list(
        self,
        items: list[dict[str, Any]],
        *,
        columns: list[str] | None = None,
        title: str | None = None,
    ) -> None:
        """Print a list of items (becomes bullet list/json array/table)."""
        ...


# Module-level access (like error_handler pattern)
_console: OutputConsole | None = None

def get_console() -> OutputConsole:
    """Get or create the output console singleton."""
    ...

def set_console(console: OutputConsole | None) -> None:
    """Set the console (for testing or reconfiguration)."""
    ...

def configure_console(
    format: Literal["human", "json", "table"] = "human",
    verbosity: int = 0,
    color: bool = True,
) -> OutputConsole:
    """Configure and return the global console."""
    ...
```

---

## 4. Acceptance Criteria

> **MUST** = Required for feature completion
> **SHOULD** = Nice-to-have
> **MUST NOT** = Explicit anti-requirements

### Must Have

- [ ] `OutputConsole` class with `print_message`, `print_success`, `print_warning`, `print_data`, `print_list` methods
- [ ] Human format uses Rich styling (colors, checkmarks, bullet points)
- [ ] JSON format outputs valid JSON to stdout (parseable by `jq`)
- [ ] Table format uses Rich Table for structured list output
- [ ] Module-level `get_console()`, `set_console()`, `configure_console()` functions
- [ ] Respects `verbosity` level (quiet = -1 suppresses non-error output)
- [ ] All public API exported from `raise_cli.output`
- [ ] >90% test coverage on new code

### Should Have

- [ ] `print_data` renders nested dicts as Rich Tree in human mode
- [ ] Color can be disabled via `color=False` for CI environments

### Must NOT

- [ ] **DO NOT** print to stderr (that's for errors only - handled by error_handler)
- [ ] **DO NOT** add dependencies beyond Rich (already in project)
- [ ] **DO NOT** change error handling behavior (F1.4 owns that)

---

## References

**Related ADRs**:
- ADR-002: Pydantic for validation (settings integration)

**Related Features**:
- F1.4: Exception Hierarchy (error output pattern to follow)
- F1.3: Configuration System (settings source for format/verbosity)

**Dependencies**:
- F1.4 must be complete (it is)
- Rich library (already installed)

---

**Template Version**: 2.0 (Lean Feature Spec)
**Created**: 2026-01-31
