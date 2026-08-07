"""Confluence configuration — instance, routing, and multi-instance schema.

Models for .raise/docs.yaml (agnostic) and legacy .raise/confluence.yaml.
Supports full multi-instance and flat minimal formats.

RAISE-1054 (S1051.1), RAISE-1056 (S1051.3), RAISE-3413 (S20.1)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, Field, field_validator, model_validator

from raise_cli.exceptions import ConfigurationError
from raise_cli.output.symbols import ARROW


class ArtifactRouting(BaseModel):
    """Routing config for one artifact type (e.g. adr, roadmap).

    Either parent_title or parent_path must be set (S4342.1).
    parent_path takes priority over parent_title when both are present.
    """

    parent_title: str | None = Field(
        default=None, description="Flat parent page title (single lookup)"
    )
    parent_path: list[str] | None = Field(
        default=None,
        description="Hierarchical parent path — adapter traverses left→right, creating missing pages",
    )
    labels: list[str] = Field(
        default_factory=list, description="Labels to apply on publish"
    )
    local_dir: str | None = Field(
        default=None, description="Local base directory for rai docs write"
    )
    naming: Literal["dated", "slug"] = Field(
        default="slug",
        description="File naming convention: dated={YYYY-MM-DD}-{slug}.md, slug={slug}.md",
    )

    @model_validator(mode="after")
    def _require_parent(self) -> ArtifactRouting:
        if self.parent_path is not None and len(self.parent_path) == 0:
            raise ValueError("parent_path must not be empty")
        if not self.parent_title and not self.parent_path:
            raise ValueError("parent_title or parent_path must be set")
        return self


class ConfluenceInstanceConfig(BaseModel):
    """Single Confluence instance connection config."""

    url: str = Field(
        ..., description="Confluence base URL (e.g. https://x.atlassian.net/wiki)"
    )
    username: str | None = Field(
        default=None,
        description="Atlassian account email (optional — falls back to env var)",
    )
    space_key: str = Field(..., description="Default space key")
    instance_name: str = Field(
        default="default",
        description="Instance identifier for token resolution",
    )
    routing: dict[str, ArtifactRouting] = Field(
        default_factory=dict,
        description="Artifact type → routing config (parent page + labels)",
    )
    home_page_id: str | None = Field(
        default=None,
        description="Space homepage ID — fallback ancestor for free-form publish and parent auto-create (S20.9)",
    )

    @field_validator("home_page_id", mode="before")
    @classmethod
    def _coerce_home_page_id(cls, v: object) -> str | None:
        """Coerce int to str — YAML delivers unquoted IDs as int.

        Normalizes falsy values (False, empty string) to None.
        """
        if not v:
            return None
        return str(v)


class ConfluenceConfig(BaseModel):
    """Root config — multi-instance with default.

    Supports two formats:
    1. Full: {default_instance: "name", instances: {name: {...}}}
    2. Flat: {url, username, space_key} → auto-normalized to single "default" instance
    """

    default_instance: str = Field(default="default")
    instances: dict[str, ConfluenceInstanceConfig]

    @model_validator(mode="after")
    def _validate_default_exists(self) -> ConfluenceConfig:
        if self.default_instance not in self.instances:
            msg = (
                f"default_instance '{self.default_instance}' not found in instances "
                f"(available: {', '.join(self.instances)})"
            )
            raise ValueError(msg)
        return self

    def get_instance(self, name: str | None = None) -> ConfluenceInstanceConfig:
        """Get instance by name, or default."""
        target = name or self.default_instance
        if target not in self.instances:
            msg = f"Confluence instance '{target}' not found (available: {', '.join(self.instances)})"
            raise KeyError(msg)
        return self.instances[target]

    def resolve_routing(
        self, artifact_type: str, instance: str | None = None
    ) -> ArtifactRouting | None:
        """Resolve routing for artifact type on instance. Returns None if not configured."""
        inst = self.get_instance(instance)
        return inst.routing.get(artifact_type)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ConfluenceConfig:
        """Create config from dict, auto-normalizing flat format.

        Flat: {url, username, space_key, ...} → single "default" instance.
        Full: {default_instance, instances: {...}} → pass through.
        """
        if "instances" in data:
            return cls.model_validate(data)
        # Flat format — normalize to multi-instance
        return cls(
            default_instance="default",
            instances={"default": ConfluenceInstanceConfig.model_validate(data)},
        )


_CONFLUENCE_YAML_PATH = Path(".raise/confluence.yaml")


# ── S20.1 — docs.yaml agnostic schema (ADR-048) ─────────────────────────────


class CustomTypeEntry(BaseModel):
    """A custom artifact type registered outside RAISE_ROUTING_PRESET.

    Stored in docs.yaml custom_types section. Merged into target routing
    at load time by load_confluence_target_config() (RAISE-4856).
    """

    group: str = Field(..., description="Semantic group / parent page name")
    labels: list[str] = Field(
        default_factory=list, description="Labels to apply on publish"
    )
    local_dir: str | None = Field(
        default=None, description="Local base directory for rai docs write"
    )


class SyncEntry(BaseModel):
    """Sync manifest entry: local_path → remote location after publish."""

    remote_id: str
    url: str
    updated_at: str


class ConfluenceTargetConfig(ConfluenceInstanceConfig):
    """Agnostic target config for one Confluence instance (ADR-048).

    Extends ConfluenceInstanceConfig with type discriminator.
    Compatible with ConfluenceClient (accepts ConfluenceInstanceConfig).
    """

    type: Literal["confluence"] = "confluence"


_DOCS_YAML_PATH = Path(".raise/docs.yaml")
_DOCS_YAML_HEADER = """\
# Documentation adapter configuration — managed by rai docs
# default_target: which target to use when none specified
# targets.<name>.type: adapter type (confluence, ...)
# targets.<name>.url: adapter base URL
# targets.<name>.routing: artifact type -> parent page + labels
#
"""


class DocsConfig(BaseModel):
    """Root docs config — vendor-agnostic routing only (ADR-048).

    Stores raw target dicts — each adapter validates its own section.
    Use load_confluence_target_config() to get a typed Confluence config.

    custom_types: project-level artifact types registered outside
    RAISE_ROUTING_PRESET. Merged into target routing at load time (RAISE-4856).
    """

    default_target: str = Field(default="default")
    targets: dict[str, dict[str, Any]]
    custom_types: dict[str, CustomTypeEntry] = Field(default_factory=dict)

    def get_raw_target(self, name: str | None = None) -> dict[str, Any]:
        """Return raw target dict by name, or the default target."""
        key = name or self.default_target
        if key not in self.targets:
            available = ", ".join(self.targets)
            msg = f"Docs target '{key}' not found (available: {available})"
            raise KeyError(msg)
        return self.targets[key]

    def get_target_type(self, name: str | None = None) -> str:
        """Return the adapter type for a target (e.g. 'confluence')."""
        return self.get_raw_target(name).get("type", "")


def _migrate_confluence_to_docs(data: dict[str, Any]) -> dict[str, Any]:
    """Transform legacy confluence.yaml dict → docs.yaml dict."""
    if "instances" in data:
        targets = {
            name: {**inst, "type": "confluence"}
            for name, inst in data["instances"].items()
        }
        return {
            "default_target": data.get("default_instance", "default"),
            "targets": targets,
        }
    # Flat format: {url, space_key, ...}
    instance_name = data.get("instance_name", "default")
    return {
        "default_target": instance_name,
        "targets": {instance_name: {**data, "type": "confluence"}},
    }


def load_docs_config(project_root: Path) -> DocsConfig:
    """Load .raise/docs.yaml. Auto-migrates from confluence.yaml if needed.

    Priority:
    1. docs.yaml exists → load directly
    2. confluence.yaml exists → migrate, write docs.yaml, return result
    3. Neither → FileNotFoundError
    """
    docs_path = project_root / _DOCS_YAML_PATH
    legacy_path = project_root / _CONFLUENCE_YAML_PATH

    if docs_path.exists():
        with open(docs_path, encoding="utf-8") as f:
            data: dict[str, Any] = yaml.safe_load(f)
        if not data:
            msg = f"Docs config is empty: {docs_path}"
            raise ConfigurationError(msg)
        return DocsConfig.model_validate(data)

    if legacy_path.exists():
        with open(legacy_path, encoding="utf-8") as f:
            legacy_data: dict[str, Any] = yaml.safe_load(f)
        if not legacy_data:
            msg = f"Confluence config is empty: {legacy_path}"
            raise ConfigurationError(msg)
        migrated = _migrate_confluence_to_docs(legacy_data)
        docs_path.parent.mkdir(parents=True, exist_ok=True)
        with open(docs_path, "w", encoding="utf-8") as f:
            f.write(_DOCS_YAML_HEADER)
            yaml.dump(migrated, f, default_flow_style=False, sort_keys=False)
        print(f"[rai] Migrated {_CONFLUENCE_YAML_PATH} {ARROW} {_DOCS_YAML_PATH}")
        return DocsConfig.model_validate(migrated)

    msg = f"Docs config not found: {docs_path}"
    raise FileNotFoundError(msg)


def load_confluence_target_config(
    project_root: Path,
    target_name: str | None = None,
) -> ConfluenceTargetConfig:
    """Load and validate the Confluence target section from docs.yaml.

    Each adapter owns its own config validation — this is Confluence's loader.
    Merges custom_types from docs.yaml into the target routing — custom entries
    take precedence over same-key routing entries (RAISE-4856).
    Raises KeyError if target not found, ValidationError if fields are wrong.
    """
    config = load_docs_config(project_root)
    raw = config.get_raw_target(target_name)
    target = ConfluenceTargetConfig.model_validate(raw)

    if config.custom_types:
        merged = dict(target.routing)
        for type_name, entry in config.custom_types.items():
            merged[type_name] = ArtifactRouting(
                parent_title=entry.group,
                labels=entry.labels if entry.labels else [type_name],
                local_dir=entry.local_dir,
            )
        target = target.model_copy(update={"routing": merged})

    return target


def load_all_confluence_targets(
    project_root: Path,
) -> tuple[str, dict[str, ConfluenceTargetConfig]]:
    """Load all confluence-typed targets from docs.yaml.

    Returns (default_name, targets_dict). Falls back to first target if
    default_target is not a confluence target.
    Merges custom_types into every target's routing (RAISE-4856).
    """
    config = load_docs_config(project_root)
    targets = {
        name: ConfluenceTargetConfig.model_validate(raw)
        for name, raw in config.targets.items()
        if raw.get("type") == "confluence"
    }
    if not targets:
        msg = "No confluence targets found in docs.yaml"
        raise ConfigurationError(msg)

    if config.custom_types:
        custom_routing = {
            type_name: ArtifactRouting(
                parent_title=entry.group,
                labels=entry.labels if entry.labels else [type_name],
                local_dir=entry.local_dir,
            )
            for type_name, entry in config.custom_types.items()
        }
        targets = {
            name: target.model_copy(
                update={"routing": {**target.routing, **custom_routing}}
            )
            for name, target in targets.items()
        }

    default = (
        config.default_target
        if config.default_target in targets
        else next(iter(targets))
    )
    return default, targets


def load_confluence_config(project_root: Path) -> ConfluenceConfig:
    """Load and validate .raise/confluence.yaml.

    Supports full multi-instance and flat minimal formats.
    Raises FileNotFoundError if config file doesn't exist.
    """
    config_path = project_root / _CONFLUENCE_YAML_PATH
    if not config_path.exists():
        msg = f"Confluence config not found: {config_path}"
        raise FileNotFoundError(msg)
    with open(config_path, encoding="utf-8") as f:
        data: dict[str, Any] = yaml.safe_load(f)
    if not data:
        msg = f"Confluence config is empty: {config_path}"
        raise ConfigurationError(msg)
    return ConfluenceConfig.from_dict(data)
