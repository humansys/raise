"""CLI commands for adapter discovery and validation.

Provides `rai adapter list`, `rai adapter check`, `rai adapter validate`,
and `rai adapter status` for inspecting, checking, and validating adapter
configurations.

Architecture: ADR-033 (PM), ADR-034 (Governance), ADR-036 (Graph Backend), ADR-041 (Declarative)
"""

from __future__ import annotations

import inspect
import os
from importlib.metadata import entry_points
from pathlib import Path
from typing import Annotated, Any

import typer
from rich.console import Console

from rai_cli.adapters.protocols import (
    DocumentationTarget,
    GovernanceParser,
    GovernanceSchemaProvider,
    ProjectManagementAdapter,
)
from rai_cli.adapters.registry import (
    EP_DOC_TARGETS,
    EP_GOVERNANCE_PARSERS,
    EP_GOVERNANCE_SCHEMAS,
    EP_GRAPH_BACKENDS,
    EP_PM_ADAPTERS,
)
from rai_cli.hooks.emitter import create_emitter
from rai_cli.hooks.events import AdapterFailedEvent, AdapterLoadedEvent
from rai_cli.output.formatters.adapters import (
    format_check_human,
    format_check_json,
    format_list_human,
    format_list_json,
    format_validate_human,
)
from rai_cli.tier.context import TierContext
from raise_core.graph.backends.protocol import KnowledgeGraphBackend

adapters_app = typer.Typer(
    name="adapter",
    help="Inspect and validate registered adapters",
    no_args_is_help=True,
)

console = Console()

# Group → (Protocol display name, Protocol class).
# Only consumer of this mapping — lives here per arch review Q1.
ADAPTER_GROUPS: dict[str, tuple[str, type]] = {
    EP_GOVERNANCE_PARSERS: ("GovernanceParser", GovernanceParser),
    EP_GRAPH_BACKENDS: ("KnowledgeGraphBackend", KnowledgeGraphBackend),
    EP_PM_ADAPTERS: ("ProjectManagementAdapter", ProjectManagementAdapter),
    EP_GOVERNANCE_SCHEMAS: ("GovernanceSchemaProvider", GovernanceSchemaProvider),
    EP_DOC_TARGETS: ("DocumentationTarget", DocumentationTarget),
}


def _get_dist_name(ep: Any) -> str:
    """Best-effort extraction of distribution name from an entry point."""
    try:
        return ep.dist.name  # type: ignore[union-attr]
    except AttributeError:
        return "unknown"


def _collect_groups() -> list[dict[str, Any]]:
    """Collect adapter info for all entry point groups."""
    groups: list[dict[str, Any]] = []
    for group, (proto_name, _proto_cls) in ADAPTER_GROUPS.items():
        adapters: list[dict[str, str]] = []
        for ep in entry_points(group=group):
            adapters.append({"name": ep.name, "package": _get_dist_name(ep)})
        groups.append(
            {
                "group": group,
                "protocol_name": proto_name,
                "adapters": adapters,
            }
        )
    return groups


def _get_tier() -> str:
    """Get current tier level string."""
    ctx = TierContext.from_manifest(Path.cwd())
    return ctx.tier.value


@adapters_app.command("list")
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
    """List all registered adapters by entry point group.

    Shows each entry point group with its registered adapters and
    their source package.

    Examples:
        $ rai adapter list
        $ rai adapter list --format json
    """
    tier = _get_tier()
    groups = _collect_groups()

    if format == "json":
        typer.echo(format_list_json(tier, groups))
    else:
        format_list_human(tier, groups, console)


@adapters_app.command("check")
def check_command(
    format: Annotated[
        str,
        typer.Option(
            "--format",
            "-f",
            help="Output format: human or json",
        ),
    ] = "human",
) -> None:
    """Validate adapters against their Protocol contracts.

    Loads each registered adapter and checks compliance via isinstance()
    against its corresponding @runtime_checkable Protocol.

    Examples:
        $ rai adapter check
        $ rai adapter check --format json
    """
    results: list[dict[str, Any]] = []
    emitter = create_emitter()

    for group, (proto_name, proto_cls) in ADAPTER_GROUPS.items():
        for ep in entry_points(group=group):
            try:
                loaded: Any = ep.load()
            except Exception as exc:  # noqa: BLE001
                emitter.emit(
                    AdapterFailedEvent(
                        adapter_name=ep.name,
                        group=group,
                        error=str(exc),
                    )
                )
                results.append(
                    {
                        "group": group,
                        "name": ep.name,
                        "package": _get_dist_name(ep),
                        "protocol_name": proto_name,
                        "compliant": False,
                        "error": f"Failed to load: {exc}",
                    }
                )
                continue

            compliant = inspect.isclass(loaded) and issubclass(loaded, proto_cls)
            error = None if compliant else f"Not a {proto_name} subclass"
            if compliant:
                emitter.emit(
                    AdapterLoadedEvent(
                        adapter_name=ep.name,
                        group=group,
                        adapter_type=type(loaded).__name__,
                    )
                )
            else:
                emitter.emit(
                    AdapterFailedEvent(
                        adapter_name=ep.name,
                        group=group,
                        error=error or "",
                    )
                )
            results.append(
                {
                    "group": group,
                    "name": ep.name,
                    "package": _get_dist_name(ep),
                    "protocol_name": proto_name,
                    "compliant": compliant,
                    "error": error,
                }
            )

    if format == "json":
        typer.echo(format_check_json(results))
    else:
        format_check_human(results, console)


