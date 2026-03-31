"""Jira configuration — instance, project routing, and multi-instance schema.

Models for .raise/jira.yaml with loader function.
Supports multi-instance format with project→instance routing.

RAISE-1052 (S1052.2)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator


class JiraInstance(BaseModel, frozen=True):
    """Single Jira instance connection config."""

    site: str = Field(..., description="Jira site (e.g. humansys.atlassian.net)")
    email: str = Field(default="", description="Account email (optional — falls back to env)")
    projects: list[str] = Field(
        default_factory=list,
        description="Project keys on this instance (informational)",
    )


class JiraProject(BaseModel, frozen=True):
    """Project-level config with instance routing."""

    instance: str = Field(..., description="Instance key (must exist in instances dict)")
    name: str = Field(default="", description="Human-readable project name")
    category: str = Field(default="", description="Project category (e.g. Development)")
    description: str = Field(default="", description="Project description")
    board_type: str = Field(default="", description="Board type (e.g. scrum, kanban)")
    components: list[str] = Field(default_factory=list, description="Project components")


class JiraConfig(BaseModel, frozen=True):
    """Root config — multi-instance with default.

    Extra fields (workflow, team, issue_types) are accepted but not modeled.
    They pass through via model_config extra="allow" for consumption by other code.
    """

    model_config = ConfigDict(extra="allow")

    default_instance: str = Field(..., description="Default instance key")
    instances: dict[str, JiraInstance] = Field(..., description="Named Jira instances")
    projects: dict[str, JiraProject] = Field(
        default_factory=dict,
        description="Project key → project config",
    )

    @model_validator(mode="after")
    def _validate_instance_references(self) -> JiraConfig:
        """Validate default_instance and project instance references."""
        if self.default_instance not in self.instances:
            msg = (
                f"default_instance '{self.default_instance}' not found in instances "
                f"(available: {', '.join(self.instances)})"
            )
            raise ValueError(msg)
        for key, project in self.projects.items():
            if project.instance not in self.instances:
                msg = (
                    f"Project '{key}' references instance '{project.instance}' "
                    f"not found in instances (available: {', '.join(self.instances)})"
                )
                raise ValueError(msg)
        return self

    def resolve_instance(self, project_key: str) -> JiraInstance:
        """Resolve JiraInstance for a project key.

        Looks up project → instance mapping. Falls back to default_instance
        if project_key is not in the projects dict.
        """
        if project_key in self.projects:
            instance_name = self.projects[project_key].instance
        else:
            instance_name = self.default_instance
        return self.instances[instance_name]

    def resolve_site(self, project_key: str) -> str:
        """Resolve full site URL for a project key.

        Returns https://{site} for use with atlassian-python-api.
        """
        inst = self.resolve_instance(project_key)
        return f"https://{inst.site}"


# ── Loader ──────────────────────────────────────────────────────────────

_JIRA_YAML_PATH = Path(".raise") / "jira.yaml"


def load_jira_config(project_root: Path) -> JiraConfig:
    """Load and validate .raise/jira.yaml.

    Raises FileNotFoundError if config file doesn't exist.
    Raises ValueError if config is empty.
    Raises yaml.YAMLError if YAML is malformed.
    Raises pydantic.ValidationError if schema is invalid.
    """
    config_path = project_root / _JIRA_YAML_PATH
    if not config_path.exists():
        msg = f"Jira config not found: {config_path}"
        raise FileNotFoundError(msg)
    with open(config_path) as f:
        data: dict[str, Any] = yaml.safe_load(f)
    if not data:
        msg = f"Jira config is empty: {config_path}"
        raise ValueError(msg)
    return JiraConfig.model_validate(data)
