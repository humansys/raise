"""Tests for Confluence config schema + Pydantic models.

S1051.3 (RAISE-1056)
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from raise_cli.adapters.confluence_config import (
    ArtifactRouting,
    ConfluenceConfig,
    ConfluenceInstanceConfig,
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
