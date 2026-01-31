# Python CLI Architecture Best Practices Analysis

**Research Date:** 2026-01-30
**Objective:** Analyze architecture patterns from mature Python CLIs to inform raise-cli design

---

## 1. Executive Summary

Analysis of seven mature Python CLI tools reveals consistent architectural patterns that promote maintainability, testability, and user experience:

**Key Patterns Identified:**

1. **Strict Layering**: All successful CLIs separate presentation (CLI) from core business logic
2. **Configuration Cascade**: Standard precedence: CLI args > env vars > config files > defaults
3. **Pydantic Dominance**: Modern CLIs favor Pydantic for configuration and data validation
4. **Rich Output**: Rich library is the de facto standard for formatted terminal output
5. **Typer for CLI**: Modern Python CLIs increasingly adopt Typer over raw Click
6. **Modular Monolith**: Single deployable with clear internal boundaries
7. **Factory Pattern**: Object creation separated from business logic

**Verdict for raise-cli:** The current architecture design in CLAUDE.md aligns well with industry best practices. Minor adjustments recommended in testing patterns and error handling.

---

## 2. Directory Structure Patterns

### Common Layout (Modern Python CLI)

```
src/project_name/
├── __init__.py
├── __main__.py          # Entry point: python -m project_name
├── cli/                  # CLI layer (Typer commands)
│   ├── __init__.py
│   ├── main.py          # App initialization, root command
│   └── commands/        # Subcommand modules
│       ├── foo.py
│       └── bar.py
├── core/                 # Business logic (CLI-agnostic)
│   ├── __init__.py
│   ├── engine.py        # Main orchestration
│   └── services/        # Domain services
├── config/               # Configuration handling
│   ├── __init__.py
│   ├── settings.py      # Pydantic Settings model
│   └── loader.py        # Config file loading
├── schemas/              # Pydantic data models
│   ├── __init__.py
│   └── models.py
├── output/               # Output formatting
│   ├── __init__.py
│   └── formatters.py    # JSON, table, human formats
└── exceptions.py         # Centralized error definitions
```

### Examples from Analyzed CLIs

**Poetry** (`src/poetry/`):
- `console/` - CLI commands and user interaction
- `config/` - Settings management
- `packages/`, `repositories/` - Domain logic
- `factory.py` - Object creation
- `exceptions.py` - Error definitions

**HTTPie** (`httpie/`):
- `cli/` - Command-line parsing
- `core.py` - Central request logic
- `output/` - Response formatting
- `config.py` - Settings
- `plugins/` - Extensibility

**Black** (`src/black/`):
- `__main__.py` - Entry point
- `__init__.py` - Core formatting logic
- `output.py`, `report.py` - User feedback
- `files.py` - File handling
- `concurrency.py` - Parallel processing

### raise-cli Current Design vs Pattern

| Pattern Element | raise-cli Design | Match |
|-----------------|------------------|-------|
| `engines/` for core logic | Yes | Aligned |
| `cli/` for Typer commands | Yes | Aligned |
| `schemas/` for Pydantic models | Yes | Aligned |
| `core/` for utilities | Yes | Aligned |
| Centralized `exceptions.py` | Not explicit | Consider adding |
| `output/` for formatting | Not explicit | Consider adding |

---

## 3. Layering Patterns

### The Three-Layer Architecture

All mature CLIs follow a consistent layering pattern:

```
┌─────────────────────────────────────────┐
│           Presentation Layer            │
│  (CLI commands, output formatting)      │
│  - Typer/Click decorators               │
│  - Argument parsing                     │
│  - Output rendering (Rich)              │
│  - User prompts                         │
└───────────────────┬─────────────────────┘
                    │ calls
                    ▼
┌─────────────────────────────────────────┐
│           Application Layer             │
│  (Orchestration, use cases)             │
│  - Command handlers                     │
│  - Workflow coordination                │
│  - Error translation                    │
└───────────────────┬─────────────────────┘
                    │ uses
                    ▼
┌─────────────────────────────────────────┐
│             Domain Layer                │
│  (Core business logic)                  │
│  - Engines (kata, gate, skill)          │
│  - Validators                           │
│  - Data transformers                    │
└─────────────────────────────────────────┘
```

