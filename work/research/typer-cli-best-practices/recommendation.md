# Recommendation: Typer CLI Best Practices for RaiSE

> Research ID: TYPER-CLI-BP-20260205
> Date: 2026-02-05

---

## Decision

Adopt the following Typer CLI design patterns for the RaiSE CLI (`raise` command) based on triangulated evidence from 22 sources.

**Confidence:** HIGH

---

## Rationale

The recommendations below are derived from convergent evidence across authoritative sources:
- **Official documentation:** Typer, Click, Rich
- **Industry standards:** clig.dev (17k+ GitHub stars), Heroku CLI Style Guide
- **Production CLIs:** AWS CLI, Azure CLI (millions of users)
- **Community validation:** Multiple practitioner articles with consistent patterns

---

## Recommendations by Topic

### 1. Command Structure and Grouping

**Pattern:** Topic (noun) + Command (verb) with one file per command group.

```
raise context query      # topic: context, command: query
raise graph build        # topic: graph, command: build
raise discover scan      # topic: discover, command: scan
```

**Implementation:**

```python
# src/raise_cli/cli/commands/context.py
import typer

app = typer.Typer(help="Context operations for governance artifacts")

@app.command()
def query(
    terms: str = typer.Argument(..., help="Search terms"),
    format: str = typer.Option("human", "--format", "-f", help="Output format: human, json, table"),
):
    """Query the context graph for relevant artifacts."""
    ...

# src/raise_cli/cli/main.py
from .commands import context, graph, discover

app = typer.Typer()
app.add_typer(context.app, name="context")
app.add_typer(graph.app, name="graph")
app.add_typer(discover.app, name="discover")
```

**When to nest:** When commands form a logical group (>3 related commands). When to flatten: For top-level utility commands (init, version).

---

### 2. Option Design

**Pattern:** Flags over positional arguments. Standard flag names.

| Flag | Purpose | Convention |
|------|---------|------------|
| `-f, --format` | Output format | human, json, table |
| `-v, --verbose` | Verbose output | Global callback |
| `-q, --quiet` | Suppress output | Global callback |
| `--dry-run` | Show what would happen | Per-command |
| `-h, --help` | Show help | Automatic |
| `--version` | Show version | Automatic |

**Naming conventions:**
- Lowercase with dashes: `--output-format` not `--outputFormat`
- Boolean flags: `--verbose/--no-verbose` pattern
- Help text: lowercase, no period, describes what the option does

```python
@app.command()
def build(
    path: str = typer.Argument(".", help="Path to project"),
    unified: bool = typer.Option(False, "--unified", "-u", help="Build unified graph"),
    format: str = typer.Option("human", "--format", "-f", help="Output format"),
):
    """Build the governance graph from project artifacts."""
    ...
```

---

### 3. Output Formatting

**Pattern:** Three formats, human as default, Rich for formatting.

```python
from enum import Enum
from rich.console import Console
from rich.table import Table

class OutputFormat(str, Enum):
    human = "human"
    json = "json"
    table = "table"

console = Console()

def format_output(data: dict, format: OutputFormat) -> None:
    """Format and output data based on specified format."""
    if format == OutputFormat.json:
        console.print_json(data=data)
    elif format == OutputFormat.table:
        table = Table()
        # ... build table
        console.print(table)
    else:  # human
        # Rich panels, markdown, etc.
        console.print(...)
```

**Guidelines:**
- Human format: Use Rich panels, colors, markdown (TTY-aware)
- JSON format: Stable schema, no color escapes, suitable for `jq`
- Table format: grep-parseable, headers, no wrapping

---

### 4. Error Handling and Exit Codes

**Pattern:** Exception hierarchy mapped to exit codes. Catch at boundary.

```python
# src/raise_cli/exceptions.py
from enum import IntEnum

class ExitCode(IntEnum):
    SUCCESS = 0
    GENERAL_ERROR = 1
    INVALID_ARGUMENT = 2
    CONFIG_ERROR = 3
    VALIDATION_ERROR = 4
    NOT_FOUND = 5
    PERMISSION_ERROR = 6
    NETWORK_ERROR = 7

class RaiseError(Exception):
    """Base exception for RaiSE CLI."""
    exit_code: ExitCode = ExitCode.GENERAL_ERROR

    def __init__(self, message: str, suggestion: str | None = None):
        self.message = message
        self.suggestion = suggestion
        super().__init__(message)

class ConfigError(RaiseError):
    """Configuration-related errors."""
    exit_code = ExitCode.CONFIG_ERROR

class ValidationError(RaiseError):
    """Validation failures."""
    exit_code = ExitCode.VALIDATION_ERROR

# In CLI boundary
@app.command()
def command(...):
    try:
        result = service.operation(...)
    except RaiseError as e:
        console.print(f"[red]Error:[/red] {e.message}")
        if e.suggestion:
            console.print(f"[dim]Suggestion:[/dim] {e.suggestion}")
        raise typer.Exit(e.exit_code)
```

