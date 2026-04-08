"""Init CLI command for RaiSE project initialization.

This module provides the `rai init` command that:
- Detects if the project is greenfield or brownfield
- Creates .raise/manifest.yaml with project metadata
- Loads or creates ~/.rai/developer.yaml for personal profile
- Scaffolds skills, workflows, and governance for each target agent
- Supports multiple agents via --agent (repeatable) or --detect

Example:
    $ rai init                           # defaults to claude
    $ rai init --agent cursor            # single agent
    $ rai init --agent claude --agent cursor  # multi-agent
    $ rai init --detect                  # auto-detect installed agents
    $ rai init --ide antigravity         # (deprecated) alias for --agent
"""

import sys
from datetime import date
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel

from raise_cli.config.agent_registry import AgentRegistry, load_registry
from raise_cli.config.agents import AgentChoice, AgentConfig
from raise_cli.hooks.emitter import create_emitter
from raise_cli.hooks.events import InitCompleteEvent
from raise_cli.onboarding.bootstrap import BootstrapResult
from raise_cli.onboarding.conventions import detect_conventions
from raise_cli.onboarding.detection import (
    DetectionResult,
    ProjectType,
    detect_project_type,
)
from raise_cli.onboarding.governance import (
    GovernanceScaffoldResult,
    generate_guardrails,
)
from raise_cli.onboarding.instructions import generate_instructions
from raise_cli.onboarding.manifest import (
    AgentsManifest,
    BranchConfig,
    IdeManifest,
    ProjectInfo,
    ProjectManifest,
    load_manifest,
    save_manifest,
)
from raise_cli.onboarding.profile import (
    DeveloperProfile,
    ExperienceLevel,
    load_developer_profile,
    save_developer_profile,
)
from raise_cli.onboarding.skills import SkillScaffoldResult

console = Console()


def _print_skill_sync_summary(result: SkillScaffoldResult) -> None:  # noqa: C901 -- complexity 12, refactor deferred
    """Print a summary table of skill sync actions."""
    from raise_cli.skills_base import __version__ as cli_version

    console.print(f"\n[bold]Skill sync: raise-cli {cli_version}[/bold]\n")

    rows: list[tuple[str, str, str]] = []
    for name in result.skills_installed:
        rows.append((name, "[green]new[/green]", "install"))
    for name in result.skills_updated:
        rows.append((name, "[cyan]updated[/cyan]", "auto-update"))
    for name in result.skills_conflicted:
        rows.append((name, "[yellow]conflict[/yellow]", "prompt"))
    for name in result.skills_kept:
        rows.append((name, "[yellow]kept[/yellow]", "user chose keep"))
    for name in result.skills_overwritten:
        rows.append((name, "[cyan]overwritten[/cyan]", "user chose overwrite"))
    for name in result.skills_current:
        rows.append((name, "current", "skip"))

    rows.sort(key=lambda r: r[0])

    from rich.table import Table

    table = Table(show_header=True)
    table.add_column("Skill", style="bold")
    table.add_column("Status")
    table.add_column("Action")
    for name, status, action in rows:
        table.add_row(name, status, action)

    console.print(table)

    n_install = len(result.skills_installed)
    n_update = len(result.skills_updated)
    n_conflict = len(result.skills_conflicted) + len(result.skills_kept)
    n_current = len(result.skills_current) + len(result.skills_overwritten)
    parts: list[str] = []
    if n_install:
        parts.append(f"{n_install} new")
    if n_update:
        parts.append(f"{n_update} auto-update")
    if n_conflict:
        parts.append(f"{n_conflict} conflict")
    if n_current:
        parts.append(f"{n_current} current")
    console.print(f"\n  Summary: {', '.join(parts)}\n")


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

  [bold]1. Fill governance[/bold] (in Claude Code / AI editor):
     Type [bold cyan]{skill_recommendation}[/bold cyan]
     [dim]→ {skill_description}[/dim]

  [bold]2. Start a session[/bold] (after governance is set up):
     Type [bold cyan]/rai-session-start[/bold cyan]
     [dim]→ Loads your context, remembers patterns, proposes focused work[/dim]

  [bold]3. Explore the CLI[/bold] (in terminal):
     [dim]rai --help[/dim]      — see all commands
     [dim]rai context[/dim]     — query project context
     [dim]rai memory[/dim]      — query Rai's memory

