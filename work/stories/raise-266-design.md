# Design: RAISE-266 Contract Chain Lean

## What & Why

**Problem:** After E250 skill compression, lifecycle skills produce/consume artifacts independently — no typed contract between them. The chain designed in RAISE-249 (brief→scope→story→design→plan) was lost.

**Value:** Typed artifacts between skills make each phase ground the next. Implementation becomes mechanical because every decision is already made upstream.

## Gemba: Current State

| Skill | Lines | Budget | Produces | Consumes | Chain Gap |
|-------|:-----:|:------:|----------|----------|-----------|
| `rai-epic-start` | 140 | 10 | `scope.md` (informal) | — | No brief artifact |
| `rai-epic-design` | 164 | -14 | `scope.md` (mixed WHAT+HOW) | Problem Brief (optional) | No design.md, already over limit |
| `rai-story-start` | 136 | 14 | `scope.md` (informal) | Epic scope | No story artifact with AC |
| `rai-story-design` | 143 | 7 | `design.md` | Story scope | Doesn't read story.md AC |
| `rai-story-plan` | 129 | 21 | `plan.md` | Design doc | No AC traceability |

## Approach

**Key constraint:** Skills must stay ≤150 lines. Templates carry the artifact format; skills just reference them.

**Strategy:** Each change is 3-8 net lines in the skill + a template file in `templates/`.

### Change 1: `rai-epic-start` — Add brief.md artifact

**Current Step 3** creates `scope.md`. Split into TWO artifacts:
- `scope.md` stays (boundaries, stories, done criteria) — already there
- `brief.md` added (hypothesis, success metrics, appetite, rabbit holes)

Skill change: In Step 3, add 4 lines referencing `templates/brief.md` as second artifact.
Template: `templates/brief.md` (~25 lines, SAFe hypothesis format)

**Net skill delta:** +4 lines (140→144) ✓

### Change 2: `rai-epic-design` — Consume brief, produce design.md

**Current Step 1** already checks for Problem Brief. Add brief.md check too.
**Current Step 5** writes only scope.md. Add design.md as second output.

Skill changes:
- Step 1: +1 line (check for `brief.md` alongside Problem Brief)
- Step 5: +2 lines (create `design.md` using template when epic involves architecture)
- Output table: +1 line
- **Also trim:** Step 2 ADR table (3 lines compressible), Step 4 risk template (2 lines)

Template: `templates/design.md` (~20 lines, Gemba + target components)

**Net skill delta:** -1 line (164→163... still over). Need ~15 more lines trimmed.

**Aggressive trim targets:**
- ShuHaRi section: 3→2 lines (combine Ha+Ri)
- Context section: merge "When to skip" into "When to use"
- Step 1 heuristic table: 3 rows → inline sentence
- Step 3 heuristic table: 4 rows → 2 rows
- Step 4 risk template row: remove example `{risk}` placeholder

**Net after trim:** ~148 lines ✓

### Change 3: `rai-story-start` — Add story.md artifact

**Current Step 3** creates `scope.md`. Add `story.md` as second artifact.

Skill change: In Step 3, add 5 lines referencing `templates/story.md`.
Template: `templates/story.md` (~20 lines, Connextra + Gherkin)

**Net skill delta:** +5 lines (136→141) ✓

### Change 4: `rai-story-design` — Consume story.md

**Current Step 2** (Frame What & Why) works from scratch. Should load `story.md` first.
**Current Step 5** (Acceptance Criteria) generates AC from scratch. Should reference `story.md`.

Skill changes:
- Step 2: +2 lines (load story.md, use its User Story as starting frame)
- Step 5: +2 lines (reference story.md Gherkin AC instead of generating from scratch)
- Context Inputs line: update to mention story.md

**Net skill delta:** +4 lines (143→147) ✓

### Change 5: `rai-story-plan` — AC traceability

**Current Step 2** creates tasks without AC reference. Add traceability.

Skill change: In Step 2 "Per task" bullet list, add 1 line: AC scenario reference from story.md.

**Net skill delta:** +1 line (129→130) ✓

## Examples

### brief.md template (in `rai-epic-start/templates/`)

```markdown
---
epic_id: "{EPIC_ID}"
title: "{title}"
status: "draft"
created: "YYYY-MM-DD"
---

# Epic Brief: {title}

## Hypothesis
For [target users] who [need/pain],
the [solution] is a [category]
that [delivers this value].
Unlike [current state], our solution [key differentiator].

## Success Metrics
- **Leading:** [early signal]
- **Lagging:** [outcome after epic]

## Appetite
[S/M/L] — [S=2-4, M=5-7, L=8-10 stories]

## Rabbit Holes
- [attractive trap to avoid]
```

### story.md template (in `rai-story-start/templates/`)

```markdown
---
story_id: "{STORY_ID}"
epic_ref: "{EPIC_ID}"
size: "{XS|S|M|L}"
status: "draft"
---

# Story: {title}

## User Story
As a [role],
I want [capability],
so that [benefit].

## Acceptance Criteria

### Scenario: {happy path}
```gherkin
Given [context]
When [action]
Then [outcome]
```

### Scenario: {edge case}
```gherkin
Given [context]
When [action]
Then [outcome]
```
```

### design.md template (in `rai-epic-design/templates/`)

```markdown
---
epic_id: "{EPIC_ID}"
grounded_in: "Gemba of [files]"
---

# Epic Design: {title}

## Affected Surface (Gemba)
| Module/File | Current State | Changes |

## Target Components
| Component | Responsibility | Key Interface |

## Key Contracts
[Types and interfaces at component level]

## Migration Path
[Backward compat strategy, if restructuring]
```

## Acceptance Criteria

**MUST:**
- `rai-epic-start` produces `brief.md` alongside `scope.md`
- `rai-story-start` produces `story.md` alongside `scope.md`
- `rai-epic-design` reads `brief.md`, produces `design.md` alongside `scope.md`
- `rai-story-design` reads `story.md` AC
- All 5 skills ≤150 lines

**SHOULD:**
- `rai-story-plan` tasks reference story.md AC scenarios
- Templates match RAISE-249 contract formats (lean versions)

**MUST NOT:**
- Inline full template content in skills (templates stay in `templates/`)
- Break ADR-040 line limit (≤150)
