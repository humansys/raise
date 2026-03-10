---
story_id: "S247.1"
title: "Create graph group"
epic_ref: "RAISE-247"
size: "M"
status: "draft"
created: "2026-02-23"
---

# Story: Create `graph` group

## User Story
As an AI agent executing skills,
I want graph-related commands under `rai graph` instead of `rai memory`,
so that the CLI namespace reflects bounded contexts and I can discover commands by domain.

## Acceptance Criteria

### Scenario: Graph commands work under new group
```gherkin
Given the rai CLI is installed
When I run `rai graph build`
Then it builds the knowledge graph (same behavior as `rai memory build`)
And the exit code is 0
```

### Scenario: All 7 graph commands are available
```gherkin
Given the rai CLI is installed
When I run `rai graph --help`
Then I see commands: build, validate, query, context, list, viz, extract
```

### Scenario: Backward-compat alias with deprecation warning
```gherkin
Given the rai CLI is installed
When I run `rai memory build`
Then it delegates to `rai graph build`
And stderr contains "DEPRECATED: use 'rai graph build' instead"
And the command still succeeds (exit 0)
```

### Scenario: Registration in main CLI
```gherkin
Given graph.py defines the graph_app Typer group
When the CLI loads
Then `rai graph` appears in the top-level help
And `rai memory` still appears (for backward compat)
```

## Examples (Specification by Example)

| Old Command | New Command | Deprecation Warning |
|-------------|-------------|---------------------|
| `rai memory build` | `rai graph build` | Yes |
| `rai memory query "test"` | `rai graph query "test"` | Yes |
| `rai memory context mod-cli` | `rai graph context mod-cli` | Yes |
| `rai memory validate` | `rai graph validate` | Yes |
| `rai memory list` | `rai graph list` | Yes |
| `rai memory viz` | `rai graph viz` | Yes |
| `rai memory extract` | `rai graph extract` | Yes |
| `rai graph build` | `rai graph build` | No |

## Notes

- This is the first extraction story — establishes the pattern (new file, register in main.py, backward-compat shim with deprecation warning) that S2 and S3 will replicate.
- The 7 commands to extract: `build`, `validate`, `query`, `context`, `list`, `viz`, `extract` (lines ~90-1009 of memory.py).
- After extraction, `memory.py` retains: `generate`, `add-pattern`, `reinforce`, `add-calibration`, `add-session`, `emit-work`, `emit-session`, `emit-calibration` (8 commands).
- Backward-compat approach: keep `memory_app` with thin wrappers that print deprecation + call the real function.
- See epic scope.md and ADR-038 for full context.