---

### 5. Testing CLI Applications

**Pattern:** CliRunner + pytest + parametrization.

```python
# tests/cli/test_context.py
import pytest
from typer.testing import CliRunner
from raise_cli.cli.main import app

runner = CliRunner()

class TestContextQuery:
    """Tests for raise context query command."""

    def test_query_success(self):
        """Query returns matching results."""
        result = runner.invoke(app, ["context", "query", "governance"])
        assert result.exit_code == 0
        assert "governance" in result.stdout.lower()

    def test_query_json_format(self):
        """JSON format returns valid JSON."""
        result = runner.invoke(app, ["context", "query", "test", "--format", "json"])
        assert result.exit_code == 0
        import json
        data = json.loads(result.stdout)
        assert isinstance(data, dict)

    @pytest.mark.parametrize("terms,expected_count", [
        ("governance", 5),
        ("nonexistent_term_xyz", 0),
        ("principle", 10),
    ])
    def test_query_result_counts(self, terms: str, expected_count: int):
        """Query returns expected number of results."""
        result = runner.invoke(app, ["context", "query", terms, "--format", "json"])
        data = json.loads(result.stdout)
        assert len(data.get("results", [])) >= expected_count

    def test_query_missing_terms(self):
        """Missing terms argument shows error."""
        result = runner.invoke(app, ["context", "query"])
        assert result.exit_code != 0
        assert "Missing argument" in result.stdout

class TestErrorHandling:
    """Tests for error handling and exit codes."""

    def test_invalid_format_option(self):
        """Invalid format option returns validation error."""
        result = runner.invoke(app, ["context", "query", "test", "--format", "invalid"])
        assert result.exit_code == 2  # INVALID_ARGUMENT
```

---

### 6. Common Anti-Patterns to Avoid

| Anti-Pattern | Why Bad | Do Instead |
|--------------|---------|------------|
| Ambiguous command names | `update` vs `upgrade` confusion | Clear, distinct names |
| Catch-all subcommands | Prevents future commands | Explicit command registration |
| Arbitrary abbreviations | Breaks when adding commands | Only explicit aliases |
| Fat commands | Untestable, hard to maintain | Thin commands, call services |
| Requiring prompts | Breaks automation | Always provide flag alternatives |
| Positional-heavy args | Order confusion | Flags for 2+ parameters |
| Ignoring TTY | Broken output in pipes | Rich TTY detection |
| Stack traces in output | Not user-friendly | Catch, rewrite, suggest |

---

## Trade-offs

### What We Accept

1. **More code for output formatting** - Three format modes means three code paths, but enables both human UX and automation.
2. **Exception hierarchy overhead** - Creating exception classes takes time upfront but pays off in consistent error handling.
3. **Test duplication** - Testing all formats and edge cases requires many tests, but catches regressions early.

### What We Sacrifice

1. **Simplicity of single output mode** - Human-only would be simpler but blocks scripting use cases.
2. **Minimal exception handling** - Just letting exceptions bubble would be less code but terrible UX.

---

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Output format schema drift | Medium | High | Schema versioning, tests for stability |
| Exit code conflicts | Low | Medium | Document exit codes, avoid >125 |
| Rich dependency issues | Low | Low | Pin version, test across terminals |
| Testing complexity | Medium | Medium | Helper fixtures, clear test organization |

---

## Alternatives Considered

### Alternative 1: Click Directly Instead of Typer

**Why not:** Typer provides type-hint-driven development, automatic help generation, and Rich integration. Click requires more boilerplate. Typer is built on Click, so we can drop down when needed.

### Alternative 2: Argparse

**Why not:** No subcommand composition, no automatic help text from type hints, more verbose. Industry consensus is on Typer/Click.

### Alternative 3: Single Output Format

**Why not:** Blocks automation. AWS, Azure, Heroku, kubectl all support multiple formats. Expected behavior for serious CLIs.

---

## Implementation Checklist

- [ ] Create `OutputFormat` enum and `format_output()` utility
- [ ] Create exception hierarchy in `exceptions.py` with exit codes
- [ ] Add `--format` global option via callback
- [ ] Structure commands as one file per command group
- [ ] Create CliRunner-based test fixtures
- [ ] Document exit codes in CLI help
- [ ] Add Rich tables and panels for human output
- [ ] Test all three output formats
- [ ] Test error paths with appropriate exit codes

---

## References

- [Typer Documentation](https://typer.tiangolo.com/)
- [Click Documentation](https://click.palletsprojects.com/)
- [Command Line Interface Guidelines](https://clig.dev/)
- [Heroku CLI Style Guide](https://devcenter.heroku.com/articles/cli-style-guide)
- [Rich Documentation](https://rich.readthedocs.io/)

---

*Recommendation created: 2026-02-05*
*Research: TYPER-CLI-BP-20260205*
