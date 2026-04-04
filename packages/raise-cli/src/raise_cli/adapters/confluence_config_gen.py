"""Confluence config generator — pure functions producing valid config dicts.

Takes SpaceInfo list from v2 discovery + user selections, returns a dict
that passes ConfluenceConfig.from_dict() validation. No side effects.

RAISE-1059 (S1051.6)
"""

from __future__ import annotations

from typing import Any

from raise_cli.adapters.confluence_config import ArtifactRouting
from raise_cli.adapters.models.docs import SpaceInfo

# Default routing for common artifact types when none provided
_DEFAULT_ROUTING: dict[str, ArtifactRouting] = {
    "adr": ArtifactRouting(parent_title="Architecture", labels=["adr", "architecture"]),
    "developer": ArtifactRouting(
        parent_title="Developer Docs", labels=["developer-docs"]
    ),
}


def generate_confluence_config(
    spaces: list[SpaceInfo],
    selected_space: str,
    instance_url: str,
    instance_name: str = "default",
    routing: dict[str, ArtifactRouting] | None = None,
) -> dict[str, Any]:
    """Generate a Confluence config dict from discovery data.

    Args:
        spaces: Discovered spaces from ConfluenceDiscoveryService.discover_spaces().
        selected_space: Space key chosen by the user.
        instance_url: Confluence base URL (e.g. "https://x.atlassian.net/wiki").
        instance_name: Logical instance identifier (defaults to "default").
        routing: Optional artifact routing overrides. Defaults provided if None.

    Returns:
        Dict matching ConfluenceConfig multi-instance format.

    Raises:
        ValueError: If selected_space is not in the spaces list.
    """
    space_keys = {s.key for s in spaces}
    if selected_space not in space_keys:
        available = ", ".join(sorted(space_keys))
        msg = f"Space '{selected_space}' not found. Available: {available}"
        raise ValueError(msg)

    effective_routing = routing if routing is not None else _DEFAULT_ROUTING

    routing_dict: dict[str, dict[str, Any]] = {
        name: {
            "parent_title": r.parent_title,
            "labels": r.labels,
        }
        for name, r in effective_routing.items()
    }

    return {
        "default_instance": instance_name,
        "instances": {
            instance_name: {
                "url": instance_url,
                "space_key": selected_space,
                "instance_name": instance_name,
                "routing": routing_dict,
            },
        },
    }
