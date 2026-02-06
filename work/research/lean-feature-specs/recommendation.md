# Recommendation: Lean Feature Specification Template for RaiSE

> Evidence-based design for human understanding + AI alignment
> Date: 2026-01-31
> Confidence: HIGH (based on 25 sources, 72% HIGH-confidence factors)

---

## Executive Summary

**Decision**: Implement a lean story spec template with YAML frontmatter + Markdown body, emphasizing concrete examples and acceptance criteria over prose descriptions

**Confidence**: HIGH

**Rationale**: Convergent evidence from 9 Very High + 13 High sources demonstrates:
1. Clarity/structure critical for AI code quality (6 sources)
2. Examples outperform prose for AI alignment (5 sources)
3. Hybrid YAML+Markdown optimal for human+AI (4 sources)
4. Iterative refinement essential (4 sources)
5. Specs consumed as AI prompts - optimize accordingly (3 sources, Claude-specific)

**Trade-offs**:
- **Accept**: Upfront effort to write examples (~10 min)
- **Accept**: Learning curve for YAML frontmatter usage
- **Gain**: Better AI alignment, faster human review, iterative refinement support

**Risks**:
- Template too heavy for simple features (mitigated by optional sections)
- Examples become stale if not updated (mitigated by version control + review gates)
- Over-specification of "how" constrains AI (mitigated by "what/why" focus)

---

## Recommendation 1: Feature Spec Template Structure

### Template Design

Create `.raise/templates/tech/tech-design-story-v2.md`:

```markdown
---
story_id: "[F#.#]"
title: "[Feature Name]"
epic_ref: "[E# Epic Name]"
story_points: [number]
complexity: "[simple|moderate|complex]"
status: "[draft|approved|implemented]"
version: "1.0"
created: "[YYYY-MM-DD]"
updated: "[YYYY-MM-DD]"
template: "lean-feature-spec-v2"
---

# Feature: [Title]

> **Epic**: [E#] - [Epic Name]
> **Complexity**: [simple|moderate|complex] | **SP**: [number]

---

## 1. What & Why

**Problem**: [1-2 sentences describing what problem this solves or what gap it fills]

**Value**: [1-2 sentences explaining why this matters to users/project]

---

## 2. Approach

**How we'll solve it** (high-level):
[1-2 sentences describing the solution approach - WHAT we're building, not detailed HOW]

**Components affected**:
- **[Component/Module 1]**: [What changes - create/modify/delete]
- **[Component/Module 2]**: [What changes]

---

## 3. Interface / Examples

> **IMPORTANT**: Provide concrete examples - these drive AI code generation accuracy

### API / CLI Usage

```[language]
# Example of how this feature is used
[Concrete code example showing the interface]
```

### Expected Output

```[language or text]
# What the feature produces or how it behaves
[Example output or behavior]
```

### Data Structures (if applicable)

```[language]
# Key data models or schemas
[Example structure - e.g., Pydantic model, TypeScript interface, database schema]
```

---

## 4. Acceptance Criteria

> **MUST** = Required for feature completion
> **SHOULD** = Nice-to-have, defer if time-constrained

### Must Have

- [ ] [Critical requirement 1 - specific and testable]
- [ ] [Critical requirement 2]
- [ ] [Critical requirement 3]

### Should Have

- [ ] [Nice-to-have 1]
- [ ] [Nice-to-have 2]

### Must NOT

- [ ] [Explicit anti-requirement - what to avoid]

---

<details>
<summary><h2>5. Detailed Scenarios (Optional - Use for Complex Features)</h2></summary>

> **When to include**: Complex features with multiple edge cases or state transitions

### Scenario 1: [Happy Path]

```gherkin
Given [initial context]
When [user action]
Then [expected outcome]
And [additional verification]
```

### Scenario 2: [Edge Case / Error Handling]

```gherkin
Given [error condition context]
When [user action]
Then [expected error handling]
```

</details>

---

<details>
<summary><h2>6. Algorithm / Logic (Optional - Use for Non-Obvious Implementation)</h2></summary>

> **When to include**: Non-trivial algorithms, complex state machines, or specialized logic

```python
# Pseudocode or detailed algorithm description
def complex_operation(input_data):
    # Step 1: [What happens]
    # Step 2: [What happens]
    # Return: [What's produced]
    pass
