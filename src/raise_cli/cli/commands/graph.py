"""CLI commands for concept graph operations."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.table import Table

from raise_cli.governance import ConceptType, GovernanceExtractor

graph_app = typer.Typer(
    name="graph",
    help="Concept graph operations (extract, build, query)",
    no_args_is_help=True,
)

console = Console()


@graph_app.command()
def extract(
    file_path: Annotated[
        Optional[Path],
        typer.Argument(help="Path to governance file (optional, extracts all if not provided)"),
    ] = None,
    format: Annotated[
        str,
        typer.Option("--format", "-f", help="Output format (human or json)"),
    ] = "human",
) -> None:
    """Extract concepts from governance markdown files.

    If no file path is provided, extracts from all standard governance locations:
    - governance/projects/*/prd.md (requirements)
    - governance/solution/vision.md (outcomes)
    - framework/reference/constitution.md (principles)

    Examples:
        # Extract from all governance files
        $ raise graph extract

        # Extract from specific file
        $ raise graph extract governance/projects/raise-cli/prd.md

        # Output as JSON
        $ raise graph extract --format json
    """
    extractor = GovernanceExtractor()

    if file_path:
        # Extract from single file
        if not file_path.exists():
            console.print(f"[red]Error:[/red] File not found: {file_path}")
            raise typer.Exit(1)

        concepts = extractor.extract_from_file(file_path)

        if format == "json":
            # JSON output
            output = {
                "concepts": [
                    {
                        "id": c.id,
                        "type": c.type.value,
                        "file": c.file,
                        "section": c.section,
                        "lines": list(c.lines),
                        "content": c.content,
                        "metadata": c.metadata,
                    }
                    for c in concepts
                ],
                "total": len(concepts),
            }
            console.print(json.dumps(output, indent=2))
        else:
            # Human-readable output
            console.print(f"\nExtracting concepts from [cyan]{file_path.name}[/cyan]...")

            for concept in concepts:
                console.print(f"  ✓ Found {concept.metadata.get('requirement_id') or concept.metadata.get('principle_number') or concept.section}")

            console.print(f"→ Extracted [green]{len(concepts)}[/green] concepts\n")

    else:
        # Extract from all governance files
        result = extractor.extract_with_result()

        if format == "json":
            # JSON output
            output = {
                "concepts": [
                    {
                        "id": c.id,
                        "type": c.type.value,
                        "file": c.file,
                        "section": c.section,
                        "lines": list(c.lines),
                        "content": c.content,
                        "metadata": c.metadata,
                    }
                    for c in result.concepts
                ],
                "total": result.total,
                "files_processed": result.files_processed,
                "errors": result.errors,
            }
            console.print(json.dumps(output, indent=2))
        else:
            # Human-readable output
            console.print("\nExtracting concepts from governance files...")

            # Group concepts by type
            by_type: dict[ConceptType, list] = {}
            for concept in result.concepts:
                by_type.setdefault(concept.type, []).append(concept)

            # Display by file type
            if ConceptType.REQUIREMENT in by_type:
                reqs = by_type[ConceptType.REQUIREMENT]
                console.print(f"  📄 prd.md → [green]{len(reqs)}[/green] requirements")

            if ConceptType.OUTCOME in by_type:
                outcomes = by_type[ConceptType.OUTCOME]
                console.print(
                    f"  📄 vision.md → [green]{len(outcomes)}[/green] outcomes"
                )

            if ConceptType.PRINCIPLE in by_type:
                principles = by_type[ConceptType.PRINCIPLE]
                console.print(
                    f"  📄 constitution.md → [green]{len(principles)}[/green] principles"
                )

            console.print(f"→ Total: [green]{result.total}[/green] concepts extracted\n")

            if result.errors:
                console.print("[yellow]Warnings:[/yellow]")
                for error in result.errors:
                    console.print(f"  ⚠  {error}")
