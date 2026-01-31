# Tech Design: raise-cli

> **Status**: Draft
> **Date**: 2026-01-30
> **Version**: 1.1.0
> **Related**: `governance/projects/raise-cli/prd.md`, `governance/projects/raise-cli/vision.md`
> **Research**: `work/research/outputs/python-cli-architecture-analysis.md`

---

## 1. Objective and Solution

**Technical Problem**:
RaiSE methodology exists as static markdown files with no execution runtime. Engineers cannot programmatically execute katas, validate gates, or generate context for AI assistants.

**Proposed Solution**:
Build a CLI tool that parses kata/gate definitions, tracks execution state, validates artifacts deterministically, and produces structured output for both humans and AI assistants.

**Architecture Pattern**: Three-Layer Architecture (aligned with Poetry, HTTPie, Black patterns)

**Components Involved**:
- **Presentation Layer (CLI)**: Command parsing, output formatting (Typer + Rich)
- **Application Layer (Handlers)**: Orchestration, use cases, error translation
- **Domain Layer (Engines)**: Core business logic (Kata, Gate, SAR, Context)
- **Core Layer**: Schemas, configuration, state, utilities

---

## 2. Architecture

### 2.1 System Context (C4 Level 1)

```
                              ┌─────────────────┐
                              │  RaiSE Engineer │
                              │     (User)      │
                              └────────┬────────┘
                                       │ invokes
                                       ▼
┌──────────────────────────────────────────────────────────────────┐
│                          raise-cli                                │
│                    "Governance CLI for RaiSE"                     │
└──────────────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
   ┌───────────┐        ┌───────────┐        ┌───────────┐
   │    Git    │        │  ast-grep │        │  ripgrep  │
   │  (VCS)    │        │ (AST)     │        │ (Search)  │
   └───────────┘        └───────────┘        └───────────┘

         │
         ▼
   ┌───────────┐
   │  Agent    │  ← Discovers via raise/SKILL.md
   │  Skills   │
   │ Ecosystem │
   └───────────┘
```

**Actors**:
- **RaiSE Engineer**: Primary user invoking CLI commands
- **AI Assistants**: Discover via Agent Skills, invoke CLI commands

**External Systems**:
- **Git**: Repository state, history (required)
- **ast-grep**: AST pattern matching (optional)
- **ripgrep**: Content search (optional)
- **Agent Skills Ecosystem**: Distribution channel (output)

### 2.2 Container Diagram (C4 Level 2) — Three-Layer Architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│                              raise-cli                                    │
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │                    PRESENTATION LAYER (CLI)                          │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                  │ │
│  │  │  Commands   │  │   Output    │  │   Errors    │                  │ │
│  │  │   (Typer)   │  │   (Rich)    │  │  (Handler)  │                  │ │
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘                  │ │
│  └─────────┼────────────────┼────────────────┼──────────────────────────┘ │
│            │                │                │                            │
│            ▼                ▼                ▼                            │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │                    APPLICATION LAYER (Handlers)                      │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐  │ │
│  │  │    Kata     │  │    Gate     │  │     SAR     │  │  Context   │  │ │
│  │  │  Handler    │  │  Handler    │  │   Handler   │  │  Handler   │  │ │
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └─────┬──────┘  │ │
│  └─────────┼────────────────┼────────────────┼───────────────┼─────────┘ │
│            │                │                │               │           │
│            ▼                ▼                ▼               ▼           │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │                      DOMAIN LAYER (Engines)                          │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐  │ │
│  │  │    Kata     │  │    Gate     │  │     SAR     │  │  Context   │  │ │
│  │  │   Engine    │  │   Engine    │  │   Engine    │  │ Generator  │  │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └────────────┘  │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│            │                │                │               │           │
│            ▼                ▼                ▼               ▼           │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │                         CORE LAYER                                   │ │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────┐  │ │
│  │  │ Schemas  │ │ Settings │ │  State   │ │ Metrics  │ │Exceptions │  │ │
│  │  │(Pydantic)│ │(Pydantic)│ │ (JSON)   │ │ (JSON)   │ │ (Errors)  │  │ │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └───────────┘  │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
   ┌───────────┐        ┌───────────┐        ┌───────────┐
   │  .raise/  │        │ ast-grep  │        │  ripgrep  │
   │  katas/   │        └───────────┘        └───────────┘
   │  gates/   │
   │ commands/ │
   └───────────┘
