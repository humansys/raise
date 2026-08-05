"""CLI commands for interactive adapter setup.

Provides `rai adapter setup jira` (and later `confluence`) for guided
adapter configuration using live discovery.

S1604.1 (E1604)
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any, cast

import typer
import yaml
from rich.console import Console

from raise_cli.adapters.confluence_client import ConfluenceClient
from raise_cli.adapters.confluence_config import (
    ConfluenceInstanceConfig,
    load_docs_config,
)
from raise_cli.adapters.confluence_config_gen import (
    build_routing_from_preset,
    generate_confluence_config,
    suggest_routing,
    write_confluence_config,
)
from raise_cli.adapters.confluence_discovery import ConfluenceDiscoveryService
from raise_cli.adapters.jira_client import JiraClient
from raise_cli.adapters.jira_config_gen import (
    add_org_to_jira_config,
    generate_jira_config,
    write_jira_config,
)
from raise_cli.adapters.jira_discovery import JiraDiscovery
from raise_cli.output.symbols import CHECK, CROSS

setup_app = typer.Typer(
    name="setup",
    help="Interactive adapter configuration",
    no_args_is_help=True,
)

console = Console()


def _check_env_var(name: str) -> str | None:
    """Return env var value or None."""
    return os.environ.get(name)


def _check_jira_credentials() -> tuple[str, str]:
    """Check Jira credentials and exit with guidance if missing.

    Returns:
        Tuple of (token, username).

    Raises:
        typer.Exit: If credentials are missing.
    """
    console.print("\nChecking credentials...")

    token = _check_env_var("JIRA_API_TOKEN")
    if not token:
        console.print(f"  {CROSS} JIRA_API_TOKEN not found\n")
        console.print("Set the following environment variables:")
        console.print('  export JIRA_API_TOKEN="your-api-token"')
        console.print('  export JIRA_USERNAME="your-email@company.com"')
        console.print(
            "\nGenerate a token at: "
            "https://id.atlassian.com/manage-profile/security/api-tokens"
        )
        raise typer.Exit(1)

    username = _check_env_var("JIRA_USERNAME")
    if not username:
        console.print(f"  {CHECK} JIRA_API_TOKEN found")
        console.print(f"  {CROSS} JIRA_USERNAME not found\n")
        console.print("Set the following environment variable:")
        console.print('  export JIRA_USERNAME="your-email@company.com"')
        raise typer.Exit(1)

    console.print(f"  {CHECK} JIRA_API_TOKEN found")
    console.print(f"  {CHECK} JIRA_USERNAME found")
    return token, username


def _require_interactive_terminal() -> None:
    """Refuse non-TTY stdin with a clear error.

    Adapter setup is multi-prompt + project selection; piping stdin (or
    invoking from a non-interactive context) corrupts prompts. On Windows
    + non-TTY, rich.Prompt has been observed to prepend a BOM (U+FEFF) to
    default values, producing invalid IDNA labels in URLs (RAISE-3744).
    Refusing up front gives a clear actionable error instead of failing
    deep in URL construction.
    """
    if sys.platform == "win32" and not sys.stdin.isatty():
        console.print(
            "[red]Adapter setup requires an interactive terminal.[/red] "
            "Stdin is not a TTY (looks like piped input or a non-interactive "
            "shell). Run this command directly in a terminal — it cannot be "
            "scripted via stdin pipes today."
        )
        raise typer.Exit(2)


def _sanitize_prompt(value: str) -> str:
    """Strip BOM (U+FEFF) and surrounding whitespace from prompt input.

    Defense in depth for RAISE-3744: even if a non-TTY case slips past the
    isatty guard (or appears under a different rendering path), strip the
    BOM character so URL construction does not blow up with IDNA errors.
    Removes BOM anywhere in the string (it is never a meaningful character
    in user-typed Atlassian site/instance names) and trims surrounding
    whitespace.
    """
    return value.replace("﻿", "").strip()


def _prompt_site_and_instance() -> tuple[str, str]:
    """Prompt for Atlassian site domain and instance name.

    Returns:
        Tuple of (site, instance_name).
    """
    site_raw: str = typer.prompt("\nAtlassian site", default="")
    site = _sanitize_prompt(site_raw)
    if not site:
        console.print("[red]Site domain is required.[/red]")
        raise typer.Exit(1)

    # Default instance name from site subdomain
    default_instance = site.split(".")[0] if "." in site else site
    instance_name_raw: str = typer.prompt("Instance name", default=default_instance)
    instance_name = _sanitize_prompt(instance_name_raw)
    return site, instance_name


def _discover_projects(
    site: str, username: str, token: str
) -> Any:  # Returns JiraProjectMap
    """Run Jira discovery and return project map."""
    console.print("\nDiscovering projects...")
    client = JiraClient(url=f"https://{site}", username=username, token=token)
    discovery = JiraDiscovery(client)
    project_map = discovery.discover()

    if not project_map.projects:
        console.print("[red]No projects found. Check permissions.[/red]")
        raise typer.Exit(1)

    console.print(f"Found {len(project_map.projects)} projects:")
    for p in project_map.projects:
        console.print(f"  {p.key:<12} {p.name}")

    return project_map


def _prompt_project_selection(available_keys: list[str]) -> list[str]:
    """Prompt user to select projects from discovered list.

    Returns:
        List of selected project keys.
    """
    raw: str = typer.prompt(
        "\nInclude projects (comma-separated, or 'all')", default="all"
    )
    if raw.strip().lower() == "all":
        return available_keys

    selected = [k.strip().upper() for k in raw.split(",") if k.strip()]
    invalid = [k for k in selected if k not in available_keys]
    if invalid:
        console.print(f"[red]Unknown projects: {', '.join(invalid)}[/red]")
        console.print(f"Available: {', '.join(available_keys)}")
        raise typer.Exit(1)

    return selected


def _preview_and_confirm(config_dict: dict[str, Any], filename: str) -> bool:
    """Show YAML preview and ask for write confirmation.

    Returns:
        True if user confirms write.
    """
    console.print("\nPreview:")
    console.print("─" * 40)
    console.print(yaml.dump(config_dict, default_flow_style=False, sort_keys=False))
    console.print("─" * 40)

    return typer.confirm(f"Write to .raise/{filename}?", default=False)


def _write_jira_result(
    config_dict: dict[str, Any],
    *,
    add_org_mode: bool,
    project_root: Path,
) -> Path:
    """Write Jira config, merging if add_org_mode, overwriting otherwise.

    Raises typer.Exit(1) on ValueError (org collision in merge mode).
    """
    if add_org_mode:
        try:
            return add_org_to_jira_config(config_dict, project_root=project_root)
        except ValueError as exc:
            console.print(f"[red]Error:[/red] {exc}")
            raise typer.Exit(1) from exc
    return write_jira_config(config_dict, project_root=project_root, overwrite=True)


@setup_app.command("jira")
def setup_jira(
    overwrite: bool = typer.Option(
        False, "--overwrite", help="Overwrite existing config"
    ),
    site: str | None = typer.Option(None, "--site", help="Atlassian site domain"),
    instance: str | None = typer.Option(
        None, "--instance", help="Logical instance name (legacy; prefer --org)"
    ),
    org: str | None = typer.Option(
        None,
        "--org",
        help="Logical org name — adds org to existing backlog.yaml without overwriting (RAISE-6248)",
    ),
    projects: str | None = typer.Option(
        None, "--projects", help="Comma-separated project keys (non-interactive)"
    ),
    yes: bool = typer.Option(False, "--yes", help="Skip confirmations"),
) -> None:
    """Configure the Jira adapter (interactive or non-interactive).

    Interactive mode (no flags): guided prompts for site, instance, projects.
    Non-interactive mode (--site + --instance + --projects + --yes): no TTY needed.

    Use --org instead of --instance to ADD a new org to an existing config
    without overwriting the current setup (multi-org, RAISE-6248).

    Requires JIRA_API_TOKEN and JIRA_USERNAME environment variables.

    Examples:
        $ rai adapter setup jira
        $ rai adapter setup jira --overwrite
        $ rai adapter setup jira --site x.atlassian.net --instance x --projects RAISE --yes
        $ rai adapter setup jira --site y.atlassian.net --org y --projects PROJ --yes
    """
    # --org takes priority over --instance; enables merge mode
    org_name = org or instance
    add_org_mode = org is not None  # merge-into-existing semantics
    non_interactive = all([site, org_name, projects])

    if not non_interactive:
        _require_interactive_terminal()

    # Step 1: Check credentials
    token, username = _check_jira_credentials()

    # Step 2: Check existing config (skip for add-org mode — we're merging, not replacing)
    config_path = Path.cwd() / ".raise" / "backlog.yaml"
    if not add_org_mode and (
        config_path.exists()
        and not overwrite
        and not (non_interactive and yes)
        and not typer.confirm(
            f"\n{config_path} already exists. Overwrite?", default=False
        )
    ):
        console.print("Aborted.")
        raise typer.Exit(0)

    # Step 3: Resolve site, instance, and project selection
    if non_interactive:
        site_val = cast("str", site)
        instance_name = cast("str", org_name)
        projects_val = cast("str", projects)
    else:
        site_val, instance_name = _prompt_site_and_instance()
        projects_val = ""

    # Step 4: Discover projects
    project_map = _discover_projects(site_val, username, token)
    available_keys = [p.key for p in project_map.projects]

    # Step 5: Select projects
    if non_interactive:
        selected = [k.strip().upper() for k in projects_val.split(",") if k.strip()]
        invalid = [k for k in selected if k not in available_keys]
        if invalid:
            console.print(f"[red]Unknown projects: {', '.join(invalid)}[/red]")
            console.print(f"Available: {', '.join(available_keys)}")
            raise typer.Exit(1)
    else:
        selected = _prompt_project_selection(available_keys)

    # Step 6: Generate config
    config_dict = generate_jira_config(
        project_map=project_map,
        selected_projects=selected,
        instance_name=instance_name,
        site=site_val,
    )

    # Step 7: Preview and confirm
    if non_interactive and yes:
        result_path = _write_jira_result(
            config_dict, add_org_mode=add_org_mode, project_root=Path.cwd()
        )
        console.print(f"\n{CHECK} Written to {result_path}")
        return

    if not _preview_and_confirm(config_dict, "backlog.yaml"):
        console.print("Aborted.")
        return

    # Step 8: Write
    result_path = _write_jira_result(
        config_dict, add_org_mode=add_org_mode, project_root=Path.cwd()
    )
    console.print(f"\n{CHECK} Written to {result_path}")


# ── Confluence setup (S1604.2) ─────────────────────────────────────


def _check_confluence_credentials() -> tuple[str, str]:
    """Check Confluence credentials and exit with guidance if missing.

    Returns:
        Tuple of (token, username).

    Raises:
        typer.Exit: If credentials are missing.
    """
    console.print("\nChecking credentials...")

    token = _check_env_var("CONFLUENCE_API_TOKEN")
    if not token:
        console.print(f"  {CROSS} CONFLUENCE_API_TOKEN not found\n")
        console.print("Set the following environment variables:")
        console.print('  export CONFLUENCE_API_TOKEN="your-api-token"')
        console.print('  export CONFLUENCE_USERNAME="your-email@company.com"')
        console.print(
            "\nGenerate a token at: "
            "https://id.atlassian.com/manage-profile/security/api-tokens"
        )
        raise typer.Exit(1)

    username = _check_env_var("CONFLUENCE_USERNAME")
    if not username:
        console.print(f"  {CHECK} CONFLUENCE_API_TOKEN found")
        console.print(f"  {CROSS} CONFLUENCE_USERNAME not found\n")
        console.print("Set the following environment variable:")
        console.print('  export CONFLUENCE_USERNAME="your-email@company.com"')
        raise typer.Exit(1)

    console.print(f"  {CHECK} CONFLUENCE_API_TOKEN found")
    console.print(f"  {CHECK} CONFLUENCE_USERNAME found")
    return token, username


def _discover_spaces(site: str) -> tuple[ConfluenceDiscoveryService, list[Any]]:
    """Run Confluence discovery and return service + spaces list."""
    console.print("\nDiscovering spaces...")
    inst = ConfluenceInstanceConfig(
        url=f"https://{site}/wiki",
        space_key="",  # not needed for discovery
    )
    client = ConfluenceClient(inst)
    discovery = ConfluenceDiscoveryService(client)
    spaces = discovery.discover_spaces()

    if not spaces:
        console.print("[red]No spaces found. Check permissions.[/red]")
        raise typer.Exit(1)

    console.print(f"Found {len(spaces)} spaces:")
    for s in spaces:
        console.print(f"  {s.key:<12} {s.name}")

    return discovery, spaces


def _discover_routing_from_page_tree(
    discovery: ConfluenceDiscoveryService, selected_space: str
) -> tuple[dict[str, Any] | None, str | None]:
    """Try to discover routing from the space page tree.

    Returns:
        Tuple of (routing dict or None, home_page_id or None).
    """
    console.print("\nDiscovering page structure...")
    try:
        page_tree = discovery.discover_page_tree(selected_space)
        home_page_id: str | None = page_tree.id
        routing = suggest_routing(page_tree)
        if routing:
            console.print(
                f"  {CHECK} Found routing suggestions for: {', '.join(routing.keys())}"
            )
        else:
            console.print("  No routing suggestions found — using defaults")
        return routing, home_page_id
    except Exception:  # noqa: BLE001
        console.print("  [yellow]Page tree discovery failed — using defaults[/yellow]")
        return None, None


def _prompt_space_selection(available_keys: list[str]) -> str:
    """Prompt user to select a space.

    Returns:
        Selected space key.
    """
    raw: str = typer.prompt("\nSelect space", default=available_keys[0])
    normalized = raw.strip().lower()
    key = next((k for k in available_keys if k.lower() == normalized), None)

    if key is None:
        console.print(f"[red]Unknown space: {raw.strip()}[/red]")
        console.print(f"Available: {', '.join(available_keys)}")
        raise typer.Exit(1)

    return key


def _load_existing_docs_config(config_path: Path) -> dict[str, Any] | None:
    """Load existing docs.yaml as a raw dict for append mode. Returns None on any failure."""
    try:
        docs = load_docs_config(config_path.parent.parent)
        return {"default_target": docs.default_target, "targets": dict(docs.targets)}
    except Exception:  # noqa: BLE001
        return None


@setup_app.command("confluence")
def setup_confluence(
    overwrite: bool = typer.Option(
        False, "--overwrite", help="Overwrite existing config"
    ),
    site: str | None = typer.Option(None, "--site", help="Atlassian site domain"),
    instance: str | None = typer.Option(
        None, "--instance", help="Logical instance name"
    ),
    space: str | None = typer.Option(
        None, "--space", help="Space key (non-interactive)"
    ),
    yes: bool = typer.Option(False, "--yes", help="Skip confirmations"),
    structure: str | None = typer.Option(
        None,
        "--structure",
        help="Routing preset to inject ('raise' for full RaiSE routing).",
    ),
    append: bool = typer.Option(
        False,
        "--append",
        help="Add or update a target without overwriting existing ones.",
    ),
) -> None:
    """Configure the Confluence adapter (interactive or non-interactive).

    Interactive mode (no flags): guided prompts for site, instance, space.
    Non-interactive mode (--site + --instance + --space + --yes): no TTY needed.

    Requires CONFLUENCE_API_TOKEN and CONFLUENCE_USERNAME environment variables.

    Examples:
        $ rai adapter setup confluence
        $ rai adapter setup confluence --overwrite
        $ rai adapter setup confluence --site x.atlassian.net --instance x --space RAISE --yes
    """
    non_interactive = all([site, instance, space])

    if not non_interactive:
        _require_interactive_terminal()

    # Step 1: Check credentials
    _check_confluence_credentials()

    # Step 2: Check existing config
    config_path = Path.cwd() / ".raise" / "docs.yaml"
    if not append and (
        config_path.exists()
        and not overwrite
        and not (non_interactive and yes)
        and not typer.confirm(
            f"\n{config_path} already exists. Overwrite?", default=False
        )
    ):
        console.print("Aborted.")
        raise typer.Exit(0)

    # Step 2b: Load existing config for append mode
    existing_config = (
        _load_existing_docs_config(config_path)
        if append and config_path.exists()
        else None
    )

    # Step 3: Resolve site, instance, and space
    if non_interactive:
        site_val = cast("str", site)
        instance_name = cast("str", instance)
        space_input = cast("str", space).strip()
    else:
        site_val, instance_name = _prompt_site_and_instance()
        space_input = ""

    # Step 4: Discover spaces
    discovery, spaces = _discover_spaces(site_val)
    available_keys = [s.key for s in spaces]

    # Step 5: Select space
    if non_interactive:
        normalized = space_input.lower()
        selected_space = next(
            (k for k in available_keys if k.lower() == normalized), None
        )
        if selected_space is None:
            console.print(f"[red]Unknown space: {space_input}[/red]")
            console.print(f"Available: {', '.join(available_keys)}")
            raise typer.Exit(1)
    else:
        selected_space = _prompt_space_selection(available_keys)

    # Step 6: Routing — always discover home_page_id; preset or page-tree for routing
    routing, home_page_id = _discover_routing_from_page_tree(discovery, selected_space)

    if structure is not None:
        try:
            routing = build_routing_from_preset(structure)
        except ValueError as exc:
            console.print(f"[red]{exc}[/red]")
            raise typer.Exit(1) from exc
        console.print(
            f"  {CHECK} Injecting RaiSE routing preset ({len(routing)} artifact types)"
        )

    # Step 7: Generate config
    config_dict = generate_confluence_config(
        spaces=spaces,
        selected_space=selected_space,
        instance_url=f"https://{site_val}/wiki",
        instance_name=instance_name,
        routing=routing if routing else None,
        home_page_id=home_page_id,
        existing_config=existing_config,
    )

    # Step 8: Preview and confirm
    if non_interactive and yes:
        result_path = write_confluence_config(
            config_dict, project_root=Path.cwd(), overwrite=True
        )
        console.print(f"\n{CHECK} Written to {result_path}")
        return

    if not _preview_and_confirm(config_dict, "docs.yaml"):
        console.print("Aborted.")
        return

    # Step 9: Write
    result_path = write_confluence_config(
        config_dict, project_root=Path.cwd(), overwrite=True
    )
    console.print(f"\n{CHECK} Written to {result_path}")


# ── Auto setup (S6277.5) ─────────────────────────────────────────────


def _require_env(name: str) -> str:
    """Return env var value or raise typer.Exit with guidance."""
    val = os.environ.get(name)
    if not val:
        console.print(f"[red]{CROSS} Missing required env var: {name}[/red]")
        raise typer.Exit(1)
    return val


def _normalize_site(url: str) -> str:
    """Strip protocol prefix and trailing /wiki from URL, returning bare domain."""
    for prefix in ("https://", "http://"):
        url = url.removeprefix(prefix)
    url = url.rstrip("/")
    url = url.removesuffix("/wiki")
    return url


def _site_to_instance(site: str) -> str:
    """Derive instance name from site domain."""
    return site.split(".")[0] if "." in site else site


def _auto_jira(force: bool) -> bool:
    """Run Jira auto-setup. Returns True on success."""
    site = _normalize_site(_require_env("JIRA_URL"))
    token = _require_env("JIRA_API_TOKEN")
    username = _require_env("JIRA_USERNAME")

    config_path = Path.cwd() / ".raise" / "backlog.yaml"
    if config_path.exists() and not force:
        console.print(
            f"[red]{CROSS} {config_path} already exists.[/red] "
            "Use --force to overwrite."
        )
        raise typer.Exit(1)

    instance_name = _site_to_instance(site)
    console.print(f"{CHECK} Detected Jira site: {site}")

    project_map = _discover_projects(site, username, token)
    selected = [p.key for p in project_map.projects]

    config_dict = generate_jira_config(
        project_map=project_map,
        selected_projects=selected,
        instance_name=instance_name,
        site=site,
    )
    result_path = write_jira_config(
        config_dict, project_root=Path.cwd(), overwrite=True
    )
    console.print(f"{CHECK} Written {result_path}")
    return True


def _auto_confluence(force: bool, structure: str | None) -> bool:
    """Run Confluence auto-setup. Returns True on success, False if skipped."""
    conf_url = os.environ.get("CONFLUENCE_URL")
    if not conf_url:
        console.print(
            "[yellow]⚠ Confluence: CONFLUENCE_URL not set — skipping docs adapter[/yellow]"
        )
        return False

    conf_token = os.environ.get("CONFLUENCE_API_TOKEN")
    conf_username = os.environ.get("CONFLUENCE_USERNAME")
    if not conf_token or not conf_username:
        missing = []
        if not conf_token:
            missing.append("CONFLUENCE_API_TOKEN")
        if not conf_username:
            missing.append("CONFLUENCE_USERNAME")
        console.print(
            f"[yellow]⚠ Confluence: {', '.join(missing)} not set "
            "— skipping docs adapter[/yellow]"
        )
        return False

    config_path = Path.cwd() / ".raise" / "docs.yaml"
    if config_path.exists() and not force:
        console.print(
            f"[red]{CROSS} {config_path} already exists.[/red] "
            "Use --force to overwrite."
        )
        raise typer.Exit(1)

    site = _normalize_site(conf_url)
    instance_name = _site_to_instance(site)
    console.print(f"{CHECK} Detected Confluence site: {site}")

    discovery, spaces = _discover_spaces(site)
    selected_space = spaces[0].key if spaces else ""

    routing = None
    home_page_id: str | None = None
    try:
        routing_suggested, home_page_id = _discover_routing_from_page_tree(
            discovery, selected_space
        )
        routing = routing_suggested
    except Exception:  # noqa: BLE001, S110
        pass

    if structure is not None:
        routing = build_routing_from_preset(structure)

    config_dict = generate_confluence_config(
        spaces=spaces,
        selected_space=selected_space,
        instance_url=f"https://{site}/wiki",
        instance_name=instance_name,
        routing=routing if routing else None,
        home_page_id=home_page_id,
    )
    result_path = write_confluence_config(
        config_dict, project_root=Path.cwd(), overwrite=True
    )
    console.print(f"{CHECK} Written {result_path}")
    return True


@setup_app.command("auto")
def setup_auto(
    force: bool = typer.Option(False, "--force", help="Overwrite existing configs"),
    structure: str | None = typer.Option(
        None,
        "--structure",
        help="Confluence routing preset (e.g. 'raise').",
    ),
) -> None:
    """Auto-configure adapters from environment variables (zero prompts).

    Reads JIRA_URL, JIRA_API_TOKEN, JIRA_USERNAME to configure the Jira
    adapter. Optionally reads CONFLUENCE_URL, CONFLUENCE_API_TOKEN,
    CONFLUENCE_USERNAME for the docs adapter. Missing Confluence env vars
    are non-fatal (warns and skips).

    Examples:
        $ rai adapter setup auto
        $ rai adapter setup auto --force
        $ rai adapter setup auto --structure raise
    """
    _auto_jira(force)
    _auto_confluence(force, structure)
