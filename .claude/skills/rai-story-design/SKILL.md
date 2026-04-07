---
name: rai-story-design
description: Create lean story spec for human review and AI alignment. Use before story plan.

allowed-tools:
  - Read
  - Edit
  - Write
  - Grep
  - Glob
  - "Bash(rai:*)"

license: MIT

metadata:
  raise.work_cycle: story
  raise.frequency: per-story
  raise.fase: "4"
  raise.prerequisites: project-backlog
  raise.next: story-plan
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "2.5.0"
  raise.visibility: public
  raise.output_type: story-design
  raise.inputs: |
    - story_md: file_path, required, previous_skill
    - scope_md: file_path, optional, previous_skill
  raise.outputs: |
    - design_yaml: file_path, .raise/artifacts/
    - design_md: file_path, next_skill
  raise.aspects: introspection
  raise.introspection:
    phase: story.design
    context_source: scope doc
    affected_modules: []
    max_tier1_queries: 3
    max_jit_queries: 5
    tier1_queries:
      - "patterns for {affected_modules} design decisions"
      - "prior designs for similar scope in {phase}"
      - "risks and lessons from related epics"
---

# Story Design

## Purpose

Create a lean story specification optimized for both human review (clear intent) and AI alignment (accurate code generation).

## Mastery Levels (ShuHaRi)

- **Shu**: Follow all steps, include examples for every story
- **Ha**: Adjust depth to complexity, but never skip the gemba walk
- **Ri**: Custom spec patterns for specialized domains

## Context

**When to use:** Before planning ANY story. Design is never optional — it is the gemba walk that prevents duplicate components, wasted effort, and wrong approaches.

**Inputs:** Story from backlog, User Story artifact (`story.md` from `/rai-story-start`), epic scope/design documents.

## Steps

### PRIME (mandatory — do not skip)

Before starting Step 1, you MUST execute the PRIME protocol:

1. **Chain read**: No chain read — story-design is the first skill in the story chain.
2. **Graph query**: Execute tier1 queries from this skill's metadata using `rai graph query`. If graph is unavailable, note and continue.
3. **Present**: Surface retrieved patterns as context. 0 results is valid — not a failure.

### Step 1: Assess Complexity

| Criterion | Simple | Moderate | Complex |
|-----------|--------|----------|---------|
| Components | 1-2 | 3-4 | 5+ |
| Story points | <5 | 5-8 | >8 |
| External integrations | 0-1 | 2-3 | 4+ |
| Algorithm complexity | Trivial | Custom logic | Novel |

| Result | Action |
|--------|--------|
| Simple | Lean design — core sections, quick gemba walk |
| Moderate | Core sections + examples |
| Complex | Full spec with all sections |

> **JIT**: Before assessing complexity, query graph for patterns from similar stories
> → `aspects/introspection.md § JIT Protocol`

**Risk gate:** If story is marked HIGH RISK in epic scope, discuss risks before designing — name concerns, failure modes, and scope boundaries.

**UX gate:** If story touches human interaction (workflows, prompts, DX), recommend `/rai-research` first (~10 min).

**Integration gate:** If story name includes "dogfood", "E2E", or "integration", OR if epic has separate client/server stories developed with mocks — AC MUST include at least one scenario that runs with **real infrastructure** (docker compose, actual DB, real HTTP calls). Unit tests with mocks cannot catch cross-component contract mismatches (auth headers, payload validation, parameter limits).

<verification>
Complexity assessed. Risk/UX/Integration gates evaluated.
</verification>

### Step 2: Gemba Walk (mandatory — do not skip)

Go to the actual code. Design without reading the code is guessing.

1. **Read what exists**: Open and read the files/modules that this story will touch. Understand the current state before proposing changes.
2. **Search for duplicates**: Grep for similar functionality, components, or patterns that already exist. Before creating anything new, verify it doesn't exist already.
3. **Check best practices**: Look at how similar problems are solved in the codebase. Follow established patterns rather than inventing new ones.
4. **Map dependencies**: Identify what depends on the code you'll change, and what the changed code depends on.

```bash
# Example gemba commands
grep -r "similar_function" packages/  # Does this already exist?
grep -r "class SimilarModel" packages/ # Duplicate models?
```

| Finding | Action |
|---------|--------|
| Similar component exists | Reuse or extend it — do NOT create a duplicate |
| No established pattern | Document the new pattern as a design decision |
| Multiple approaches found | List them in Step 4 with trade-offs |

<verification>
Code has been read. No duplicate components will be created. Existing patterns identified.
</verification>

### Step 3: Frame What & Why (informed by gemba)

Load `story.md` (from `/rai-story-start`) if it exists — use its User Story as starting frame.

> **JIT**: Before framing problem and value, query graph for prior designs with similar scope
> → `aspects/introspection.md § JIT Protocol`

