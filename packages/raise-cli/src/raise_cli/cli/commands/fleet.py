"""CLI commands for fleet dispatch — `rai fleet dispatch`.

Thin Typer wrapper: resolves PM adapter, fetches active issues, delegates
to FleetDispatchService (which calls DagDependencyResolver), and prints
the DispatchPlan in human-readable form.

No-op collision stubs (NoopTaskClaimStore, NoopModuleScope, NoopMergePreflight)
are wired in — intentionally inert for N<4 agents (ADR-106 §3, ADR-095 §Q7).
E-FLEET-2 replaces the stubs with SQLite/git implementations without touching
this command.

Note on --dry-run: in this phase (FLEET-3), dispatch() computes the plan but
does NOT yet assign worktrees — worktree assignment is E-FLEET-2. The --dry-run
flag therefore only affects the output label; its contract is forward-looking.

Architecture: E-FLEET-3 (RAISE-8397), ADR-106, ADR-095
"""

from __future__ import annotations

import re
from typing import Annotated

import typer
from rich.console import Console

from raise_cli.adapters.models.pm import IssueDetail
from raise_cli.cli.commands._resolve import resolve_adapter
from raise_cli.fleet.dispatch_service import FleetDispatchService
from raise_core.fleet.contracts import DispatchPlan

fleet_app = typer.Typer(
    name="fleet",
    help="Fleet dispatch — resolve DAG and dispatch parallel-eligible stories.",
    no_args_is_help=True,
)


# PAT-E-1090: force group routing even when only one command is registered
@fleet_app.command("_reserved", hidden=True, deprecated=True)
def _reserved_stub() -> None:  # pragma: no cover  # type: ignore[reportUnusedFunction]
    """Internal stub — do not use."""


console = Console()
err_console = Console(stderr=True)

# JQL template: active stories in the project (not Done/Cancelled)
_ACTIVE_JQL = (
    'project = "{project}" AND issuetype = Story '
    "AND status not in (Done, Cancelled) ORDER BY created ASC"
)

# Limit for issue search — fleet dispatch targets active stories only
_SEARCH_LIMIT = 200

# Jira project key format: uppercase letter followed by uppercase letters/digits/underscores
_PROJECT_KEY_RE = re.compile(r"^[A-Z][A-Z0-9_]+$")


@fleet_app.command("dispatch")
def dispatch(
    project: Annotated[
        str,
        typer.Option(
            "--project",
            "-p",
            help="Jira project key (e.g. RAISE)",
        ),
    ],
    dry_run: Annotated[
        bool,
        typer.Option(
            "--dry-run",
            help="Print the DispatchPlan without assigning worktrees.",
        ),
    ] = False,
    adapter: Annotated[
        str | None,
        typer.Option(
            "--adapter",
            "-a",
            help="PM adapter override (auto-detect if omitted)",
        ),
    ] = None,
) -> None:
    """Resolve blockedBy DAG and dispatch parallel-eligible stories.

    Reads active stories from the backlog, builds DispatchCandidates from
    their 'is blocked by' links, resolves the DAG, and prints which stories
    are dispatchable, blocked, or rejected (terminal mission).

    No-op collision stubs are active — correct for N<4 agents (ADR-106 §3).
    --dry-run labels output as preview; worktree assignment is E-FLEET-2.
    """
    if not _PROJECT_KEY_RE.match(project):
        err_console.print(
            f"[red]Error:[/red] Invalid project key '{project}'. "
            "Expected format: uppercase letters, digits, underscores (e.g. RAISE)."
        )
        raise typer.Exit(1)

    pm = resolve_adapter(adapter)

    # Fetch active stories — search returns IssueSummary; we need IssueDetail
    # for links, so we call get_issue for each result.
    jql = _ACTIVE_JQL.format(project=project)
    try:
        summaries = pm.search(jql, limit=_SEARCH_LIMIT, fetch_all=False)
    except Exception as exc:
        err_console.print(f"[red]Error:[/red] Failed to search backlog: {exc}")
        raise typer.Exit(1) from exc

    if len(summaries) == _SEARCH_LIMIT:
        err_console.print(
            f"[yellow]Warn:[/yellow] Search returned {_SEARCH_LIMIT} results (limit). "
            "Some stories may be excluded from the plan."
        )

    issues: list[IssueDetail] = []
    for s in summaries:
        try:
            detail = pm.get_issue(s.key)
            issues.append(detail)
        except Exception as exc:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
            err_console.print(
                f"[yellow]Warn:[/yellow] Could not fetch detail for {s.key}: {exc}"
            )

    if summaries and not issues:
        err_console.print(
            "[red]Error:[/red] Could not fetch details for any issue. "
            "Check adapter connectivity."
        )
        raise typer.Exit(1)

    service = FleetDispatchService()
    plan = service.dispatch(issues)

    # Human-readable output
    _print_plan(plan, dry_run=dry_run)


def _print_plan(
    plan: DispatchPlan,
    *,
    dry_run: bool,
) -> None:
    """Render DispatchPlan to console."""
    if not (plan.dispatchable or plan.blocked or plan.rejected):
        console.print("[dim]Nothing to dispatch.[/dim]")
        return

    dry_label = " [dim](dry-run)[/dim]" if dry_run else ""
    console.print(f"\n[bold]Fleet Dispatch Plan[/bold]{dry_label}\n")

    if plan.dispatchable:
        console.print(
            "[green bold]Dispatchable[/green bold] (ready for parallel dispatch):"
        )
        for key in plan.dispatchable:
            console.print(f"  [green]{key}[/green]")

    if plan.blocked:
        console.print("\n[yellow bold]Blocked[/yellow bold] (unresolved dependencies):")
        for key in plan.blocked:
            console.print(f"  [yellow]{key}[/yellow]")

    if plan.rejected:
        console.print(
            "\n[red bold]Rejected[/red bold] (terminal mission — Done/Cancelled):"
        )
        for key in plan.rejected:
            console.print(f"  [dim]{key}[/dim]")

    console.print()
