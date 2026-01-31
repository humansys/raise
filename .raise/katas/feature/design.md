---
id: feature-design
titulo: "Design: Feature Specification"
work_cycle: feature
frequency: per-feature-as-needed
fase_metodologia: 4

prerequisites:
  - project/backlog
template: templates/tech/tech-design-feature-v2.md
gate: null
next_kata: feature/plan

adaptable: true
shuhari:
  shu: "Follow template completely; include all required sections with examples"
  ha: "Skip optional sections for simple features; adjust detail to complexity"
  ri: "Create custom spec patterns for specialized domains or tool contexts"

version: 1.0.0
---

# Design: Feature Specification

## Purpose

Create a lean feature specification that optimizes for both human understanding (quick review, clear intent) and AI alignment (accurate code generation), based on evidence from 25+ research sources.

**Core principle**: Specs are consumed by both humans AND AI - optimize for both.

## Context

**When to use:**
- Before planning complex features (>3 components, >5 SP, non-trivial logic)
- When feature requires architectural decisions or trade-offs
- When multiple implementation approaches exist
- When AI will generate significant code from the specification

**When to skip:**
- Simple features (<3 components, <5 SP, obvious implementation) → Go directly to `feature/plan`
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

### Step 1: Assess Complexity

Determine if feature needs a specification document.

**Complexity matrix**:

| Criterion | Simple | Moderate | Complex |
|-----------|--------|----------|---------|
| **Components touched** | 1-2 | 3-4 | 5+ |
| **Story points** | <5 | 5-8 | >8 |
| **External integrations** | 0-1 | 2-3 | 4+ |
| **Algorithm complexity** | Trivial/standard | Some custom logic | Novel algorithms |
| **State management** | Stateless or simple | Multiple states | Complex state machine |
| **Error scenarios** | 1-2 cases | 3-5 cases | Many edge cases |

**Decision matrix**:
- **Simple** (1-2 criteria match Simple) → Skip design kata, go to `feature/plan`
- **Moderate** (3+ criteria match Moderate) → Create feature spec, use core sections only
- **Complex** (2+ criteria match Complex) → Create feature spec, include optional sections as needed

**Verification:** Complexity level determined and documented.

> **If you can't continue:** Complexity unclear → Default to creating spec (safe choice - better to over-document than under-specify)

---

### Step 2: Frame What & Why

Define the feature's purpose and value clearly and concisely.

**What to capture:**
- **Problem**: What gap does this fill? What pain does it solve? (1-2 sentences max)
- **Value**: Why does this matter to users/project/stakeholders? (1-2 sentences max)

**Quality criteria:**
- Problem is specific (not vague like "improve UX")
- Value is measurable or observable (not abstract)
- Can be explained to non-technical stakeholder in 30 seconds

**Example (good)**:
- Problem: "Users can't cancel in-progress tasks, leading to wasted resources"
- Value: "Enables resource cleanup and better user control, reducing cloud costs"

**Example (bad)**:
- Problem: "Task management needs improvement"
- Value: "Better UX"

**Verification:** Problem and value clearly stated in 1-2 sentences each.

> **If you can't continue:** Unclear value proposition → Escalate to backlog refinement; feature may not be justified

---

### Step 3: Describe Approach (High-Level)

Describe WHAT you're building and WHY this approach, not detailed HOW.

**What to document:**
- Solution approach (1-2 sentences describing the general strategy)
- Components affected (list with change type: create/modify/delete)

