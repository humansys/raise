---
research_id: "PYDANTIC-V2-BEST-PRACTICES-20260205"
primary_question: "What are the best practices and anti-patterns for using Pydantic v2 in a CLI tool codebase?"
decision_context: "Inform raise-cli codebase standards and refactoring decisions"
depth: "standard"
created: "2026-02-05"
version: "1.0"
template: "research-prompt-v1"
---

# Research Prompt: Pydantic v2 Best Practices

> Template for structured AI research with epistemological rigor

---

## Role Definition

You are a **Research Specialist** with expertise in **Python data validation, type systems, and CLI architecture**. Your task is to conduct epistemologically rigorous research following scientific standards for evidence evaluation.

**Your responsibilities:**
- Search systematically across academic, official, and practitioner sources
- Evaluate evidence quality using RaiSE criteria
- Triangulate findings from 3+ independent sources per major claim
- Document contrary evidence and uncertainty explicitly
- Produce reproducible, auditable research outputs

---

## Research Question

**Primary**: What are the best practices and anti-patterns for using Pydantic v2 in a CLI tool codebase?

**Secondary** (supporting questions):
1. When should we use BaseModel vs dataclass (standard or Pydantic)?
2. What are the patterns for model_validator vs field_validator (pre vs after)?
3. What are serialization best practices (model_dump, model_json_schema)?
4. What performance considerations apply (frozen, slots, lazy initialization)?
5. What common anti-patterns should we avoid?
6. How does Pydantic v2 integrate with FastAPI/Typer?

---

## Decision Context

**This research will inform**: raise-cli code standards, guardrails, and potential refactoring

**Stakeholder**: RaiSE development team

**Timeline**: Immediate (F&F release Feb 9)

**Impact**: Consistent, performant, maintainable data models across the CLI toolkit

---

## Instructions

### Search Strategy

Execute searches across these source types:

1. **Official documentation**
   - Pydantic v2 official docs (docs.pydantic.dev)
   - Migration guide from v1 to v2
   - Purpose: Authoritative technical specifications

2. **Production evidence**
   - GitHub repositories using Pydantic v2 (>100 stars, active)
   - FastAPI, Typer integration patterns
   - Purpose: Real-world validation, battle-tested patterns

3. **Community validation**
   - Reddit (r/Python, r/FastAPI), Hacker News
   - Conference talks, podcasts
   - Purpose: Emerging consensus, practitioner wisdom

**Keywords to search**:
- "pydantic v2 best practices"
- "pydantic BaseModel vs dataclass"
- "pydantic model_validator field_validator"
- "pydantic performance optimization"
- "pydantic anti-patterns"
- "pydantic typer integration"
- "pydantic frozen model"
- "pydantic serialization patterns"

**Sources to avoid**: Pydantic v1-only documentation (pre-2023)

---

### Evidence Evaluation

Use RaiSE engineering criteria for evidence levels.

---

## Constraints

**Time**: ~2 hours (standard depth)

**Focus priorities**:
1. Model design patterns (BaseModel vs dataclass)
2. Validation patterns
3. Performance considerations
4. Anti-patterns

**Out of scope**:
- Database ORM integration (SQLAlchemy, etc.)
- Complex nested validation beyond CLI needs
- Pydantic AI specific patterns (separate research)

---

## Reproducibility Metadata

**Tool used**: WebSearch + synthesis
**Search date**: 2026-02-05
**Prompt version**: 1.0
**Researcher**: Rai (Claude Opus 4.5)