```

**Rationale**: [Why this approach]
**Alternatives considered**: [Other approaches and why not chosen]

</details>

---

<details>
<summary><h2>7. Constraints & Non-Functional Requirements (Optional)</h2></summary>

> **When to include**: Performance, security, or scalability requirements

| Type | Constraint | Rationale |
|------|------------|-----------|
| **Performance** | [e.g., "<100ms response time"] | [Why this matters] |
| **Security** | [e.g., "No secrets in code"] | [Risk mitigation] |
| **Scalability** | [e.g., "Handle 10k items"] | [Expected growth] |
| **Compatibility** | [e.g., "Python 3.12+"] | [Platform requirements] |

</details>

---

<details>
<summary><h2>8. Testing Approach (Optional)</h2></summary>

> **When to include**: Non-obvious testing strategy or specialized test requirements

| Test Type | What to Cover | Tooling |
|-----------|---------------|---------|
| **Unit** | [What units to test] | pytest |
| **Integration** | [What integrations to verify] | [Tool/framework] |
| **Manual** | [What to verify manually] | N/A |

</details>

---

## References

- **Related ADRs**: [ADR-XXX](link)
- **Related Features**: F#.#, F#.#
- **External Docs**: [Title](URL) if applicable

---

**Template Version**: 2.0 (Lean Feature Spec)
**Last Updated**: [YYYY-MM-DD]
**Based on**: Research `work/research/lean-feature-specs/`
```

**Confidence**: HIGH
**Implementation**: Replace existing `tech-design-story.md` or create v2 variant

---

## Recommendation 2: Feature/Design Kata Creation

### Create New Kata

Create `.raise/katas/story/design.md`:

```yaml
---
id: story-design
titulo: "Design: Feature Specification"
work_cycle: feature
frequency: per-story-as-needed
fase_metodologia: 4

prerequisites:
  - project/backlog
template: templates/tech/tech-design-story-v2.md
gate: gates/gate-story-design.md
next_kata: feature/plan

adaptable: true
shuhari:
  shu: "Follow template completely; include all examples"
  ha: "Skip optional sections for simple features"
  ri: "Create custom spec patterns for specialized domains"

version: 1.0.0
---

# Design: Feature Specification

## Purpose

Create a lean story specification that optimizes for both human understanding (quick review) and AI alignment (accurate code generation), based on evidence from 25+ sources.

## Context

**When to use:**
- Before planning complex features (>3 components, >5 SP, non-trivial logic)
- When feature requires architectural decisions
- When multiple implementation approaches exist
- When AI will generate significant code from spec

**When to skip:**
- Simple features (<3 components, <5 SP, obvious implementation)
- Infrastructure/scaffolding work
- Bug fixes (use issue tracker)

**Inputs required:**
- Feature from backlog (ID, description, acceptance criteria)
- Technical Design (project-level) for architectural context

**Output:**
- Feature spec in `work/stories/{feature-id}/design.md`

## Steps

### Step 1: Assess Complexity

Determine if feature needs full spec:

| Criterion | Simple | Moderate | Complex |
|-----------|--------|----------|---------|
| Components touched | 1-2 | 3-4 | 5+ |
| Story points | <5 | 5-8 | >8 |
| Integrations | 0-1 | 2-3 | 4+ |
| Algorithm complexity | Trivial | Standard | Novel |

**Decision**:
- Simple → Skip design, go directly to feature/plan
- Moderate/Complex → Create story spec using template

**Verification:** Complexity assessed and documented.

> **If you can't continue:** Unclear complexity → Default to creating spec (safe choice)

### Step 2: Frame What & Why

Define the feature's purpose and value:
- **Problem**: What gap does this fill? (1-2 sentences)
- **Value**: Why does this matter? (1-2 sentences)

**Verification:** Problem and value clearly stated.

> **If you can't continue:** Unclear value proposition → Escalate to backlog refinement

### Step 3: Describe Approach (High-Level)

Describe WHAT you're building, not detailed HOW:
- Solution approach (1-2 sentences)
- Components affected (list with change type)

**IMPORTANT**: Focus on what/why, not implementation details. AI handles "how".

**Verification:** Approach is clear but not over-specified.

> **If you can't continue:** Too many unknowns → Spike needed; create research task

### Step 4: Create Examples (REQUIRED)

**This is the most critical section for AI alignment.**

Provide concrete examples:
- **API/CLI usage**: How feature is invoked
- **Expected output**: What it produces
- **Data structures**: Key models/schemas (if applicable)

**Quality criteria**:
- Examples are runnable (or close to it)
- Cover happy path + 1-2 common cases
- Show actual code, not placeholders

**Verification:** Examples provided; can be copied and used.

> **If you can't continue:** Can't envision examples → Approach not concrete enough; return to Step 3

### Step 5: Define Acceptance Criteria

Specify "done" conditions:
- **MUST**: Required for completion (3-5 items)
- **SHOULD**: Nice-to-have (1-3 items)
- **MUST NOT**: Explicit anti-requirements

**Criteria quality**:
- Specific and testable
- Observable outcomes (not internal states)
- Traceable to user value

**Verification:** Acceptance criteria are clear and complete.

> **If you can't continue:** Unclear what "done" means → Refine problem statement in Step 2

### Step 6: Add Optional Sections (If Needed)

Based on complexity:

**Complex features** → Add:
- Detailed scenarios (Gherkin)
- Algorithm/logic (pseudocode)
- Constraints (non-functional requirements)
- Testing approach

**Simple/Moderate features** → Skip optional sections

**Verification:** Optional sections match complexity.

> **If you can't continue:** N/A

### Step 7: Review & Refine

Self-review against checklist:
- [ ] YAML frontmatter complete
- [ ] What & Why clear (can explain to teammate in 2 min)
- [ ] Examples concrete and runnable
- [ ] Acceptance criteria specific and testable
- [ ] Emphasis used for critical requirements ("IMPORTANT", "MUST")
- [ ] Optional sections justified by complexity

**Verification:** Spec ready for human review.

> **If you can't continue:** Spec fails checklist → Iterate on weak sections

## Output

- **Artefact**: Feature Specification
- **Ubicación**: `work/stories/{feature-id}/design.md`
- **Gate**: `gates/gate-story-design.md` (if exists)
- **Next kata**: `feature/plan` (decompose into tasks)

## Quality Checklist

- [ ] Complexity assessed (simple/moderate/complex)
- [ ] Problem and value clearly stated
- [ ] Approach described at appropriate level (what, not how)
- [ ] **Concrete examples provided** (critical for AI)
- [ ] Acceptance criteria specific and testable
- [ ] Optional sections match complexity
- [ ] Spec reviewable in <5 minutes
- [ ] Spec creation took <30 minutes (if longer, template may be too heavy)

## References

- Template: `.raise/templates/tech/tech-design-story-v2.md`
- Research: `work/research/lean-feature-specs/`
- Related kata: `feature/plan`
```