**Focus areas:**
- **What** will be built (the capability)
- **Why** this approach (constraints, trade-offs)
- **NOT** step-by-step implementation details (that's for AI to determine)

**Example (good)**:
```markdown
**Approach**: Add cancellation API endpoint and background job cleanup mechanism.

**Components**:
- **API routes**: Add POST /tasks/{id}/cancel endpoint
- **Task executor**: Modify to check cancellation flag
- **Database schema**: Add cancelled_at timestamp field
```

**Example (bad - over-specified)**:
```markdown
**Approach**: Create a new TaskCancellationService class with a cancel() method
that will first acquire a lock, then update the database using SQLAlchemy ORM,
then publish a RabbitMQ message to the worker queue using pika library...
```

**Verification:** Approach describes WHAT at appropriate abstraction level (not too vague, not too detailed).

> **If you can't continue:** Too many unknowns or multiple conflicting approaches → Spike needed; create research task or ADR

---

### Step 4: Create Examples (REQUIRED - Most Critical Section)

**This is the MOST IMPORTANT section for AI code generation accuracy.**

Provide concrete, runnable (or near-runnable) examples.

**What to include:**

1. **API/CLI Usage Example**
   - Show how the feature is invoked
   - Use realistic parameters/data
   - Could be copied and run

2. **Expected Output Example**
   - What the feature produces
   - Include realistic responses/data
   - Show both success and common error cases

3. **Data Structures** (if applicable)
   - Key models, schemas, or types
   - Example: Pydantic models, TypeScript interfaces, database schemas

**Quality criteria:**
- Examples use concrete values, not placeholders like `<value>` or `TODO`
- Examples cover happy path + 1-2 common cases
- Code is in correct language/syntax (not pseudocode unless truly necessary)
- Examples are consistent with existing codebase style

**Example (good)**:
```python
# API Usage
from raise_cli import KataEngine

engine = KataEngine(kata_id="project/discovery")
result = engine.execute()

# Expected Output
{
    "kata_id": "project/discovery",
    "status": "completed",
    "artifacts_created": ["governance/project/prd.md"],
    "duration_seconds": 1247
}

# Data Structure
class KataResult(BaseModel):
    kata_id: str
    status: Literal["pending", "in_progress", "completed", "failed"]
    artifacts_created: list[Path]
    duration_seconds: int
```

**Verification:** Examples are concrete, runnable, and cover key scenarios.

> **If you can't continue:** Can't envision concrete examples → Approach not concrete enough; return to Step 3 and add more specifics

---

### Step 5: Define Acceptance Criteria

Specify clear "done" conditions that are testable and observable.

**Structure:**
- **MUST**: Required for feature completion (3-5 items typically)
- **SHOULD**: Nice-to-have, defer if time-constrained (1-3 items)
- **MUST NOT**: Explicit anti-requirements (what to avoid)

**Quality criteria for good acceptance criteria:**
- **Specific**: Not vague ("works well" ❌ / "responds in <100ms" ✓)
- **Testable**: Can be verified programmatically or manually
- **Observable**: Focus on outcomes, not internal states
- **Complete**: Covers functional + non-functional requirements
- **Traceable**: Links back to user value from Step 2

**Example (good)**:
```markdown
### Must Have
- [ ] CLI command `raise kata run {id}` executes specified kata
- [ ] All kata steps displayed with instructions and verification prompts
- [ ] State persists if execution interrupted (can resume)
- [ ] Exit code 0 on success, non-zero on failure

### Should Have
- [ ] Progress bar showing completion percentage
- [ ] Elapsed time displayed for each step

### Must NOT
- [ ] Execute kata if prerequisites not met (must fail fast with clear error)
- [ ] Modify files outside work/ directory without explicit confirmation
```

**Example (bad - vague)**:
```markdown
### Must Have
- [ ] Feature works correctly
- [ ] Good error handling
- [ ] Performant execution
```

**Verification:** Acceptance criteria are specific, testable, and complete.

> **If you can't continue:** Unclear what "done" means → Refine problem statement in Step 2; feature definition may be incomplete

---

### Step 6: Add Optional Sections (Complexity-Driven)

Based on complexity assessment from Step 1, include optional sections:

**For COMPLEX features, add:**
- **Detailed Scenarios** (Section 5): Gherkin scenarios for edge cases and error handling
- **Algorithm/Logic** (Section 6): Pseudocode for non-obvious implementations
- **Constraints** (Section 7): Performance, security, scalability requirements
- **Testing Approach** (Section 8): Specialized test strategy

**For MODERATE features:**
- Consider adding 1-2 optional sections if they clarify non-obvious aspects
- Default: skip unless complexity warrants

**For SIMPLE features:**
- Skip all optional sections (they won't be used anyway since we skipped this kata!)

**Verification:** Optional sections match complexity; not added "just because template has them".

> **If you can't continue:** Uncertain which sections to include → Default to fewer rather than more (can always add later)

---

### Step 7: Optimize for AI (Claude-Specific)

Apply Claude Code optimization patterns.

**Emphasis for critical requirements:**
- Use `**IMPORTANT:**` for must-read context
- Use `**MUST:**` for non-negotiable requirements
- Use `**DO NOT:**` for explicit prohibitions

**Example**:
```markdown
**IMPORTANT**: This feature will be used in hot path - performance is critical.

**MUST**: Validate all user input before processing to prevent injection attacks.

**DO NOT**: Make blocking network calls in the main thread.
```

**Rationale**: Research shows Claude (and other LLMs) respond better to explicit emphasis patterns for adherence.

**Verification:** Critical requirements have appropriate emphasis.

> **If you can't continue:** N/A (optional optimization)

---

### Step 8: Review & Refine

Self-review against quality checklist before submitting for human review.

**Checklist:**
- [ ] YAML frontmatter complete (feature_id, complexity, story_points, etc.)
- [ ] What & Why clear - can explain to teammate in 2 minutes
- [ ] Approach describes WHAT at right level (not too vague, not over-specified HOW)
- [ ] **Examples are concrete and runnable** (not placeholders)
- [ ] Acceptance criteria specific and testable (not vague)
- [ ] Optional sections justified by complexity (not just filling template)
- [ ] Emphasis used for critical requirements ("IMPORTANT", "MUST", "DO NOT")
- [ ] Spec is reviewable in <5 minutes (for human)
- [ ] Spec creation took <30 minutes (if longer, template may be too heavy - consider simplifying)

**Verification:** All checklist items pass; spec ready for human review.

> **If you can't continue:** Spec fails checklist → Iterate on weak sections before proceeding

---

## Output

- **Artefacto**: Feature Specification (Lean Format v2)
- **Ubicación**: `work/features/{feature-id}/design.md`
- **Gate**: `gates/gate-feature-design.md` (if exists - validates spec quality)
- **Next kata**: `feature/plan` (decompose spec into implementation tasks)

---

## Quality Standards

### Target Metrics

| Metric | Target | Rationale |
|--------|--------|-----------|
| **Creation time** | <30 minutes | Spec should be quick to write |
| **Review time** | <5 minutes | Human should scan quickly |
| **Spec length (simple)** | 50-80 lines | Lean, not bloated |
| **Spec length (complex)** | 100-150 lines | Proportional to complexity |
| **Examples included** | 100% | Critical for AI alignment |
| **Acceptance criteria** | 3-5 MUST items | Specific and complete |

### Evidence-Based Design

This kata based on research with 25 sources:
- **Clarity & Structure**: 6 sources (HIGH confidence) - Template enforces structure
- **Examples > Prose**: 5 sources (HIGH confidence) - Examples section required
- **YAML+Markdown**: 4 sources (HIGH confidence) - Hybrid format optimal
- **Iterative Refinement**: 4 sources (HIGH confidence) - Specs must be easy to update
- **Specs as Prompts**: 3 sources (HIGH confidence) - Optimize for Claude's context processing

Full research: `work/research/lean-feature-specs/`

---

## Common Pitfalls

### Pitfall 1: Over-Specifying "How"

**Symptom**: Spec reads like pseudocode with step-by-step implementation
**Why it's bad**: Constrains AI; removes value of AI's implementation knowledge
**Fix**: Focus on WHAT and WHY; trust AI to determine HOW

### Pitfall 2: Vague Examples

**Symptom**: Examples use `<placeholder>`, `TODO`, or are too abstract
**Why it's bad**: AI can't learn from abstract examples; generates generic code
**Fix**: Use realistic, concrete values; show actual code

### Pitfall 3: Untestable Acceptance Criteria

**Symptom**: Criteria like "works well", "good performance", "user-friendly"
**Why it's bad**: Can't verify objectively; leads to scope creep
**Fix**: Make criteria specific, observable, measurable

### Pitfall 4: Filling Optional Sections "Just Because"

**Symptom**: Simple feature has Gherkin scenarios, algorithm pseudocode, etc.
**Why it's bad**: Wastes time; adds noise; harder to review
**Fix**: Only include optional sections if complexity warrants

### Pitfall 5: Skipping Spec for Complex Features

**Symptom**: Going straight to coding for >5 SP, multi-component features
**Why it's bad**: High misalignment risk; rework likely; poor AI code quality
**Fix**: Trust the complexity assessment; create spec for moderate/complex features

---

## References

- **Template**: `.raise/templates/tech/tech-design-feature-v2.md`
- **Research**: `work/research/lean-feature-specs/` (evidence base for design decisions)
- **Related kata**: `feature/plan` (next step: task decomposition)

---

## Changelog

| Version | Date | Change |
|---------|------|--------|
| 1.0.0 | 2026-01-31 | Initial kata based on lean spec research |

---

*RaiSE Framework - Feature Design Kata v1.0*
*Evidence-based process for human-AI collaboration*
