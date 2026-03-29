"""Tests for Confluence config schema + Pydantic models.

S1051.3 (RAISE-1056)
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from raise_cli.adapters.confluence_config import (
    ArtifactRouting,
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
