---
story_id: RAISE-243
title: rai-skill-create
epic: RAISE-242
size: M
complexity: moderate
---

# Design: RAISE-243 rai-skill-create

## What & Why

**Problem:** Creating new RaiSE skills requires manually reading existing skills, copying structure, and knowing conventions. The scaffold command generates a template full of TODOs that still needs significant knowledge to fill correctly.

**Value:** A conversational skill that guides the user through skill creation, composing existing CLI tools and reading reference patterns. Reduces errors, ensures consistency, and lowers the barrier for expanding the skill ecosystem.

## Architectural Context

**Module:** `mod-skills` (domain layer, `bc-skills`)
**Impact:** Zero code changes to `src/`. This is a pure SKILL.md file in `.claude/skills/rai-skill-create/`.
**Infra used:** `rai skill check-name`, `rai skill scaffold`, `rai skill validate`

## Approach

The skill creator is an **orchestration skill** — it composes existing CLI tools in a conversational flow. The intelligence is in the conversation design, not in new code.

**Flow:**

```
User intent → Step 1: Understand purpose
    ↓
Step 2: Derive name → rai skill check-name
    ↓
Step 3: Determine lifecycle position (prerequisites, next, gate)
    ↓
Step 4: Read reference skills for domain patterns
    ↓
Step 5: Design skill content (Purpose, Context, Steps, Output)
    ↓
Step 6: Write SKILL.md (frontmatter + body)
    ↓
Step 7: Validate → rai skill validate
    ↓
Step 8: Present summary + next steps
```

**CLI vs Inference balance:** ~30% CLI (check-name, scaffold metadata, validate), ~70% inference (content design, pattern matching, conversational guidance).

## Components Affected

| Component | Change | Notes |
|-----------|--------|-------|
| `.claude/skills/rai-skill-create/SKILL.md` | Create | The skill itself |
| No `src/` changes | — | Uses existing CLI infra as-is |

## Examples

### Invocation

```
User: /rai-skill-create
User: Quiero crear un skill para code review
```

### CLI Tool Usage (within skill steps)

```bash
# Step 2: Name validation
rai skill check-name rai-review-code

# Step 4: Find reference skills by listing all, then read relevant ones
rai skill list --format json
# Then read SKILL.md files of similar domain skills

# Step 7: Validation
rai skill validate .claude/skills/rai-review-code/SKILL.md
```

### Generated Output (SKILL.md frontmatter)

```yaml
---
name: rai-review-code
description: >
  Systematic code review focusing on correctness, security, and maintainability.
  Use after implementation to catch issues before merge.

license: MIT

metadata:
  raise.work_cycle: story
  raise.frequency: per-story
  raise.fase: "7"
  raise.prerequisites: "rai-story-implement"
  raise.next: "rai-story-close"
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "1.0.0"
---
```

### Generated Output (body sections)

The skill creator fills each required section (Purpose, Context, Steps, Output) with content derived from conversation + reference patterns. NOT scaffold TODOs — real content.

## Acceptance Criteria

**MUST:**
- Skill validates name via `rai skill check-name` before proceeding
- Skill generates a complete SKILL.md (frontmatter + all required sections)
- Generated SKILL.md passes `rai skill validate` without errors
- Skill reads at least 1 reference skill from the same domain for pattern matching
- ShuHaRi levels defined in the skill itself

**SHOULD:**
- Conversational flow adapts to user's clarity level (asks more if vague, less if precise)
- Lifecycle metadata (work_cycle, frequency, fase) inferred from domain when possible

**MUST NOT:**
- Modify any file in `src/` — this is a pure SKILL.md
- Generate skills with TODO placeholders — all content must be filled
- Skip validation step
