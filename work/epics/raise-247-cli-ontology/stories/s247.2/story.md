---
story_id: "S247.2"
title: "Create pattern group"
epic_ref: "RAISE-247"
size: "S"
status: "draft"
created: "2026-02-23"
---

# Story: Create pattern group

## User Story
As a developer using rai CLI,
I want `rai pattern add` and `rai pattern reinforce` as dedicated commands,
so that the memory god object is decomposed and pattern-related commands have a coherent home.

## Acceptance Criteria

### Scenario: Add pattern via new group
```gherkin
Given the rai CLI is installed
When I run `rai pattern add "some insight" --context "testing" --type technical`
Then the pattern is added to the memory graph
And the output confirms creation with a pattern ID
```

### Scenario: Backward compat for add-pattern
```gherkin
Given a user running the old command
When I run `rai memory add-pattern "some insight"`
Then the command succeeds with a deprecation warning
And suggests `rai pattern add` as the replacement
```

### Scenario: Reinforce pattern via new group
```gherkin
Given a pattern exists in the graph
When I run `rai pattern reinforce PAT-E-183 --vote 1 --from S247.2`
Then the pattern score is updated
```

### Scenario: Backward compat for reinforce
```gherkin
Given a user running the old command
When I run `rai memory reinforce PAT-E-183 --vote 1`
Then the command succeeds with a deprecation warning
And suggests `rai pattern reinforce` as the replacement
```

## Notes
- Same extraction pattern as S247.1 (graph group): new file, register in main.py, backward-compat shim with `_deprecation_warning`
- `_deprecation_warning` helper is in memory.py — either import it or duplicate (discuss in design)
- `add-pattern` is at memory.py:401, `reinforce` is at memory.py:303
- `pattern list` is deferred — `graph list --types pattern` covers it (from epic scope)
- See epic design.md for full CLI ontology context
