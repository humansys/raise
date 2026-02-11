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
  raise.version: "1.1.0"
---

# Design: Feature Specification

## Purpose

Create a lean story specification that optimizes for both human understanding (quick review, clear intent) and AI alignment (accurate code generation).

**Core principle**: Specs are consumed by both humans AND AI - optimize for both.

## Mastery Levels (ShuHaRi)

**Shu (守)**: Follow template completely; include all required sections with examples.

**Ha (破)**: Skip optional sections for simple features; adjust detail to complexity.

**Ri (離)**: Create custom spec patterns for specialized domains or tool contexts.

## Context

**When to use:**
- Before planning complex features (>3 components, >5 SP, non-trivial logic)
- When feature requires architectural decisions or trade-offs
- When multiple implementation approaches exist
- When AI will generate significant code from the specification

**When to skip:**
- Simple features (<3 components, <5 SP, obvious implementation) → Go directly to `/rai-story-plan`
- Infrastructure/scaffolding work where implementation is self-evident
- Bug fixes (use issue tracker instead)
- Refactoring (unless substantial architectural change)

**Inputs required:**
- Feature from backlog (ID, description, story points, acceptance criteria)
- Technical Design (project-level) for architectural context
- Clarity on problem and value proposition

**Output:**
- Feature specification: `work/epics/e{N}-{name}/stories/f{N}.{M}-{name}/design.md`
- Uses lean template v2 (YAML + Markdown + Examples + Acceptance Criteria)

## Steps

### Step 0: Emit Feature Start (Telemetry)

Record the start of the design phase:

```bash
rai memory emit-work story {story_id} --event start --phase design
```

**Example:** `rai memory emit-work story S15.1 -e start -p design`

### Step 0.1: Verify Prerequisites & Load Context (Parallel)

Run these in parallel (all independent):

```bash
# Check epic context
ls work/epics/e{N}-*/scope.md 2>/dev/null || echo "WARN: No epic context"

# Query architecture patterns and ADRs
rai memory query "architecture patterns ADR" --types pattern,decision --limit 5
```

**From epic check:**
- Epic exists → Continue, reference in design
- Epic missing + simple feature → Continue with note
- Epic missing + complex feature → Suggest `/rai-story-start` first

**Skip condition:** Standalone bugfixes or experiments without epic.

**From memory query:**
- Learned patterns from prior features
- Prior architectural decisions (ADRs) relevant to this feature

**Verification:** Epic context loaded OR explicitly standalone; patterns noted.

> **If you can't continue:** Complex feature without epic → Run `/rai-story-start` first.

### Step 0.2: Load Architectural Context

Identify the primary module(s) this story affects, then load their architectural context:

```bash
rai memory context mod-<name>
# Example: rai memory context mod-memory
```

**How to identify the relevant module(s):**
- From the story scope: which source module(s) will be modified?
- Module names use `mod-` prefix (e.g., `mod-memory`, `mod-graph`, `mod-session`)
- If unclear, check the epic scope for module references
- For cross-cutting work, query multiple modules

**What this returns:**
- **Bounded context:** Which domain this module belongs to
- **Layer:** Architecture layer (leaf, domain, integration, orchestration)
- **Constraints:** Applicable guardrails (MUST and SHOULD)
- **Dependencies:** What this module depends on and what depends on it

**How to use the context in design:**
- Respect bounded context boundaries — don't cross domains without explicit justification
- Follow layer dependency rules — dependencies flow downward (orchestration → integration → domain → leaf)
- Address all MUST constraints in the design
- Note SHOULD constraints as recommendations
- Present an "Architectural Context" section in the design output summarizing module, domain, layer, and key constraints

**If module not found:** The module may not be in the graph yet. Continue without architectural context but note the gap.

**Verification:** Architectural context loaded OR gap noted.

### Step 1: Assess Complexity

Determine if feature needs a specification document.

