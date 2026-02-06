---
research_id: "DRY-SOLID-PYTHON-20260205"
primary_question: "What are practical guidelines for applying DRY and SOLID principles in Python CLI codebases without over-engineering?"
decision_context: "Code quality standards for raise-cli development"
depth: "standard"
created: "2026-02-05"
version: "1.0"
template: "research-prompt-v1"
---

# Research Prompt: DRY and SOLID Principles in Python

> Practical application guidelines for CLI codebases

---

## Role Definition

You are a **Research Specialist** with expertise in **Python software architecture and design principles**. Your task is to conduct epistemologically rigorous research following scientific standards for evidence evaluation.

**Your responsibilities:**
- Search systematically across academic, official, and practitioner sources
- Evaluate evidence quality using RaiSE criteria
- Triangulate findings from 3+ independent sources per major claim
- Document contrary evidence and uncertainty explicitly
- Produce reproducible, auditable research outputs

---

## Research Question

**Primary**: What are practical guidelines for applying DRY and SOLID principles in Python CLI codebases without over-engineering?

**Secondary** (supporting questions):
1. When does DRY abstraction help vs hurt in Python? What is the "rule of three" and how should it be applied?
2. How should SOLID principles be adapted for Python's dynamic nature (not Java-style)?
3. When is composition preferred over inheritance in Python, and what patterns support this?
4. What are Python-specific code smells and their refactoring patterns?
5. How to balance DRY/SOLID with KISS/YAGNI in practice?
6. What refactoring patterns (extract method, extract class, introduce parameter object) work best in Python?
7. When should abstractions be created vs keeping code simple and direct?

---

## Decision Context

**This research will inform**: Code quality guidelines for raise-cli v2.0 development, potential updates to guardrails.md

**Stakeholder**: RaiSE development team (primarily Emilio)

**Timeline**: Immediate application

**Impact**: Wrong guidance leads to either spaghetti code (too little abstraction) or over-engineered complexity (too much abstraction). Both hurt maintainability.

---

## Instructions

### Search Strategy

Execute searches across these source types:

1. **Academic sources**
   - Google Scholar: "DRY principle software" "SOLID Python" "code abstraction empirical study"
   - arXiv: software engineering code quality
   - Purpose: Peer-reviewed research, theoretical foundations

2. **Official documentation**
   - Python official docs on modules, classes, design patterns
   - PEP documents on Python design philosophy
   - Purpose: Authoritative technical specifications

3. **Production evidence**
   - GitHub repositories (filter: >100 stars, active maintenance)
   - Engineering blogs: FAANG, major Python shops
   - Books: Clean Code, Pragmatic Programmer, Fluent Python
   - Purpose: Real-world validation, battle-tested patterns

4. **Community validation**
   - Reddit (r/Python, r/learnpython, r/programming)
   - Hacker News discussions
   - Conference talks (PyCon, EuroPython)
   - Purpose: Emerging consensus, practitioner wisdom

**Keywords to search**:
- "DRY principle Python when to apply"
- "SOLID principles Python dynamic language"
- "Python composition over inheritance"
- "Python code smells refactoring"
- "KISS YAGNI vs DRY SOLID balance"
- "Python extract method refactoring"
- "rule of three abstraction"
- "premature abstraction antipattern"
- "Python dependency injection simple"
- "duck typing vs interfaces Python"

**Sources to avoid**: Java-centric material that doesn't acknowledge Python's differences, pre-Python 3.6 content (type hints changed everything)

---

### Evidence Evaluation

For each source, assess:
- Type: Primary/Secondary/Tertiary
- Evidence Level: Very High/High/Medium/Low
- Key Finding: One-line takeaway
- Relevance: How it answers our question
- Date: Publication date (prefer 2020+)

---

### Triangulation Requirements

- Standard depth: 15-30 sources
- Major claims require 3+ independent confirmations
- Document contrary evidence explicitly

---

## Output Format

Artifacts in `work/research/dry-solid-python/`:
1. `sources/evidence-catalog.md` - All sources with ratings
2. `synthesis.md` - Triangulated claims and patterns
3. `recommendation.md` - Actionable guidelines
4. `README.md` - Navigation and summary

---

## Constraints

**Time**: 4-6 hours standard depth

**Focus priorities**:
1. Python-specific guidance (not generic OOP)
2. CLI codebase applicability
3. Practical heuristics over theory
4. Modern Python (3.10+) patterns

**Out of scope**:
- Web framework patterns (Django, Flask)
- Data science / ML patterns
- Academic theory without practical application
- Non-Python languages

---

## Reproducibility Metadata

To be filled after research:
- Tool/model used: TBD
- Search date: 2026-02-05
- Prompt version: 1.0
- Researcher: Rai (Claude Opus 4.5)
- Total time: TBD
