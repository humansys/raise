"""CLI commands for adapter discovery and validation.

Provides `rai adapters list` and `rai adapters check` for inspecting
registered adapter entry points and validating Protocol compliance.

Architecture: ADR-033 (PM), ADR-034 (Governance), ADR-036 (Graph Backend)
"""

from __future__ import annotations

import inspect
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
)
from rai_cli.tier.context import TierContext
from rai_core.graph.backends.protocol import KnowledgeGraphBackend

adapters_app = typer.Typer(
    name="adapters",
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
        $ rai adapters list
        $ rai adapters list --format json
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
        $ rai adapters check
        $ rai adapters check --format json
    """
    results: list[dict[str, Any]] = []
    emitter = create_emitter()

    for group, (proto_name, proto_cls) in ADAPTER_GROUPS.items():
        for ep in entry_points(group=group):
            try:
                loaded: Any = ep.load()
            except Exception as exc:  # noqa: BLE001
                emitter.emit(AdapterFailedEvent(
                    adapter_name=ep.name,
                    group=group,
                    error=str(exc),
                ))
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
                emitter.emit(AdapterLoadedEvent(
                    adapter_name=ep.name,
                    group=group,
                    adapter_type=type(loaded).__name__,
                ))
            else:
                emitter.emit(AdapterFailedEvent(
                    adapter_name=ep.name,
                    group=group,
                    error=error or "",
                ))
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
