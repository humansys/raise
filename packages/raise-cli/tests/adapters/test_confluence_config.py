"""Tests for Confluence config schema + Pydantic models.

S1051.3 (RAISE-1056)
"""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from raise_cli.adapters.confluence_config import (
    ArtifactRouting,
    ConfluenceConfig,
    ConfluenceInstanceConfig,
    load_confluence_config,
)


# ── T1: ArtifactRouting ──────────────────────────────────────────────────


class TestArtifactRouting:
    """ArtifactRouting model tests."""

    def test_valid_routing(self) -> None:
        routing = ArtifactRouting(
            parent_title="Architecture Decision Records",
            labels=["adr", "architecture"],
        )
        assert routing.parent_title == "Architecture Decision Records"
        assert routing.labels == ["adr", "architecture"]

    def test_labels_default_empty(self) -> None:
        routing = ArtifactRouting(parent_title="Roadmap")
        assert routing.labels == []

    def test_parent_title_required(self) -> None:
        with pytest.raises(ValidationError):
            ArtifactRouting()  # type: ignore[call-arg]


# ── T2: ConfluenceInstanceConfig routing extension ───────────────────────


class TestConfluenceInstanceConfigRouting:
    """ConfluenceInstanceConfig with optional routing field."""

    def test_routing_defaults_empty(self) -> None:
        config = ConfluenceInstanceConfig(
            url="https://x.atlassian.net/wiki",
            username="a@b.com",
            space_key="TEST",
        )
        assert config.routing == {}

    def test_routing_with_entries(self) -> None:
        config = ConfluenceInstanceConfig(
            url="https://x.atlassian.net/wiki",
            username="a@b.com",
            space_key="TEST",
            routing={
                "adr": ArtifactRouting(
                    parent_title="ADRs",
                    labels=["adr"],
                ),
            },
        )
        assert "adr" in config.routing
        assert config.routing["adr"].parent_title == "ADRs"

    def test_backwards_compat_four_fields(self) -> None:
        """S1051.1 usage: url, username, space_key, instance_name — still works."""
        config = ConfluenceInstanceConfig(
            url="https://x.atlassian.net/wiki",
            username="a@b.com",
            space_key="TEST",
            instance_name="prod",
        )
        assert config.instance_name == "prod"
        assert config.routing == {}


# ── T3: ConfluenceConfig root model ─────────────────────────────────────


def _make_instance(**overrides: str) -> ConfluenceInstanceConfig:
    """Helper: create instance config with defaults."""
    defaults = {
        "url": "https://x.atlassian.net/wiki",
        "username": "a@b.com",
        "space_key": "TEST",
    }
    return ConfluenceInstanceConfig(**{**defaults, **overrides})


class TestConfluenceConfig:
    """ConfluenceConfig root model tests."""

    def test_full_config_validates(self) -> None:
        cfg = ConfluenceConfig(
            default_instance="prod",
            instances={"prod": _make_instance(instance_name="prod")},
        )
        assert cfg.default_instance == "prod"
        assert "prod" in cfg.instances

    def test_get_instance_default(self) -> None:
        cfg = ConfluenceConfig(
            default_instance="prod",
            instances={"prod": _make_instance(instance_name="prod")},
        )
        assert cfg.get_instance().instance_name == "prod"

    def test_get_instance_by_name(self) -> None:
        cfg = ConfluenceConfig(
            default_instance="prod",
            instances={
                "prod": _make_instance(instance_name="prod"),
                "staging": _make_instance(instance_name="staging", space_key="STG"),
            },
        )
        assert cfg.get_instance("staging").space_key == "STG"

    def test_get_instance_unknown_raises(self) -> None:
        cfg = ConfluenceConfig(
            default_instance="prod",
            instances={"prod": _make_instance(instance_name="prod")},
        )
        with pytest.raises(KeyError, match="nope"):
            cfg.get_instance("nope")

    def test_default_instance_not_in_instances_raises(self) -> None:
        with pytest.raises(ValidationError, match="default_instance"):
            ConfluenceConfig(
                default_instance="missing",
                instances={"prod": _make_instance()},
            )


# ── T4: Flat config normalization ───────────────────────────────────────


