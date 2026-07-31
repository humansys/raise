"""CLI commands for backlog management via ProjectManagementAdapter.

Provides the ``rai backlog`` command group. All commands delegate to a
ProjectManagementAdapter discovered via entry points (Pattern B, D2).
The adapter is resolved automatically when exactly one is registered,
or selected explicitly via ``--adapter NAME`` (D3).

Query format in ``search`` is adapter-specific: JQL for Jira, etc. (AR5).

Architecture: E301 (Agent Tool Abstraction), ADR-033 (PM Adapter)
"""

# drift: ignore — grupo de comandos backlog tocado por muchas historias; densidad
# de story-tokens pre-existente (no accretion nueva). drift-story-accretion CAND-05.

from __future__ import annotations

import contextlib
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated, Any, cast

import typer
import yaml
from rich.console import Console
from rich.markup import escape

from raise_cli.adapters.backlog_config import load_backlog_config, save_backlog_config
from raise_cli.adapters.models import IssueRef, IssueSpec, ProjectVersion
from raise_cli.adapters.models.pm import (
    FIXED_PREFIXES,
    WorkflowConfig,
    assign_prefix,
    canonicalize_issue_type_key,
)
from raise_cli.adapters.types_config import load_types_config
from raise_cli.backlog.hooks import pipeline_run_active as _pipeline_run_active
from raise_cli.backlog.sync import sync_backlog
from raise_cli.cli.commands._resolve import get_effective_adapter_name, resolve_adapter
from raise_cli.config.paths import resolve_checkout_root
from raise_cli.output.symbols import ARROW, BIDIR, CHECK, CROSS
from raise_cli.storage.work_items import (
    WorkItem,
    WorkItemStore,
    WorkItemType,
    slugify_local_key,
)

backlog_app = typer.Typer(
    name="backlog",
    help="Manage backlog items via ProjectManagementAdapter",
    no_args_is_help=True,
)
version_app = typer.Typer(
    name="version",
    help="Manage project fixVersions/release versions",
    no_args_is_help=True,
)
backlog_app.add_typer(version_app, name="version")

console = Console()
err_console = Console(stderr=True)

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

# Org override — sets RAISE_BACKLOG_ORG before adapter creation (RAISE-6248)
OrgOption = Annotated[
    str | None,
    typer.Option(
        "--org", help="Org override — routes to a specific org (sets RAISE_BACKLOG_ORG)"
    ),
]


def _sanitize_pipe(value: str) -> str:
    """Replace pipe characters in value to preserve agent format field boundaries."""
    return value.replace("|", "¦")


def _parse_fields(raw: list[str]) -> dict[str, Any]:
    """Parse ``--field key=value`` entries into a dict.

    Values are strings by default.  If a value starts with ``{`` or ``[``,
    it is parsed as JSON so callers can pass structured Jira field values
    like ``{"value": "Sev-2"}``.
    """
    result: dict[str, Any] = {}
    for entry in raw:
        key, _, value = entry.partition("=")
        key = key.strip()
        value = value.strip()
        if not key:
            continue
        if value.startswith(("{", "[")):
            with contextlib.suppress(json.JSONDecodeError):
                value = json.loads(value)
        result[key] = value
    return result


def _resolve_issue_type_alias(issue_type: str, adapter: str | None) -> str:
    """Resolve a localized issue type alias (e.g. "Historia" -> "Story").

    Shared by ``create`` and ``update`` so both honor
    ``config.issue_type_aliases``. Falls back to the input unchanged when no
    backlog config is found or the adapter can't be resolved.
    """
    try:
        config = load_backlog_config(Path.cwd(), get_effective_adapter_name(adapter))
        return config.issue_type_aliases.get(issue_type, issue_type)
    except (FileNotFoundError, KeyError):
        return issue_type


def _collect_simple_update_fields(
    *,
    summary: str | None,
    labels: str | None,
    priority: str | None,
    assignee: str | None,
    parent: str | None,
    issue_type: str | None,
    fix_version: str | None,
    adapter: str | None,
) -> dict[str, Any]:
    """Map ``rai backlog update``'s scalar options onto Jira field IDs.

    Extracted from ``update`` to keep its cyclomatic complexity under the
    lint threshold (C901) now that hierarchy flags (parent/type/fixVersions,
    RAISE-14071) joined the original set.
    """
    fields: dict[str, Any] = {}
    if summary is not None:
        fields["summary"] = summary
    if labels is not None:
        fields["labels"] = labels.split(",")
    if priority is not None:
        fields["priority"] = priority
    if assignee is not None:
        fields["assignee"] = assignee
    if parent is not None:
        fields["parent"] = parent
    if issue_type is not None:
        fields["issuetype"] = _resolve_issue_type_alias(issue_type, adapter)
    if fix_version is not None:
        fields["fixVersions"] = fix_version
    return fields


def _validate_format(format: str) -> None:
    """Validate format option, exit with error if invalid."""
    if format not in _VALID_FORMATS:
        console.print(f"[red]Error:[/red] Invalid format: {format}")
        console.print(f"Valid formats: {', '.join(_VALID_FORMATS)}")
        raise typer.Exit(1)


def _require_version_capability(pm: Any) -> Any:
    """Return a PM adapter that supports project version management."""
    if not callable(getattr(pm, "list_versions", None)) or not callable(
        getattr(pm, "create_version", None)
    ):
        console.print(
            "[red]Error:[/red] Adapter does not support project version management"
        )
        raise typer.Exit(1)
    return pm


def _print_version_agent(version: ProjectVersion) -> None:
    """Print one version in stable pipe-delimited ACI format."""
    print(
        "|".join(
            [
                _sanitize_pipe(version.id),
                _sanitize_pipe(version.name),
                str(version.released),
                str(version.archived),
                _sanitize_pipe(version.release_date),
            ]
        )
    )


def _resolve_description(
    inline: str | None,
    file: Path | None,
    from_stdin: bool,
) -> str:
    """Resolve description text from file, stdin, or inline flag (priority: file > stdin > inline).

    Safe transport for Markdown with backticks, $vars, and newlines that would
    be interpolated by Bash when passed as inline CLI arguments (RAISE-5962).
    """
    if file is not None:
        if not file.exists():
            console.print(f"[red]Error:[/red] Description file not found: {file}")
            raise typer.Exit(1)
        return file.read_text(encoding="utf-8")
    if from_stdin:
        return sys.stdin.read()
    return inline or ""


# S3 (RAISE-14642) — unified creation ontology: `-t <type>` for the 5
# work-item levels (theme -> initiative -> epic -> story -> task) routes to
# `work_items` instead of the legacy remote-only path. D3 (s3-design.md):
# case-sensitive exact match against these lowercase names only — legacy
# Jira issue-type values (`Bug`, `Task`, ...) are always capitalized in this
# codebase's convention (FIXED_PREFIXES keys are `Epic`/`Story`/`Bug`), so
# `-t Task` (default) keeps meaning "Jira Task issue type, remote-only"
# while `-t task` (lowercase) means the new ontology type.
_ONTOLOGY_TYPES = frozenset({"theme", "initiative", "epic", "story", "task"})


def _is_ontology_type(issue_type: str) -> bool:
    """Return True if `issue_type` is one of the 5 ontology levels (D3)."""
    return issue_type in _ONTOLOGY_TYPES


def _resolve_explicit_parent(
    store: WorkItemStore, parent: str | None
) -> tuple[str | None, str | None]:
    """Resolve `--parent` against `work_items` by local_key or jira_key.

    T4 scope: explicit `--parent` only — errors loudly (exit 1) if given but
    not found, rather than silently creating a root item. The AC8
    parent-resolution heuristic (no `--parent` given) is T5.
    """
    if parent is None:
        return None, None
    item = store.get_by_local_key(parent) or store.get_by_jira_key(parent)
    if item is None:
        console.print(f"[red]Error:[/red] Parent '{parent}' not found in work_items")
        raise typer.Exit(1)
    return item.local_key, item.jira_key


def _is_test_context() -> bool:
    """Return True when running inside pytest (D5, mirrors mission.py:66-68)."""
    return bool(os.environ.get("PYTEST_CURRENT_TEST"))


def _infer_parent(
    store: WorkItemStore, parent_type: str | None
) -> tuple[str | None, str | None]:
    """AC8 (SHOULD): infer a parent when exactly one candidate of `parent_type` exists.

    No `--parent` given and `types.yaml` declares a `parent_resolution` for
    this type — best-effort, single-candidate only (YAGNI gate, s3-design.md
    §Approach "Lean gates"): no fuzzy matching, no recency heuristics.
    """
    if parent_type is None:
        return None, None
    candidates = store.list_all(type=parent_type)
    if len(candidates) != 1:
        return None, None
    return candidates[0].local_key, candidates[0].jira_key


