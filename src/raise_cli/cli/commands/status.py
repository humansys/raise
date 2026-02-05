"""CLI command for project status.

This module provides the `raise status` command for viewing
project health and initialization state at a glance.

Example:
    $ raise status  # Show project status
"""

from __future__ import annotations

from pathlib import Path

import typer
import yaml

from raise_cli.onboarding.profile import ExperienceLevel, load_developer_profile

status_app = typer.Typer(
    name="status",
    help="Show project status and health",
)


def _get_project_info(project_path: Path) -> dict[str, str | bool | None]:
    """Get project initialization info.

    Args:
        project_path: Path to the project root.

    Returns:
        Dict with project info (name, type, initialized).
    """
    raise_dir = project_path / ".raise"
    manifest_path = raise_dir / "manifest.yaml"

    if not raise_dir.exists():
        return {"initialized": False, "name": None, "type": None}

    if manifest_path.exists():
        try:
            data = yaml.safe_load(manifest_path.read_text())
            return {
                "initialized": True,
                "name": data.get("name", project_path.name),
                "type": data.get("type", "unknown"),
            }
        except yaml.YAMLError:
            pass

    return {"initialized": True, "name": project_path.name, "type": "unknown"}


@status_app.callback(invoke_without_command=True)
def status(
    ctx: typer.Context,
) -> None:
    """Show project status and health.

    Displays:
    - Project initialization state
    - Developer profile info
    - Governance file status

    Examples:
        $ raise status
    """
    if ctx.invoked_subcommand is not None:
        return

    project_path = Path.cwd()
    project_info = _get_project_info(project_path)

    typer.echo("RaiSE Project Status")
    typer.echo("─" * 20)

    # Project info
    if project_info["initialized"]:
        typer.echo(f"Project: {project_info['name']} ({project_info['type']})")
    else:
        typer.echo(f"Project: {project_path.name} (not initialized)")
        typer.echo("  Run `raise init` to initialize")

    # Developer profile
    profile = load_developer_profile()
    if profile:
        level_display = {
            ExperienceLevel.SHU: "shu - learning",
            ExperienceLevel.HA: "ha - practicing",
            ExperienceLevel.RI: "ri - mastering",
        }
        typer.echo(
            f"Developer: {profile.name} "
            f"({level_display.get(profile.experience_level, profile.experience_level)}, "
            f"{profile.sessions_total} sessions)"
        )
    else:
        typer.echo("Developer: No profile configured")
        typer.echo("  Run `raise profile session --name 'Your Name'` to create")

    # Governance files
    typer.echo("")
    typer.echo("Governance:")
    governance_dir = project_path / "governance" / "solution"

    guardrails = governance_dir / "guardrails.md"
    if guardrails.exists():
        typer.echo("  ✓ guardrails.md")
    else:
        typer.echo("  ✗ guardrails.md (run `raise init`)")

    claude_md = project_path / "CLAUDE.md"
    if claude_md.exists():
        typer.echo("  ✓ CLAUDE.md")
    else:
        typer.echo("  ✗ CLAUDE.md (run `raise init`)")

    # Graph status
    graph_path = project_path / ".raise" / "graph" / "unified.json"
    if graph_path.exists():
        from datetime import datetime

        mtime = datetime.fromtimestamp(graph_path.stat().st_mtime)
        typer.echo("")
        typer.echo(f"Graph: Built ({mtime.strftime('%Y-%m-%d %H:%M')})")
    elif project_info["initialized"]:
        typer.echo("")
        typer.echo("Graph: Not built (run `raise graph build --unified`)")
