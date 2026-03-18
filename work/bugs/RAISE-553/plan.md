# Bug Plan: RAISE-553

## Tasks

### T1 — Regression tests (RED)
File: tests/cli/test_backlog_errors.py
Tests: para cada uno de los 7 comandos afectados, verificar que:
- adapter lanza Exception → exit code 1
- output contiene "[red]Error:[/red]" (o "Error:") y NO contiene "Traceback"
Commit: test(RAISE-553): regression tests for backlog command error handling [RED]

### T2 — Add try/except to 7 commands (GREEN)
File: src/raise_cli/cli/commands/backlog.py
Comandos: create, transition, update, link, comment, search, batch-transition
Patrón: try/except Exception → console.print("[red]Error:[/red] {exc}") → typer.Exit(1)
Commit: fix(RAISE-553): wrap adapter calls in backlog commands with error handling [GREEN]

### T3 — Gates
.venv/bin/pytest tests/cli/ --tb=short
.venv/bin/ruff check src/ tests/
.venv/bin/ruff format --check src/ tests/
.venv/bin/pyright src/raise_cli/cli/commands/backlog.py
