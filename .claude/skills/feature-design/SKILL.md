---
name: feature-design
description: >
  Create lean feature specifications optimized for both human understanding
  and AI alignment. Use before planning complex features (>3 components, >5 SP),
  when architectural decisions are needed, or when AI will generate significant code.

license: MIT

metadata:
  raise.work_cycle: feature
  raise.frequency: per-feature-as-needed
  raise.fase: "4"
  raise.prerequisites: project-backlog
  raise.next: feature-plan
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "1.0.0"

hooks:
  PostToolUse:
    - matcher: "Write"
      hooks:
        - type: command
          command: "RAISE_SKILL_NAME=feature-design \"$CLAUDE_PROJECT_DIR\"/.claude/skills/scripts/log-artifact-created.sh"
  Stop:
    - hooks:
        - type: command
          command: "RAISE_SKILL_NAME=feature-design \"$CLAUDE_PROJECT_DIR\"/.claude/skills/scripts/log-skill-complete.sh"
---

# Design: Feature Specification

## Purpose

Create a lean feature specification that optimizes for both human understanding (quick review, clear intent) and AI alignment (accurate code generation).

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
- Simple features (<3 components, <5 SP, obvious implementation) → Go directly to `/feature-plan`
- Infrastructure/scaffolding work where implementation is self-evident
- Bug fixes (use issue tracker instead)
- Refactoring (unless substantial architectural change)

**Inputs required:**
- Feature from backlog (ID, description, story points, acceptance criteria)
- Technical Design (project-level) for architectural context
- Clarity on problem and value proposition

**Output:**
- Feature specification in `work/features/{feature-id}/design.md`
- Uses lean template v2 (YAML + Markdown + Examples + Acceptance Criteria)

## Steps

### Step 0: Emit Feature Start (Telemetry)

Record the start of the design phase:

```bash
raise telemetry emit feature {feature_id} --event start --phase design
```

**Example:** `raise telemetry emit feature F9.4 -e start -p design`

### Step 0.5: Query Context

Load relevant architecture patterns and ADRs from unified context:

```bash
raise context query "architecture patterns ADR" --unified --types pattern,feature --limit 5
```

Review returned patterns before proceeding. Key patterns inform design decisions.

**Verification:** Context loaded; relevant patterns noted.

> **If context unavailable:** Run `raise graph build --unified` first, or proceed without patterns.

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
- **Simple** → Skip design, go to `/feature-plan`
- **Moderate** → Create spec, use core sections only
- **Complex** → Create spec, include optional sections as needed

> **If you can't continue:** Complexity unclear → Default to creating spec (safe choice)

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
raise telemetry emit feature {feature_id} --event complete --phase design
```

**Example:** `raise telemetry emit feature F9.4 -e complete -p design`

## Output

- **Artifact**: `work/features/{feature-id}/design.md`
- **Telemetry**: `.rai/telemetry/signals.jsonl` (feature_lifecycle: design start/complete)
- **Template**: `references/tech-design-feature-v2.md`
- **Next**: `/feature-plan`

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

## References

- Template: `references/tech-design-feature-v2.md`
- Next skill: `/feature-plan`