def _create_work_item(
    *,
    summary: str,
    project: str,
    issue_type: WorkItemType,
    parent: str | None,
    description: str,
    local: bool,
    format: str,  # noqa: A002 - mirrors create()'s own `format` param name
    pm: Any,
) -> None:
    """Ontology-type creation path for `create()` (S3, RAISE-14642 T4/T5).

    Extracted to keep `create()`'s cyclomatic complexity under the lint
    threshold — same rationale as `_collect_simple_update_fields`.
    """
    project_root = resolve_checkout_root()
    store = WorkItemStore(project_root)
    types_config = load_types_config(project_root)
    local_key = slugify_local_key(store, issue_type, summary)
    parent_local_key, parent_jira_key = _resolve_explicit_parent(store, parent)
    type_config = types_config.types.get(issue_type)
    no_portfolio = type_config.no_portfolio_default if type_config else False
    if parent is None and type_config is not None:
        parent_local_key, parent_jira_key = _infer_parent(
            store, type_config.parent_resolution
        )

    if local:
        _persist_work_item(
            store,
            id_key=local_key,
            issue_type=issue_type,
            local_key=local_key,
            jira_key=None,
            parent_local_key=parent_local_key,
            parent_jira_key=parent_jira_key,
            summary=summary,
            no_portfolio=no_portfolio,
        )
        if format == "agent":
            print(local_key)
        else:
            console.print(f"Created: {local_key} (local; no Jira issue)")
        return

    # Dual-write to Jira (T5, RAISE-14642), mirroring mission.py's
    # disciplined pattern: _is_test_context guard (D5) so unit tests never
    # hit the network, jira_issue_type resolved from types.yaml (not the
    # raw ontology `-t` value), remote_synced fail-loud reporting via the
    # existing _report_write_outcome (reused, not reimplemented).
    if _is_test_context():
        _persist_work_item(
            store,
            id_key=local_key,
            issue_type=issue_type,
            local_key=local_key,
            jira_key=None,
            parent_local_key=parent_local_key,
            parent_jira_key=parent_jira_key,
            summary=summary,
            no_portfolio=no_portfolio,
        )
        # _is_test_context() short-circuit — no Jira call made, jira_key
        # stays None (exactly like mission.py's _sync_create_to_jira).
        if format == "agent":
            print(local_key)
        else:
            console.print(f"Created: {local_key}")
        return

    jira_issue_type = type_config.jira_issue_type if type_config else issue_type
    spec = IssueSpec(
        summary=summary,
        issue_type=jira_issue_type,
        description=description,
        parent=parent_jira_key,
    )
    try:
        ref = pm.create_issue(project, spec)
    except Exception as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(1) from exc

    _persist_work_item(
        store,
        id_key=local_key,
        issue_type=issue_type,
        local_key=local_key,
        jira_key=ref.key,
        parent_local_key=parent_local_key,
        parent_jira_key=parent_jira_key,
        summary=summary,
        no_portfolio=no_portfolio,
    )
    if format == "agent":
        print(ref.key)
    else:
        _report_write_outcome(ref, f"Created: {ref.key}")


def _persist_work_item(
    store: WorkItemStore,
    *,
    id_key: str,
    issue_type: WorkItemType,
    local_key: str,
    jira_key: str | None,
    parent_local_key: str | None,
    parent_jira_key: str | None,
    summary: str,
    no_portfolio: bool,
) -> WorkItem:
    """Build and persist a `WorkItem` row — single INSERT, confirmed keys only.

    Shared by both `_create_work_item` sub-paths (local-only and dual-write)
    so the id/timestamp construction lives in exactly one place.
    """
    now = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    work_item = WorkItem(
        id=f"{id_key}-{datetime.now(UTC):%y%m%d%H%M%S%f}",
        type=issue_type,
        local_key=local_key,
        jira_key=jira_key,
        parent_local_key=parent_local_key,
        parent_jira_key=parent_jira_key,
        summary=summary,
        no_portfolio=no_portfolio,
        created_at=now,
        updated_at=now,
    )
    return store.create(work_item)


@version_app.command("list")
def version_list(
    project: Annotated[
        str, typer.Option("--project", "-p", help="Project key (e.g., RAISE)")
    ],
    adapter: AdapterOption = None,
    format: FormatOption = "human",
) -> None:
    """List project fixVersions/release versions."""
    _validate_format(format)
    pm = _require_version_capability(resolve_adapter(adapter))
    try:
        versions: list[ProjectVersion] = pm.list_versions(project)
    except Exception as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(1) from exc

    if format == "agent":
        for version in versions:
            _print_version_agent(version)
        return

    if not versions:
        console.print(f"No versions found for {project}")
        return
    for version in versions:
        status = []
        if version.released:
            status.append("released")
        if version.archived:
            status.append("archived")
        suffix = f" ({', '.join(status)})" if status else ""
        release = f" — {version.release_date}" if version.release_date else ""
        console.print(f"{version.name}{suffix}{release}")


@version_app.command("create")
def version_create(
    name: Annotated[str, typer.Argument(help="Version name (e.g., 3.2)")],
    project: Annotated[
        str, typer.Option("--project", "-p", help="Project key (e.g., RAISE)")
    ],
    adapter: AdapterOption = None,
    format: FormatOption = "human",
) -> None:
    """Create a project fixVersion/release version if missing."""
    _validate_format(format)
    pm = _require_version_capability(resolve_adapter(adapter))
    try:
        version: ProjectVersion = pm.create_version(project, name)
    except Exception as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(1) from exc

    state = "created" if version.created else "exists"
    if format == "agent":
        print(f"{version.name}|{state}|{version.id}")
        return
    label = "Created" if version.created else "Already exists"
    console.print(f"{label}: {version.name}")


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
        typer.Option(
            "--description",
            "-d",
            help="Short inline description; prefer --description-file for Markdown",
        ),
    ] = None,
    description_file: Annotated[
        Path | None,
        typer.Option(
            "--description-file",
            help="Path to a Markdown file; safe for backticks, $vars, newlines",
        ),
    ] = None,
    description_stdin: Annotated[
        bool,
        typer.Option(
            "--description-stdin",
            help="Read description from stdin; safe for piped Markdown",
        ),
    ] = False,
    field: Annotated[
        list[str] | None,
        typer.Option(
            "--field",
            "-F",
            help="Custom field by ID (e.g. customfield_13267=Value, repeatable). Select fields auto-wrapped.",
        ),
    ] = None,
    local: Annotated[
        bool,
        typer.Option(
            "--local",
            help=(
                "Local-only work item (ontology types only) — skip Jira "
                "entirely, jira_key stays NULL (scratch-guard, mirrors "
                "`rai mission new --scratch`)"
            ),
        ),
    ] = False,
    adapter: AdapterOption = None,
    format: FormatOption = "human",
) -> None:
    """Create a new backlog item."""
    _validate_format(format)
    pm = resolve_adapter(adapter)
    # Resolve localized type alias (e.g. "Historia" → "Story") before creating.
    issue_type = _resolve_issue_type_alias(issue_type, adapter)

    if _is_ontology_type(issue_type):
        _create_work_item(
            summary=summary,
            project=project,
            issue_type=cast("WorkItemType", issue_type),
            parent=parent,
            description=_resolve_description(
                description, description_file, description_stdin
            ),
            local=local,
            format=format,
            pm=pm,
        )
        return

    metadata: dict[str, Any] = {}
    if field:
        metadata.update(_parse_fields(field))
    spec = IssueSpec(
        summary=summary,
        issue_type=issue_type,
        description=_resolve_description(
            description, description_file, description_stdin
        ),
        labels=labels.split(",") if labels else [],
        parent=parent or None,
        metadata=metadata,
    )
    try:
        ref = pm.create_issue(project, spec)
    except Exception as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(1) from exc

    # Defensive output for RAISE-3746 — Windows + Python 3.14 + asyncio +
    # httpx aclose() in SyncPMAdapter cleanup has been observed to leave
    # stdout in a "Bad file descriptor" state for non-Epic issue types.
    # The issue IS created in Jira; if printing the success message
    # crashes the user sees exit 1 and re-runs, creating duplicates.
    # Fall back to a bare stdout write that bypasses rich entirely so the
    # user always sees the key and exit code is 0 when the create
    # succeeded.
    success_msg = ref.key if format == "agent" else f"Created: {ref.key}"
    try:
        if format == "agent":
            print(ref.key)
        else:
            console.print(success_msg)
    except (OSError, ValueError):
        # OSError covers [Errno 9] Bad file descriptor; ValueError covers
        # "I/O operation on closed file". Fall back to __stdout__ which
        # references the original process stdout even if the rich Console
        # or the current sys.stdout has been replaced/closed during async
        # cleanup. Best-effort — silent if even this fails.
        with contextlib.suppress(Exception):
            sys.__stdout__.write(success_msg + "\n")  # type: ignore[union-attr]
            sys.__stdout__.flush()  # type: ignore[union-attr]