**Complexity matrix**:

| Criterion | Simple | Moderate | Complex |
|-----------|--------|----------|---------|
| Components touched | 1-2 | 3-4 | 5+ |
| Story points | <5 | 5-8 | >8 |
| External integrations | 0-1 | 2-3 | 4+ |
| Algorithm complexity | Trivial | Some custom logic | Novel algorithms |
| State management | Stateless | Multiple states | Complex state machine |

**Decision**:
- **Simple** → Skip design, go to `/rai-story-plan`
- **Moderate** → Create spec, use core sections only
- **Complex** → Create spec, include optional sections as needed

> **If you can't continue:** Complexity unclear → Default to creating spec (safe choice)

### Step 1.5: Risk Assessment (Conditional)

**For features marked HIGH RISK in the epic scope**, pause to discuss risks before designing.

> *"Estudio en la duda, acción en la fe."* — Study in doubt, act in faith.

**Check for risk markers:**
```bash
grep -i "high risk\|HIGH RISK" work/epics/e*-*/scope.md 2>/dev/null | grep -i "{story_id}" || echo "No explicit risk marker"
```

**If HIGH RISK detected, discuss:**

1. **What makes this risky?** — Name the specific concerns (new capability, accuracy requirements, external dependencies, unclear scope)

2. **What could go wrong?** — Concrete failure modes, not abstract worries

3. **What would make you comfortable?** — Clear scope boundaries, honest confidence, user review steps, validation approach

4. **Scope decision:** Is this feature trying to solve a bigger problem than its SP suggests? Should we scope down?

**Output:** Document risk assessment in the design spec's Approach section or as a dedicated "Risks" section.

**Skip condition:** Feature not marked HIGH RISK and complexity is Simple/Moderate.

**Rationale:** Risk conversations before implementation clarify scope and build confidence. The doubt informs how we act, not whether we act.

> **If you can't continue:** Risks too unclear → Consider `/rai-research` skill first, or timebox a spike.

### Step 1.7: Research Gate for UX-Facing Stories (Conditional)

**If the story touches human interaction**, consider running `/rai-research` before designing.

**A story is "UX-facing" when it:**
- Introduces or changes user-facing workflows (onboarding, wizards, prompts)
- Designs information presentation for human consumption (dashboards, reports, summaries)
- Makes assumptions about user behavior, preferences, or mental models
- Touches developer experience (DX) — CLI ergonomics, error messages, skill output format

**Why:** In S-WELCOME (SES-142), 10 minutes of research prevented building the wrong thing entirely. Industry evidence on Dunning-Kruger, imposter syndrome, and zero-config convergence overturned the initial design instinct (mandatory wizard → sensible defaults). Cost is low (~10 min); value is high when it redirects.

**If UX-facing:**
> "This story touches human interaction. I recommend running `/rai-research` to ground the design in evidence before proceeding. ~10 min investment. Want to do that first?"

**Skip condition:** Story is purely technical (internal APIs, data processing, infrastructure, refactoring).

**Reference:** PAT-E-263

### Step 2: Frame What & Why

Define the feature's purpose and value clearly.

**Capture:**
- **Problem**: What gap does this fill? (1-2 sentences max)
- **Value**: Why does this matter? (1-2 sentences max)

**Quality criteria:**
- Problem is specific (not vague like "improve UX")
- Value is measurable or observable
- Can be explained to non-technical stakeholder in 30 seconds

> **If you can't continue:** Unclear value → Escalate to backlog refinement

### Step 3: Describe Approach (High-Level)

Describe WHAT you're building and WHY this approach, not detailed HOW.

**Document:**
- Solution approach (1-2 sentences)
- Components affected (list with change type: create/modify/delete)

**Focus on WHAT, not HOW** — trust AI to determine implementation details.

> **If you can't continue:** Too many unknowns → Spike needed; create research task

### Step 4: Create Examples (CRITICAL)

