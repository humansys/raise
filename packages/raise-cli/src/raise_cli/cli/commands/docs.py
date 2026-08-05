"""CLI commands for governance documentation via DocumentationTarget.

Provides the ``rai docs`` command group. All commands delegate to a
DocumentationTarget discovered via entry points. The target is resolved
automatically when exactly one is registered, or selected explicitly
via ``--target NAME``.

CLI owns domain logic (artifact type → local path convention).
Adapter owns platform config (space mapping, parent pages).

Architecture: E301 (Agent Tool Abstraction), ADR-034 (Governance)
"""

from __future__ import annotations

import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Annotated, cast

import typer
from rich.console import Console

from raise_cli.adapters.confluence_config import ArtifactRouting  # noqa: TC001
from raise_cli.adapters.confluence_exceptions import ConfluenceNotFoundError
from raise_cli.adapters.google_drive_exceptions import GoogleDriveAuthError
from raise_cli.cli.commands._resolve import resolve_docs_target
from raise_cli.cli.commands.docs_type import type_app
from raise_cli.docs.migrate import MigrationItem
from raise_cli.output.symbols import ARROW

docs_app = typer.Typer(
    name="docs",
    help="Manage governance documentation via DocumentationTarget",
    no_args_is_help=True,
)
docs_app.add_typer(type_app, name="type")

console = Console()

# Common option for target override (D5)
TargetOption = Annotated[
    str | None,
    typer.Option(
        "--target",
        "-t",
        help="Target name override; use 'all' to publish to every target",
    ),
]

# Convention: governance artifacts live at governance/{type}.md
GOVERNANCE_DIR = "governance"


def _to_slug(title: str) -> str:
    """Derive a URL-safe slug from an artifact title."""
    slug = title.lower()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-")


def _preload_routing(
    artifact_type: str, output_path: str | None
) -> ArtifactRouting | None:
    """Load routing config for artifact_type when output_path is not given.

    Returns None if --output-path was provided (routing unused).
    Raises typer.Exit(1) if docs.yaml is missing or invalid.
    """
    if output_path:
        return None
    from raise_cli.adapters.confluence_config import load_confluence_target_config

    try:
        return load_confluence_target_config(Path.cwd()).routing.get(artifact_type)
    except (FileNotFoundError, ValueError) as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(1) from exc


def _resolve_write_path(
    artifact_type: str,
    title: str,
    output_path: str | None,
    date: str | None,
    routing: ArtifactRouting | None = None,
) -> Path:
    """Resolve local destination path for rai docs write.

    Priority: --output-path > routing config (local_dir + naming) > ValueError

    ``routing`` may be pre-loaded by the caller to avoid a redundant config
    parse (the write command loads it once for both path resolution and the
    R2 date-warning).  Falls back to loading from docs.yaml when omitted.
    """
    if output_path:
        return Path(output_path)

    if routing is None:
        from raise_cli.adapters.confluence_config import load_confluence_target_config

        config = load_confluence_target_config(Path.cwd())
        routing = config.routing.get(artifact_type)

    if routing is None or routing.local_dir is None:
        raise ValueError(
            f"No local_dir configured for '{artifact_type}'. "
            "Use --output-path to specify destination."
        )

    slug = _to_slug(title)
    effective_date = date or datetime.now().strftime("%Y-%m-%d")

    if routing.naming == "dated":
        filename = f"{effective_date}-{slug}.md"
    else:
        filename = f"{slug}.md"

    return Path(routing.local_dir) / filename


def _resolve_artifact_path(artifact_type: str) -> Path:
    """Resolve artifact type to local file path by convention.

    Convention: ``governance/{artifact_type}.md``

    Args:
        artifact_type: Governance artifact type (e.g., "roadmap", "adr").

    Returns:
        Path to the governance file.

    Raises:
        typer.Exit: If the file does not exist.
    """
    path = Path(GOVERNANCE_DIR) / f"{artifact_type}.md"
    if not path.exists():
        console.print(f"[red]Error:[/red] File not found: {path}")
        raise typer.Exit(1)
    return path