def _report_write_outcome(ref: IssueRef, success_msg: str) -> None:
    """Print CLI feedback for a write based on ``IssueRef.remote_synced`` (RAISE-12598).

    RAISE-11745: the composite adapter can silently queue a write locally
    (unmapped ledger key, no remote configured, transient remote failure)
    while the caller sees no exception. ``remote_synced`` carries that
    outcome so this is the single place the CLI decides how loud to be:

    - ``True`` or ``None`` (older/unrelated call sites that don't set the
      field) \u2014 unchanged plain success line, exit 0.
    - ``False`` with a remote configured (reason != "no_remotes") \u2014 this is
      the false-positive-success failure mode: loud WARNING to stderr,
      exit 1.
    - ``False`` with no remote configured (reason == "no_remotes") \u2014 pure
      local/offline project; queueing is expected behavior, not a failure:
      informational notice, exit 0.
    """
    if ref.remote_synced is not False:
        console.print(success_msg)
        return
    reason = ref.metadata.get("remote_sync_reason", "unknown")
    if reason == "no_remotes":
        console.print(
            f"{success_msg} [dim](queued locally; no remote configured)[/dim]"
        )
        return
    err_console.print(
        f"[bold red]Warning:[/bold red] {ref.key}: queued locally; "
        f"NOT yet on remote (reason: {reason}) \u2014 run "
        "'rai backlog pending-ops list --dead' or verify manually."
    )
    raise typer.Exit(1)


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
    _report_write_outcome(ref, f"{ref.key}: transitioned \u2192 {status}")


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
    parent: Annotated[
        str | None, typer.Option("--parent", help="Parent issue key")
    ] = None,
    issue_type: Annotated[
        str | None, typer.Option("--type", "-t", help="Issue type")
    ] = None,
    fix_version: Annotated[
        str | None,
        typer.Option(
            "--fix-version",
            help="Fix version name (REPLACES any existing fixVersions on the issue)",
        ),
    ] = None,
    description: Annotated[
        str | None,
        typer.Option(
            "--description",
            "-d",
            help="Short inline description; prefer --description-file for Markdown",
        ),
    ] = None,
    description_file: Annotated[
        Path | None,
        typer.Option(
            "--description-file",
            help="Path to a Markdown file; safe for backticks, $vars, newlines",
        ),
    ] = None,
    description_stdin: Annotated[
        bool,
        typer.Option(
            "--description-stdin",
            help="Read description from stdin; safe for piped Markdown",
        ),
    ] = False,
    field: Annotated[
        list[str] | None,
        typer.Option(
            "--field",
            "-F",
            help="Custom field by ID (e.g. customfield_13267=Value, repeatable). Select fields auto-wrapped.",
        ),
    ] = None,
    adapter: AdapterOption = None,
) -> None:
    """Update fields on a backlog item."""
    pm = resolve_adapter(adapter)
    fields: dict[str, Any] = {}
    if field:
        fields.update(_parse_fields(field))
    fields.update(
        _collect_simple_update_fields(
            summary=summary,
            labels=labels,
            priority=priority,
            assignee=assignee,
            parent=parent,
            issue_type=issue_type,
            fix_version=fix_version,
            adapter=adapter,
        )
    )
    resolved_desc = _resolve_description(
        description, description_file, description_stdin
    )
    if resolved_desc:
        fields["description"] = resolved_desc

    if not fields:
        console.print("[yellow]Warning:[/yellow] No fields to update.")
        raise typer.Exit(0)

    try:
        ref = pm.update_issue(key, fields)
    except Exception as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(1) from exc
    _report_write_outcome(ref, f"{ref.key}: updated")


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
        linked = pm.link_issues(source, target, link_type)
    except Exception as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(1) from exc
    if linked:
        console.print(f"{source} \u2192 {link_type} \u2192 {target}: linked")
    else:
        console.print(f"{source} \u2192 {link_type} \u2192 {target}: queued for replay")


@backlog_app.command()
def reparent(
    child: Annotated[str, typer.Argument(help="Child issue key (bug/story)")],
    parent: Annotated[str, typer.Argument(help="Parent epic key")],
    adapter: AdapterOption = None,
) -> None:
    """Set the Epic parent of an existing issue (wraps link_to_parent)."""
    pm = resolve_adapter(adapter)
    try:
        confirmed = pm.link_to_parent(child, parent)
    except Exception as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(1) from exc
    if confirmed:
        console.print(f"{child} \u2192 parent \u2192 {parent}: reparented")
    else:
        console.print(f"{child} \u2192 parent \u2192 {parent}: queued for replay")


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
    console.print(escape(detail.summary))

    # Optional fields — only show when non-empty
    if detail.assignee:
        console.print(f"Assignee: {detail.assignee}")
    if detail.labels:
        console.print(f"Labels:   {', '.join(detail.labels)}")
    if detail.parent_key:
        console.print(f"Parent:   {detail.parent_key}")
    if detail.priority:
        console.print(f"Priority: {detail.priority}")
    if detail.comment_count:
        console.print(f"Comments: [{detail.comment_count}]")
    if detail.created:
        console.print(f"Created:  {detail.created}")

    # Description
    if detail.description:
        console.print()
        console.print(escape(detail.description))


@backlog_app.command("get-comments")
def get_comments(
    key: Annotated[str, typer.Argument(help="Issue key (e.g., RAISE-123)")],
    limit: Annotated[int, typer.Option("--limit", "-n", help="Max comments")] = 10,
    offset: Annotated[int, typer.Option("--offset", help="Start from comment N")] = 0,
    all_results: Annotated[
        bool, typer.Option("--all", help="Return all comments")
    ] = False,
    adapter: AdapterOption = None,
) -> None:
    """Retrieve comments for a backlog item."""
    pm = resolve_adapter(adapter)
    try:
        comments = pm.get_comments(
            key, limit=limit, offset=offset, fetch_all=all_results
        )
    except Exception as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(1) from exc

    if not comments:
        console.print("No comments.")
        return

    for c in comments:
        # Truncate timestamp to date+time (drop timezone for compactness)
        ts = c.created[:19].replace("T", " ") if c.created else ""
        console.print(escape(f"[{ts}] {c.author}:"))
        # Indent comment body
        for line in c.body.splitlines():
            console.print(f"  {escape(line)}")
        console.print()


sprint_app = typer.Typer(
    name="sprint",
    help="Sprint visibility and assignment (Jira-specific)",
    no_args_is_help=True,
)
backlog_app.add_typer(sprint_app)


@sprint_app.command("list")
def sprint_list(
    project: Annotated[str, typer.Argument(help="Project key (e.g., RAISE)")],
    state: Annotated[
        str | None, typer.Option("--state", help="Filter: active, future, or closed")
    ] = None,
    adapter: AdapterOption = None,
) -> None:
    """List sprints for a project."""
    pm = resolve_adapter(adapter)
    try:
        sprints = pm.get_sprints(project, state=state)  # type: ignore[attr-defined]
    except Exception as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(1) from exc

    if not sprints:
        console.print("No sprints found.")
        return

    for s in sprints:
        date_range = ""
        if s.start_date and s.end_date:
            date_range = f"  {s.start_date[:10]} → {s.end_date[:10]}"
        console.print(f"[{s.id}]  {s.name}  ({s.state}){date_range}")


@sprint_app.command("assign")
def sprint_assign(
    key: Annotated[str, typer.Argument(help="Issue key (e.g., RAISE-123)")],
    sprint_id: Annotated[int, typer.Argument(help="Sprint ID")],
    adapter: AdapterOption = None,
) -> None:
    """Assign an issue to a sprint."""
    pm = resolve_adapter(adapter)
    try:
        pm.assign_to_sprint(key, sprint_id)  # type: ignore[attr-defined]
    except Exception as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(1) from exc

    console.print(f"{key} → sprint {sprint_id}")


@backlog_app.command()
def attach(
    key: Annotated[str, typer.Argument(help="Issue key (e.g., RAISE-123)")],
    file: Annotated[Path, typer.Argument(help="Path to the file to upload")],
    mime_type: Annotated[
        str | None, typer.Option("--mime-type", help="MIME type (inferred if omitted)")
    ] = None,
    adapter: AdapterOption = None,
) -> None:
    """Upload a file attachment to a backlog item."""
    if not file.exists():
        console.print(f"[red]Error:[/red] File not found: {file}")
        raise typer.Exit(1)
    pm = resolve_adapter(adapter)
    try:
        ref = pm.attach(key, file, mime_type)
    except Exception as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(1) from exc
    console.print(f"Attached: {ref.filename} (ID: {ref.id})")


@backlog_app.command(name="get-attachments")
def get_attachments(
    key: Annotated[str, typer.Argument(help="Issue key (e.g., RAISE-123)")],
    download: Annotated[
        Path | None,
        typer.Option("--download", help="Download all attachments to this directory"),
    ] = None,
    adapter: AdapterOption = None,
) -> None:
    """List (and optionally download) attachments on a backlog item."""
    from rich.table import Table

    pm = resolve_adapter(adapter)
    try:
        attachments = pm.get_attachments(key)
    except Exception as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(1) from exc

    if not attachments:
        console.print("No attachments.")
        return

    if download:
        download.mkdir(parents=True, exist_ok=True)
        for att in attachments:
            try:
                content = pm.download_attachment(att.id)
            except Exception as exc:
                console.print(f"[red]Error:[/red] downloading {att.filename}: {exc}")
                raise typer.Exit(1) from exc
            (download / att.filename).write_bytes(content)
            size_kb = len(content) / 1024
            console.print(f"Downloaded: {download / att.filename} ({size_kb:.1f} KB)")
    else:
        table = Table(show_header=True, header_style="bold")
        table.add_column("filename")
        table.add_column("mime_type")
        table.add_column("size")
        table.add_column("created")
        for att in attachments:
            size_str = (
                f"{att.size / 1024:.1f} KB" if att.size >= 1024 else f"{att.size} B"
            )
            created_str = (
                att.created_at[:19].replace("T", " ") if att.created_at else ""
            )
            table.add_row(att.filename, att.mime_type, size_str, created_str)
        console.print(table)


