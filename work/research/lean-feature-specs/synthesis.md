# Synthesis: Lean Feature Specification Critical Success Factors

> Triangulated findings from 25 sources (9 Very High, 13 High, 3 Medium evidence)
> Date: 2026-01-31

---

## Critical Success Factors (Ranked)

### CSF-1: Clarity and Structure (HIGHEST PRIORITY)

**Confidence**: HIGH

**Evidence** (6 independent sources):
1. [Why AI Code Needs Better Requirements](https://www.inflectra.com/Ideas/Topic/Why-Your-AI-Generated-Code-Needs-Better-Requirements.aspx) - "Clarity/structure MORE significant than traditional dev; ambiguous requirements = poor quality, security vulnerabilities"
2. [Requirements Engineering for AI Systems](https://www.sciencedirect.com/science/article/abs/pii/S0950584923000307) - "Structured requirements critical; ambiguity = poor quality code"
3. [Claude Best Practices](https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/claude-4-best-practices) - "Claude 4.x responds well to clear, explicit instructions; being specific enhances results"
4. [Spec-Driven Development 2025](https://www.softwareseni.com/spec-driven-development-in-2025-the-complete-guide-to-using-ai-to-write-production-code/) - "Formal specifications or detailed user stories wherever feasible"
5. [Best Practices AI Coding](https://graphite.com/guides/best-practices-ai-coding-assistants) - "More specific/detailed prompts = better code; be precise not vague"
6. [Addy Osmani Workflow](https://addyosmani.com/blog/ai-coding-workflow/) - "AI code generation thrives on clarity"

**Disagreement**: None found - universal consensus

**Implication**: Feature spec template MUST enforce structure; optional sections should be clearly marked; ambiguity is a critical defect

---

### CSF-2: Concrete Examples Over Prose (HIGH PRIORITY)

**Confidence**: HIGH

**Evidence** (5 independent sources):
1. [Best Practices AI Coding](https://graphite.com/guides/best-practices-ai-coding-assistants) - "Incorporate code examples, comments, docstrings; provide examples/preferences upfront"
2. [Addy Osmani Workflow](https://addyosmani.com/blog/ai-coding-workflow/) - "Providing in-line examples of output format is powerful technique"
3. [Claude Best Practices](https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/claude-4-best-practices) - Examples improve results vs prose alone
4. [Graphite AI Assistants](https://graphite.com/guides/best-practices-ai-coding-assistants) - "Guide AI to match team idioms" via examples
5. [Self-Planning Code Generation](https://dl.acm.org/doi/10.1145/3672456) - Step-by-step examples improve accuracy

**Disagreement**: None found; convergent evidence

**Implication**: Feature spec template should include code examples section (not optional); prose descriptions alone insufficient

---

### CSF-3: Hybrid Format (Markdown + YAML/Structured Metadata)

**Confidence**: HIGH

**Evidence** (4 independent sources):
1. [Markdown/YAML for Human+AI](https://blog.tech4teaching.net/markdown-json-yml-and-xml-what-is-the-best-content-format-for-both-human-and-ai/) - "Best format is Markdown + YAML metadata; Markdown for readability, YAML for structure AI needs"
2. [YAML for Documentation](https://redaction-technique.org/blog/scalable-maintainable-technical-docs-with-yaml) - "YAML human-readable, hierarchical, structured; ideal for scaling"
3. [Cursor Rules](https://extremelysunnyyk.medium.com/maximizing-your-cursor-use-advanced-prompting-cursor-rules-and-tooling-integration-496181fa919c) - YAML frontmatter + Markdown body pattern emerging
4. [CLAUDE.md Patterns](https://gist.github.com/0xdevalias/f40bc5a6f84c4c5ad862e314894b2fa6) - Community converging on YAML frontmatter for metadata

**Disagreement**: None found

**Implication**: Feature spec should use YAML frontmatter (structured metadata) + Markdown body (human-readable content)

---

### CSF-4: Iterative Refinement Support

**Confidence**: HIGH

**Evidence** (4 independent sources):
1. [Spec-Driven Development 2025](https://www.softwareseni.com/spec-driven-development-in-2025-the-complete-guide-to-using-ai-to-write-production-code/) - "Retry loops with error feedback (2-3 iterations); iteratively refine requirements, regenerate code"
2. [spec2code Framework](https://arxiv.org/html/2411.13269v1) - "Iterative backprompting improves quality"
3. [Agile + AI](https://rtslabs.com/agile-methodologies-for-ai-project-success) - "Iterative nature allows continuous refinement"
4. [CLAUDE.md Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices) - "Refine like prompts; iterate on effectiveness"

**Disagreement**: None found

**Implication**: Feature specs must be easy to update; version control friendly; support rapid iteration

---

### CSF-5: Specs as AI Prompts (Context Optimization)

**Confidence**: HIGH (Claude-specific)

**Evidence** (3 independent sources):
1. [CLAUDE.md Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices) - "CLAUDE.md files are part of Claude's prompts; refine like prompts; use 'IMPORTANT' emphasis; document commands, style guidelines"
2. [Claude Best Practices](https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/claude-4-best-practices) - "Clear, explicit instructions; specific output enhances results"
3. [Cursor Integration](https://extremelysunnyyk.medium.com/maximizing-your-cursor-use-advanced-prompting-cursor-rules-and-tooling-integration-496181fa919c) - Context files loaded automatically; initialization step

**Disagreement**: None found

**Implication**: Feature specs will be read by Claude - optimize for token efficiency, clarity, emphasis patterns ("IMPORTANT", "MUST", etc.)

---

### CSF-6: What/Why Over How (Human Role Shift)

**Confidence**: HIGH

**Evidence** (3 independent sources):
1. [SE 3.0 AI Teammates](https://arxiv.org/html/2507.15003v1) - "Human role: define goals, constraints, permissions; review changes; AI handles implementation"
2. [Coding with AI Reflection](https://www.arxiv.org/pdf/2512.23982) - "Shift from memorizing details to orchestrating collaborative process"
3. [Spec-Driven Development](https://www.softwareseni.com/spec-driven-development-in-2025-the-complete-guide-to-using-ai-to-write-production-code/) - "Specifications become source of truth guiding AI"

**Disagreement**: Some debate on full automation vs human detail involvement

**Implication**: Feature specs should focus on WHAT to build and WHY, not HOW (implementation details); constraints and acceptance criteria > step-by-step algorithms

---

### CSF-7: Formal vs Informal Specifications (Hybrid Approach)

**Confidence**: MEDIUM

**Evidence** (3 sources, mixed contexts):
1. [SpecGen](https://arxiv.org/html/2401.08807v1) - Formal specs improve verifiability (279/385 programs)
2. [spec2code Framework](https://arxiv.org/html/2411.13269v1) - "Formal ACSL + natural language; hybrid approach effective"
3. [Best Practices AI](https://www.leanware.co/insights/best-practices-ai-software-development) - "Formal specifications or detailed user stories where feasible"

**Disagreement**: Formal specs valuable but heavy; context-dependent (embedded systems vs web features)

**Implication**: For RaiSE (web/CLI context): Structured informal specs sufficient; full formal specs (ACSL, Lean) overkill for most features; reserve for critical/complex features only

---

### CSF-8: Gherkin/BDD - Selective Use

**Confidence**: MEDIUM

**Evidence** (3 sources):
1. [Acceptance Test Generation](https://arxiv.org/html/2504.07244v1) - LLMs can generate syntactically correct Gherkin; comprehensive validation
2. [Gherkin Acceptance Criteria](https://testquality.com/how-to-write-effective-gherkin-acceptance-criteria/) - "Plain language; one of best for comprehensive/precise specs"
3. [Given-When-Then Guide](https://www.parallelhq.com/blog/given-when-then-acceptance-criteria) - Clear test scenarios

**Disagreement**: Effectiveness vs verbosity trade-off

**Implication**: Gherkin useful for complex features with many edge cases; overkill for simple scaffolding/infrastructure features; make it optional, not required

---

## Minimal Viable Specification (MVS) Structure

Based on triangulated evidence:

### REQUIRED Sections (4 core)

| Section | Purpose | Evidence |
|---------|---------|----------|
| **1. What & Why** | Problem statement, objective, value | CSF-6 (what/why over how) |
| **2. Approach** | Solution approach (1-2 sentences) | CSF-1 (clarity), CSF-6 (orchestration) |
| **3. Examples** | Concrete code examples, API samples | CSF-2 (examples > prose) |
| **4. Acceptance Criteria** | Done conditions (informal or Gherkin) | CSF-1 (clarity), CSF-4 (iteration) |

### OPTIONAL Sections (progressive disclosure)

| Section | When to Include | Evidence |
|---------|----------------|----------|
| **Algorithm/Logic** | Complex algorithms, non-obvious flow | CSF-7 (context-dependent detail) |
| **Gherkin Scenarios** | Complex features, many edge cases | CSF-8 (selective use) |
| **Non-Functional Req** | Performance, security, scalability constraints | [Why AI Code Needs Better Requirements](https://www.inflectra.com/Ideas/Topic/Why-Your-AI-Generated-Code-Needs-Better-Requirements.aspx) |
| **Risks/Trade-offs** | Significant decisions with alternatives | Architectural thinking |

---

## Format Recommendation

### YAML Frontmatter (Structured Metadata)

```yaml
---
feature_id: "F1.1"
title: "Project Scaffolding"
epic: "E1 Core Foundation"
story_points: 3
complexity: simple
status: draft
version: 1.0
---
```

**Rationale**: CSF-3 (hybrid format); machine-parseable; human-scannable

### Markdown Body (Human-Readable Content)

**Rationale**: CSF-3 (hybrid format); Git-friendly; universal tooling support

### Emphasis Patterns (Claude Optimization)

Use `**IMPORTANT:**`, `**MUST:**`, `**DO NOT:**` for critical requirements

**Rationale**: CSF-5 (specs as prompts); [CLAUDE.md Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices) - Anthropic uses emphasis for adherence

---

## Human vs AI Optimization Matrix

| Element | Human Benefit | AI Benefit | Verdict |
|---------|--------------|------------|---------|
| **YAML frontmatter** | Quick scan (meta at glance) | Structured parsing | REQUIRED |
| **Prose "Why"** | Context, motivation | Low value for code gen | REQUIRED (human) |
| **Code examples** | Quick understanding | High accuracy | REQUIRED (both) |
| **Gherkin scenarios** | Test clarity | Parseable format | OPTIONAL (trade-off) |
| **Detailed "How"** | Learning value | Constrains creativity | AVOID (let AI decide) |
| **Acceptance criteria** | Review checklist | Done definition | REQUIRED (both) |

**Key Insight**: Optimize for BOTH; when conflict, examples + acceptance criteria bridge the gap

---

## Evidence-Based Template Structure (Proposed)

```markdown
---
# YAML Frontmatter (CSF-3)
feature_id: "[F#.#]"
title: "[Feature Name]"
epic: "[E# Epic Name]"
complexity: "[simple|moderate|complex]"
version: "1.0"
---

# Feature: [Title]

## 1. What & Why (CSF-6)
**Problem**: [1-2 sentences - what problem does this solve]
**Value**: [Why this matters to users/project]

## 2. Approach (CSF-1, CSF-6)
[1-2 sentences describing the solution approach - WHAT we're building, not HOW]

**Components affected**:
- [Component 1]: [change]
- [Component 2]: [change]

## 3. Examples (CSF-2 - REQUIRED)

**Example usage**:
```python
# Concrete code example showing the interface/API
```

**Example output**:
```
# What it produces/does
```

## 4. Acceptance Criteria (CSF-1, CSF-4)

**MUST**:
- [ ] [Critical requirement 1]
- [ ] [Critical requirement 2]

**SHOULD**:
- [ ] [Nice-to-have 1]

<details>
<summary><h2>5. Detailed Scenarios (Optional - CSF-8)</h2></summary>

**Scenario 1**: [Gherkin if complex feature]
```gherkin
Given [context]
When [action]
Then [outcome]
```
</details>

<details>
<summary><h2>6. Algorithm/Logic (Optional - CSF-7)</h2></summary>

[Pseudocode or detailed logic for non-obvious algorithms]
</details>

<details>
<summary><h2>7. Constraints (Optional)</h2></summary>

| Type | Constraint | Rationale |
|------|------------|-----------|
| Performance | [e.g., "<100ms response"] | [why] |
| Security | [e.g., "No secrets in code"] | [why] |
</details>
```

**Estimated length**: 50-80 lines for simple features, 100-150 for complex
**Ratio**: ~1:1 to 2:1 spec:code (lean, not heavy)

---

## Paradigm Shifts Identified

### Shift 1: Specs ARE Prompts

**Traditional**: Specs for humans, code for machines
**AI-Assisted**: Specs consumed by both humans AND AI as context
**Implication**: Optimize specs for Claude's prompt processing (emphasis, structure, examples)

### Shift 2: What/Why Over How

**Traditional**: Detailed design docs specify implementation approach
**AI-Assisted**: Humans define goals/constraints, AI determines implementation
**Implication**: Lean toward under-specification of HOW; over-specify WHAT and acceptance criteria

### Shift 3: Iterative Spec Refinement

**Traditional**: Spec → Implement → Done
**AI-Assisted**: Spec → Generate → Test → Refine Spec → Regenerate (2-3 cycles)
**Implication**: Specs must be version-controlled, easy to update, Git-friendly

### Shift 4: Examples as First-Class Citizens

**Traditional**: Examples nice-to-have, prose sufficient
**AI-Assisted**: Examples more valuable than prose for AI code generation
**Implication**: Examples section REQUIRED, not optional

---

## Gaps & Unknowns

### Gap 1: Optimal Spec Length/Detail Trade-offs

**Issue**: Limited empirical data on ideal spec length for AI accuracy vs human review time
**Evidence**: Qualitative consensus (be clear) but no quantitative studies
**Consequence**: Need to experiment with F1.1 and iterate
**Recommendation**: Start lean (50-80 lines), measure misalignment, adjust

### Gap 2: Tool-Specific Differences

**Issue**: Claude vs Copilot vs Cursor may need different formats
**Evidence**: [Tool Comparison](https://graphite.com/guides/programming-with-ai-workflows-claude-copilot-cursor) - Claude deep context, Copilot inline, Cursor RAG
**Consequence**: RaiSE targets Claude primarily - optimize for Claude's strengths (deep context, project understanding)
**Recommendation**: Design for Claude; note if pattern doesn't work for other tools

### Gap 3: Feature Complexity Calibration

**Issue**: When to use simple vs complex spec template
**Evidence**: Consensus on "it depends" but no clear heuristic
**Consequence**: Need guidelines for template selection
**Recommendation**: complexity: simple (<3 components, <5 SP) = minimal template; complex (>3 components, >5 SP, algorithms) = full template with optional sections

---

## Confidence Summary

| Factor | Sources | Evidence Level | Confidence |
|--------|---------|----------------|------------|
| Clarity & Structure | 6 | Very High + High | HIGH |
| Examples > Prose | 5 | Very High + High | HIGH |
| Hybrid Format (YAML+MD) | 4 | High + Medium | HIGH |
| Iterative Refinement | 4 | Very High + High | HIGH |
| Specs as Prompts | 3 | Very High (Claude-specific) | HIGH |
| What/Why Over How | 3 | Very High | HIGH |
| Formal Specs Value | 3 | Very High (context: embedded) | MEDIUM (RaiSE context) |
| Gherkin Selective Use | 3 | Very High + Medium | MEDIUM |

**Overall Research Quality**: HIGH (72% of factors at HIGH confidence)

---

## Next Steps

1. **Create feature/design kata** using this template structure
2. **Test with F1.1** (Project Scaffolding) - simple feature
3. **Measure**:
   - Spec creation time (target: <30 min)
   - Human review time (target: <5 min)
   - AI alignment (subjective: did code match intent?)
   - Iteration cycles (target: 1-2 before acceptance)
4. **Iterate template** based on real usage
5. **Document learnings** in ADR

---

*Synthesis completed: 2026-01-31*
*Next: Formulate recommendation with template implementation*
