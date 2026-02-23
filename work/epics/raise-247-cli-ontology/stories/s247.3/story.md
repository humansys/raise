---
story_id: "S247.3"
title: "Create signal group"
epic_ref: "RAISE-247"
size: "S"
status: "draft"
created: "2026-02-23"
---

# Story: Create `signal` group

## User Story
As a developer using RaiSE,
I want `rai signal` commands (emit-work, emit-session, emit-calibration) extracted from `rai memory`,
so that telemetry/signal commands live in a bounded context that reflects their domain.

## Acceptance Criteria

### Scenario: emit-work via new canonical command
```gherkin
Given a valid story ID and event
When I run `rai signal emit-work story S247.3 --event start --phase design`
Then the signal is emitted to signals.jsonl
And exit code is 0
```

### Scenario: backward-compat alias for emit-work
```gherkin
Given the legacy command
When I run `rai memory emit-work story S247.3 --event start`
Then a deprecation warning is shown pointing to `rai signal emit-work`
And the command still executes successfully
```

### Scenario: deprecation message format is correct
```gherkin
Given any legacy `rai memory emit-*` command
When executed
Then the deprecation message contains the exact new command name (e.g. "rai signal emit-work")
And does NOT contain the old command name as the replacement
```

## Examples (Specification by Example)

| Command | Expected | Notes |
|---------|----------|-------|
| `rai signal emit-work story S1 --event start` | exit 0, signal written | canonical |
| `rai signal emit-session --summary "test"` | exit 0, signal written | canonical |
| `rai signal emit-calibration --score 1.5` | exit 0, signal written | canonical |
| `rai memory emit-work story S1 --event start` | deprecation warn + exit 0 | shim |
| `rai memory emit-session --summary "test"` | deprecation warn + exit 0 | shim |
| `rai memory emit-calibration --score 1.5` | deprecation warn + exit 0 | shim |

## Notes
- Same extraction pattern as S247.1 (graph.py) and S247.2 (pattern.py)
- Three subcommands (not unified `signal emit <type>`) — arch review R1 decision in scope.md §Decisions
- `get_memory_dir_for_scope` is in `rai_cli.memory`, NOT `config.paths` — verify on Gemba
- Retro S247.2 signal: test deprecation message format in T2 (automated), not just smoke test
- S4 will remove `add-calibration` and `add-session` from memory (redundant after this story)
- Reference: `work/epics/raise-247-cli-ontology/scope.md §S3`
