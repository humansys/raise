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
                # Fallback: get_all_spaces() may omit mixed-case keys (RAISE-1187)
                direct = self._client.get_space_direct(space_key)
                if direct is None:
                    raise ConfluenceNotFoundError(
                        f"Space '{space_key}' not found. "
                        f"Available: {', '.join(s.key for s in all_spaces)}"
                    )
                logger.info(
                    "Space '%s' not in enumerated results, found via direct lookup",
                    space_key,
                )
                matched = [direct]
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
        try:
            return self._client.get_spaces()
        except DiscoveryError:
            raise
        except Exception as e:
            raise self.wrap_error(e, "discover_spaces") from e

    def discover_page_tree(
        self, space_key: str, max_depth: int = DEFAULT_MAX_DEPTH
    ) -> PageNode:
        """Build recursive page tree from space homepage.

        Resolves homepage via client.get_space_homepage_id(),
        then walks children recursively up to max_depth.
        Labels are fetched per page during the walk.
        """
        try:
            homepage_id = self._client.get_space_homepage_id(space_key)
            if not homepage_id:
                raise DiscoveryError(
                    f"discover_page_tree({space_key}): space has no homepage"
                )
            homepage_page = self._client.get_page_by_id(homepage_id)
            homepage_labels = self._client.get_labels(homepage_id)
            root = PageNode(
                id=homepage_id,
                title=homepage_page.title,
                labels=homepage_labels,
                children=self._walk_children(homepage_id, depth=1, max_depth=max_depth),
            )
            return root
        except DiscoveryError:
            raise
        except Exception as e:
            raise self.wrap_error(e, f"discover_page_tree({space_key})") from e

    def discover_labels(self, page_ids: list[str]) -> dict[str, list[str]]:
        """Get labels for a list of pages. Returns {page_id: [label, ...]}.

        Missing or deleted pages return an empty list (graceful degradation).
        """
        try:
            result: dict[str, list[str]] = {}
            for page_id in page_ids:
                try:
                    result[page_id] = self._client.get_labels(page_id)
                except ConfluenceNotFoundError:
                    result[page_id] = []
            return result
        except DiscoveryError:
            raise
        except Exception as e:
            raise self.wrap_error(e, "discover_labels") from e

    def build_space_map(
        self, space_key: str, max_depth: int = DEFAULT_MAX_DEPTH
    ) -> SpaceMap:
        """Composite: space info + page tree + label index.

        1. Find space in discover_spaces() by key
        2. Build page tree with labels
        3. Build inverted label index from tree
        """
        try:
            spaces = self.discover_spaces()
            matched = [s for s in spaces if s.key == space_key]
            if not matched:
                # Fallback: get_all_spaces() may omit mixed-case keys (RAISE-1187)
                direct = self._client.get_space_direct(space_key)
                if direct is None:
                    raise DiscoveryError(
                        f"build_space_map: space '{space_key}' not found"
                    )
                logger.info(
                    "Space '%s' not in enumerated results, found via direct lookup",
                    space_key,
                )
                matched = [direct]
            space_info = matched[0]
            tree = self.discover_page_tree(space_key, max_depth)
            label_index = self.build_label_index(tree)
            return SpaceMap(
                space=space_info,
                homepage_id=tree.id,
                page_tree=tree,
                label_index=label_index,
            )
        except DiscoveryError:
            raise
        except Exception as e:
            raise self.wrap_error(e, f"build_space_map({space_key})") from e

    def _walk_children(
        self, page_id: str, depth: int, max_depth: int
    ) -> list[PageNode]:
        """Recursive child page walk with depth limit."""
        if depth > max_depth:
            return []
        children_summaries = self._client.get_page_children(page_id)
        nodes: list[PageNode] = []
        for child in children_summaries:
            labels = self._client.get_labels(child.id)
            grandchildren = self._walk_children(child.id, depth + 1, max_depth)
            nodes.append(
                PageNode(
                    id=child.id,
                    title=child.title,
                    labels=labels,
                    children=grandchildren,
                )
            )
        return nodes

    @staticmethod
    def build_label_index(tree: PageNode) -> dict[str, list[str]]:
        """Build inverted index: label -> [page_id, ...] from tree."""
        index: dict[str, list[str]] = {}
        stack: list[PageNode] = [tree]
        while stack:
            node = stack.pop()
            for label in node.labels:
                index.setdefault(label, []).append(node.id)
            stack.extend(node.children)
        return index

    def wrap_error(self, error: Exception, context: str) -> DiscoveryError:
        """Wrap any exception in DiscoveryError with context."""
        if isinstance(error, DiscoveryError):
            return error
        return DiscoveryError(f"{context}: {error}", cause=error)
