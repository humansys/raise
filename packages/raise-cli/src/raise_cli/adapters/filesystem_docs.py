"""Filesystem documentation target — writes artifacts as local markdown files.

Implements DocumentationTarget for local file storage. Used standalone
(offline/no Confluence) or as part of CompositeDocTarget for dual-write.

RAISE-1051 (S1051.7)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from raise_cli.adapters.models.docs import PageContent, PageSummary, PublishResult
from raise_cli.adapters.models.health import AdapterHealth


class FilesystemDocsTarget:
    """Writes documentation artifacts as local markdown files.

    File path comes from metadata["path"] (relative to project root).
    No-arg constructor for entry point discovery: uses CWD as project root.
    """

    def __init__(self, project_root: Path | None = None) -> None:
        self._root = project_root or Path.cwd()

    def can_publish(self, doc_type: str, metadata: dict[str, Any]) -> bool:
        """True if metadata contains a file path."""
        return "path" in metadata

    def publish(
        self, doc_type: str, content: str, metadata: dict[str, Any]
    ) -> PublishResult:
        """Write content to local file at metadata['path']."""
        raw_path = metadata.get("path")
        if not raw_path:
            return PublishResult(
                success=False,
                message="metadata['path'] is required for filesystem publishing",
            )
        error = self._validate_frontmatter(content, doc_type)
        if error:
            return error
        path = self._root / raw_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        return PublishResult(
            success=True, url=str(path), message="Written to filesystem"
        )

    def _validate_frontmatter(
        self, content: str, doc_type: str
    ) -> PublishResult | None:
        """Validate frontmatter YAML. Returns PublishResult on failure, None on success."""
        if not content.startswith("---\n"):
            return None  # No frontmatter — pass through

        end = content.find("\n---\n", 4)
        if end == -1:
            end = content.find("\n---", 4)
            if end == -1:
                return None  # Malformed delimiters — treat as no frontmatter

        raw_yaml = content[4:end]

        try:
            data = yaml.safe_load(raw_yaml)
        except yaml.YAMLError as exc:
            return PublishResult(
                success=False, message=f"Unparseable YAML frontmatter: {exc}"
            )

        if data is None:
            return None  # Empty frontmatter (---\n--- with nothing between)

        if not isinstance(data, dict):
            return PublishResult(
                success=False,
                message=f"Frontmatter must be a YAML mapping, got {type(data).__name__}",
            )

        # Determine required fields
        required: set[str] = {"title", "status"}
        is_story = "story_id" in data or doc_type.startswith("story-")
        is_epic = "epic_id" in data or doc_type.startswith("epic-")

        if is_story:
            required |= {"story_id", "epic_id"}
        elif is_epic:
            required.add("epic_id")

        missing = required - data.keys()
        if missing:
            return PublishResult(
                success=False,
                message=f"Missing required frontmatter fields: {sorted(missing)}",
            )

        return None

    def get_page(self, identifier: str) -> PageContent:
        """Not supported — filesystem is write-only target."""
        raise NotImplementedError("FilesystemDocsTarget does not support get_page")

    def search(self, query: str, limit: int = 10) -> list[PageSummary]:
        """Not supported — returns empty list."""
        return []

    def health(self) -> AdapterHealth:
        """Always healthy — filesystem is always available."""
        return AdapterHealth(name="filesystem-docs", healthy=True)
