"""CLI commands for workflow gate discovery and execution.

Provides ``rai gate check`` and ``rai gate list`` for discovering
and invoking registered WorkflowGate implementations.

Architecture: ADR-039 §1 (WorkflowGate Protocol), §5 (Standalone gates)
"""

from __future__ import annotations

import json
import logging
import stat
from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated

import typer
import yaml
from pydantic import ValidationError
from rich.console import Console

from raise_cli.gates.ar.story_gate import marker_path as _ar_marker_path
from raise_cli.gates.calibration.log import append_promotion_entry
from raise_cli.gates.calibration.promotion_policy import (
    CalibrationRecord,
    PromotionPolicy,
    evaluate_promotion,
)
from raise_cli.gates.drift.baseline import apply_strict_drift, load_baseline
from raise_cli.gates.execution import (
    GateNotFoundError,
    run_all_gates,
    run_gate,
    run_gates_for_point,
)
from raise_cli.gates.models import GateResult
from raise_cli.gates.registry import GateRegistry
from raise_cli.telemetry.trailer import resolve_session_id

_AR_ATTEST_GATES = frozenset({"gate-ar-story", "gate-ar-bugfix"})

# Single source of truth for promote-check's CLI defaults — reuses
# PromotionPolicy's own defaults rather than duplicating the 0.10/3
# literals (AC: configurable, not hard-coded).
_DEFAULT_PROMOTION_POLICY = PromotionPolicy()

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


def _print_result(result: GateResult) -> None:
    """Print a single gate result in human format.

    Advisory results carrying live violations get a distinct WARN marker —
    unconditional visibility (RAISE-14280), independent of --strict-drift.
    A passing advisory gate with no violations still renders as a plain
    pass (nothing to warn about).
    """
    if not result.passed:
        marker = "[red]{CROSS}[/red]"
    elif result.advisory and result.details:
        marker = "[yellow]{WARN}[/yellow]"
    else:
        marker = "[green]{CHECK}[/green]"
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
            blocker_tag = " [BLOCKER]" if getattr(g, "is_blocker", False) else ""
            console.print(
                f"  {g.gate_id:<20s} {g.description:<30s} {g.workflow_point}{blocker_tag}"
            )


@gate_app.command("check")
def check_command(
    gate_id: Annotated[
        str | None,
        typer.Argument(help="Gate ID to check (omit for --all or --point)"),
    ] = None,
    all_gates: Annotated[
        bool,
        typer.Option("--all", "-a", help="Run all discovered gates"),
    ] = False,
    point: Annotated[
        str | None,
        typer.Option("--point", help="Run gates for a specific workflow_point"),
    ] = None,
    format: Annotated[
        str,
        typer.Option("--format", "-f", help="Output format: human or json"),
    ] = "human",
    scope: Annotated[
        str | None,
        typer.Option(
            "--scope",
            help="Append a path argument to the gate command (e.g. scope tests to a subdirectory)",
        ),
    ] = None,
    strict_drift: Annotated[
        bool,
        typer.Option(
            "--strict-drift",
            help=(
                "Block advisory drift violations NOT frozen in "
                "governance/drift-baseline.json (RAISE-14280). Default off: "
                "locally, advisory drift never blocks — only visible as WARN."
            ),
        ),
    ] = False,
) -> None:
    """Run workflow gates and report results.

    Check a specific gate by ID, use --all to run every discovered gate,
    or use --point to run gates for a specific workflow transition.
    Exit code 0 when all pass, 1 when any fail.

    --strict-drift changes only advisory drift gates: a violation already
    present in governance/drift-baseline.json stays non-blocking, but a
    violation NOT in the baseline (new drift) flips that gate to failing.
    Non-advisory gates are unaffected. This is the CI enforcement locus
    (ADR-130) — local runs default to WARN-only.

    Examples:
        $ rai gate check gate-tests
        $ rai gate check gate-tests --scope packages/raise-cli/tests/test_gates/
        $ rai gate check --all
        $ rai gate check --point before:story:close
        $ rai gate check --all --format json
        $ rai gate check drift-post-refactor-orphan --strict-drift
    """
    registry = _get_registry()
    extra_args: tuple[str, ...] = (scope,) if scope else ()

    exclusive = sum([bool(gate_id), all_gates, bool(point)])
    if exclusive > 1:
        console.print(
            "[red]Error:[/red] Provide gate_id, --all, or --point — not multiple."
        )
        raise typer.Exit(1)

    if exclusive == 0:
        console.print("[red]Error:[/red] Provide a gate_id, --all, or --point.")
        raise typer.Exit(1)

    if gate_id:
        _check_single(registry, gate_id, format, extra_args, strict_drift=strict_drift)
    elif point:
        _check_all(
            registry,
            format,
            workflow_point=point,
            extra_args=extra_args,
            strict_drift=strict_drift,
        )
    else:
        _check_all(registry, format, extra_args=extra_args, strict_drift=strict_drift)


