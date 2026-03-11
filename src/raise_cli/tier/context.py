"""Tier detection and capability registry.

Detects the active deployment tier (COMMUNITY/PRO/Enterprise) from the project
manifest and exposes capability checks for adapters and CLI commands.

Architecture: ADR-037 (TierContext)
"""

from __future__ import annotations

import logging
from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

__all__ = ["Capability", "TierCapabilityError", "TierContext", "TierLevel"]


class Capability(StrEnum):
    """Capabilities available across tiers (ADR-037)."""

    SHARED_MEMORY = "shared_memory"
    SEMANTIC_SEARCH = "semantic_search"
    TEAM_AWARENESS = "team_awareness"
    JIRA_INTEGRATION = "jira_integration"
    DOCS_PUBLISH = "docs_publish"
    ORG_GOVERNANCE = "org_governance"
    AUDIT_LOGGING = "audit_logging"


class TierLevel(StrEnum):
    """Deployment tier levels."""

    COMMUNITY = "community"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class TierCapabilityError(Exception):
    """Raised when a required capability is not available in the current tier."""

    def __init__(
        self,
        capability: Capability,
        current_tier: TierLevel,
        suggested_tier: TierLevel,
    ) -> None:
        self.capability = capability
        self.current_tier = current_tier
        self.suggested_tier = suggested_tier
        super().__init__(
            f"Capability '{capability}' requires {suggested_tier} tier "
            f"(current: {current_tier}). "
            f"Upgrade to {suggested_tier} to enable this feature."
        )


# Minimum tier required for each capability.
_CAPABILITY_TIER: dict[Capability, TierLevel] = {
    Capability.SHARED_MEMORY: TierLevel.PRO,
    Capability.SEMANTIC_SEARCH: TierLevel.PRO,
    Capability.TEAM_AWARENESS: TierLevel.PRO,
    Capability.JIRA_INTEGRATION: TierLevel.PRO,
    Capability.DOCS_PUBLISH: TierLevel.PRO,
    Capability.ORG_GOVERNANCE: TierLevel.ENTERPRISE,
    Capability.AUDIT_LOGGING: TierLevel.ENTERPRISE,
}


class TierContext(BaseModel):
    """Tier detection and capability registry."""

    tier: TierLevel = TierLevel.COMMUNITY
    backend_url: str | None = None
    capabilities: set[Capability] = Field(default_factory=lambda: set[Capability]())

    def has(self, capability: Capability) -> bool:
        """Check if a capability is available."""
        return capability in self.capabilities

    def require_or_suggest(self, capability: Capability) -> None:
        """Raise TierCapabilityError if capability is missing."""
        if not self.has(capability):
            suggested = _CAPABILITY_TIER.get(capability, TierLevel.PRO)
            raise TierCapabilityError(
                capability=capability,
                current_tier=self.tier,
                suggested_tier=suggested,
            )

    @classmethod
    def from_manifest(cls, project_root: Path) -> TierContext:
        """Detect tier from .raise/manifest.yaml via load_manifest().

        Falls back to COMMUNITY if no manifest or no tier section.
        """
        from raise_cli.onboarding.manifest import load_manifest

        manifest = load_manifest(project_root)
        if manifest is None or manifest.tier is None:
            return cls.community()

        tier_cfg = manifest.tier

        # Parse tier level, fall back to COMMUNITY for unknown values.
        try:
            tier_level = TierLevel(tier_cfg.level)
        except ValueError:
            logger.warning(
                "Unknown tier level '%s', defaulting to community", tier_cfg.level
            )
            tier_level = TierLevel.COMMUNITY

        # Parse capabilities, skip unknown ones.
        capabilities: set[Capability] = set()
        for cap_str in tier_cfg.capabilities:
            try:
                capabilities.add(Capability(cap_str))
            except ValueError:
                logger.warning("Unknown capability '%s', skipping", cap_str)

        return cls(
            tier=tier_level,
            backend_url=tier_cfg.backend_url,
            capabilities=capabilities,
        )

    @classmethod
    def community(cls) -> TierContext:
        """Factory for default COMMUNITY tier."""
        return cls()
