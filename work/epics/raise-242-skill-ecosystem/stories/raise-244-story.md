# Story: RAISE-244 rai-bugfix

> **Epic:** RAISE-242 (Skill Ecosystem)
> **Branch:** `epic/raise-242/skill-ecosystem` (S size — no dedicated branch)
> **Size:** S
> **Depends on:** RAISE-243 (rai-skill-create)

---

## User Story

**As a** RaiSE developer encountering a bug,
**I want** a `rai-bugfix` skill that guides me through systematic root cause analysis and fix,
**So that** I resolve defects with reproducibility, traceability, and clean commits — not just symptoms.

---

## Acceptance Criteria

```gherkin
Feature: rai-bugfix skill creation via rai-skill-create

  Scenario: rai-bugfix created from conversation
    Given rai-skill-create is invoked
    When I provide "rai-bugfix" as the skill name
    And I describe systematic bug fixing as the purpose
    Then the skill is scaffolded with rai skill scaffold
    And filled with content through conversation
    And it passes rai skill validate without errors

  Scenario: rai-bugfix guides a bug fix workflow
    Given rai-bugfix exists in .claude/skills/rai-bugfix/SKILL.md
    When a developer invokes /rai-bugfix
    Then they are guided through: reproduce → analyse → fix → test → commit → close
    And the workflow is traceable (branch, evidence, commit message)

  Scenario: E2E validation of rai-skill-create
    Given rai-bugfix was created using rai-skill-create
    When I review the process
    Then rai-skill-create worked without errors or workarounds
    And any friction discovered is documented as patterns
```

---

## Examples (SbE)

| Input | Expected Output |
|-------|----------------|
| `rai skill check-name rai-bugfix` | Name valid, no conflicts |
| `rai skill validate .claude/skills/rai-bugfix/SKILL.md` | All checks pass |
| `/rai-bugfix` invoked | Step-by-step bug fix workflow presented |