**Confidence**: HIGH
**Implementation**: Create new kata file

---

## Recommendation 3: Update Existing Template

### Migrate Existing tech-design-story.md

Current template (`.raise/templates/tech/tech-design-story.md`) → Create v2 variant

**Migration strategy**:
1. Create new file: `tech-design-story-v2.md` (don't break existing)
2. Update template README to list both versions
3. Reference v2 from new feature/design kata
4. Mark v1 as "legacy" after validation period

**Confidence**: HIGH
**Rationale**: Preserve backward compatibility; iterate based on usage

---

## Recommendation 4: Validation Plan

### Test with F1.1 (Project Scaffolding)

**Apply template to F1.1**:
1. Create `work/stories/f1.1-project-scaffolding/design.md` using v2 template
2. Measure:
   - Creation time (target: <30 min)
   - Human review time (target: <5 min to understand)
   - AI alignment (subjective: did generated code match intent?)
   - Iteration cycles needed (target: 1-2)
3. Document learnings

**Success criteria**:
- Spec created in <30 min ✓
- Emilio can review/approve in <5 min ✓
- Claude generates aligned code (minimal corrections) ✓
- Total cycle time (spec → code → review) faster than without spec ✓

**Confidence**: MEDIUM (need empirical validation)

---

## Recommendation 5: ADR Documentation

### Create ADR-XXX: Lean Feature Spec Format

**Decision**: Adopt YAML+Markdown lean story spec template with examples-first approach

**Alternatives considered**:
1. **Full Gherkin for all stories** - Rejected: Too verbose for simple features
2. **Prose-only specs** - Rejected: Poor AI alignment (evidence from 5 sources)
3. **Formal specs (ACSL, Lean)** - Rejected: Overkill for web/CLI context
4. **No specs, direct to code** - Rejected: High misalignment risk (evidence from 6 sources)

**Status**: Proposed (pending F1.1 validation)

**Confidence**: HIGH (evidence-based)

---

## Implementation Roadmap

### Phase 1: Template Creation (Immediate)

- [ ] Create `.raise/templates/tech/tech-design-story-v2.md`
- [ ] Create `.raise/katas/story/design.md`
- [ ] Update `.raise/templates/README.md` to reference v2 template

**Time estimate**: 1 hour

### Phase 2: Validation (Next Session)

- [ ] Apply template to F1.1 (Project Scaffolding)
- [ ] Measure against success criteria
- [ ] Document learnings
- [ ] Iterate template based on findings

**Time estimate**: 2-3 hours (includes F1.1 spec creation + iteration)

### Phase 3: Rollout (After Validation)

- [ ] Create ADR documenting decision
- [ ] Update project governance to reference new process
- [ ] Mark v1 template as legacy
- [ ] Use v2 for all future features (F1.2+)

**Time estimate**: 1 hour

---

## Trade-offs Analysis

### Accept: Examples Take Time to Write

**Cost**: ~10 minutes per story to write good examples
**Benefit**: 5+ sources show examples improve AI accuracy significantly
**RaiSE Alignment**: "Specs are source of truth; code is expression"

**Verdict**: Accept. Investment pays off in better AI alignment and faster review.

### Accept: YAML Frontmatter Learning Curve

**Cost**: New users need to learn YAML syntax
**Benefit**: Structured metadata enables tooling, parsing, automation
**RaiSE Alignment**: "Governance as Code"

**Verdict**: Accept. One-time learning cost; provide examples in template.

### Accept: Optional Sections May Be Skipped

**Cost**: Risk of under-specification for complex features
**Benefit**: Keeps simple features lean
**RaiSE Alignment**: "Simplicidad over Completitud"

**Verdict**: Accept. Feature/design kata provides guidance on when to include optionals.

---

## Risks & Mitigations

### Risk 1: Template Still Too Heavy for Simple Features

**Likelihood**: Medium
**Impact**: Low (slows down simple features)

**Mitigation**:
- Clear guidance in kata: skip design for simple features (<5 SP, <3 components)
- Measure creation time; iterate if consistently >30 min
- Provide "lite" version for very simple features if needed

### Risk 2: Examples Become Stale as Code Evolves

**Likelihood**: Medium
**Impact**: Medium (misleading specs)

**Mitigation**:
- Include examples in spec review gate
- Version control specs alongside code
- Periodic spec audit during refactoring

### Risk 3: Over-Specification of "How" Constrains AI

**Likelihood**: Low (if kata followed)
**Impact**: Medium (suboptimal implementations)

**Mitigation**:
- Kata explicitly warns against over-specification
- Focus on what/why, not how
- Review gate checks for this

### Risk 4: Template Doesn't Work for Other AI Tools

**Likelihood**: Low (RaiSE targets Claude primarily)
**Impact**: Low (if users want Copilot/Cursor support)

**Mitigation**:
- Document as "Claude-optimized"
- Note in template if pattern doesn't translate to other tools
- Community can adapt for other tools if needed

---

## Success Metrics

### Leading Indicators (Process)

- Feature specs created using v2 template (target: 100% for moderate/complex features)
- Spec creation time (target: <30 min)
- Optional sections usage matches complexity (target: >80% appropriate use)

### Lagging Indicators (Outcome)

- Human review time (target: <5 min to understand spec)
- AI alignment (subjective: code matches intent on first pass) (target: >80%)
- Iteration cycles (target: 1-2 before acceptance)
- Developer satisfaction (qualitative feedback)

### Quality Indicators

- Examples provided in specs (target: 100%)
- Acceptance criteria specific and testable (target: 100%)
- Specs reviewed in <5 min (target: >80%)

---

## Next Steps

1. **Immediate**: Create v2 template and feature/design kata
2. **This session**: Apply template to F1.1 (validate with real feature)
3. **Next session**: Iterate based on F1.1 learnings
4. **Before F1.2**: Finalize template and create ADR

---

## Governance Linkage

### ADR Status

**Recommendation**: Create ADR-XXX "Lean Feature Spec Format for Human-AI Collaboration"
- **Decision**: Adopt v2 template
- **Alternatives**: Documented above
- **Rationale**: Evidence-based (25 sources)
- **Status**: Proposed (pending F1.1 validation)

### Backlog Impact

- **No change to F1.1-F7.4 story scope**
- **Adds**: Feature spec creation time (~30 min per moderate/complex feature)
- **Reduces**: Misalignment rework time (expected net positive)
- **Enables**: Faster review, better AI code generation

### Parking Lot Resolution

This research resolves: "What makes a good lean story spec for human-AI collaboration?"
**Status**: Resolved with actionable recommendation

---

## References

**Full evidence catalog**: `work/research/lean-feature-specs/sources/evidence-catalog.md`
**Synthesis document**: `work/research/lean-feature-specs/synthesis.md`

**Key sources**:
- [Why AI Code Needs Better Requirements](https://www.inflectra.com/Ideas/Topic/Why-Your-AI-Generated-Code-Needs-Better-Requirements.aspx) - Clarity critical
- [CLAUDE.md Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices) - Specs as prompts
- [Spec-Driven Development 2025](https://www.softwareseni.com/spec-driven-development-in-2025-the-complete-guide-to-using-ai-to-write-production-code/) - Iterative refinement
- [Markdown/YAML for Human+AI](https://blog.tech4teaching.net/markdown-json-yml-and-xml-what-is-the-best-content-format-for-both-human-and-ai/) - Hybrid format
- [SE 3.0 AI Teammates](https://arxiv.org/html/2507.15003v1) - What/why over how

---

**Recommendation Status**: READY FOR IMPLEMENTATION
**Confidence**: HIGH
**Next Action**: Create v2 template + feature/design kata, then validate with F1.1

---

*Research completed: 2026-01-31*
*Total sources: 25 (9 Very High, 13 High, 3 Medium)*
*Research time: ~3 hours (prompt creation + searches + synthesis)*
*Dogfooding: ✓ Used new research prompt template successfully*
