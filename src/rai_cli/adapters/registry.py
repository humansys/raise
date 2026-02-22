"""Entry point registry for adapter discovery.

Discovers adapter implementations registered via Python entry points
(``[project.entry-points]`` in pyproject.toml). Each group maps to a
Protocol contract from ``rai_cli.adapters.protocols``.

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


def _discover(group: str) -> dict[str, type]:
    """Load all entry points for a group. Skips broken or non-class ones with warning."""
    result: dict[str, type] = {}
    for ep in entry_points(group=group):
        try:
            loaded: Any = ep.load()
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "Skipping entry point '%s' in group '%s': %s", ep.name, group, exc
            )
            continue
        if not inspect.isclass(loaded):
            logger.warning(
                "Skipping entry point '%s' in group '%s': expected a class, got %s",
                ep.name,
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