class TestFlatConfigNormalization:
    """Flat {url, username, space_key} normalizes to ConfluenceConfig."""

    def test_flat_dict_normalizes(self) -> None:
        flat = {
            "url": "https://x.atlassian.net/wiki",
            "username": "a@b.com",
            "space_key": "TEST",
        }
        cfg = ConfluenceConfig.from_dict(flat)
        assert cfg.default_instance == "default"
        assert "default" in cfg.instances
        assert cfg.get_instance().url == "https://x.atlassian.net/wiki"

    def test_flat_with_instance_name(self) -> None:
        flat = {
            "url": "https://x.atlassian.net/wiki",
            "username": "a@b.com",
            "space_key": "TEST",
            "instance_name": "prod",
        }
        cfg = ConfluenceConfig.from_dict(flat)
        assert cfg.default_instance == "default"
        assert cfg.get_instance().instance_name == "prod"

    def test_full_dict_passes_through(self) -> None:
        full = {
            "default_instance": "prod",
            "instances": {
                "prod": {
                    "url": "https://x.atlassian.net/wiki",
                    "username": "a@b.com",
                    "space_key": "TEST",
                    "instance_name": "prod",
                },
            },
        }
        cfg = ConfluenceConfig.from_dict(full)
        assert cfg.default_instance == "prod"


# ── T5: resolve_routing ─────────────────────────────────────────────────


class TestResolveRouting:
    """resolve_routing on ConfluenceConfig."""

    def test_known_type_returns_routing(self) -> None:
        cfg = ConfluenceConfig(
            default_instance="prod",
            instances={
                "prod": ConfluenceInstanceConfig(
                    url="https://x.atlassian.net/wiki",
                    username="a@b.com",
                    space_key="TEST",
                    instance_name="prod",
                    routing={
                        "adr": ArtifactRouting(
                            parent_title="ADRs", labels=["adr"]
                        ),
                    },
                ),
            },
        )
        r = cfg.resolve_routing("adr")
        assert r is not None
        assert r.parent_title == "ADRs"

    def test_unknown_type_returns_none(self) -> None:
        cfg = ConfluenceConfig(
            default_instance="prod",
            instances={"prod": _make_instance(instance_name="prod")},
        )
        assert cfg.resolve_routing("nonexistent") is None

    def test_routing_on_specific_instance(self) -> None:
        cfg = ConfluenceConfig(
            default_instance="prod",
            instances={
                "prod": _make_instance(instance_name="prod"),
                "docs": ConfluenceInstanceConfig(
                    url="https://docs.atlassian.net/wiki",
                    username="a@b.com",
                    space_key="DOCS",
                    instance_name="docs",
                    routing={
                        "roadmap": ArtifactRouting(parent_title="Roadmap"),
                    },
                ),
            },
        )
        assert cfg.resolve_routing("roadmap", instance="docs") is not None
        assert cfg.resolve_routing("roadmap") is None  # not on default


# ── T6: load_confluence_config ──────────────────────────────────────────


class TestLoadConfluenceConfig:
    """load_confluence_config reads .raise/confluence.yaml."""

    def test_load_full_yaml(self, tmp_path: Path) -> None:
        yaml_content = """\
default_instance: humansys
instances:
  humansys:
    url: "https://humansys.atlassian.net/wiki"
    username: "emilio@humansys.ai"
    space_key: "RaiSE1"
    instance_name: "humansys"
    routing:
      adr:
        parent_title: "Architecture Decision Records"
        labels: ["adr", "architecture"]
"""
        config_dir = tmp_path / ".raise"
        config_dir.mkdir()
        (config_dir / "confluence.yaml").write_text(yaml_content)

        cfg = load_confluence_config(tmp_path)
        assert cfg.default_instance == "humansys"
        assert cfg.get_instance().space_key == "RaiSE1"
        assert cfg.resolve_routing("adr") is not None

    def test_load_flat_yaml(self, tmp_path: Path) -> None:
        yaml_content = """\
url: "https://x.atlassian.net/wiki"
username: "a@b.com"
space_key: "TEST"
"""
        config_dir = tmp_path / ".raise"
        config_dir.mkdir()
        (config_dir / "confluence.yaml").write_text(yaml_content)

        cfg = load_confluence_config(tmp_path)
        assert cfg.default_instance == "default"
        assert cfg.get_instance().url == "https://x.atlassian.net/wiki"

    def test_missing_file_raises(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            load_confluence_config(tmp_path)

    def test_invalid_yaml_raises(self, tmp_path: Path) -> None:
        config_dir = tmp_path / ".raise"
        config_dir.mkdir()
        (config_dir / "confluence.yaml").write_text("not_valid: [}")

        with pytest.raises(Exception):  # yaml.ScannerError
            load_confluence_config(tmp_path)