- **Problem**: What gap does this fill? (1-2 sentences)
- **Value**: Why does this matter? (1-2 sentences, measurable or observable)

<verification>
Can explain to non-technical stakeholder in 30 seconds.
</verification>

### Step 4: Describe Approach (lean principles)

> **JIT**: Before describing approach, query graph for implementation patterns in affected modules
> → `aspects/introspection.md § JIT Protocol`

Document WHAT you're building and WHY this approach (not detailed HOW):
- Solution approach (1-2 sentences)
- Components affected (list with change type: create/modify/delete)

**Lean design gates** — challenge every component before committing:

- **KISS**: Is this the simplest approach that works? If not, simplify.
- **DRY**: Does this duplicate logic that exists elsewhere (gemba walk should have found it)?
- **YAGNI**: Are you building for a real requirement or a hypothetical one? Cut speculative features.
- **MVP**: What is the smallest version that delivers the value from Step 3? Build that, not more.

**For refactoring:** grep all call sites of the target. A half-migration is worse than none.

**For data mutations:** What happens when inputs reference missing entities? Declare the strategy explicitly: reject with error, skip + report count, partial success with warnings. Silent drops are semantic bugs.

**Value preservation gate:** Before finalizing components, ask: "What domain knowledge does this layer provide that a generic pass-through wouldn't?" If the answer is "none", the design may be over-abstracted. If the answer involves config/resolution/mapping that an existing pattern handles differently, check where that responsibility lives in the proven pattern.

For complex stories, add: scenarios (Gherkin), algorithm pseudocode, constraints, testing strategy.

<verification>
Approach is concrete enough to envision examples. Value preservation gate passed.
</verification>

### Step 5: Create Examples (MOST IMPORTANT)

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

### Step 6: Define Acceptance Criteria

> **JIT**: Before defining acceptance criteria, query graph for testing patterns and quality standards
> → `aspects/introspection.md § JIT Protocol`

If `story.md` has Gherkin AC, reference them here — refine, don't duplicate. If no `story.md`, define from scratch:

- **MUST**: Required for completion (3-5 items, specific and testable)
- **SHOULD**: Nice-to-have (1-3 items)
- **MUST NOT**: Explicit anti-requirements

All criteria must be observable outcomes traceable to value from Step 2.

<verification>
Criteria are specific, testable, and traceable. Spec reviewable in <5 minutes.
</verification>

## Output

After completing all steps, produce the design in two locations:

### 1. Typed artifact (source of truth)

Write a YAML artifact to `.raise/artifacts/s{N}.{M}-design.yaml` with this structure:

```yaml
artifact_type: story-design
version: 1
skill: rai-story-design
created: '{ISO 8601 timestamp}'
story: 'S{N}.{M}'
epic: 'E{N}'
content:
  summary: '{Problem + Value in 1-2 sentences}'
  complexity: simple|moderate|complex
  acceptance_criteria:
    - id: AC1
      description: '{criterion text}'
      verifiable: true
  integration_points:
    - module: '{dotted.module.path}'
      change_type: new|modification|deletion
      files: ['{relative/path.py}']
  decisions:
    - id: D1
      choice: '{what was chosen}'
      rationale: '{why}'
      alternatives_considered: ['{alt1}', '{alt2}']
refs:
  backlog_item: '{RAISE-NNN}'
  epic_scope: 'work/epics/e{N}-{name}/scope.md'
metadata: {}
```

### 2. Human-readable Markdown

Write the design as `work/epics/e{N}-{name}/stories/s{N}.{M}-design.md` — colocated with other story artifacts (story.md, scope.md, plan.md, retrospective.md).

| Item | Destination |
|------|-------------|
| Typed artifact | `.raise/artifacts/s{N}.{M}-design.yaml` |
| Design document | `work/epics/e{N}-{name}/stories/s{N}.{M}-design.md` |
| Next | `/rai-story-plan` |

## Quality Checklist

- [ ] Complexity assessed — design depth matches complexity
- [ ] Gemba walk done — actual code read, duplicates checked, patterns identified
- [ ] Lean gates passed: KISS, DRY, YAGNI, MVP — simplest version that delivers value
- [ ] What & Why clear in <2 minutes
- [ ] Examples are concrete and runnable (100% coverage)
- [ ] Acceptance criteria specific and testable (3-5 MUST items)
- [ ] Risk/UX/Integration gates evaluated before designing
- [ ] Data mutation stories declare missing-entity strategy
- [ ] Value preservation gate: domain intelligence preserved, not simplified away
- [ ] Spec creation <30 minutes, review <5 minutes
- [ ] NEVER over-specify HOW — trust AI for implementation details
- [ ] NEVER skip examples — they are the most important section

## References

- Next: `/rai-story-plan`
- Risk assessment: design is not optional
- UX research gate: `/rai-research` before UX stories
- Value preservation gate: domain intelligence over abstraction
