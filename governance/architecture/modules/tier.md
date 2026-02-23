---
type: module
name: tier
purpose: "Tier detection and capability registry for open-core architecture"
status: current
depends_on: [onboarding]
depended_by: []
entry_points: []
public_api:
  - "Capability"
  - "TierLevel"
  - "TierContext"
  - "TierCapabilityError"
layer: domain
bounded_context: adapters
---

# Module: tier

## Overview

Detects the active deployment tier (COMMUNITY/PRO/Enterprise) from the project
manifest and exposes capability checks for adapters and CLI commands.

## Key Files

| File | Purpose |
|------|---------|
| `context.py` | `Capability` enum, `TierLevel` enum, `TierContext` model, `TierCapabilityError` |

## Data Flow

- Reads `.raise/manifest.yaml` via `onboarding.manifest.load_manifest()`
- Consumed by S211.6 (`rai adapters list/check`) and future tier-aware commands

## Architecture

- ADR-037: TierContext
- Progressive enrichment: COMMUNITY is default, PRO/Enterprise add capabilities
- No feature gating — `has()` checks, not `if tier == PRO` guards
