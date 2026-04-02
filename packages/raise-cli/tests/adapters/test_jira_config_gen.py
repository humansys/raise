"""Tests for Jira config generator — S1130.5."""

from __future__ import annotations

import pytest

from raise_cli.adapters.jira_config import JiraConfig
from raise_cli.adapters.jira_config_gen import generate_jira_config
from raise_cli.adapters.jira_discovery import JiraProjectMap
from raise_cli.adapters.models.pm import (
    IssueTypeInfo,
    ProjectInfo,
    WorkflowState,
)

# ── Fixtures ─────────────────────────────────────────────────────────


def _make_project_map(
    *,
    projects: list[ProjectInfo] | None = None,
    workflows: dict[str, list[WorkflowState]] | None = None,
    issue_types: dict[str, list[IssueTypeInfo]] | None = None,
) -> JiraProjectMap:
    """Build a JiraProjectMap with sensible defaults."""
    default_projects = [
        ProjectInfo(key="RAISE", name="RAISE", project_type_key="software"),
        ProjectInfo(key="RTEST", name="RaiSE Test", project_type_key="software"),
    ]
    ps = projects if projects is not None else default_projects
    keys = [p.key for p in ps]
    return JiraProjectMap(
        projects=ps,
        workflows=workflows if workflows is not None else {k: [] for k in keys},
        issue_types=issue_types if issue_types is not None else {k: [] for k in keys},
    )


# ── T1: Core generator + schema validation ──────────────────────────


class TestCoreGenerator:
    """Core generator produces valid JiraConfig dicts."""

    def test_minimal_config_validates(self) -> None:
        """Generated config passes JiraConfig.model_validate()."""
        pm = _make_project_map()
        result = generate_jira_config(
            project_map=pm,
            selected_projects=["RAISE"],
            instance_name="humansys",
            site="humansys.atlassian.net",
        )
        config = JiraConfig.model_validate(result)
        assert config.default_instance == "humansys"
        assert "humansys" in config.instances
        assert config.instances["humansys"].site == "humansys.atlassian.net"

    def test_selected_project_in_output(self) -> None:
        """Selected project appears in projects section."""
        pm = _make_project_map()
        result = generate_jira_config(
            project_map=pm,
            selected_projects=["RAISE"],
            instance_name="humansys",
            site="humansys.atlassian.net",
        )
        assert "RAISE" in result["projects"]
        project = result["projects"]["RAISE"]
        assert project["instance"] == "humansys"
        assert project["name"] == "RAISE"

    def test_multiple_projects(self) -> None:
        """Multiple selected projects all appear in output."""
        pm = _make_project_map()
        result = generate_jira_config(
            project_map=pm,
            selected_projects=["RAISE", "RTEST"],
            instance_name="humansys",
            site="humansys.atlassian.net",
        )
        config = JiraConfig.model_validate(result)
        assert "RAISE" in config.projects
        assert "RTEST" in config.projects

    def test_invalid_project_raises(self) -> None:
        """ValueError raised for project not in discovery map."""
        pm = _make_project_map()
        with pytest.raises(ValueError, match="NOPE"):
            generate_jira_config(
                project_map=pm,
                selected_projects=["NOPE"],
                instance_name="humansys",
                site="humansys.atlassian.net",
            )

    def test_instance_projects_list(self) -> None:
        """Instance includes selected project keys in its projects list."""
        pm = _make_project_map()
        result = generate_jira_config(
            project_map=pm,
            selected_projects=["RAISE", "RTEST"],
            instance_name="humansys",
            site="humansys.atlassian.net",
        )
        assert result["instances"]["humansys"]["projects"] == ["RAISE", "RTEST"]
