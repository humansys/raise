"""Tests for ConfluenceDiscovery service.

S1130.1 — covers all 4 Gherkin scenarios from s1130.1-story.md.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from raise_cli.adapters.confluence_discovery import (
    ConfluenceDiscovery,
    ConfluenceSpaceMap,
)
from raise_cli.adapters.confluence_exceptions import (
    ConfluenceAuthError,
    ConfluenceNotFoundError,
)
from raise_cli.adapters.models.docs import PageSummary, SpaceInfo


def _make_client(
    spaces: list[SpaceInfo] | None = None,
    homepage_ids: dict[str, str] | None = None,
    children: dict[str, list[PageSummary]] | None = None,
    auth_error: bool = False,
) -> MagicMock:
    """Build a mocked ConfluenceClient."""
    client = MagicMock()

    if auth_error:
        client.get_spaces.side_effect = ConfluenceAuthError("Invalid credentials")
        return client

    client.get_spaces.return_value = spaces or []

    _homepage_ids = homepage_ids or {}

    def _get_homepage_id(space_key: str) -> str | None:
        return _homepage_ids.get(space_key)

    client.get_space_homepage_id.side_effect = _get_homepage_id

    _children = children or {}

    def _get_children(page_id: str) -> list[PageSummary]:
        return _children.get(page_id, [])

    client.get_page_children.side_effect = _get_children
    return client


# ── Fixtures ─────────────────────────────────────────────────────────

SPACE_A = SpaceInfo(
    key="SPACEA", name="Space A", url="/wiki/spaces/SPACEA", type="global"
)
SPACE_B = SpaceInfo(
    key="SPACEB", name="Space B", url="/wiki/spaces/SPACEB", type="global"
)

PAGE_1 = PageSummary(id="101", title="Page 1", url="/page/101", space_key="SPACEA")
PAGE_2 = PageSummary(id="102", title="Page 2", url="/page/102", space_key="SPACEA")

HOMEPAGE_IDS = {"SPACEA": "1000", "SPACEB": "2000"}


# ── Scenario 1: Discover all accessible spaces ──────────────────────


class TestDiscoverAllSpaces:
    def test_returns_all_spaces(self) -> None:
        client = _make_client(spaces=[SPACE_A, SPACE_B], homepage_ids=HOMEPAGE_IDS)
        discovery = ConfluenceDiscovery(client)

        result = discovery.discover()

        assert isinstance(result, ConfluenceSpaceMap)
        assert len(result.spaces) == 2
        assert result.spaces[0].key == "SPACEA"
        assert result.spaces[1].key == "SPACEB"

    def test_spaces_have_required_fields(self) -> None:
        client = _make_client(spaces=[SPACE_A], homepage_ids=HOMEPAGE_IDS)
        discovery = ConfluenceDiscovery(client)

        result = discovery.discover()

        space = result.spaces[0]
        assert space.key == "SPACEA"
        assert space.name == "Space A"
        assert space.url == "/wiki/spaces/SPACEA"
        assert space.type == "global"

    def test_empty_instance_returns_empty_map(self) -> None:
        client = _make_client(spaces=[])
        discovery = ConfluenceDiscovery(client)

        result = discovery.discover()

        assert result.spaces == []
        assert result.top_level_pages == {}


# ── Scenario 2: Discover specific space with page tree ───────────────


class TestDiscoverSpecificSpace:
    def test_filters_to_requested_space(self) -> None:
        client = _make_client(spaces=[SPACE_A, SPACE_B], homepage_ids=HOMEPAGE_IDS)
        discovery = ConfluenceDiscovery(client)

        result = discovery.discover(space_key="SPACEA")

        assert len(result.spaces) == 1
        assert result.spaces[0].key == "SPACEA"

    def test_populates_top_level_pages_via_homepage(self) -> None:
        client = _make_client(
            spaces=[SPACE_A],
            homepage_ids={"SPACEA": "1000"},
            children={"1000": [PAGE_1, PAGE_2]},
        )
        discovery = ConfluenceDiscovery(client)

        result = discovery.discover(space_key="SPACEA")

        assert "SPACEA" in result.top_level_pages
        assert len(result.top_level_pages["SPACEA"]) == 2
        assert result.top_level_pages["SPACEA"][0].title == "Page 1"
        assert result.top_level_pages["SPACEA"][1].title == "Page 2"
        # Verify get_page_children was called with homepage ID, not space key
        client.get_page_children.assert_called_once_with("1000")

    def test_no_homepage_returns_empty_pages(self) -> None:
        client = _make_client(
            spaces=[SPACE_A],
            homepage_ids={},  # no homepage
        )
        discovery = ConfluenceDiscovery(client)

        result = discovery.discover(space_key="SPACEA")

        assert result.top_level_pages["SPACEA"] == []
        client.get_page_children.assert_not_called()


# ── Scenario 3: Handle inaccessible space ────────────────────────────


class TestDiscoverSpaceNotFound:
    def test_raises_not_found_for_missing_space(self) -> None:
        client = _make_client(spaces=[SPACE_A])
        discovery = ConfluenceDiscovery(client)

        with pytest.raises(ConfluenceNotFoundError, match="NONEXISTENT"):
            discovery.discover(space_key="NONEXISTENT")


# ── Scenario 4: Handle connection failure ────────────────────────────


class TestDiscoverAuthFailure:
    def test_propagates_auth_error(self) -> None:
        client = _make_client(auth_error=True)
        discovery = ConfluenceDiscovery(client)

        with pytest.raises(ConfluenceAuthError, match="Invalid credentials"):
            discovery.discover()


# ── Model tests ──────────────────────────────────────────────────────


class TestConfluenceSpaceMap:
    def test_is_frozen(self) -> None:
        space_map = ConfluenceSpaceMap(spaces=[SPACE_A], top_level_pages={})
        with pytest.raises(Exception):  # noqa: B017 — Pydantic ValidationError
            space_map.spaces = []  # type: ignore[misc]