**This is the MOST IMPORTANT section for AI code generation accuracy.**

Provide concrete, runnable examples:

1. **API/CLI Usage Example** — How the feature is invoked
2. **Expected Output Example** — What it produces (success + error cases)
3. **Data Structures** — Key models, schemas, or types

**Quality criteria:**
- Examples use concrete values, not placeholders
- Code is in correct language/syntax (not pseudocode)
- Examples are consistent with existing codebase style

> **If you can't continue:** Can't envision examples → Approach not concrete enough; return to Step 3

### Step 5: Define Acceptance Criteria

Specify clear "done" conditions.

**Structure:**
- **MUST**: Required for completion (3-5 items)
- **SHOULD**: Nice-to-have (1-3 items)
- **MUST NOT**: Explicit anti-requirements

**Quality criteria:**
- Specific and testable (not "works well")
- Observable outcomes (not internal states)
- Traceable to user value from Step 2

> **If you can't continue:** Unclear what "done" means → Refine problem statement

### Step 6: Add Optional Sections (Complexity-Driven)

Based on complexity assessment:

**For COMPLEX features:**
- Detailed Scenarios (Gherkin for edge cases)
- Algorithm/Logic (pseudocode for non-obvious implementations)
- Constraints (performance, security, scalability)
- Testing Approach (specialized strategy)

**For MODERATE features:**
- Add 1-2 optional sections only if they clarify non-obvious aspects

> **If you can't continue:** Uncertain which sections → Default to fewer

### Step 7: Optimize for AI (Claude-Specific)

Apply emphasis patterns for critical requirements:

- `**IMPORTANT:**` for must-read context
- `**MUST:**` for non-negotiable requirements
- `**DO NOT:**` for explicit prohibitions

### Step 8: Review & Refine

Self-review checklist:
- [ ] YAML frontmatter complete
- [ ] What & Why clear (explain in 2 minutes)
- [ ] Approach describes WHAT at right level
- [ ] **Examples are concrete and runnable**
- [ ] Acceptance criteria specific and testable
- [ ] Optional sections justified by complexity
- [ ] Spec reviewable in <5 minutes
- [ ] Spec creation took <30 minutes

### Step 9: Emit Feature Complete (Telemetry)

Record the completion of the design phase:

```bash
rai memory emit-work story {story_id} --event complete --phase design
```

**Example:** `rai memory emit-work story S15.1 -e complete -p design`

## Output

- **Artifact**: `work/epics/e{N}-{name}/stories/f{N}.{M}-{name}/design.md`
- **Telemetry**: `.raise/rai/personal/telemetry/signals.jsonl` (feature_lifecycle: design start/complete)
- **Template**: `references/tech-design-story-v2.md`
- **Next**: `/rai-story-plan`

## Quality Standards

| Metric | Target |
|--------|--------|
| Creation time | <30 minutes |
| Review time | <5 minutes |
| Spec length (simple) | 50-80 lines |
| Spec length (complex) | 100-150 lines |
| Examples included | 100% |
| Acceptance criteria | 3-5 MUST items |

## Common Pitfalls

1. **Over-specifying "How"** — Focus on WHAT; trust AI for implementation
2. **Vague examples** — Use concrete values, not placeholders
3. **Untestable criteria** — Make them specific and measurable
4. **Filling optional sections "just because"** — Match to complexity
5. **Skipping spec for complex features** — Trust the complexity assessment
6. **Skipping risk discussion for HIGH RISK features** — The doubt clarifies scope

## Known Limitations

**Self-review (Step 8):** The builder verifying their own work is a form of muda (waste). Lean principles suggest separation of production and inspection. Future improvement: `/quality-review` skill with a reviewer-focused prompt. See `dev/parking-lot.md` → "Separation of Builder and Verifier".

## References

- Template: `references/tech-design-story-v2.md`
- Next skill: `/rai-story-plan`
