---
story_id: "S249.5"
title: "story-start v1.1 — User Story Artifact (Contract 3)"
epic_ref: "RAISE-249"
complexity: "simple"
status: "draft"
---

# Design: story-start v1.1 — User Story Artifact

## 1. What & Why

**Problem:** story-start v1.2 produces a scope commit (in/out/done) but no structured User Story artifact. story-design has no standardized input — it infers the "What & Why" from the scope commit text and epic context. The Connextra format, Gherkin AC, and SbE examples are generated late (in design or plan) instead of being defined upfront.

**Value:** Adding a User Story artifact (Contract 3) to story-start gives story-design structured input: role/capability/benefit (Connextra), behavior specs (Gherkin), and concrete examples (SbE). Gherkin AC flows through the entire chain — defined once, referenced everywhere, never duplicated.

## 2. Approach

Add Step 5.5 to `rai-story-start/SKILL.md` that produces a `story.md` artifact in Contract 3 format. Update the Output section to include the new artifact. Add depth heuristic so XS stories skip Gherkin ceremony.

**Components affected:**
- `.claude/skills/rai-story-start/SKILL.md` — modify (add Step 5.5, update Output, bump version)

## 3. Gemba: Current State

| Section | Current Content | What Changes | What Stays |
|---------|----------------|--------------|------------|
| Frontmatter | version 1.2.0 | → 1.3.0 | All other metadata |
| Steps 1-3 | Epic verification (branch, scope, feature in epic) | No change | As-is |
| Step 4 | Create feature branch + S/XS skip condition | No change | As-is |
| Step 5 | Define scope (in/out/done template) | No change | As-is |
| *(gap)* | — | **+Step 5.5 User Story Artifact** | — |
| Step 6 | Scope commit | No change | As-is |
| Step 7 | Display lifecycle stages | No change | As-is |
| Step 8 | Emit telemetry | No change | As-is |
| Output | Branch + scope commit + telemetry | **Add:** User Story artifact (`story.md`) | Existing outputs stay |
| Context § Output | 3 bullet points | **Add:** `story.md` with Contract 3 format | Existing bullets stay |
| Feature Start Summary | Template with scope summary | **Add:** story.md mention | Template structure stays |

## 4. New Content: Step 5.5

### Step 5.5: Create User Story Artifact

**Purpose:** Produce a structured User Story that story-design consumes as input (Contract 3). Defines WHO wants WHAT and WHY (Connextra), HOW it behaves (Gherkin), and concrete examples (SbE).

**Depth heuristic by story size:**

| Size | User Story Depth |
|------|-----------------|
| XS | Skip — scope commit is sufficient |
| S | Connextra + 1-2 Gherkin scenarios (happy path + 1 edge case) |
| M | Connextra + 3-5 Gherkin scenarios + SbE table |
| L+ | Full: Connextra + 5+ scenarios + SbE + Notes with epic design references |

**Artifact location:** `work/epics/{epic-id}/stories/{story-id}/story.md`

**Template (Contract 3 format):**

```markdown
---
story_id: "{story_id}"
title: "{title}"
epic_ref: "{epic_id}"
size: "{S|M|L}"
status: "draft"
created: "{date}"
---

# Story: {title}

## User Story
As a [role/persona],
I want [capability],
so that [benefit/outcome].

## Acceptance Criteria

### Scenario: {happy path}
\```gherkin
Given [initial context]
When [action]
Then [expected outcome]
\```

### Scenario: {edge case}
\```gherkin
Given [context]
When [action]
Then [outcome]
\```

## Examples (Specification by Example)

| Input | Action | Expected Output |
|-------|--------|----------------|
| [concrete value] | [concrete action] | [concrete result] |

## Notes
[context, constraints, references to epic design.md]
```

**How story-design consumes it:**
- User Story → frames the What & Why (Step 2)
- Gherkin scenarios → become acceptance criteria (Step 5 references, not duplicates)
- SbE examples → become test cases in story-plan
- Notes → link to epic design.md for component context

**Skip condition:** XS stories — scope commit is sufficient, no story.md needed.

**Verification:** `story.md` created with YAML frontmatter + Connextra + Gherkin scenarios.

## 5. Acceptance Criteria

No story.md exists for this meta-story (we're building the thing that produces story.md). Inline AC:

**MUST:**
- Step 5.5 added between Step 5 (scope) and Step 6 (commit)
- Contract 3 template included with YAML frontmatter + Connextra + Gherkin + SbE
- Depth heuristic table for XS/S/M/L+
- "How story-design consumes it" section explaining the contract
- Skip condition for XS stories documented
- Output section updated to include story.md
- Version bumped to 1.3.0
- Platform-agnostic (PAT-E-400): no language-specific examples in the template

**SHOULD:**
- Step 6 (scope commit) updated to also `git add` the story.md
- Feature Start Summary template mentions story.md

**MUST NOT:**
- Change Steps 1-5 or Steps 6-8 logic
- Add CLI code or template files
- Make Gherkin mandatory for XS stories