### Key Principles

1. **Dependencies flow inward**: CLI imports core, never reverse
2. **Core is CLI-agnostic**: Business logic works without CLI
3. **Schemas shared across layers**: Pydantic models bridge layers
4. **Output formatting at edge**: Format decisions in presentation layer

### Poetry's Layering (Reference Implementation)

```python
# console/commands/add.py (Presentation)
class AddCommand(Command):
    def handle(self) -> int:
        # Parse CLI args, call application layer
        installer = Installer(self.io, self.env, self.poetry)
        return installer.run()

# installation/installer.py (Application)
class Installer:
    def run(self) -> int:
        # Orchestrate domain operations
        self._resolve_dependencies()
        self._install_packages()

# puzzle/solver.py (Domain)
class Solver:
    def solve(self) -> Transaction:
        # Pure business logic, no CLI awareness
```

### raise-cli Alignment

The current design with `engines/` as domain layer is correct. Recommendation:

- **Add**: Application layer between `cli/` and `engines/` for orchestration
- **Keep**: `engines/` as pure domain logic
- **Clarify**: `cli/` should only handle parsing and output, delegating to handlers

---

## 4. Configuration Patterns

### Standard Precedence Order

All analyzed CLIs follow this precedence (highest to lowest):

1. **CLI arguments** (explicit user intent)
2. **Environment variables** (deployment configuration)
3. **Project config file** (`pyproject.toml`, `.project.toml`)
4. **User config file** (`~/.config/project/config.toml`)
5. **System defaults** (hardcoded fallbacks)

### Pydantic Settings Pattern

Modern CLIs use `pydantic-settings` for configuration:

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class RaiseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="RAISE_",
        env_file=".env",
        toml_file="pyproject.toml",
        extra="ignore"
    )

    # Settings with defaults
    output_format: Literal["json", "human", "table"] = "human"
    verbosity: int = 0
    color: bool = True

    # Project-specific
    governance_path: Path = Path("governance")
    work_path: Path = Path("work")

# Usage in CLI
settings = RaiseSettings()
```

### Configuration File Formats

| Format | Use Case | Python Support |
|--------|----------|----------------|
| TOML | Config files, `pyproject.toml` | `tomllib` (3.11+) |
| JSON | Data interchange, API responses | Built-in |
| YAML | Complex config (avoid if possible) | `pyyaml` |

**Recommendation:** Use `pyproject.toml` with `[tool.raise]` section for project config.

### Config Loading Pattern (HTTPie-style)

```python
# config/loader.py
def load_config() -> RaiseSettings:
    """Load configuration with proper precedence."""
    # 1. Start with defaults
    settings = RaiseSettings()

    # 2. Load project config if exists
    project_config = find_project_config()
    if project_config:
        settings = settings.model_copy(
            update=load_toml_section(project_config, "tool.raise")
        )

    # 3. Environment variables override (automatic via Pydantic)
    # 4. CLI args override (done at command level)

    return settings
```

---

## 5. State Management Patterns

### When CLIs Need State

| State Type | Example | Storage Pattern |
|------------|---------|-----------------|
| Session state | Auth tokens | XDG config dir |
| Cache | Resolved deps | XDG cache dir |
| Lock files | poetry.lock | Project root |
| History | Command history | XDG data dir |

### XDG Base Directory Specification

All CLIs should respect XDG conventions:

```python
from pathlib import Path
import os

def get_config_dir() -> Path:
    """Get XDG config directory."""
    xdg_config = os.environ.get("XDG_CONFIG_HOME")
    if xdg_config:
        return Path(xdg_config) / "raise"
    return Path.home() / ".config" / "raise"

def get_cache_dir() -> Path:
    """Get XDG cache directory."""
    xdg_cache = os.environ.get("XDG_CACHE_HOME")
    if xdg_cache:
        return Path(xdg_cache) / "raise"
    return Path.home() / ".cache" / "raise"
