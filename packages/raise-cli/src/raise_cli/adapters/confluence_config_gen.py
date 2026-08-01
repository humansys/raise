"""Docs config generator — pure functions producing valid docs.yaml config dicts.

Takes SpaceInfo list from v2 discovery + user selections, returns a dict
that passes DocsConfig.model_validate() validation. No side effects.

RAISE-1059 (S1051.6), RAISE-3413 (S20.1)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from raise_cli.adapters.confluence_config import ArtifactRouting
from raise_cli.adapters.confluence_discovery import PageNode
from raise_cli.adapters.models.docs import SpaceInfo

# Default routing for common artifact types when none provided
_DEFAULT_ROUTING: dict[str, ArtifactRouting] = {
    "adr": ArtifactRouting(parent_title="Architecture", labels=["adr", "architecture"]),
    "developer": ArtifactRouting(
        parent_title="Developer Docs", labels=["developer-docs"]
    ),
}

# Governance preset — stable org-level docs: architecture records + developer docs.
_PRESET_GOVERNANCE: dict[str, list[str]] = {
    "Architecture": [
        "adr",
        "architecture-domain-model",
        "architecture-index",
        "architecture-module",
        "architecture-system-context",
        "architecture-system-design",
    ],
    "Developer Docs": [
        "project-vision",
        "project-prd",
        "project-guardrails",
        "project-backlog",
    ],
}

# Work preset — ephemeral team artifacts: epics, stories, bugs, sessions, research.
_PRESET_WORK: dict[str, list[str]] = {
    "Epics": ["epic-brief", "epic-scope", "epic-design", "epic-docs"],
    "Stories": ["story", "story-scope", "story-design", "story-plan"],
    "Bugs": ["bugfix-scope", "bugfix-analysis", "bugfix-plan", "bugfix-retro"],
    "Sessions": ["session-diary", "retrospective", "mission-retro"],
    "Research": ["research", "proposal"],
}

# Full RaiSE routing preset — all 27 artifact types, composed from work + governance.
# Validated against: grep -rh "rai docs write" .claude/skills/ | sort -u
# Parent page title keys must be disjoint between _PRESET_WORK and _PRESET_GOVERNANCE —
# if a key appears in both, _PRESET_GOVERNANCE silently wins.
RAISE_ROUTING_PRESET: dict[str, list[str]] = {**_PRESET_WORK, **_PRESET_GOVERNANCE}

_PRESET_MAP: dict[str, dict[str, list[str]]] = {
    "governance": _PRESET_GOVERNANCE,
    "raise": RAISE_ROUTING_PRESET,
    "work": _PRESET_WORK,
}


def build_routing_from_preset(structure: str) -> dict[str, ArtifactRouting]:
    """Build artifact routing from a named preset.

    Args:
        structure: Preset name. Supported: "governance", "raise", "work".

    Returns:
        Dict of artifact_type → ArtifactRouting for all types in the preset.

    Raises:
        ValueError: If structure is not a known preset name.
    """
    if structure not in _PRESET_MAP:
        msg = (
            f"Unknown structure preset: '{structure}'. Supported: {sorted(_PRESET_MAP)}"
        )
        raise ValueError(msg)
    return {
        artifact_type: ArtifactRouting(parent_title=parent, labels=[artifact_type])
        for parent, types in _PRESET_MAP[structure].items()
        for artifact_type in types
    }


def generate_confluence_config(
    spaces: list[SpaceInfo],
    selected_space: str,
    instance_url: str,
    instance_name: str = "default",
    routing: dict[str, ArtifactRouting] | None = None,
    home_page_id: str | None = None,
    existing_config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Generate a docs.yaml config dict from Confluence discovery data.

    Args:
        spaces: Discovered spaces from ConfluenceDiscoveryService.discover_spaces().
        selected_space: Space key chosen by the user.
        instance_url: Confluence base URL (e.g. "https://x.atlassian.net/wiki").
        instance_name: Logical target identifier (defaults to "default").
        routing: Optional artifact routing overrides. Defaults provided if None.
        home_page_id: Space homepage page ID, discovered from the space root.
        existing_config: When provided, upserts the new target into this config
            and returns the merged result. default_target is preserved unchanged.
            When None, returns a fresh single-target config (current behavior).

    Returns:
        Dict matching DocsConfig format (default_target/targets).

    Raises:
        ValueError: If selected_space is not in the spaces list.
    """
    space_keys = {s.key for s in spaces}
    if selected_space not in space_keys:
        available = ", ".join(sorted(space_keys))
        msg = f"Space '{selected_space}' not found. Available: {available}"
        raise ValueError(msg)

    effective_routing = routing if routing is not None else _DEFAULT_ROUTING

    routing_dict: dict[str, dict[str, Any]] = {}
    for name, r in effective_routing.items():
        entry: dict[str, Any] = {"labels": r.labels}
        if r.parent_path:
            entry["parent_path"] = r.parent_path
        else:
            entry["parent_title"] = r.parent_title
        routing_dict[name] = entry

    target: dict[str, Any] = {
        "type": "confluence",
        "url": instance_url,
        "space_key": selected_space,
        "instance_name": instance_name,
        "routing": routing_dict,
        "sync_manifest": {},
    }
    if home_page_id is not None:
        target["home_page_id"] = home_page_id

    if existing_config is None:
        return {
            "default_target": instance_name,
            "targets": {instance_name: target},
        }

    result: dict[str, Any] = {
        "default_target": existing_config["default_target"],
        "targets": dict(existing_config["targets"]),
    }
    result["targets"][instance_name] = target
    return result