def _lookup_docs_sync(project_root: Path, local_path: str) -> str | None:
    """Return remote_id from docs_sync for local_path, or None if not tracked."""
    try:
        from raise_cli.storage.connection import get_project_db, get_project_id
        from raise_cli.storage.schema import create_all

        db = get_project_db(project_root)
        create_all(db)
        pid = get_project_id(project_root)
        row = db.execute(
            "SELECT remote_id FROM docs_sync WHERE local_path = ? AND project_id = ?",
            (local_path, pid),
        ).fetchone()
        db.close()
        return row[0] if row and row[0] else None
    except Exception:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
        return None


def _validate_free_form(
    title: str | None, parent: str | None, file: Path | None, stdin: bool
) -> str | None:
    """Validate free-form publish args and return remote_id if file is tracked, else None."""
    tracked = _lookup_docs_sync(Path.cwd(), str(file)) if file is not None else None
    _require_free_form_flags(
        title, parent, file, stdin, has_remote_id=tracked is not None
    )
    return tracked


def _require_free_form_flags(
    title: str | None,
    parent: str | None,
    file: Path | None,
    stdin: bool,
    has_remote_id: bool = False,
) -> None:
    if not title:
        console.print(
            "[red]Error:[/red] --title es requerido cuando no se especifica artifact_type"
        )
        console.print(
            "Ejemplo: rai docs publish --title 'Mi Reporte' --parent 'Reports' --file report.md"
        )
        raise typer.Exit(1)
    if not parent and not has_remote_id:
        console.print(
            "[red]Error:[/red] --parent es requerido cuando no se especifica artifact_type"
        )
        console.print("Usa el ID o título de la página padre en tu docs adapter")
        raise typer.Exit(1)
    if file is None and not stdin:
        console.print(
            "[red]Error:[/red] --file o --stdin requerido en publish libre (sin artifact_type)"
        )
        raise typer.Exit(1)


@docs_app.command()
def publish(
    artifact_type: Annotated[
        str | None,
        typer.Argument(
            help="Artifact type (e.g., roadmap, adr). Omit for free-form publish."
        ),
    ] = None,
    title: Annotated[
        str | None, typer.Option("--title", help="Page title (default: artifact type)")
    ] = None,
    file: Annotated[
        Path | None,
        typer.Option(
            "--file", "-f", help="Read content from file (skips governance/ convention)"
        ),
    ] = None,
    path: Annotated[
        str | None,
        typer.Option(
            "--path",
            "-p",
            help="Local file path for filesystem target (used with --stdin)",
        ),
    ] = None,
    stdin: Annotated[
        bool,
        typer.Option("--stdin", help="Read content from stdin (requires --path)"),
    ] = False,
    parent: Annotated[
        str | None,
        typer.Option("--parent", help="Parent page ID (overrides routing config)"),
    ] = None,
    target: TargetOption = None,
) -> None:
    """Publish an artifact to a documentation target.

    Content sources (in priority order):
    1. --file PATH — read from existing file
    2. --stdin — read from stdin (pipe or heredoc), requires --path
    3. governance/{type}.md — default convention (requires artifact_type)
    """
    tracked_remote_id: str | None = None
    if artifact_type is None:
        tracked_remote_id = _validate_free_form(title, parent, file, stdin)
    if file is not None:
        if not file.exists():
            console.print(f"[red]Error:[/red] File not found: {file}")
            raise typer.Exit(1)
        content = file.read_text(encoding="utf-8")
        effective_path = path or str(file)
    elif stdin:
        content = sys.stdin.read()
        if not content.strip():
            console.print("[red]Error:[/red] No content received from stdin")
            raise typer.Exit(1)
        if not path:
            console.print(
                "[red]Error:[/red] --path is required when reading from stdin"
            )
            raise typer.Exit(1)
        effective_path = path
    else:
        # _require_free_form_flags raises Exit(1) when file/stdin absent and artifact_type
        # is None, so this branch is always reached with a non-None artifact_type.
        resolved = _resolve_artifact_path(cast("str", artifact_type))
        content = resolved.read_text(encoding="utf-8")
        effective_path = path or str(resolved)

    doc_target = resolve_docs_target(target)

    # Invariant: free-form → title is str (guards); routing → artifact_type is str.
    page_title: str = title or artifact_type  # type: ignore[assignment]
    metadata: dict[str, str] = {
        "title": page_title,
        "path": effective_path,
        **{
            k: v
            for k, v in {"parent_id": parent, "remote_id": tracked_remote_id}.items()
            if v is not None
        },
    }

    result = doc_target.publish(
        doc_type=artifact_type,  # None in free-form; adapter uses metadata
        content=content,
        metadata=metadata,
    )
    if result.success:
        console.print(f"Published: {artifact_type} {ARROW} {result.url}")
        if result.message and "sync pending" in result.message:
            console.print(f"[yellow]Warning:[/yellow] {result.message}")
    else:
        console.print(f"[red]Error:[/red] {result.message}")
        raise typer.Exit(1)