@backlog_app.command()
def search(
    query: Annotated[
        str,
        typer.Argument(
            help="Search query (format depends on adapter, e.g., JQL for Jira)"
        ),
    ],
    limit: Annotated[int, typer.Option("--limit", "-n", help="Max results")] = 50,
    offset: Annotated[int, typer.Option("--offset", help="Start from result N")] = 0,
    all_results: Annotated[
        bool, typer.Option("--all", help="Return all results")
    ] = False,
    adapter: AdapterOption = None,
    format: FormatOption = "human",
    org: Annotated[
        str | None,
        typer.Option(
            "--org", help="Override default org (sets RAISE_BACKLOG_ORG, RAISE-6248)"
        ),
    ] = None,
) -> None:
    """Search backlog items. Query format is adapter-specific (AR5)."""
    _validate_format(format)
    if org:
        os.environ["RAISE_BACKLOG_ORG"] = org
    pm = resolve_adapter(adapter)
    try:
        results = pm.search(query, limit=limit, offset=offset, fetch_all=all_results)
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
    dry_run: Annotated[
        bool,
        typer.Option(
            "--dry-run",
            help="Print planned transitions with [dry-run] prefix; execute nothing (exit 0)",
        ),
    ] = False,
    force: Annotated[
        bool,
        typer.Option(
            "--force",
            help="Bypass _pipeline_run_active engine-ownership guard and proceed",
        ),
    ] = False,
    adapter: AdapterOption = None,
) -> None:
    """Transition multiple backlog items at once.

    With ``--dry-run``: prints planned transitions, makes no changes (S15036 AC3).
    With ``--force``: bypasses the engine-ownership guard (S15036 AC4).
    """
    pm = resolve_adapter(adapter)
    key_list = [k.strip() for k in keys.split(",") if k.strip()]
    if not key_list:
        console.print("[red]Error:[/red] No valid keys provided.")
        raise typer.Exit(1)

    # AC3: --dry-run \u2014 print planned transitions, execute nothing
    if dry_run:
        for key in key_list:
            console.print(f"[dry-run] {key} \u2192 {status}", markup=False)
        raise typer.Exit(0)

    # AC4: engine-ownership guard \u2014 block manual transitions when pipeline runs are active
    if force:
        console.print("[force] bypassing engine_owned guard", markup=False)
    elif _pipeline_run_active():
        console.print(
            "[yellow]Warning:[/yellow] pipeline run is active \u2014 skipping batch-transition "
            "(use --force to bypass engine_owned guard)"
        )
        raise typer.Exit(0)

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


@backlog_app.command("batch-create")
def batch_create(
    file: Annotated[
        Path, typer.Option("--file", "-f", help="YAML file with a list of issue specs")
    ],
    adapter: AdapterOption = None,
) -> None:
    """Create multiple backlog items from a YAML file."""
    if not file.exists():
        console.print(f"[red]Error:[/red] File not found: {file}")
        raise typer.Exit(1)

    try:
        raw = yaml.safe_load(file.read_text())
    except Exception as exc:
        console.print(f"[red]Error:[/red] Failed to parse YAML: {exc}")
        raise typer.Exit(1) from exc

    if not isinstance(raw, list):
        console.print("[red]Error:[/red] YAML file must contain a list of issue specs.")
        raise typer.Exit(1)

    specs = [IssueSpec(**item) for item in raw]
    pm = resolve_adapter(adapter)

    try:
        result = pm.batch_create(specs)
    except Exception as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(1) from exc

    succeeded = len(result.succeeded)
    total = succeeded + len(result.failed)
    console.print(f"{succeeded}/{total} created")
    for failure in result.failed:
        console.print(f"  [red]{CROSS}[/red] {failure.key}: {failure.error}")


@backlog_app.command()
def unlink(
    link_id: Annotated[str, typer.Argument(help="Link ID to remove")],
    adapter: AdapterOption = None,
) -> None:
    """Remove a link between backlog items by link ID."""
    pm = resolve_adapter(adapter)
    try:
        pm.remove_link(link_id)
    except Exception as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(1) from exc
    console.print(f"{link_id}: removed")


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


@backlog_app.command("seed-from-git")
def seed_from_git(
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", help="Count insertable keys without writing rows"),
    ] = False,
    limit: Annotated[
        int | None,
        typer.Option("--limit", help="Restrict to the most recent N commits"),
    ] = None,
) -> None:
    """Backfill work_items with RAISE-XXXXX keys extracted from git history."""
    from raise_cli.backlog.seed import extract_raise_keys

    root = resolve_checkout_root()
    keys = extract_raise_keys(root, limit=limit)
    store = WorkItemStore(root)
    inserted, skipped = store.seed_jira_keys(keys, dry_run=dry_run)
    console.print(
        f"Scanned git history: [bold]{len(keys)}[/bold] unique RAISE keys found"
    )
    if dry_run:
        console.print(
            f"Would insert: [green]{inserted}[/green] | "
            f"Already present: [yellow]{skipped}[/yellow]"
        )
        console.print("[dim](dry run — no rows written)[/dim]")
    else:
        console.print(
            f"Inserted: [green]{inserted}[/green] | "
            f"Skipped (already present): [yellow]{skipped}[/yellow]"
        )


def _resolve_remote_adapter() -> Any:
    """Resolve a remote (non-filesystem) PM adapter for reconciliation."""
    import inspect

    from raise_cli.adapters.filesystem import FilesystemPMAdapter
    from raise_cli.adapters.sync import SyncPMAdapter
    from raise_cli.cli.commands._resolve import discover_pm  # noqa: PLC2701

    entries = discover_pm()
    for name, cls in entries.items():
        try:
            instance = cls()
            if inspect.iscoroutinefunction(getattr(instance, "get_issue", None)):
                instance = SyncPMAdapter(instance)
            if not isinstance(instance, FilesystemPMAdapter):
                return instance
        except Exception as exc:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
            console.print(f"  [red]{CROSS}[/red] {name}: {exc}")

    console.print(f"  [red]{CROSS}[/red] No remote adapter found")
    console.print("  Install a remote adapter (e.g., Jira) to reconcile.")
    raise typer.Exit(2)


def _display_reconcile_preview(actions: list[Any]) -> tuple[int, int, int]:
    """Display reconcile preview. Returns (link_count, create_count, review_count)."""
    from raise_cli.backlog.reconcile import ReconcileAction

    links = creates = reviews = 0
    action: ReconcileAction
    for action in actions:
        if action.action == "link":
            console.print(
                f"  [green]LINK[/green]    {action.local_id} ↔ {action.jira_key} ({action.reason})"
            )
            links += 1
        elif action.action == "create":
            console.print(
                f'  [cyan]CREATE[/cyan]  {action.local_id} "{action.title}" → new {action.item_type}'
            )
            creates += 1
        elif action.action == "review":
            console.print(
                f"  [yellow]REVIEW[/yellow]  {action.local_id} — {action.reason}"
            )
            reviews += 1
    return links, creates, reviews


def _display_reconcile_results(result: Any) -> None:
    """Display reconcile execution results."""
    for action in result.actions:
        if action.action == "link":
            console.print(
                f"  [green]{CHECK}[/green]  {action.local_id} {BIDIR} {action.jira_key}"
            )
        elif action.action == "create" and action.error:
            console.print(
                f"  [red]{CROSS}[/red]  {action.local_id} {ARROW} {action.error}"
            )
        elif action.action == "create":
            console.print(
                f"  [green]{CHECK}[/green]  {action.local_id} {ARROW} {action.jira_key}"
            )
        elif action.action == "review":
            console.print(f"  [dim]⊘[/dim]  {action.local_id} — skipped (review)")

    console.print(
        f"\n  Reconcile complete: {result.linked} linked, {result.created} created, "
        f"{result.reviewed} review, {result.failed} failed."
    )


@backlog_app.command()
def reconcile(
    project: Annotated[
        str, typer.Option("--project", "-p", help="Remote project key (e.g., RAISE)")
    ] = "RAISE",
    dry_run: Annotated[
        bool, typer.Option("--dry-run", help="Preview only, no changes")
    ] = False,
    link_only: Annotated[
        bool,
        typer.Option("--link-only", help="Only link existing matches, skip creates"),
    ] = False,
) -> None:
    """Reconcile work/epics/ artifacts against Jira.

    Scans filesystem for epics and stories, matches deterministically
    against Jira, and syncs: LINK existing, CREATE new, REVIEW ambiguous.
    """
    from raise_cli.backlog.reconcile import (
        execute_reconcile,
        fetch_jira_index,
        plan_reconcile,
    )
    from raise_cli.backlog.scanner import scan_work_epics
    from raise_cli.storage.work_items import WorkItemStore

    project_root = Path.cwd()

    # --- Phase 1: SCAN + VALIDATE ---
    console.print("\n[bold]Phase 1 — SCAN + VALIDATE[/bold]")

    items = scan_work_epics(project_root)
    console.print(
        f"  [green]{CHECK}[/green] Filesystem: {len(items)} items scanned from work/epics/"
    )

    remote = _resolve_remote_adapter()
    remote_health = remote.health()
    console.print(
        f"  [green]{CHECK}[/green] {remote_health.name}: {remote_health.message}"
    )

    # --- Phase 2: MATCH (Jira read-only) ---
    console.print("\n[bold]Phase 2 — MATCH[/bold]")

    jira_index = fetch_jira_index(remote, project)
    console.print(f"  Fetched {len(jira_index)} issues from Jira")

    wi_store = WorkItemStore(project_root)
    actions = plan_reconcile(items, jira_index, wi_store)

    if link_only:
        actions = [a for a in actions if a.action != "create"]

    # --- Phase 3: PREVIEW ---
    console.print("\n[bold]Phase 3 — PREVIEW[/bold]")

    links, creates, reviews = _display_reconcile_preview(actions)
    console.print(
        f"\n  Summary: {links} to link, {creates} to create, {reviews} to review (skipped)"
    )

    if dry_run:
        console.print("\n  [yellow]Dry run — no changes made.[/yellow]")
        raise typer.Exit(0)

    if not creates and not links:
        console.print("\n  Nothing to reconcile.")
        raise typer.Exit(0)

    # --- Phase 4: CONFIRM + EXECUTE ---
    if not typer.confirm("\nProceed with reconciliation?", default=False):
        raise typer.Exit(0)

    console.print("\n[bold]Phase 4 — EXECUTE[/bold]")
    result = execute_reconcile(actions, remote, wi_store, project)
    _display_reconcile_results(result)

    if result.failed > 0:
        raise typer.Exit(1)


