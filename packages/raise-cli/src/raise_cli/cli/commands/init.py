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

import json
import logging
import sys
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel

from raise_cli.agents.mcp_template import MCP_JSON_CONTENT
from raise_cli.config.agent_registry import AgentRegistry, load_registry
from raise_cli.config.agents import AgentChoice, AgentConfig
from raise_cli.config.paths import get_global_rai_dir
from raise_cli.config.server import get_server_credentials
from raise_cli.core.text import slugify as _slugify
from raise_cli.hooks.emitter import create_emitter
from raise_cli.hooks.events import InitCompleteEvent
from raise_cli.onboarding.bootstrap import ENV_EXAMPLE_CONTENT, BootstrapResult
from raise_cli.onboarding.conventions import detect_conventions
from raise_cli.onboarding.detection import (
    DetectedValue,
    DetectionResult,
    ProjectType,
    detect_apps,
    detect_base_branch,
    detect_ci,
    detect_project_type,
    detect_scm,
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
from raise_cli.onboarding.purge import (
    WORKTREEINCLUDE_CONTENT,
    FileDisposition,
    clean_global_profile,
    compute_dispositions,
    execute_purge,
    generate_agents_md_content,
)
from raise_cli.onboarding.skills import SkillScaffoldResult

console = Console()
logger = logging.getLogger(__name__)


def _server_config_for_init() -> tuple[str, str] | None:
    """Resolve server connection for init --server."""
    return get_server_credentials()


def _pull_server_config(project_name: str, project_path: Path) -> None:
    """Pull adapter config from RaiSE server during init."""
    raise_dir = project_path / ".raise"
    cfg = _server_config_for_init()
    if not cfg:
        console.print(
            "[red]Not connected to a RaiSE server.[/red] "
            "Run [bold]rai connect[/bold] first."
        )
        raise typer.Exit(1)
    server_url, api_key = cfg
    slug = _slugify(project_name)

    from raise_cli.cli.commands.project import pull_config_core

    result = pull_config_core(
        server_url=server_url,
        api_key=api_key,
        project_slug=slug,
        config_dir=raise_dir,
        force=True,
    )

    if result.status == "no_config":
        slug = _fallback_project_slug(server_url, api_key, slug)
        if slug:
            result = pull_config_core(
                server_url=server_url,
                api_key=api_key,
                project_slug=slug,
                config_dir=raise_dir,
                force=True,
            )

    if result.status in ("ok", "no_config"):
        from raise_cli.onboarding.manifest import persist_server_slug

        persist_server_slug(project_path, slug)

    if result.status == "ok":
        console.print("[green]✓ Config pulled[/green] from server")
        for fname in result.written:
            console.print(f"  Written: {raise_dir / fname}")
        console.print()
        console.print("  Set your credentials:")
        console.print("    export JIRA_API_TOKEN=<your-token>")
        console.print("    export JIRA_EMAIL=<your-email>")
    elif result.status == "no_config":
        console.print(
            f"[yellow]⚠ No adapter config[/yellow] on server for project '{slug}'"
        )
        console.print("  Push config with: [bold]rai project push-config[/bold]")


def _pull_knowledge_sync(project_path: Path, server_slug: str = "") -> None:
    """Descarga y mezcla el knowledge graph del servidor durante init (S-KS.1).

    Orquesta: pull remoto → parse payload → merge LWW → upsert SQLite local.
    Cualquier excepción → WARN log, return. Init continúa, exit 0 (AC-5).
    """
    from raise_cli.config.paths import checkout_scope_id
    from raise_cli.graph.backends.api import ApiGraphBackend
    from raise_cli.graph.backends.sqlite import SQLiteGraphBackend
    from raise_cli.graph.merge import merge_server_graph
    from raise_cli.graph.utils import build_graph_from_payload
    from raise_cli.storage.connection import (
        get_project_db_path,
        get_project_id,
    )

    cfg = _server_config_for_init()
    if not cfg:
        return  # sin credenciales → silencio (ya manejado en _pull_server_config)

    server_url, api_key = cfg

    try:
        local_id = get_project_id(project_path)
        remote_id = server_slug or local_id
        db_path = get_project_db_path(project_path)

        remote = ApiGraphBackend(
            server_url=server_url,
            api_key=api_key,
            project_id=remote_id,
        )
        local = SQLiteGraphBackend(
            project_id=local_id,
            db_path=db_path,
            # RAISE-15607: this backend calls upsert_nodes() — a scan-scope
            # writer. It must land in the checkout being initialised, not in
            # the repo-wide (cartridge) partition.
            checkout_id=checkout_scope_id(project_path),
        )

        console.print("  Pulling knowledge graph from server...")
        payload = remote.pull()

        server_graph = build_graph_from_payload(payload)
        local_graph = local.load()
        merged = merge_server_graph(local_graph, server_graph)

        # Conteos para el mensaje de éxito
        local_count = len(list(local_graph.graph.nodes()))
        server_count = len(payload.get("nodes", []))
        merged_count = len(list(merged.graph.nodes()))

        local.upsert_nodes(merged)

        console.print(
            f"  [green]✓ Knowledge graph merged:[/green] "
            f"{local_count} local + {server_count} server = {merged_count} nodes"
        )

    except Exception as exc:  # noqa: BLE001
        logger.warning(
            "Knowledge graph pull failed (%s) — using local graph only",
            exc,
        )
        console.print(
            "  [yellow]⚠ Knowledge graph pull failed[/yellow] "
            f"({exc}) — using local graph only"
        )


def _pull_cartridge_bootstrap(project_path: Path, server_slug: str = "") -> None:
    """Instala cartridges asignados al proyecto en el servidor (S-KS.2).

    Para cada cartridge asignado en server que no esté instalado localmente,
    llama install_from_server(). Idempotente: cartridges ya instalados se omiten.
    Cualquier excepción → WARN log, return. Init continúa, exit 0 (AC-4).
    """
    from raise_cli.cartridges.server_client import (
        CartridgeServerClient,
    )
    from raise_cli.cartridges.server_install import install_from_server
    from raise_cli.graph.backends.sqlite import SQLiteGraphBackend
    from raise_cli.storage.connection import (
        get_project_db_path,
        get_project_id,
    )

    cfg = _server_config_for_init()
    if not cfg:
        return  # sin credenciales → silencio (ya manejado en _pull_server_config)

    server_url, api_key = cfg

    try:
        local_id = get_project_id(project_path)
        remote_id = server_slug or local_id
        db_path = get_project_db_path(project_path)

        client = CartridgeServerClient(server_url, api_key)
        try:
            assigned = client.list_project_assignments(remote_id)
        finally:
            client.close()

        if not assigned:
            return  # sin cartridges asignados → no-op silencioso

        backend = SQLiteGraphBackend(local_id, db_path)
        installed_names = {row[0] for row in backend.list_cartridge_installations()}

        to_install = [a for a in assigned if a.cartridge_name not in installed_names]

        if not to_install:
            return  # todos ya instalados → idempotente

        console.print(f"  Instalando {len(to_install)} cartridge(s) del servidor...")

        installed_count = 0
        for assignment in to_install:
            try:
                n = install_from_server(
                    name=assignment.cartridge_name,
                    server_url=server_url,
                    api_key=api_key,
                    project_id=local_id,
                    db_path=db_path,
                    policy=assignment.policy,
                    ensure_org_install=False,
                )
                console.print(
                    f"  [green]✓ {assignment.cartridge_name}[/green] ({n} nodos)"
                )
                installed_count += 1
            except Exception as exc:  # noqa: BLE001 — per-cartridge isolation (QR H1)
                logger.warning(
                    "Cartridge '%s' no pudo instalarse (%s) — omitido",
                    assignment.cartridge_name,
                    exc,
                )
                console.print(
                    f"  [yellow]⚠ {assignment.cartridge_name}[/yellow] "
                    f"no disponible ({exc}) — omitido"
                )

        if installed_count > 0:
            console.print(
                f"  [green]✓ {installed_count} cartridge(s) instalado(s)[/green]"
            )

    except Exception as exc:  # noqa: BLE001
        logger.warning(
            "Cartridge bootstrap falló (%s) — init continúa sin cartridges",
            exc,
        )
        console.print(
            "  [yellow]⚠ Cartridge bootstrap falló[/yellow] "
            f"({exc}) — init continúa sin cartridges"
        )


def _pull_calibration_sync(project_path: Path, server_slug: str = "") -> None:
    """Descarga y merge calibración histórica del servidor (S-KS.3).

    Pull server → merge append-only por ID → write local nuevas → push locales al server.
    Cualquier excepción → WARN log, return. Init continúa, exit 0 (AC-4).
    """
    from raise_cli.calibration.merge import merge_calibration
    from raise_cli.calibration.server_client import (
        CalibrationServerClient,
    )
    from raise_cli.storage.connection import get_project_id

    cfg = _server_config_for_init()
    if not cfg:
        return

    server_url, api_key = cfg

    try:
        local_id = get_project_id(project_path)
        remote_id = server_slug or local_id
        cal_file = project_path / ".raise" / "rai" / "memory" / "calibration.jsonl"

        client = CalibrationServerClient(server_url, api_key)
        try:
            server_entries = client.pull(remote_id)
        finally:
            client.close()

        local_entries: list[dict[str, object]] = []
        if cal_file.exists():
            local_entries = [
                json.loads(line)
                for line in cal_file.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]

        merged, to_push = merge_calibration(local_entries, server_entries)

        # Escribir entradas nuevas del server al archivo local
        new_local = merged[len(local_entries) :]
        if new_local:
            cal_file.parent.mkdir(parents=True, exist_ok=True)
            with cal_file.open("a", encoding="utf-8") as f:
                for entry in new_local:
                    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            console.print(
                f"  [green]✓ Calibración[/green] {len(new_local)} entradas del servidor"
            )

        # Push entradas locales nuevas al server
        if to_push:
            push_client = CalibrationServerClient(server_url, api_key)
            try:
                n = push_client.push_bulk(remote_id, to_push)
                logger.debug("Calibración: %d entradas pushed al server", n)
            finally:
                push_client.close()

    except Exception as exc:  # noqa: BLE001
        logger.warning("Calibración sync falló (%s) — continuando sin sync", exc)
        console.print(
            f"  [yellow]⚠ Calibración sync[/yellow] no disponible ({exc}) — omitida"
        )


def _pull_patterns_sync(project_path: Path, server_slug: str = "") -> None:
    """Descarga y merge patrones del servidor durante init --server (S9776.1).

    Pull server → merge LWW local → upsert SQLite.
    Cualquier excepción → WARN log, return. Init continúa, exit 0 (AC-2/3).
    """
    from raise_cli.memory.sync import pull_patterns
    from raise_cli.storage.connection import (
        get_project_db,
        get_project_id,
    )

    cfg = _server_config_for_init()
    if not cfg:
        return

    try:
        local_id = get_project_id(project_path)
        remote_id = server_slug or local_id
        conn = get_project_db(project_path)
        try:
            result = pull_patterns(conn, project_id=remote_id)
        finally:
            conn.close()

        pulled = result.get("pulled", 0)
        new_count = result.get("new", 0)
        updated = result.get("updated", 0)
        if pulled:
            console.print(
                f"  [green]✓ Patrones sincronizados:[/green] "
                f"{pulled} pulled ({new_count} nuevos, {updated} actualizados)"
            )
        else:
            console.print("  [dim]✓ Patrones: sin cambios del servidor[/dim]")

    except Exception as exc:  # noqa: BLE001
        logger.warning(
            "Pattern sync falló (%s) — continuando sin sync de patrones",
            exc,
        )
        console.print(
            f"  [yellow]⚠ Pattern sync[/yellow] no disponible ({exc}) — omitido"
        )


def _restore_cc_memory_if_available(project_path: Path) -> None:
    """Restore CC Memory from git-tracked copy if available (S9476.1).

    Called during ``rai init --server`` after the project bootstrap completes.
    If ``.raise/rai/personal/memory/`` exists (e.g., cloned from git), imports
    the files to the machine-local CC Memory directory using LWW semantics.

    This is a best-effort operation — failures are logged, not raised.
    """
    from raise_cli.config.paths import get_personal_dir
    from raise_cli.memory.portability import import_memory

    personal_memory = get_personal_dir(project_path) / "memory"
    if not personal_memory.exists():
        return  # nothing to restore — silent

    try:
        result = import_memory(project_path, dry_run=False, overwrite=False)
        if result.copied:
            console.print(
                f"  [green]✓ CC Memory[/green] {len(result.copied)} file(s) restored "
                f"from .raise/rai/personal/memory/"
            )
    except Exception as exc:  # noqa: BLE001
        logger.warning(
            "CC Memory restore failed (%s) — continuing without restore", exc
        )


def _fallback_project_slug(
    server_url: str, api_key: str, tried_slug: str
) -> str | None:
    """When dirname-derived slug misses, try listing available projects."""
    from raise_cli.cli.commands import project as _proj_mod

    try:
        resp = _proj_mod.httpx.get(
            f"{server_url}/api/v2/projects",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10,
        )
        if resp.status_code >= 400:
            return None
        projects: list[dict[str, str]] = resp.json()
    except Exception:  # noqa: BLE001
        return None

    if not projects:
        return None

    slugs = [p.get("slug", "") for p in projects if p.get("slug")]

    if len(slugs) == 1:
        console.print(
            f"[yellow]⚠ No project '{tried_slug}' on server.[/yellow] "
            f"Found '[bold]{slugs[0]}[/bold]' — pulling config."
        )
        return slugs[0]

    console.print(
        f"[yellow]⚠ No project '{tried_slug}' on server.[/yellow] Available projects:"
    )
    for s in slugs:
        console.print(f"  • {s}")
    console.print(
        "\n  Re-run with: [bold]rai init --server --slug <project-slug>[/bold]"
    )
    return None


def _print_skill_sync_summary(result: SkillScaffoldResult) -> None:  # noqa: C901 -- complexity 12, refactor deferred
    """Print a summary table of skill sync actions."""
    from raise_cli import __version__ as cli_version

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

    content = generate_agents_md_content(project_name, agent_types)
    agents_md_path.write_text(content, encoding="utf-8")


def _scaffold_global_env_example() -> bool:
    """Create ~/.rai/.env.example with adapter credential placeholders.

    Idempotent — never overwrites an existing file.

    Returns:
        True if the file was created, False if it already existed.
    """
    dest = get_global_rai_dir() / ".env.example"
    if dest.exists():
        return False
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(ENV_EXAMPLE_CONTENT, encoding="utf-8")
    return True


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

    _scaffold_global_env_example()

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

    When an existing manifest is present, preserve its configured structure,
    refresh detection-owned project metadata, and only fill missing detected
    values (RAISE-1431, RAISE-1462).
    """
    existing_manifest = load_manifest(project_path)
    ep = existing_manifest.project if existing_manifest else None

    # Preserve user-configured toolchain commands; fall back to detection
    detected_test = detection.toolchain.test_command if detection.toolchain else None
    detected_lint = detection.toolchain.lint_command if detection.toolchain else None
    detected_type = (
        detection.toolchain.type_check_command if detection.toolchain else None
    )
    detected_format = (
        detection.toolchain.format_command if detection.toolchain else None
    )

    def existing_or_detected(
        field_name: str,
        existing_value: str | None,
        detected_value: str | None,
    ) -> str | None:
        """Preserve explicit values, including null; fill only absent fields."""
        if ep is not None and field_name in ep.model_fields_set:
            return existing_value
        return detected_value

    effective_language = existing_or_detected(
        "language",
        ep.language if ep else None,
        detection.language,
    )
    effective_test = existing_or_detected(
        "test_command",
        ep.test_command if ep else None,
        detected_test,
    )
    effective_lint = existing_or_detected(
        "lint_command",
        ep.lint_command if ep else None,
        detected_lint,
    )
    effective_type = existing_or_detected(
        "type_check_command",
        ep.type_check_command if ep else None,
        detected_type,
    )
    effective_format = existing_or_detected(
        "format_command",
        ep.format_command if ep else None,
        detected_format,
    )

    # Preserve existing name if caller got it from directory (no --name flag)
    effective_name = project_name
    if (
        existing_manifest
        and existing_manifest.project.name
        and project_name == project_path.name
    ):
        effective_name = existing_manifest.project.name

    # Detect monorepo apps (RAISE-2023)
    detected_apps = detect_apps(project_path, toolchain=detection.toolchain)
    effective_apps = (
        ep.apps
        if ep is not None and "apps" in ep.model_fields_set
        else (detected_apps or None)
    )

    if ep:
        optional_updates = {
            field_name: value
            for field_name, value in (
                ("language", effective_language),
                ("test_command", effective_test),
                ("lint_command", effective_lint),
                ("type_check_command", effective_type),
                ("format_command", effective_format),
                ("apps", effective_apps),
            )
            if value is not None
        }
        project_updates: dict[str, object] = {
            "name": effective_name,
            "project_type": detection.project_type,
            "code_file_count": detection.code_file_count,
            **optional_updates,
        }
        project_info = ep.model_copy(update=project_updates)
    else:
        project_info = ProjectInfo(
            name=effective_name,
            project_type=detection.project_type,
            code_file_count=detection.code_file_count,
            language=effective_language,
            test_command=effective_test,
            lint_command=effective_lint,
            type_check_command=effective_type,
            format_command=effective_format,
            apps=effective_apps,
            detected_at=datetime.now(UTC),
        )

    # Preserve existing agents/ide if present, merge new detections (RAISE-1431)
    if existing_manifest:
        existing_agents = (
            existing_manifest.agents.types if existing_manifest.agents else []
        )
        # Merge: keep existing + add newly detected (no duplicates)
        merged_agents = list(dict.fromkeys(existing_agents + valid_agent_types))
        effective_agents = existing_manifest.agents.model_copy(
            update={"types": merged_agents}
        )
        effective_ide = existing_manifest.ide
    else:
        effective_agents = AgentsManifest(types=valid_agent_types)
        # Sync ide.type with agents.types[0] (RAISE-218)
        primary = valid_agent_types[0] if valid_agent_types else "claude"
        try:
            effective_ide = IdeManifest(type=primary)  # type: ignore[arg-type]
        except Exception:  # noqa: BLE001 — intentional broad catch (grandfathered at BLE001 enablement, RAISE-15490)
            effective_ide = IdeManifest()

    manifest = (
        existing_manifest.model_copy(
            update={
                "project": project_info,
                "agents": effective_agents,
                "ide": effective_ide,
            }
        )
        if existing_manifest
        else ProjectManifest(
            project=project_info,
            agents=effective_agents,
            ide=effective_ide,
            branches=BranchConfig(),
        )
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


def _scaffold_raise_config_toml(project_path: Path) -> None:
    """Scaffold `.raise/config.toml` with a commented [rai] section.

    Idempotent: skips silently if `.raise/config.toml` already exists.

    The file documents available settings but leaves them all commented out
    so defaults apply. Users uncomment and set only what they need.
    """
    raise_dir = project_path / ".raise"
    config_toml = raise_dir / "config.toml"
    if config_toml.exists():
        return

    raise_dir.mkdir(parents=True, exist_ok=True)
    content = """\
# RaiSE project configuration
# Settings here apply to all contributors in this project.
# Uncomment and set only what you need — all fields are optional.
#
# Full cascade (highest to lowest priority):
#   CLI flags > env vars (RAI_*) > pyproject.toml [tool.rai]
#   > this file > ~/.config/rai/config.toml > defaults

[rai]
# output_format = "human"   # human | json | table
# verbosity = 0             # -1 (quiet) to 3 (debug)
# color = true
"""
    config_toml.write_text(content, encoding="utf-8")


def _scaffold_worktreeinclude(project_path: Path) -> None:
    """Scaffold `.worktreeinclude` with gitignored defaults for all supported agents.

    Idempotent — never overwrites an existing file (user may have customised it).
    Covers Claude (.claude/settings.local.json), Hermes (.hermes/config.yaml),
    Codex (.codex/, .codex-plugin/), universal env files, and direnv
    activation (.envrc — safe to copy verbatim since it only uses relative
    paths; see RAISE-10081).
    """
    worktreeinclude = project_path / ".worktreeinclude"
    if worktreeinclude.exists():
        return
    worktreeinclude.write_text(WORKTREEINCLUDE_CONTENT, encoding="utf-8")


def _scaffold_mcp_json(project_path: Path) -> None:
    """Scaffold `.mcp.json` with the rai-workspace MCP server entry.

    Idempotent: skips silently if `.mcp.json` already exists (users may have
    customised it with their own MCP servers).

    Conditional on the `mcp` extra being importable. If `mcp` is absent the
    pipeline MCP server cannot run anyway, so scaffolding would be misleading.

    Fixes RAISE-1664: init/upgrade used to never create this file, leaving
    Claude Code unable to auto-discover the rai-workspace MCP tools.
    """
    import importlib.util

    mcp_json = project_path / ".mcp.json"
    if mcp_json.exists():
        return

    if importlib.util.find_spec("mcp") is None:
        return

    mcp_json.write_text(json.dumps(MCP_JSON_CONTENT, indent=2) + "\n", encoding="utf-8")


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
    report_conflicts: bool = False,
    no_skills: bool = False,
) -> SkillScaffoldResult | None:
    """Run per-agent scaffolding (skills, workflows, memory copy).

    Returns:
        Combined SkillScaffoldResult for every configured agent, or None.
    """
    from raise_cli.onboarding.skills import (
        combine_skill_scaffold_results,
        scaffold_skills,
    )
    from raise_cli.onboarding.workflows import scaffold_workflows

    skill_results: list[SkillScaffoldResult] = []

    for agent_type in valid_agent_types:
        config = registry.get_config(agent_type)
        plugin = registry.get_plugin(agent_type)

        if not no_skills:
            skills_result = scaffold_skills(
                project_path,
                agent_config=config,
                plugin=plugin,
                force=force,
                skip_updates=skip_updates,
                dry_run=dry_run,
                skill_set=skill_set,
                report_conflicts=report_conflicts,
            )
            skill_results.append(skills_result)

        if dry_run:
            continue

        scaffold_workflows(project_path, agent_config=config)

        if config.agent_type == "claude":
            from raise_cli.config.paths import get_claude_memory_path

            claude_memory = get_claude_memory_path(project_path)
            claude_memory.parent.mkdir(parents=True, exist_ok=True)
            claude_memory.write_text(memory_content, encoding="utf-8")

        plugin.post_init(project_path, config)

    return combine_skill_scaffold_results(skill_results) if skill_results else None


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

    # Never overwrite user-customized guardrails on re-init (RAISE-1320/Gustavo).
    # Allow overwrite of empty scaffold templates (contain "fill with" marker).
    if guardrails_path.exists():
        existing = guardrails_path.read_text(encoding="utf-8")
        if "fill with /rai-project-create" not in existing:
            return

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


def _run_agent_post_init(project_path: Path, agent_types: list[str]) -> None:
    """Scaffold skills, workflows, instructions and run post_init for each agent.

    Called when .raise/ already exists and --agent is passed to init.
    Mirrors upgrade_command scaffolding: idempotent, skips current, updates outdated.
    """
    from raise_cli.onboarding.skills import scaffold_skills
    from raise_cli.onboarding.workflows import scaffold_workflows

    existing_manifest = load_manifest(project_path)
    project_name = (
        existing_manifest.project.name if existing_manifest else project_path.name
    )
    detection = detect_project_type(project_path)

    registry = load_registry(project_root=project_path)
    valid_types = _validate_agent_types(agent_types, registry)
    for agent_type in valid_types:
        config = registry.get_config(agent_type)
        plugin = registry.get_plugin(agent_type)

        scaffold_skills(project_path, agent_config=config, plugin=plugin)
        scaffold_workflows(project_path, agent_config=config)

        instructions_content = generate_instructions(
            project_name=project_name,
            detection=detection,
            project_path=project_path,
        )
        instructions_path = project_path / config.instructions_file
        instructions_path.parent.mkdir(parents=True, exist_ok=True)
        instructions_path.write_text(instructions_content, encoding="utf-8")

        created = plugin.post_init(project_path, config)
        if created:
            console.print(
                f"[green]✓[/green] {agent_type}: {len(created)} files configured"
            )
            for f in created:
                console.print(f"  [dim]{f}[/dim]")


def _apply_project_conventions(project_path: Path) -> None:
    """Detect and merge ADR-071 project.* convention defaults into manifest."""
    from raise_cli.onboarding.detection import detect_project_conventions
    from raise_cli.onboarding.merge_conventions import merge_project_conventions

    current_manifest = load_manifest(project_path)
    if current_manifest is None:
        return
    conventions = detect_project_conventions(project_path)
    if not conventions:
        return
    added = merge_project_conventions(current_manifest, conventions, project_path)
    if added:
        console.print(
            "[bold]Conventions:[/bold] project.code.root_glob added to manifest"
            "  [dim](run rai manifest validate to verify)[/dim]"
        )
    else:
        console.print(
            "[dim]Project conventions already configured — no changes made.[/dim]"
        )


def _is_interactive() -> bool:
    """Return True when stdin is a real TTY (not piped or CI)."""
    import sys

    return sys.stdin.isatty()


def _fmt_detected(detected: DetectedValue[str]) -> str:
    """Render a DetectedValue for plan display, with its confidence tier.

    A tier=default/value=None result is never shown as a confirmed value —
    "not detected" always carries its tier alongside it, so a guess is never
    mistaken for a verified fact (RAISE-16561/RAISE-16563).
    """
    if detected.value is None:
        return f"not detected ({detected.tier})"
    return f"{detected.value} ({detected.tier} — {detected.source or 'unknown'})"


def _build_init_write_plan(
    project_path: Path,
    *,
    detect: bool,
    server: bool,
    no_skills: bool,
) -> list[str]:
    """List every path/action init_command would write, gated behind --apply.

    Census (RAISE-16562/S15707.1 design): manifest, bootstrap assets
    (governance/cartridges), skills, per-agent instructions, .mcp.json,
    .worktreeinclude, .raise/config.toml, developer profile, plus the
    conditional --detect and --server write-paths.
    """
    lines = [
        str(project_path / ".raise" / "manifest.yaml"),
        str(project_path / ".raise") + " (governance, cartridges)",
    ]
    if not no_skills:
        lines.append("skills for target agent(s)")
    lines.append("instructions file(s) per agent")
    lines.append(str(project_path / ".mcp.json"))
    lines.append(str(project_path / ".worktreeinclude"))
    lines.append(str(project_path / ".raise" / "config.toml"))
    lines.append("~/.rai/developer.yaml (if not already present)")
    if detect:
        lines.append("AGENTS.md, project conventions (--detect)")
    if server:
        lines.append(
            "server pulls: adapter config, knowledge graph, cartridges, "
            "calibration, patterns (--server)"
        )
    return lines


def _show_init_preflight(
    project_path: Path,
    valid_agent_types: list[str],
    registry: "AgentRegistry",  # noqa: ARG001 — reserved for future preflight detail
    *,
    apply: bool,
    detect: bool = False,
    server: bool = False,
    no_skills: bool = False,
) -> None:
    """Print the init plan — what would be written, using real detected values.

    Extended from the RAISE-15702 preflight summary (which only listed
    agents + a generic "Writes: .raise" line) to cover every write-path and
    use real SCM/branch/CI detection (RAISE-16562/S15707.1, D1: reuse this
    function rather than a parallel plan renderer). Used both as the default
    read-only plan (apply=False) and as the confirmation preflight shown
    before an interactive --apply (apply=True).
    """
    from raise_cli.skills_base import DISTRIBUTABLE_SKILLS

    skill_count = len(DISTRIBUTABLE_SKILLS)
    agents_line = ", ".join(f"{a} ({skill_count} skills)" for a in valid_agent_types)

    scm = detect_scm(project_path)
    branch = detect_base_branch(project_path)
    ci = detect_ci(project_path)
    write_lines = _build_init_write_plan(
        project_path, detect=detect, server=server, no_skills=no_skills
    )
    would_write = "\n".join(f"    {line}" for line in write_lines)

    heading = "Init preflight" if apply else "Init plan"
    console.print(
        f"\n[bold]{heading}[/bold] — {project_path.name}\n"
        f"  Agents:    {agents_line}\n"
        f"  SCM:       {_fmt_detected(scm)}\n"
        f"  Branch:    {_fmt_detected(branch)}\n"
        f"  CI:        {_fmt_detected(ci)}\n"
        f"  Would write:\n{would_write}\n"
        f"  Global:    ~/.rai/developer.yaml"
    )
    if not apply:
        console.print("\nNo files written. Run with --apply to write.\n")


def init_command(  # noqa: C901 -- CLI gateway with user space detection; intentional
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
            help="Target agent(s): claude, cursor, windsurf, copilot, antigravity, roo, hermes, codex, kimi, devin. Repeatable.",
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
    apply: Annotated[
        bool,
        typer.Option(
            "--apply",
            help="Write files. Without --apply, rai init only prints the plan "
            "and writes nothing (RAISE-16562).",
        ),
    ] = False,
    dry_run: Annotated[
        bool,
        typer.Option(
            "--dry-run",
            help="[deprecated] No longer needed — rai init without --apply "
            "already never writes. Kept as a no-op alias.",
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
    server: Annotated[
        bool,
        typer.Option(
            "--server",
            help="Pull adapter config from the RaiSE server after init.",
        ),
    ] = False,
    slug: Annotated[
        str | None,
        typer.Option(
            "--slug",
            help="Explicit project slug for --server (bypasses dirname derivation).",
        ),
    ] = None,
    no_skills: Annotated[
        bool,
        typer.Option(
            "--no-skills",
            help="Skip skill copy — use when skills are already in user space (~/.claude/skills/).",
        ),
    ] = False,
    yes: Annotated[
        bool,
        typer.Option(
            "--yes",
            "-y",
            help="Skip confirmation prompt — suitable for CI and scripts (RAISE-15702).",
        ),
    ] = False,
    check_instructions: Annotated[
        bool,
        typer.Option(
            "--check-instructions",
            help="Check instruction files are in sync with .raise/ sources. Exit 1 on drift.",
        ),
    ] = False,
) -> None:
    """Initialize a RaiSE project in the current directory.

    First-time setup only. If the project is already initialized (.raise/ exists),
    use ``rai upgrade`` instead to update skills, framework files, and configuration.

    Examples:
        $ rai init                                 # prints the plan, writes nothing
        $ rai init --apply                         # writes, defaults to claude
        $ rai init --apply --agent cursor          # single agent
        $ rai init --apply --agent claude --agent cursor  # multi-agent
        $ rai init --apply --detect                # auto-detect agents
        $ rai init --apply --force                 # re-init (destructive)
        $ rai init --apply --server                # pull adapter config from server
    """
    project_path = (path if path is not None else Path.cwd()).resolve()
    project_name = name if name is not None else project_path.name

    # --check-instructions: read-only sync check, exit 0/1 (RAISE-16300)
    if check_instructions:
        from raise_cli.onboarding.instructions_check import check_instructions_sync

        result = check_instructions_sync(project_path)
        if result.is_clean:
            console.print("✓ OK — all instructions in sync")
            raise typer.Exit(code=0)
        for drift in result.drifted:
            console.print(f"DRIFT {drift.instructions_file}: {drift.reason}")
        console.print(
            f"✗ {len(result.drifted)} file(s) out of sync — "
            "run 'rai init --detect' to fix"
        )
        raise typer.Exit(code=1)

    # Guard: already initialized? Suggest rai upgrade (RAISE-1462)
    # Exception: --agent runs plugin post_init only (e.g. adding codex to existing project)
    raise_dir = project_path / ".raise"
    if raise_dir.is_dir() and not force:
        if agent:
            if not apply:
                console.print(
                    f"\n[bold]Init plan[/bold] — {project_path.name}\n"
                    f"  Would configure agent(s): {', '.join(agent)}\n"
                    "\nNo files written. Run with --apply to write.\n"
                )
                raise typer.Exit(code=0)
            _run_agent_post_init(project_path, list(agent))
            raise typer.Exit(code=0)
        console.print(
            "[yellow]Project already initialized[/yellow] "
            f"(.raise/ exists at {project_path}).\n\n"
            "To update skills and framework files, run:\n"
            "  [bold]rai upgrade[/bold]\n\n"
            "To re-initialize from scratch, run:\n"
            "  [bold]rai init --force[/bold]"
        )
        raise typer.Exit(code=1)

    # Detect project type (read-only — safe for dry-run)
    detection = detect_project_type(project_path)

    # Load agent registry and resolve agent types (read-only)
    registry = load_registry(project_root=project_path)
    agent_types = _resolve_agent_types(agent, ide, detect, project_path, registry)

    if detect and agent is None and ide is None and not yes:
        agent_types = _prompt_agent_selection(agent_types, registry)

    valid_agent_types = _validate_agent_types(agent_types, registry)

    # --dry-run is deprecated: rai init without --apply already never writes.
    # Kept as a no-op alias so existing scripts don't break (RAISE-16562).
    if dry_run:
        console.print(
            "[yellow]--dry-run is deprecated[/yellow] — rai init without "
            "--apply already never writes. This flag will be removed in a "
            "future version."
        )

    # --apply is the sole write-gate (RAISE-16562/S15707.1). Without it,
    # print the plan — using real detected SCM/branch/CI — and write nothing,
    # regardless of interactivity, --yes, --force, --detect, or --server.
    if not apply:
        _show_init_preflight(
            project_path,
            valid_agent_types,
            registry,
            apply=False,
            detect=detect,
            server=server,
            no_skills=no_skills,
        )
        raise typer.Exit(code=0)

    # --- Preflight display + confirmation (RAISE-15702) ---
    _show_init_preflight(
        project_path,
        valid_agent_types,
        registry,
        apply=True,
        detect=detect,
        server=server,
        no_skills=no_skills,
    )
    if (
        not yes
        and not force
        and _is_interactive()
        and not typer.confirm("Proceed with init?", default=False)
    ):
        raise typer.Exit(0)

    # --- All writes below this line ---

    # Load or create developer profile
    profile, created_profile = _load_or_create_profile(project_path)

    # Create and save manifest
    manifest = _create_and_save_manifest(
        project_path, project_name, detection, valid_agent_types
    )

    # Bootstrap project assets (Rai base, governance, MEMORY.md)
    bootstrap_result, governance_result, memory_content = _bootstrap_project_assets(
        project_path, project_name, manifest
    )

    # Scaffold bundled cartridges to .raise/cartridges/
    from raise_cli.onboarding.cartridges import scaffold_cartridges

    cartridges_result = scaffold_cartridges(project_path, force=force)
    if cartridges_result.cartridges_distributed > 0:
        console.print(
            f"  Distributed {cartridges_result.cartridges_distributed} "
            f"cartridge(s): {', '.join(cartridges_result.names_distributed)}"
        )
    if cartridges_result.cartridges_skipped > 0:
        console.print(
            f"  [dim]Skipped {cartridges_result.cartridges_skipped} existing "
            f"cartridge(s)[/dim]"
        )

    # User space detection: skip skills if already in ~/.claude/skills/
    if not no_skills and not force:
        from raise_cli.onboarding.skills import detect_user_space_skills
        from raise_cli.skills_base import DISTRIBUTABLE_SKILLS

        user_skills_dir = Path.home() / ".claude" / "skills"
        user_space_count = detect_user_space_skills(user_skills_dir)
        if user_space_count > 0:
            import sys

            total = len(DISTRIBUTABLE_SKILLS)
            if sys.stdin.isatty():
                answer = input(
                    f"Found {user_space_count}/{total} RaiSE skills in {user_skills_dir} (user space).\n"
                    "Skip local copy? [Y/n]: "
                )
                no_skills = answer.strip().lower() not in ("n", "no")
            else:
                console.print(
                    f"[dim]Found {user_space_count} RaiSE skills in user space — skipping local copy.[/dim]"
                )
                no_skills = True

    # Per-agent scaffolding
    first_config = registry.get_config(valid_agent_types[0])
    first_skills_result = _scaffold_per_agent(
        project_path,
        valid_agent_types,
        registry,
        memory_content,
        force=force,
        skip_updates=skip_updates,
        dry_run=False,
        skill_set=skill_set,
        no_skills=no_skills,
    )

    # Generate instructions file for every configured agent (RAISE-13457).
    # Previously only wrote first_config.instructions_file; all agents need regeneration.
    if (project_path / ".raise").is_dir():
        instructions_content = generate_instructions(
            project_name=project_name,
            detection=detection,
            project_path=project_path,
        )
        for _agent_type in valid_agent_types:
            _agent_config = registry.get_config(_agent_type)
            instructions_path = project_path / _agent_config.instructions_file
            instructions_path.parent.mkdir(parents=True, exist_ok=True)
            instructions_path.write_text(instructions_content, encoding="utf-8")

    # Scaffold .mcp.json for Claude Code auto-discovery (RAISE-1664)
    _scaffold_mcp_json(project_path)
    # Scaffold .worktreeinclude with gitignored defaults for all agents (RAISE-5114)
    _scaffold_worktreeinclude(project_path)
    # Scaffold .raise/config.toml — language-agnostic project config surface
    _scaffold_raise_config_toml(project_path)

    # Emit init:complete event
    emitter = create_emitter()
    emitter.emit(
        InitCompleteEvent(
            project_path=project_path,
            project_name=project_name,
        )
    )

    # Pull adapter config from server (S6277.4, S8862.5 slug fallback)
    if server:
        server_project_slug = _slugify(slug or project_name)
        _pull_server_config(slug or project_name, project_path)
        # Pull knowledge graph del servidor y merge LWW (S-KS.1)
        _pull_knowledge_sync(project_path, server_slug=server_project_slug)
        # Bootstrap cartridges asignados al proyecto (S-KS.2)
        _pull_cartridge_bootstrap(project_path, server_slug=server_project_slug)
        # Sync calibración histórica del equipo (S-KS.3)
        _pull_calibration_sync(project_path, server_slug=server_project_slug)
        # Pull patrones del equipo del servidor (S9776.1)
        _pull_patterns_sync(project_path, server_slug=server_project_slug)
        # Restore CC Memory from git-tracked copy if available (S9476.1)
        _restore_cc_memory_if_available(project_path)

    # AGENTS.md on --detect
    if detect:
        _generate_agents_md(project_path, valid_agent_types, project_name)

    # Project conventions on --detect (ADR-071 project.* defaults)
    if detect:
        _apply_project_conventions(project_path)

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


# =============================================================================
# rai upgrade — re-init with merge strategy (RAISE-1462)
# =============================================================================


def upgrade_command(  # noqa: C901 -- CLI gateway with many options; intentional
    path: Annotated[
        Path | None,
        typer.Option(
            "--path",
            "-p",
            help="Project root directory (defaults to current directory).",
        ),
    ] = None,
    detect: Annotated[
        bool,
        typer.Option(
            "--detect",
            "-d",
            help="Re-detect installed agents and update AGENTS.md.",
        ),
    ] = False,
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
    report_conflicts: Annotated[
        bool,
        typer.Option(
            "--report-conflicts",
            help="Output skill conflicts as JSON instead of resolving interactively.",
        ),
    ] = False,
    no_skills: Annotated[
        bool,
        typer.Option(
            "--no-skills",
            help="Skip skill sync — use when skills are already in user space (~/.claude/skills/).",
        ),
    ] = False,
) -> None:
    """Update an existing RaiSE project to the latest version.

    Updates skills, framework files, and regenerates AGENTS.md while preserving
    user-configured values (manifest fields, governance docs, custom skills).

    Use ``rai init`` for first-time project setup.

    Examples:
        $ rai upgrade                  # update skills + framework
        $ rai upgrade --detect         # also re-detect agents
        $ rai upgrade --dry-run        # preview changes
        $ rai upgrade --skip-updates   # only install new skills
    """
    project_path = (path if path is not None else Path.cwd()).resolve()

    # Guard: must be initialized
    raise_dir = project_path / ".raise"
    if not raise_dir.is_dir():
        console.print(
            "[red]Project not initialized[/red] "
            f"(no .raise/ at {project_path}).\n\n"
            "Run [bold]rai init[/bold] first to set up the project."
        )
        raise typer.Exit(code=1)

    # Load existing manifest for project name
    existing_manifest = load_manifest(project_path)
    project_name = (
        existing_manifest.project.name if existing_manifest else project_path.name
    )

    # Developer profile updates are project-visible state and must not run
    # during a read-only preview.
    if not dry_run:
        _profile, _created = _load_or_create_profile(project_path)

    # Detect project type
    detection = detect_project_type(project_path)

    # Load agent registry and resolve agent types
    registry = load_registry(project_root=project_path)
    if detect:
        agent_types = _resolve_agent_types(None, None, True, project_path, registry)
    elif existing_manifest:
        agent_types = (
            existing_manifest.agents.types if existing_manifest.agents else ["claude"]
        )
    else:
        agent_types = ["claude"]

    valid_agent_types = _validate_agent_types(agent_types, registry)

    memory_content = ""
    if not dry_run:
        # Update manifest with merge strategy (preserves user config)
        manifest = _create_and_save_manifest(
            project_path, project_name, detection, valid_agent_types
        )

        # Bootstrap (idempotent — skips existing files)
        _bootstrap_result, _governance_result, memory_content = (
            _bootstrap_project_assets(project_path, project_name, manifest)
        )

    # Update skills (diff/merge UX)
    first_skills_result = _scaffold_per_agent(
        project_path,
        valid_agent_types,
        registry,
        memory_content,
        force=force,
        skip_updates=skip_updates,
        dry_run=dry_run,
        skill_set=skill_set,
        report_conflicts=report_conflicts,
        no_skills=no_skills,
    )

    # Report-conflicts: output JSON and exit
    if report_conflicts and first_skills_result is not None:
        if first_skills_result.conflict_details:
            import json

            report = [d.model_dump() for d in first_skills_result.conflict_details]
            console.print_json(json.dumps(report))
            raise typer.Exit(code=1)
        raise typer.Exit(code=0)

    # Dry-run: show summary and exit
    if dry_run:
        has_updates = False
        if first_skills_result is not None:
            _print_skill_sync_summary(first_skills_result)
            has_updates = bool(
                first_skills_result.skills_updated
                or first_skills_result.skills_installed
                or first_skills_result.skills_conflicted
            )
        raise typer.Exit(code=0 if not has_updates else 1)

    # Regenerate instructions file for every configured agent (RAISE-13457).
    # Previously only wrote first_config.instructions_file; all agents need regeneration.
    if raise_dir.is_dir():
        instructions_content = generate_instructions(
            project_name=project_name,
            detection=detection,
            project_path=project_path,
        )
        for _agent_type in valid_agent_types:
            _agent_config = registry.get_config(_agent_type)
            instructions_path = project_path / _agent_config.instructions_file
            instructions_path.parent.mkdir(parents=True, exist_ok=True)
            instructions_path.write_text(instructions_content, encoding="utf-8")

    # Scaffold .mcp.json if missing (RAISE-1664). Idempotent.
    _scaffold_mcp_json(project_path)
    # Scaffold .worktreeinclude with gitignored defaults for all agents (RAISE-5114)
    _scaffold_worktreeinclude(project_path)
    # Scaffold .raise/config.toml — language-agnostic project config surface
    _scaffold_raise_config_toml(project_path)

    # Emit event
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

    # Output
    console.print(f"\n[bold green]Upgrade complete[/bold green] — {project_name}\n")
    if first_skills_result:
        installed = len(first_skills_result.skills_installed)
        updated = len(first_skills_result.skills_updated)
        kept = len(first_skills_result.skills_kept)
        if installed or updated:
            console.print(
                f"  Skills: {installed} new, {updated} updated, {kept} unchanged"
            )
        else:
            console.print("  Skills: all up to date")


# =============================================================================
# rai purge — cleanly reverse `rai init` (RAISE-15700)
# =============================================================================


def _print_purge_preview(
    project_path: Path,
    to_remove: list[FileDisposition],
    to_preserve: list[FileDisposition],
) -> None:
    """Print the plan of what purge will remove and preserve."""
    console.print(f"\n[bold]rai purge[/bold] — {project_path}\n")
    if to_remove:
        console.print(f"[red]Will remove ({len(to_remove)}):[/red]")
        for disposition in to_remove:
            console.print(f"  - {disposition.path}")
    if to_preserve:
        console.print(
            f"\n[yellow]Will preserve — modified since scaffolding "
            f"({len(to_preserve)}):[/yellow]"
        )
        for disposition in to_preserve:
            console.print(f"  - {disposition.path}")
    console.print()


def purge_command(
    path: Annotated[
        Path | None,
        typer.Option(
            "--path",
            "-p",
            help="Project root directory (defaults to current directory).",
        ),
    ] = None,
    dry_run: Annotated[
        bool,
        typer.Option(
            "--dry-run",
            help="Preview what would be removed without writing anything.",
        ),
    ] = False,
    include_global: Annotated[
        bool,
        typer.Option(
            "--include-global",
            help="Also remove this project's entry from ~/.rai/developer.yaml.",
        ),
    ] = False,
    yes: Annotated[
        bool,
        typer.Option(
            "--yes",
            "-y",
            help="Skip the interactive confirmation prompt.",
        ),
    ] = False,
) -> None:
    """Cleanly reverse `rai init`: remove all RaiSE-owned files from a project.

    Detects RaiSE-owned paths (.raise/, governance/, agent skills/workflows,
    instructions files, .mcp.json, .worktreeinclude, .env.example) and
    removes those that are unmodified since scaffolding. Files a human has
    edited are preserved and reported, never silently deleted.
    """
    project_path = (path or Path.cwd()).resolve()
    raise_dir = project_path / ".raise"

    if not raise_dir.is_dir():
        console.print(
            f"[red]Error:[/red] {project_path} is not a RaiSE project "
            "(no .raise/ directory found). Nothing to purge."
        )
        raise typer.Exit(code=1)

    dispositions = compute_dispositions(project_path)
    to_remove = [d for d in dispositions if d.action == "remove"]
    to_preserve = [d for d in dispositions if d.action == "preserve"]

    _print_purge_preview(project_path, to_remove, to_preserve)

    if dry_run:
        console.print("[dim]Dry run — no files were removed.[/dim]")
        raise typer.Exit(code=0)

    if not yes and to_remove:
        confirmed = typer.confirm("Proceed with removal?", default=False)
        if not confirmed:
            console.print("[dim]Aborted — no files were removed.[/dim]")
            raise typer.Exit(code=1)

    result = execute_purge(project_path, dispositions)

    if include_global:
        global_cleaned = clean_global_profile(project_path)
        result = result.model_copy(update={"global_cleaned": global_cleaned})

    console.print(
        f"[bold green]Purge complete[/bold green] — "
        f"{len(result.files_removed)} files, "
        f"{len(result.dirs_removed)} directories removed"
    )
    if result.files_preserved:
        console.print(
            f"[yellow]{len(result.files_preserved)} file(s) preserved "
            f"(modified)[/yellow]"
        )
    if include_global:
        status = "cleaned" if result.global_cleaned else "no matching entry found"
        console.print(f"[dim]Global profile: {status}[/dim]")