@docs_app.command()
def write(
    artifact_type: Annotated[
        str, typer.Argument(help="Artifact type (e.g., session-diary, epic-docs, adr)")
    ],
    title: Annotated[str, typer.Option("--title", help="Page title")],
    file: Annotated[
        Path | None,
        typer.Option("--file", "-f", help="Read content from file (draft source)"),
    ] = None,
    stdin: Annotated[
        bool, typer.Option("--stdin", help="Read content from stdin")
    ] = False,
    output_path: Annotated[
        str | None,
        typer.Option(
            "--output-path",
            help="Explicit local destination path (overrides routing config)",
        ),
    ] = None,
    date: Annotated[
        str | None,
        typer.Option("--date", help="Date override for 'dated' naming (YYYY-MM-DD)"),
    ] = None,
    target: TargetOption = None,
) -> None:
    """Create a governance artifact: write locally and publish to remote target.

    Resolves local destination from routing config (local_dir + naming) or
    --output-path. Dual-write: filesystem + remote target in one call.

    Content sources (in priority order):
    1. --file PATH — read from existing draft file
    2. --stdin — read from stdin (pipe or heredoc)
    """
    if not title.strip():
        console.print("[red]Error:[/red] --title cannot be empty")
        raise typer.Exit(1)

    if file is not None:
        if not file.exists():
            console.print(f"[red]Error:[/red] File not found: {file}")
            raise typer.Exit(1)
        content = file.read_text(encoding="utf-8")
    elif stdin:
        content = sys.stdin.read()
        if not content.strip():
            console.print("[red]Error:[/red] No content received from stdin")
            raise typer.Exit(1)
    else:
        console.print("[red]Error:[/red] Provide --file or --stdin as content source")
        raise typer.Exit(1)

    _routing = _preload_routing(artifact_type, output_path)
    if date is not None and _routing is not None and _routing.naming == "slug":
        console.print(
            f"[yellow]Warning:[/yellow] --date has no effect for '{artifact_type}' (naming=slug)"
        )

    try:
        local_path = _resolve_write_path(
            artifact_type, title, output_path, date, routing=_routing
        )
    except ValueError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(1) from exc

    metadata: dict[str, str] = {"title": title, "path": str(local_path)}

    doc_target = resolve_docs_target(target, require_local=True)

    result = doc_target.publish(
        doc_type=artifact_type, content=content, metadata=metadata
    )
    if result.success:
        if result.message:
            console.print(f"[yellow]Warning:[/yellow] {result.message}")
        console.print(f"Published: {artifact_type} {ARROW} {result.url}")
    else:
        console.print(f"[red]Error:[/red] {result.message}")
        raise typer.Exit(1)


@docs_app.command()
def get(
    identifier: Annotated[str, typer.Argument(help="Page ID on the remote target")],
    target: TargetOption = None,
) -> None:
    """Retrieve a page from the documentation target."""
    doc_target = resolve_docs_target(target)
    try:
        page = doc_target.get_page(identifier)
    except ConfluenceNotFoundError:
        console.print(f"[red]Error:[/red] Page not found: {identifier}")
        raise typer.Exit(1) from None
    except GoogleDriveAuthError as exc:
        console.print(f"[red]Error:[/red] {exc.message}")
        raise typer.Exit(1) from None
    # Compact header + content
    header_parts = [f"# {page.title}"]
    if page.space_key:
        header_parts.append(f"Space: {page.space_key}")
    if page.version > 1:
        header_parts.append(f"Version: {page.version}")
    parent_label = page.parent_title or page.parent_id
    if parent_label:
        header_parts.append(f"Parent: {parent_label}")
    if page.url:
        header_parts.append(page.url)

    console.print(header_parts[0])
    if len(header_parts) > 1:
        console.print(" | ".join(header_parts[1:]))
    console.print()
    console.print(page.content)