[dim]Don't have Claude Code? https://claude.ai/download[/dim]
"""

PROJECT_DETECTED_RI = """{project_type} project ({file_count} files). Created .raise/manifest.yaml

[dim]Next:[/dim] {skill_recommendation}   [dim]Then:[/dim] /rai-session-start   [dim]CLI:[/dim] rai --help   [dim](claude.ai/download)[/dim]
"""


def _get_welcome_message(profile: DeveloperProfile | None) -> str:
    """Get welcome message based on profile existence and level."""
    if profile is None:
        return WELCOME_SHU

    if profile.experience_level == ExperienceLevel.RI:
        return WELCOME_BACK_RI.format(name=profile.name)
    if profile.experience_level == ExperienceLevel.HA:
        return f"[cyan]Welcome back, {profile.name}.[/cyan]\n"
    return WELCOME_SHU


def _get_skill_recommendation(project_type: str) -> tuple[str, str]:
    """Get recommended skill based on project type."""
    if project_type == "brownfield":
        return (
            "/rai-project-onboard",
            "Analyze codebase and fill governance from conversation",
        )
    return (
        "/rai-project-create",
        "Fill governance from conversation (new project)",
    )


def _build_shu_bootstrap_lines(
    bootstrap_result: BootstrapResult,
) -> list[str]:
    """Build SHU-level status lines for Rai base bootstrap results."""
    lines: list[str] = []
    if bootstrap_result.already_existed:
        if bootstrap_result.patterns_added > 0 or bootstrap_result.patterns_updated > 0:
            parts: list[str] = []
            if bootstrap_result.patterns_added > 0:
                parts.append(f"{bootstrap_result.patterns_added} new")
            if bootstrap_result.patterns_updated > 0:
                parts.append(f"{bootstrap_result.patterns_updated} updated")
            lines.append(
                "[bold]Synced:[/bold]  .raise/rai/memory/  "
                f"[dim]— {', '.join(parts)} base patterns[/dim]"
            )
        else:
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
            from importlib.resources import files as _res_files

            _base = _res_files("raise_cli.rai_base")
            _src = _base / "memory" / "patterns-base.jsonl"
            _count = len(
                [
                    ln
                    for ln in _src.read_text(encoding="utf-8").strip().splitlines()
                    if ln.strip()
                ]
            )
            lines.append(
                "[bold]Created:[/bold] .raise/rai/memory/  "
                f"[dim]— {_count} base patterns[/dim]"
            )
        if bootstrap_result.methodology_copied:
            lines.append(
                "[bold]Created:[/bold] .raise/rai/framework/  "
                "[dim]— methodology definition[/dim]"
            )
    return lines


def _build_shu_files_section(
    created_profile: bool,
    bootstrap_result: BootstrapResult | None,
    skills_result: SkillScaffoldResult | None,
    governance_result: GovernanceScaffoldResult | None,
    skills_dir: str | None,
) -> str:
    """Build the files-section string for SHU-level project message."""
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

    if bootstrap_result is not None:
        lines.extend(_build_shu_bootstrap_lines(bootstrap_result))

    if skills_result is not None:
        if skills_result.already_existed:
            lines.append(
                f"[bold]Loaded:[/bold]  {skills_dir}/  "
                "[dim]— skills already present[/dim]"
            )
        elif skills_result.skills_copied > 0:
            lines.append(
                f"[bold]Created:[/bold] {skills_dir}/  "
                f"[dim]— {skills_result.skills_copied} onboarding skills[/dim]"
            )

    if governance_result is not None:
        if governance_result.already_existed:
            lines.append(
                "[bold]Loaded:[/bold]  governance/  "
                "[dim]— governance templates already present[/dim]"
            )
        elif governance_result.files_created > 0:
            lines.append(
                f"[bold]Created:[/bold] governance/  "
                f"[dim]— {governance_result.files_created} governance templates[/dim]"
            )

    return "\n".join(lines)


def _build_ri_extra_messages(
    bootstrap_result: BootstrapResult | None,
    skills_result: SkillScaffoldResult | None,
    governance_result: GovernanceScaffoldResult | None,
    skills_dir: str | None,
) -> str:
    """Build extra message lines for RI-level project message."""
    bootstrap_msg = ""
    if bootstrap_result is not None:
        if not bootstrap_result.already_existed:
            bootstrap_msg = (
                f"  Bootstrapped Rai base v{bootstrap_result.base_version}\n"
            )
        elif (
            bootstrap_result.patterns_added > 0 or bootstrap_result.patterns_updated > 0
        ):
            parts_ri: list[str] = []
            if bootstrap_result.patterns_added > 0:
                parts_ri.append(f"{bootstrap_result.patterns_added} new")
            if bootstrap_result.patterns_updated > 0:
                parts_ri.append(f"{bootstrap_result.patterns_updated} updated")
            bootstrap_msg = f"  Synced base patterns: {', '.join(parts_ri)}\n"
    skills_msg = ""
    if skills_result is not None and not skills_result.already_existed:
        skills_msg = (
            f"  Installed {skills_result.skills_copied} skills to {skills_dir}/\n"
        )
    governance_msg = ""
    if governance_result is not None and not governance_result.already_existed:
        governance_msg = (
            f"  Scaffolded governance/ ({governance_result.files_created} templates)\n"
        )
    return bootstrap_msg + skills_msg + governance_msg


def _get_project_message(
    project_type: str,
    file_count: int,
    profile: DeveloperProfile | None,
    created_profile: bool,
    bootstrap_result: BootstrapResult | None = None,
    skills_result: SkillScaffoldResult | None = None,
    governance_result: GovernanceScaffoldResult | None = None,
    agent_config: AgentConfig | None = None,
) -> str:
    """Get project detection message based on experience level."""
    skills_dir = agent_config.skills_dir if agent_config else ".claude/skills"
    skill_cmd, skill_desc = _get_skill_recommendation(project_type)

    if profile is None or profile.experience_level == ExperienceLevel.SHU:
        files_section = _build_shu_files_section(
            created_profile,
            bootstrap_result,
            skills_result,
            governance_result,
            skills_dir,
        )
        return PROJECT_DETECTED_SHU.format(
            project_type=project_type.capitalize(),
            file_count=file_count,
            files_section=files_section,
            skill_recommendation=skill_cmd,
            skill_description=skill_desc,
        )

    extra = _build_ri_extra_messages(
        bootstrap_result, skills_result, governance_result, skills_dir
    )
    return (
        PROJECT_DETECTED_RI.format(
            project_type=project_type.capitalize(),
            file_count=file_count,
            skill_recommendation=skill_cmd,
        )
        + extra
    )


def _create_new_profile(project_path: Path) -> DeveloperProfile:
    """Create a new developer profile with defaults."""
    today = date.today()
    return DeveloperProfile(
        name="Developer",
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


def _resolve_agent_types(
    agent: list[str] | None,
    ide: AgentChoice | None,
    detect: bool,
    project_path: Path,
    registry: AgentRegistry,
) -> list[str]:
    """Resolve the list of agent types to initialize for.

    Priority: --agent > --ide (deprecated) > --detect > default ["claude"]
    """
    if agent:
        return list(agent)
    if ide is not None:
        return [ide.value]
    if detect:
        detected = registry.detect_agents(project_path)
        return detected if detected else ["claude"]
    return ["claude"]


def _prompt_agent_selection(
    detected: list[str],
    registry: AgentRegistry,
) -> list[str]:
    """Show detected agents and prompt user to confirm or extend selection.

    In non-interactive contexts (no TTY), prints the detected agents and
    returns them without prompting.

    Args:
        detected: Agent types found by auto-detection.
        registry: Registry used to list all available agents.

    Returns:
        Final list of agent types selected by the user.
    """
    all_agents = registry.list_agents()
    detected_label = ", ".join(detected) if detected else "none"
    console.print(f"\n[bold]Detected agents:[/bold] {detected_label}")

    if not sys.stdin.isatty():
        return detected if detected else ["claude"]

    console.print(f"[dim]Available:[/dim] {', '.join(all_agents)}")
    default = ",".join(detected) if detected else "claude"
    raw = typer.prompt(
        "Configure agents (comma-separated)",
        default=default,
    )
    return [a.strip() for a in raw.split(",") if a.strip()]


def _generate_agents_md(
    project_path: Path, agent_types: list[str], project_name: str
) -> None:
    """Generate AGENTS.md at project root — cross-tool instructions file.

    AGENTS.md is supported by Cursor, Windsurf, Copilot, Codex CLI, Kilo Code,
    OpenCode (60K+ repos use it as the universal agent instructions file).

    Uses IDE-specific session start instructions when only one agent is
    configured; uses generic instructions for multi-agent setups.
    """
    agents_md_path = project_path / "AGENTS.md"
    if agents_md_path.exists():
        return

    # Claude Code uses /skill-name syntax; other IDEs do not.
    # Use the slash-command form only for single-claude setups.
    if agent_types == ["claude"]:
        session_instruction = "Run `/rai-session-start` to load full context."
    else:
        session_instruction = (
            "Invoke the `rai-session-start` skill from your IDE to load full context."
        )

    content = (
        f"# {project_name}\n\n"
        f"> RaiSE-governed project. {session_instruction}\n\n"
        f"## Active Agents\n\n" + "\n".join(f"- {a}" for a in agent_types) + "\n\n"
        "## Process\n\n"
        "This project follows the RaiSE methodology. "
        "See `.raise/` for governance artifacts and `rai --help` for CLI.\n"
    )
    agents_md_path.write_text(content, encoding="utf-8")


def _load_or_create_profile(
    project_path: Path,
) -> tuple[DeveloperProfile, bool]:
    """Load existing developer profile or create a new one.

    Returns:
        Tuple of (profile, created_profile) where created_profile is True
        if a new profile was just created.
    """
    profile = load_developer_profile()
    created_profile = False

    if profile is None:
        profile = _create_new_profile(project_path)
        save_developer_profile(profile)
        created_profile = True
    else:
        profile = _update_profile_with_project(profile, project_path)
        save_developer_profile(profile)

    return profile, created_profile


def _validate_agent_types(
    agent_types: list[str],
    registry: AgentRegistry,
) -> list[str]:
    """Validate agent types against registry, warning on unknowns."""
    valid: list[str] = []
    for at in agent_types:
        try:
            registry.get_config(at)
            valid.append(at)
        except KeyError:
            console.print(f"[yellow]Warning:[/yellow] Unknown agent '{at}' — skipped.")
    return valid if valid else ["claude"]


def _create_and_save_manifest(
    project_path: Path,
    project_name: str,
    detection: DetectionResult,
    valid_agent_types: list[str],
) -> ProjectManifest:
    """Create project manifest from detection results and save it.

    When an existing manifest is present, preserve user-configured values
    and only update detection-derived fields (RAISE-1431, RAISE-1320).

    Preserved on re-init: name, ide, agents, language (if set), detected_at,
    toolchain commands (if user-configured), branches, tier, backlog.
    Updated on re-init: project_type, code_file_count (always re-scanned).
    """
    existing_manifest = load_manifest(project_path)
    ep = existing_manifest.project if existing_manifest else None

    # Preserve existing name if caller got it from directory (no --name flag)
    effective_name = project_name
    if ep and ep.name:
        if project_name == project_path.name:
            effective_name = ep.name

    # Preserve user-configured language; fall back to detection (RAISE-1320)
    effective_language = ep.language if ep and ep.language else detection.language

    # Preserve user-configured toolchain commands; fall back to detection
    detected_test = detection.toolchain.test_command if detection.toolchain else None
    detected_lint = detection.toolchain.lint_command if detection.toolchain else None
    detected_type = detection.toolchain.type_check_command if detection.toolchain else None
    detected_format = detection.toolchain.format_command if detection.toolchain else None

    project_info = ProjectInfo(
        name=effective_name,
        project_type=detection.project_type,
        code_file_count=detection.code_file_count,
        language=effective_language,
        test_command=ep.test_command if ep and ep.test_command else detected_test,
        lint_command=ep.lint_command if ep and ep.lint_command else detected_lint,
        type_check_command=ep.type_check_command if ep and ep.type_check_command else detected_type,
        format_command=ep.format_command if ep and ep.format_command else detected_format,
        # Preserve original detected_at timestamp on re-init (RAISE-1320)
        **({"detected_at": ep.detected_at} if ep else {}),
    )

    # Preserve existing agents/ide if present, merge new detections (RAISE-1431)
    if existing_manifest:
        existing_agents = existing_manifest.agents.types if existing_manifest.agents else []
        merged_agents = list(dict.fromkeys(existing_agents + valid_agent_types))
        effective_agents = merged_agents
        effective_ide = existing_manifest.ide
    else:
        effective_agents = valid_agent_types
        primary = valid_agent_types[0] if valid_agent_types else "claude"
        try:
            effective_ide = IdeManifest(type=primary)  # type: ignore[arg-type]
        except Exception:
            effective_ide = IdeManifest()

    manifest = ProjectManifest(
        project=project_info,
        agents=AgentsManifest(types=effective_agents),
        ide=effective_ide,
        branches=existing_manifest.branches if existing_manifest else BranchConfig(),
        tier=existing_manifest.tier if existing_manifest else None,
        # Preserve backlog config on re-init (RAISE-1320)
        backlog=existing_manifest.backlog if existing_manifest else None,
    )
    save_manifest(manifest, project_path)
    return manifest


def _bootstrap_project_assets(
    project_path: Path,
    project_name: str,
    manifest: ProjectManifest,
) -> tuple[BootstrapResult, GovernanceScaffoldResult, str]:
    """Bootstrap Rai base, governance templates, and generate MEMORY.md.

    Returns:
        Tuple of (bootstrap_result, governance_result, memory_content).
    """
    from raise_cli.onboarding.bootstrap import bootstrap_rai_base

    bootstrap_result = bootstrap_rai_base(project_path)

    from raise_cli.onboarding.governance import scaffold_governance

    governance_result = scaffold_governance(project_path, project_name)

    from raise_cli.config.paths import get_framework_dir, get_memory_dir
    from raise_cli.onboarding.memory_md import generate_memory_md

    methodology_path = get_framework_dir(project_path) / "methodology.yaml"
    patterns_path = get_memory_dir(project_path) / "patterns.jsonl"
    memory_content = generate_memory_md(
        methodology_path=methodology_path,
        patterns_path=patterns_path,
        project_name=project_name,
        development_branch=manifest.branches.development,
    )
    canonical_memory = get_memory_dir(project_path) / "MEMORY.md"
    canonical_memory.parent.mkdir(parents=True, exist_ok=True)
    canonical_memory.write_text(memory_content, encoding="utf-8")

    return bootstrap_result, governance_result, memory_content


def _scaffold_per_agent(
    project_path: Path,
    valid_agent_types: list[str],
    registry: AgentRegistry,
    memory_content: str,
    *,
    force: bool,
    skip_updates: bool,
    dry_run: bool,
    skill_set: str | None,
) -> SkillScaffoldResult | None:
    """Run per-agent scaffolding (skills, workflows, memory copy).

    Returns:
        The SkillScaffoldResult for the first agent, or None.
    """
    from raise_cli.onboarding.skills import scaffold_skills
    from raise_cli.onboarding.workflows import scaffold_workflows

    first_skills_result: SkillScaffoldResult | None = None

    for agent_type in valid_agent_types:
        config = registry.get_config(agent_type)
        plugin = registry.get_plugin(agent_type)

        skills_result = scaffold_skills(
            project_path,
            agent_config=config,
            plugin=plugin,
            force=force,
            skip_updates=skip_updates,
            dry_run=dry_run,
            skill_set=skill_set,
        )
        if agent_type == valid_agent_types[0]:
            first_skills_result = skills_result

        scaffold_workflows(project_path, agent_config=config)

        if config.agent_type == "claude":
            from raise_cli.config.paths import get_claude_memory_path

            claude_memory = get_claude_memory_path(project_path)
            claude_memory.parent.mkdir(parents=True, exist_ok=True)
            claude_memory.write_text(memory_content, encoding="utf-8")

        plugin.post_init(project_path, config)

    return first_skills_result


def _output_brownfield_warning(
    profile: DeveloperProfile,
    detection: DetectionResult,
    governance_result: GovernanceScaffoldResult,
) -> None:
    """Warn when brownfield governance was just scaffolded (empty templates)."""
    if not (
        detection.project_type == ProjectType.BROWNFIELD
        and not governance_result.already_existed
        and governance_result.files_created > 0
    ):
        return

    skill_cmd, _ = _get_skill_recommendation("brownfield")
    if profile.experience_level == ExperienceLevel.RI:
        console.print(
            f"\n[yellow]⚠ Governance docs are empty templates.[/yellow] "
            f"Run [bold cyan]{skill_cmd}[/bold cyan] to fill them."
        )
    else:
        console.print(
            Panel(
                f"[bold yellow]Governance docs need your input[/bold yellow]\n\n"
                f"[dim]vision.md, prd.md, backlog.md[/dim] were created as empty templates.\n"
                f"Any agent that reads them now will get [bold]no context[/bold].\n\n"
                f"Fill them before starting work:\n"
                f"  [bold cyan]{skill_cmd}[/bold cyan]",
                border_style="yellow",
                title="[yellow]⚠ Next step required[/yellow]",
            )
        )


def _detect_and_generate_guardrails(
    project_path: Path,
    project_name: str,
    profile: DeveloperProfile,
    instructions_file: str,
) -> None:
    """Detect conventions and generate guardrails for brownfield projects."""
    conventions = detect_conventions(project_path)

    if conventions.files_analyzed == 0:
        return

    guardrails_content = generate_guardrails(conventions, project_name=project_name)
    guardrails_dir = project_path / "governance"
    guardrails_dir.mkdir(parents=True, exist_ok=True)
    guardrails_path = guardrails_dir / "guardrails.md"
    guardrails_path.write_text(guardrails_content, encoding="utf-8")

    instructions_path = project_path / instructions_file
    conf = conventions.overall_confidence.value.upper()
    if profile.experience_level == ExperienceLevel.RI:
        console.print(
            f"\n[dim]Conventions detected ({conventions.files_analyzed} files, "
            f"{conf} confidence). Generated guardrails.md and {instructions_file}[/dim]"
        )
    else:
        console.print(
            f"\n[bold cyan]Convention Detection[/bold cyan]\n"
            f"Analyzed {conventions.files_analyzed} files with {conf} confidence.\n"
            f"Generated:\n"
            f"  - [bold]{guardrails_path}[/bold] (code standards)\n"
            f"  - [bold]{instructions_path}[/bold] (project context)\n\n"
            f"[dim]Review and adjust as needed.[/dim]"
        )


def _output_init_messages(
    profile: DeveloperProfile,
    created_profile: bool,
    detection: DetectionResult,
    bootstrap_result: BootstrapResult,
    first_skills_result: SkillScaffoldResult | None,
    governance_result: GovernanceScaffoldResult,
    first_config: AgentConfig,
) -> None:
    """Print welcome and project detection messages."""
    welcome = _get_welcome_message(profile if not created_profile else None)
    project_msg = _get_project_message(
        project_type=detection.project_type.value,
        file_count=detection.code_file_count,
        profile=profile,
        created_profile=created_profile,
        bootstrap_result=bootstrap_result,
        skills_result=first_skills_result,
        governance_result=governance_result,
        agent_config=first_config,
    )

    if profile.experience_level == ExperienceLevel.RI and not created_profile:
        console.print(welcome)
        console.print(project_msg)
    else:
        console.print(Panel(welcome.strip(), border_style="cyan"))
        console.print(project_msg)


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
            help="Auto-detect installed agents from project markers. Also generates AGENTS.md.",
        ),
    ] = False,
    agent: Annotated[
        list[str] | None,
        typer.Option(
            "--agent",
            help="Target agent(s): claude, cursor, windsurf, copilot, antigravity. Repeatable.",
        ),
    ] = None,
    ide: Annotated[
        AgentChoice | None,
        typer.Option(
            "--ide",
            help="[deprecated] Use --agent instead.",
            hidden=False,
        ),
    ] = None,
    dry_run: Annotated[
        bool,
        typer.Option(
            "--dry-run",
            help="Preview skill updates without writing files.",
        ),
    ] = False,
    force: Annotated[
        bool,
        typer.Option(
            "--force",
            help="Overwrite all skill files without prompting.",
        ),
    ] = False,
    skip_updates: Annotated[
        bool,
        typer.Option(
            "--skip-updates",
            help="Keep all existing skills, only install new ones.",
        ),
    ] = False,
    skill_set: Annotated[
        str | None,
        typer.Option(
            "--skill-set",
            help="Overlay a skill set from .raise/skills/{name}/ on top of builtins.",
        ),
    ] = None,
) -> None:
    """Initialize a RaiSE project in the current directory.

    Detects project type (greenfield/brownfield), creates .raise/manifest.yaml,
    and scaffolds skills/workflows for each target agent.

    Examples:
        $ rai init                                 # defaults to claude
        $ rai init --agent cursor                  # single agent
        $ rai init --agent claude --agent cursor   # multi-agent
        $ rai init --detect                        # auto-detect agents
        $ rai init --ide antigravity               # (deprecated) alias
    """
    project_path = (path if path is not None else Path.cwd()).resolve()
    project_name = name if name is not None else project_path.name

    # Load or create developer profile
    profile, created_profile = _load_or_create_profile(project_path)

    # Detect project type
    detection = detect_project_type(project_path)

    # Load agent registry and resolve agent types
    registry = load_registry(project_root=project_path)
    agent_types = _resolve_agent_types(agent, ide, detect, project_path, registry)

    if detect and agent is None and ide is None:
        agent_types = _prompt_agent_selection(agent_types, registry)

    valid_agent_types = _validate_agent_types(agent_types, registry)

    # Create and save manifest
    manifest = _create_and_save_manifest(
        project_path, project_name, detection, valid_agent_types
    )

    # Bootstrap project assets (Rai base, governance, MEMORY.md)
    bootstrap_result, governance_result, memory_content = _bootstrap_project_assets(
        project_path, project_name, manifest
    )

    # Per-agent scaffolding
    first_config = registry.get_config(valid_agent_types[0])
    first_skills_result = _scaffold_per_agent(
        project_path,
        valid_agent_types,
        registry,
        memory_content,
        force=force,
        skip_updates=skip_updates,
        dry_run=dry_run,
        skill_set=skill_set,
    )

    # Dry-run: show skill sync summary and exit
    if dry_run and first_skills_result is not None:
        _print_skill_sync_summary(first_skills_result)
        has_updates = bool(
            first_skills_result.skills_updated
            or first_skills_result.skills_installed
            or first_skills_result.skills_conflicted
        )
        raise typer.Exit(code=0 if not has_updates else 1)

    # Generate CLAUDE.md (or agent-specific instructions) for RaiSE projects
    if (project_path / ".raise").is_dir():
        instructions_content = generate_instructions(
            project_name=project_name,
            detection=detection,
            project_path=project_path,
        )
        instructions_path = project_path / first_config.instructions_file
        instructions_path.parent.mkdir(parents=True, exist_ok=True)
        instructions_path.write_text(instructions_content, encoding="utf-8")

    # Emit init:complete event
    emitter = create_emitter()
    emitter.emit(
        InitCompleteEvent(
            project_path=project_path,
            project_name=project_name,
        )
    )

    # AGENTS.md on --detect
    if detect:
        _generate_agents_md(project_path, valid_agent_types, project_name)

    # Output results and post-init warnings
    _output_init_messages(
        profile,
        created_profile,
        detection,
        bootstrap_result,
        first_skills_result,
        governance_result,
        first_config,
    )
    _output_brownfield_warning(profile, detection, governance_result)

    if detect and detection.project_type == ProjectType.BROWNFIELD:
        _detect_and_generate_guardrails(
            project_path, project_name, profile, first_config.instructions_file
        )
