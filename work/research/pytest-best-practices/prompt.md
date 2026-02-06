---
research_id: "pytest-best-practices-20260205"
primary_question: "What are the established best practices and anti-patterns for pytest-based testing in Python projects?"
decision_context: "Inform RaiSE testing standards and guardrails (>90% coverage requirement)"
depth: "standard"
created: "2026-02-05"
version: "1.0"
template: "research-prompt-v1"
---

# Research Prompt: Pytest Best Practices and Patterns

> Template for structured AI research with epistemological rigor

---

## Role Definition

You are a **Research Specialist** with expertise in **Python testing, pytest ecosystem, and software quality assurance**. Your task is to conduct epistemologically rigorous research following scientific standards for evidence evaluation.

**Your responsibilities:**
- Search systematically across academic, official, and practitioner sources
- Evaluate evidence quality using RaiSE criteria
- Triangulate findings from 3+ independent sources per major claim
- Document contrary evidence and uncertainty explicitly
- Produce reproducible, auditable research outputs

---

## Research Question

**Primary**: What are the established best practices, patterns, and anti-patterns for pytest-based testing that maximize test reliability, maintainability, and value?

**Secondary** (supporting questions):
1. What fixture design patterns (scope, factories, parametrization) yield maintainable test suites?
2. What test organization strategies (conftest.py, naming, discovery) scale well for medium-large projects?
3. What mocking strategies (unittest.mock, pytest-mock, monkeypatch) minimize brittle tests?
4. How should property-based testing with Hypothesis integrate with pytest?
5. What patterns distinguish effective integration tests from flaky ones?
6. What coverage metrics are meaningful vs vanity metrics?
7. What are the most common anti-patterns that create technical debt?

---

## Decision Context

**This research will inform**: RaiSE testing guardrails, specifically the >90% coverage requirement and recommended testing patterns

**Stakeholder**: RaiSE framework users (professional Python developers)

**Timeline**: Immediate (informing current development practices)

**Impact**: Testing patterns affect code quality, development velocity, and maintenance burden across all RaiSE projects

---

## Instructions

### Search Strategy

Execute searches across these source types:

1. **Official documentation**
   - pytest official documentation (pytest.org)
   - Hypothesis documentation (hypothesis.readthedocs.io)
   - Python unittest.mock documentation
   - Purpose: Authoritative technical specifications

2. **Production evidence**
   - GitHub repositories (filter: >1k stars, active maintenance)
   - Engineering blogs: Real Python, Test & Code podcast, Pydantic team
   - Purpose: Real-world validation, battle-tested patterns

3. **Community validation**
   - Reddit r/Python, r/learnpython
   - Python Discord testing channels
   - PyCon talks on testing
   - Purpose: Emerging consensus, practitioner wisdom

4. **Expert practitioners**
   - Brian Okken (Python Testing with pytest author)
   - David MacIver (Hypothesis author)
   - Anthony Sottile (pytest maintainer)
   - Purpose: Deep expertise, nuanced guidance

**Keywords to search**:
- "pytest best practices 2024 2025 2026"
- "pytest fixture factory pattern"
- "pytest conftest organization"
- "pytest monkeypatch vs mock"
- "hypothesis property testing pytest"
- "pytest integration testing patterns"
- "pytest coverage meaningful metrics"
- "pytest anti-patterns"

**Sources to avoid**: Python 2.x resources, pytest <6.0 patterns, unittest-only resources

---

### Evidence Evaluation

For each source, assess and record:

- **Type**: Primary/Secondary/Tertiary
- **Evidence Level**: Very High/High/Medium/Low (per RaiSE criteria)
- **Key Finding**: One-line takeaway
- **Relevance**: How it answers our question
- **Date**: Publication or last update date

---

### Triangulation Requirements

**Target source count**: 15-30 sources (standard depth)

**For major claims**: Require 3+ independent confirmations

**Confidence calibration**:
- HIGH: 3+ Very High or High sources, convergent evidence
- MEDIUM: 2-3 sources, some convergence
- LOW: <2 sources or significant disagreement

---

## Output Format

Produce evidence catalog and synthesized findings per the research skill template.

---

## Quality Criteria

- [ ] Research question is specific and falsifiable
- [ ] 15+ sources consulted
- [ ] Major claims triangulated (3+ sources)
- [ ] Confidence levels explicitly stated
- [ ] Contrary evidence acknowledged
- [ ] Actionable recommendations produced

---

## Constraints

**Time**: 4-6 hours equivalent effort

**Focus priorities**: Fixture design and anti-patterns first

**Out of scope**: Django-specific testing, async testing patterns (unless directly relevant)

---

## Reproducibility Metadata

- Tool/model used: WebSearch + manual synthesis
- Search date: 2026-02-05
- Prompt version: 1.0
- Researcher: Rai (Claude Opus 4.5)
