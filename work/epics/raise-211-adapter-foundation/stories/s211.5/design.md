---
story_id: "S211.5"
title: "TierContext"
epic_ref: "RAISE-211"
size: "S"
status: "design"
created: "2026-02-22"
grounded_in: "Gemba of adapters/protocols.py, adapters/registry.py, graph/filesystem_backend.py, onboarding/manifest.py, epic design.md §TierContext, ADR-037"
---

# Design: TierContext

## 1. What & Why

**Problem:** raise-cli has no way to know what tier (COMMUNITY/PRO/Enterprise) is active. `get_active_backend()` hardcodes `FilesystemGraphBackend` with a TODO for tier-based selection. Adapters and CLI commands can't branch behavior based on available capabilities.

**Value:** After this story, any code path can ask `TierContext.has(Capability.X)` and get a truthful answer. `require_or_suggest()` provides actionable upgrade messages instead of cryptic errors. Foundation for S211.6 (`rai adapters list/check`) and all future PRO/Enterprise features.

## 2. Approach

New module `src/rai_cli/tier/context.py` with:
- `Capability` StrEnum — enumerated capabilities across tiers
- `TierLevel` StrEnum — COMMUNITY, PRO, ENTERPRISE
- `TierContext` Pydantic model — tier + capabilities + detection from manifest

Detection: `from_manifest()` reuses `load_manifest()` from `onboarding/manifest.py` — one parser, one file, one error handling path (R1 from arch review). If manifest has a `tier` section → parse it. If no manifest or no tier section → COMMUNITY with no extra capabilities. Progressive enrichment (PAT-E-379): COMMUNITY is the default, PRO/Enterprise add capabilities.

## 3. Gemba: Current State

| File | Current Interface | What Changes | What Stays |
|------|------------------|--------------|------------|
| `adapters/protocols.py` | 5 Protocol contracts | Nothing in this story | All protocols |
| `adapters/registry.py` | `_discover()`, 5 `get_*()` functions | Nothing in this story | All registry functions |
| `graph/filesystem_backend.py` | `get_active_backend(path) -> FilesystemGraphBackend` | TODO comment references S211.5 — no code change this story | `FilesystemGraphBackend`, `get_active_backend` |
| `onboarding/manifest.py` | `ProjectManifest` Pydantic model, `load_manifest()` | Add optional `tier: TierConfig | None` field to `ProjectManifest` | `load_manifest()`, all other fields |

One existing file modified (`manifest.py` — add `TierConfig` model + field). Rest is greenfield.

## 4. Target Interfaces

```python
# src/rai_cli/tier/context.py — single file, no separate errors.py (R2)

from enum import StrEnum
from pathlib import Path
from pydantic import BaseModel, Field

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
    def __init__(self, capability: Capability, current_tier: TierLevel, suggested_tier: TierLevel) -> None: ...

class TierContext(BaseModel):
    """Tier detection and capability registry."""
    tier: TierLevel = TierLevel.COMMUNITY
    backend_url: str | None = None
    capabilities: set[Capability] = Field(default_factory=set)

    def has(self, capability: Capability) -> bool:
        """Check if a capability is available."""

    def require_or_suggest(self, capability: Capability) -> None:
        """Raise TierCapabilityError if capability missing, with upgrade suggestion."""

    @classmethod
    def from_manifest(cls, project_root: Path) -> TierContext:
        """Detect tier via load_manifest(). Falls back to COMMUNITY."""

    @classmethod
    def community(cls) -> TierContext:
        """Factory for default COMMUNITY tier."""
```

```python
# src/rai_cli/onboarding/manifest.py — add TierConfig to ProjectManifest (R1)

class TierConfig(BaseModel):
    """Tier configuration from manifest (optional section)."""
    level: str = "community"
    backend_url: str | None = None
    capabilities: list[str] = Field(default_factory=list)

class ProjectManifest(BaseModel):
    # ... existing fields ...
    tier: TierConfig | None = None  # new, optional
```

### Integration Points
- `TierContext.from_manifest()` calls `load_manifest()` from `onboarding/manifest.py`, reads `manifest.tier` (R1: one parser, one file)
- S211.6 will consume `TierContext` for `rai adapters list/check`
- `get_active_backend()` TODO will be addressed in a future story (not this one)

## 5. Acceptance Criteria

See: `story.md` § Acceptance Criteria

## 6. Constraints

- **Pydantic model** (guardrail MUST-ARCH-002): TierContext as BaseModel, not dataclass (diverges from epic design.md which used dataclass — Pydantic is the project standard)
- **No manifest schema change**: TierContext reads an optional `tier` key from existing manifest. If absent, COMMUNITY. No migration needed.
- **Manifest YAML format** for tier section:
  ```yaml
  # .raise/manifest.yaml (optional tier section)
  tier:
    level: pro
    backend_url: https://api.raiseframework.ai
    capabilities:
      - shared_memory
      - semantic_search
  ```

---

*Design created: 2026-02-22*
*Next: `/rai-story-plan`*
