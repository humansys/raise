---
story_id: RAISE-243
title: rai-skill-create ADR-040 Compliance
epic: RAISE-242
size: S
complexity: simple
---

# Design: RAISE-243 — rai-skill-create ADR-040 Compliance

## What & Why

**Problem:** `rai-skill-create` has 508 lines, uses stale CLI commands (`rai memory *`), has no
Quality Checklist, and carries a Notes section of philosophy. It violates ADR-040 on every metric.
The skill used to create skills teaches by the wrong example.

**Value:** A contract-compliant `rai-skill-create` generates skills with current CLI commands,
within the token target, and with Quality Checklist in the recency zone — where agents read it most.

## Approach

Refactor `.claude/skills/rai-skill-create/SKILL.md` in-place. Deterministic transformation:

| Change | From | To |
|--------|------|----|
| Lines | 508 | ≤150 |
| Sections | 8 (incl. Notes) | 7 fixed (ADR-040 order) |
| CLI commands | `rai memory *` | `rai graph/pattern/signal *` |
| Conditionals | Prose paragraphs | Decision tables |
| Quality Checklist | Missing | Present (recency zone) |
| Notes section | Philosophy + heuristics | Removed / collapsed to References |

**Component affected:** `.claude/skills/rai-skill-create/SKILL.md` — modify only.

## Examples

### CLI command mapping (all occurrences)

```bash
# BEFORE (stale ontology)
rai memory build
rai memory query "{topic}" --types pattern --limit 5
rai memory add-pattern "..." --context "..." --type process --from RAISE-N
rai memory emit-work story RAISE-N --event start --phase design
rai memory context mod-skills

# AFTER (current ontology)
rai graph build
rai graph query "{topic}" --types pattern --limit 5
rai pattern add "..." --context "..." --type process --from RAISE-N
rai signal emit-work story RAISE-N --event start --phase design
rai graph context mod-skills
```

### Memory indexing step (invariant — must be preserved)

```bash
# After writing SKILL.md, always index in graph:
rai graph build
rai graph query "{skill-name}" --types skill --format compact
```

### Section structure

```
# Skill Create

## Purpose
## Mastery Levels (ShuHaRi)
## Context
## Steps
## Output
## Quality Checklist   ← new, replaces Notes
## References
```

### Step compression example

The 9-step original compresses to ~5 steps by:
- Collapsing Step 4 (discover CLI) and Step 4a/4b/4c into one step with a table
- Collapsing Step 5 (design content) subsections into concise bullets
- Moving philosophy and heuristics from Notes to References links
- Decision tables replace prose conditionals in lifecycle and pattern sections

## Acceptance Criteria

**MUST:**
- `rai skill validate .claude/skills/rai-skill-create/SKILL.md` exits 0
- Exactly 7 sections in ADR-040 order
- Body ≤150 lines (frontmatter excluded)
- Zero occurrences of `rai memory` in body
- Quality Checklist present as penultimate section (before References)
- Memory indexing step preserved with `rai graph build`

**SHOULD:**
- Decision tables for lifecycle position and pattern classification (not prose)

**MUST NOT:**
- Remove the graph indexing step
- Modify the frontmatter schema
