---
name: rai-story-design
description: >
  Create lean story specifications optimized for both human understanding
  and AI alignment. Design is not optional (PAT-186) — use before /rai-story-plan
  for every story to ground integration decisions.

license: MIT

metadata:
  raise.work_cycle: story
  raise.frequency: per-story
  raise.fase: "4"
  raise.prerequisites: project-backlog
  raise.next: story-plan
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "2.0.0"
  raise.visibility: public
---

# Story Design

## Purpose

Create a lean story specification optimized for both human review (clear intent) and AI alignment (accurate code generation).

## Mastery Levels (ShuHaRi)

- **Shu**: Follow all steps, include examples for every story
- **Ha**: Skip optional sections for simple stories, adjust detail to complexity
- **Ri**: Custom spec patterns for specialized domains

## Context

**When to use:** Before planning any story that involves architectural decisions, multiple approaches, or >3 components.

**When to skip:** Simple stories (<3 components, obvious implementation) → go to `/rai-story-plan`.

**Inputs:** Story from backlog (ID, description, acceptance criteria), epic scope document.

## Steps

### Step 1: Assess Complexity

| Criterion | Simple | Moderate | Complex |
|-----------|--------|----------|---------|
| Components | 1-2 | 3-4 | 5+ |
| Story points | <5 | 5-8 | >8 |
| External integrations | 0-1 | 2-3 | 4+ |
| Algorithm complexity | Trivial | Custom logic | Novel |

| Result | Action |
|--------|--------|
| Simple | Skip design → `/rai-story-plan` |
| Moderate | Core sections only |
| Complex | Full spec with optional sections |

**Risk gate:** If story is marked HIGH RISK in epic scope, discuss risks before designing — name concerns, failure modes, and scope boundaries.

**UX gate:** If story touches human interaction (workflows, prompts, DX), recommend `/rai-research` first (~10 min, PAT-E-263).

<verification>
Complexity assessed. Risk/UX gates evaluated.
</verification>

### Step 2: Frame What & Why

- **Problem**: What gap does this fill? (1-2 sentences)
- **Value**: Why does this matter? (1-2 sentences, measurable or observable)

<verification>
Can explain to non-technical stakeholder in 30 seconds.
</verification>

### Step 3: Describe Approach

Document WHAT you're building and WHY this approach (not detailed HOW):
- Solution approach (1-2 sentences)
- Components affected (list with change type: create/modify/delete)

**For refactoring:** grep all call sites of the target. A half-migration is worse than none.

For complex stories, add: scenarios (Gherkin), algorithm pseudocode, constraints, testing strategy.

<verification>
Approach is concrete enough to envision examples.
</verification>

### Step 4: Create Examples (MOST IMPORTANT)

**This section drives AI code generation accuracy more than any other.**

Provide concrete, runnable examples:
1. **API/CLI usage** — how the story is invoked
2. **Expected output** — success + error cases
3. **Data structures** — key models, schemas, types

Use concrete values (not placeholders), correct syntax (not pseudocode), consistent with codebase style.

<verification>
Examples are concrete, runnable, and cover success + error paths.
</verification>

<if-blocked>
Can't envision examples → approach not concrete enough, return to Step 3.
</if-blocked>

### Step 5: Define Acceptance Criteria

- **MUST**: Required for completion (3-5 items, specific and testable)
- **SHOULD**: Nice-to-have (1-3 items)
- **MUST NOT**: Explicit anti-requirements

All criteria must be observable outcomes traceable to value from Step 2.

<verification>
Criteria are specific, testable, and traceable. Spec reviewable in <5 minutes.
</verification>

## Output

| Item | Destination |
|------|-------------|
| Design spec | `work/epics/e{N}-{name}/stories/s{N}.{M}-design.md` |
| Next | `/rai-story-plan` |

## Quality Checklist

- [ ] Complexity assessed — design depth matches complexity
- [ ] What & Why clear in <2 minutes
- [ ] Examples are concrete and runnable (100% coverage)
- [ ] Acceptance criteria specific and testable (3-5 MUST items)
- [ ] Risk/UX gates evaluated before designing
- [ ] Spec creation <30 minutes, review <5 minutes
- [ ] NEVER over-specify HOW — trust AI for implementation details
- [ ] NEVER skip examples — they are the most important section

## References

- Next: `/rai-story-plan`
- Risk assessment: PAT-186 (design not optional)
- UX research gate: PAT-E-263