```

### 2.3 Component Diagram (C4 Level 3)

```
src/raise_cli/
├── __init__.py             # Package metadata, version
├── __main__.py             # Entry point: python -m raise_cli
├── exceptions.py           # Centralized error hierarchy
│
├── cli/                    # PRESENTATION LAYER
│   ├── __init__.py
│   ├── main.py             # Typer app, global options (-v, -q, --format)
│   ├── commands/           # Command modules
│   │   ├── __init__.py
│   │   ├── kata.py         # raise kata [list|run|status]
│   │   ├── gate.py         # raise gate [check|list]
│   │   ├── analyze.py      # raise analyze
│   │   ├── context.py      # raise context [generate]
│   │   └── metrics.py      # raise metrics [show|export]
│   └── error_handler.py    # Error presentation with Rich
│
├── output/                 # OUTPUT FORMATTING
│   ├── __init__.py
│   ├── console.py          # Rich console singleton
│   ├── formatters.py       # JSON, human, table formatters
│   └── progress.py         # Spinners, progress bars
│
├── handlers/               # APPLICATION LAYER
│   ├── __init__.py
│   ├── kata_handler.py     # KataHandler (orchestrates kata use cases)
│   ├── gate_handler.py     # GateHandler (orchestrates gate validation)
│   ├── sar_handler.py      # SARHandler (orchestrates analysis)
│   └── context_handler.py  # ContextHandler (orchestrates generation)
│
├── engines/                # DOMAIN LAYER (stable, CLI-agnostic)
│   ├── __init__.py
│   ├── kata.py             # KataEngine (pure business logic)
│   ├── gate.py             # GateEngine (pure business logic)
│   ├── sar.py              # SAREngine (pure business logic)
│   └── context.py          # ContextGenerator (pure business logic)
│
├── schemas/                # DATA MODELS
│   ├── __init__.py
│   ├── kata.py             # KataDefinition, KataState, KataResult
│   ├── gate.py             # GateDefinition, GateResult, CriterionResult
│   ├── sar.py              # SARReport, CodePattern, Technology
│   └── metrics.py          # ExecutionMetric, MetricsSummary
│
├── config/                 # CONFIGURATION
│   ├── __init__.py
│   ├── settings.py         # RaiseSettings (Pydantic Settings)
│   ├── loader.py           # Config file discovery and loading
│   └── paths.py            # XDG-compliant directory helpers
│
└── core/                   # UTILITIES
    ├── __init__.py
    ├── state.py            # State persistence (JSON)
    ├── discovery.py        # .raise/ content discovery
    └── subprocess.py       # git, ast-grep, ripgrep wrappers
```

### 2.4 Layer Responsibilities

| Layer | Responsibility | May Import |
|-------|----------------|------------|
| **Presentation (cli/)** | Parse args, format output, handle errors | handlers, output, config |
| **Application (handlers/)** | Orchestrate use cases, translate errors | engines, schemas, config |
| **Domain (engines/)** | Pure business logic, no I/O awareness | schemas only |
| **Core** | Shared utilities, schemas, config | Nothing from upper layers |

**Key Rule**: Dependencies flow inward. Engines never import from CLI or handlers.

---

## 3. Configuration Management

### 3.1 Configuration Precedence

Standard cascade (highest to lowest priority):

1. **CLI arguments** (`--format json`, `-v`)
2. **Environment variables** (`RAISE_OUTPUT_FORMAT=json`)
3. **Project config** (`pyproject.toml` `[tool.raise]`)
4. **User config** (`~/.config/raise/config.toml`)
5. **System defaults** (hardcoded)

### 3.2 Pydantic Settings

```python
# config/settings.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from pathlib import Path
from typing import Literal

