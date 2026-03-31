"""Tests for Jira config schema + Pydantic models.

S1052.2 (E1052)
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from raise_cli.adapters.jira_config import (
    JiraConfig,
    JiraInstance,
    JiraProject,
    load_jira_config,
)

# ── T1: JiraInstance ────────────────────────────────────────────────────


class TestJiraInstance:
    """JiraInstance model tests."""

    def test_minimal_instance(self) -> None:
        inst = JiraInstance(site="humansys.atlassian.net")
        assert inst.site == "humansys.atlassian.net"
        assert inst.email == ""
        assert inst.projects == []

    def test_full_instance(self) -> None:
        inst = JiraInstance(
            site="humansys.atlassian.net",
            email="emilio@humansys.ai",
            projects=["RAISE", "RTEST"],
        )
        assert inst.email == "emilio@humansys.ai"
        assert inst.projects == ["RAISE", "RTEST"]

    def test_site_required(self) -> None:
        with pytest.raises(ValidationError):
            JiraInstance()  # type: ignore[call-arg]

    def test_frozen(self) -> None:
        inst = JiraInstance(site="x.atlassian.net")
        with pytest.raises(ValidationError):
            inst.site = "other"  # type: ignore[misc]


# ── T1: JiraProject ────────────────────────────────────────────────────


class TestJiraProject:
    """JiraProject model tests."""

    def test_minimal_project(self) -> None:
        proj = JiraProject(instance="humansys")
        assert proj.instance == "humansys"
        assert proj.name == ""
        assert proj.category == ""
        assert proj.description == ""
        assert proj.board_type == ""
        assert proj.components == []

    def test_full_project(self) -> None:
        proj = JiraProject(
            instance="humansys",
            name="RAISE",
            category="Development",
            description="RaiSE framework development",
            board_type="scrum",
            components=["cli", "core"],
        )
        assert proj.name == "RAISE"
        assert proj.board_type == "scrum"
        assert proj.components == ["cli", "core"]

    def test_instance_required(self) -> None:
        with pytest.raises(ValidationError):
            JiraProject()  # type: ignore[call-arg]


# ── T1: JiraConfig ─────────────────────────────────────────────────────


def _make_instance(**overrides: str | list[str]) -> JiraInstance:
    """Helper: create JiraInstance with defaults."""
    defaults: dict[str, str | list[str]] = {"site": "humansys.atlassian.net"}
    return JiraInstance(**{**defaults, **overrides})  # type: ignore[arg-type]


class TestJiraConfig:
    """JiraConfig root model tests."""

    def test_minimal_config(self) -> None:
        cfg = JiraConfig(
            default_instance="humansys",
            instances={"humansys": _make_instance()},
        )
        assert cfg.default_instance == "humansys"
        assert "humansys" in cfg.instances

    def test_config_with_projects(self) -> None:
        cfg = JiraConfig(
            default_instance="humansys",
            instances={"humansys": _make_instance()},
            projects={
                "RAISE": JiraProject(instance="humansys", name="RAISE"),
            },
        )
        assert "RAISE" in cfg.projects

    def test_default_instance_not_in_instances_raises(self) -> None:
        with pytest.raises(ValidationError, match="default_instance"):
            JiraConfig(
                default_instance="missing",
                instances={"humansys": _make_instance()},
            )

    def test_project_references_unknown_instance_raises(self) -> None:
        with pytest.raises(ValidationError, match="instance 'nope'"):
            JiraConfig(
                default_instance="humansys",
                instances={"humansys": _make_instance()},
                projects={
                    "RAISE": JiraProject(instance="nope", name="RAISE"),
                },
            )

    def test_extra_fields_allowed(self) -> None:
        """workflow, team, issue_types pass through without error."""
        cfg = JiraConfig(
            default_instance="humansys",
            instances={"humansys": _make_instance()},
            workflow={"states": [{"name": "Backlog"}]},  # type: ignore[call-arg]
            team=[{"name": "Emilio"}],  # type: ignore[call-arg]
            issue_types=[{"name": "Story"}],  # type: ignore[call-arg]
        )
        assert cfg.default_instance == "humansys"

    def test_frozen(self) -> None:
        cfg = JiraConfig(
            default_instance="humansys",
            instances={"humansys": _make_instance()},
        )
        with pytest.raises(ValidationError):
            cfg.default_instance = "other"  # type: ignore[misc]


# ── T1: load_jira_config ──────────────────────────────────────────────


SAMPLE_JIRA_YAML = """\
default_instance: humansys

instances:
  humansys:
    site: humansys.atlassian.net
    projects: [RAISE, RTEST]

projects:
  RAISE:
    instance: humansys
    name: RAISE
    category: Development
    description: RaiSE framework development
    board_type: scrum

  RTEST:
    instance: humansys
    name: RaiSE Test Sandbox
    category: Testing
    description: Integration test sandbox
    board_type: scrum

workflow:
  states:
    - name: Backlog
      id: 11

team:
  - name: Emilio Osorio
    identifier: emilio@humansys.ai

issue_types:
  - name: Epic
"""


class TestLoadJiraConfig:
    """load_jira_config reads .raise/jira.yaml."""

    def test_load_full_yaml(self, tmp_path: Path) -> None:
        config_dir = tmp_path / ".raise"
        config_dir.mkdir()
        (config_dir / "jira.yaml").write_text(SAMPLE_JIRA_YAML)

        cfg = load_jira_config(tmp_path)
        assert cfg.default_instance == "humansys"
        assert "humansys" in cfg.instances
        assert cfg.instances["humansys"].site == "humansys.atlassian.net"
        assert "RAISE" in cfg.projects
        assert cfg.projects["RAISE"].category == "Development"

    def test_missing_file_raises(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            load_jira_config(tmp_path)

    def test_empty_yaml_raises(self, tmp_path: Path) -> None:
        config_dir = tmp_path / ".raise"
        config_dir.mkdir()
        (config_dir / "jira.yaml").write_text("")

        with pytest.raises(ValueError, match="empty"):
            load_jira_config(tmp_path)

    def test_invalid_yaml_raises(self, tmp_path: Path) -> None:
        config_dir = tmp_path / ".raise"
        config_dir.mkdir()
        (config_dir / "jira.yaml").write_text("not_valid: [}")

        with pytest.raises(yaml.YAMLError):
            load_jira_config(tmp_path)

    def test_extra_sections_preserved(self, tmp_path: Path) -> None:
        """workflow, team, issue_types in YAML don't cause validation errors."""
        config_dir = tmp_path / ".raise"
        config_dir.mkdir()
        (config_dir / "jira.yaml").write_text(SAMPLE_JIRA_YAML)

        cfg = load_jira_config(tmp_path)
        # Extra fields accessible via model_extra
        assert cfg.default_instance == "humansys"
