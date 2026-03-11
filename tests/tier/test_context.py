"""Tests for TierContext — tier detection and capability registry."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from raise_cli.tier.context import (
    Capability,
    TierCapabilityError,
    TierContext,
    TierLevel,
)

# =============================================================================
# T1: Enums, has(), community()
# =============================================================================


class TestCapabilityEnum:
    """Tests for Capability StrEnum."""

    def test_expected_members(self) -> None:
        expected = {
            "shared_memory",
            "semantic_search",
            "team_awareness",
            "jira_integration",
            "docs_publish",
            "org_governance",
            "audit_logging",
        }
        assert {c.value for c in Capability} == expected


class TestTierLevelEnum:
    """Tests for TierLevel StrEnum."""

    def test_expected_members(self) -> None:
        assert {t.value for t in TierLevel} == {"community", "pro", "enterprise"}


class TestTierContextCommunity:
    """Tests for TierContext.community() factory."""

    def test_community_returns_community_tier(self) -> None:
        ctx = TierContext.community()
        assert ctx.tier == TierLevel.COMMUNITY

    def test_community_has_no_capabilities(self) -> None:
        ctx = TierContext.community()
        assert ctx.capabilities == set()

    def test_community_has_no_backend_url(self) -> None:
        ctx = TierContext.community()
        assert ctx.backend_url is None


class TestTierContextHas:
    """Tests for TierContext.has()."""

    def test_has_returns_false_for_missing_capability(self) -> None:
        ctx = TierContext.community()
        assert ctx.has(Capability.SHARED_MEMORY) is False

    def test_has_returns_true_for_present_capability(self) -> None:
        ctx = TierContext(capabilities={Capability.SHARED_MEMORY})
        assert ctx.has(Capability.SHARED_MEMORY) is True

    def test_has_returns_false_for_other_capability(self) -> None:
        ctx = TierContext(capabilities={Capability.SHARED_MEMORY})
        assert ctx.has(Capability.SEMANTIC_SEARCH) is False


# =============================================================================
# T2: require_or_suggest(), from_manifest()
# =============================================================================


class TestRequireOrSuggest:
    """Tests for TierContext.require_or_suggest()."""

    def test_raises_for_missing_capability(self) -> None:
        ctx = TierContext.community()
        with pytest.raises(TierCapabilityError) as exc_info:
            ctx.require_or_suggest(Capability.SEMANTIC_SEARCH)
        assert exc_info.value.capability == Capability.SEMANTIC_SEARCH
        assert exc_info.value.current_tier == TierLevel.COMMUNITY

    def test_passes_for_present_capability(self) -> None:
        ctx = TierContext(capabilities={Capability.SEMANTIC_SEARCH})
        ctx.require_or_suggest(Capability.SEMANTIC_SEARCH)  # no raise

    def test_error_message_is_actionable(self) -> None:
        ctx = TierContext.community()
        with pytest.raises(TierCapabilityError) as exc_info:
            ctx.require_or_suggest(Capability.SEMANTIC_SEARCH)
        msg = str(exc_info.value)
        assert "semantic_search" in msg
        assert "community" in msg


class TestFromManifest:
    """Tests for TierContext.from_manifest()."""

    def test_no_manifest_returns_community(self, tmp_path: Path) -> None:
        ctx = TierContext.from_manifest(tmp_path / "nonexistent")
        assert ctx.tier == TierLevel.COMMUNITY
        assert ctx.capabilities == set()

    def test_manifest_without_tier_section(self, tmp_path: Path) -> None:
        rai_dir = tmp_path / ".raise"
        rai_dir.mkdir()
        (rai_dir / "manifest.yaml").write_text(
            "version: '1.0'\n"
            "project:\n"
            "  name: test\n"
            "  project_type: greenfield\n"
            "  code_file_count: 0\n"
            "  detected_at: '2026-01-01T00:00:00Z'\n"
        )
        ctx = TierContext.from_manifest(tmp_path)
        assert ctx.tier == TierLevel.COMMUNITY
        assert ctx.capabilities == set()

    def test_manifest_with_pro_tier(self, tmp_path: Path) -> None:
        rai_dir = tmp_path / ".raise"
        rai_dir.mkdir()
        data = {
            "version": "1.0",
            "project": {
                "name": "test",
                "project_type": "greenfield",
                "code_file_count": 0,
                "detected_at": "2026-01-01T00:00:00Z",
            },
            "tier": {
                "level": "pro",
                "backend_url": "https://api.raiseframework.ai",
                "capabilities": ["shared_memory", "semantic_search"],
            },
        }
        (rai_dir / "manifest.yaml").write_text(yaml.dump(data))

        ctx = TierContext.from_manifest(tmp_path)
        assert ctx.tier == TierLevel.PRO
        assert ctx.backend_url == "https://api.raiseframework.ai"
        assert Capability.SHARED_MEMORY in ctx.capabilities
        assert Capability.SEMANTIC_SEARCH in ctx.capabilities

    def test_manifest_with_enterprise_tier(self, tmp_path: Path) -> None:
        rai_dir = tmp_path / ".raise"
        rai_dir.mkdir()
        data = {
            "version": "1.0",
            "project": {
                "name": "test",
                "project_type": "greenfield",
                "code_file_count": 0,
                "detected_at": "2026-01-01T00:00:00Z",
            },
            "tier": {
                "level": "enterprise",
                "backend_url": "https://enterprise.example.com",
                "capabilities": [
                    "shared_memory",
                    "semantic_search",
                    "org_governance",
                    "audit_logging",
                ],
            },
        }
        (rai_dir / "manifest.yaml").write_text(yaml.dump(data))

        ctx = TierContext.from_manifest(tmp_path)
        assert ctx.tier == TierLevel.ENTERPRISE
        assert ctx.backend_url == "https://enterprise.example.com"
        assert len(ctx.capabilities) == 4
        assert Capability.AUDIT_LOGGING in ctx.capabilities

    def test_manifest_with_unknown_capability_ignored(self, tmp_path: Path) -> None:
        rai_dir = tmp_path / ".raise"
        rai_dir.mkdir()
        data = {
            "version": "1.0",
            "project": {
                "name": "test",
                "project_type": "greenfield",
                "code_file_count": 0,
                "detected_at": "2026-01-01T00:00:00Z",
            },
            "tier": {
                "level": "pro",
                "capabilities": ["shared_memory", "future_capability"],
            },
        }
        (rai_dir / "manifest.yaml").write_text(yaml.dump(data))

        ctx = TierContext.from_manifest(tmp_path)
        assert ctx.tier == TierLevel.PRO
        assert Capability.SHARED_MEMORY in ctx.capabilities
        assert len(ctx.capabilities) == 1  # unknown skipped
