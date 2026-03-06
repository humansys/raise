"""YAML reader for skill artifacts."""

from __future__ import annotations

from pathlib import Path

import yaml

from raise_cli.artifacts.models import SkillArtifact

# Lazy import to avoid circular dependency
_artifact_registry: dict[str, type[SkillArtifact]] | None = None


def _get_registry() -> dict[str, type[SkillArtifact]]:
    """Build the artifact type registry on first access."""
    global _artifact_registry  # noqa: PLW0603
    if _artifact_registry is None:
        from raise_cli.artifacts.story_design import StoryDesignArtifact

        _artifact_registry = {
            "story-design": StoryDesignArtifact,
        }
    return _artifact_registry


def read_artifact(path: Path) -> SkillArtifact:
    """Load and validate a single artifact from a YAML file.

    Dispatches to the correct model subclass based on ``artifact_type``.
    Falls back to ``SkillArtifact`` (base) for unknown types.

    Raises:
        pydantic.ValidationError: If the YAML doesn't match the schema.
    """
    data = yaml.safe_load(path.read_text())
    artifact_type = data.get("artifact_type", "")
    registry = _get_registry()
    model_class = registry.get(artifact_type, SkillArtifact)
    return model_class.model_validate(data)


def read_all_artifacts(artifacts_dir: Path) -> list[SkillArtifact]:
    """Load all artifacts from a directory.

    Returns an empty list if the directory doesn't exist or is empty.
    Raises ``ValidationError`` if any file fails validation.
    """
    if not artifacts_dir.is_dir():
        return []

    artifacts: list[SkillArtifact] = []
    for yaml_file in sorted(artifacts_dir.glob("*.yaml")):
        artifacts.append(read_artifact(yaml_file))
    return artifacts
