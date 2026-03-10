---
story_id: "S211.5"
title: "TierContext"
epic_ref: "RAISE-211"
size: "S"
status: "draft"
created: "2026-02-22"
---

# Story: TierContext

## User Story
As a raise-cli developer,
I want a TierContext that detects the active tier and available capabilities,
so that adapters and CLI commands can branch behavior based on COMMUNITY/PRO/Enterprise without hardcoding tier checks.

## Acceptance Criteria

### Scenario: Community tier by default
```gherkin
Given no manifest file exists
When TierContext.from_manifest() is called
Then it returns a COMMUNITY tier with no extra capabilities
```

### Scenario: PRO tier from manifest
```gherkin
Given a manifest with tier: pro and backend_url set
When TierContext.from_manifest() is called
Then it returns a PRO tier with PRO capabilities enabled
```

### Scenario: Capability check
```gherkin
Given a COMMUNITY TierContext
When has(Capability.SHARED_MEMORY) is called
Then it returns False
```

### Scenario: Actionable suggestion for missing capability
```gherkin
Given a COMMUNITY TierContext
When require_or_suggest(Capability.SEMANTIC_SEARCH) is called
Then it raises with a message suggesting upgrade to PRO
```

## Notes
- Design contract in epic `design.md` §TierContext (lines 166-200)
- ADR-037 defines the tier model
- `get_active_backend()` in `graph/filesystem_backend.py` has a TODO referencing TierContext
- S211.6 (`rai adapters list/check`) depends on this story
