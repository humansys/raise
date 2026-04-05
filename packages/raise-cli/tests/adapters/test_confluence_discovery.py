"""Tests for ConfluenceDiscovery service.

S1130.1 — covers all 4 Gherkin scenarios from s1130.1-story.md.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from raise_cli.adapters.confluence_discovery import (
    ConfluenceDiscovery,
    ConfluenceDiscoveryService,
    ConfluenceSpaceMap,
    DiscoveryError,
    PageNode,
    SpaceMap,
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


# ══════════════════════════════════════════════════════════════════════
# S1051.4 — ConfluenceDiscoveryService (V2)
# ══════════════════════════════════════════════════════════════════════

# ── PageNode model tests ────────────────────────────────────────────


class TestPageNode:
    def test_construction_minimal(self) -> None:
        node = PageNode(id="1", title="Root")
        assert node.id == "1"
        assert node.title == "Root"
        assert node.labels == []
        assert node.children == []

    def test_construction_with_labels(self) -> None:
        node = PageNode(id="1", title="Root", labels=["adr", "docs"])
        assert node.labels == ["adr", "docs"]

    def test_recursive_children(self) -> None:
        child = PageNode(id="2", title="Child")
        parent = PageNode(id="1", title="Parent", children=[child])
        assert len(parent.children) == 1
        assert parent.children[0].id == "2"

    def test_deep_nesting(self) -> None:
        leaf = PageNode(id="3", title="Leaf")
        mid = PageNode(id="2", title="Mid", children=[leaf])
        root = PageNode(id="1", title="Root", children=[mid])
        assert root.children[0].children[0].id == "3"


# ── SpaceMap model tests ────────────────────────────────────────────


class TestSpaceMap:
    def test_construction(self) -> None:
        space = SpaceInfo(key="DEV", name="Dev", url="/wiki/spaces/DEV", type="global")
        root = PageNode(id="1", title="Home")
        smap = SpaceMap(
            space=space,
            homepage_id="1",
            page_tree=root,
            label_index={"adr": ["2", "3"]},
        )
        assert smap.space.key == "DEV"
        assert smap.homepage_id == "1"
        assert smap.page_tree.title == "Home"
        assert smap.label_index == {"adr": ["2", "3"]}


# ── DiscoveryError tests ────────────────────────────────────────────


class TestDiscoveryError:
    def test_message(self) -> None:
        err = DiscoveryError("something failed")
        assert err.message == "something failed"
        assert str(err) == "something failed"
        assert err.cause is None

    def test_with_cause(self) -> None:
        cause = ValueError("root cause")
        err = DiscoveryError("wrapped", cause=cause)
        assert err.cause is cause
        assert isinstance(err, Exception)


# ── ConfluenceDiscoveryService init tests ────────────────────────────


class TestServiceInit:
    def test_takes_client(self) -> None:
        client = MagicMock()
        service = ConfluenceDiscoveryService(client)
        # Verify service works with the client by calling a method
        client.get_spaces.return_value = []
        assert service.discover_spaces() == []


# ── Helper: build a V2-capable mock client ──────────────────────────


def _make_v2_client(
    *,
    spaces: list[SpaceInfo] | None = None,
    homepage_ids: dict[str, str | None] | None = None,
    children: dict[str, list[PageSummary]] | None = None,
    labels: dict[str, list[str]] | None = None,
    page_titles: dict[str, str] | None = None,
) -> MagicMock:
    """Build a mocked ConfluenceClient for V2 discovery service tests."""
    client = MagicMock()
    client.get_spaces.return_value = spaces or []

    _homepage_ids: dict[str, str | None] = homepage_ids or {}

    def _get_homepage(sk: str) -> str | None:
        return _homepage_ids.get(sk)

    client.get_space_homepage_id.side_effect = _get_homepage

    _children: dict[str, list[PageSummary]] = children or {}

    def _get_children(pid: str) -> list[PageSummary]:
        return _children.get(pid, [])

    client.get_page_children.side_effect = _get_children

    _labels: dict[str, list[str]] = labels or {}

    def _get_labels(pid: str) -> list[str]:
        return _labels.get(pid, [])

    client.get_labels.side_effect = _get_labels

    _titles: dict[str, str] = page_titles or {}

    def _get_page(pid: str) -> MagicMock:
        return MagicMock(title=_titles.get(pid, ""))

    client.get_page_by_id.side_effect = _get_page

    return client


# ── TestServiceDiscoverSpaces ────────────────────────────────────────


class TestServiceDiscoverSpaces:
    def test_delegates_to_client(self) -> None:
        client = _make_v2_client(spaces=[SPACE_A, SPACE_B])
        service = ConfluenceDiscoveryService(client)

        result = service.discover_spaces()

        assert len(result) == 2
        assert result[0].key == "SPACEA"
        client.get_spaces.assert_called_once()

    def test_empty_returns_empty(self) -> None:
        client = _make_v2_client(spaces=[])
        service = ConfluenceDiscoveryService(client)

        result = service.discover_spaces()

        assert result == []

    def test_wraps_client_error(self) -> None:
        from raise_cli.adapters.confluence_exceptions import ConfluenceApiError

        client = _make_v2_client()
        client.get_spaces.side_effect = ConfluenceApiError("503 Service Unavailable")
        service = ConfluenceDiscoveryService(client)

        with pytest.raises(DiscoveryError, match="discover_spaces") as exc_info:
            service.discover_spaces()

        assert exc_info.value.cause is not None


# ── TestServiceDiscoverPageTree ──────────────────────────────────────


class TestServiceDiscoverPageTree:
    def test_builds_tree_from_homepage(self) -> None:
        client = _make_v2_client(
            homepage_ids={"RaiSE1": "100"},
            page_titles={"100": "Home"},
            children={
                "100": [
                    PageSummary(id="101", title="ADR", url="", space_key="RaiSE1"),
                    PageSummary(id="102", title="Roadmap", url="", space_key="RaiSE1"),
                ]
            },
            labels={"100": [], "101": ["adr"], "102": ["roadmap"]},
        )
        service = ConfluenceDiscoveryService(client)

        tree = service.discover_page_tree("RaiSE1", max_depth=1)

        assert tree.id == "100"
        assert tree.title == "Home"
        assert len(tree.children) == 2
        assert tree.children[0].id == "101"
        assert tree.children[0].labels == ["adr"]
        assert tree.children[1].id == "102"

    def test_respects_max_depth(self) -> None:
        """max_depth=1 means homepage + direct children, no grandchildren."""
        client = _make_v2_client(
            homepage_ids={"S": "1"},
            page_titles={"1": "Root"},
            children={
                "1": [PageSummary(id="2", title="Child", url="", space_key="S")],
                "2": [PageSummary(id="3", title="Grandchild", url="", space_key="S")],
            },
            labels={},
        )
        service = ConfluenceDiscoveryService(client)

        tree = service.discover_page_tree("S", max_depth=1)

        assert len(tree.children) == 1
        assert tree.children[0].id == "2"
        # Grandchildren should NOT be fetched at max_depth=1
        assert tree.children[0].children == []

    def test_recursive_depth_2(self) -> None:
        """max_depth=2 gets grandchildren but not great-grandchildren."""
        client = _make_v2_client(
            homepage_ids={"S": "1"},
            page_titles={"1": "Root"},
            children={
                "1": [PageSummary(id="2", title="Child", url="", space_key="S")],
                "2": [PageSummary(id="3", title="Grandchild", url="", space_key="S")],
                "3": [PageSummary(id="4", title="Great", url="", space_key="S")],
            },
            labels={},
        )
        service = ConfluenceDiscoveryService(client)

        tree = service.discover_page_tree("S", max_depth=2)

        assert tree.children[0].children[0].id == "3"
        assert tree.children[0].children[0].children == []

    def test_no_homepage_raises_discovery_error(self) -> None:
        client = _make_v2_client(homepage_ids={"S": None})
        service = ConfluenceDiscoveryService(client)

        with pytest.raises(DiscoveryError, match="no homepage"):
            service.discover_page_tree("S")

    def test_wraps_api_error(self) -> None:
        from raise_cli.adapters.confluence_exceptions import ConfluenceApiError

        client = _make_v2_client()
        client.get_space_homepage_id.side_effect = ConfluenceApiError("503")
        service = ConfluenceDiscoveryService(client)

        with pytest.raises(DiscoveryError, match="discover_page_tree") as exc_info:
            service.discover_page_tree("S")

        assert isinstance(exc_info.value.cause, ConfluenceApiError)


# ── TestServiceDiscoverLabels ────────────────────────────────────────


class TestServiceDiscoverLabels:
    def test_returns_labels_per_page(self) -> None:
        client = _make_v2_client(labels={"101": ["adr", "arch"], "102": ["roadmap"]})
        service = ConfluenceDiscoveryService(client)

        result = service.discover_labels(["101", "102"])

        assert result == {"101": ["adr", "arch"], "102": ["roadmap"]}

    def test_missing_page_returns_empty_list(self) -> None:
        """Graceful degradation: missing/deleted pages get empty labels (S1)."""
        client = _make_v2_client(labels={})

        # Make get_labels raise ConfluenceNotFoundError for unknown pages
        def _empty_labels(_pid: str) -> list[str]:
            return []

        client.get_labels.side_effect = _empty_labels
        service = ConfluenceDiscoveryService(client)

        result = service.discover_labels(["99999"])

        assert result == {"99999": []}

    def test_wraps_api_error(self) -> None:
        from raise_cli.adapters.confluence_exceptions import ConfluenceApiError

        client = _make_v2_client()
        client.get_labels.side_effect = ConfluenceApiError("500")
        service = ConfluenceDiscoveryService(client)

        with pytest.raises(DiscoveryError, match="discover_labels"):
            service.discover_labels(["101"])


# ── TestServiceBuildSpaceMap ─────────────────────────────────────────


class TestServiceBuildSpaceMap:
    def test_composite_result(self) -> None:
        client = _make_v2_client(
            spaces=[SPACE_A],
            homepage_ids={"SPACEA": "1000"},
            page_titles={"1000": "Space A Home"},
            children={
                "1000": [
                    PageSummary(id="1001", title="ADR", url="", space_key="SPACEA"),
                ]
            },
            labels={"1000": [], "1001": ["adr", "architecture"]},
        )
        service = ConfluenceDiscoveryService(client)

        result = service.build_space_map("SPACEA", max_depth=1)

        assert isinstance(result, SpaceMap)
        assert result.space.key == "SPACEA"
        assert result.homepage_id == "1000"
        assert result.page_tree.id == "1000"
        assert len(result.page_tree.children) == 1
        # Label index is inverted
        assert result.label_index == {
            "adr": ["1001"],
            "architecture": ["1001"],
        }

    def test_nonexistent_space_raises_discovery_error(self) -> None:
        client = _make_v2_client(spaces=[SPACE_A])
        service = ConfluenceDiscoveryService(client)

        with pytest.raises(DiscoveryError, match="NONEXISTENT.*not found"):
            service.build_space_map("NONEXISTENT")

    def test_label_index_from_multiple_pages(self) -> None:
        """Label index collects page IDs across the tree."""
        client = _make_v2_client(
            spaces=[SPACE_A],
            homepage_ids={"SPACEA": "1"},
            page_titles={"1": "Home"},
            children={
                "1": [
                    PageSummary(id="2", title="P2", url="", space_key="SPACEA"),
                    PageSummary(id="3", title="P3", url="", space_key="SPACEA"),
                ]
            },
            labels={"1": ["root"], "2": ["shared", "adr"], "3": ["shared"]},
        )
        service = ConfluenceDiscoveryService(client)

        result = service.build_space_map("SPACEA", max_depth=1)

        assert "shared" in result.label_index
        assert set(result.label_index["shared"]) == {"2", "3"}
        assert result.label_index["root"] == ["1"]
        assert result.label_index["adr"] == ["2"]


# ── TestBuildLabelIndex (static method) ──────────────────────────────


class TestBuildLabelIndex:
    def test_empty_tree(self) -> None:
        tree = PageNode(id="1", title="Root")
        index = ConfluenceDiscoveryService.build_label_index(tree)
        assert index == {}

    def test_single_level(self) -> None:
        tree = PageNode(id="1", title="Root", labels=["a", "b"])
        index = ConfluenceDiscoveryService.build_label_index(tree)
        assert index == {"a": ["1"], "b": ["1"]}

    def test_multi_level(self) -> None:
        tree = PageNode(
            id="1",
            title="Root",
            labels=["shared"],
            children=[
                PageNode(id="2", title="C1", labels=["shared", "unique"]),
                PageNode(id="3", title="C2", labels=["other"]),
            ],
        )
        index = ConfluenceDiscoveryService.build_label_index(tree)
        assert set(index["shared"]) == {"1", "2"}
        assert index["unique"] == ["2"]
        assert index["other"] == ["3"]


# ── TestWrapError ────────────────────────────────────────────────────


# ── RAISE-1187: Mixed-case space key fallback ─────────────────────────


SPACE_MIXED = SpaceInfo(
    key="RaiSE1", name="RaiSE Documentation", url="/wiki/spaces/RaiSE1", type="global"
)


class TestDiscoverFallbackForMissingSpace:
    """RAISE-1187: discover(space_key=...) should fall back to direct lookup
    when get_spaces() omits the space (mixed-case key upstream quirk)."""

    def test_v1_discover_falls_back_to_direct_lookup(self) -> None:
        """V1: discover(space_key="RaiSE1") succeeds even if get_spaces() omits it."""
        client = _make_client(
            spaces=[SPACE_A],  # RaiSE1 NOT in enumerated spaces
            homepage_ids={"RaiSE1": "5000"},
            children={"5000": [PAGE_1]},
        )
        # Direct lookup returns the space
        client.get_space_direct.return_value = SPACE_MIXED
        discovery = ConfluenceDiscovery(client)

        result = discovery.discover(space_key="RaiSE1")

        assert len(result.spaces) == 1
        assert result.spaces[0].key == "RaiSE1"
        client.get_space_direct.assert_called_once_with("RaiSE1")

    def test_v1_discover_still_raises_when_truly_missing(self) -> None:
        """V1: truly nonexistent space raises even after fallback attempt."""
        client = _make_client(spaces=[SPACE_A])
        client.get_space_direct.return_value = None
        discovery = ConfluenceDiscovery(client)

        with pytest.raises(ConfluenceNotFoundError, match="NONEXISTENT"):
            discovery.discover(space_key="NONEXISTENT")

    def test_v2_build_space_map_falls_back_to_direct_lookup(self) -> None:
        """V2: build_space_map("RaiSE1") succeeds even if get_spaces() omits it."""
        client = _make_v2_client(
            spaces=[SPACE_A],  # RaiSE1 NOT in enumerated spaces
            homepage_ids={"RaiSE1": "5000"},
            page_titles={"5000": "RaiSE Home"},
            children={
                "5000": [
                    PageSummary(id="5001", title="ADR", url="", space_key="RaiSE1"),
                ]
            },
            labels={"5000": [], "5001": ["adr"]},
        )
        client.get_space_direct.return_value = SPACE_MIXED
        service = ConfluenceDiscoveryService(client)

        result = service.build_space_map("RaiSE1", max_depth=1)

        assert result.space.key == "RaiSE1"
        assert result.homepage_id == "5000"
        client.get_space_direct.assert_called_once_with("RaiSE1")

    def test_v2_build_space_map_still_raises_when_truly_missing(self) -> None:
        """V2: truly nonexistent space raises DiscoveryError after fallback."""
        client = _make_v2_client(spaces=[SPACE_A])
        client.get_space_direct.return_value = None
        service = ConfluenceDiscoveryService(client)

        with pytest.raises(DiscoveryError, match="NONEXISTENT.*not found"):
            service.build_space_map("NONEXISTENT")


class TestWrapError:
    def test_wraps_generic_exception(self) -> None:
        client = MagicMock()
        service = ConfluenceDiscoveryService(client)
        cause = RuntimeError("boom")

        result = service.wrap_error(cause, "test_context")

        assert isinstance(result, DiscoveryError)
        assert result.message == "test_context: boom"
        assert result.cause is cause

    def test_passes_through_discovery_error(self) -> None:
        client = MagicMock()
        service = ConfluenceDiscoveryService(client)
        original = DiscoveryError("already wrapped")

        result = service.wrap_error(original, "context")

        assert result is original
