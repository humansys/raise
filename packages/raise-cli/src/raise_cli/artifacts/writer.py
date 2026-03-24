"""YAML writer for skill artifacts."""

from __future__ import annotations

from pathlib import Path

import yaml

from raise_cli.artifacts.models import SkillArtifact


def _artifact_filename(artifact: SkillArtifact) -> str:
    """Derive filename from artifact story/epic and type.

    Convention: ``{id}-{type_suffix}.yaml``
    where type_suffix strips the first segment (e.g., ``story-design`` → ``design``).
    """
    # Use story if available, else epic
    work_id = artifact.story or artifact.epic or "unknown"
    work_id = work_id.lower()

    # Strip prefix from artifact type: "story-design" → "design"
    type_suffix = artifact.artifact_type.value.split("-", 1)[-1]

    return f"{work_id}-{type_suffix}.yaml"


def write_artifact(artifact: SkillArtifact, project_root: Path) -> Path:
    """Serialize artifact to YAML in ``.raise/artifacts/``.

    Creates the directory if it doesn't exist.

    Returns:
        Path to the written YAML file.
    """
    artifacts_dir = project_root / ".raise" / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    filename = _artifact_filename(artifact)
    path = artifacts_dir / filename

    data = artifact.model_dump(mode="json")
    path.write_text(yaml.dump(data, default_flow_style=False, sort_keys=False))

    return path
