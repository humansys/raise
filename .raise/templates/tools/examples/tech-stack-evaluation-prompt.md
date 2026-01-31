---
research_id: "python-cli-frameworks-20260131"
primary_question: "Which Python CLI framework best balances developer experience, type safety, and maintainability for raise-cli?"
decision_context: "ADR: CLI Framework Selection for raise-cli v2.0"
depth: "standard"
created: "2026-01-31"
version: "1.0"
template: "research-prompt-v1"
---

# Research Prompt: Python CLI Framework Evaluation

> Example research prompt demonstrating template usage
> For RaiSE raise-cli v2.0 framework selection

---

## Role Definition

You are a **Research Specialist** with expertise in **Python CLI framework architecture and developer tooling**. Your task is to conduct epistemologically rigorous research following scientific standards for evidence evaluation.

**Your responsibilities:**
- Search systematically across academic, official, and practitioner sources
- Evaluate evidence quality using RaiSE criteria
- Triangulate findings from 3+ independent sources per major claim
- Document contrary evidence and uncertainty explicitly
- Produce reproducible, auditable research outputs

---

## Research Question

**Primary**: Which Python CLI framework (Click, Typer, argparse, others) best balances developer experience, type safety, and long-term maintainability for a governance automation tool like raise-cli?

**Secondary** (supporting questions):
1. What are the type safety capabilities of each framework?
2. How does each framework integrate with Pydantic models?
3. What's the maintenance status and community health of each option?
4. What production use cases exist at scale for each framework?
5. How do testing and documentation experiences compare?

---

## Decision Context

**This research will inform**: ADR-XXX "CLI Framework Selection for raise-cli v2.0"

**Stakeholder**: raise-cli development team, future contributors

**Timeline**: Decision needed before F1.2 (CLI Skeleton) implementation

**Impact**: Wrong choice = technical debt, poor DX, difficult refactoring. This is a foundational decision affecting all CLI features (22+ story points in backlog).

---

## Instructions

### Search Strategy

Execute searches across these source types:

1. **Academic sources**
   - Google Scholar: `"Python CLI framework" comparison evaluation`
   - arXiv: `command line interface design python`
   - Purpose: Interface design principles, usability research

