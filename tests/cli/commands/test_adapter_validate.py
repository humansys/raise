"""Tests for `rai adapter validate` CLI command and reference config."""

from __future__ import annotations

from importlib import resources
from pathlib import Path

import yaml

from rai_cli.adapters.declarative.schema import DeclarativeAdapterConfig

# All 11 PM protocol methods from AsyncProjectManagementAdapter
PM_METHODS = {
    "create_issue",
    "get_issue",
    "update_issue",
    "transition_issue",
    "batch_transition",
    "link_to_parent",
    "link_issues",
    "add_comment",
    "get_comments",
    "search",
    "health",
}


class TestReferenceConfig:
    """Reference github.yaml validates and covers all PM methods."""

    def test_reference_yaml_validates(self) -> None:
        """Reference config parses into a valid DeclarativeAdapterConfig."""
        ref_dir = resources.files("rai_cli.adapters.declarative.reference")
        yaml_path = ref_dir / "github.yaml"
        raw = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))  # type: ignore[union-attr]
        config = DeclarativeAdapterConfig.model_validate(raw)
        assert config.adapter.name == "github"
        assert config.adapter.protocol == "pm"

    def test_reference_covers_all_pm_methods(self) -> None:
        """Reference config has entries for all 11 PM protocol methods."""
        ref_dir = resources.files("rai_cli.adapters.declarative.reference")
        yaml_path = ref_dir / "github.yaml"
        raw = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))  # type: ignore[union-attr]
        config = DeclarativeAdapterConfig.model_validate(raw)
        assert set(config.methods.keys()) == PM_METHODS
