"""Jira config generator — pure function producing valid config dicts.

Takes JiraProjectMap from discovery + user selections, returns a dict
that passes JiraConfig.model_validate() validation. No side effects.

RAISE-1130 (S1130.5)
"""

from __future__ import annotations

from typing import Any

from raise_cli.adapters.jira_discovery import JiraProjectMap


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

    return {
        "default_instance": instance_name,
        "instances": instances,
        "projects": projects,
    }
