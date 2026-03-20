"""CLI extension discovery via entry points.

External packages register Typer command groups under the ``rai.cli.commands``
entry point group.  See ADR-039 §3 for the general entry point pattern.

Convention for consumers (e.g. rai-agent/pyproject.toml)::

    [project.entry-points."rai.cli.commands"]
    knowledge = "rai_agent.knowledge.cli:app"

Result: ``rai knowledge validate ./nodes/`` works when rai-agent is installed.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from importlib.metadata import entry_points
from typing import Any, Literal

import typer

logger = logging.getLogger(__name__)

EP_CLI_COMMANDS: str = "rai.cli.commands"


@dataclass(frozen=True)
class ExtensionInfo:
    """Result of attempting to load a CLI extension."""

    name: str
    dist: str
    status: Literal["loaded", "skipped", "error"]
    reason: str | None = None


def _dist_name(ep: Any) -> str:
    """Best-effort extraction of the distribution name for an entry point."""
    try:
        return ep.dist.name  # type: ignore[union-attr]
    except AttributeError:
        return "unknown"


def discover_cli_extensions(app: typer.Typer) -> list[ExtensionInfo]:
    """Discover and register CLI extensions from entry points.

    Scans the ``rai.cli.commands`` entry point group and registers each
    valid Typer app as a sub-command group.  Invalid or broken extensions
    are skipped with a warning.

    Returns:
        List of :class:`ExtensionInfo` describing what was found.
    """
    results: list[ExtensionInfo] = []

    for ep in entry_points(group=EP_CLI_COMMANDS):
        dist = _dist_name(ep)

        # Load the entry point
        try:
            ext_app: Any = ep.load()
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "Skipping CLI extension '%s' from '%s': %s",
                ep.name,
                dist,
                exc,
            )
            results.append(
                ExtensionInfo(name=ep.name, dist=dist, status="error", reason=str(exc))
            )
            continue

        # Validate type
        if not isinstance(ext_app, typer.Typer):
            reason = f"expected Typer app, got {type(ext_app).__name__}"
            logger.warning(
                "Skipping CLI extension '%s' from '%s': %s",
                ep.name,
                dist,
                reason,
            )
            results.append(
                ExtensionInfo(name=ep.name, dist=dist, status="skipped", reason=reason)
            )
            continue

        # Register
        app.add_typer(ext_app, name=ep.name)
        logger.debug("Loaded CLI extension '%s' from '%s'", ep.name, dist)
        results.append(ExtensionInfo(name=ep.name, dist=dist, status="loaded"))

    return results
