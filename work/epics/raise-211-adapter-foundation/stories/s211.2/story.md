---
story_id: "S211.2"
title: "Entry point registry"
epic_ref: "RAISE-211"
size: "S"
status: "draft"
created: "2026-02-22"
---

# Story: Entry point registry

## User Story
As a raise-cli plugin developer,
I want adapter implementations to be discovered automatically via Python entry points,
so that I can extend raise-cli by publishing a package without modifying core code.

## Acceptance Criteria

### Scenario: Discover PM adapters
```gherkin
Given a package registers entry point group "rai.adapters.pm"
When get_pm_adapters() is called
Then it returns a dict mapping adapter name to loaded class
```

### Scenario: Discover governance schemas
```gherkin
Given a package registers entry point group "rai.governance.schemas"
When get_governance_schemas() is called
Then it returns a dict mapping schema name to loaded class
```

### Scenario: No adapters registered
```gherkin
Given no packages register the "rai.adapters.pm" group
When get_pm_adapters() is called
Then it returns an empty dict without error
```

### Scenario: Broken entry point handled gracefully
```gherkin
Given a package registers an entry point that fails to load
When the registry discovers it
Then it logs a warning and skips the broken entry point
And other valid entry points are still returned
```

## Notes
- Entry point groups per ADR-033/034/036: `rai.adapters.pm`, `rai.governance.schemas`, `rai.governance.parsers`, `rai.docs.targets`, `rai.graph.backends`
- Registry lives in `src/rai_cli/adapters/registry.py` (per ADR-034 layout)
- S211.1 Protocols are the contracts that registry discovers
- S211.3 will consume this registry to wire `rai memory build`
