"""Filesystem documentation target — writes artifacts as local markdown files.

Implements DocumentationTarget for local file storage. Used standalone
(offline/no Confluence) or as part of CompositeDocTarget for dual-write.

RAISE-1051 (S1051.7)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

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
        path = self._root / raw_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        return PublishResult(
            success=True, url=str(path), message="Written to filesystem"
        )

    def get_page(self, identifier: str) -> PageContent:
        """Not supported — filesystem is write-only target."""
        raise NotImplementedError("FilesystemDocsTarget does not support get_page")

    def search(self, query: str, limit: int = 10) -> list[PageSummary]:
        """Not supported — returns empty list."""
        return []

    def health(self) -> AdapterHealth:
        """Always healthy — filesystem is always available."""
        return AdapterHealth(name="filesystem-docs", healthy=True)
