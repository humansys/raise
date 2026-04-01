"""Confluence discovery service — structured space and page tree queries.

Internal service consumed by doctor and config generator (D1: not a CLI command).
Wraps ConfluenceClient methods into a structured ConfluenceSpaceMap.

RAISE-1130 (S1130.1)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field

from raise_cli.adapters.confluence_exceptions import ConfluenceNotFoundError
from raise_cli.adapters.models.docs import PageSummary, SpaceInfo

if TYPE_CHECKING:
    from raise_cli.adapters.confluence_client import ConfluenceClient


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
                pages = self._client.get_page_children(space.key)
                top_level_pages[space.key] = pages
            except Exception:  # noqa: BLE001 — discovery is best-effort per space
                top_level_pages[space.key] = []

        return ConfluenceSpaceMap(spaces=spaces, top_level_pages=top_level_pages)
