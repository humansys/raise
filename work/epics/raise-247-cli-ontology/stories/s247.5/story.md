---
story_id: "S247.5"
title: "Merge publish+release, flatten singletons"
epic_ref: "E247"
jira: "RAISE-254"
size: "S"
status: "draft"
created: "2026-02-23"
---

# Story: Merge publish+release, flatten singletons

## User Story
As the CLI ontology,
I want overlapping groups consolidated and singleton wrappers flattened,
so that the command namespace is clean and agents find commands where expected.

## Acceptance Criteria

### Scenario: publish commands absorbed into release group
```gherkin
Given the current CLI has `rai publish check` and `rai publish release`
When S247.5 is complete
Then `rai release check` and `rai release publish` exist as commands
And `rai release list` still works
And `rai publish check` and `rai publish release` print deprecation + delegate
```

### Scenario: base show flattened to rai info
```gherkin
Given the current CLI has `rai base show`
When S247.5 is complete
Then `rai info` exists as a top-level command
And `rai base show` prints deprecation + delegates to `rai info`
```

### Scenario: profile show flattened to rai profile
```gherkin
Given the current CLI has `rai profile show` (requires subcommand)
When S247.5 is complete
Then `rai profile` (no subcommand) shows the profile
And the old `rai profile show` still works
```

## Notes
- This is a MERGE pattern (not extract like S1-S3). Two source files → one target.
- `publish release` → `release publish` (verb swap). The `release` group absorbs publish.
- Backward-compat aliases follow the same deprecation pattern established in S1-S3.
- `profile` flattening: change from `no_args_is_help=True` to `invoke_without_command=True` + callback.
- `base show` → `rai info`: new top-level command, remove `base` group entirely (add deprecation shim).
