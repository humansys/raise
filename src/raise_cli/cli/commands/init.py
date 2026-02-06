"""Init CLI command for RaiSE project initialization.

This module provides the `raise init` command that:
- Detects if the project is greenfield or brownfield
- Creates .raise/manifest.yaml with project metadata
- Loads or creates ~/.rai/developer.yaml for personal profile
- Outputs adaptive messages based on experience level
- Optionally detects conventions and generates guardrails (--detect)

Example:
    $ raise init
    $ raise init --name my-custom-name
    $ raise init --detect  # Detect conventions and generate guardrails
"""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import TYPE_CHECKING, Annotated

if TYPE_CHECKING:
    from raise_cli.onboarding.bootstrap import BootstrapResult

import typer
from rich.console import Console
from rich.panel import Panel

from raise_cli.onboarding.claudemd import generate_claude_md
from raise_cli.onboarding.conventions import detect_conventions
from raise_cli.onboarding.detection import ProjectType, detect_project_type
from raise_cli.onboarding.governance import generate_guardrails
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
{files_section}

[bold cyan]What's next?[/bold cyan]

  [bold]1. Start a session[/bold] (in Claude Code / AI editor):
     Type [bold cyan]/session-start[/bold cyan]
     [dim]→ Loads your context, remembers patterns, proposes focused work[/dim]

  [bold]2. Explore the CLI[/bold] (in terminal):
     [dim]raise --help[/dim]      — see all commands
     [dim]raise context[/dim]     — query project context
     [dim]raise memory[/dim]      — query Rai's memory

[dim]Don't have Claude Code? https://claude.ai/download[/dim]
"""

PROJECT_DETECTED_RI = """{project_type} project ({file_count} files). Created .raise/manifest.yaml

[dim]Editor:[/dim] /session-start   [dim]CLI:[/dim] raise --help   [dim](claude.ai/download)[/dim]
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
    bootstrap_result: BootstrapResult | None = None,
) -> str:
    """Get project detection message based on experience level.

    Args:
        project_type: Detected project type (greenfield/brownfield).
        file_count: Number of code files detected.
        profile: Developer profile (None for new users).
        created_profile: Whether profile was just created.
        bootstrap_result: Result of base Rai bootstrap (None if not run).

    Returns:
        Formatted message string for console output.
    """
    if profile is None or profile.experience_level == ExperienceLevel.SHU:
        # Build files section with descriptions
        lines = [
            "[bold]Created:[/bold] .raise/manifest.yaml  [dim]— project metadata[/dim]"
        ]
        if created_profile:
            lines.append(
                "[bold]Created:[/bold] ~/.rai/developer.yaml  "
                "[dim]— your preferences (first time)[/dim]"
            )
        else:
            lines.append(
                "[bold]Loaded:[/bold]  ~/.rai/developer.yaml  [dim]— your preferences[/dim]"
            )

        # Bootstrap info
        if bootstrap_result is not None:
            if bootstrap_result.already_existed:
                lines.append(
                    "[bold]Loaded:[/bold]  .raise/rai/  "
                    "[dim]— Rai base already present[/dim]"
                )
            else:
                if bootstrap_result.identity_copied:
                    lines.append(
                        "[bold]Created:[/bold] .raise/rai/identity/  "
                        "[dim]— Rai's base identity[/dim]"
                    )
                if bootstrap_result.patterns_copied:
                    lines.append(
                        "[bold]Created:[/bold] .raise/rai/memory/  "
                        "[dim]— 20 universal patterns[/dim]"
                    )
                if bootstrap_result.methodology_copied:
                    lines.append(
                        "[bold]Created:[/bold] .raise/rai/framework/  "
                        "[dim]— methodology definition[/dim]"
                    )

        files_section = "\n".join(lines)

        return PROJECT_DETECTED_SHU.format(
            project_type=project_type.capitalize(),
            file_count=file_count,
            files_section=files_section,
        )
    else:
        bootstrap_msg = ""
        if bootstrap_result is not None and not bootstrap_result.already_existed:
            bootstrap_msg = (
                f"  Bootstrapped Rai base v{bootstrap_result.base_version}\n"
            )
        return (
            PROJECT_DETECTED_RI.format(
                project_type=project_type.capitalize(),
                file_count=file_count,
            )
            + bootstrap_msg
        )


