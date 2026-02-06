# CLI Anti-Patterns Scan Report

> Scan of `src/raise_cli/cli/` against `governance/solution/guardrails-stack.md` Section 2 (CLI)

**Date:** 2026-02-05
**Scanned:** 12 files in `src/raise_cli/cli/`

---

## Summary

| Severity | Count |
|----------|-------|
| High | 2 |
| Medium | 5 |
| Low | 3 |
| **Total** | **10** |

---

## Findings

### 1. print() Instead of Rich Console

**Guideline:** Use Rich Console for all output to enable consistent formatting and markup.

#### Finding 1.1 (Low)

**File:** `/home/emilio/Code/raise-commons/src/raise_cli/cli/error_handler.py:109`

```python
print(output, file=sys.stderr)
```

**Analysis:** This is in `_handle_error_json()` for JSON output to stderr. Using `print()` here is acceptable since JSON output should be plain text without Rich formatting.

**Verdict:** Acceptable - JSON output should be plain.

---

#### Finding 1.2 (Medium)

**File:** `/home/emilio/Code/raise-commons/src/raise_cli/cli/commands/profile.py:50-60`

```python
typer.echo(
    "No developer profile found. Run `raise init` in a project to create one."
)
...
typer.echo(output.rstrip())
```

**Analysis:** Uses `typer.echo()` throughout instead of `console.print()` from Rich. Other commands in the codebase use Rich Console consistently.

**Suggested Fix:**
```python
from rich.console import Console
console = Console()

# Replace typer.echo with:
console.print("No developer profile found. Run [cyan]raise init[/cyan] to create one.")
```

---

#### Finding 1.3 (Medium)

**File:** `/home/emilio/Code/raise-commons/src/raise_cli/cli/commands/status.py:74-128`

```python
typer.echo("RaiSE Project Status")
typer.echo("─" * 20)
typer.echo(f"Project: {project_info['name']} ({project_info['type']})")
# ... 20+ more typer.echo() calls
```

**Analysis:** Entire module uses `typer.echo()` instead of Rich Console. Inconsistent with other commands (graph, memory, context, discover) which all use Rich.

**Suggested Fix:**
```python
from rich.console import Console
console = Console()

console.print("[bold]RaiSE Project Status[/bold]")
console.print("─" * 20)
console.print(f"Project: [cyan]{project_info['name']}[/cyan] ({project_info['type']})")
```

---

### 2. sys.exit() Instead of raise typer.Exit()

**Guideline:** Use `raise typer.Exit(code)` for proper Typer exception handling.

**Finding:** No violations found. All exit points correctly use `raise typer.Exit()`.

**Evidence:** 42 occurrences of `typer.Exit` found, 0 occurrences of `sys.exit()` in command code.

---

### 3. Multiple Required Positional Arguments

**Guideline:** One positional argument is OK; prefer flags for additional parameters.

#### Finding 3.1 (High)

**File:** `/home/emilio/Code/raise-commons/src/raise_cli/cli/commands/memory.py:409-414`

```python
@memory_app.command("add-calibration")
def add_calibration_cmd(
    feature: Annotated[str, typer.Argument(help="Feature ID (e.g., F3.5)")],
    name: Annotated[str, typer.Argument(help="Feature name")],
    size: Annotated[str, typer.Argument(help="T-shirt size (XS, S, M, L, XL)")],
    actual: Annotated[int, typer.Argument(help="Actual minutes")],
```

**Analysis:** 4 required positional arguments. Order is unclear and inflexible. Compare to guardrails which say "One positional is OK".

**Suggested Fix:**
```python
@memory_app.command("add-calibration")
def add_calibration_cmd(
    feature: Annotated[str, typer.Argument(help="Feature ID (e.g., F3.5)")],  # Keep one positional
    name: Annotated[str, typer.Option("--name", "-n", help="Feature name")],
    size: Annotated[str, typer.Option("--size", "-s", help="T-shirt size (XS, S, M, L, XL)")],
    actual: Annotated[int, typer.Option("--actual", "-a", help="Actual minutes")],
```

---

#### Finding 3.2 (Medium)

