---
story_id: "S211.6"
title: "rai adapters list/check"
epic_ref: "E211"
size: "S"
status: "draft"
created: "2026-02-23"
---

# Story: rai adapters list/check

## User Story
As a developer using rai-cli,
I want to list installed adapters and check their validity,
so that I can verify which extensions are available and troubleshoot broken plugins.

## Acceptance Criteria

### Scenario: List adapters with none installed beyond built-ins
```gherkin
Given a project with no third-party adapter packages installed
When I run `rai adapters list`
Then I see a table of all entry point groups with their registered adapters
And built-in adapters (e.g., FilesystemGraphBackend) appear with source "rai-cli"
```

### Scenario: Check adapters validates Protocol compliance
```gherkin
Given adapters are registered via entry points
When I run `rai adapters check`
Then each adapter is loaded and validated against its Protocol contract
And passing adapters show a checkmark
And broken/non-compliant adapters show an error with actionable message
```

## Notes
- Depends on S211.2 (registry: `_discover()`, `get_*()` functions) and S211.5 (TierContext for tier display)
- CLI commands live in `src/rai_cli/cli/commands/` — new `adapters.py` module
- Uses existing `_discover()` from `adapters/registry.py` — no new discovery logic
- Protocol compliance check: `runtime_checkable` + `isinstance()` for each loaded class
