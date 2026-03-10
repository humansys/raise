---
story_id: "S249.3"
title: "epic-start v1.1 — Epic Brief Artifact (Contract 1)"
epic_ref: "RAISE-249"
size: "S"
status: "draft"
created: "2026-02-22"
---

# Story: epic-start v1.1 — Epic Brief Artifact (Contract 1)

## User Story
As a developer starting a new epic,
I want epic-start to produce a structured Epic Brief artifact,
so that epic-design receives typed input (hypothesis, appetite, boundaries) instead of starting from scratch.

## Acceptance Criteria

### Scenario: Epic Brief produced on epic start
```gherkin
Given a developer runs /rai-epic-start for a new epic
When Step 3.5 executes
Then a brief.md file is created at work/epics/{epic-id}/brief.md
And the file contains YAML frontmatter with epic_id, title, status, created
And the file contains Hypothesis, Success Metrics, Appetite, and Scope Boundaries sections
```

### Scenario: epic-design consumes the brief
```gherkin
Given a brief.md exists for an epic
When the developer runs /rai-epic-design
Then epic-design reads the brief's Hypothesis to frame the objective
And epic-design reads the Appetite to constrain story count
And epic-design reads No-Gos as Out of Scope
And epic-design reads Rabbit Holes as Risks
```

## Notes
- Contract 1 format defined in epic design.md § Contract 1
- SAFe Lean Startup hypothesis format + Shape Up appetite/no-gos/rabbit holes
- epic-design (S4) will add the consumption side — this story only adds production