@docs_app.command()
def search(
    query: Annotated[str, typer.Argument(help="Search query")],
    limit: Annotated[int, typer.Option("--limit", "-n", help="Max results")] = 10,
    target: TargetOption = None,
) -> None:
    """Search documentation pages on the remote target."""
    doc_target = resolve_docs_target(target)
    results = doc_target.search(query, limit=limit)
    if not results:
        console.print("No results.")
        return
    for page in results:
        console.print(f"{page.id:<8} {page.space_key:<8} {page.title}")


def _render_migration_preview(items: list[MigrationItem], project_root: Path) -> None:
    """Group items by doc_type and print a preview table with relative paths."""
    by_type: dict[str, list[str]] = {}
    for item in items:
        try:
            display_path = str(item.path.relative_to(project_root))
        except ValueError:
            display_path = str(item.path)
        by_type.setdefault(item.doc_type, []).append(display_path)
    for dt in sorted(by_type):
        console.print(f"\n  {dt}  ({len(by_type[dt])} files)")
        for path in sorted(by_type[dt]):
            console.print(f"    {path}")
    console.print(f"\n  Summary: {len(items)} to publish")


@docs_app.command()
def migrate(
    dry_run: Annotated[
        bool, typer.Option("--dry-run", help="Preview only; no publishes")
    ] = False,
    yes: Annotated[
        bool, typer.Option("--yes", help="Skip confirmation prompt")
    ] = False,
    doc_type: Annotated[
        str | None,
        typer.Option("--type", help="Only migrate one doc_type (e.g., sop)"),
    ] = None,
    target: TargetOption = None,
) -> None:
    """Bulk-publish filesystem docs to the remote documentation target.

    Discovers docs via ``manifest.graph.document_sources``. Each file is
    published through the configured target (CompositeDocTarget = filesystem
    + Confluence). Remote failures queue as pending ops automatically (S1700.6).
    Re-runs are idempotent via Confluence title upsert — no docs-ledger.
    """
    from raise_cli.docs.migrate import (
        PublishOutcome,
        execute_migration,
        plan_migration,
    )

    project_root = Path.cwd()

    # Phase 1 — SCAN
    console.print("\n[bold]Phase 1 — SCAN[/bold]")
    items = plan_migration(project_root, doc_type_filter=doc_type)
    console.print(f"  Filesystem: {len(items)} docs discovered")

    if not items:
        console.print("\n  Nothing to migrate.")
        raise typer.Exit(0)

    # Phase 2 — PREVIEW
    console.print("\n[bold]Phase 2 — PREVIEW[/bold]")
    _render_migration_preview(items, project_root)

    if dry_run:
        console.print("\n  [yellow]Dry run — no changes made.[/yellow]")
        raise typer.Exit(0)

    # Phase 3 — CONFIRM
    if not yes and not typer.confirm("\nProceed with migration?", default=False):
        raise typer.Exit(0)

    # Phase 4 — EXECUTE
    console.print("\n[bold]Phase 3 — EXECUTE[/bold]")
    doc_target = resolve_docs_target(target)
    result = execute_migration(items, doc_target)

    for item, outcome, publish_result in result.items:
        marker = {
            PublishOutcome.PUBLISHED: "[green]✓[/green]",
            PublishOutcome.QUEUED: "[yellow]⊘[/yellow]",
            PublishOutcome.FAILED: "[red]✗[/red]",
            PublishOutcome.SKIPPED: "[dim]·[/dim]",
        }[outcome]
        try:
            display_path = str(item.path.relative_to(project_root))
        except ValueError:
            display_path = str(item.path)
        detail = publish_result.url or publish_result.message or ""
        console.print(f"  {marker} {item.doc_type:<10} {display_path} {ARROW} {detail}")

    # Summary
    console.print("\n[bold]Summary[/bold]")
    console.print(f"  Total:             {result.total}")
    console.print(f"  Published:         {result.published}")
    console.print(f"  Queued (pending):  {result.queued}")
    console.print(f"  Failed:            {result.failed}")

    if result.failed > 0:
        raise typer.Exit(1)


