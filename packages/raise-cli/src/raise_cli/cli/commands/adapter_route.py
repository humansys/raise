"""CLI commands for surgical routing updates to .raise/docs.yaml.

Provides `rai adapter route patch` for atomically updating parent_path or
parent_title on one artifact type or an entire named group.

RAISE-4855 (E4342)
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Any

import typer
import yaml
from rich.console import Console

from raise_cli.adapters.confluence_config_gen import RAISE_ROUTING_PRESET
from raise_cli.output.symbols import CHECK, CROSS

route_app = typer.Typer(
    name="route",
    help="Routing operations on .raise/docs.yaml",
    no_args_is_help=True,
)

console = Console()


def _apply_routing_patch(
    routing: dict[str, Any],
    types_to_patch: list[str],
    path_list: list[str] | None,
    parent_title: str | None,
) -> None:
    """Write parent_path or parent_title into each type's routing entry."""
    for t in types_to_patch:
        entry = routing.setdefault(t, {})
        if path_list is not None:
            entry["parent_path"] = path_list
            entry.pop("parent_title", None)
        else:
            entry["parent_title"] = parent_title
            entry.pop("parent_path", None)


def _extract_header(raw: str) -> str:
    """Extract leading comment/blank lines from YAML text."""
    lines: list[str] = []
    for line in raw.splitlines():
        if line.startswith("#") or line.strip() == "":
            lines.append(line)
        else:
            break
    return "\n".join(lines) + "\n" if lines else ""


@route_app.command("patch")
def route_patch(
    target: Annotated[
        str | None,
        typer.Option(
            "--target",
            "-t",
            help="Target name (default: default_target from docs.yaml)",
        ),
    ] = None,
    artifact_type: Annotated[
        str | None,
        typer.Option("--type", help="Artifact type to patch (e.g. adr, story)"),
    ] = None,
    group: Annotated[
        str | None,
        typer.Option(
            "--group", help="Group to patch (e.g. Epics, Stories, Architecture)"
        ),
    ] = None,
    parent_path: Annotated[
        str | None,
        typer.Option(
            "--parent-path", help='Slash-separated path, e.g. "Architecture/ADRs"'
        ),
    ] = None,
    parent_title: Annotated[
        str | None,
        typer.Option("--parent-title", help="Parent page title"),
    ] = None,
    project: Annotated[
        Path,
        typer.Option("--project", help="Project root (default: current directory)"),
    ] = Path("."),
) -> None:
    """Patch routing entries in .raise/docs.yaml.

    Sets or replaces parent_path / parent_title for one artifact type or a
    named group. Setting one field clears the other. Atomic read-modify-write
    that preserves header comments.

    Examples:
        $ rai adapter route patch --type adr --parent-path "Architecture/ADRs"
        $ rai adapter route patch --target humansys --type story --parent-title "Stories"
        $ rai adapter route patch --group Epics --parent-path "Engineering/Projects/Epics"
    """
    # Validate mutual exclusions
    if bool(artifact_type) == bool(group):
        console.print(f"[red]{CROSS}[/red] Specify exactly one of --type or --group.")
        raise typer.Exit(1)

    if bool(parent_path) == bool(parent_title):
        console.print(
            f"[red]{CROSS}[/red] Specify exactly one of --parent-path or --parent-title."
        )
        raise typer.Exit(1)

    # Load docs.yaml
    docs_path = project / ".raise" / "docs.yaml"
    if not docs_path.exists():
        console.print(
            f"[red]{CROSS}[/red] {docs_path} not found — run [bold]rai adapter setup confluence[/bold] first."
        )
        raise typer.Exit(1)

    raw = docs_path.read_text(encoding="utf-8")
    header = _extract_header(raw)
    try:
        data = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        console.print(f"[red]{CROSS}[/red] Cannot parse {docs_path}: {exc}")
        raise typer.Exit(1) from None

    # Resolve effective target
    effective_target = target or data.get("default_target")
    if effective_target not in data.get("targets", {}):
        available = ", ".join(data.get("targets", {}).keys())
        console.print(
            f"[red]{CROSS}[/red] Target [bold]{effective_target}[/bold] not found (available: {available})."
        )
        raise typer.Exit(1)

    # Resolve artifact types
    if artifact_type:
        types_to_patch = [artifact_type]
    else:
        if group not in RAISE_ROUTING_PRESET:
            available_groups = ", ".join(sorted(RAISE_ROUTING_PRESET))
            console.print(
                f"[red]{CROSS}[/red] Group [bold]{group}[/bold] not found "
                f"(available: {available_groups})."
            )
            raise typer.Exit(1)
        types_to_patch = RAISE_ROUTING_PRESET[group]

    # Apply patch
    routing = data["targets"][effective_target].setdefault("routing", {})
    path_list: list[str] | None = None

    if parent_path:
        path_list = [seg.strip() for seg in parent_path.split("/") if seg.strip()]
        if not path_list:
            console.print(
                f"[red]{CROSS}[/red] --parent-path cannot be empty after parsing."
            )
            raise typer.Exit(1)

    _apply_routing_patch(routing, types_to_patch, path_list, parent_title)

    # Write back preserving header
    with open(docs_path, "w", encoding="utf-8") as f:
        f.write(header)
        yaml.dump(
            data, f, default_flow_style=False, sort_keys=False, allow_unicode=True
        )

    count = len(types_to_patch)
    noun = "entry" if count == 1 else "entries"
    detail = (
        f"parent_path={path_list}" if parent_path else f"parent_title={parent_title!r}"
    )
    console.print(
        f"{CHECK} {count} routing {noun} patched in [bold]{effective_target}[/bold] ({detail})"
    )
