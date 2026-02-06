"""Output formatters for skill commands."""

from __future__ import annotations

import json
from typing import Any

from rich.console import Console
from rich.table import Table

from raise_cli.skills.schema import Skill


def format_skill_list_human(
    skills: list[Skill],
    grouped: dict[str, list[Skill]],
    console: Console,
) -> None:
    """Format skill list for human output.

    Args:
        skills: All skills (for count).
        grouped: Skills grouped by lifecycle.
        console: Rich console for output.
    """
    if not skills:
        console.print("No skills found in .claude/skills/")
        return

    console.print(f"[bold]Skills[/bold] ({len(skills)} found)\n")

    # Define lifecycle order for consistent output
    lifecycle_order = ["session", "epic", "feature", "discovery", "utility", "meta", "unknown"]

    for lifecycle in lifecycle_order:
        if lifecycle not in grouped:
            continue

        lifecycle_skills = grouped[lifecycle]
        console.print(f"[bold cyan]{lifecycle.capitalize()}[/bold cyan]")

        table = Table(show_header=False, box=None, padding=(0, 2, 0, 0))
        table.add_column("Name", style="green")
        table.add_column("Version", style="dim")
        table.add_column("Description")

        for skill in sorted(lifecycle_skills, key=lambda s: s.name):
            # Truncate description if too long
            desc = skill.description
            if len(desc) > 50:
                desc = desc[:47] + "..."
            table.add_row(
                skill.name,
                skill.version or "-",
                desc,
            )

        console.print(table)
        console.print()


def format_skill_list_json(
    skills: list[Skill],
    skill_dir: str,
) -> str:
    """Format skill list as JSON.

    Args:
        skills: List of skills to format.
        skill_dir: Path to skill directory.

    Returns:
        JSON string.
    """
    skill_data: list[dict[str, Any]] = []
    for skill in sorted(skills, key=lambda s: s.name):
        skill_data.append({
            "name": skill.name,
            "version": skill.version,
            "lifecycle": skill.lifecycle,
            "description": skill.description,
            "path": skill.path,
        })

    output = {
        "skills": skill_data,
        "skill_dir": skill_dir,
        "count": len(skills),
    }

    return json.dumps(output, indent=2)
