"""CLI commands for backlog management via ProjectManagementAdapter.

Provides the ``rai backlog`` command group. All commands delegate to a
ProjectManagementAdapter discovered via entry points (Pattern B, D2).
The adapter is resolved automatically when exactly one is registered,
or selected explicitly via ``--adapter NAME`` (D3).

Query format in ``search`` is adapter-specific: JQL for Jira, etc. (AR5).

Architecture: E301 (Agent Tool Abstraction), ADR-033 (PM Adapter)
"""

from __future__ import annotations

from typing import Annotated

import typer
from rich.console import Console

from rai_cli.adapters.models import IssueSpec
from rai_cli.cli.commands._adapter_resolve import resolve_adapter

backlog_app = typer.Typer(
    name="backlog",
    help="Manage backlog items via ProjectManagementAdapter",
    no_args_is_help=True,
)

console = Console()

# Common option for adapter override (D3)
AdapterOption = Annotated[
    str | None,
    typer.Option("--adapter", "-a", help="Adapter name override (auto-detect if omitted)"),
]


@backlog_app.command()
def create(
    summary: Annotated[str, typer.Argument(help="Issue title")],
    project: Annotated[str, typer.Option("--project", "-p", help="Project key (e.g., RAISE)")],
    issue_type: Annotated[str, typer.Option("--type", "-t", help="Issue type")] = "Task",
    labels: Annotated[str | None, typer.Option("--labels", "-l", help="Comma-separated labels")] = None,
    parent: Annotated[str | None, typer.Option("--parent", help="Parent issue key")] = None,
    description: Annotated[str | None, typer.Option("--description", "-d", help="Issue description (markdown)")] = None,
    adapter: AdapterOption = None,
) -> None:
    """Create a new backlog item."""
    pm = resolve_adapter(adapter)
    spec = IssueSpec(
        summary=summary,
        issue_type=issue_type,
        description=description or "",
        labels=labels.split(",") if labels else [],
        metadata={"parent": parent} if parent else {},
    )
    ref = pm.create_issue(project, spec)
    console.print(f"Created: {ref.key}")


@backlog_app.command()
def transition(
    key: Annotated[str, typer.Argument(help="Issue key (e.g., RAISE-123)")],
    status: Annotated[str, typer.Argument(help="Target status")],
    adapter: AdapterOption = None,
) -> None:
    """Transition a backlog item to a new status."""
    pm = resolve_adapter(adapter)
    ref = pm.transition_issue(key, status)
    console.print(f"{ref.key}: transitioned \u2192 {status}")


@backlog_app.command()
def update(
    key: Annotated[str, typer.Argument(help="Issue key (e.g., RAISE-123)")],
    summary: Annotated[str | None, typer.Option("--summary", "-s", help="New summary")] = None,
    labels: Annotated[str | None, typer.Option("--labels", "-l", help="Comma-separated labels")] = None,
    priority: Annotated[str | None, typer.Option("--priority", help="Priority name")] = None,
    assignee: Annotated[str | None, typer.Option("--assignee", help="Assignee identifier")] = None,
    adapter: AdapterOption = None,
) -> None:
    """Update fields on a backlog item."""
    pm = resolve_adapter(adapter)
    fields: dict[str, object] = {}
    if summary is not None:
        fields["summary"] = summary
    if labels is not None:
        fields["labels"] = labels.split(",")
    if priority is not None:
        fields["priority"] = priority
    if assignee is not None:
        fields["assignee"] = assignee

    if not fields:
        console.print("[yellow]Warning:[/yellow] No fields to update.")
        raise typer.Exit(0)

    ref = pm.update_issue(key, fields)
    console.print(f"{ref.key}: updated")


@backlog_app.command()
def link(
    source: Annotated[str, typer.Argument(help="Source issue key")],
    target: Annotated[str, typer.Argument(help="Target issue key")],
    link_type: Annotated[str, typer.Argument(help="Link type (e.g., 'blocks', 'relates')")],
    adapter: AdapterOption = None,
) -> None:
    """Link two backlog items (AR4: uses link_issues only)."""
    pm = resolve_adapter(adapter)
    pm.link_issues(source, target, link_type)
    console.print(f"{source} \u2192 {link_type} \u2192 {target}: linked")


@backlog_app.command()
def comment(
    key: Annotated[str, typer.Argument(help="Issue key (e.g., RAISE-123)")],
    body: Annotated[str, typer.Argument(help="Comment text (markdown)")],
    adapter: AdapterOption = None,
) -> None:
    """Add a comment to a backlog item."""
    pm = resolve_adapter(adapter)
    ref = pm.add_comment(key, body)
    console.print(f"{key}: comment added ({ref.id})")


@backlog_app.command()
def search(
    query: Annotated[str, typer.Argument(help="Search query (format depends on adapter, e.g., JQL for Jira)")],
    limit: Annotated[int, typer.Option("--limit", "-n", help="Max results")] = 50,
    adapter: AdapterOption = None,
) -> None:
    """Search backlog items. Query format is adapter-specific (AR5)."""
    pm = resolve_adapter(adapter)
    results = pm.search(query, limit=limit)
    if not results:
        console.print("No results.")
        return
    for issue in results:
        console.print(f"{issue.key} {issue.status:<12} {issue.summary}")


@backlog_app.command("batch-transition")
def batch_transition(
    keys: Annotated[str, typer.Argument(help="Comma-separated issue keys (e.g., RAISE-1,RAISE-2)")],
    status: Annotated[str, typer.Argument(help="Target status")],
    adapter: AdapterOption = None,
) -> None:
    """Transition multiple backlog items at once."""
    pm = resolve_adapter(adapter)
    key_list = [k.strip() for k in keys.split(",") if k.strip()]
    if not key_list:
        console.print("[red]Error:[/red] No valid keys provided.")
        raise typer.Exit(1)

    result = pm.batch_transition(key_list, status)
    succeeded = len(result.succeeded)
    failed = len(result.failed)
    total = succeeded + failed

    console.print(f"{succeeded}/{total} transitioned \u2192 {status}")
    for failure in result.failed:
        console.print(f"  [red]\u2717[/red] {failure.key}: {failure.error}")
