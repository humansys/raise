"""Confluence discovery service — structured space and page tree queries.

Internal service consumed by doctor and config generator (D1: not a CLI command).
Wraps ConfluenceClient methods into a structured ConfluenceSpaceMap.

RAISE-1130 (S1130.1)
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field

from raise_cli.adapters.confluence_exceptions import ConfluenceNotFoundError
from raise_cli.adapters.models.docs import PageSummary, SpaceInfo

if TYPE_CHECKING:
    from raise_cli.adapters.confluence_client import ConfluenceClient

logger = logging.getLogger(__name__)


class ConfluenceSpaceMap(BaseModel):
    """Discovered Confluence space structure."""

    model_config = ConfigDict(frozen=True)

    spaces: list[SpaceInfo] = Field(..., description="Discovered spaces")
    top_level_pages: dict[str, list[PageSummary]] = Field(
        ...,
        description="Space key → top-level pages under that space's homepage",
    )


class ConfluenceDiscovery:
    """Queries a Confluence instance for space and page tree structure.

    Consumed by AdapterDoctorCheck and config generator — not user-facing.
    """

    def __init__(self, client: ConfluenceClient) -> None:
        self._client = client

    def discover(self, space_key: str | None = None) -> ConfluenceSpaceMap:
        """Discover spaces and their top-level page trees.

        Args:
            space_key: If provided, filter to this space only.
                       Raises ConfluenceNotFoundError if not found.

        Returns:
            ConfluenceSpaceMap with spaces and top-level pages.
        """
        all_spaces = self._client.get_spaces()

        if space_key is not None:
            matched = [s for s in all_spaces if s.key == space_key]
            if not matched:
                raise ConfluenceNotFoundError(
                    f"Space '{space_key}' not found. "
                    f"Available: {', '.join(s.key for s in all_spaces)}"
                )
            spaces = matched
        else:
            spaces = all_spaces

        top_level_pages: dict[str, list[PageSummary]] = {}
        for space in spaces:
            try:
                homepage_id = self._client.get_space_homepage_id(space.key)
                if homepage_id:
                    pages = self._client.get_page_children(homepage_id)
                    top_level_pages[space.key] = pages
                else:
                    logger.debug("No homepage found for space %s", space.key)
                    top_level_pages[space.key] = []
            except Exception:  # noqa: BLE001 — discovery is best-effort per space
                logger.debug(
                    "Failed to get pages for space %s", space.key, exc_info=True
                )
                top_level_pages[space.key] = []

        return ConfluenceSpaceMap(spaces=spaces, top_level_pages=top_level_pages)


# ══════════════════════════════════════════════════════════════════════
# V2 Discovery Service — S1051.4
# ══════════════════════════════════════════════════════════════════════


class PageNode(BaseModel):
    """Recursive page tree node with labels."""

    id: str
    title: str
    labels: list[str] = Field(default_factory=list)
    children: list[PageNode] = Field(default_factory=list)  # pyright: ignore[reportUnknownVariableType]


PageNode.model_rebuild()  # resolve forward ref for recursive type


class DiscoveryError(Exception):
    """Discovery-layer error wrapping client errors."""

    def __init__(self, message: str, cause: Exception | None = None) -> None:
        self.message = message
        self.cause = cause
        super().__init__(message)


class SpaceMap(BaseModel):
    """Complete structural snapshot of a Confluence space."""

    space: SpaceInfo
    homepage_id: str
    page_tree: PageNode
    label_index: dict[str, list[str]]  # label -> [page_id, ...]


class ConfluenceDiscoveryService:
    """Queries live Confluence for structural metadata.

    Consumed by doctor (validation) and setup (config generation).
    All methods raise DiscoveryError on failure.

    RAISE-1057 (S1051.4)
    """

    DEFAULT_MAX_DEPTH: int = 3

    def __init__(self, client: ConfluenceClient) -> None:
        self._client = client

    def discover_spaces(self) -> list[SpaceInfo]:
        """List all accessible spaces."""
        raise NotImplementedError

    def discover_page_tree(
        self, space_key: str, max_depth: int = DEFAULT_MAX_DEPTH
    ) -> PageNode:
        """Build recursive page tree from space homepage."""
        raise NotImplementedError

    def discover_labels(self, page_ids: list[str]) -> dict[str, list[str]]:
        """Get labels for a list of pages. Returns {page_id: [label, ...]}."""
        raise NotImplementedError

    def build_space_map(
        self, space_key: str, max_depth: int = DEFAULT_MAX_DEPTH
    ) -> SpaceMap:
        """Composite: space info + page tree + label index."""
        raise NotImplementedError

    def _walk_children(
        self, page_id: str, depth: int, max_depth: int
    ) -> list[PageNode]:
        """Recursive child page walk with depth limit."""
        raise NotImplementedError

    @staticmethod
    def _build_label_index(tree: PageNode) -> dict[str, list[str]]:
        """Build inverted index: label -> [page_id, ...] from tree."""
        raise NotImplementedError

    def _wrap_error(self, error: Exception, context: str) -> DiscoveryError:
        """Wrap any exception in DiscoveryError with context."""
        if isinstance(error, DiscoveryError):
            return error
        return DiscoveryError(f"{context}: {error}", cause=error)
