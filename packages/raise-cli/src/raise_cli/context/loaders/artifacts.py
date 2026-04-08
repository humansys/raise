"""Artifacts loader for the context graph.

Loads typed skill artifacts from .raise/artifacts/ as graph nodes.
"""

from __future__ import annotations

import logging
from pathlib import Path

from raise_core.graph.models import GraphNode

logger = logging.getLogger(__name__)


def load_artifacts(project_root: Path) -> list[GraphNode]:
    """Load typed skill artifacts from ``.raise/artifacts/``.

    Each artifact becomes a GraphNode with type ``artifact``.
    Malformed artifacts are skipped with a warning.

    Args:
        project_root: Root directory for the project.

    Returns:
        List of GraphNode for artifact concepts.
    """
    from raise_cli.artifacts.reader import read_artifact
    from raise_cli.artifacts.writer import (
        _artifact_filename,  # pyright: ignore[reportPrivateUsage]
    )

    artifacts_dir = project_root / ".raise" / "artifacts"
    if not artifacts_dir.is_dir():
        return []

    nodes: list[GraphNode] = []
    for yaml_file in sorted(artifacts_dir.glob("*.yaml")):
        try:
            artifact = read_artifact(yaml_file)
        except Exception:
            logger.debug("Skipping malformed artifact: %s", yaml_file.name)
            continue

        work_id = (artifact.story or artifact.epic or "unknown").lower()
        node_id = f"artifact-{work_id}-{artifact.artifact_type.value}"

        # Extract summary from content (typed or dict)
        if isinstance(artifact.content, dict):  # pyright: ignore[reportUnnecessaryIsInstance]
            summary = artifact.content.get("summary", str(artifact.content))
        else:
            summary = getattr(artifact.content, "summary", str(artifact.content))

        filename = _artifact_filename(artifact)

        node = GraphNode(
            id=node_id,
            type="artifact",
            content=summary,
            source_file=f".raise/artifacts/{filename}",
            created=artifact.created.isoformat(),
            metadata={
                "artifact_type": artifact.artifact_type.value,
                "skill": artifact.skill,
                "story": artifact.story,
                "epic": artifact.epic,
                "version": artifact.version,
            },
        )
        nodes.append(node)

    return nodes
