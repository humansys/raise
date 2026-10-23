"""CLI command for base Rai package information.

Provides the top-level `rai info` command for viewing information about
the bundled base Rai package.

Moved from `base show` during CLI restructuring.

Example:
    $ rai info          # View base package info and install status
"""

from __future__ import annotations

from importlib.resources import files
from pathlib import Path

import typer

from raise_cli.config.paths import get_identity_dir
from raise_cli.rai_base import __version__ as base_version


def _get_project_root() -> Path:
    """Get the project root directory."""
    return Path.cwd()


def _count_base_patterns() -> int:
    """Count patterns in the bundled base package."""
    base = files("raise_cli.rai_base")
    source = base / "memory" / "patterns-base.jsonl"
    content = source.read_text(encoding="utf-8")  # type: ignore[union-attr]
    return sum(1 for line in content.splitlines() if line.strip())


def _check_installed(project_root: Path) -> bool:
    """Check if base Rai has been bootstrapped to this project."""
    identity_dir = get_identity_dir(project_root)
    return identity_dir.exists() and any(identity_dir.iterdir())


def info_command() -> None:
    """Display base Rai package information.

    Shows the bundled base version, contents (identity, patterns,
    methodology), and whether it has been installed in the current project.

    Examples:
        $ rai info
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
        typer.echo("Status: Not installed (run `rai init` to bootstrap)")