def _check_single(
    registry: GateRegistry,
    gate_id: str,
    fmt: str,
    extra_args: tuple[str, ...] = (),
    strict_drift: bool = False,
) -> None:
    """Check a single gate by ID — delegates to the gate-execution seam."""
    working_dir = Path.cwd()
    try:
        result = run_gate(
            gate_id, working_dir, extra_args=extra_args, registry=registry
        )
    except GateNotFoundError:
        if fmt == "json":
            typer.echo(json.dumps({"error": f"Gate '{gate_id}' not found"}))
        else:
            console.print(f"[red]Error:[/red] Gate '{gate_id}' not found.")
        raise typer.Exit(1) from None

    if strict_drift:
        result = apply_strict_drift(result, load_baseline(working_dir))

    if fmt == "json":
        typer.echo(
            json.dumps(
                {
                    "gate_id": result.gate_id,
                    "passed": result.passed,
                    "message": result.message,
                    "details": list(result.details),
                    "advisory": result.advisory,
                },
                indent=2,
            )
        )
    else:
        _print_result(result)

    raise typer.Exit(0 if result.passed else 1)


def _check_all(
    registry: GateRegistry,
    fmt: str,
    workflow_point: str | None = None,
    extra_args: tuple[str, ...] = (),
    strict_drift: bool = False,
) -> None:
    """Check all discovered gates, optionally filtered by workflow_point.

    ``workflow_point`` present → ``run_gates_for_point`` (scoped per
    ``SCOPED_POINTS`` — this is the RAISE-13749 fix reaching the CLI for
    ``--point before:bug:close``). ``workflow_point`` absent (``--all``) →
    ``run_all_gates`` — H1: the blanket sweep stays its own entry point,
    never routed through the point-based function.
    """
    working_dir = Path.cwd()
    if workflow_point is not None:
        report = run_gates_for_point(
            workflow_point, working_dir, extra_args=extra_args, registry=registry
        )
    else:
        report = run_all_gates(working_dir, extra_args=extra_args, registry=registry)

    results = report.results
    if not results:
        if fmt == "json":
            typer.echo(json.dumps({"gates": [], "summary": "No gates discovered"}))
        else:
            console.print("No gates discovered.")
        raise typer.Exit(0)

    # --strict-drift (RAISE-14280) flips advisory drift gates carrying NEW
    # violations (not frozen in governance/drift-baseline.json) to failing.
    # Applied on top of the release execution seam: transform each GateResult
    # BEFORE deciding failures, so a WARN advisory with new drift counts as a
    # failure. Baseline is loaded only when strict_drift is active.
    failed: list[GateResult]
    if strict_drift:
        baseline = load_baseline(working_dir)
        results = tuple(apply_strict_drift(r, baseline) for r in results)
        failed = [r for r in results if not r.passed]
    else:
        failed = list(report.failures)

    if fmt == "json":
        data = [
            {
                "gate_id": r.gate_id,
                "passed": r.passed,
                "message": r.message,
                "details": list(r.details),
                "advisory": r.advisory,
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


@gate_app.command("ar-attest")
def ar_attest_command(
    gate: Annotated[
        str,
        typer.Option(
            "--gate",
            help="Which AR gate to attest for: gate-ar-story or gate-ar-bugfix",
        ),
    ],
) -> None:
    """Write the AR attestation marker the review phase produces (D1, RAISE-14326).

    Writes via the SAME ``_marker_path()`` formula ``gate-ar-story`` /
    ``gate-ar-bugfix`` read — single source of truth for writer and checker,
    so a review skill never hand-computes the path (and cannot drift from
    it). Called from the review phase only (``/rai-story-review``,
    ``/rai-bugfix-review``) — close phases only verify via
    ``rai gate check gate-ar-*``.

    Examples:
        $ rai gate ar-attest --gate gate-ar-story
        $ rai gate ar-attest --gate gate-ar-bugfix
    """
    if gate not in _AR_ATTEST_GATES:
        console.print(
            f"[red]Error:[/red] --gate must be one of "
            f"{sorted(_AR_ATTEST_GATES)}, got {gate!r}."
        )
        raise typer.Exit(1)

    working_dir = Path.cwd()
    marker = _ar_marker_path(working_dir)
    if marker is None:
        console.print(
            "[red]Error:[/red] No session context — cannot attest without a "
            "resolvable session ID (RAISE_AGENT_SESSION_ID / RAISE_CC_SESSION_ID)."
        )
        raise typer.Exit(1)

    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.touch()
    console.print(f"[green]Attested[/green] {gate} — marker written at {marker}")
    raise typer.Exit(0)


# ---------------------------------------------------------------------------
# promote-check — FF false-positive calibration & promotion decision
# ---------------------------------------------------------------------------


@gate_app.command("promote-check")
def promote_check_command(
    ff: Annotated[
        str,
        typer.Option("--ff", help="Fitness function name to evaluate for promotion"),
    ],
    data: Annotated[
        Path,
        typer.Option("--data", help="Path to a calibration data YAML file"),
    ],
    max_fp_rate: Annotated[
        float,
        typer.Option(
            "--max-fp-rate",
            help="Maximum allowed false-positive rate (default matches PromotionPolicy)",
        ),
    ] = _DEFAULT_PROMOTION_POLICY.max_fp_rate,
    min_stories: Annotated[
        int,
        typer.Option(
            "--min-stories",
            help="Minimum recorded stories required (default matches PromotionPolicy)",
        ),
    ] = _DEFAULT_PROMOTION_POLICY.min_stories,
) -> None:
    """Evaluate a fitness function's calibration data for promotion.

    NOT a `WorkflowGate` — this is a rare, on-demand steward action (promoting
    a CI drift guard from advisory to hard-blocking), not a per-MR workflow
    transition, so it is invisible to `rai gate list`/`rai gate check --all`.

    Loads `--data` (YAML), runs `evaluate_promotion()`, appends exactly one
    entry to `.raise/rai/fitness-functions/promotion-log.json` (never
    overwriting existing entries), and exits 0 (approved) / 1 (denied) so
    it is scriptable by a steward. See governance/runbook-guards.md
    "Promoting a Guard from Advisory to Blocking".

    Examples:
        $ rai gate promote-check --ff capability-overlap --data calibration.yaml
        $ rai gate promote-check --ff my-ff --data cal.yaml --max-fp-rate 0.05 --min-stories 5
    """
    if not data.exists():
        console.print(f"[red]Error:[/red] Calibration data file not found: {data}")
        raise typer.Exit(1)

    try:
        raw = yaml.safe_load(data.read_text(encoding="utf-8")) or {}
        record = CalibrationRecord.model_validate(raw)
    except (yaml.YAMLError, ValidationError) as exc:
        console.print(f"[red]Error:[/red] Invalid calibration data in {data}: {exc}")
        raise typer.Exit(1) from exc

    if record.ff_name != ff:
        console.print(
            f"[red]Error:[/red] --ff {ff!r} does not match ff_name "
            f"{record.ff_name!r} in {data}. Mismatch — refusing to evaluate "
            "the wrong dataset."
        )
        raise typer.Exit(1)

    policy = PromotionPolicy(max_fp_rate=max_fp_rate, min_stories=min_stories)
    decision = evaluate_promotion(record, policy)

    working_dir = Path.cwd()
    entry = {
        "timestamp": datetime.now(tz=UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "ff_name": decision.ff_name,
        "total_flags": decision.total_flags,
        "false_positives": decision.total_false_positives,
        "fp_rate": decision.fp_rate,
        "decision": "approved" if decision.approved else "denied",
        "reason": decision.reason,
        "promoter": resolve_session_id() or "unknown",
        "remarks": "",
    }
    append_promotion_entry(working_dir, entry)

    if decision.approved:
        console.print(f"[green]APPROVED[/green]: {decision.reason}")
    else:
        console.print(f"[red]DENIED[/red]: {decision.reason}")

    raise typer.Exit(0 if decision.approved else 1)


# ---------------------------------------------------------------------------
# Hook management constants
# ---------------------------------------------------------------------------

_HOOK_MARKER = "# Installed by: rai gate install-hook"

_HOOK_SHIM = (
    "#!/usr/bin/env bash\n"
    "# Installed by: rai gate install-hook\n"
    "# Remove with:  rai gate uninstall-hook\n"
    "uv run python -m raise_cli.gates.hook\n"
)


def _find_hook_path() -> Path:
    """Resolve .git/hooks/pre-commit from cwd."""
    return Path.cwd() / ".git" / "hooks" / "pre-commit"


# ---------------------------------------------------------------------------
# install-hook
# ---------------------------------------------------------------------------


@gate_app.command("install-hook")
def install_hook_command(
    force: Annotated[
        bool,
        typer.Option("--force", help="Overwrite existing non-rai hook"),
    ] = False,
) -> None:
    """Install a pre-commit hook that runs lint, format, and type-check.

    The hook is a thin bash shim that invokes the Python hook module via
    ``uv run python -m raise_cli.gates.hook``.

    Refuses to overwrite an existing hook unless it was installed by rai
    (detected via marker comment) or ``--force`` is used.

    Examples:
        $ rai gate install-hook
        $ rai gate install-hook --force
    """
    hook_path = _find_hook_path()

    if hook_path.exists():
        content = hook_path.read_text(encoding="utf-8")
        if _HOOK_MARKER not in content and not force:
            console.print(
                "[red]Error:[/red] Pre-commit hook already exists and was not "
                "installed by rai. Use --force to overwrite."
            )
            raise typer.Exit(1)

    hook_path.write_text(_HOOK_SHIM, encoding="utf-8")
    hook_path.chmod(
        hook_path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
    )
    console.print("[green]Installed[/green] pre-commit hook.")
    raise typer.Exit(0)


# ---------------------------------------------------------------------------
# uninstall-hook
# ---------------------------------------------------------------------------


@gate_app.command("uninstall-hook")
def uninstall_hook_command() -> None:
    """Remove the rai-installed pre-commit hook.

    Only removes the hook if it contains the rai marker comment.
    Refuses to remove hooks installed by other tools.

    Examples:
        $ rai gate uninstall-hook
    """
    hook_path = _find_hook_path()

    if not hook_path.exists():
        console.print("[red]Error:[/red] No pre-commit hook found.")
        raise typer.Exit(1)

    content = hook_path.read_text(encoding="utf-8")
    if _HOOK_MARKER not in content:
        console.print(
            "[red]Error:[/red] Pre-commit hook was not installed by rai. Not removing."
        )
        raise typer.Exit(1)

    hook_path.unlink()
    console.print("[green]Removed[/green] pre-commit hook.")
    raise typer.Exit(0)
