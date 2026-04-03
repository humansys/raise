"""Project manifest schema and persistence.

The manifest file (.raise/manifest.yaml) stores project metadata detected
during initialization, including project type and code file count.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

import yaml
from pydantic import BaseModel, Field, ValidationError, model_validator

from raise_cli.config.ide import IdeType
from raise_cli.config.paths import MANIFEST_FILE, get_raise_dir
from raise_cli.onboarding.detection import ProjectType

logger = logging.getLogger(__name__)


class ProjectInfo(BaseModel):
    """Information about the project detected during init.

    Attributes:
        name: Project name (usually directory name).
        project_type: Whether greenfield or brownfield.
        language: Dominant programming language (auto-detected or user-specified).
        test_command: Command to run tests (configuration over convention).
        lint_command: Command to run linter (configuration over convention).
        type_check_command: Command to run type checker (configuration over convention).
        format_command: Command to run formatter check (configuration over convention).
        code_file_count: Number of code files detected.
        detected_at: When the project was initialized.
    """

    name: str
    project_type: ProjectType
    language: str | None = None
    test_command: str | None = None
    lint_command: str | None = None
    type_check_command: str | None = None
    format_command: str | None = None
    code_file_count: int = 0
    detected_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class BranchConfig(BaseModel):
    """Branch naming configuration for the project.

    Attributes:
        development: The development/integration branch name.
        main: The stable/production branch name.
    """

    development: str = "main"
    main: str = "main"


class IdeManifest(BaseModel):
    """IDE configuration persisted in manifest (legacy single-IDE format).

    Attributes:
        type: Which IDE this project uses.
    """

    type: IdeType = "claude"


class AgentsManifest(BaseModel):
    """Multi-agent configuration persisted in manifest.

    Replaces IdeManifest with a list to support multiple simultaneous agents.

    Attributes:
        types: List of active agent types (e.g. ["claude", "cursor", "windsurf"]).
    """

    types: list[str] = Field(default_factory=lambda: ["claude"])


class BacklogConfig(BaseModel):
    """Backlog configuration from manifest (optional section).

    Attributes:
        adapter_default: Default PM adapter name (e.g., 'jira', 'filesystem').
    """

    adapter_default: str | None = None


class TierConfig(BaseModel):
    """Tier configuration from manifest (optional section).

    Attributes:
        level: Tier level string (community, pro, enterprise).
        backend_url: Backend URL for PRO/Enterprise tiers.
        capabilities: List of capability strings enabled for this tier.
    """

    level: str = "community"
    backend_url: str | None = None
    capabilities: list[str] = Field(default_factory=list)


class ProjectManifest(BaseModel):
    """Project manifest stored in .raise/manifest.yaml.

    Attributes:
        version: Manifest schema version.
        project: Project information.
        branches: Branch naming configuration.
        ide: Legacy single-IDE configuration (backward compat — read/write).
        agents: Multi-agent configuration (new format).
        tier: Optional tier configuration (S211.5).
    """

    version: str = "1.0"
    project: ProjectInfo
    branches: BranchConfig = Field(default_factory=BranchConfig)
    ide: IdeManifest = Field(default_factory=IdeManifest)
    agents: AgentsManifest = Field(default_factory=AgentsManifest)
    tier: TierConfig | None = None
    backlog: BacklogConfig | None = None

    @model_validator(mode="before")
    @classmethod
    def _migrate_ide_to_agents(cls, data: Any) -> dict[str, Any]:
        """Migrate old ide.type format to agents.types on load.

        If 'agents' key is absent but 'ide' key is present, derive
        agents.types from ide.type for backward compat.
        """
        if not isinstance(data, dict):
            return cast("dict[str, Any]", data)
        typed: dict[str, Any] = cast("dict[str, Any]", data)
        if "agents" not in typed and "ide" in typed:
            raw_ide: object = typed["ide"]
            if isinstance(raw_ide, dict):
                raw_type: object = cast("dict[str, object]", raw_ide).get(
                    "type", "claude"
                )
                ide_type: str = str(raw_type) if raw_type is not None else "claude"
            else:
                ide_type = "claude"
            typed["agents"] = {"types": [ide_type]}
        return typed


def save_manifest(manifest: ProjectManifest, project_root: Path) -> None:
    """Save project manifest to .raise/manifest.yaml.

    Creates .raise/ directory if it doesn't exist.

    Args:
        manifest: The manifest to save.
        project_root: Root directory of the project.
    """
    raise_dir = get_raise_dir(project_root)
    raise_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = raise_dir / MANIFEST_FILE

    # Convert to dict with proper serialization
    data = manifest.model_dump(mode="json")

    content = yaml.dump(
        data, default_flow_style=False, allow_unicode=True, sort_keys=False
    )
    manifest_path.write_text(content, encoding="utf-8")
    logger.debug("Saved manifest: %s", manifest_path)


def load_manifest(project_root: Path) -> ProjectManifest | None:
    """Load project manifest from .raise/manifest.yaml.

    Args:
        project_root: Root directory of the project.

    Returns:
        ProjectManifest if file exists and is valid, None otherwise.
    """
    manifest_path = get_raise_dir(project_root) / MANIFEST_FILE

    if not manifest_path.exists():
        logger.debug("Manifest not found: %s", manifest_path)
        return None

    try:
        content = manifest_path.read_text(encoding="utf-8")
        data = yaml.safe_load(content)
        if data is None:
            logger.warning("Empty manifest: %s", manifest_path)
            return None
        return ProjectManifest.model_validate(data)
    except yaml.YAMLError as e:
        logger.warning("Invalid YAML in manifest: %s", e)
        return None
    except ValidationError as e:
        logger.warning("Invalid manifest schema: %s", e)
        return None