# ── Routing suggestion from page tree ────────────────────────────────

# Artifact type → keywords that match top-level page titles (case-insensitive substring)
_ROUTING_KEYWORDS: dict[str, list[str]] = {
    "adr": ["architecture decision", "adr"],
    "roadmap": ["roadmap"],
    "developer": ["developer doc", "developer guide"],
    "retrospective": ["retrospective", "retro"],
}


def suggest_routing(tree: PageNode) -> dict[str, ArtifactRouting]:
    """Suggest artifact routing from top-level page titles.

    Matches each top-level child title against known artifact type keywords
    using case-insensitive substring matching. Returns a dict of artifact
    type → ArtifactRouting for each match found.

    Args:
        tree: Root PageNode whose children are top-level pages.

    Returns:
        Dict of artifact_type → ArtifactRouting for matched pages.
    """
    suggestions: dict[str, ArtifactRouting] = {}
    for child in tree.children:
        title_lower = child.title.lower()
        for artifact_type, keywords in _ROUTING_KEYWORDS.items():
            if artifact_type in suggestions:
                continue  # already matched this type
            for keyword in keywords:
                if keyword in title_lower:
                    suggestions[artifact_type] = ArtifactRouting(
                        parent_title=child.title,
                        labels=[artifact_type],
                    )
                    break
    return suggestions


# ── YAML writer ──────────────────────────────────────────────────────

_CONFIG_HEADER = """\
# Documentation adapter configuration — generated by /rai-docs-setup
# See: https://raise.dev/docs/adapters/docs
#
# default_target: which target to use when none specified
# targets.<name>.type: adapter type (confluence, ...)
# targets.<name>.url: adapter base URL
# targets.<name>.space_key: target space
# targets.<name>.routing: artifact type → parent page + labels
# targets.<name>.sync_manifest: local_path → {remote_id, url, updated_at}
#
"""


def write_confluence_config(
    config_dict: dict[str, Any],
    project_root: Path,
    overwrite: bool = False,
) -> Path:
    """Write a config dict to .raise/docs.yaml.

    Args:
        config_dict: Config dict (should pass DocsConfig.model_validate()).
        project_root: Project root directory.
        overwrite: If False, raises FileExistsError when file exists.

    Returns:
        Path to the written file.

    Raises:
        FileExistsError: If config exists and overwrite is False.
    """
    config_dir = project_root / ".raise"
    config_path = config_dir / "docs.yaml"

    if config_path.exists() and not overwrite:
        msg = f"{config_path} already exists. Use overwrite=True to replace."
        raise FileExistsError(msg)

    config_dir.mkdir(parents=True, exist_ok=True)

    with open(config_path, "w", encoding="utf-8") as f:
        f.write(_CONFIG_HEADER)
        yaml.dump(config_dict, f, default_flow_style=False, sort_keys=False)

    return config_path
