---
story_id: "S211.3"
title: "rai memory build → registry"
epic_ref: "RAISE-211"
size: "M"
status: "draft"
created: "2026-02-22"
---

# Story: rai memory build → registry

## User Story
As a plugin developer,
I want governance parsers discovered via entry points instead of hardcoded imports,
so that external packages can contribute parsers without modifying raise-cli core.

## Acceptance Criteria

### Scenario: Built-in parsers discovered via registry
```gherkin
Given raise-cli is installed with default entry points
When I run `rai memory build`
Then all 10 governance parsers are discovered via `get_governance_parsers()`
And the resulting graph is functionally identical to the current hardcoded output
```

### Scenario: External parser registered via entry point
```gherkin
Given an external package registers a parser in `rai.governance.parsers`
When I run `rai memory build`
Then the external parser is included alongside built-in parsers
And its nodes appear in the graph
```

### Scenario: Broken parser degrades gracefully
```gherkin
Given a registered parser raises an exception during parse()
When I run `rai memory build`
Then the build completes successfully
And a warning is logged for the broken parser
And all other parsers contribute their nodes normally
```

### Scenario: GovernanceExtractor uses registry path
```gherkin
Given the GovernanceExtractor is instantiated
When extract_all() is called
Then parsers are loaded via registry, not hardcoded imports
And the extraction result matches current behavior
```

## Examples (Specification by Example)

| Parser | Current Location | Wraps Directly | Needs Refactor |
|--------|-----------------|:--------------:|:--------------:|
| requirements (prd) | parsers/prd.py | Yes | No |
| outcomes (vision) | parsers/vision.py | Yes | No |
| principles (constitution) | parsers/constitution.py | Yes | No |
| releases (roadmap) | parsers/roadmap.py | Yes | No |
| epics (backlog) | parsers/backlog.py | Yes | No |
| stories (epic) | parsers/epic.py | Yes | No |
| decisions (adr) | parsers/adr.py | No | Glob logic internal |
| guardrails | parsers/guardrails.py | No | Glob logic internal |
| terms (glossary) | parsers/glossary.py | No | Glob logic internal |
| epic_details (epic) | parsers/epic.py | Yes | No |

## Notes
- Gemba from SES-247 validated: 6 parsers wrap directly, 3-4 need glob logic extracted
- Don't implement GovernanceSchemaProvider as a formal class yet — YAGNI
- Builder `load_governance()` currently delegates to GovernanceExtractor which hardcodes imports
- `_concept_to_node()` conversion stays in builder (Concept → ConceptNode mapping)
- Zero regression: snapshot test comparing before/after graph is the safety net
- ADR references: ADR-033, ADR-034
