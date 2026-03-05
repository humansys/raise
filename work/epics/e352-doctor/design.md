---
epic_id: "E352"
grounded_in: "Gemba of src/rai_cli/gates/ (protocol, registry, models), dev/research/e352-doctor-research.md"
---

# Epic Design: rai doctor

## Affected Surface (Gemba)

| Module/File | Current State | Changes |
|-------------|---------------|---------|
| `src/rai_cli/doctor/` | Does not exist | New module: protocol, registry, checks, CLI |
| `src/rai_cli/cli/commands/doctor.py` | Does not exist | New Typer command group |
| `src/rai_cli/gates/` | Existing gate system | No changes — separate domain |
| `pyproject.toml` | Has `rai.gates` entry points | Add `rai.doctor.checks` entry point group |

## Target Components

| Component | Responsibility | Key Interface |
|-----------|---------------|---------------|
| `doctor.protocol` | DoctorCheck contract | `DoctorCheck` Protocol class |
| `doctor.models` | Check result types | `CheckResult`, `CheckStatus` |
| `doctor.registry` | Auto-discover checks via entry points | `CheckRegistry.discover()` |
| `doctor.runner` | Execute checks in pipeline order | `run_checks() -> list[CheckResult]` |
| `doctor.report` | Generate diagnostic report, mailto | `generate_report()`, `open_mailto()` |
| `doctor.checks.environment` | Python, OS, versions, extras | Entry point: `environment` |
| `doctor.checks.project` | .raise/ structure, manifest, graph | Entry point: `project` |
| `doctor.checks.adapters` | Adapter config, env vars | Entry point: `adapters` |
| `doctor.checks.skills` | Skill sync, deployment | Entry point: `skills` |
| `doctor.checks.mcp` | MCP server health (--online only) | Entry point: `mcp` |
| `cli/commands/doctor.py` | CLI surface | `rai doctor [-v] [--json] [--fix] [--online] [category]` |

## Key Contracts

```python
# --- doctor/models.py ---

from enum import Enum
from dataclasses import dataclass

class CheckStatus(Enum):
    PASS = "pass"
    WARN = "warn"
    ERROR = "error"

@dataclass(frozen=True)
class CheckResult:
    check_id: str        # e.g. "env-python-version"
    category: str        # e.g. "environment"
    status: CheckStatus
    message: str         # human-readable summary
    fix_hint: str = ""   # actionable suggestion (e.g. "run: pip install rai-cli[mcp]")
    details: tuple[str, ...] = ()


# --- doctor/protocol.py ---

from typing import ClassVar, Protocol, runtime_checkable

@runtime_checkable
class DoctorCheck(Protocol):
    check_id: ClassVar[str]
    category: ClassVar[str]        # groups checks in output
    description: ClassVar[str]
    requires_online: ClassVar[bool] = False  # skipped unless --online

    def evaluate(self, context: DoctorContext) -> list[CheckResult]: ...


@dataclass(frozen=True)
class DoctorContext:
    working_dir: Path
    online: bool = False  # --online flag
    verbose: bool = False


# --- doctor/registry.py ---
# Same pattern as gates/registry.py but with:
EP_DOCTOR: str = "rai.doctor.checks"


# --- doctor/runner.py ---
PIPELINE_ORDER: list[str] = [
    "environment",   # must pass before others
    "project",       # .raise/ structure
    "adapters",      # adapter config
    "skills",        # skill sync
    "mcp",           # MCP servers (online only)
]

def run_checks(
    registry: CheckRegistry,
    context: DoctorContext,
    categories: list[str] | None = None,  # filter to specific categories
) -> list[CheckResult]:
    """Execute checks in pipeline order, skip downstream on critical failure."""
    ...
```

## Report Schema

```python
# --- doctor/report.py ---

@dataclass
class DiagnosticReport:
    """Non-sensitive diagnostic snapshot."""
    timestamp: str
    rai_version: str
    python_version: str
    os_info: str
    check_results: list[CheckResult]
    raise_structure: list[str]    # file names only, no contents
    installed_extras: list[str]
    mcp_server_names: list[str]   # names only, no credentials
    adapter_types: list[str]      # types only, no config values

def generate_report(results: list[CheckResult], working_dir: Path) -> DiagnosticReport:
    """Collect non-sensitive data into report."""
    ...

def report_to_markdown(report: DiagnosticReport) -> str:
    """Render report as markdown for email body."""
    ...

def open_mailto(report: DiagnosticReport, to: str = "support@raise.humansys.ai") -> bool:
    """Open default email client via mailto: URI. Returns True if opened."""
    # Uses webbrowser.open(f"mailto:{to}?subject=...&body=...")
    # Fallback: copy to clipboard + print instructions
    ...
```

## CLI Surface

```
rai doctor                    # all checks, problems only (exit 0/1)
rai doctor -v                 # verbose: all checks including passing
rai doctor --json             # JSON output for CI
rai doctor --online           # include MCP/adapter connectivity checks
rai doctor --fix              # auto-remediate with .bak backup
rai doctor environment        # single category
rai doctor report             # write report to .raise/rai/personal/
rai doctor report --send      # open mailto: with report content
```

## Entry Points (pyproject.toml)

```toml
[project.entry-points."rai.doctor.checks"]
environment = "rai_cli.doctor.checks.environment:EnvironmentCheck"
project = "rai_cli.doctor.checks.project:ProjectCheck"
adapters = "rai_cli.doctor.checks.adapters:AdapterCheck"
skills = "rai_cli.doctor.checks.skills:SkillCheck"
mcp = "rai_cli.doctor.checks.mcp:McpCheck"
```

## Migration Path

Greenfield — no existing doctor module. No backward compatibility needed.
Gate system unchanged — separate domain, separate entry points.
