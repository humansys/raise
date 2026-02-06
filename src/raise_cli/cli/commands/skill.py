"""CLI commands for skill management.

Provides deterministic operations for listing, validating, and scaffolding
RaiSE skills, following the inference economy principle.
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from raise_cli.output.formatters.skill import (
    format_name_check_human,
    format_name_check_json,
    format_skill_list_human,
    format_skill_list_json,
    format_validation_human,
    format_validation_json,
)
from raise_cli.skills.locator import SkillLocator, get_default_skill_dir
from raise_cli.skills.name_checker import check_name
from raise_cli.skills.validator import ValidationResult, validate_skill, validate_skill_file

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


@skill_app.command("validate")
def validate_command(
    path: Annotated[
        str | None,
        typer.Argument(
            help="Path to skill file or directory. Validates all skills if not specified.",
        ),
    ] = None,
    format: Annotated[
        str,
        typer.Option(
            "--format",
            "-f",
            help="Output format: human or json",
        ),
    ] = "human",
) -> None:
    """Validate skill structure against RaiSE schema.

    Checks frontmatter, required fields, sections, and naming conventions.
    """
    results: list[ValidationResult] = []

    if path:
        # Validate specific file or directory
        target = Path(path)
        if target.is_file():
            results.append(validate_skill_file(target))
        elif target.is_dir():
            # Look for SKILL.md in directory
            skill_file = target / "SKILL.md"
            if skill_file.exists():
                results.append(validate_skill_file(skill_file))
            else:
                results.append(ValidationResult(
                    path=str(target),
                    errors=[f"No SKILL.md found in {target}"],
                ))
        else:
            results.append(ValidationResult(
                path=str(target),
                errors=[f"Path not found: {target}"],
            ))
    else:
        # Validate all skills
        skill_dir = get_default_skill_dir()
        locator = SkillLocator(skill_dir)
        skills = locator.load_all_skills()

        for skill in skills:
            results.append(validate_skill(skill))

    # Output results
    if format == "json":
        print(format_validation_json(results))
    else:
        format_validation_human(results, console)

    # Exit with error code if any validation failed
    if not all(r.is_valid for r in results):
        raise typer.Exit(code=1)


@skill_app.command("check-name")
def check_name_command(
    name: Annotated[
        str,
        typer.Argument(
            help="Proposed skill name to check (e.g., 'feature-validate').",
        ),
    ],
    format: Annotated[
        str,
        typer.Option(
            "--format",
            "-f",
            help="Output format: human or json",
        ),
    ] = "human",
) -> None:
    """Check a proposed skill name against naming conventions.

    Validates that the name follows {domain}-{action} pattern,
    doesn't conflict with existing skills or CLI commands,
    and uses a known lifecycle domain.
    """
    result = check_name(name)

    # Output results
    if format == "json":
        print(format_name_check_json(result))
    else:
        format_name_check_human(result, console)

    # Exit with error code if name is invalid
    if not result.is_valid:
        raise typer.Exit(code=1)