```

### State File Formats

| Format | Best For | Example |
|--------|----------|---------|
| JSON | Simple key-value state | Session tokens |
| SQLite | Complex queryable data | Execution history |
| TOML | Human-editable config | User preferences |

### Poetry's Lock File Pattern

```python
# For raise-cli: governance state could use similar pattern
# governance/.raise-state.json
{
    "version": "1.0",
    "last_validated": "2026-01-30T10:00:00Z",
    "gates_passed": {
        "constitution": "hash123",
        "guardrails": "hash456"
    }
}
```

---

## 6. Error Handling Patterns

### Error Hierarchy Pattern

All mature CLIs use a structured error hierarchy:

```python
# exceptions.py

class RaiseError(Exception):
    """Base exception for all raise-cli errors."""
    exit_code: int = 1

    def __init__(self, message: str, hint: str | None = None):
        self.message = message
        self.hint = hint
        super().__init__(message)

class ConfigurationError(RaiseError):
    """Configuration-related errors."""
    exit_code: int = 2

class GovernanceError(RaiseError):
    """Governance validation errors."""
    exit_code: int = 3

class KataError(RaiseError):
    """Kata execution errors."""
    exit_code: int = 4

class GateError(RaiseError):
    """Gate validation failures."""
    exit_code: int = 5
```

### Exit Code Conventions

| Code | Meaning | Example |
|------|---------|---------|
| 0 | Success | Command completed |
| 1 | General error | Unhandled exception |
| 2 | Configuration error | Invalid config file |
| 3 | Validation error | Governance check failed |
| 4 | User error | Invalid arguments |
| 5 | External error | Git command failed |

### Error Presentation Pattern

```python
# cli/error_handler.py
from rich.console import Console
from rich.panel import Panel

console = Console(stderr=True)

def handle_error(error: RaiseError) -> int:
    """Format and display error to user."""
    console.print(Panel(
        f"[red bold]Error:[/] {error.message}",
        title="[red]raise[/]",
        border_style="red"
    ))

    if error.hint:
        console.print(f"\n[dim]Hint:[/] {error.hint}")

    return error.exit_code

# In main CLI entry point
@app.callback()
def main():
    try:
        # Command execution
        pass
    except RaiseError as e:
        raise SystemExit(handle_error(e))
    except Exception as e:
        # Log unexpected errors, show generic message
        console.print("[red]Unexpected error occurred[/]")
        raise SystemExit(1)
```

---

## 7. Output & UX Patterns

### Output Format Flag Pattern

Standard approach for machine-readable output:

```python
from enum import Enum
from typing import Annotated
import typer

class OutputFormat(str, Enum):
    human = "human"
    json = "json"
    table = "table"

@app.command()
def list_katas(
    format: Annotated[OutputFormat, typer.Option("--format", "-f")] = OutputFormat.human
):
    katas = engine.list_katas()

    if format == OutputFormat.json:
        console.print_json(data=katas)
    elif format == OutputFormat.table:
        print_table(katas)
    else:
        print_human_readable(katas)
```

### Rich Integration Pattern

```python
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

console = Console()

# Progress for long operations
def run_gate(gate_id: str):
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task(f"Running gate: {gate_id}", total=None)
        result = engine.run_gate(gate_id)
        progress.update(task, completed=True)

    return result

# Tables for structured data
def print_katas(katas: list[Kata]):
    table = Table(title="Available Katas")
    table.add_column("ID", style="cyan")
    table.add_column("Name")
    table.add_column("Type", style="green")

    for kata in katas:
        table.add_row(kata.id, kata.name, kata.type)

    console.print(table)
```

### Verbosity Levels

```python
from enum import IntEnum

class Verbosity(IntEnum):
    QUIET = -1    # Errors only
    NORMAL = 0    # Standard output
    VERBOSE = 1   # Additional info (-v)
    DEBUG = 2     # Debug info (-vv)
    TRACE = 3     # Full trace (-vvv)

