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

**Value**: [1-2 sentences explaining why this matters to users/project/stakeholders]

---

## 2. Approach

**How we'll solve it** (high-level):

[1-2 sentences describing the solution approach - WHAT we're building, not detailed HOW. Focus on goals and constraints, not implementation steps.]

**Components affected**:
- **[Component/Module 1]**: [What changes - create/modify/delete]
- **[Component/Module 2]**: [What changes]

---

## 3. Interface / Examples

> **IMPORTANT**: Provide concrete examples - these are critical for AI code generation accuracy

### API / CLI Usage

```[language]
# Example of how this feature is used
# Show actual code that could be run

[Concrete code example showing the interface]
```

### Expected Output

```[language or text]
# What the feature produces or how it behaves
# Include realistic data/responses

[Example output or behavior]
```

### Data Structures (if applicable)

```[language]
# Key data models, schemas, or type definitions
# Example: Pydantic models, TypeScript interfaces, database schemas

[Example structure]
```

---

## 4. Acceptance Criteria

> **MUST** = Required for feature completion
> **SHOULD** = Nice-to-have, defer if time-constrained
> **MUST NOT** = Explicit anti-requirements

### Must Have

- [ ] [Critical requirement 1 - specific and testable]
- [ ] [Critical requirement 2 - specific and testable]
- [ ] [Critical requirement 3 - specific and testable]

### Should Have

- [ ] [Nice-to-have requirement 1]
- [ ] [Nice-to-have requirement 2]

### Must NOT

- [ ] [Explicit anti-requirement - what to avoid or prevent]

---

<details>
<summary><h2>5. Detailed Scenarios (Optional - Use for Complex Features)</h2></summary>

> **When to include**: Complex features with multiple edge cases, state transitions, or error conditions

### Scenario 1: [Happy Path / Primary Use Case]

```gherkin
Given [initial context or preconditions]
When [user action or trigger event]
Then [expected outcome]
And [additional verification or side effects]
```

### Scenario 2: [Edge Case / Error Handling]

```gherkin
Given [error condition context or invalid state]
When [user action or trigger]
Then [expected error handling or graceful degradation]
And [what should NOT happen]
```

### Scenario 3: [Another Important Case]

```gherkin
Given [context]
When [action]
Then [outcome]
```

</details>

---

<details>
<summary><h2>6. Algorithm / Logic (Optional - Use for Non-Obvious Implementation)</h2></summary>

> **When to include**: Non-trivial algorithms, complex state machines, specialized business logic, or performance-critical operations

```python
# Pseudocode or detailed algorithm description
# Focus on WHAT steps happen, not necessarily exact syntax

def complex_operation(input_data):
    """
    High-level algorithm outline
    """
    # Step 1: [What happens and why]

    # Step 2: [What happens and why]

    # Step 3: [What happens and why]

    # Return: [What's produced]
    return result
```

**Rationale**: [Why this approach was chosen]

**Alternatives considered**:
- [Alternative 1]: [Why not chosen]
- [Alternative 2]: [Why not chosen]

**Complexity**: [Time/space complexity if relevant - e.g., O(n log n)]

</details>

---

<details>
<summary><h2>7. Constraints & Non-Functional Requirements (Optional)</h2></summary>

> **When to include**: Performance, security, scalability, or compatibility requirements that constrain implementation

| Type | Constraint | Rationale |
|------|------------|-----------|
| **Performance** | [e.g., "<100ms response time", "Handle 10k requests/sec"] | [Why this threshold matters] |
| **Security** | [e.g., "No secrets in code", "Hash passwords with bcrypt"] | [Risk being mitigated] |
| **Scalability** | [e.g., "Support up to 10k concurrent users"] | [Expected growth or limits] |
| **Compatibility** | [e.g., "Python 3.12+", "PostgreSQL 14+"] | [Platform or dependency requirements] |
| **Accessibility** | [e.g., "WCAG 2.1 AA compliance"] | [User needs or regulatory requirements] |
| **Reliability** | [e.g., "99.9% uptime", "Graceful degradation"] | [Service level expectations] |

</details>

---

<details>
<summary><h2>8. Testing Approach (Optional)</h2></summary>

> **When to include**: Non-obvious testing strategy, specialized test requirements, or critical quality assurance needs

| Test Type | What to Cover | Tooling / Framework |
|-----------|---------------|---------------------|
| **Unit** | [What units/functions to test; edge cases to verify] | pytest, unittest |
| **Integration** | [What integrations to verify; external dependencies] | pytest + fixtures, testcontainers |
| **E2E** | [User workflows to validate end-to-end] | Playwright, Selenium |
| **Performance** | [Load testing, benchmarks] | pytest-benchmark, locust |
| **Manual** | [What requires human verification; exploratory testing] | N/A |

**Test Data**:
- [Where to get test data or fixtures]
- [Any data generation strategy]

**Coverage Target**: [e.g., ">90% for core logic"]

</details>

---

## References

**Related ADRs**:
- [ADR-XXX: Decision Title](../../../dev/decisions/adr-xxx.md)

**Related Features**:
- F#.#: [Feature Title]
- F#.#: [Feature Title]

**External Docs**:
- [Document Title](URL) - [Why relevant]

**Dependencies**:
- [Upstream feature that must complete first]
- [Library or service this depends on]

---

**Template Version**: 2.0 (Lean Feature Spec)
**Created**: [YYYY-MM-DD]
**Last Updated**: [YYYY-MM-DD]
**Based on**: Research `work/research/lean-feature-specs/` (2026-01-31)

---

## Template Usage Notes

### When to Use This Template

- **Complex features**: >3 components, >5 SP, non-trivial logic
- **Architectural decisions**: Multiple implementation approaches
- **AI code generation**: Significant code to be AI-generated

### When to Skip

- **Simple features**: <3 components, <5 SP, obvious implementation → Go directly to `feature/plan`
- **Bug fixes**: Use issue tracker
- **Infrastructure/scaffolding**: If implementation is self-evident

### Section Priority

**Always include (4 core sections)**:
1. What & Why
2. Approach
3. Examples (CRITICAL for AI alignment)
4. Acceptance Criteria

**Include as needed (4 optional sections)**:
5. Detailed Scenarios (complex features with edge cases)
6. Algorithm/Logic (non-obvious implementations)
7. Constraints (performance/security requirements)
8. Testing (specialized test needs)

### Tips for Effective Specs

**For AI alignment**:
- ✓ Concrete examples over prose descriptions
- ✓ Specific acceptance criteria (testable, observable)
- ✓ Use emphasis: **IMPORTANT**, **MUST**, **DO NOT**
- ✓ Focus on WHAT and WHY, not detailed HOW

**For human reviewability**:
- ✓ Keep core sections concise (1-2 sentences for What/Why)
- ✓ Use collapsible `<details>` for optional sections
- ✓ Target: Reviewable in <5 minutes
- ✓ YAML frontmatter enables quick scanning

**For iteration**:
- ✓ Version control this file alongside code
- ✓ Update spec based on implementation learnings
- ✓ 2-3 iteration cycles normal: spec → code → refine spec → regenerate

### Evidence Base

This template design based on research with 25 sources:
- 9 Very High evidence (academic papers, vendor docs)
- 13 High evidence (engineering blogs, production cases)
- 3 Medium evidence (community validation)

**Key findings**:
- Clarity & structure critical (6 sources)
- Examples outperform prose for AI (5 sources)
- YAML+Markdown optimal format (4 sources)
- Iterative refinement essential (4 sources)

Full research: `work/research/lean-feature-specs/`
