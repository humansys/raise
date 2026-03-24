"""CLI commands for backlog management via ProjectManagementAdapter.

Provides the ``rai backlog`` command group. All commands delegate to a
ProjectManagementAdapter discovered via entry points (Pattern B, D2).
The adapter is resolved automatically when exactly one is registered,
or selected explicitly via ``--adapter NAME`` (D3).

Query format in ``search`` is adapter-specific: JQL for Jira, etc. (AR5).

Architecture: E301 (Agent Tool Abstraction), ADR-033 (PM Adapter)
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Any

import typer
from rich.console import Console

from raise_cli.adapters.models import IssueSpec
from raise_cli.backlog.sync import sync_backlog
from raise_cli.cli.commands._resolve import resolve_adapter

backlog_app = typer.Typer(
    name="backlog",
    help="Manage backlog items via ProjectManagementAdapter",
    no_args_is_help=True,
)

console = Console()

_VALID_FORMATS = ("human", "agent")

# Common option for adapter override (D3)
AdapterOption = Annotated[
    str | None,
    typer.Option(
        "--adapter", "-a", help="Adapter name override (auto-detect if omitted)"
    ),
]

# Output format option (S325.3: ACI)
FormatOption = Annotated[
    str,
    typer.Option("--format", "-f", help="Output format (human or agent)"),
]


def _sanitize_pipe(value: str) -> str:
    """Replace pipe characters in value to preserve agent format field boundaries."""
    return value.replace("|", "¦")


def _validate_format(format: str) -> None:
    """Validate format option, exit with error if invalid."""
    if format not in _VALID_FORMATS:
        console.print(f"[red]Error:[/red] Invalid format: {format}")
        console.print(f"Valid formats: {', '.join(_VALID_FORMATS)}")
        raise typer.Exit(1)


@backlog_app.command()
def create(
    summary: Annotated[str, typer.Argument(help="Issue title")],
    project: Annotated[
        str, typer.Option("--project", "-p", help="Project key (e.g., RAISE)")
    ],
    issue_type: Annotated[
        str, typer.Option("--type", "-t", help="Issue type")
    ] = "Task",
    labels: Annotated[
        str | None, typer.Option("--labels", "-l", help="Comma-separated labels")
    ] = None,
    parent: Annotated[
        str | None, typer.Option("--parent", help="Parent issue key")
    ] = None,
    description: Annotated[
        str | None,
        typer.Option("--description", "-d", help="Issue description (markdown)"),
    ] = None,
    adapter: AdapterOption = None,
    format: FormatOption = "human",
) -> None:
    """Create a new backlog item."""
    _validate_format(format)
    pm = resolve_adapter(adapter)
    spec = IssueSpec(
        summary=summary,
        issue_type=issue_type,
        description=description or "",
        labels=labels.split(",") if labels else [],
        metadata={"parent": parent} if parent else {},
    )
    try:
        ref = pm.create_issue(project, spec)
    except Exception as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(1) from exc
    if format == "agent":
        print(ref.key)
    else:
        console.print(f"Created: {ref.key}")


@backlog_app.command()
def transition(
    key: Annotated[str, typer.Argument(help="Issue key (e.g., RAISE-123)")],
    status: Annotated[str, typer.Argument(help="Target status")],
    adapter: AdapterOption = None,
) -> None:
    """Transition a backlog item to a new status."""
    pm = resolve_adapter(adapter)
    try:
        ref = pm.transition_issue(key, status)
    except Exception as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(1) from exc
    console.print(f"{ref.key}: transitioned \u2192 {status}")


@backlog_app.command()
def update(
    key: Annotated[str, typer.Argument(help="Issue key (e.g., RAISE-123)")],
    summary: Annotated[
        str | None, typer.Option("--summary", "-s", help="New summary")
    ] = None,
    labels: Annotated[
        str | None, typer.Option("--labels", "-l", help="Comma-separated labels")
    ] = None,
    priority: Annotated[
        str | None, typer.Option("--priority", help="Priority name")
    ] = None,
    assignee: Annotated[
        str | None, typer.Option("--assignee", help="Assignee identifier")
    ] = None,
    adapter: AdapterOption = None,
) -> None:
    """Update fields on a backlog item."""
    pm = resolve_adapter(adapter)
    fields: dict[str, Any] = {}
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

    try:
        ref = pm.update_issue(key, fields)
    except Exception as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(1) from exc
    console.print(f"{ref.key}: updated")


@backlog_app.command()
def link(
    source: Annotated[str, typer.Argument(help="Source issue key")],
    target: Annotated[str, typer.Argument(help="Target issue key")],
    link_type: Annotated[
        str, typer.Argument(help="Link type (e.g., 'blocks', 'relates')")
    ],
    adapter: AdapterOption = None,
) -> None:
    """Link two backlog items (AR4: uses link_issues only)."""
    pm = resolve_adapter(adapter)
    try:
        pm.link_issues(source, target, link_type)
    except Exception as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(1) from exc
    console.print(f"{source} \u2192 {link_type} \u2192 {target}: linked")


@backlog_app.command()
def comment(
    key: Annotated[str, typer.Argument(help="Issue key (e.g., RAISE-123)")],
    body: Annotated[str, typer.Argument(help="Comment text (markdown)")],
    adapter: AdapterOption = None,
) -> None:
    """Add a comment to a backlog item."""
    pm = resolve_adapter(adapter)
    try:
        ref = pm.add_comment(key, body)
    except Exception as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(1) from exc
    console.print(f"{key}: comment added ({ref.id})")


@backlog_app.command()
def get(
    key: Annotated[str, typer.Argument(help="Issue key (e.g., RAISE-123)")],
    adapter: AdapterOption = None,
) -> None:
    """Retrieve details for a single backlog item."""
    pm = resolve_adapter(adapter)
    try:
        detail = pm.get_issue(key)
    except Exception as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(1) from exc

    # Header: key, status, type
    console.print(f"{detail.key}  {detail.status}  {detail.issue_type}")
    console.print(detail.summary)

    # Optional fields — only show when non-empty
    if detail.assignee:
        console.print(f"Assignee: {detail.assignee}")
    if detail.labels:
        console.print(f"Labels:   {', '.join(detail.labels)}")
    if detail.parent_key:
        console.print(f"Parent:   {detail.parent_key}")
    if detail.priority:
        console.print(f"Priority: {detail.priority}")
    if detail.created:
        console.print(f"Created:  {detail.created}")

    # Description
    if detail.description:
        console.print()
        console.print(detail.description)


@backlog_app.command("get-comments")
def get_comments(
    key: Annotated[str, typer.Argument(help="Issue key (e.g., RAISE-123)")],
    limit: Annotated[int, typer.Option("--limit", "-n", help="Max comments")] = 10,
    adapter: AdapterOption = None,
) -> None:
    """Retrieve comments for a backlog item."""
    pm = resolve_adapter(adapter)
    try:
        comments = pm.get_comments(key, limit=limit)
    except Exception as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(1) from exc

    if not comments:
        console.print("No comments.")
        return

    for c in comments:
        # Truncate timestamp to date+time (drop timezone for compactness)
        ts = c.created[:19].replace("T", " ") if c.created else ""
        console.print(f"[{ts}] {c.author}:")
        # Indent comment body
        for line in c.body.splitlines():
            console.print(f"  {line}")
        console.print()


@backlog_app.command()
def search(
    query: Annotated[
        str,
        typer.Argument(
            help="Search query (format depends on adapter, e.g., JQL for Jira)"
        ),
    ],
    limit: Annotated[int, typer.Option("--limit", "-n", help="Max results")] = 50,
    adapter: AdapterOption = None,
    format: FormatOption = "human",
) -> None:
    """Search backlog items. Query format is adapter-specific (AR5)."""
    _validate_format(format)
    pm = resolve_adapter(adapter)
    try:
        results = pm.search(query, limit=limit)
    except Exception as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(1) from exc
    if not results:
        if format != "agent":
            console.print("No results.")
        return
    if format == "agent":
        for issue in results:
            print(
                f"{issue.key}|{_sanitize_pipe(issue.status)}|{_sanitize_pipe(issue.summary)}"
            )
    else:
        for issue in results:
            console.print(f"{issue.key} {issue.status:<12} {issue.summary}")


@backlog_app.command("batch-transition")
def batch_transition(
    keys: Annotated[
        str, typer.Argument(help="Comma-separated issue keys (e.g., RAISE-1,RAISE-2)")
    ],
    status: Annotated[str, typer.Argument(help="Target status")],
    adapter: AdapterOption = None,
) -> None:
    """Transition multiple backlog items at once."""
    pm = resolve_adapter(adapter)
    key_list = [k.strip() for k in keys.split(",") if k.strip()]
    if not key_list:
        console.print("[red]Error:[/red] No valid keys provided.")
        raise typer.Exit(1)

    try:
        result = pm.batch_transition(key_list, status)
    except Exception as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(1) from exc
    succeeded = len(result.succeeded)
    failed = len(result.failed)
    total = succeeded + failed

    console.print(f"{succeeded}/{total} transitioned \u2192 {status}")
    for failure in result.failed:
        console.print(f"  [red]\u2717[/red] {failure.key}: {failure.error}")


@backlog_app.command()
def sync(
    project: Annotated[
        str | None,
        typer.Option("--project", "-p", help="Project key filter (e.g., RAISE)"),
    ] = None,
    adapter: AdapterOption = None,
) -> None:
    """Regenerate governance/backlog.md from a remote adapter."""
    pm = resolve_adapter(adapter)

    # Derive adapter name for display
    adapter_name = (
        adapter
        or type(pm).__name__.lower().replace("pmadapter", "").replace("adapter", "")
        or "unknown"
    )

    output_path = Path.cwd() / "governance" / "backlog.md"

    try:
        result = sync_backlog(
            pm,
            adapter_name,
            project_filter=project,
            output_path=output_path,
        )
    except ValueError as exc:
        # Filesystem adapter no-op
        console.print(f"[yellow]{exc}[/yellow]")
        raise typer.Exit(0) from exc
    except RuntimeError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(1) from exc

    console.print(
        f"Synced {result.output_path} from {result.adapter_name} "
        f"({result.epic_count} epics, {result.timestamp})"
    )
