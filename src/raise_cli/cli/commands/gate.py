"""CLI commands for workflow gate discovery and execution.

Provides ``rai gate check`` and ``rai gate list`` for discovering
and invoking registered WorkflowGate implementations.

Architecture: ADR-039 §1 (WorkflowGate Protocol), §5 (Standalone gates)
"""

from __future__ import annotations

import json
import logging
from typing import Annotated

import typer
from rich.console import Console

from raise_cli.gates.models import GateContext, GateResult
from raise_cli.gates.protocol import WorkflowGate
from raise_cli.gates.registry import GateRegistry

logger = logging.getLogger(__name__)

gate_app = typer.Typer(
    name="gate",
    help="Discover and run workflow gates",
    no_args_is_help=True,
)

console = Console()


def _get_registry() -> GateRegistry:
    """Create and populate a gate registry from entry points."""
    reg = GateRegistry()
    reg.discover()
    return reg


def _run_gate(gate: WorkflowGate, context: GateContext) -> GateResult:
    """Run a single gate with error isolation.

    Gate exceptions are caught and converted to a failed GateResult.
    Gates never crash the CLI.
    """
    try:
        return gate.evaluate(context)
    except Exception as exc:  # noqa: BLE001
        msg = f"{type(exc).__name__}: {exc}"
        logger.warning("Gate '%s' raised: %s", context.gate_id, msg)
        return GateResult(
            passed=False,
            gate_id=context.gate_id,
            message=msg,
        )


def _print_result(result: GateResult) -> None:
    """Print a single gate result in human format."""
    marker = "[green]✓[/green]" if result.passed else "[red]✗[/red]"
    console.print(f"  {marker} {result.gate_id}: {result.message}")
    for detail in result.details:
        console.print(f"    {detail}")


@gate_app.command("list")
def list_command(
    format: Annotated[
        str,
        typer.Option("--format", "-f", help="Output format: human or json"),
    ] = "human",
) -> None:
    """List all discovered workflow gates.

    Shows each gate's ID, description, and workflow point.

    Examples:
        $ rai gate list
        $ rai gate list --format json
    """
    registry = _get_registry()
    gates = registry.gates

    if not gates:
        if format == "json":
            typer.echo(json.dumps({"gates": []}, indent=2))
        else:
            console.print("No gates discovered.")
        return

    if format == "json":
        data = [
            {
                "gate_id": g.gate_id,
                "description": g.description,
                "workflow_point": g.workflow_point,
            }
            for g in gates
        ]
        typer.echo(json.dumps({"gates": data}, indent=2))
    else:
        console.print("[bold]Discovered gates:[/bold]\n")
        for g in gates:
            console.print(f"  {g.gate_id:<20s} {g.description:<30s} {g.workflow_point}")


@gate_app.command("check")
def check_command(
    gate_id: Annotated[
        str | None,
        typer.Argument(help="Gate ID to check (omit for --all)"),
    ] = None,
    all_gates: Annotated[
        bool,
        typer.Option("--all", "-a", help="Run all discovered gates"),
    ] = False,
    format: Annotated[
        str,
        typer.Option("--format", "-f", help="Output format: human or json"),
    ] = "human",
) -> None:
    """Run workflow gates and report results.

    Check a specific gate by ID, or use --all to run every discovered gate.
    Exit code 0 when all pass, 1 when any fail.

    Examples:
        $ rai gate check gate-tests
        $ rai gate check --all
        $ rai gate check --all --format json
    """
    registry = _get_registry()

    if gate_id and all_gates:
        console.print("[red]Error:[/red] Provide gate_id OR --all, not both.")
        raise typer.Exit(1)

    if not gate_id and not all_gates:
        console.print("[red]Error:[/red] Provide a gate_id or use --all.")
        raise typer.Exit(1)

    if gate_id:
        _check_single(registry, gate_id, format)
    else:
        _check_all(registry, format)


def _check_single(registry: GateRegistry, gate_id: str, fmt: str) -> None:
    """Check a single gate by ID."""
    gate = registry.get_gate(gate_id)
    if gate is None:
        if fmt == "json":
            typer.echo(json.dumps({"error": f"Gate '{gate_id}' not found"}))
        else:
            console.print(f"[red]Error:[/red] Gate '{gate_id}' not found.")
        raise typer.Exit(1)

    context = GateContext(gate_id=gate_id)
    result = _run_gate(gate, context)

    if fmt == "json":
        typer.echo(
            json.dumps(
                {
                    "gate_id": result.gate_id,
                    "passed": result.passed,
                    "message": result.message,
                    "details": list(result.details),
                },
                indent=2,
            )
        )
    else:
        _print_result(result)

    raise typer.Exit(0 if result.passed else 1)


def _check_all(registry: GateRegistry, fmt: str) -> None:
    """Check all discovered gates."""
    gates = registry.gates
    if not gates:
        if fmt == "json":
            typer.echo(json.dumps({"gates": [], "summary": "No gates discovered"}))
        else:
            console.print("No gates discovered.")
        raise typer.Exit(0)

    results: list[GateResult] = []
    for gate in gates:
        context = GateContext(gate_id=gate.gate_id)
        result = _run_gate(gate, context)
        results.append(result)

    failed = [r for r in results if not r.passed]

    if fmt == "json":
        data = [
            {
                "gate_id": r.gate_id,
                "passed": r.passed,
                "message": r.message,
                "details": list(r.details),
            }
            for r in results
        ]
        typer.echo(
            json.dumps({"gates": data, "all_passed": len(failed) == 0}, indent=2)
        )
    else:
        for r in results:
            _print_result(r)
        console.print()
        if failed:
            console.print(
                f"[red bold]FAILED:[/red bold] {len(failed)} of {len(results)} gates failed"
            )
        else:
            console.print(
                f"[green bold]PASSED:[/green bold] {len(results)} gates passed"
            )

    raise typer.Exit(1 if failed else 0)
