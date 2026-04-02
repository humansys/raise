"""Tests for Confluence config generator — S1130.4."""

from __future__ import annotations

import pytest

from raise_cli.adapters.confluence_config import ArtifactRouting, ConfluenceConfig
from raise_cli.adapters.confluence_config_gen import generate_confluence_config
from raise_cli.adapters.confluence_discovery import ConfluenceSpaceMap
from raise_cli.adapters.models.docs import PageSummary, SpaceInfo


def _sample_space_map() -> ConfluenceSpaceMap:
    """Create a sample space map for testing."""
    return ConfluenceSpaceMap(
        spaces=[
            SpaceInfo(
                key="RaiSE1",
                name="RaiSE Documentation",
                url="/wiki/spaces/RaiSE1",
                type="global",
            ),
            SpaceInfo(
                key="OPS", name="Operations", url="/wiki/spaces/OPS", type="global"
            ),
        ],
        top_level_pages={
            "RaiSE1": [
                PageSummary(id="123", title="Architecture", url="/wiki/pages/123"),
                PageSummary(id="456", title="Developer Docs", url="/wiki/pages/456"),
            ],
            "OPS": [],
        },
    )


class TestGenerateMinimalConfig:
    def test_returns_dict(self) -> None:
        result = generate_confluence_config(
            space_map=_sample_space_map(),
            selected_space="RaiSE1",
            instance_url="https://humansys.atlassian.net/wiki",
        )
        assert isinstance(result, dict)

    def test_includes_url(self) -> None:
        result = generate_confluence_config(
            space_map=_sample_space_map(),
            selected_space="RaiSE1",
            instance_url="https://humansys.atlassian.net/wiki",
        )
        # Should be findable in the config structure
        config = ConfluenceConfig.from_dict(result)
        inst = config.get_instance()
        assert inst.url == "https://humansys.atlassian.net/wiki"

    def test_includes_selected_space_key(self) -> None:
        result = generate_confluence_config(
            space_map=_sample_space_map(),
            selected_space="RaiSE1",
            instance_url="https://humansys.atlassian.net/wiki",
        )
        config = ConfluenceConfig.from_dict(result)
        inst = config.get_instance()
        assert inst.space_key == "RaiSE1"


class TestConfigValidation:
    def test_generated_config_passes_confluence_config_validation(self) -> None:
        result = generate_confluence_config(
            space_map=_sample_space_map(),
            selected_space="RaiSE1",
            instance_url="https://humansys.atlassian.net/wiki",
        )
        # This is the key test — output MUST be valid ConfluenceConfig
        config = ConfluenceConfig.from_dict(result)
        assert config.default_instance == "default"
        assert "default" in config.instances


class TestRouting:
    def test_includes_routing_when_provided(self) -> None:
        routing: dict[str, ArtifactRouting] = {
            "adr": ArtifactRouting(parent_title="Architecture", labels=["adr"]),
            "developer": ArtifactRouting(parent_title="Dev Docs", labels=["dev"]),
        }
        result = generate_confluence_config(
            space_map=_sample_space_map(),
            selected_space="RaiSE1",
            instance_url="https://humansys.atlassian.net/wiki",
            routing=routing,
        )
        config = ConfluenceConfig.from_dict(result)
        inst = config.get_instance()
        assert "adr" in inst.routing
        assert inst.routing["adr"].parent_title == "Architecture"

    def test_default_routing_when_none(self) -> None:
        result = generate_confluence_config(
            space_map=_sample_space_map(),
            selected_space="RaiSE1",
            instance_url="https://humansys.atlassian.net/wiki",
        )
        config = ConfluenceConfig.from_dict(result)
        inst = config.get_instance()
        # Should have sensible defaults
        assert "adr" in inst.routing
        assert "developer" in inst.routing


class TestErrors:
    def test_invalid_space_raises(self) -> None:
        with pytest.raises(ValueError, match="MISSING"):
            generate_confluence_config(
                space_map=_sample_space_map(),
                selected_space="MISSING",
                instance_url="https://humansys.atlassian.net/wiki",
            )
