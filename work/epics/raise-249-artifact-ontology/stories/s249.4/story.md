---
story_id: "S249.4"
title: "epic-design v1.2 — Separate scope.md / design.md"
epic_ref: "RAISE-249"
size: "S"
status: "draft"
created: "2026-02-22"
---

# Story: epic-design v1.2 — Separate scope.md / design.md

## User Story
As an AI agent running `/rai-epic-design`,
I want the skill to produce separate `scope.md` and `design.md` artifacts,
so that each downstream consumer gets a focused input (epic-plan gets scope, story-design gets design) instead of parsing one mixed document.

## Acceptance Criteria

### Scenario: Epic design produces two artifacts
```gherkin
Given an epic with a brief.md from epic-start
When I run /rai-epic-design
Then scope.md is created with objective, stories, in/out scope, and done criteria
And design.md is created with Gemba, target components, key contracts, and migration path
And scope.md does NOT contain implementation details (Gemba, interfaces)
And design.md does NOT contain project management details (story table, done criteria)
```

### Scenario: Downstream skills can consume the artifacts
```gherkin
Given scope.md and design.md produced by epic-design
When /rai-epic-plan reads scope.md
Then it finds the stories table and dependencies for sequencing
When /rai-story-design reads design.md
Then it finds component interfaces to refine to function level
```

## Notes
- Contract 2 format defined in `work/epics/raise-249-artifact-ontology/design.md` § Contract 2
- Current SKILL.md v1.0.0 produces a single `scope.md` with everything mixed
- The split aligns with separation of concerns: scope = PM artifact, design = engineering artifact
- PAT-E-400 (platform agnosticism): examples in skill should not assume Python-only
