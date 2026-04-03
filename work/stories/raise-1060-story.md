---
story_id: "RAISE-1060"
epic_ref: "standalone"
size: "S"
type: "code"
status: "in_progress"
---

# Story: Adapter Models Restructure

## User Story
As a RaiSE adapter developer,
I want boundary models organized by protocol concern (PM, Docs, Governance, Health),
so that each adapter domain has clear ownership of its models and filesystem internals
don't leak into shared boundary contracts.

## Acceptance Criteria

### Scenario: Models split by protocol concern
```gherkin
Given the current monolithic models.py with 20+ models
When I split into per-protocol modules under models/
Then PM models are in models/pm.py
And Docs models are in models/docs.py
And Governance models are in models/governance.py
And shared models (AdapterHealth) are in models/health.py
```

### Scenario: Filesystem internals moved out
```gherkin
Given BacklogItem, BacklogLink, BacklogComment in models.py
When I move them to the filesystem adapter module
Then they are no longer in the shared models package
And filesystem.py imports them from their new location
```

### Scenario: Zero breaking changes
```gherkin
Given 47+ import sites using `from raise_cli.adapters.models import X`
When the restructure is complete
Then all existing imports continue working via re-exports
And all tests pass without modification
And __all__ in adapters/__init__.py is unchanged
```

### Scenario: SpaceInfo added for Confluence discovery
```gherkin
Given the new models/docs.py module
When SpaceInfo is added alongside PageContent and PageSummary
Then it is available as a docs boundary model
And it is re-exported from raise_cli.adapters.models
```

## Notes
- Prerequisite for RAISE-1051 S1051.1 (Confluence client wrapper)
- Aligns models.py with adapter-vision.md §5 and pluggable-domains-vision.md §3
- BacklogItem/BacklogLink/BacklogComment used ONLY by filesystem.py + its tests
- Re-export via models/__init__.py ensures zero breaking changes
