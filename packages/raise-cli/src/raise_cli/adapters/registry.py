"""Entry point registry for adapter discovery.

Discovers adapter implementations registered via Python entry points
(``[project.entry-points]`` in pyproject.toml). Each group maps to a
Protocol contract from ``raise_cli.adapters.protocols``.

Trust model: entry point loading inherits the ``pip install`` trust boundary.
If a package is installed in the environment, its entry points are trusted.
There is no allowlist or sandboxing — this is consistent with how pytest,
stevedore, and the broader Python ecosystem handle plugin discovery.

Architecture: ADR-033 (PM), ADR-034 (Governance), ADR-036 (Graph Backend)
"""

from __future__ import annotations

import inspect
import logging
from importlib.metadata import entry_points
from typing import Any

logger = logging.getLogger(__name__)

# Entry point group names — stable contract for external packages.
EP_PM_ADAPTERS: str = "rai.adapters.pm"
EP_GOVERNANCE_SCHEMAS: str = "rai.governance.schemas"
EP_GOVERNANCE_PARSERS: str = "rai.governance.parsers"
EP_DOC_TARGETS: str = "rai.docs.targets"
EP_GRAPH_BACKENDS: str = "rai.graph.backends"

# Session protocol entry point groups (ADR-038)
EP_STATE_DERIVERS: str = "rai.session.state_deriver"
EP_SESSION_REGISTRIES: str = "rai.session.registry"
EP_WORKSTREAM_MONITORS: str = "rai.session.monitor"


def _dist_name(ep: Any) -> str:
    """Best-effort extraction of the distribution name that provides an entry point."""
    try:
        return ep.dist.name  # type: ignore[union-attr]
    except AttributeError:
        return "unknown"


def _discover(group: str) -> dict[str, type]:
    """Load all entry points for a group. Skips broken or non-class ones with warning."""
    result: dict[str, type] = {}
    for ep in entry_points(group=group):
        try:
            loaded: Any = ep.load()
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "Skipping entry point '%s' from '%s' in group '%s': %s",
                ep.name,
                _dist_name(ep),
                group,
                exc,
            )
            continue
        if not inspect.isclass(loaded):
            logger.warning(
                "Skipping entry point '%s' from '%s' in group '%s': expected a class, got %s",
                ep.name,
                _dist_name(ep),
                group,
                type(loaded).__name__,
            )
            continue
        result[ep.name] = loaded
    return result


def get_pm_adapters() -> dict[str, type]:
    """Discover ProjectManagementAdapter implementations."""
    return _discover(EP_PM_ADAPTERS)


def get_governance_schemas() -> dict[str, type]:
    """Discover GovernanceSchemaProvider implementations."""
    return _discover(EP_GOVERNANCE_SCHEMAS)


def get_governance_parsers() -> dict[str, type]:
    """Discover GovernanceParser implementations."""
    return _discover(EP_GOVERNANCE_PARSERS)


def get_doc_targets() -> dict[str, type]:
    """Discover DocumentationTarget implementations."""
    return _discover(EP_DOC_TARGETS)


def get_graph_backends() -> dict[str, type]:
    """Discover KnowledgeGraphBackend implementations."""
    return _discover(EP_GRAPH_BACKENDS)


# Session protocol discovery (ADR-038)


def get_state_derivers() -> dict[str, type]:
    """Discover StateDeriver implementations."""
    return _discover(EP_STATE_DERIVERS)


def get_session_registries() -> dict[str, type]:
    """Discover SessionRegistry implementations."""
    return _discover(EP_SESSION_REGISTRIES)


def get_workstream_monitors() -> dict[str, type]:
    """Discover WorkstreamMonitor implementations."""
    return _discover(EP_WORKSTREAM_MONITORS)
