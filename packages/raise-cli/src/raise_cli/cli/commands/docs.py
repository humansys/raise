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

import sys
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from raise_cli.cli.commands._resolve import resolve_docs_target

docs_app = typer.Typer(
    name="docs",
    help="Manage governance documentation via DocumentationTarget",
    no_args_is_help=True,
)

console = Console()

# Common option for target override (D5)
TargetOption = Annotated[
    str | None,
    typer.Option(
        "--target", "-t", help="Target name override (auto-detect if omitted)"
    ),
]

# Convention: governance artifacts live at governance/{type}.md
GOVERNANCE_DIR = "governance"


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


@docs_app.command()
def publish(
    artifact_type: Annotated[
        str, typer.Argument(help="Artifact type (e.g., roadmap, adr, story-design)")
    ],
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
    3. governance/{type}.md — default convention
    """
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
        resolved = _resolve_artifact_path(artifact_type)
        content = resolved.read_text(encoding="utf-8")
        effective_path = path or str(resolved)

    doc_target = resolve_docs_target(target)

    page_title = title or artifact_type
    metadata: dict[str, str] = {"title": page_title, "path": effective_path}
    if parent is not None:
        metadata["parent_id"] = parent

    result = doc_target.publish(
        doc_type=artifact_type, content=content, metadata=metadata
    )
    if result.success:
        console.print(f"Published: {artifact_type} → {result.url}")
        if result.message and "sync pending" in result.message:
            console.print(f"[yellow]Warning:[/yellow] {result.message}")
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
    page = doc_target.get_page(identifier)
    # Compact header + content
    header_parts = [f"# {page.title}"]
    if page.space_key:
        header_parts.append(f"Space: {page.space_key}")
    if page.version > 1:
        header_parts.append(f"Version: {page.version}")
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