# ── fields sub-app ────────────────────────────────────────────────────

fields_app = typer.Typer(
    name="fields",
    help="Manage custom field configuration for Jira",
    no_args_is_help=True,
)


@fields_app.command("_reserved", hidden=True, deprecated=True)
def _reserved_stub() -> None:  # pragma: no cover  # type: ignore[reportUnusedFunction]
    """PAT-E-1090: prevents Typer treating subcommand as argument."""


@fields_app.command()
def discover(  # noqa: C901 -- complexity from best-effort validation, refactor deferred
    names: Annotated[
        str | None,
        typer.Option(
            "--names", help="Comma-separated display names (e.g. 'Bug Type,Severity')"
        ),
    ] = None,
    project: Annotated[
        str | None,
        typer.Option(
            "--project",
            help='REMOVED — use `fields search --project KEY "query"` instead',
        ),
    ] = None,
    issue_type: Annotated[
        str | None,
        typer.Option(
            "--issue-type",
            help="Issue type for the field (e.g. 'Bug', 'Story', 'Task'). "
            "Use `rai backlog issue-types --project KEY` to list available types.",
        ),
    ] = None,
    org: OrgOption = None,
    context: Annotated[
        str | None,
        typer.Option(
            "--context",
            help="[deprecated] Use --issue-type instead.",
            hidden=True,
        ),
    ] = None,
    adapter: AdapterOption = None,
) -> None:
    """Discover custom fields by display name and save to .raise/backlog.yaml.

    Use --names to discover by display name, any issue type.
    To search fields by partial name, use `fields search --project KEY "query"`.
    To list valid issue types, use `rai backlog issue-types --project KEY`.
    """
    if org:
        os.environ["RAISE_BACKLOG_ORG"] = org
    if project:
        console.print(
            "[red]Error:[/red] --project is no longer supported here. "
            'Use `fields search --project KEY "query"` to search fields by name.'
        )
        raise typer.Exit(1)

    if not names:
        console.print("[red]Error:[/red] provide --names")
        raise typer.Exit(1)

    # Resolve issue type — --issue-type takes precedence; --context is deprecated alias
    if context is not None and issue_type is None:
        console.print(
            "[yellow]Warning:[/yellow] --context is deprecated, use --issue-type instead."
        )
        issue_type = context
    if issue_type is None:
        console.print("[red]Error:[/red] provide --issue-type (e.g. --issue-type Bug)")
        raise typer.Exit(1)

    # Resolve display name → canonical (e.g. "Historia" → "Story") before API call.
    bcfg: Any = None
    try:
        bcfg = load_backlog_config(Path.cwd(), get_effective_adapter_name(adapter))
        issue_type = bcfg.issue_type_aliases.get(issue_type, issue_type)
    except Exception:  # noqa: BLE001,S110 -- best-effort alias resolution, non-critical
        pass

    if issue_type is None:
        console.print("[red]Error:[/red] provide --issue-type (e.g. --issue-type Bug)")
        raise typer.Exit(1)
    resolved_issue_type = issue_type

    pm = resolve_adapter(adapter)

    # project_key drives createmeta scoping for discover_named_fields (RAISE-15667) —
    # computed once and reused for the issue-type warning below.
    proj_key = _infer_project_key(bcfg)

    # Best-effort: warn when issue_type is not found in Jira (S4180.4).
    try:
        if proj_key:
            known_types = pm.discover_issue_types(proj_key)
            if resolved_issue_type.lower() not in {
                it.name.lower() for it in known_types
            }:
                available = ", ".join(sorted(it.name for it in known_types))
                console.print(
                    f"[yellow]Warning:[/yellow] issue type '{resolved_issue_type}' not found in Jira. "
                    f"Available: {available}"
                )
    except Exception:  # noqa: BLE001,S110 -- best-effort, never blocks
        pass

    names_list = [n.strip() for n in names.split(",") if n.strip()]
    if not names_list:
        console.print(
            "[red]Error:[/red] --names must contain at least one non-empty name"
        )
        raise typer.Exit(1)
    try:
        named_fields = pm.discover_named_fields(
            names=names_list, issue_type=resolved_issue_type, project_key=proj_key
        )
    except Exception as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(1) from exc
    if not named_fields:
        console.print(f"No fields found for {names_list} — backlog.yaml not modified")
        return
    # Canonicalize casing before keying so repeated `fields discover` calls
    # with different operator-typed casing (e.g. "bug" vs "Bug") never
    # re-split custom_fields into sibling dict keys on disk (RAISE-10285).
    custom_fields_key = canonicalize_issue_type_key(resolved_issue_type)
    named_updates: dict[str, Any] = {
        "custom_fields": {
            custom_fields_key: [
                f.model_dump(exclude={"schema_type"}) for f in named_fields
            ]
        }
    }
    adapter_name = get_effective_adapter_name(adapter)
    save_backlog_config(Path.cwd(), adapter_name, named_updates)
    save_backlog_config(
        Path.cwd(),
        adapter_name,
        {"field_types": {f.id: f.schema_type for f in named_fields}},
    )
    console.print(
        f"Saved {len(named_fields)} field(s) to .raise/backlog.yaml (issue type: {resolved_issue_type})"
    )


def _print_fields_human(custom_fields: dict[str, list[Any]]) -> None:
    """Print custom_fields in human-readable format. Fields may be CustomField objects or dicts."""
    for section_name, section_fields in custom_fields.items():
        if not section_fields:
            continue
        console.print(f"custom_fields.{section_name}:")
        for field in section_fields:
            name = field.name if hasattr(field, "name") else field["name"]
            fid = field.id if hasattr(field, "id") else field["id"]
            contexts = (
                field.field_contexts
                if hasattr(field, "field_contexts")
                else field.get("field_contexts", [])
            )
            console.print(f"  {name}  {fid}")
            for ctx in contexts:
                is_global = (
                    ctx.is_global if hasattr(ctx, "is_global") else ctx.get("is_global")
                )
                ctx_name = ctx.name if hasattr(ctx, "name") else ctx["name"]
                values = ctx.values if hasattr(ctx, "values") else ctx.get("values", [])
                ctx_label = "global" if is_global else "project"
                console.print(f"    {ctx_name} ({ctx_label}):  {', '.join(values)}")


def _print_fields_agent(custom_fields: dict[str, list[Any]]) -> None:
    """Print custom_fields in pipe-delimited agent format. Fields may be CustomField objects or dicts."""
    for context_name, fields in custom_fields.items():
        for field in fields:
            name = field.name if hasattr(field, "name") else field["name"]
            fid = field.id if hasattr(field, "id") else field["id"]
            contexts = (
                field.field_contexts
                if hasattr(field, "field_contexts")
                else field.get("field_contexts", [])
            )
            for ctx in contexts:
                is_global = (
                    ctx.is_global if hasattr(ctx, "is_global") else ctx.get("is_global")
                )
                ctx_name = ctx.name if hasattr(ctx, "name") else ctx["name"]
                values = ctx.values if hasattr(ctx, "values") else ctx.get("values", [])
                is_global_str = "true" if is_global else "false"
                print(
                    f"{name}|{fid}|{context_name}|{ctx_name}|{is_global_str}|{','.join(values)}"
                )


@fields_app.command("search")
def search_fields(
    project: Annotated[str, typer.Option("--project", help="Project key (e.g. RAISE)")],
    query: Annotated[
        str, typer.Argument(help="Partial field name to search (case-insensitive)")
    ],
    adapter: AdapterOption = None,
    org: OrgOption = None,
) -> None:
    """Search custom fields by partial name (read-only)."""
    if org:
        os.environ["RAISE_BACKLOG_ORG"] = org
    pm = resolve_adapter(adapter)
    try:
        all_fields = pm.discover_fields(project)
    except Exception as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(1) from exc

    matches = [f for f in all_fields if query.lower() in f.name.lower()]
    if not matches:
        console.print(f"No fields found matching '{query}'")
        return

    for f in matches:
        console.print(f"{f.id}  {f.name}")


@fields_app.command("list")
def list_fields(
    format: FormatOption = "human",
    adapter: AdapterOption = None,
) -> None:
    """List custom fields configured in .raise/backlog.yaml."""
    _validate_format(format)
    try:
        config = load_backlog_config(Path.cwd(), get_effective_adapter_name(adapter))
    except (FileNotFoundError, KeyError) as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(1) from exc

    custom_fields = config.custom_fields
    if not custom_fields or not any(custom_fields.values()):
        console.print("No custom_fields configured in .raise/backlog.yaml.")
        return

    if format == "agent":
        _print_fields_agent(custom_fields)
    else:
        _print_fields_human(custom_fields)


