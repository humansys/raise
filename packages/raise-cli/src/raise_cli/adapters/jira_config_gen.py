"""Jira config generator — pure function producing valid config dicts.

Takes JiraProjectMap from discovery + user selections, returns a dict
that passes JiraConfig.model_validate() validation. No side effects.

RAISE-1130 (S1130.5)
"""

from __future__ import annotations

from typing import Any

from raise_cli.adapters.jira_discovery import JiraProjectMap
from raise_cli.adapters.models.pm import WorkflowState


def _slugify(name: str) -> str:
    """Convert status name to mapping key: lowercase, spaces → hyphens."""
    return name.strip().lower().replace(" ", "-")


def _merge_workflows(
    project_map: JiraProjectMap,
    selected_keys: set[str],
) -> list[WorkflowState]:
    """Merge and deduplicate workflow states across selected projects."""
    seen: dict[tuple[str, str], WorkflowState] = {}
    for key in sorted(selected_keys):
        for ws in project_map.workflows.get(key, []):
            dedup_key = (ws.name, ws.status_category)
            if dedup_key not in seen:
                seen[dedup_key] = ws
    return list(seen.values())


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
            raise ValueError(msg)

    # Find full ProjectInfo for selected projects
    selected_infos = [
        p for p in project_map.projects if p.key in set(selected_projects)
    ]

    # Build instances section
    instances: dict[str, dict[str, Any]] = {
        instance_name: {
            "site": site,
            "projects": sorted(p.key for p in selected_infos),
        },
    }

    # Build projects section
    projects: dict[str, dict[str, Any]] = {}
    for info in selected_infos:
        projects[info.key] = {
            "instance": instance_name,
            "name": info.name,
        }

    result: dict[str, Any] = {
        "default_instance": instance_name,
        "instances": instances,
        "projects": projects,
    }

    # Workflow section — merge states across selected projects
    selected_keys = {p.key for p in selected_infos}
    merged_states = _merge_workflows(project_map, selected_keys)
    if merged_states:
        states_list: list[dict[str, Any]] = [
            {"name": ws.name, "category": ws.status_category} for ws in merged_states
        ]
        status_mapping: dict[str, str] = {
            _slugify(ws.name): ws.name for ws in merged_states
        }
        result["workflow"] = {
            "states": states_list,
            "status_mapping": status_mapping,
        }

    return result