class RaiseSettings(BaseSettings):
    """Configuration for raise-cli with proper precedence."""

    model_config = SettingsConfigDict(
        env_prefix="RAISE_",
        env_file=".env",
        toml_file="pyproject.toml",
        extra="ignore"
    )

    # Output settings
    output_format: Literal["human", "json", "table"] = "human"
    color: bool = True
    verbosity: int = Field(default=0, ge=-1, le=3)  # -1=quiet, 0=normal, 1-3=verbose

    # Paths (project-level)
    raise_dir: Path = Path(".raise")
    governance_dir: Path = Path("governance")
    work_dir: Path = Path("work")

    # External tools
    ast_grep_path: str | None = None
    ripgrep_path: str | None = None

    # Feature flags
    interactive: bool = False
```

### 3.3 XDG Directory Compliance

```python
# config/paths.py
import os
from pathlib import Path

def get_config_dir() -> Path:
    """XDG config directory: ~/.config/raise/"""
    xdg = os.environ.get("XDG_CONFIG_HOME")
    base = Path(xdg) if xdg else Path.home() / ".config"
    return base / "raise"

def get_cache_dir() -> Path:
    """XDG cache directory: ~/.cache/raise/"""
    xdg = os.environ.get("XDG_CACHE_HOME")
    base = Path(xdg) if xdg else Path.home() / ".cache"
    return base / "raise"

def get_data_dir() -> Path:
    """XDG data directory: ~/.local/share/raise/"""
    xdg = os.environ.get("XDG_DATA_HOME")
    base = Path(xdg) if xdg else Path.home() / ".local" / "share"
    return base / "raise"
```

### 3.4 Config File Format

```toml
# pyproject.toml
[tool.raise]
output_format = "human"
color = true
verbosity = 0

# User config: ~/.config/raise/config.toml
[raise]
output_format = "json"  # Override for CI/scripts
color = false
```

---

## 4. Error Handling

### 4.1 Exception Hierarchy

```python
# exceptions.py
from typing import Any

class RaiseError(Exception):
    """Base exception for all raise-cli errors."""
    exit_code: int = 1
    error_code: str = "E000"

    def __init__(
        self,
        message: str,
        *,
        hint: str | None = None,
        details: dict[str, Any] | None = None
    ):
        self.message = message
        self.hint = hint
        self.details = details or {}
        super().__init__(message)


class ConfigurationError(RaiseError):
    """Configuration-related errors."""
    exit_code = 2
    error_code = "E001"


class KataNotFoundError(RaiseError):
    """Kata definition not found."""
    exit_code = 3
    error_code = "E002"


class GateNotFoundError(RaiseError):
    """Gate definition not found."""
    exit_code = 3
    error_code = "E003"


class ArtifactNotFoundError(RaiseError):
    """Artifact file not found."""
    exit_code = 4
    error_code = "E004"


class DependencyError(RaiseError):
    """External dependency not available."""
    exit_code = 5
    error_code = "E005"


class StateError(RaiseError):
    """State file corrupted or invalid."""
    exit_code = 6
    error_code = "E006"


class ValidationError(RaiseError):
    """Schema or artifact validation failed."""
    exit_code = 7
    error_code = "E007"


class GateFailedError(RaiseError):
    """Gate validation did not pass."""
    exit_code = 10
    error_code = "E010"
```

### 4.2 Exit Codes

| Code | Meaning | Exception |
|------|---------|-----------|
| 0 | Success | — |
| 1 | General error | `RaiseError` |
| 2 | Configuration error | `ConfigurationError` |
| 3 | Resource not found | `KataNotFoundError`, `GateNotFoundError` |
| 4 | Artifact not found | `ArtifactNotFoundError` |
| 5 | Dependency unavailable | `DependencyError` |
| 6 | State corruption | `StateError` |
| 7 | Validation error | `ValidationError` |
| 10 | Gate failed | `GateFailedError` |

### 4.3 Error Presentation

```python
# cli/error_handler.py
from rich.console import Console
from rich.panel import Panel
from raise_cli.exceptions import RaiseError

console = Console(stderr=True)

