"""Jira config generator — pure function producing valid config dicts.

Takes JiraProjectMap from discovery + user selections, returns a dict
that passes JiraConfig.model_validate() validation. No side effects.

Workflow states and issue types are placed per-project (RAISE-1300),
not merged globally.

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
            raise ValueError(msg)

    # Find full ProjectInfo for selected projects
    selected_keys = set(selected_projects)
    selected_infos = [p for p in project_map.projects if p.key in selected_keys]

    # Build instances section
    instances: dict[str, dict[str, Any]] = {
        instance_name: {
            "site": site,
            "projects": sorted(p.key for p in selected_infos),
        },
    }

    # Build projects section — with per-project workflow_states and issue_types
    projects: dict[str, dict[str, Any]] = {}
    for info in selected_infos:
        project_entry: dict[str, Any] = {
            "instance": instance_name,
            "name": info.name,
        }

        # Per-project workflow states
        workflow_states = project_map.workflows.get(info.key, [])
        if workflow_states:
            project_entry["workflow_states"] = [
                {"name": ws.name, "category": ws.status_category}
                for ws in workflow_states
            ]

        # Per-project issue types
        issue_types = project_map.issue_types.get(info.key, [])
        if issue_types:
            project_entry["issue_types"] = [
                {"name": it.name, "subtask": it.subtask} for it in issue_types
            ]

        projects[info.key] = project_entry

    return {
        "default_instance": instance_name,
        "instances": instances,
        "projects": projects,
    }