# ── statuses sub-app ──────────────────────────────────────────────────

statuses_app = typer.Typer(
    name="statuses",
    help="Manage workflow status configuration",
    no_args_is_help=True,
)


@statuses_app.command("_reserved", hidden=True, deprecated=True)
def _reserved_statuses_stub() -> None:  # pragma: no cover  # type: ignore[reportUnusedFunction]  # fmt: skip
    """PAT-E-1090: prevents Typer treating subcommand as argument."""


def _infer_project_key(bcfg: Any) -> str | None:
    """Return the first project key from BacklogAdapterConfig.projects, or None."""
    return next(iter(bcfg.projects), None) if bcfg is not None else None


def _resolve_display_name(pm: Any, project_key: str, canonical_type: str) -> str | None:
    """Return the localized display name for canonical_type, or None if no mismatch.

    Unwraps the adapter chain (CompositeBacklogAdapter → LedgerAwareAdapter →
    SyncPMAdapter → JiraAdapter) using isinstance checks — same pattern as resolve.py.
    Stops immediately on any unknown type (MagicMock in tests, JiraAdapter in prod).
    """
    from raise_cli.adapters.composite_pm import CompositeBacklogAdapter
    from raise_cli.adapters.ledger_aware import LedgerAwareAdapter
    from raise_cli.adapters.sync import SyncPMAdapter as _SyncPMAdapter

    try:
        inner: Any = pm
        for _ in range(4):
            if isinstance(inner, CompositeBacklogAdapter):
                remotes = inner.remotes
                inner = remotes[0] if remotes else inner
            elif isinstance(inner, LedgerAwareAdapter):
                inner = inner.remote
            elif isinstance(inner, _SyncPMAdapter):
                inner = inner.adapter
            else:
                break
        # Route by project_key (RAISE-10004): default_org is an org name, not a
        # project key — _client_for(default_org) raises UnknownProjectKeyError.
        client = inner._client_for(project_key)  # type: ignore[union-attr]
        display_name = client.find_issue_type_display_name(project_key, canonical_type)  # type: ignore[reportUnknownVariableType]
        return display_name if isinstance(display_name, str) else None
    except Exception:  # noqa: S110,BLE001 -- best-effort, non-critical
        return None


def _resolve_canonical_name(pm: Any, project_key: str, display_type: str) -> str | None:
    """Return canonical Jira type name for a localized display name, or None.

    Unwraps adapter chain — same pattern as _resolve_display_name.
    Calls JiraClient.resolve_canonical_from_display (inverse of find_issue_type_display_name).
    """
    from raise_cli.adapters.composite_pm import CompositeBacklogAdapter
    from raise_cli.adapters.ledger_aware import LedgerAwareAdapter
    from raise_cli.adapters.sync import SyncPMAdapter as _SyncPMAdapter

    try:
        inner: Any = pm
        for _ in range(4):
            if isinstance(inner, CompositeBacklogAdapter):
                remotes = inner.remotes
                inner = remotes[0] if remotes else inner
            elif isinstance(inner, LedgerAwareAdapter):
                inner = inner.remote
            elif isinstance(inner, _SyncPMAdapter):
                inner = inner.adapter
            else:
                break
        # Route by project_key (RAISE-10004): default_org is an org name, not a
        # project key — _client_for(default_org) raises UnknownProjectKeyError.
        client = inner._client_for(project_key)  # type: ignore[union-attr]
        result = client.resolve_canonical_from_display(project_key, display_type)  # type: ignore[reportUnknownVariableType]
        return result if isinstance(result, str) else None
    except Exception:  # noqa: S110,BLE001 -- best-effort, non-critical
        return None


@statuses_app.command("discover")
def statuses_discover(  # noqa: C901 -- complexity 12, refactor deferred
    project_key: Annotated[str, typer.Argument(help="Jira project key (e.g. RAISE)")],
    issue_type: Annotated[
        str,
        typer.Option(
            "--issue-type", help="Issue type to filter statuses (default: Story)"
        ),
    ] = "Story",
    adapter: AdapterOption = None,
    org: OrgOption = None,
) -> None:
    """Discover workflow statuses for a project and save to .raise/backlog.yaml."""
    if org:
        os.environ["RAISE_BACKLOG_ORG"] = org
    pm = resolve_adapter(adapter)

    # Resolve display name → canonical before the API call so passing either form works.
    # e.g. --issue-type Historia (display) → canonical "Story" for Jira, save under "Historia".
    canonical_type = issue_type
    try:
        cfg = load_backlog_config(Path.cwd(), get_effective_adapter_name(adapter))
        canonical_type = cfg.issue_type_aliases.get(issue_type, issue_type)
    except Exception:  # noqa: BLE001,S110 -- best-effort alias resolution, non-critical
        pass

    try:
        states = pm.discover_statuses(project_key, issue_type=canonical_type)
    except Exception as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(1) from exc

    if not states and canonical_type == issue_type:
        resolved = _resolve_canonical_name(pm, project_key, issue_type)
        if resolved:
            try:
                states = pm.discover_statuses(project_key, issue_type=resolved)
            except Exception:  # noqa: BLE001,S110 -- best-effort fallback
                states = []
            if states:
                canonical_type = resolved
                save_backlog_config(
                    Path.cwd(),
                    get_effective_adapter_name(adapter),
                    {"issue_type_aliases": {issue_type: canonical_type}},
                )
                console.print(
                    f"[dim]Resolved '{issue_type}' → '{canonical_type}' via Jira API[/dim]"
                )

    if not states:
        import contextlib

        available: list[str] = []
        with contextlib.suppress(Exception):
            available = [it.name for it in pm.discover_issue_types(project_key)]
        types_hint = f" Available types: {', '.join(available)}" if available else ""
        console.print(
            f"[red]Error:[/red] issue type '{issue_type}' not found in project {project_key}.{types_hint}"
        )
        raise typer.Exit(1)

    for s in states:
        console.print(f"{s.name:<20} id={s.id:<8} category={s.status_category}")

    # Detect localization mismatch to find the display name used as the workflow key.
    # If input was already a display name, skip the Jira lookup — use it directly.
    workflow_key = issue_type
    updates: dict[str, Any] = {}
    if canonical_type == issue_type:
        display_name = _resolve_display_name(pm, project_key, canonical_type)
        if display_name is not None:
            workflow_key = display_name
            updates["issue_type_aliases"] = {display_name: canonical_type}

    status_mapping = [s.name for s in states]
    updates["workflow"] = {
        workflow_key: {
            "states": [s.model_dump() for s in states],
            "status_mapping": status_mapping,
        }
    }
    save_backlog_config(Path.cwd(), get_effective_adapter_name(adapter), updates)
    console.print(
        f"Saved {len(states)} status(es) for issue type '{issue_type}' to .raise/backlog.yaml"
    )


def _print_statuses_human(workflow: dict[str, WorkflowConfig]) -> None:
    for itype, wf_config in workflow.items():
        console.print(f"{itype}:")
        for s in wf_config.states:
            name: str = s.get("name", "")
            sid: str = s.get("id", "")
            cat: str = s.get("status_category", "")
            console.print(f"  {name:<20} id={sid:<8} category={cat}")


def _print_statuses_agent(workflow: dict[str, WorkflowConfig]) -> None:
    for itype, wf_config in workflow.items():
        for s in wf_config.states:
            name: str = s.get("name", "")
            sid: str = s.get("id", "")
            print(
                f"{_sanitize_pipe(name)}|{_sanitize_pipe(sid)}|{_sanitize_pipe(itype)}"
            )


@statuses_app.command("list")
def statuses_list(
    issue_type: Annotated[
        str | None,
        typer.Option("--issue-type", help="Filter by issue type (e.g. Bug, Story)"),
    ] = None,
    format: FormatOption = "human",
    adapter: AdapterOption = None,
) -> None:
    """List workflow statuses configured in .raise/backlog.yaml."""
    _validate_format(format)
    try:
        config = load_backlog_config(Path.cwd(), get_effective_adapter_name(adapter))
    except (FileNotFoundError, KeyError) as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(1) from exc

    workflow = config.workflow
    if not workflow:
        console.print("No workflow statuses configured in .raise/backlog.yaml.")
        return

    effective_type = issue_type
    if issue_type and issue_type not in workflow:
        # Try reverse alias: canonical ("Story") → display name ("Historia") used as key.
        reverse = {v: k for k, v in config.issue_type_aliases.items()}
        candidate = reverse.get(issue_type)
        if candidate and candidate in workflow:
            effective_type = candidate
        else:
            console.print(
                f"[red]Error:[/red] issue type '{issue_type}' not found in workflow config. "
                f"Available: {list(workflow.keys())}"
            )
            raise typer.Exit(1)

    filtered = (
        {effective_type: workflow[effective_type]} if effective_type else workflow
    )
    if format == "agent":
        _print_statuses_agent(filtered)
    else:
        _print_statuses_human(filtered)


# ── link-types sub-app ───────────────────────────────────────────────

link_types_app = typer.Typer(
    name="link-types",
    help="Manage issue relation type configuration",
    no_args_is_help=True,
)


@link_types_app.command("_reserved", hidden=True, deprecated=True)
def _reserved_link_types_stub() -> None:  # pragma: no cover  # type: ignore[reportUnusedFunction]  # fmt: skip
    """PAT-E-1090: prevents Typer treating subcommand as argument."""


