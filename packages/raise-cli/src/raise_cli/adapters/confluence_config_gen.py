"""Confluence config generator — pure function producing valid config dicts.

Takes ConfluenceSpaceMap from discovery + user selections, returns a dict
that passes ConfluenceConfig.from_dict() validation. No side effects.

RAISE-1130 (S1130.4)
"""

from __future__ import annotations

from typing import Any

from raise_cli.adapters.confluence_config import ArtifactRouting
from raise_cli.adapters.confluence_discovery import ConfluenceSpaceMap

# Default routing for common artifact types when none provided
_DEFAULT_ROUTING: dict[str, ArtifactRouting] = {
    "adr": ArtifactRouting(parent_title="Architecture", labels=["adr", "architecture"]),
    "developer": ArtifactRouting(
        parent_title="Developer Docs", labels=["developer-docs"]
    ),
}


def generate_confluence_config(
    space_map: ConfluenceSpaceMap,
    selected_space: str,
    instance_url: str,
    routing: dict[str, ArtifactRouting] | None = None,
) -> dict[str, Any]:
    """Generate a Confluence config dict from discovery data.

    Args:
        space_map: Discovered space structure from ConfluenceDiscovery.
        selected_space: Space key chosen by the user.
        instance_url: Confluence base URL (e.g. "https://x.atlassian.net/wiki").
        routing: Optional artifact routing overrides. Defaults provided if None.

    Returns:
        Dict matching ConfluenceConfig flat format (url, space_key, routing).

    Raises:
        ValueError: If selected_space is not in the discovery map.
    """
    space_keys = {s.key for s in space_map.spaces}
    if selected_space not in space_keys:
        msg = (
            f"Space '{selected_space}' not found in discovery map. "
            f"Available: {', '.join(sorted(space_keys))}"
        )
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
        "url": instance_url,
        "space_key": selected_space,
        "routing": routing_dict,
    }
