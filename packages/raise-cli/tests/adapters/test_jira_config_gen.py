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


# ── T2: Workflow states + status mapping ─────────────────────────────


class TestWorkflowGeneration:
    """Workflow states and status mapping from discovery data."""

    def test_workflow_states_included(self) -> None:
        """Discovered workflow states appear in output."""
        workflows = {
            "RAISE": [
                WorkflowState(name="Backlog", status_category="new", transitions=[]),
                WorkflowState(
                    name="In Progress", status_category="indeterminate", transitions=[]
                ),
                WorkflowState(name="Done", status_category="done", transitions=[]),
            ],
        }
        pm = _make_project_map(
            projects=[
                ProjectInfo(key="RAISE", name="RAISE", project_type_key="software")
            ],
            workflows=workflows,
        )
        result = generate_jira_config(
            project_map=pm,
            selected_projects=["RAISE"],
            instance_name="humansys",
            site="humansys.atlassian.net",
        )
        assert "workflow" in result
        states = result["workflow"]["states"]
        assert len(states) == 3
        names = [s["name"] for s in states]
        assert "Backlog" in names
        assert "In Progress" in names
        assert "Done" in names

    def test_status_mapping_generated(self) -> None:
        """Status mapping keys derived from state names (slugified)."""
        workflows = {
            "RAISE": [
                WorkflowState(name="Backlog", status_category="new", transitions=[]),
                WorkflowState(
                    name="In Progress", status_category="indeterminate", transitions=[]
                ),
                WorkflowState(name="Done", status_category="done", transitions=[]),
            ],
        }
        pm = _make_project_map(
            projects=[
                ProjectInfo(key="RAISE", name="RAISE", project_type_key="software")
            ],
            workflows=workflows,
        )
        result = generate_jira_config(
            project_map=pm,
            selected_projects=["RAISE"],
            instance_name="humansys",
            site="humansys.atlassian.net",
        )
        mapping = result["workflow"]["status_mapping"]
        assert "backlog" in mapping
        assert "in-progress" in mapping
        assert "done" in mapping

    def test_status_category_in_states(self) -> None:
        """Each state includes its category."""
        workflows = {
            "RAISE": [
                WorkflowState(name="Backlog", status_category="new", transitions=[]),
            ],
        }
        pm = _make_project_map(
            projects=[
                ProjectInfo(key="RAISE", name="RAISE", project_type_key="software")
            ],
            workflows=workflows,
        )
        result = generate_jira_config(
            project_map=pm,
            selected_projects=["RAISE"],
            instance_name="humansys",
            site="humansys.atlassian.net",
        )
        state = result["workflow"]["states"][0]
        assert state["category"] == "new"

    def test_empty_workflows_omits_section(self) -> None:
        """No workflow section when no states discovered."""
        pm = _make_project_map(
            projects=[
                ProjectInfo(key="RAISE", name="RAISE", project_type_key="software")
            ],
            workflows={"RAISE": []},
        )
        result = generate_jira_config(
            project_map=pm,
            selected_projects=["RAISE"],
            instance_name="humansys",
            site="humansys.atlassian.net",
        )
        assert "workflow" not in result

    def test_multi_project_merges_workflows(self) -> None:
        """Workflows from multiple selected projects are merged (deduped)."""
        workflows = {
            "RAISE": [
                WorkflowState(name="Backlog", status_category="new", transitions=[]),
                WorkflowState(name="Done", status_category="done", transitions=[]),
            ],
            "RTEST": [
                WorkflowState(name="Backlog", status_category="new", transitions=[]),
                WorkflowState(
                    name="In Review", status_category="indeterminate", transitions=[]
                ),
                WorkflowState(name="Done", status_category="done", transitions=[]),
            ],
        }
        pm = _make_project_map(workflows=workflows)
        result = generate_jira_config(
            project_map=pm,
            selected_projects=["RAISE", "RTEST"],
            instance_name="humansys",
            site="humansys.atlassian.net",
        )
        states = result["workflow"]["states"]
        names = {s["name"] for s in states}
        # Union of both projects, deduplicated
        assert names == {"Backlog", "Done", "In Review"}

    def test_schema_validates_with_workflow(self) -> None:
        """Full config with workflow still passes JiraConfig.model_validate()."""
        workflows = {
            "RAISE": [
                WorkflowState(name="Backlog", status_category="new", transitions=[]),
                WorkflowState(name="Done", status_category="done", transitions=[]),
            ],
        }
        pm = _make_project_map(
            projects=[
                ProjectInfo(key="RAISE", name="RAISE", project_type_key="software")
            ],
            workflows=workflows,
        )
        result = generate_jira_config(
            project_map=pm,
            selected_projects=["RAISE"],
            instance_name="humansys",
            site="humansys.atlassian.net",
        )
        # JiraConfig has extra="allow", so workflow passes through
        config = JiraConfig.model_validate(result)
        assert config.default_instance == "humansys"
