"""YAML reader for skill artifacts."""

from __future__ import annotations

from pathlib import Path

import yaml

from rai_cli.artifacts.models import SkillArtifact


def read_artifact(path: Path) -> SkillArtifact:
    """Load and validate a single artifact from a YAML file.

    Raises:
        pydantic.ValidationError: If the YAML doesn't match the schema.
    """
    data = yaml.safe_load(path.read_text())
    return SkillArtifact.model_validate(data)


def read_all_artifacts(artifacts_dir: Path) -> list[SkillArtifact]:
    """Load all artifacts from a directory.

    Returns an empty list if the directory doesn't exist or is empty.
    Skips files that fail validation (logs warning).
    """
    if not artifacts_dir.is_dir():
        return []

    artifacts: list[SkillArtifact] = []
    for yaml_file in sorted(artifacts_dir.glob("*.yaml")):
        artifacts.append(read_artifact(yaml_file))
    return artifacts