@link_types_app.command("discover")
def link_types_discover(
    adapter: AdapterOption = None,
    org: OrgOption = None,
) -> None:
    """Discover relation types from Jira and save to .raise/backlog.yaml."""
    if org:
        os.environ["RAISE_BACKLOG_ORG"] = org
    pm = resolve_adapter(adapter)
    try:
        types = pm.discover_link_types()
    except Exception as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(1) from exc

    for lt in types:
        console.print(
            f"{lt.name} (id={lt.id})  outward: {lt.outward} / inward: {lt.inward}"
        )

    updates: dict[str, Any] = {"relation_types": [lt.model_dump() for lt in types]}
    save_backlog_config(Path.cwd(), get_effective_adapter_name(adapter), updates)
    console.print(f"Saved {len(types)} relation type(s) to .raise/backlog.yaml")


@link_types_app.command("list")
def link_types_list(
    adapter: AdapterOption = None,
) -> None:
    """List relation types configured in .raise/backlog.yaml."""
    try:
        config = load_backlog_config(Path.cwd(), get_effective_adapter_name(adapter))
    except (FileNotFoundError, KeyError) as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(1) from exc

    types = config.relation_types
    if not types:
        console.print(
            "0 relation types configured — run 'rai backlog link-types discover' first"
        )
        return

    for lt in types:
        console.print(
            f"{lt.get('name', '?')} (id={lt.get('id', '?')})"
            f"  outward: {lt.get('outward', '?')} / inward: {lt.get('inward', '?')}"
        )
    console.print(f"{len(types)} relation type(s) configured in .raise/backlog.yaml")


# ── issue-types sub-app ──────────────────────────────────────────────

issue_types_app = typer.Typer(
    name="issue-types",
    help="Manage issue type configuration",
    no_args_is_help=True,
)


@issue_types_app.command("_reserved", hidden=True, deprecated=True)
def _reserved_issue_types_stub() -> None:  # pragma: no cover  # type: ignore[reportUnusedFunction]  # fmt: skip
    """PAT-E-1090: prevents Typer treating subcommand as argument."""


@issue_types_app.command("list")
def issue_types(
    project_key: Annotated[str, typer.Argument(help="Project key (e.g. RAISE)")],
    adapter: AdapterOption = None,
    org: OrgOption = None,
) -> None:
    """List issue types available in a project (read-only)."""
    if org:
        os.environ["RAISE_BACKLOG_ORG"] = org
    pm = resolve_adapter(adapter)
    try:
        types = pm.discover_issue_types(project_key)
    except Exception as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(1) from exc

    if not types:
        console.print(f"0 issue types found for project {project_key}")
        return

    for it in types:
        console.print(f"{it.name:<20} {it.id}")


@issue_types_app.command("discover")
def issue_types_discover(
    project_key: Annotated[str, typer.Argument(help="Project key (e.g. RAISE)")],
    adapter: AdapterOption = None,
    org: OrgOption = None,
) -> None:
    """Discover issue types and assign key prefixes in .raise/backlog.yaml.

    Fixed prefixes (Epic→e, Story→s, Bug→b) are always injected.
    Custom types receive the shortest unique lowercase prefix.
    Existing prefixes are never overwritten (immutable once assigned).
    """
    if org:
        os.environ["RAISE_BACKLOG_ORG"] = org
    pm = resolve_adapter(adapter)
    try:
        types = pm.discover_issue_types(project_key)
    except Exception as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(1) from exc

    adapter_name = get_effective_adapter_name(adapter)
    try:
        config = load_backlog_config(Path.cwd(), adapter_name)
        existing = dict(config.issue_type_prefixes)
    except Exception:  # noqa: BLE001
        existing = {}

    # Inject fixed prefixes first (never overwrite)
    for type_name, prefix in FIXED_PREFIXES.items():
        existing.setdefault(type_name, prefix)

    for it in types:
        if it.name not in existing:
            existing[it.name] = assign_prefix(it.name, existing)

    save_backlog_config(Path.cwd(), adapter_name, {"issue_type_prefixes": existing})

    lines = "\n".join(
        f"  {name:<18} → {pfx}{'  (fixed)' if name in FIXED_PREFIXES else ''}"
        for name, pfx in existing.items()
    )
    console.print(
        f"Discovered {len(types)} type(s). Saved prefixes to .raise/backlog.yaml\n{lines}"
    )


backlog_app.add_typer(fields_app, name="fields")
backlog_app.add_typer(statuses_app, name="statuses")
backlog_app.add_typer(issue_types_app, name="issue-types")
backlog_app.add_typer(link_types_app, name="link-types")


# ── projects sub-app ──────────────────────────────────────────────────

projects_app = typer.Typer(
    name="projects",
    help="List projects configured in .raise/backlog.yaml",
    no_args_is_help=True,
)


@projects_app.command("_reserved", hidden=True, deprecated=True)
def _reserved_projects_stub() -> None:  # pragma: no cover  # type: ignore[reportUnusedFunction]  # fmt: skip
    """PAT-E-1090: prevents Typer treating subcommand as argument."""


@projects_app.command("list")
def projects_list(
    adapter: AdapterOption = None,
    org: Annotated[
        str | None,
        typer.Option("--org", help="Filter to a single org (RAISE-6248)"),
    ] = None,
) -> None:
    """List projects configured in .raise/backlog.yaml (no credentials required)."""
    try:
        config = load_backlog_config(Path.cwd(), get_effective_adapter_name(adapter))
    except (FileNotFoundError, KeyError) as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(1) from exc

    has_projects = False
    for org_name, org_cfg in config.organizations.items():
        if org and org_name != org:
            continue
        if not org_cfg.projects:
            continue
        has_projects = True
        console.print(f"{org_name}:")
        for key in org_cfg.projects:
            proj = config.projects.get(key)
            desc = (
                getattr(proj, "description", None)
                or (proj.name if proj else None)
                or key
            )
            console.print(f"  {key:<8} — {desc}")

    if not has_projects:
        console.print("No projects configured.")


backlog_app.add_typer(projects_app, name="projects")


# ── pending-ops sub-app ───────────────────────────────────────────────

pending_ops_app = typer.Typer(
    name="pending-ops",
    help="Inspect and manage the pending-ops journal",
    no_args_is_help=True,
)


def _format_op_line(op: Any, *, show_error: bool = False) -> str:
    """Format a single pending op for human display."""
    attempts = f"({op.attempt_count} attempt{'s' if op.attempt_count != 1 else ''})"
    err = ""
    if show_error and op.last_error:
        truncated = op.last_error[:80]
        err = f"  {truncated}{'…' if len(op.last_error) > 80 else ''}"
    return f"  {op.id}  {op.op}  {op.key}  {op.ts}  {attempts}{err}"


def _format_op_agent(op: Any, *, show_error: bool = False) -> str:
    """Format a single pending op for agent (pipe-delimited) display."""
    if show_error:
        return (
            f"{op.id}|{op.op}|{op.key}|{op.ts}|{op.attempt_count}|{op.last_error or ''}"
        )
    return f"{op.id}|{op.op}|{op.key}|{op.ts}|{op.attempt_count}"


@pending_ops_app.command("list")
def pending_ops_list(
    dead: Annotated[
        bool,
        typer.Option("--dead", help="Show dead-letter ops instead of active queue"),
    ] = False,
    fmt: FormatOption = "human",
) -> None:
    """List pending ops or dead-letter ops."""
    from raise_cli.adapters.pending_ops import PendingOpsLog

    log = PendingOpsLog(domain="backlog", project_root=Path.cwd())
    ops = list(log.iter_dead_letter() if dead else log.iter())
    label = "dead-letter" if dead else "ops queued"

    if fmt == "agent":
        for op in ops:
            print(_format_op_agent(op, show_error=dead))
        return
    if not ops:
        console.print(f"0 {label}")
        return
    count = len(ops)
    console.print(f"{count} {label}:")
    for op in ops:
        console.print(_format_op_line(op, show_error=dead))


@pending_ops_app.command("count")
def pending_ops_count() -> None:
    """Print the number of pending ops (for scripting)."""
    from raise_cli.adapters.pending_ops import PendingOpsLog

    log = PendingOpsLog(domain="backlog", project_root=Path.cwd())
    print(log.pending_count())


@pending_ops_app.command("purge")
def pending_ops_purge(
    op_id: Annotated[
        str | None,
        typer.Option("--id", help="Remove only the op with this id"),
    ] = None,
    dead: Annotated[
        bool,
        typer.Option("--dead", help="Purge dead-letter ops instead of active queue"),
    ] = False,
    yes: Annotated[
        bool,
        typer.Option("-y", "--yes", help="Skip confirmation prompt"),
    ] = False,
) -> None:
    """Remove pending ops from the queue."""
    from raise_cli.adapters.pending_ops import PendingOpsLog

    log = PendingOpsLog(domain="backlog", project_root=Path.cwd())

    if dead:
        dead_ops = list(log.iter_dead_letter())
        count = len(dead_ops)
        if count == 0:
            console.print("0 dead-letter ops. Nothing to purge.")
            return
        if not yes:
            confirmed = typer.confirm(
                f"{count} dead-letter ops. Purge all?", default=False
            )
            if not confirmed:
                console.print("Aborted.")
                return
        removed = log.clear_dead_letter()
        console.print(f"Purged {removed} dead-letter op{'s' if removed != 1 else ''}.")
        return

    if op_id is not None:
        ops = list(log.iter())
        target = next((op for op in ops if op.id == op_id), None)
        if target is None:
            console.print(f"[red]Error:[/red] op '{op_id}' not found in queue")
            raise typer.Exit(1)
        log.mark_done(op_id)
        console.print(f"Removed op {op_id} ({target.op} {target.key})")
        return

    count = log.pending_count()
    if count == 0:
        console.print("0 ops queued. Nothing to purge.")
        return
    if not yes:
        confirmed = typer.confirm(f"{count} ops queued. Purge all?", default=False)
        if not confirmed:
            console.print("Aborted.")
            return
    removed = log.clear()
    console.print(f"Purged {removed} ops.")


