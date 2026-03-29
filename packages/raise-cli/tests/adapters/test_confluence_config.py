"""Tests for Confluence config schema + Pydantic models.

S1051.3 (RAISE-1056)
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from raise_cli.adapters.confluence_config import ArtifactRouting


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
