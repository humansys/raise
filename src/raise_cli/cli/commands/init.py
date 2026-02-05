"""Init CLI command for RaiSE project initialization.

This module provides the `raise init` command that:
- Detects if the project is greenfield or brownfield
- Creates .rai/manifest.yaml with project metadata
- Loads or creates ~/.rai/developer.yaml for personal profile
- Outputs adaptive messages based on experience level

Example:
    $ raise init
    $ raise init --name my-custom-name
"""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel

from raise_cli.onboarding.detection import detect_project_type
from raise_cli.onboarding.manifest import ProjectInfo, ProjectManifest, save_manifest
from raise_cli.onboarding.profile import (
    DeveloperProfile,
    ExperienceLevel,
    load_developer_profile,
    save_developer_profile,
)

console = Console()


# Message templates for different experience levels
WELCOME_SHU = """[bold cyan]Welcome to RaiSE![/bold cyan]

I'm [bold]Rai[/bold] — your AI partner for reliable software engineering.

Together, we'll build software that's both fast AND reliable.
The RaiSE methodology guides our collaboration:
  • [dim]You[/dim] bring intuition and judgment
  • [dim]I[/dim] bring execution and memory
  • [dim]Together[/dim]: reliable software at AI speed
"""

WELCOME_BACK_RI = "[dim]Welcome back, {name}.[/dim]"

PROJECT_DETECTED_SHU = """
[bold]Project detected:[/bold] {project_type} ({file_count} code files)
[bold]Created:[/bold] .rai/manifest.yaml
{profile_status}

[bold cyan]Next steps:[/bold cyan]
1. Open Claude Code in this directory
2. Run [bold]/session-start[/bold] to begin our first session together
3. I'll guide you through understanding your project

Questions? Visit https://raise.dev/docs
"""

PROJECT_DETECTED_RI = """{project_type} project initialized ({file_count} files).
Created .rai/manifest.yaml

Run [bold]/session-start[/bold] when ready.
"""


def _get_welcome_message(profile: DeveloperProfile | None) -> str:
    """Get welcome message based on profile existence and level."""
    if profile is None:
        return WELCOME_SHU

    if profile.experience_level == ExperienceLevel.RI:
        return WELCOME_BACK_RI.format(name=profile.name)
    elif profile.experience_level == ExperienceLevel.HA:
        return f"[cyan]Welcome back, {profile.name}.[/cyan]\n"
    else:
        return WELCOME_SHU


def _get_project_message(
    project_type: str,
    file_count: int,
    profile: DeveloperProfile | None,
    created_profile: bool,
) -> str:
    """Get project detection message based on experience level."""
    if profile is None or profile.experience_level == ExperienceLevel.SHU:
        profile_status = (
            "[bold]Created:[/bold] ~/.rai/developer.yaml (first time setup)"
            if created_profile
            else "[bold]Loaded:[/bold] ~/.rai/developer.yaml"
        )
        return PROJECT_DETECTED_SHU.format(
            project_type=project_type.capitalize(),
            file_count=file_count,
            profile_status=profile_status,
        )
    else:
        return PROJECT_DETECTED_RI.format(
            project_type=project_type.capitalize(),
            file_count=file_count,
        )


def _create_new_profile(project_path: Path) -> DeveloperProfile:
    """Create a new developer profile with defaults."""
    today = date.today()
    return DeveloperProfile(
        name="Developer",  # Will be personalized later
        experience_level=ExperienceLevel.SHU,
        sessions_total=0,
        first_session=today,
        last_session=today,
        projects=[str(project_path.resolve())],
    )


def _update_profile_with_project(
    profile: DeveloperProfile, project_path: Path
) -> DeveloperProfile:
    """Update profile to include current project."""
    project_str = str(project_path.resolve())
    if project_str not in profile.projects:
        profile.projects.append(project_str)
    profile.last_session = date.today()
    return profile


def init_command(
    name: Annotated[
        str | None,
        typer.Option(
            "--name",
            "-n",
            help="Project name (defaults to directory name)",
        ),
    ] = None,
    path: Annotated[
        Path | None,
        typer.Option(
            "--path",
            "-p",
            help="Project path (defaults to current directory)",
        ),
    ] = None,
) -> None:
    """Initialize a RaiSE project in the current directory.

    Detects project type (greenfield/brownfield), creates .rai/manifest.yaml,
    and sets up developer profile for personalized interaction.

    Examples:
        $ raise init
        $ raise init --name my-api
        $ raise init --path /path/to/project
    """
    # Determine project path
    project_path = path if path is not None else Path.cwd()
    project_path = project_path.resolve()

    # Determine project name
    project_name = name if name is not None else project_path.name

    # Load or create developer profile
    profile = load_developer_profile()
    created_profile = False

    if profile is None:
        profile = _create_new_profile(project_path)
        save_developer_profile(profile)
        created_profile = True
    else:
        profile = _update_profile_with_project(profile, project_path)
        save_developer_profile(profile)

    # Detect project type
    detection = detect_project_type(project_path)

    # Create and save manifest
    project_info = ProjectInfo(
        name=project_name,
        project_type=detection.project_type,
        code_file_count=detection.code_file_count,
    )
    manifest = ProjectManifest(project=project_info)
    save_manifest(manifest, project_path)

    # Output messages based on experience level
    welcome = _get_welcome_message(profile if not created_profile else None)
    project_msg = _get_project_message(
        project_type=detection.project_type.value,
        file_count=detection.code_file_count,
        profile=profile,
        created_profile=created_profile,
    )

    if profile.experience_level == ExperienceLevel.RI and not created_profile:
        # Concise output for experienced users
        console.print(welcome)
        console.print(project_msg)
    else:
        # Rich output for new/learning users
        console.print(Panel(welcome.strip(), border_style="cyan"))
        console.print(project_msg)