def _create_new_profile(project_path: Path) -> DeveloperProfile:
    """Create a new developer profile with defaults."""
    today = date.today()
    return DeveloperProfile(
        name="Developer",  # Will be personalized later
        experience_level=ExperienceLevel.SHU,
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
    detect: Annotated[
        bool,
        typer.Option(
            "--detect",
            "-d",
            help="Detect conventions and generate guardrails.md",
        ),
    ] = False,
) -> None:
    """Initialize a RaiSE project in the current directory.

    Detects project type (greenfield/brownfield), creates .raise/manifest.yaml,
    and sets up developer profile for personalized interaction.

    With --detect, also analyzes code conventions and generates guardrails.

    Examples:
        $ raise init
        $ raise init --name my-api
        $ raise init --path /path/to/project
        $ raise init --detect  # Detect conventions and generate guardrails
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

    # Bootstrap Rai base assets
    from raise_cli.onboarding.bootstrap import bootstrap_rai_base

    bootstrap_result = bootstrap_rai_base(project_path)

    # Generate MEMORY.md (canonical + Claude Code)
    from raise_cli.config.paths import (
        get_claude_memory_path,
        get_framework_dir,
        get_memory_dir,
    )
    from raise_cli.onboarding.memory_md import generate_memory_md

    methodology_path = get_framework_dir(project_path) / "methodology.yaml"
    patterns_path = get_memory_dir(project_path) / "patterns.jsonl"

    memory_content = generate_memory_md(
        methodology_path=methodology_path,
        patterns_path=patterns_path,
        project_name=project_name,
    )

    # Write canonical copy
    canonical_memory = get_memory_dir(project_path) / "MEMORY.md"
    canonical_memory.parent.mkdir(parents=True, exist_ok=True)
    canonical_memory.write_text(memory_content)

    # Write Claude Code copy
    claude_memory = get_claude_memory_path(project_path)
    claude_memory.parent.mkdir(parents=True, exist_ok=True)
    claude_memory.write_text(memory_content)

    # Output messages based on experience level
    welcome = _get_welcome_message(profile if not created_profile else None)
    project_msg = _get_project_message(
        project_type=detection.project_type.value,
        file_count=detection.code_file_count,
        profile=profile,
        created_profile=created_profile,
        bootstrap_result=bootstrap_result,
    )

    if profile.experience_level == ExperienceLevel.RI and not created_profile:
        # Concise output for experienced users
        console.print(welcome)
        console.print(project_msg)
    else:
        # Rich output for new/learning users
        console.print(Panel(welcome.strip(), border_style="cyan"))
        console.print(project_msg)

    # Convention detection, guardrails, and CLAUDE.md generation
    if detect and detection.project_type == ProjectType.BROWNFIELD:
        conventions = detect_conventions(project_path)

        if conventions.files_analyzed > 0:
            # Generate guardrails markdown
            guardrails_content = generate_guardrails(
                conventions, project_name=project_name
            )

            # Write to governance/solution/guardrails.md
            guardrails_dir = project_path / "governance" / "solution"
            guardrails_dir.mkdir(parents=True, exist_ok=True)
            guardrails_path = guardrails_dir / "guardrails.md"
            guardrails_path.write_text(guardrails_content)

            # Generate CLAUDE.md
            claude_md_content = generate_claude_md(
                project_name=project_name,
                detection=detection,
                conventions=conventions,
            )
            claude_md_path = project_path / "CLAUDE.md"
            claude_md_path.write_text(claude_md_content)

            # Output summary
            conf = conventions.overall_confidence.value.upper()
            if profile.experience_level == ExperienceLevel.RI:
                console.print(
                    f"\n[dim]Conventions detected ({conventions.files_analyzed} files, "
                    f"{conf} confidence). Generated guardrails.md and CLAUDE.md[/dim]"
                )
            else:
                console.print(
                    f"\n[bold cyan]Convention Detection[/bold cyan]\n"
                    f"Analyzed {conventions.files_analyzed} files with {conf} confidence.\n"
                    f"Generated:\n"
                    f"  - [bold]{guardrails_path}[/bold] (code standards)\n"
                    f"  - [bold]{claude_md_path}[/bold] (project context)\n\n"
                    f"[dim]Review and adjust as needed.[/dim]"
                )
    elif detect and detection.project_type == ProjectType.GREENFIELD:
        # Generate minimal CLAUDE.md for greenfield
        claude_md_content = generate_claude_md(
            project_name=project_name,
            detection=detection,
            conventions=None,
        )
        claude_md_path = project_path / "CLAUDE.md"
        claude_md_path.write_text(claude_md_content)

        if profile.experience_level != ExperienceLevel.RI:
            console.print(
                f"\n[dim]Created {claude_md_path}. No code to analyze yet — "
                "guardrails will be generated when conventions are established.[/dim]"
            )
