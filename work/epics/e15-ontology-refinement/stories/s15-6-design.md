---
id: S15.6
name: Skills Integration — Ontology-Guided Design
size: S
sp: 3
epic: E15
depends_on: [S15.5]
---

# Design: S15.6 Skills Integration

## Problem

Design skills (`/story-design`, `/epic-design`, `/story-plan`) query the memory graph with ad-hoc keywords, missing architectural constraints, domain boundaries, and applicable guardrails. This caused 14 SP of rework in E14.

## Value

Every design decision starts grounded in the current architecture. Skills automatically surface bounded context, layer position, constraints, and guardrails — eliminating the class of errors where designs violate existing boundaries.

## Approach

Add a **"Load Architectural Context"** step to each of the 3 design skills. The step uses the `raise memory context <module>` CLI command (delivered in S15.5) to load structured architectural context before design begins.

**Components affected:**
- `.claude/skills/story-design/SKILL.md` — modify (add step)
- `.claude/skills/epic-design/SKILL.md` — modify (add step)
- `.claude/skills/story-plan/SKILL.md` — modify (add step)

**No code changes** — this is purely skill (Markdown) modifications.

## Design: The Architectural Context Step

### Pattern (reusable across all 3 skills)

Insert as a new step after prerequisites/context loading, before the main design work begins:

```markdown
### Step N: Load Architectural Context

Identify the primary module(s) this story/epic affects, then load their architectural context:

```bash
uv run raise memory context <module-name>
```

**How to identify the relevant module(s):**
- From the story scope: which source module(s) will be modified?
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

**If module not found:** The module may not be in the graph yet. Continue without architectural context but note the gap.
```

### Per-Skill Placement

**`/story-design`:** Insert as Step 0.2 (after Step 0.1 prerequisites, before Step 1 complexity assessment). The context informs whether the design needs to address domain boundaries or layer constraints.

**`/epic-design`:** Insert as Step 0.6 (after Step 0.5 query context, before Step 1 frame objective). For epics, query multiple modules since epics span features. Add guidance: "For each candidate module the epic might touch, load its context."

**`/story-plan`:** Insert as Step 0.6 (after Step 0.5 query context, before Step 1 select story). The architectural context informs task decomposition — tasks that cross bounded contexts should be separate.

### Output Section in Artifacts

Skills should present an "Architectural Context" section in their output artifacts when context is loaded:

```markdown
## Architectural Context

**Module:** memory
**Bounded Context:** Ontology (mod-ontology)
**Layer:** Domain
**Key Constraints:**
- MUST-CODE-001: Type hints on all code
- MUST-ARCH-002: Pydantic models for all schemas
- SHOULD-CODE-001: Use pathlib for file paths

**Dependencies:** graph (depends_on), telemetry (depends_on)
**Depended on by:** session, skills
```

## Examples

### Example 1: Story Design for memory module

```bash
$ uv run raise memory context memory
# Returns: bounded context (ontology), layer (domain),
# 21 constraints, 4 dependencies
```

The `/story-design` skill would include this in the design spec:
- Check that the design respects the ontology bounded context
- Verify layer dependencies flow correctly
- List applicable MUST constraints in acceptance criteria

### Example 2: Epic Design spanning multiple modules

```bash
$ uv run raise memory context memory
$ uv run raise memory context session
$ uv run raise memory context graph
```

The `/epic-design` skill would note cross-module dependencies and domain boundaries.

### Example 3: Story Plan with cross-boundary awareness

If a story touches both `memory` (ontology BC) and `session` (experience BC), the plan should:
- Create separate tasks for each bounded context
- Note the cross-domain dependency explicitly

## Acceptance Criteria

**MUST:**
- `/story-design` SKILL.md includes architectural context step after prerequisites
- `/epic-design` SKILL.md includes architectural context step with multi-module guidance
- `/story-plan` SKILL.md includes architectural context step informing task decomposition
- Each step references `raise memory context <module>` CLI command
- Graceful fallback when module not found in graph

**SHOULD:**
- Skills describe how to present "Architectural Context" section in output artifacts
- Step placement is consistent across skills (after context loading, before main work)

**MUST NOT:**
- Add new CLI commands (S15.5 already provides everything needed)
- Require architectural context as a hard gate (soft guidance, not blocking)
- Over-engineer the step with complex logic — it's a CLI call + interpretation guidelines