2. **Official documentation**
   - Click official docs (https://click.palletsprojects.com/)
   - Typer official docs (https://typer.tiangolo.com/)
   - Python argparse docs (https://docs.python.org/3/library/argparse.html)
   - Purpose: Feature capabilities, design philosophy

3. **Production evidence**
   - GitHub: Search for projects using each framework (filter: >1k stars, Python)
   - Engineering blogs: "choosing CLI framework", "Click vs Typer", "production CLI tools"
   - Examples: GitLab, AWS CLI, Databricks CLI, uv, ruff
   - Purpose: Real-world validation, scale testing

4. **Community validation**
   - Reddit r/Python: CLI framework discussions
   - Hacker News: CLI tool announcements and discussions
   - Python Discord/Slack communities
   - Purpose: Developer experience feedback, pain points

**Keywords to search**:
- "Python CLI framework comparison 2024 2025"
- "Typer vs Click production"
- "Python CLI type safety Pydantic"
- "argparse alternatives modern Python"
- "CLI framework maintainability"
- "Python click decorators vs typer type hints"

**Sources to avoid**: Pre-2022 comparisons (outdated given Typer's evolution and Python 3.10+ features)

---

### Evidence Evaluation

For each source you find, assess and record:

- **Type**:
  - Primary (framework docs, GitHub repos, original benchmarks)
  - Secondary (engineering blogs, tutorials, comparative guides)
  - Tertiary (Reddit threads, aggregated lists)

- **Evidence Level** (use RaiSE engineering criteria):
  - **Very High**: Official docs, production use at FAANG/established companies, >10k star projects
  - **High**: Well-maintained projects >1k stars, expert engineering blogs, detailed comparisons
  - **Medium**: Community discussions with engagement, emerging tools >100 stars
  - **Low**: Personal blogs, small projects, undocumented claims

- **Key Finding**: One-line takeaway from this source

- **Relevance**: How does this inform framework choice for raise-cli?

- **Date**: Publication or last update date (framework evolution is fast)

---

### Triangulation Requirements

**Minimum source counts**: Standard depth = 15-30 sources

**For major claims** (e.g., "Typer has better DX than Click"):
- Require **3+ independent confirmations**
- At least 1 production use case validation
- If framework docs claim X, find practitioner validation

**Handling disagreement**:
- Click vs Typer debates will exist - document both perspectives
- Note whether disagreements are contextual (right tool for different jobs)
- Temporal: Has consensus shifted over time?

**Confidence calibration**:
- HIGH: 3+ sources, production validation, official docs align with practice
- MEDIUM: 2-3 sources, limited production evidence, emerging consensus
- LOW: Single source, no production validation, or contradictory evidence

---

## Output Format

Produce the following artifacts in `work/research/python-cli-frameworks/`:

### 1. Evidence Catalog (`sources/evidence-catalog.md`)

For each source:

```markdown
**Source**: [Framework Official Docs / Blog Title + Link]
- **Type**: Primary/Secondary/Tertiary
- **Evidence Level**: Very High/High/Medium/Low
- **Date**: [YYYY-MM-DD]
- **Key Finding**: [e.g., "Typer uses type hints, no decorators"]
- **Relevance**: [e.g., "Aligns with RaiSE type safety guardrail"]
```

Include summary statistics:
- Total sources by framework: Click (X), Typer (Y), argparse (Z), other (W)
- Evidence distribution
- Temporal coverage

---

### 2. Synthesis Document (`synthesis.md`)

#### Major Claims (Triangulated)

Example structure:

```markdown
**Claim 1**: Typer provides superior type safety through native Python type hints

**Confidence**: HIGH

**Evidence**:
1. [Typer Official Docs](URL) - Uses Python 3.6+ type hints, auto-completion
2. [FastAPI Author Blog](URL) - Same author, philosophy of type-driven DX
3. [Production Case: X Project](URL) - Reports improved refactoring safety

**Disagreement**: None found - consensus on type hint benefits

**Implication**: Strong alignment with RaiSE guardrail requiring type annotations
```

#### Evaluation Matrix

| Criterion | Click | Typer | argparse | Weight | Notes |
|-----------|-------|-------|----------|--------|-------|
| Type Safety | Medium | High | Low | HIGH | Critical for RaiSE |
| Pydantic Integration | Manual | Native | Manual | HIGH | Core dependency |
| Maintenance Status | ... | ... | ... | MEDIUM | ... |
| Production Adoption | ... | ... | ... | MEDIUM | ... |
| Testing DX | ... | ... | ... | LOW | ... |

---

### 3. Recommendation (`recommendation.md`)

```markdown
## Recommendation

**Decision**: Adopt Typer for raise-cli v2.0 CLI framework

**Confidence**: HIGH

**Rationale**:
- Native type hints align with RaiSE type safety guardrail (3+ sources confirm)
- Excellent Pydantic integration (framework author validation + production cases)
- Active maintenance, growing adoption (GitHub data, community feedback)
- Production validation at [examples from research]

**Trade-offs**:
- Accept: Smaller ecosystem than Click (fewer plugins)
- Accept: Newer framework (less mature, <5 years old)
- Gain: Better DX, native type safety, modern Python idioms

**Risks**:
- Framework abandonment risk (mitigation: FastAPI author maintains, strong community)
- Breaking changes in pre-1.0 releases (mitigation: Pin version, monitor releases)

**Alternatives Considered**:
- Click: More mature, but decorator-based (conflicts with type hint preference)
- argparse: Stdlib, but verbose, poor DX for complex CLIs
```

---

## Quality Criteria

**Question & Scope**
- [x] Research question is specific and falsifiable
- [x] Decision context clearly stated (ADR for raise-cli)
- [x] Scope boundaries defined (Python CLI frameworks, exclude TUI frameworks like Textual)

**Evidence Gathering**
- [ ] Minimum 15-30 sources gathered
- [ ] Mix of official docs, production cases, community feedback
- [ ] Sources dated (exclude pre-2022 unless historical context)

**Rigor & Validation**
- [ ] Major claims triangulated (3+ sources)
- [ ] Confidence levels stated
- [ ] Evaluation matrix with weighted criteria
- [ ] Production use cases validated

**Actionability**
- [ ] Clear recommendation (which framework)
- [ ] Trade-offs explicit
- [ ] Migration/adoption path considered
- [ ] Links to ADR

**Reproducibility**
- [ ] All sources cited
- [ ] Search keywords documented
- [ ] Tool used recorded
- [ ] Date recorded

---

## Constraints

**Time**: 6 hours max (standard depth)

**Focus priorities**:
1. Type safety capabilities (highest priority)
2. Pydantic integration (highest priority)
3. Production validation (medium priority)
4. Ecosystem maturity (lower priority)

**Out of scope**:
- TUI frameworks (Textual, Rich direct) - different use case
- Non-Python CLI tools (Cobra/Go, Thor/Ruby) - language constraint
- Detailed performance benchmarks - not critical for raise-cli scale

---

## Reproducibility Metadata

```markdown
**Research Metadata**:
- Tool/model used: [To be filled by researcher]
- Search date: 2026-01-31
- Prompt version: 1.0
- Researcher: [Agent/human name]
- Total time: [Hours]
```

---

## Tool Selection Guide

For this research: **Standard depth** → Recommend `llm -m perplexity` if available, else WebSearch

**Rationale**: Need current information (2024-2025), citations from official docs, production validation

---

**Prompt Status**: EXAMPLE - Demonstrates template usage
**Next Step**: Use this as reference when creating actual research prompts
