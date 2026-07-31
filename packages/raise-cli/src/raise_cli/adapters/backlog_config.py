"""Generic backlog adapter config I/O — reads/writes .raise/backlog.yaml.

Replaces jira_config.save_jira_config and load_jira_config for CLI use.
The CLI never imports from jira_config directly (PAT-F-167).

S2503.12 (RAISE-2723)
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from raise_cli.adapters.models.pm import (
    BacklogAdapterConfig,
    PipelineWorkflowConfig,
    merge_custom_fields_entries,
)

_BACKLOG_YAML_PATH = Path(".raise") / "backlog.yaml"
_JIRA_YAML_PATH = Path(".raise") / "jira.yaml"


def save_backlog_config(
    project_root: Path,
    adapter_name: str,
    updates: dict[str, Any],
) -> None:
    """Merge updates into .raise/backlog.yaml under adapter_name section.

    For each top-level key in updates:
    - custom_fields is merged by CustomField.id per issue type, grouping
      case-variant keys together — so two `fields discover`
      calls for the same type with different --names UNION their fields
      instead of the second overwriting the first.
    - Any other key that already exists as a dict is shallow-merged so
      sibling sub-keys (e.g. field_types entries) survive.
    - Replaces only the matching block in the raw file; other sections untouched.
    - Appends if section doesn't exist yet.
    """
    config_path = project_root / _BACKLOG_YAML_PATH
    config_path.parent.mkdir(parents=True, exist_ok=True)

    content = ""
    root_data: dict[str, Any] = {}
    if config_path.exists():
        content = config_path.read_text(encoding="utf-8")
        root_data = yaml.safe_load(content) or {}

    adapter_data: dict[str, Any] = root_data.get(adapter_name) or {}

    # Merge each update key into the adapter section
    for key, value in updates.items():
        existing = adapter_data.get(key)
        if key == "custom_fields" and isinstance(value, dict):
            # Merge field lists by CustomField.id rather than
            # replacing the list wholesale — otherwise a second discover for
            # the same issue type silently drops the first discover's fields.
            existing_cf: dict[str, Any] = existing if isinstance(existing, dict) else {}
            adapter_data[key] = merge_custom_fields_entries(
                [*existing_cf.items(), *value.items()]
            )
        elif isinstance(existing, dict) and isinstance(value, dict):
            adapter_data[key] = {**existing, **value}
        else:
            adapter_data[key] = value

    # Serialize full adapter section as YAML
    section_yaml = yaml.dump(
        {adapter_name: adapter_data},
        default_flow_style=False,
        allow_unicode=True,
        sort_keys=False,
    )

    # Surgically replace the adapter_name block (key + all indented/blank lines)
    pattern = re.compile(
        rf"^{re.escape(adapter_name)}:\n(?:[ \t][^\n]*\n|[ \t]*\n)*",
        re.MULTILINE,
    )
    if pattern.search(content):
        content = pattern.sub(section_yaml, content)
    else:
        if content and not content.endswith("\n"):
            content += "\n"
        content += "\n" + section_yaml if content else section_yaml

    config_path.write_text(content, encoding="utf-8")


def load_backlog_config(
    project_root: Path,
    adapter_name: str,
) -> BacklogAdapterConfig:
    """Load and validate backlog.yaml section for adapter_name.

    Runs migrate_jira_yaml_if_needed() first so projects with only jira.yaml
    continue working without manual migration.

    Raises:
        FileNotFoundError: If neither backlog.yaml nor jira.yaml exists.
        KeyError: If adapter_name section is missing.
        pydantic.ValidationError: If section doesn't match BacklogAdapterConfig.
    """
    migrate_jira_yaml_if_needed(project_root)
    config_path = project_root / _BACKLOG_YAML_PATH
    if not config_path.exists():
        msg = f"Backlog config not found: {config_path}"
        raise FileNotFoundError(msg)

    root_data: dict[str, Any] = (
        yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    )
    if adapter_name not in root_data:
        msg = f"Adapter '{adapter_name}' not configured in {config_path}"
        raise KeyError(msg)

    return BacklogAdapterConfig.model_validate(root_data[adapter_name])


def migrate_jira_yaml_if_needed(project_root: Path) -> bool:
    """Migrate .raise/jira.yaml → .raise/backlog.yaml[jira] with generic field names.

    Applies renames:
        instances       → organizations
        instance.site   → organization.url
        default_instance → default_org
        project.instance → project.org
        link_types      → relation_types

    Returns True if migration ran, False if no-op.
    Idempotent: no-op if backlog.yaml already exists.
    Preserves jira.yaml (does not delete it).
    """
    backlog_path = project_root / _BACKLOG_YAML_PATH
    jira_path = project_root / _JIRA_YAML_PATH

    if backlog_path.exists():
        return False
    if not jira_path.exists():
        return False

    raw: dict[str, Any] = yaml.safe_load(jira_path.read_text(encoding="utf-8")) or {}
    migrated = _rename_jira_to_generic(raw)

    backlog_path.parent.mkdir(parents=True, exist_ok=True)
    content = yaml.dump(
        {"jira": migrated},
        default_flow_style=False,
        allow_unicode=True,
        sort_keys=False,
    )
    backlog_path.write_text(content, encoding="utf-8")
    return True


def _rename_jira_to_generic(raw: dict[str, Any]) -> dict[str, Any]:
    """Apply field renames from jira.yaml format to backlog.yaml[jira] format."""
    result: dict[str, Any] = {}

    for key, value in raw.items():
        if key == "default_instance":
            result["default_org"] = value
        elif key == "instances":
            organizations: dict[str, Any] = {}
            instances_raw: dict[str, Any] = value or {}
            for org_name, inst in instances_raw.items():
                org: dict[str, Any] = {}
                inst_dict: dict[str, Any] = inst or {}
                for ikey, ival in inst_dict.items():
                    org["url" if ikey == "site" else ikey] = ival
                organizations[org_name] = org
            result["organizations"] = organizations
        elif key == "projects":
            projects: dict[str, Any] = {}
            projects_raw: dict[str, Any] = value or {}
            for pkey, proj in projects_raw.items():
                p: dict[str, Any] = {}
                proj_dict: dict[str, Any] = proj or {}
                for pk, pv in proj_dict.items():
                    p["org" if pk == "instance" else pk] = pv
                projects[pkey] = p
            result["projects"] = projects
        elif key == "link_types":
            result["relation_types"] = value
        else:
            result[key] = value

    return result


_PIPELINE_WORKFLOW_YAML_PATH = Path(".raise") / "backlog_config.yaml"
_PIPELINE_WORKFLOW_SECTION = "pipeline_workflow"


def load_workflow_config(config_path: Path | None = None) -> PipelineWorkflowConfig:
    """Load PipelineWorkflowConfig from the ``pipeline_workflow`` section of a YAML file.

    If ``config_path`` is None, defaults to ``.raise/backlog_config.yaml`` relative to CWD.
    Returns an empty ``PipelineWorkflowConfig`` (fail-open) if the file or section is absent.

    Story: S2 (RAISE-15029) — State Machine Builder
    """
    resolved = config_path if config_path is not None else _PIPELINE_WORKFLOW_YAML_PATH

    if not resolved.exists():
        return PipelineWorkflowConfig()

    raw: dict[str, Any] = yaml.safe_load(resolved.read_text(encoding="utf-8")) or {}
    section = raw.get(_PIPELINE_WORKFLOW_SECTION)

    if not isinstance(section, dict):
        return PipelineWorkflowConfig()

    return PipelineWorkflowConfig.model_validate(section)


def get_configured_adapters(project_root: Path) -> set[str]:
    """Return set of adapter names with a section in backlog.yaml.

    Returns empty set if backlog.yaml doesn't exist.
    """
    config_path = project_root / _BACKLOG_YAML_PATH
    if not config_path.exists():
        return set()
    root_data: dict[str, Any] = (
        yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    )
    return {k for k in root_data if isinstance(root_data[k], dict)}