@app.callback()
def main(
    verbose: Annotated[int, typer.Option("-v", "--verbose", count=True)] = 0,
    quiet: Annotated[bool, typer.Option("-q", "--quiet")] = False,
):
    verbosity = Verbosity.QUIET if quiet else Verbosity(min(verbose, 3))
    ctx.obj = {"verbosity": verbosity}
```

### Terminal Detection

```python
# Automatically disable colors when piping
console = Console(force_terminal=None)  # Auto-detect

# Check if interactive
if console.is_terminal:
    # Can use prompts, progress bars
    pass
else:
    # Piped output, use plain text
    pass
```

---

## 8. Testing Patterns

### Typer CliRunner Pattern

```python
# tests/conftest.py
import pytest
from typer.testing import CliRunner
from raise_cli.cli.main import app

@pytest.fixture
def runner():
    return CliRunner()

@pytest.fixture
def cli(runner):
    """Invoke CLI with given arguments."""
    def invoke(*args, **kwargs):
        return runner.invoke(app, list(args), **kwargs)
    return invoke

# tests/test_kata.py
def test_kata_list(cli):
    result = cli("kata", "list")
    assert result.exit_code == 0
    assert "setup/rules" in result.stdout

def test_kata_run_missing(cli):
    result = cli("kata", "run", "nonexistent")
    assert result.exit_code != 0
    assert "not found" in result.stdout.lower()
```

### Isolated Filesystem Pattern

```python
# tests/test_with_files.py
def test_governance_load(runner, tmp_path):
    # Create test governance structure
    (tmp_path / "governance").mkdir()
    (tmp_path / "governance" / "solution").mkdir()
    (tmp_path / "governance" / "solution" / "vision.md").write_text("# Vision")

    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(app, ["validate"])
        assert result.exit_code == 0
```

### Mocking External Dependencies

```python
# tests/test_git.py
from unittest.mock import patch

def test_git_status(cli):
    with patch("raise_cli.core.git.run_git") as mock_git:
        mock_git.return_value = ("main", 0)
        result = cli("status")
        assert result.exit_code == 0
        mock_git.assert_called_once()
```

### Fixtures for Common Setup

```python
# tests/conftest.py
@pytest.fixture
def sample_governance(tmp_path):
    """Create sample governance structure."""
    gov = tmp_path / "governance"
    gov.mkdir()

    solution = gov / "solution"
    solution.mkdir()
    (solution / "vision.md").write_text("# Vision\n\nTest vision.")
    (solution / "guardrails.md").write_text("# Guardrails\n\n- Rule 1")

    return gov

@pytest.fixture
def mock_git():
    """Mock git operations."""
    with patch("raise_cli.core.git") as mock:
        mock.get_branch.return_value = "main"
        mock.is_clean.return_value = True
        yield mock
```

### Property-Based Testing

```python
# tests/test_schemas.py
from hypothesis import given, strategies as st
from raise_cli.schemas.kata import KataConfig

@given(st.text(min_size=1, max_size=100))
def test_kata_id_validation(kata_id: str):
    """Kata IDs must follow naming convention."""
    # Valid IDs: lowercase, hyphens, slashes for namespacing
    if all(c.islower() or c in "-/" for c in kata_id):
        config = KataConfig(id=kata_id, name="Test")
        assert config.id == kata_id
    else:
        with pytest.raises(ValidationError):
            KataConfig(id=kata_id, name="Test")
