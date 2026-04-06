"""Tests for Confluence config generator — S1051.6 (v2).

Tests generate_confluence_config() with v2 signature:
- spaces: list[SpaceInfo] (replaces ConfluenceSpaceMap)
- instance_name: str (new param)
- Multi-instance output format
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

from raise_cli.adapters.confluence_config import ArtifactRouting, ConfluenceConfig
from raise_cli.adapters.confluence_config_gen import (
    generate_confluence_config,
    suggest_routing,
    write_confluence_config,
)
from raise_cli.adapters.confluence_discovery import PageNode
from raise_cli.adapters.models.docs import SpaceInfo


def _sample_spaces() -> list[SpaceInfo]:
    """Create sample spaces for testing."""
    return [
        SpaceInfo(
            key="RaiSE1",
            name="RaiSE Documentation",
            url="/wiki/spaces/RaiSE1",
            type="global",
        ),
        SpaceInfo(
            key="OPS",
            name="Operations",
            url="/wiki/spaces/OPS",
            type="global",
        ),
    ]


class TestGenerateMultiInstanceFormat:
    """AC1: output passes ConfluenceConfig.from_dict()."""

    def test_returns_dict(self) -> None:
        result = generate_confluence_config(
            spaces=_sample_spaces(),
            selected_space="RaiSE1",
            instance_url="https://humansys.atlassian.net/wiki",
            instance_name="humansys",
        )
        assert isinstance(result, dict)

    def test_output_passes_from_dict_validation(self) -> None:
        result = generate_confluence_config(
            spaces=_sample_spaces(),
            selected_space="RaiSE1",
            instance_url="https://humansys.atlassian.net/wiki",
            instance_name="humansys",
        )
        config = ConfluenceConfig.from_dict(result)
        assert config.default_instance == "humansys"
        assert "humansys" in config.instances

    def test_instance_has_correct_url(self) -> None:
        result = generate_confluence_config(
            spaces=_sample_spaces(),
            selected_space="RaiSE1",
            instance_url="https://humansys.atlassian.net/wiki",
            instance_name="humansys",
        )
        config = ConfluenceConfig.from_dict(result)
        inst = config.get_instance("humansys")
        assert inst.url == "https://humansys.atlassian.net/wiki"

    def test_instance_has_correct_space_key(self) -> None:
        result = generate_confluence_config(
            spaces=_sample_spaces(),
            selected_space="RaiSE1",
            instance_url="https://humansys.atlassian.net/wiki",
            instance_name="humansys",
        )
        config = ConfluenceConfig.from_dict(result)
        inst = config.get_instance("humansys")
        assert inst.space_key == "RaiSE1"

    def test_instance_has_correct_instance_name(self) -> None:
        result = generate_confluence_config(
            spaces=_sample_spaces(),
            selected_space="RaiSE1",
            instance_url="https://humansys.atlassian.net/wiki",
            instance_name="humansys",
        )
        config = ConfluenceConfig.from_dict(result)
        inst = config.get_instance("humansys")
        assert inst.instance_name == "humansys"

    def test_default_instance_name_is_default(self) -> None:
        result = generate_confluence_config(
            spaces=_sample_spaces(),
            selected_space="RaiSE1",
            instance_url="https://humansys.atlassian.net/wiki",
        )
        config = ConfluenceConfig.from_dict(result)
        assert config.default_instance == "default"


class TestInvalidSpace:
    """AC2: ValueError when selected_space not in spaces list."""

    def test_raises_value_error(self) -> None:
        with pytest.raises(ValueError, match="NONEXISTENT"):
            generate_confluence_config(
                spaces=_sample_spaces(),
                selected_space="NONEXISTENT",
                instance_url="https://humansys.atlassian.net/wiki",
                instance_name="humansys",
            )

    def test_error_lists_available_spaces(self) -> None:
        with pytest.raises(ValueError, match="RaiSE1"):
            generate_confluence_config(
                spaces=_sample_spaces(),
                selected_space="MISSING",
                instance_url="https://humansys.atlassian.net/wiki",
            )


class TestRouting:
    """AC3: default routing applied when routing=None."""

    def test_default_routing_when_none(self) -> None:
        result = generate_confluence_config(
            spaces=_sample_spaces(),
            selected_space="RaiSE1",
            instance_url="https://humansys.atlassian.net/wiki",
            instance_name="humansys",
        )
        config = ConfluenceConfig.from_dict(result)
        inst = config.get_instance("humansys")
        assert "adr" in inst.routing
        assert "developer" in inst.routing

    def test_custom_routing_preserved(self) -> None:
        routing = {
            "adr": ArtifactRouting(
                parent_title="Architecture Decision Records", labels=["adr"]
            ),
            "roadmap": ArtifactRouting(parent_title="Roadmaps", labels=["roadmap"]),
        }
        result = generate_confluence_config(
            spaces=_sample_spaces(),
            selected_space="RaiSE1",
            instance_url="https://humansys.atlassian.net/wiki",
            instance_name="humansys",
            routing=routing,
        )
        config = ConfluenceConfig.from_dict(result)
        inst = config.get_instance("humansys")
        assert inst.routing["adr"].parent_title == "Architecture Decision Records"
        assert inst.routing["roadmap"].labels == ["roadmap"]


# ── suggest_routing() tests ──────────────────────────────────────────


def _make_tree(child_titles: list[str]) -> PageNode:
    """Build a simple root + children tree for suggest_routing tests."""
    children = [
        PageNode(id=str(i), title=title, labels=[], children=[])
        for i, title in enumerate(child_titles, start=100)
    ]
    return PageNode(id="1", title="Space Home", labels=[], children=children)


class TestSuggestRouting:
    """S1: suggest_routing() matches top-level page titles against keywords."""

    def test_adr_match(self) -> None:
        tree = _make_tree(["Architecture Decision Records", "Other Page"])
        result = suggest_routing(tree)
        assert "adr" in result
        assert result["adr"].parent_title == "Architecture Decision Records"
        assert "adr" in result["adr"].labels

    def test_roadmap_match(self) -> None:
        tree = _make_tree(["Roadmaps"])
        result = suggest_routing(tree)
        assert "roadmap" in result
        assert result["roadmap"].parent_title == "Roadmaps"

    def test_developer_match(self) -> None:
        tree = _make_tree(["Developer Docs"])
        result = suggest_routing(tree)
        assert "developer" in result
        assert result["developer"].parent_title == "Developer Docs"

    def test_retrospective_match(self) -> None:
        tree = _make_tree(["Sprint Retrospective Notes"])
        result = suggest_routing(tree)
        assert "retrospective" in result

    def test_no_matches_returns_empty(self) -> None:
        tree = _make_tree(["Random Page", "Meeting Notes"])
        result = suggest_routing(tree)
        assert result == {}

    def test_multiple_matches(self) -> None:
        tree = _make_tree(
            ["Architecture Decision Records", "Roadmaps", "Developer Guide"]
        )
        result = suggest_routing(tree)
        assert "adr" in result
        assert "roadmap" in result
        assert "developer" in result

    def test_case_insensitive(self) -> None:
        tree = _make_tree(["ARCHITECTURE DECISION RECORDS"])
        result = suggest_routing(tree)
        assert "adr" in result


# ── write_confluence_config() tests ──────────────────────────────────


def _sample_config_dict() -> dict[str, Any]:
    """Produce a valid multi-instance config dict for write tests."""
    return generate_confluence_config(
        spaces=_sample_spaces(),
        selected_space="RaiSE1",
        instance_url="https://humansys.atlassian.net/wiki",
        instance_name="humansys",
    )


class TestWriteConfluenceConfig:
    """AC4, AC5: YAML writer with overwrite guard."""

    def test_writes_yaml_file(self, tmp_path: Path) -> None:
        config_dict = _sample_config_dict()
        result_path = write_confluence_config(config_dict, project_root=tmp_path)
        assert result_path.exists()
        assert result_path.name == "confluence.yaml"

    def test_written_yaml_roundtrips(self, tmp_path: Path) -> None:
        config_dict = _sample_config_dict()
        result_path = write_confluence_config(config_dict, project_root=tmp_path)
        with open(result_path) as f:
            loaded = yaml.safe_load(f)
        config = ConfluenceConfig.from_dict(loaded)
        assert config.default_instance == "humansys"
        assert config.get_instance("humansys").space_key == "RaiSE1"

    def test_raises_file_exists_error_when_not_overwrite(self, tmp_path: Path) -> None:
        config_dict = _sample_config_dict()
        write_confluence_config(config_dict, project_root=tmp_path)
        with pytest.raises(FileExistsError, match="already exists"):
            write_confluence_config(config_dict, project_root=tmp_path)

    def test_overwrite_true_succeeds(self, tmp_path: Path) -> None:
        config_dict = _sample_config_dict()
        write_confluence_config(config_dict, project_root=tmp_path)
        # Should not raise
        result_path = write_confluence_config(
            config_dict, project_root=tmp_path, overwrite=True
        )
        assert result_path.exists()

    def test_creates_raise_directory_if_missing(self, tmp_path: Path) -> None:
        config_dict = _sample_config_dict()
        result_path = write_confluence_config(config_dict, project_root=tmp_path)
        assert (tmp_path / ".raise").is_dir()
        assert result_path == tmp_path / ".raise" / "confluence.yaml"
