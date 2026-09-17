"""Jira config generator — pure function producing valid config dicts.

Takes JiraProjectMap from discovery + user selections, returns a dict
that passes JiraConfig.model_validate() validation. No side effects.

Workflow states and issue types are placed per-project (RAISE-1300),
not merged globally.

RAISE-1130 (S1130.5)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from raise_cli.adapters.jira_discovery import JiraProjectMap
from raise_cli.exceptions import ConfigurationError


def generate_jira_config(
    project_map: JiraProjectMap,
    selected_projects: list[str],
    instance_name: str,
    site: str,
) -> dict[str, Any]:
    """Generate a Jira config dict from discovery data.

    Args:
        project_map: Discovered project structure from JiraDiscovery.
        selected_projects: Project keys chosen by the user.
        instance_name: Logical instance name (e.g. "humansys").
        site: Jira site domain (e.g. "humansys.atlassian.net").

    Returns:
        Dict matching JiraConfig schema (default_instance, instances, projects).
        Workflow states and issue types are per-project inside the projects dict.

    Raises:
        ValueError: If any selected_project is not in the discovery map.
    """
    known_keys = {p.key for p in project_map.projects}
    for key in selected_projects:
        if key not in known_keys:
            msg = (
                f"Project '{key}' not found in discovery map. "
                f"Available: {', '.join(sorted(known_keys))}"
            )
            raise ConfigurationError(msg)

    # Find full ProjectInfo for selected projects
    selected_keys = set(selected_projects)
    selected_infos = [p for p in project_map.projects if p.key in selected_keys]

    # Build organizations section (generic name for instances)
    instances: dict[str, dict[str, Any]] = {
        instance_name: {
            "url": site,
            "projects": sorted(p.key for p in selected_infos),
        },
    }

    # Build projects section — with per-project workflow_states and issue_types
    projects: dict[str, dict[str, Any]] = {}
    for info in selected_infos:
        project_entry: dict[str, Any] = {
            "org": instance_name,
            "name": info.name,
        }

        # Per-project workflow states
        workflow_states = project_map.workflows.get(info.key, [])
        if workflow_states:
            project_entry["workflow_states"] = [
                {"name": ws.name, "category": ws.status_category}
                for ws in workflow_states
            ]

        # Per-project issue types — names only (subtask is Jira-internal)
        issue_types = project_map.issue_types.get(info.key, [])
        if issue_types:
            project_entry["issue_types"] = [it.name for it in issue_types]

        projects[info.key] = project_entry

    return {
        "default_org": instance_name,
        "organizations": instances,
        "projects": projects,
    }


# ── Multi-org merge (RAISE-6248) ─────────────────────────────────────


def merge_jira_config(
    existing_dict: dict[str, Any],
    new_org_name: str,
    new_org_entry: dict[str, Any],
    new_projects: dict[str, Any],
) -> dict[str, Any]:
    """Add a new org to an existing Jira config dict without changing default_org.

    Args:
        existing_dict: Current ``jira:`` section from backlog.yaml (may be empty).
        new_org_name: Logical name for the new org (e.g. ``"prosa"``).
        new_org_entry: New org config dict (``url`` + ``projects`` list).
        new_projects: Project configs keyed by project key.

    Returns:
        Merged config dict preserving existing orgs and ``default_org``.

    Raises:
        ValueError: If ``new_org_name`` already exists in organizations.
    """
    existing_orgs: dict[str, Any] = existing_dict.get("organizations", {})
    if new_org_name in existing_orgs:
        msg = (
            f"Org '{new_org_name}' already exists in organizations. "
            "Use --overwrite to replace the full config."
        )
        raise ValueError(msg)

    merged = dict(existing_dict)
    merged["organizations"] = {**existing_orgs, new_org_name: new_org_entry}
    merged["projects"] = {**existing_dict.get("projects", {}), **new_projects}
    return merged


def add_org_to_jira_config(
    new_config_dict: dict[str, Any],
    project_root: Path,
) -> Path:
    """Read existing backlog.yaml, merge a new org, and write the result.

    ``new_config_dict`` is the full output of :func:`generate_jira_config`
    for the new org.  ``default_org`` of the existing file is preserved —
    only ``organizations`` and ``projects`` are extended.

    Creates ``.raise/backlog.yaml`` with the new org as sole org if the file
    does not yet exist.

    Args:
        new_config_dict: Config dict for the new org (from ``generate_jira_config``).
        project_root: Project root directory.

    Returns:
        Path to the written file.

    Raises:
        ValueError: If the new org name already exists in the current config.
    """
    config_path = project_root / ".raise" / "backlog.yaml"

    # Load existing or start from scratch
    existing_jira: dict[str, Any] = {}
    if config_path.exists():
        with open(config_path, encoding="utf-8") as fh:
            raw = yaml.safe_load(fh) or {}
        existing_jira = raw.get("jira", {})

    # Extract new-org info from the generated config dict
    new_org_name: str = new_config_dict["default_org"]
    new_org_entry: dict[str, Any] = new_config_dict["organizations"][new_org_name]
    new_projects: dict[str, Any] = new_config_dict.get("projects", {})

    merged_jira = merge_jira_config(
        existing_jira, new_org_name, new_org_entry, new_projects
    )

    config_dir = project_root / ".raise"
    config_dir.mkdir(parents=True, exist_ok=True)
    with open(config_path, "w", encoding="utf-8") as fh:
        fh.write(_CONFIG_HEADER)
        yaml.dump({"jira": merged_jira}, fh, default_flow_style=False, sort_keys=False)

    return config_path


# ── YAML writer ──────────────────────────────────────────────────────

_CONFIG_HEADER = """\
# Backlog adapter configuration — generated by rai adapter setup
#
# Sections per adapter. Each adapter stores its config under its name key.
# default_org: which organization to use when none specified
# organizations.<name>.url: tool endpoint domain
# projects.<key>.org: which organization owns this project
#
"""


def write_jira_config(
    config_dict: dict[str, Any],
    project_root: Path,
    overwrite: bool = False,
) -> Path:
    """Write Jira config dict to .raise/backlog.yaml under jira: section.

    Args:
        config_dict: Config dict with generic names (default_org, organizations, etc.)
        project_root: Project root directory.
        overwrite: If False, raises FileExistsError when backlog.yaml exists.

    Returns:
        Path to the written file.

    Raises:
        FileExistsError: If backlog.yaml exists and overwrite is False.
    """
    config_dir = project_root / ".raise"
    config_path = config_dir / "backlog.yaml"

    if config_path.exists() and not overwrite:
        msg = f"{config_path} already exists. Use overwrite=True to replace."
        raise FileExistsError(msg)

    config_dir.mkdir(parents=True, exist_ok=True)

    with open(config_path, "w", encoding="utf-8") as f:
        f.write(_CONFIG_HEADER)
        yaml.dump({"jira": config_dict}, f, default_flow_style=False, sort_keys=False)

    return config_path
