"""CLI commands for skill management.

Provides deterministic operations for listing, validating, and scaffolding
RaiSE skills, following the inference economy principle.
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from raise_cli.cli.commands.skill_set import skill_set_app
from raise_cli.onboarding.skills import SkillScaffoldResult, scaffold_skills
from raise_cli.output.formatters.skill import (
    format_name_check_human,
    format_name_check_json,
    format_scaffold_human,
    format_scaffold_json,
    format_skill_list_human,
    format_skill_list_json,
    format_validation_human,
    format_validation_json,
)
from raise_cli.skills.locator import SkillLocator, get_default_skill_dir
from raise_cli.skills.name_checker import check_name
from raise_cli.skills.scaffold import scaffold_skill
from raise_cli.skills.validator import (
    ValidationResult,
    validate_skill,
    validate_skill_file,
)

skill_app = typer.Typer(
    name="skill",
    help="Manage RaiSE skills",
    no_args_is_help=True,
)
skill_app.add_typer(skill_set_app, name="set")

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
                results.append(
                    ValidationResult(
                        path=str(target),
                        errors=[f"No SKILL.md found in {target}"],
                    )
                )
        else:
            results.append(
                ValidationResult(
                    path=str(target),
                    errors=[f"Path not found: {target}"],
                )
            )
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
            help="Proposed skill name to check (e.g., 'story-validate').",
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


@skill_app.command("scaffold")
def scaffold_command(
    name: Annotated[
        str,
        typer.Argument(
            help="Skill name to create (e.g., 'story-validate').",
        ),
    ],
    lifecycle: Annotated[
        str | None,
        typer.Option(
            "--lifecycle",
            "-l",
            help="Lifecycle: session, epic, story, discovery, utility, meta. Inferred from name if not specified.",
        ),
    ] = None,
    after: Annotated[
        str | None,
        typer.Option(
            "--after",
            help="Skill that should come before this one (prerequisites).",
        ),
    ] = None,
    before: Annotated[
        str | None,
        typer.Option(
            "--before",
            help="Skill that should come after this one (next).",
        ),
    ] = None,
    skill_set: Annotated[
        str | None,
        typer.Option(
            "--set",
            help="Skill set to create in (e.g., 'my-team'). Creates in .raise/skills/{set}/.",
        ),
    ] = None,
    from_builtin: Annotated[
        bool,
        typer.Option(
            "--from-builtin",
            help="Copy from deployed builtin skill as starting point. Requires --set.",
        ),
    ] = False,
    format: Annotated[
        str,
        typer.Option(
            "--format",
            "-f",
            help="Output format: human or json",
        ),
    ] = "human",
) -> None:
    """Create a new skill from template.

    Generates a SKILL.md file with proper structure.
    Without --set: creates in .claude/skills/<name>/.
    With --set: creates in .raise/skills/<set>/<name>/.
    """
    result = scaffold_skill(
        name,
        lifecycle=lifecycle,
        after=after,
        before=before,
        skill_set=skill_set,
        from_builtin=from_builtin,
    )

    # Output results
    if format == "json":
        print(format_scaffold_json(result))
    else:
        format_scaffold_human(result, console)

    # Exit with error code if creation failed
    if not result.created:
        raise typer.Exit(code=1)


def _print_sync_table(result: SkillScaffoldResult) -> None:
    """Print a summary table of skill sync status."""
    from rich.table import Table

    try:
        from raise_cli.skills_base import __version__ as cli_version
    except ImportError:
        cli_version = "unknown"

    console.print(f"\n[bold]Skill sync check: raise-cli {cli_version}[/bold]\n")

    rows: list[tuple[str, str]] = []
    for name in result.skills_installed:
        rows.append((name, "[green]new — not deployed[/green]"))
    for name in result.skills_updated:
        rows.append((name, "[yellow]outdated — update available[/yellow]"))
    for name in result.skills_conflicted:
        rows.append((name, "[yellow]conflict — both changed[/yellow]"))
    for name in result.skills_current:
        rows.append((name, "[green]current[/green]"))

    rows.sort(key=lambda r: r[0])

    table = Table(show_header=True)
    table.add_column("Skill", style="bold")
    table.add_column("Status")
    for name, status in rows:
        table.add_row(name, status)

    console.print(table)

    n_stale = (
        len(result.skills_updated)
        + len(result.skills_installed)
        + len(result.skills_conflicted)
    )
    n_current = len(result.skills_current)
    if n_stale == 0:
        console.print(f"\n  All {n_current} skills are current.\n")
    else:
        console.print(
            f"\n  {n_stale} skill(s) need attention, "
            f"{n_current} current. Run [bold]rai init[/bold] to update.\n"
        )


@skill_app.command("sync")
def sync_cmd(
    path: Annotated[
        Path | None, typer.Option("--path", "-p", help="Project path")
    ] = None,
) -> None:
    """Check skill freshness against installed package version.

    Reports which skills are current, outdated, or have conflicts.
    Exit code 0 = all current, 1 = updates available.

    Examples:
        $ rai skill sync
        $ rai skill sync --path /path/to/project
    """
    from raise_cli.config.agent_registry import load_registry

    project_path = (path or Path.cwd()).resolve()
    registry = load_registry(project_root=project_path)

    # Determine agent type from manifest, fall back to "claude"
    agent_type = "claude"
    try:
        from raise_cli.onboarding.manifest import load_manifest

        manifest = load_manifest(project_path)
        if manifest and manifest.agents.types:
            agent_type = manifest.agents.types[0]
    except Exception:  # noqa: S110 -- best-effort manifest load, non-critical
        pass

    config = registry.get_config(agent_type)
    plugin = registry.get_plugin(agent_type)

    result = scaffold_skills(
        project_path,
        agent_config=config,
        plugin=plugin,
        dry_run=True,
    )

    _print_sync_table(result)

    has_updates = bool(
        result.skills_updated or result.skills_installed or result.skills_conflicted
    )
    if has_updates:
        raise typer.Exit(code=1)
