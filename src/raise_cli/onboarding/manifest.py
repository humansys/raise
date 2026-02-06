"""Project manifest schema and persistence.

The manifest file (.raise/manifest.yaml) stores project metadata detected
during initialization, including project type and code file count.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from pathlib import Path

import yaml
from pydantic import BaseModel, Field, ValidationError

from raise_cli.config.paths import MANIFEST_FILE, get_raise_dir
from raise_cli.onboarding.detection import ProjectType

logger = logging.getLogger(__name__)


class ProjectInfo(BaseModel):
    """Information about the project detected during init.

    Attributes:
        name: Project name (usually directory name).
        project_type: Whether greenfield or brownfield.
        code_file_count: Number of code files detected.
        detected_at: When the project was initialized.
    """

    name: str
    project_type: ProjectType
    code_file_count: int = 0
    detected_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ProjectManifest(BaseModel):
    """Project manifest stored in .raise/manifest.yaml.

    Attributes:
        version: Manifest schema version.
        project: Project information.
    """

    version: str = "1.0"
    project: ProjectInfo


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
