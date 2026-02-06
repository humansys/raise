"""CLI commands for base Rai package information.

This module provides the `raise base` command group for viewing
information about the bundled base Rai package.

Example:
    $ raise base show          # View base package info and install status
"""

from __future__ import annotations

from importlib.resources import files
from pathlib import Path

import typer

from raise_cli.config.paths import get_identity_dir
from raise_cli.rai_base import __version__ as base_version

base_app = typer.Typer(
    name="base",
    help="View base Rai package info",
    no_args_is_help=True,
)


def _get_project_root() -> Path:
    """Get the project root directory.

    Returns:
        Current working directory as project root.
    """
    return Path.cwd()


def _count_base_patterns() -> int:
    """Count patterns in the bundled base package.

    Returns:
        Number of base patterns in patterns-base.jsonl.
    """
    base = files("raise_cli.rai_base")
    source = base / "memory" / "patterns-base.jsonl"
    content = source.read_text()  # type: ignore[union-attr]
    return sum(1 for line in content.splitlines() if line.strip())


def _check_installed(project_root: Path) -> bool:
    """Check if base Rai has been bootstrapped to this project.

    Args:
        project_root: Project root directory.

    Returns:
        True if .raise/rai/identity/ exists with files.
    """
    identity_dir = get_identity_dir(project_root)
    return identity_dir.exists() and any(identity_dir.iterdir())


@base_app.command()
def show() -> None:
    """Display base Rai package information.

    Shows the bundled base version, contents (identity, patterns,
    methodology), and whether it has been installed in the current project.

    Examples:
        $ raise base show
    """
    project_root = _get_project_root()
    pattern_count = _count_base_patterns()
    installed = _check_installed(project_root)

    # Check for methodology
    base = files("raise_cli.rai_base")
    has_methodology = (base / "framework" / "methodology.yaml").is_file()

    # Check identity files
    identity_base = base / "identity"
    identity_files: list[str] = []
    try:
        for item in identity_base.iterdir():  # type: ignore[union-attr]
            name = getattr(item, "name", str(item))
            if name.endswith(".md"):
                identity_files.append(name)
    except (AttributeError, TypeError):
        pass

    typer.echo(f"Base Rai v{base_version}")
    typer.echo()
    typer.echo("Contents:")
    typer.echo(f"  Identity:     {', '.join(sorted(identity_files)) or 'none'}")
    typer.echo(f"  Patterns:     {pattern_count} base patterns")
    typer.echo(f"  Methodology:  {'yes' if has_methodology else 'no'}")
    typer.echo()

    if installed:
        typer.echo(f"Status: Installed in {project_root}")
    else:
        typer.echo("Status: Not installed (run `raise init` to bootstrap)")