def handle_error(error: RaiseError) -> int:
    """Format and display error with Rich."""
    console.print(Panel(
        f"[bold red]{error.message}[/]",
        title=f"[red]Error {error.error_code}[/]",
        border_style="red"
    ))

    if error.details:
        console.print("\n[dim]Details:[/]")
        for key, value in error.details.items():
            console.print(f"  • {key}: {value}")

    if error.hint:
        console.print(f"\n[cyan]Hint:[/] {error.hint}")

    return error.exit_code
```

---

## 5. Output Formatting

### 5.1 Format Flag Pattern

```python
# cli/main.py
from enum import Enum
from typing import Annotated
import typer

class OutputFormat(str, Enum):
    human = "human"
    json = "json"
    table = "table"

app = typer.Typer()

@app.callback()
def main(
    ctx: typer.Context,
    format: Annotated[OutputFormat, typer.Option(
        "--format", "-f",
        help="Output format"
    )] = OutputFormat.human,
    verbose: Annotated[int, typer.Option(
        "-v", "--verbose",
        count=True,
        help="Increase verbosity (-v, -vv, -vvv)"
    )] = 0,
    quiet: Annotated[bool, typer.Option(
        "-q", "--quiet",
        help="Suppress non-error output"
    )] = False,
):
    """RaiSE CLI - Reliable AI Software Engineering."""
    ctx.ensure_object(dict)
    ctx.obj["format"] = format
    ctx.obj["verbosity"] = -1 if quiet else min(verbose, 3)
```

### 5.2 Output Module

```python
# output/formatters.py
from typing import Any
from rich.console import Console
from rich.table import Table
import json

console = Console()

def output(data: Any, format: str, title: str | None = None):
    """Output data in specified format."""
    if format == "json":
        console.print_json(data=data)
    elif format == "table":
        print_table(data, title)
    else:
        print_human(data, title)

def print_table(data: list[dict], title: str | None = None):
    """Print data as Rich table."""
    if not data:
        console.print("[dim]No data[/]")
        return

    table = Table(title=title)
    for key in data[0].keys():
        table.add_column(key.replace("_", " ").title())

    for row in data:
        table.add_row(*[str(v) for v in row.values()])

    console.print(table)

def print_human(data: Any, title: str | None = None):
    """Print human-readable output."""
    if title:
        console.print(f"[bold]{title}[/]\n")
    console.print(data)
```

### 5.3 Progress Indicators

```python
# output/progress.py
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.console import Console
from contextlib import contextmanager

console = Console()