backlog_app.add_typer(pending_ops_app, name="pending-ops")


# ── cartridge sub-app ─────────────────────────────────────────────────────────

from raise_core.cartridges.backlog_model import (  # noqa: E402,I001
    generate_backlog_model_cartridge,
)
from raise_core.cartridges.business_rules import (  # noqa: E402,I001
    enrich_cartridge_with_business_rules,
)

cartridge_app = typer.Typer(
    name="cartridge",
    help="Manage backlog model cartridges (.raise/cartridges/backlog-*).",
    no_args_is_help=True,
)

_CARTRIDGE_REQUIRED_KEYS = {"name", "org_id", "project_id", "schema_version"}


def _get_cartridges_dir(project_root: Path = Path(".")) -> Path:
    """Return the cartridges directory for the project."""
    return (project_root / ".raise" / "cartridges").resolve()


def _embed_cartridge_nodes(cartridge_dir: Path) -> None:
    """Generate and write embeddings for a backlog cartridge.

    Loads model.json and rules.json (if present) from the cartridge's instances/
    directory, runs EmbeddingGenerator with SentenceTransformerProvider, and
    writes embeddings.npy + embedding_index.json.  Missing node files are skipped
    gracefully.  Emits a console summary line on success.
    """
    from raise_core.cartridges.embedding import (
        EmbeddingGenerator,
        SentenceTransformerProvider,
        write_embeddings,
    )
    from raise_core.graph.models import GraphNode

    instances_dir = cartridge_dir / "instances"
    nodes: list[GraphNode] = []
    for fname in ("model.json", "rules.json"):
        fpath = instances_dir / fname
        if not fpath.exists():
            continue
        raw = json.loads(fpath.read_text(encoding="utf-8"))
        if not isinstance(raw, list):
            console.print(f"[yellow]Warning:[/yellow] {fname} is not a list — skipping")
            continue
        for item in raw:
            with contextlib.suppress(Exception):
                nodes.append(GraphNode.model_validate(item))
    if nodes:
        provider = SentenceTransformerProvider()
        generator = EmbeddingGenerator(provider)
        embeddings = generator.generate(nodes)
        write_embeddings(embeddings, nodes, instances_dir)
        console.print(
            f"[green]{CHECK}[/green] Embeddings generated: {len(embeddings)} nodes"
            " → embeddings.npy"
        )
    else:
        console.print(
            f"[yellow]Warning:[/yellow] no nodes found in {cartridge_dir.name}"
            " — embeddings skipped"
        )


def _unwrap_async_adapter(pm: Any) -> Any:
    """Unwrap the sync adapter stack to retrieve the underlying async adapter.

    Raises typer.Exit(1) when the active adapter is FilesystemPMAdapter (no API
    access) or when the inner adapter cannot be resolved.
    """
    from raise_cli.adapters.filesystem import FilesystemPMAdapter
    from raise_cli.adapters.sync import SyncPMAdapter

    inner: Any = pm
    # Unwrap up to 4 layers (CompositeBacklogAdapter → LedgerAwareAdapter → SyncPMAdapter)
    for _ in range(4):
        from raise_cli.adapters.composite_pm import CompositeBacklogAdapter
        from raise_cli.adapters.ledger_aware import LedgerAwareAdapter

        if isinstance(inner, CompositeBacklogAdapter):
            remotes = inner.remotes
            if not remotes:
                break
            inner = remotes[0]
        elif isinstance(inner, LedgerAwareAdapter):
            inner = inner.remote
        elif isinstance(inner, SyncPMAdapter):
            inner = inner.adapter
        else:
            break

    if isinstance(inner, (FilesystemPMAdapter, SyncPMAdapter)):
        console.print(
            "[red]Error:[/red] cartridge generate requires a remote adapter (e.g. Jira). "
            "Install a remote adapter and re-run."
        )
        raise typer.Exit(1)

    return inner


def _run_generate(
    project_key: str,
    org: str,
    enrich: bool,
    adapter: str | None,
    *,
    embed: bool = False,
) -> None:
    """Shared implementation for generate and refresh."""
    import asyncio

    pm = resolve_adapter(adapter)
    async_adapter = _unwrap_async_adapter(pm)
    cartridges_dir = _get_cartridges_dir(Path.cwd())

    try:
        cartridge_dir = asyncio.run(
            generate_backlog_model_cartridge(
                async_adapter,
                project_key,
                cartridges_dir,
                org_id=org,
            )
        )
    except Exception as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(1) from exc

    console.print(f"[green]{CHECK}[/green] Cartridge generated: {cartridge_dir.name}")

    if enrich:
        from raise_cli.adapters.llm_enrichment import AnthropicEnrichmentClient

        llm_client = AnthropicEnrichmentClient()
        try:
            asyncio.run(enrich_cartridge_with_business_rules(cartridge_dir, llm_client))
        except Exception as exc:
            console.print(f"[red]Error:[/red] enrichment failed: {exc}")
            raise typer.Exit(1) from exc
        console.print(
            f"[green]{CHECK}[/green] Business rules enriched: {cartridge_dir.name}"
        )

    if embed:
        _embed_cartridge_nodes(cartridge_dir)


@cartridge_app.command("generate")
def cartridge_generate(
    project_key: Annotated[str, typer.Argument(help="Jira project key (e.g. RAISE)")],
    org: Annotated[str, typer.Argument(help="Organisation identifier (e.g. humansys)")],
    enrich: Annotated[
        bool,
        typer.Option("--enrich", help="Derive business rules via LLM after generating"),
    ] = False,
    embed: Annotated[
        bool,
        typer.Option(
            "--embed", help="Regenerate embeddings.npy after model generation"
        ),
    ] = False,
    adapter: AdapterOption = None,
) -> None:
    """Generate a backlog MODEL cartridge from the Jira project schema."""
    _run_generate(project_key, org, enrich, adapter, embed=embed)


@cartridge_app.command("refresh")
def cartridge_refresh(
    project_key: Annotated[str, typer.Argument(help="Jira project key (e.g. RAISE)")],
    org: Annotated[str, typer.Argument(help="Organisation identifier (e.g. humansys)")],
    enrich: Annotated[
        bool,
        typer.Option("--enrich", help="Derive business rules via LLM after refreshing"),
    ] = False,
    embed: Annotated[
        bool,
        typer.Option("--embed", help="Regenerate embeddings.npy after model refresh"),
    ] = False,
    adapter: AdapterOption = None,
) -> None:
    """Re-generate the backlog MODEL cartridge (same as generate, idempotent)."""
    _run_generate(project_key, org, enrich, adapter, embed=embed)


@cartridge_app.command("list")
def cartridge_list() -> None:
    """List backlog cartridges found in .raise/cartridges/."""
    cartridges_dir = _get_cartridges_dir(Path.cwd())
    entries = (
        sorted(cartridges_dir.glob("backlog-*")) if cartridges_dir.exists() else []
    )
    if not entries:
        console.print("No backlog cartridges found in .raise/cartridges/")
        return
    for entry in entries:
        manifest_path = entry / "CARTRIDGE.yaml"
        if manifest_path.exists():
            try:
                manifest: dict[str, Any] = yaml.safe_load(
                    manifest_path.read_text(encoding="utf-8")
                )
                schema_ver: str = manifest.get("schema_version", "?")[:8]
                console.print(f"  {entry.name:<40} schema={schema_ver}")
            except Exception:  # noqa: BLE001
                console.print(f"  {entry.name} (unreadable CARTRIDGE.yaml)")
        else:
            console.print(f"  {entry.name} (missing CARTRIDGE.yaml)")


@cartridge_app.command("validate")
def cartridge_validate(
    cartridge_name: Annotated[str, typer.Argument(help="Cartridge directory name")],
) -> None:
    """Validate a cartridge directory — checks CARTRIDGE.yaml has required keys."""
    cartridges_dir = _get_cartridges_dir(Path.cwd())
    cartridge_dir = cartridges_dir / cartridge_name
    manifest_path = cartridge_dir / "CARTRIDGE.yaml"

    if not manifest_path.exists():
        console.print(f"[red]Error:[/red] CARTRIDGE.yaml not found in {cartridge_dir}")
        raise typer.Exit(1)

    try:
        manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:
        console.print(f"[red]Error:[/red] failed to parse CARTRIDGE.yaml: {exc}")
        raise typer.Exit(1) from exc

    missing = _CARTRIDGE_REQUIRED_KEYS - set(manifest or {})
    if missing:
        console.print(
            f"[red]Error:[/red] CARTRIDGE.yaml missing required keys: {sorted(missing)}"
        )
        raise typer.Exit(1)

    console.print(f"[green]{CHECK}[/green] {cartridge_name} is valid")


backlog_app.add_typer(cartridge_app, name="cartridge")
