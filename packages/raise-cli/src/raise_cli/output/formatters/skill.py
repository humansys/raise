"""Output formatters for skill commands."""

from __future__ import annotations

import json
from typing import Any

from rich.console import Console
from rich.table import Table

from raise_cli.output.symbols import CHECK, CROSS, WARN
from raise_cli.skills.name_checker import NameCheckResult
from raise_cli.skills.scaffold import ScaffoldResult
from raise_cli.skills.schema import Skill
from raise_cli.skills.validator import ValidationResult


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
    lifecycle_order = [
        "session",
        "epic",
        "story",
        "discovery",
        "utility",
        "meta",
        "unknown",
    ]

    # Show all lifecycles: ordered first, then any unknown ones alphabetically
    ordered_set = set(lifecycle_order)
    extra_lifecycles = sorted(lc for lc in grouped if lc not in ordered_set)
    display_order = lifecycle_order + extra_lifecycles

    for lifecycle in display_order:
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
        skill_data.append(
            {
                "name": skill.name,
                "version": skill.version,
                "lifecycle": skill.lifecycle,
                "description": skill.description,
                "path": skill.path,
            }
        )

    output = {
        "skills": skill_data,
        "skill_dir": skill_dir,
        "count": len(skills),
    }

    return json.dumps(output, indent=2)


def format_validation_human(
    results: list[ValidationResult],
    console: Console,
) -> None:
    """Format validation results for human output.

    Args:
        results: List of validation results.
        console: Rich console for output.
    """
    total_errors = sum(r.error_count for r in results)
    total_warnings = sum(r.warning_count for r in results)

    for result in results:
        console.print(f"\n[bold]Validating:[/bold] {result.path}")

        if result.is_valid and result.warning_count == 0:
            console.print("[green]{CHECK} All checks passed[/green]")
            continue

        # Show errors
        for error in result.errors:
            console.print(f"[red]{CROSS} {error}[/red]")

        # Show warnings
        for warning in result.warnings:
            console.print(f"[yellow]{WARN} {warning}[/yellow]")

    # Summary
    console.print()
    if total_errors == 0 and total_warnings == 0:
        console.print(f"[green]All {len(results)} skill(s) valid[/green]")
    else:
        parts: list[str] = []
        if total_errors > 0:
            parts.append(f"[red]{total_errors} error(s)[/red]")
        if total_warnings > 0:
            parts.append(f"[yellow]{total_warnings} warning(s)[/yellow]")
        console.print(f"{len(results)} skill(s) checked: {', '.join(parts)}")


def format_validation_json(results: list[ValidationResult]) -> str:
    """Format validation results as JSON.

    Args:
        results: List of validation results.

    Returns:
        JSON string.
    """
    output: list[dict[str, Any]] = []
    for result in results:
        output.append(
            {
                "path": result.path,
                "valid": result.is_valid,
                "errors": result.errors,
                "warnings": result.warnings,
            }
        )

    return json.dumps(
        {
            "results": output,
            "total_errors": sum(r.error_count for r in results),
            "total_warnings": sum(r.warning_count for r in results),
            "all_valid": all(r.is_valid for r in results),
        },
        indent=2,
    )


def format_name_check_human(result: NameCheckResult, console: Console) -> None:
    """Format name check result for human output.

    Args:
        result: Name check result.
        console: Rich console for output.
    """
    console.print(f"\n[bold]Checking name:[/bold] {result.name}\n")

    # Pattern check
    if result.valid_pattern:
        console.print("[green]{CHECK} Follows {domain}-{action} pattern[/green]")
    else:
        console.print("[red]{CROSS} Does not follow {domain}-{action} pattern[/red]")

    # Skill conflict
    if result.no_skill_conflict:
        console.print("[green]{CHECK} No conflict with existing skills[/green]")
    else:
        console.print(
            f"[red]{CROSS} Conflicts with existing skill: {result.conflicting_skill}[/red]"
        )

    # CLI conflict
    if result.no_cli_conflict:
        console.print("[green]{CHECK} No CLI command conflict[/green]")
    else:
        console.print(
            f"[red]{CROSS} Conflicts with CLI command: {result.conflicting_command}[/red]"
        )

    # Lifecycle check
    if result.known_lifecycle:
        console.print("[green]{CHECK} Domain is a known lifecycle[/green]")
    else:
        console.print("[yellow]{WARN} Domain is not a standard lifecycle[/yellow]")

    # Final verdict
    console.print()
    if result.is_valid:
        console.print(f"[bold green]Name '{result.name}' is valid.[/bold green]")
    else:
        console.print(f"[bold red]Name '{result.name}' is not valid.[/bold red]")

    # Suggestions
    if result.suggestions:
        console.print()
        for suggestion in result.suggestions:
            console.print(f"[dim]→ {suggestion}[/dim]")


def format_name_check_json(result: NameCheckResult) -> str:
    """Format name check result as JSON.

    Args:
        result: Name check result.

    Returns:
        JSON string.
    """
    return json.dumps(
        {
            "name": result.name,
            "valid": result.is_valid,
            "checks": {
                "valid_pattern": result.valid_pattern,
                "no_skill_conflict": result.no_skill_conflict,
                "no_cli_conflict": result.no_cli_conflict,
                "known_lifecycle": result.known_lifecycle,
            },
            "conflicts": {
                "skill": result.conflicting_skill,
                "command": result.conflicting_command,
            },
            "suggestions": result.suggestions,
        },
        indent=2,
    )


def format_scaffold_human(result: ScaffoldResult, console: Console) -> None:
    """Format scaffold result for human output.

    Args:
        result: Scaffold result.
        console: Rich console for output.
    """
    if result.created:
        console.print(f"\n[green]{CHECK} Created skill at:[/green] {result.path}")
        console.print("\n[dim]Next steps:[/dim]")
        console.print("  1. Edit the SKILL.md to add description and steps")
        console.print("  2. Run [cyan]rai skill validate[/cyan] to check structure")
        console.print("  3. Test the skill with Claude Code")
    else:
        console.print("\n[red]{CROSS} Failed to create skill[/red]")
        console.print(f"[red]  {result.error}[/red]")


def format_scaffold_json(result: ScaffoldResult) -> str:
    """Format scaffold result as JSON.

    Args:
        result: Scaffold result.

    Returns:
        JSON string.
    """
    return json.dumps(
        {
            "created": result.created,
            "path": result.path,
            "error": result.error,
        },
        indent=2,
    )