@contextmanager
def spinner(message: str):
    """Show spinner for long operations."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        progress.add_task(description=message, total=None)
        yield
```

---

## 6. Data Contracts

### 6.1 CLI Commands (Public API)

```yaml
# Global options (all commands)
--format, -f: enum[human, json, table]  # Output format
--verbose, -v: count                     # Verbosity level (up to -vvv)
--quiet, -q: bool                        # Suppress non-error output

# Kata Commands
raise kata list:
  output: List[KataSummary]

raise kata run <kata-id>:
  args:
    kata_id: str          # e.g., "project/discovery"
    --project: str?       # Project name
    --interactive: bool   # Guided mode
  output: KataExecutionResult

raise kata status:
  args:
    --project: str?       # Filter by project
  output: List[KataState]

# Gate Commands
raise gate list:
  output: List[GateSummary]

raise gate check <gate-id>:
  args:
    gate_id: str          # e.g., "gate-discovery"
    --artifact: str?      # Path to artifact
  output: GateResult

# Analysis Commands
raise analyze:
  args:
    --path: str           # Directory to analyze (default: .)
    --output: str?        # Output path for SAR
  output: SARReport

# Context Commands
raise context generate:
  args:
    --format: enum[claude, cursor, both]
    --output: str?        # Output path
  output: ContextFiles

# Metrics Commands
raise metrics show:
  output: MetricsSummary

raise metrics export:
  args:
    --output: str?        # Output path
  output: MetricsExport
```

### 6.2 Core Schemas

```python
# schemas/kata.py
from pydantic import BaseModel
from datetime import datetime
from typing import Literal

class KataDefinition(BaseModel):
    """Parsed kata definition from .raise/katas/*.md"""
    id: str
    titulo: str
    work_cycle: Literal["solution", "project", "feature", "setup"]
    frequency: str
    prerequisites: list[str] = []
    template: str | None = None
    gate: str | None = None
    next_kata: str | None = None
    steps: list["KataStep"]

class KataStep(BaseModel):
    number: int
    title: str
    description: str
    verification: str
    jidoka_action: str | None = None

class KataState(BaseModel):
    """Execution state for a kata instance"""
    kata_id: str
    project: str | None = None
    status: Literal["not_started", "in_progress", "completed", "blocked"]
    current_step: int = 0
    started_at: datetime | None = None
    completed_at: datetime | None = None

class KataExecutionResult(BaseModel):
    kata_id: str
    status: Literal["completed", "blocked", "error"]
    steps_completed: int
    total_steps: int
    output_artifacts: list[str] = []
    duration_seconds: float
```

```python
# schemas/gate.py
class GateDefinition(BaseModel):
    """Parsed gate definition from .raise/gates/*.md"""
    id: str
    work_cycle: str
    titulo: str
    blocking: bool
    criteria: list["GateCriterion"]

class GateCriterion(BaseModel):
    number: int
    criterion: str
    verification: str
    required: bool  # Must vs Should

class GateResult(BaseModel):
    """Result of gate validation"""
    gate_id: str
    artifact_path: str
    passed: bool
    criteria_results: list["CriterionResult"]
    timestamp: datetime
    duration_seconds: float

class CriterionResult(BaseModel):
    criterion_id: int
    criterion: str
    passed: bool
    required: bool
    details: str | None = None
```

```python
# schemas/sar.py
class SARReport(BaseModel):
    """Structure Analysis Report"""
    project_path: str
    generated_at: datetime
    summary: "SARSummary"
    structure: "DirectoryStructure"
    patterns: list["CodePattern"]
    technologies: list["Technology"]

class SARSummary(BaseModel):
    total_files: int
    total_lines: int
    languages: dict[str, int]  # language -> line count

class CodePattern(BaseModel):
    pattern_type: str  # e.g., "class", "function", "import"
    name: str
    file_path: str
    line_number: int

class Technology(BaseModel):
    name: str
    category: str  # e.g., "framework", "library", "tool"
    confidence: float  # 0.0 - 1.0
    evidence: list[str]  # Files that indicate this tech
```

---

## 7. Data Flows

### 7.1 Kata Execution Flow (Three-Layer)

```
┌───────────┐     ┌───────────┐     ┌───────────┐     ┌───────────┐
│    CLI    │────▶│  Handler  │────▶│  Engine   │────▶│   State   │
│ (command) │     │(orchestra)│     │  (logic)  │     │  (JSON)   │
└───────────┘     └───────────┘     └───────────┘     └───────────┘
      │                 │                 │
      │                 │                 ▼
      │                 │           ┌───────────┐
      │                 │           │  .raise/  │
      │                 │           │  katas/   │
      │                 │           └───────────┘
      │                 │
      ▼                 ▼
┌───────────┐     ┌───────────┐
│  Output   │     │  Metrics  │
│  (Rich)   │     │  (JSON)   │
└───────────┘     └───────────┘
```

1. **CLI Layer**: Parses `raise kata run project/discovery`, validates args
2. **Handler Layer**: Creates `KataHandler`, orchestrates execution
3. **Engine Layer**: `KataEngine` loads definition, processes steps
4. **State**: Persisted to `.raise/state/katas.json`
5. **Output**: Formatted via Rich (human) or JSON

### 7.2 Handler Pattern Example

```python
# handlers/kata_handler.py
from raise_cli.engines.kata import KataEngine
from raise_cli.schemas.kata import KataExecutionResult
from raise_cli.exceptions import KataNotFoundError
from raise_cli.core.state import StateManager

class KataHandler:
    """Application layer: orchestrates kata use cases."""

    def __init__(self, settings: RaiseSettings):
        self.engine = KataEngine(settings.raise_dir)
        self.state = StateManager(settings.raise_dir / "state")

    def run_kata(
        self,
        kata_id: str,
        project: str | None = None,
        interactive: bool = False
    ) -> KataExecutionResult:
        """Execute a kata with full orchestration."""
        # Load kata definition
        kata = self.engine.load_kata(kata_id)
        if not kata:
            raise KataNotFoundError(
                f"Kata '{kata_id}' not found",
                hint=f"Run 'raise kata list' to see available katas",
                details={"searched": str(self.engine.katas_dir / f"{kata_id}.md")}
            )

        # Check prerequisites
        self._check_prerequisites(kata, project)

        # Load or create state
        state = self.state.get_kata_state(kata_id, project)

        # Execute kata
        result = self.engine.execute(kata, state, interactive)

        # Update state and metrics
        self.state.save_kata_state(state)
        self._record_metric(result)

        return result
```

---

## 8. Security

| Aspect | Measure |
|--------|---------|
| **Secrets** | Never store in config; use environment variables |
| **File access** | Respect .gitignore; filter .env, credentials files |
| **Subprocess** | Validate paths before passing to ast-grep/ripgrep; no shell=True |
| **Output** | Filter potential secrets from context generation |
| **Dependencies** | Pin versions; audit with `pip-audit` |
| **User input** | Validate all paths; prevent directory traversal |

---

## 9. Testing Strategy

### 9.1 Test Structure

```
tests/
├── conftest.py              # Shared fixtures
├── unit/                    # Unit tests (engines, schemas)
│   ├── test_kata_engine.py
│   ├── test_gate_engine.py
│   ├── test_sar_engine.py
│   └── test_schemas.py
├── integration/             # Integration tests (handlers + engines)
│   ├── test_kata_handler.py
│   └── test_gate_handler.py
├── cli/                     # CLI tests (CliRunner)
│   ├── test_kata_commands.py
│   ├── test_gate_commands.py
│   └── test_output_formats.py
├── e2e/                     # End-to-end workflows
│   └── test_full_workflow.py
└── fixtures/                # Test data
    ├── raise/               # Mock .raise directory
    └── projects/            # Sample projects
```

### 9.2 CliRunner Pattern (Typer)

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
    """Invoke CLI and return result."""
    def invoke(*args, catch_exceptions=False, **kwargs):
        return runner.invoke(app, list(args), catch_exceptions=catch_exceptions, **kwargs)
    return invoke

# tests/cli/test_kata_commands.py
def test_kata_list(cli):
    result = cli("kata", "list")
    assert result.exit_code == 0
    assert "project/discovery" in result.stdout

def test_kata_list_json(cli):
    result = cli("kata", "list", "--format", "json")
    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert isinstance(data, list)

def test_kata_run_not_found(cli):
    result = cli("kata", "run", "nonexistent/kata")
    assert result.exit_code == 3  # KataNotFoundError
    assert "not found" in result.stdout.lower()
```

### 9.3 Isolated Filesystem Tests

```python
# tests/integration/test_kata_handler.py
def test_kata_execution(tmp_path):
    # Create mock .raise structure
    raise_dir = tmp_path / ".raise"
    raise_dir.mkdir()
    katas_dir = raise_dir / "katas" / "project"
    katas_dir.mkdir(parents=True)

    (katas_dir / "test.md").write_text("""---
id: test
titulo: Test Kata
work_cycle: project
---
# Test Kata
## Paso 1
Test step
""")

    settings = RaiseSettings(raise_dir=raise_dir)
    handler = KataHandler(settings)

    result = handler.run_kata("project/test")
    assert result.status == "completed"
```

### 9.4 Mocking External Tools

```python
# tests/unit/test_sar_engine.py
from unittest.mock import patch, MagicMock

def test_sar_without_ast_grep():
    """SAR should work without ast-grep (graceful degradation)."""
    with patch("raise_cli.core.subprocess.which", return_value=None):
        engine = SAREngine()
        report = engine.analyze(Path("."))

        assert report.patterns == []  # No patterns without ast-grep
        assert report.summary.total_files > 0  # Basic analysis still works
```

---

## 10. Decisions and Trade-offs

### 10.1 Key Decisions

| Decision | Rationale |
|----------|-----------|
| Three-layer architecture | Industry standard (Poetry, HTTPie); testable, maintainable |
| Pydantic Settings for config | Type-safe, automatic env/file precedence |
| Rich for output | De facto standard for Python CLI UX |
| XDG directory compliance | Standard locations for state/cache |
| Handlers between CLI and engines | Separates orchestration from pure logic |
| Exit codes per error type | CI/CD integration, scripting support |

### 10.2 Alternatives Rejected

| Alternative | Reason for Rejection |
|-------------|----------------------|
| Direct CLI → Engine calls | Mixing orchestration with presentation |
| Custom config parsing | Pydantic Settings handles precedence automatically |
| Print statements for output | Rich provides better UX, JSON mode, terminal detection |
| Single exit code | Harder to script, no error categorization |

### 10.3 Open Questions

- [ ] How to handle kata definitions with embedded code blocks?
- [ ] Should gate validation support custom Python validators?
- [ ] Best approach for kata template variable substitution (Jinja2 vs custom)?

---

## 11. Distribution

### 11.1 Package Structure

```
raise-cli/
├── src/
│   └── raise_cli/          # Main package
├── tests/                  # Test suite
├── raise/
│   └── SKILL.md            # Agent Skill for ecosystem distribution
├── pyproject.toml          # Package metadata (uv/pip)
├── README.md
└── LICENSE                 # MIT
```

### 11.2 Installation

```bash
# Primary (recommended)
pip install raise-cli

# Alternative
uv pip install raise-cli
pipx install raise-cli

# From source
git clone ... && cd raise-cli && pip install -e .
```

### 11.3 Agent Skill

```markdown
# raise/SKILL.md
---
name: raise
description: Reliable AI Software Engineering - governance CLI for AI-assisted development
metadata:
  author: humansys
  version: "2.0"
---

# RaiSE Governance

Use `raise-cli` for deterministic governance of AI-assisted development.

## Installation
pip install raise-cli

## Core Commands
- `raise kata run <kata-id>` — Execute governance katas
- `raise gate check <gate-id>` — Validate artifacts against gates
- `raise analyze` — Brownfield codebase analysis (SAR)
- `raise context generate` — Generate CLAUDE.md from governance

## Global Options
- `--format json|human|table` — Output format
- `-v/-vv/-vvv` — Increase verbosity
- `-q` — Quiet mode (errors only)
```

---

## 12. Observability

### 12.1 Metrics Storage

```json
// ~/.local/share/raise/metrics.json (XDG data dir)
{
  "version": "1.0",
  "executions": [
    {
      "timestamp": "2026-01-30T10:30:00Z",
      "command": "kata run project/discovery",
      "duration_seconds": 5.2,
      "exit_code": 0,
      "details": {"steps_completed": 9}
    }
  ]
}
```

### 12.2 Verbosity Levels

| Level | Flag | Output |
|-------|------|--------|
| Quiet | `-q` | Errors only |
| Normal | (default) | Standard output |
| Verbose | `-v` | Additional info |
| Debug | `-vv` | Debug details |
| Trace | `-vvv` | Full trace |

---

## 13. Traceability

| Source | Artifact | Relationship |
|--------|----------|--------------|
| PRD | `governance/projects/raise-cli/prd.md` | Requirements |
| Vision | `governance/projects/raise-cli/vision.md` | Architecture direction |
| Solution Vision | `governance/solution/vision.md` | System constraints |
| CLI Research | `work/research/outputs/python-cli-architecture-analysis.md` | Best practices |
| Backlog | `governance/projects/raise-cli/backlog.md` | Implementation tasks (next) |

---

## 14. Approvals

| Role | Name | Date | Status |
|------|------|------|--------|
| Technical Lead | Emilio Osorio | 2026-01-30 | Pending |
| Architect | Emilio Osorio | 2026-01-30 | Pending |

---

## Changelog

| Version | Date | Author | Change |
|---------|------|--------|--------|
| 1.0.0 | 2026-01-30 | Claude Opus 4.5 | Initial version |
| 1.1.0 | 2026-01-30 | Claude Opus 4.5 | Added three-layer architecture, Pydantic Settings, XDG compliance, error hierarchy, Rich output, CliRunner testing (based on Python CLI best practices research) |

---

*Generated by: `project/design` kata*
*Template: tech-design v1*