```

---

## 9. Recommendations for raise-cli

### What We Should Adopt

| Pattern | Priority | Rationale |
|---------|----------|-----------|
| Centralized `exceptions.py` | High | Clear error hierarchy, consistent exit codes |
| `output/` module for formatters | High | Separate output from logic |
| Pydantic Settings for config | High | Type-safe, precedence-aware config |
| XDG directory conventions | Medium | Standard locations for state/cache |
| Rich progress indicators | Medium | Better UX for long operations |
| `--format` flag pattern | Medium | Machine-readable output option |

### What We Should Change

1. **Add Application Layer**
   - Current: `cli/` -> `engines/`
   - Proposed: `cli/` -> `handlers/` -> `engines/`
   - Rationale: Handlers translate CLI intent to domain operations

2. **Explicit Error Handling**
   - Add `exceptions.py` with `RaiseError` hierarchy
   - Define exit codes for each error category
   - Implement error presentation with Rich

3. **Output Abstraction**
   - Add `output/` module with formatters
   - Support `--format json|human|table`
   - Auto-detect terminal for color/formatting

### What We're Missing

1. **XDG-compliant state storage**
   - For: execution history, cache, user preferences
   - Pattern: `~/.config/raise/`, `~/.cache/raise/`

2. **Verbosity controls**
   - `-v/-vv/-vvv` for verbose/debug/trace
   - `-q` for quiet mode (errors only)

3. **Testing infrastructure**
   - `conftest.py` with CliRunner fixtures
   - Mock patterns for git, ast-grep, ripgrep
   - Property tests for validators

### What's Already Good

| Current Design Element | Status |
|------------------------|--------|
| `engines/` as domain layer | Aligned with best practices |
| `schemas/` for Pydantic models | Aligned with best practices |
| `cli/` for Typer commands | Aligned with best practices |
| Modular monolith pattern | Aligned with best practices |
| Engine-content separation | Aligned with best practices |
| Pydantic over TypedDict | Aligned with best practices |

---

## 10. Reference Implementations

### Directory Structure

- **Poetry**: [src/poetry/](https://github.com/python-poetry/poetry/tree/main/src/poetry) - Clean module separation
- **HTTPie**: [httpie/](https://github.com/httpie/cli/tree/master/httpie) - Output formatting patterns

### Configuration

- **Ruff**: [pyproject.toml](https://github.com/astral-sh/ruff/blob/main/pyproject.toml) - Config file patterns
- **Pydantic Settings**: [Documentation](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) - Settings precedence

### Testing

- **Click Testing**: [Documentation](https://click.palletsprojects.com/en/stable/testing/) - CliRunner patterns
- **Typer Testing**: [Documentation](https://typer.tiangolo.com/tutorial/testing/) - Testing with CliRunner

### Output Formatting

- **Rich**: [Console API](https://rich.readthedocs.io/en/stable/console.html) - Output patterns
- **Rich CLI**: [GitHub](https://github.com/Textualize/rich-cli) - JSON formatting

### Error Handling

- **Typer Exceptions**: [Documentation](https://typer.tiangolo.com/tutorial/exceptions/) - Error patterns

---

## Sources

- [Best Practices for Structuring a Python CLI Application](https://medium.com/@ernestwinata/best-practices-for-structuring-a-python-cli-application-1bc8f8a57369)
- [Clean Architecture Essentials: Transforming Python Development](https://deepengineering.substack.com/p/clean-architecture-essentials-transforming)
- [Layered Architecture & Dependency Injection](https://dev.to/markoulis/layered-architecture-dependency-injection-a-recipe-for-clean-and-testable-fastapi-code-3ioo)
- [6 ways to improve the architecture of your Python project](https://www.piglei.com/articles/en-6-ways-to-improve-the-arch-of-you-py-project/)
- [Testing - Typer](https://typer.tiangolo.com/tutorial/testing/)
- [How To Test CLI Applications With Pytest, Argparse And Typer](https://pytest-with-eric.com/pytest-advanced/pytest-argparse-typer/)
- [Settings Management - Pydantic](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [Controlling Python Exit Codes and Shell Scripts](https://henryleach.com/2025/02/controlling-python-exit-codes-and-shell-scripts/)
- [Exceptions and Errors - Typer](https://typer.tiangolo.com/tutorial/exceptions/)
- [Testing Click Applications](https://click.palletsprojects.com/en/stable/testing/)
- [Console API - Rich](https://rich.readthedocs.io/en/stable/console.html)
- [Poetry Documentation](https://python-poetry.org/docs/cli/)
- [Black Documentation](https://black.readthedocs.io/)

---

*Research conducted for raise-cli architecture design*
*Date: 2026-01-30*