**File:** `/home/emilio/Code/raise-commons/src/raise_cli/cli/commands/telemetry.py:200-209`

```python
@telemetry_app.command("emit")
def emit_work(
    work_type: Annotated[str, typer.Argument(help="Work type (epic, feature)")],
    work_id: Annotated[str, typer.Argument(help="Work ID (e.g., E9, F9.4)")],
```

**Analysis:** 2 positional arguments. Less severe than 4, but still unclear order.

**Suggested Fix:**
```python
def emit_work(
    work_id: Annotated[str, typer.Argument(help="Work ID (e.g., E9, F9.4)")],  # Keep most important
    work_type: Annotated[str, typer.Option("--type", "-t", help="Work type (epic, feature)")] = "feature",
```

---

### 4. Missing --help Text on Options

**Guideline:** All options should have descriptive help text.

**Finding:** No violations found. All `typer.Option()` calls include `help=` parameter.

**Evidence:** Reviewed all 56 `typer.Option()` occurrences - all have help text.

---

### 5. Inconsistent Output Formats

**Guideline:** Support `--format` with human (default), json, table.

#### Finding 5.1 (High)

**File:** `/home/emilio/Code/raise-commons/src/raise_cli/cli/commands/profile.py`

**Analysis:** No `--format` option. Only outputs YAML format for `show` command.

| Command | Has --format | Formats Supported |
|---------|--------------|-------------------|
| profile show | No | YAML only |
| profile session | No | Text only |
| profile session-end | No | Text only |

**Suggested Fix:**
```python
@profile_app.command()
def show(
    format: Annotated[
        str,
        typer.Option("--format", "-f", help="Output format (yaml, json, human)"),
    ] = "yaml",
) -> None:
```

---

#### Finding 5.2 (Medium)

**File:** `/home/emilio/Code/raise-commons/src/raise_cli/cli/commands/status.py`

**Analysis:** No `--format` option. Only outputs human-readable text.

**Suggested Fix:**
```python
@status_app.callback(invoke_without_command=True)
def status(
    ctx: typer.Context,
    format: Annotated[
        str,
        typer.Option("--format", "-f", help="Output format (human, json)"),
    ] = "human",
) -> None:
```

---

#### Finding 5.3 (Low)

**File:** `/home/emilio/Code/raise-commons/src/raise_cli/cli/commands/init.py`

**Analysis:** No `--format` option. Acceptable since init is an interactive command that should always output human-readable text.

**Verdict:** Acceptable - interactive commands don't need JSON output.

---

### Format Support Summary

| Command Group | --format Support | Formats |
|---------------|------------------|---------|
| context | Yes | markdown, json |
| graph | Yes | human, json |
| memory | Yes | markdown, json, table |
| discover | Yes | human, json, summary |
| telemetry | No | human only |
| profile | No | yaml/text only |
| status | No | human only |
| init | No | human only (acceptable) |

---

## Recommendations

### Priority 1 (High - Fix Before Release)

1. **memory add-calibration:** Refactor 4 positional args to 1 positional + 3 flags
2. **profile commands:** Add `--format` option with json support

### Priority 2 (Medium - Fix in Next Sprint)

3. **status command:** Add `--format` option with json support
4. **profile.py:** Migrate from `typer.echo()` to Rich Console
5. **status.py:** Migrate from `typer.echo()` to Rich Console
6. **telemetry emit:** Refactor 2 positional to 1 positional + 1 flag

### Priority 3 (Low - Tech Debt)

7. **telemetry commands:** Add `--format` option for scripting

---

## Files Reviewed

```
src/raise_cli/cli/
├── __init__.py
├── main.py
├── error_handler.py
└── commands/
    ├── __init__.py
    ├── context.py      ✓ Rich + format support
    ├── discover.py     ✓ Rich + format support
    ├── graph.py        ✓ Rich + format support
    ├── init.py         ✓ Rich (format N/A)
    ├── memory.py       ! 4 positional args
    ├── profile.py      ! typer.echo, no format
    ├── status.py       ! typer.echo, no format
    └── telemetry.py    ! 2 positional args
```

---

*Generated by CLI anti-pattern scan*
*Guardrails source: governance/solution/guardrails-stack.md Section 2*
