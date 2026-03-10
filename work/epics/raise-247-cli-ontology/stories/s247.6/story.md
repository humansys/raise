---
story_id: "S247.6"
title: "Update all skills and generated docs"
epic_ref: "E247"
size: "M"
status: "draft"
created: "2026-02-23"
jira: "RAISE-255"
---

# Story: Update all skills and generated docs

## User Story
As an AI agent executing RaiSE skills,
I want all skill files and generated docs to reference the new CLI command structure,
so that skill instructions match the actual CLI commands after the E247 ontology restructure.

## Acceptance Criteria

### Scenario: Stale `rai memory` references replaced
```gherkin
Given skills_base/ contains references to `rai memory`
When S247.6 sweep is complete
Then no `rai memory` references remain in skills_base/ or CLAUDE.md
And references point to `rai graph`, `rai pattern`, or `rai signal` as appropriate
```

### Scenario: Stale `rai publish` references replaced
```gherkin
Given skills_base/ contains references to `rai publish`
When S247.6 sweep is complete
Then no `rai publish` references remain in skills_base/
And references point to `rai release` as appropriate
```

### Scenario: Stale `rai base` references replaced
```gherkin
Given skills_base/ contains references to `rai base`
When S247.6 sweep is complete
Then no `rai base` references remain in skills_base/
And references point to `rai info` or `rai profile` as appropriate
```

### Scenario: CLAUDE.md CLI Quick Reference updated
```gherkin
Given CLAUDE.md is generated from .raise/ canonical source
When `rai init` is run after updates
Then CLAUDE.md CLI Quick Reference reflects new command structure
```

### Scenario: Verification gate passes
```gherkin
Given all replacements are complete
When the verification gate script runs
Then grep finds 0 stale references
And exit code is 0
```

## Examples (Specification by Example)

| Old Reference | New Reference | Context |
|---------------|---------------|---------|
| `rai memory build` | `rai graph build` | Graph construction |
| `rai memory query` | `rai graph query` | Graph querying |
| `rai memory context` | `rai graph context` | Module context |
| `rai memory add-pattern` | `rai pattern add` | Pattern creation |
| `rai memory emit-work` | `rai signal emit-work` | Telemetry signals |
| `rai publish check` | `rai release check` | Release checks |
| `rai publish run` | `rai release publish` | PyPI publish |
| `rai base` | `rai info` | Project info |
| `rai base profile` | `rai profile` | Developer profile |

## Notes
- 22 skills in skills_base/ to sweep
- Run `rai init` after to propagate to .claude/skills/ and .agent/skills/
- Verification gate defined in scope.md lines 215-223
- PAT-E-151 (rename long tail) — be methodical, grep after each batch
