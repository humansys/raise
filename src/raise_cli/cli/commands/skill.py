"""CLI commands for skill management.

Provides deterministic operations for listing, validating, and scaffolding
RaiSE skills, following the inference economy principle.
"""

from __future__ import annotations

from typing import Annotated

import typer
from rich.console import Console

from raise_cli.output.formatters.skill import (
    format_skill_list_human,
    format_skill_list_json,
)
from raise_cli.skills.locator import SkillLocator, get_default_skill_dir

skill_app = typer.Typer(
    name="skill",
    help="Manage RaiSE skills",
    no_args_is_help=True,
)

console = Console()


@skill_app.command("list")
def list_command(
    format: Annotated[
        str,
        typer.Option(
            "--format",
            "-f",
            help="Output format: human or json",
        ),
    ] = "human",
) -> None:
    """List all skills in the skill directory.

    Shows skills grouped by lifecycle with version and description.
    """
    skill_dir = get_default_skill_dir()
    locator = SkillLocator(skill_dir)
    skills = locator.load_all_skills()
    grouped = locator.group_by_lifecycle(skills)

    if format == "json":
        output = format_skill_list_json(skills, str(skill_dir))
        print(output)  # Plain print for valid JSON
    else:
        format_skill_list_human(skills, grouped, console)
