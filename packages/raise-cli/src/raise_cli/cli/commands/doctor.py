"""rai doctor — self-diagnostic and bug reporting.

Architecture: ADR-045 (DoctorCheck protocol, E352).
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from raise_cli.doctor.models import CheckResult, CheckStatus, DoctorContext
from raise_cli.doctor.registry import CheckRegistry
from raise_cli.doctor.runner import PIPELINE_ORDER, run_checks, summarize

doctor_app = typer.Typer(
    name="doctor",
    help="Diagnose RaiSE setup, report problems, and auto-fix common issues.",
    invoke_without_command=True,
)

console = Console(stderr=True)

_STATUS_STYLE: dict[CheckStatus, tuple[str, str]] = {
    CheckStatus.PASS: ("[green]OK[/green]", "  "),
    CheckStatus.WARN: ("[yellow]!![/yellow]", "[yellow]!![/yellow]"),
    CheckStatus.ERROR: ("[red]XX[/red]", "[red]XX[/red]"),
}


def _format_result_line(category: str, message: str, status: CheckStatus) -> str:
    """Format a single result line for human output."""
    _, prefix = _STATUS_STYLE[status]
    return f"  {prefix} {category:14s} {message}"


def _render_json_output(
    results: list[CheckResult],
    passes: int,
    warns: int,
    errors: int,
) -> None:
    """Render check results as JSON to stdout."""
    import json

    out = Console()
    data = {
        "results": [
            {
                "check_id": r.check_id,
                "category": r.category,
                "status": r.status.value,
                "message": r.message,
                "fix_hint": r.fix_hint,
                "details": list(r.details),
            }
            for r in results
        ],
        "summary": {"pass": passes, "warn": warns, "error": errors},
    }
    out.print_json(json.dumps(data))


def _format_summary_line(warns: int, errors: int) -> str:
    """Build the summary line listing warning and error counts."""
    parts: list[str] = []
    if warns:
        parts.append(f"{warns} warning{'s' if warns > 1 else ''}")
    if errors:
        parts.append(f"{errors} error{'s' if errors > 1 else ''}")
    return f"\n{', '.join(parts)}."


def _render_human_output(
    results: list[CheckResult],
    warns: int,
    errors: int,
    verbose: bool,
) -> None:
    """Render check results as human-readable output to stdout."""
    out = Console()
    if not results:
        out.print(
            "No checks registered. Install raise-cli with extras for diagnostics."
        )
        return

    for r in results:
        if not verbose and r.status == CheckStatus.PASS:
            continue
        out.print(_format_result_line(r.category, r.message, r.status))
        if r.fix_hint:
            from rich.markup import escape

            out.print(f"       hint: {escape(r.fix_hint)}")

    if warns == 0 and errors == 0:
        out.print("\n[green]All checks passed.[/green]")
    else:
        out.print(_format_summary_line(warns, errors))


def _apply_fixes(results: list[CheckResult]) -> None:
    """Run auto-fixes for fixable non-passing results."""
    fixable = [r for r in results if r.fix_id and r.status != CheckStatus.PASS]
    if fixable:
        from raise_cli.doctor.fix import run_fixes

        out = Console()
        outcomes = run_fixes(fixable, Path.cwd())
        for fix_id, success in outcomes:
            status_label = "[green]fixed[/green]" if success else "[red]failed[/red]"
            out.print(f"  fix: {fix_id} -- {status_label}")


@doctor_app.callback()
def doctor(  # noqa: C901 -- complexity 15, refactor deferred
    ctx: typer.Context,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Show all checks including passing"),
    ] = False,
    json_output: Annotated[
        bool,
        typer.Option("--json", help="JSON output for CI"),
    ] = False,
    fix: Annotated[
        bool,
        typer.Option("--fix", help="Auto-fix common issues (with backup)"),
    ] = False,
    online: Annotated[
        bool,
        typer.Option(
            "--online", help="Include online checks (MCP, adapter connectivity)"
        ),
    ] = False,
    category: Annotated[
        str | None,
        typer.Option("--category", "-c", help="Run only this check category"),
    ] = None,
) -> None:
    """Run diagnostic checks on your RaiSE setup."""
    if ctx.invoked_subcommand is not None:
        return

    registry = CheckRegistry()
    registry.discover()

    categories = [category] if category else None
    if category and category not in PIPELINE_ORDER:
        available = ", ".join(PIPELINE_ORDER)
        console.print(f"Unknown category '{category}'. Available: {available}")
        raise typer.Exit(1)

    context = DoctorContext(
        working_dir=Path.cwd(),
        online=online,
        verbose=verbose,
    )

    results = run_checks(registry, context, categories)
    passes, warns, errors = summarize(results)

    if json_output:
        _render_json_output(results, passes, warns, errors)
    else:
        _render_human_output(results, warns, errors, verbose)

    if fix:
        _apply_fixes(results)

    if errors > 0:
        raise typer.Exit(1)


@doctor_app.command()
def report(
    send: Annotated[
        bool,
        typer.Option("--send", help="Open email client with report"),
    ] = False,
) -> None:
    """Generate diagnostic report, optionally send via email."""
    from raise_cli.doctor.report import (
        SUPPORT_EMAIL,
        generate_report,
        open_mailto,
        save_report,
    )

    registry = CheckRegistry()
    registry.discover()
    context = DoctorContext(working_dir=Path.cwd())
    results = run_checks(registry, context)

    report_data = generate_report(results, Path.cwd())
    saved = save_report(report_data, Path.cwd())
    out = Console()
    out.print(f"Report saved to {saved}")

    if send:
        opened = open_mailto(report_data)
        if opened:
            out.print("Email client opened. Review and send.")
        else:
            out.print("Could not open email client.")
            out.print(f"Email to: {SUPPORT_EMAIL}")
            out.print(f"Attach or paste the report from: {saved}")
    else:
        out.print("To send: rai doctor report --send")
