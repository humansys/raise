"""YAML pipeline loader with multi-tier resolution.

Loads pipeline definitions from YAML files across configurable search paths.
Higher-priority tiers (later in search_paths) override lower-priority ones.

Story: S1064.2 — YAML Pipeline Loader (RAISE-1074)
Epic: E1064 — Pipeline Engine Core
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

import yaml
from pydantic import ValidationError

from raise_cli.exceptions import RaiError
from raise_core.workflow.models import PipelineDefinition


class PipelineError(RaiError):
    """Raised when a pipeline cannot be loaded.

    Covers: pipeline not found, YAML parse error, schema validation failure.
    Messages always include relevant context (pipeline name, file path).
    """

    exit_code: int = 8
    error_code: str = "E008"


class PipelineLoader:
    """Loads pipeline definitions from YAML files across ordered search paths.

    Args:
        search_paths: Directories to search, ordered lowest-priority first.
            The last directory wins when the same pipeline name exists in
            multiple tiers. Non-existent directories are silently skipped.
    """

    def __init__(self, search_paths: Sequence[Path]) -> None:
        self._search_paths = list(search_paths)

    @property
    def search_paths(self) -> list[Path]:
        """Ordered search paths (lowest priority first)."""
        return list(self._search_paths)

    def load(self, name: str) -> PipelineDefinition:
        """Load a pipeline definition by name.

        Searches directories in reverse order (highest priority first).
        Parses YAML and validates against PipelineDefinition schema.
        Validates sub-pipeline references (depth-1 enforcement).

        Args:
            name: Pipeline name (without .yaml extension).

        Returns:
            Validated PipelineDefinition.

        Raises:
            PipelineError: If pipeline not found, YAML invalid, schema fails,
                or sub-pipeline nesting exceeds depth 1.
        """
        yaml_path = self._resolve(name)
        raw = self._parse_yaml(yaml_path)
        definition = self._validate(raw, yaml_path)
        self._validate_sub_pipelines(definition)
        return definition

    def _validate_sub_pipelines(self, definition: PipelineDefinition) -> None:
        """Resolve sub-pipeline references and enforce depth-1."""
        for phase in definition.phases:
            if phase.pipeline is None:
                continue
            sub_path = self._resolve(phase.pipeline)
            sub_raw = self._parse_yaml(sub_path)
            sub_def = self._validate(sub_raw, sub_path)
            for sub_phase in sub_def.phases:
                if sub_phase.pipeline is not None:
                    msg = (
                        f"sub-pipeline '{phase.pipeline}' phase '{sub_phase.id}' "
                        f"declares pipeline '{sub_phase.pipeline}' — "
                        f"nesting depth > 1 is not allowed"
                    )
                    raise PipelineError(msg)

    def list_available(self) -> list[str]:
        """Return sorted, deduplicated pipeline names across all tiers.

        Scans all search paths for .yaml files. Non-existent directories
        are silently skipped.

        Returns:
            Sorted list of pipeline names (without .yaml extension).
        """
        names: set[str] = set()
        for search_path in self._search_paths:
            if not search_path.is_dir():
                continue
            for yaml_file in search_path.glob("*.yaml"):
                names.add(yaml_file.stem)
        return sorted(names)

    def _resolve(self, name: str) -> Path:
        """Find the highest-priority YAML file for a pipeline name."""
        if not name or "/" in name or "\\" in name or name.startswith("."):
            msg = f"invalid pipeline name '{name}': must be a simple identifier"
            raise PipelineError(msg)
        filename = f"{name}.yaml"
        # Reverse iterate: last path has highest priority
        for search_path in reversed(self._search_paths):
            candidate = search_path / filename
            if candidate.is_file():
                return candidate
        msg = f"pipeline '{name}' not found in search paths"
        raise PipelineError(msg)

    def _parse_yaml(self, path: Path) -> dict[str, object]:
        """Parse YAML file, wrapping errors with file path context."""
        try:
            text = path.read_text()
            data = yaml.safe_load(text)
        except yaml.YAMLError as exc:
            msg = f"invalid YAML in {path}: {exc}"
            raise PipelineError(msg) from exc
        if not isinstance(data, dict):
            msg = f"invalid YAML in {path}: expected mapping, got {type(data).__name__}"
            raise PipelineError(msg)
        return data  # type: ignore[return-value]

    def _validate(self, raw: dict[str, object], path: Path) -> PipelineDefinition:
        """Validate raw dict against PipelineDefinition schema."""
        try:
            return PipelineDefinition.model_validate(raw)
        except ValidationError as exc:
            msg = f"schema validation failed for {path}: {exc}"
            raise PipelineError(msg) from exc


def create_loader(project_root: Path | None = None) -> PipelineLoader:
    """Create a PipelineLoader with default 3-tier search paths.

    Tiers (lowest to highest priority):
        1. Built-in: ``<package>/pipelines_base/``
        2. Project: ``{project_root}/.raise/pipelines/`` (if project_root given)
        3. User: ``~/.raise/pipelines/``

    Non-existent directories are silently skipped by PipelineLoader.

    Args:
        project_root: Project root directory. When None, project tier is omitted.

    Returns:
        Configured PipelineLoader.
    """
    # Built-in pipelines ship alongside this package
    builtin_dir = Path(__file__).parent / "pipelines_base"
    user_dir = Path.home() / ".raise" / "pipelines"

    paths: list[Path] = [builtin_dir]
    if project_root is not None:
        paths.append(project_root / ".raise" / "pipelines")
    paths.append(user_dir)

    return PipelineLoader(search_paths=paths)
