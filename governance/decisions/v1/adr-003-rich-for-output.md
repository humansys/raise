# ADR-003: Rich for CLI Output

**Date:** 2026-01-30
**Status:** Accepted
**Deciders:** Emilio Osorio, Rai

---

## Context

raise-cli needs to output information to users in multiple formats:
- **Human-friendly:** Colored, formatted, readable terminal output
- **Machine-readable:** JSON for scripts and APIs
- **Tabular:** ASCII tables for lists

The CLI should provide excellent UX for human users while supporting automation.

---

## Decision

Use **Rich** library for all human-facing output.

**Scope:**
- All CLI output (kata results, gate validation, lists)
- Error messages (formatted panels with hints)
- Progress indicators (spinners, progress bars)
- Tables (for list commands)
- Console singleton for consistent formatting

**Pattern:**
```python
from rich.console import Console
from rich.panel import Panel

console = Console()
console.print(Panel("Kata completed!", style="green"))
```

---

## Alternatives Considered

### Alternative 1: print() statements
**Rejected because:**
- No color/formatting
- No terminal detection (breaks in CI)
- No progress indicators
- Inconsistent formatting
- Manual ANSI escape codes (error-prone)

### Alternative 2: colorama
**Rejected because:**
- Only handles colors (no tables, panels, progress)
- Limited formatting options
- Still need to build formatting manually
- Rich is superset of colorama features

### Alternative 3: click.echo + click.style
**Rejected because:**
- We're using Typer (built on click), but Rich is better for output
- Click styling is basic (no tables, panels, progress)
- Rich has better terminal detection
- Rich actively maintained with modern features

### Alternative 4: termcolor
**Rejected because:**
- Minimal feature set (just colors)
- No progress indicators
- No tables or structured output
- Rich is more comprehensive

---

## Consequences

### Positive
- **Beautiful output:** Colors, tables, panels, progress bars out of box
- **Terminal detection:** Auto-disables formatting in CI/pipes
- **Consistent UX:** All commands use same Rich components
- **Progress indicators:** Spinners for long operations (kata execution)
- **Error formatting:** Beautiful error panels with hints
- **JSON mode:** Rich can output JSON too (`.print_json()`)
- **Wide adoption:** Used by FastAPI, Typer, pytest, Poetry

### Negative
- **Dependency:** Adds Rich (~300KB)
- **Learning curve:** Team needs to learn Rich API
- **Overkill for simple output:** More complex than `print()`

### Mitigations
- **Dependency size:** 300KB is reasonable for UX improvement
- **Learning curve:** Rich docs excellent, patterns intuitive
- **Complexity:** Abstract into output module (F1.5), commands just call `output()`

---

## Examples

### Panel for Success
```python
from rich.panel import Panel
console.print(Panel("✓ Kata completed", style="green"))
```

### Table for Lists
```python
from rich.table import Table
table = Table(title="Available Katas")
table.add_column("ID")
table.add_column("Title")
table.add_row("project/discovery", "Project Discovery")
console.print(table)
```

### Progress Bar
```python
from rich.progress import track
for step in track(kata.steps, description="Executing..."):
    execute_step(step)
```

### Error Panel
```python
console.print(Panel(
    "[bold red]Error E003[/]: Kata not found",
    subtitle="Try: raise kata list"
))
```

---

## Integration with Output Module (F1.5)

Rich will be wrapped in output module:
```python
# output/formatters.py
def output(data: Any, format: str):
    if format == "json":
        console.print_json(data)
    elif format == "table":
        print_table(data)  # Uses Rich Table
    else:
        print_human(data)  # Uses Rich Panel/Text
```

Commands don't use Rich directly - they call `output()`.

---

## References

- Rich docs: https://rich.readthedocs.io/
- Rich GitHub: https://github.com/Textualize/rich
- Design: `governance/projects/raise-cli/design.md` (Section 5)
- Used by: FastAPI, Typer, pytest, Poetry

---

*ADR-003 - Rich for output*