@adapters_app.command("validate")
def validate_command(
    file: Annotated[
        Path,
        typer.Argument(help="Path to YAML adapter config file"),
    ],
) -> None:
    """Validate a declarative YAML adapter config.

    Checks that the YAML file conforms to the DeclarativeAdapterConfig
    schema. Reports adapter name, protocol, and method counts on success,
    or specific field errors on failure.

    Examples:
        $ rai adapter validate .raise/adapters/github.yaml
        $ rai adapter validate my-adapter.yaml
    """
    import yaml
    from pydantic import ValidationError

    from rai_cli.adapters.declarative.schema import DeclarativeAdapterConfig

    if not file.exists():
        console.print(f"[red]Error:[/red] File not found: {file}")
        raise typer.Exit(1)

    try:
        raw = yaml.safe_load(file.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        console.print(f"[red]✗ Invalid adapter config:[/red] {file.name}")
        console.print(f"  Cannot parse YAML: {exc}")
        raise typer.Exit(1) from None

    if not isinstance(raw, dict):
        console.print(f"[red]✗ Invalid adapter config:[/red] {file.name}")
        console.print("  YAML content is not a mapping")
        raise typer.Exit(1)

    try:
        config = DeclarativeAdapterConfig.model_validate(raw)
    except ValidationError as exc:
        console.print(f"[red]✗ Invalid adapter config:[/red] {file.name}")
        for err in exc.errors():
            loc = ".".join(str(p) for p in err["loc"])
            console.print(f"  {loc}")
            console.print(f"    {err['msg']}")
        raise typer.Exit(1) from None

    format_validate_human(config, console)


# ---------------------------------------------------------------------------
# rai adapter status — show configuration status for known adapters
# ---------------------------------------------------------------------------

# Jira env var names expected by McpJiraAdapter._create_bridge
_JIRA_ENV_VARS: list[tuple[str, str]] = [
    ("JIRA_URL", "Jira instance URL"),
    ("JIRA_USERNAME", "Jira user email"),
    ("JIRA_API_TOKEN", "Jira API token (or JIRA_TOKEN)"),
]


def _check_jira_config(project_root: Path) -> dict[str, Any]:
    """Collect Jira adapter configuration status.

    Returns a dict with keys: yaml_path, yaml_exists, env_vars (list of
    dicts with name, set, description), and ready (bool).
    """
    yaml_path = project_root / ".raise" / "jira.yaml"
    env_results: list[dict[str, Any]] = []
    for var_name, description in _JIRA_ENV_VARS:
        if var_name == "JIRA_API_TOKEN":
            is_set = bool(os.environ.get("JIRA_API_TOKEN") or os.environ.get("JIRA_TOKEN"))
        else:
            is_set = bool(os.environ.get(var_name))
        env_results.append({"name": var_name, "set": is_set, "description": description})

    all_env_set = all(e["set"] for e in env_results)
    return {
        "yaml_path": str(yaml_path),
        "yaml_exists": yaml_path.exists(),
        "env_vars": env_results,
        "ready": yaml_path.exists() and all_env_set,
    }


@adapters_app.command("status")
def status_command(
    format: Annotated[
        str,
        typer.Option(
            "--format",
            "-f",
            help="Output format: human or json",
        ),
    ] = "human",
) -> None:
    """Show configuration status for known adapters.

    Checks that required config files exist and environment variables
    are set. Useful for verifying setup after configuring an adapter.

    Examples:
        $ rai adapter status
        $ rai adapter status --format json
    """
    import json as json_mod

    project_root = Path.cwd()
    jira_status = _check_jira_config(project_root)

    if format == "json":
        typer.echo(json_mod.dumps({"jira": jira_status}, indent=2))
        return

    console.print("[bold]Adapter Configuration Status[/bold]\n")

    # --- Jira ---
    console.print("[bold]Jira[/bold]")

    yaml_path = jira_status["yaml_path"]
    if jira_status["yaml_exists"]:
        console.print(f"  [green]\u2713[/green] Config: {yaml_path}")
    else:
        console.print(f"  [red]\u2717[/red] Config: {yaml_path} [red](not found)[/red]")
        console.print(
            "    [dim]Create .raise/jira.yaml with status_mapping and project config.[/dim]"
        )

    for env_var in jira_status["env_vars"]:
        if env_var["set"]:
            console.print(f"  [green]\u2713[/green] {env_var['name']}: set")
        else:
            console.print(
                f"  [red]\u2717[/red] {env_var['name']}: [red]not set[/red]"
                f"  [dim]({env_var['description']})[/dim]"
            )

    console.print()
    if jira_status["ready"]:
        console.print("[green]Jira adapter is fully configured.[/green]")
    else:
        missing: list[str] = []
        if not jira_status["yaml_exists"]:
            missing.append(".raise/jira.yaml")
        for env_var in jira_status["env_vars"]:
            if not env_var["set"]:
                missing.append(env_var["name"])
        console.print(
            f"[yellow]Jira adapter is not ready.[/yellow] Missing: {', '.join(missing)}"
        )
        console.print(
            "\n[dim]Set env vars in .env or shell. "
            "See CLAUDE.md 'Jira Access' section for details.[/dim]"
        )
