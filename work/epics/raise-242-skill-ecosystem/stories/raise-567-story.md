# Story: RAISE-567 rai-bugfix retrospective improvement

> **Epic:** RAISE-242 (Skill Ecosystem)
> **Branch:** `story/raise-567/bugfix-retrospective`
> **Size:** XS

---

## User Story

**As a** RaiSE developer closing a bug fix,
**I want** a structured retrospective in `rai-bugfix` Step 5 (Review),
**So that** causal insights are persisted with the right scope and behavioral patterns are reinforced — the same way `/rai-story-review` does it.

---

## Acceptance Criteria

```gherkin
Feature: rai-bugfix structured retrospective

  Scenario: heutagogical checkpoint in review phase
    Given a bug fix is complete
    When the developer runs rai-bugfix Step 5 (Review)
    Then they are asked 4 heutagogical questions with specific examples
    And their answers inform the retrospective document

  Scenario: pattern add with project scope
    Given a recurring or insightful bug cause is identified
    When the developer runs rai pattern add
    Then the command uses --scope project (not global)
    And the pattern is scoped to this codebase

  Scenario: behavioral pattern reinforcement
    Given behavioral patterns were loaded at session start
    When the review phase is complete
    Then the developer runs rai pattern reinforce for relevant patterns
    And votes 1 (followed), 0 (not relevant), or -1 (contradicted)
```

---

## Examples (SbE)

| Scenario | Expected |
|----------|----------|
| Recurring bug | `rai pattern add "..." --scope project --from RAISE-N` |
| Pattern followed | `rai pattern reinforce {id} --vote 1 --from RAISE-N` |
| Retro doc | `work/bugs/RAISE-N/retro.md` with checkpoint + patterns section |
