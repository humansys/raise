"""CLI commands for managing custom artifact types in .raise/docs.yaml.

Provides `rai docs type add`, `rai docs type list`, and `rai docs type remove`
for registering project-level artifact types outside RAISE_ROUTING_PRESET.

RAISE-4856 (E4342)
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Any

import typer
import yaml
from rich.console import Console

from raise_cli.adapters.confluence_config_gen import RAISE_ROUTING_PRESET
from raise_cli.output.symbols import CHECK, CROSS

type_app = typer.Typer(
    name="type",
    help="Manage custom artifact types in .raise/docs.yaml",
    no_args_is_help=True,
)

console = Console()

_KNOWN_GROUPS = sorted(RAISE_ROUTING_PRESET.keys())


def _extract_header(raw: str) -> str:
    """Extract leading comment/blank lines from YAML text."""
    lines: list[str] = []
    for line in raw.splitlines():
        if line.startswith("#") or line.strip() == "":
            lines.append(line)
        else:
            break
    return "\n".join(lines) + "\n" if lines else ""


def _load_docs_yaml(project: Path) -> tuple[str, dict[str, Any]]:
    """Load docs.yaml, return (header, data). Exits on missing/invalid."""
    docs_path = project / ".raise" / "docs.yaml"
    if not docs_path.exists():
        console.print(
            f"[red]{CROSS}[/red] {docs_path} not found — run [bold]rai adapter setup confluence[/bold] first."
        )
        raise typer.Exit(1)
    raw = docs_path.read_text(encoding="utf-8")
    header = _extract_header(raw)
    try:
        data: dict[str, Any] = yaml.safe_load(raw) or {}
    except yaml.YAMLError as exc:
        console.print(f"[red]{CROSS}[/red] Cannot parse {docs_path}: {exc}")
        raise typer.Exit(1) from None
    return header, data


def _write_docs_yaml(project: Path, header: str, data: dict[str, Any]) -> None:
    """Atomic write of docs.yaml preserving header comments."""
    docs_path = project / ".raise" / "docs.yaml"
    with open(docs_path, "w", encoding="utf-8") as f:
        f.write(header)
        yaml.dump(
            data, f, default_flow_style=False, sort_keys=False, allow_unicode=True
        )


@type_app.command("add")
def type_add(
    name: Annotated[str, typer.Argument(help="Artifact type name (e.g. transcript)")],
    group: Annotated[
        str, typer.Option("--group", "-g", help="Semantic group / parent page name")
    ],
    labels: Annotated[
        str | None,
        typer.Option("--labels", help="Comma-separated labels (default: [name])"),
    ] = None,
    local_dir: Annotated[
        str | None,
        typer.Option(
            "--local-dir",
            help="Local directory for rai docs write (e.g. work/sessions)",
        ),
    ] = None,
    force: Annotated[
        bool,
        typer.Option("--force", help="Overwrite if type already exists"),
    ] = False,
    project: Annotated[
        Path,
        typer.Option("--project", help="Project root (default: current directory)"),
    ] = Path("."),
) -> None:
    """Register a custom artifact type in .raise/docs.yaml.

    Examples:
        $ rai docs type add transcript --group Sessions
        $ rai docs type add interview --group Interviews --labels interview,recording
    """
    if not group.strip():
        console.print(f"[red]{CROSS}[/red] --group cannot be empty.")
        raise typer.Exit(1)

    header, data = _load_docs_yaml(project)

    custom_types: dict[str, Any] = data.setdefault("custom_types", {}) or {}
    data["custom_types"] = custom_types

    if name in custom_types and not force:
        console.print(
            f"[red]{CROSS}[/red] Type [bold]{name}[/bold] already registered "
            f"(group: {custom_types[name].get('group', '?')}). Use --force to overwrite."
        )
        raise typer.Exit(1)

    label_list = (
        [lbl.strip() for lbl in labels.split(",") if lbl.strip()] if labels else []
    )

    entry: dict[str, Any] = {"group": group}
    if label_list:
        entry["labels"] = label_list
    if local_dir:
        entry["local_dir"] = local_dir

    custom_types[name] = entry
    _write_docs_yaml(project, header, data)

    console.print(
        f"[green]{CHECK}[/green] [bold]{name}[/bold] registered (group: {group})"
    )

    if group not in _KNOWN_GROUPS:
        known = ", ".join(_KNOWN_GROUPS)
        console.print(f"  [dim]Hint: known groups are {known}[/dim]")


@type_app.command("list")
def type_list(
    project: Annotated[
        Path,
        typer.Option("--project", help="Project root (default: current directory)"),
    ] = Path("."),
) -> None:
    """List all registered custom artifact types."""
    _, data = _load_docs_yaml(project)

    custom_types: dict[str, Any] = data.get("custom_types") or {}

    if not custom_types:
        console.print("No custom artifact types registered.")
        return

    count = len(custom_types)
    console.print(f"Custom artifact types ({count}):")
    for type_name, entry in custom_types.items():
        grp = entry.get("group", "—")
        lbls = entry.get("labels", [])
        ldir = entry.get("local_dir")
        labels_str = f"  labels={lbls}" if lbls else ""
        dir_str = f"  local_dir={ldir}" if ldir else ""
        console.print(f"  [bold]{type_name}[/bold]   group={grp}{labels_str}{dir_str}")


@type_app.command("remove")
def type_remove(
    name: Annotated[str, typer.Argument(help="Artifact type name to remove")],
    project: Annotated[
        Path,
        typer.Option("--project", help="Project root (default: current directory)"),
    ] = Path("."),
) -> None:
    """Remove a custom artifact type from .raise/docs.yaml."""
    header, data = _load_docs_yaml(project)

    custom_types: dict[str, Any] = data.get("custom_types") or {}

    if name not in custom_types:
        console.print(
            f"[red]{CROSS}[/red] Type [bold]{name}[/bold] not found in custom_types."
        )
        raise typer.Exit(1)

    del custom_types[name]
    if not custom_types:
        data.pop("custom_types", None)

    _write_docs_yaml(project, header, data)
    console.print(f"[green]{CHECK}[/green] [bold]{name}[/bold] removed")