@docs_app.command()
def label(
    name: Annotated[str, typer.Argument(help="Label name to add")],
    page: Annotated[str, typer.Option("--page", help="Page ID")],
    target: TargetOption = None,
) -> None:
    """Add a label to a documentation page."""
    doc_target = resolve_docs_target(target)
    doc_target.add_label(page, name)
    console.print(f"Label '{name}' added to page {page}")


@docs_app.command()
def children(
    page_id: Annotated[str, typer.Argument(help="Parent page ID")],
    target: TargetOption = None,
) -> None:
    """List child pages of a documentation page."""
    doc_target = resolve_docs_target(target)
    pages = doc_target.get_page_children(page_id)
    if not pages:
        console.print("No child pages.")
        return
    for p in pages:
        console.print(f"{p.id:<10} {p.title}")


@docs_app.command()
def delete(
    page_id: Annotated[str, typer.Argument(help="Page ID to delete")],
    yes: Annotated[bool, typer.Option("--yes", help="Confirm deletion")] = False,
    target: TargetOption = None,
) -> None:
    """Delete a documentation page."""
    if not yes:
        console.print("[red]Error:[/red] Use --yes to confirm page deletion.")
        raise typer.Exit(1)
    doc_target = resolve_docs_target(target)
    doc_target.delete_page(page_id)
    console.print(f"Page {page_id} deleted.")


@docs_app.command(name="list")
def list_docs(
    name: Annotated[
        str | None,
        typer.Option("--name", help="Filter by keyword in local path"),
    ] = None,
) -> None:
    """List documents tracked in the local sync registry."""
    from raise_cli.adapters.composite_docs import migrate_docs_yaml_to_sqlite
    from raise_cli.storage.connection import get_project_db, get_project_id
    from raise_cli.storage.schema import create_all

    project_root = Path.cwd()
    migrate_docs_yaml_to_sqlite(project_root)
    db = get_project_db(project_root)
    create_all(db)
    pid = get_project_id(project_root)

    query = "SELECT local_path, remote_id, url, updated_at FROM docs_sync WHERE project_id = ?"
    params: list[object] = [pid]
    if name:
        query += " AND local_path LIKE ?"
        params.append(f"%{name}%")
    query += " ORDER BY local_path"

    rows = db.execute(query, params).fetchall()
    db.close()

    if not rows:
        console.print("No documents tracked yet.")
        return

    for local_path, remote_id, url, updated_at in rows:
        console.print(f"{local_path:<50} {remote_id:<14} {url:<60} {updated_at}")


@docs_app.command()
def comment(
    body: Annotated[str, typer.Argument(help="Comment text to add")],
    page: Annotated[str, typer.Option("--page", help="Page ID")],
    target: TargetOption = None,
) -> None:
    """Add a comment to a documentation page."""
    doc_target = resolve_docs_target(target)
    doc_target.add_comment(page, body)
    console.print(f"Comment added to page {page}")


@docs_app.command()
def attach(
    file: Annotated[Path, typer.Argument(help="Local file to attach")],
    page: Annotated[str, typer.Option("--page", help="Page ID")],
    comment: Annotated[
        str | None, typer.Option("--comment", help="Attachment comment")
    ] = None,
    embed: Annotated[
        bool, typer.Option("--embed", help="Append view-file macro to page body")
    ] = False,
    target: TargetOption = None,
) -> None:
    """Attach a local file to a documentation page."""
    if not file.exists():
        console.print(f"[red]Error:[/red] file not found: {file}")
        raise typer.Exit(1)
    doc_target = resolve_docs_target(target)
    url = doc_target.upload_attachment(str(page), str(file), comment)
    console.print(url)
    if embed:
        doc_target.embed_attachment(str(page), file.name)
        console.print(
            f'Embedded: view-file macro for "{file.name}" appended to page {page}'
        )
