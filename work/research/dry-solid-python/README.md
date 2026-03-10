# Research: DRY and SOLID Principles in Python

> Practical guidelines for CLI codebase development

---

## Research Metadata

| Field | Value |
|-------|-------|
| **Research ID** | DRY-SOLID-PYTHON-20260205 |
| **Primary Question** | What are practical guidelines for applying DRY and SOLID principles in Python CLI codebases without over-engineering? |
| **Decision Context** | Code quality standards for raise-cli v2.0 development |
| **Depth** | Standard (4-6 hours) |
| **Tool/Model** | WebSearch (Claude Opus 4.5) |
| **Search Date** | 2026-02-05 |
| **Prompt Version** | 1.0 |
| **Researcher** | Rai |
| **Total Time** | ~3 hours |

---

## Quick Summary (5 minutes)

### Key Findings

1. **Rule of Three**: Wait for 3 occurrences before abstracting. First two instances don't reveal the true pattern.

2. **Semantic over Syntactic**: Only abstract code that represents the SAME business concept. Similar-looking code with different purposes should stay separate.

3. **Python SOLID is Lighter**: Duck typing, Protocols, and first-class functions reduce need for Java-style interfaces and inheritance.

4. **Composition by Default**: Reserve inheritance for genuine "is-a" relationships. Use composition for everything else.

5. **Premature Abstraction Compounds**: Wrong abstractions get worse as developers add special cases instead of removing them.

6. **Simple DI Wins**: Constructor injection + composition root is enough. Skip DI frameworks for CLI tools.

7. **Practicality Beats Purity**: Python's Zen supports pragmatic trade-offs over dogmatic adherence.

### Core Recommendation

**Adopt pragmatic guidelines that favor simplicity:**
- Start simple, add complexity when evidence demands
- Duplication < wrong abstraction (Sandi Metz)
- Functions and modules before classes
- Protocols over ABCs for type hints
- Composition over inheritance

---

## Document Index

| Document | Purpose | Read Time |
|----------|---------|-----------|
| [synthesis.md](synthesis.md) | Triangulated claims with evidence | 15 min |
| [recommendation.md](recommendation.md) | Actionable guidelines for raise-cli | 10 min |
| [sources/evidence-catalog.md](sources/evidence-catalog.md) | All 28 sources with ratings | Reference |
| [prompt.md](prompt.md) | Research prompt used | Reference |

---

## Decision Tree: When to Abstract

```
Duplicated code appears?
│
├── First occurrence
│   └── DO NOTHING - Just implement
│
├── Second occurrence
│   └── DO NOTHING - Not enough data
│
└── Third occurrence
    │
    ├── Same semantic concept?
    │   ├── Yes → ABSTRACT (Extract function/class)
    │   └── No → KEEP SEPARATE
    │
    └── Different semantic concepts that happen to look similar?
        └── KEEP SEPARATE - Not true duplication
```

---

## Quality Checklist (Passed)

- [x] Research question is specific and falsifiable
- [x] 10+ sources consulted (28 sources)
- [x] Evidence catalog created with levels
- [x] Major claims triangulated (3+ sources each)
- [x] Confidence level explicitly stated for each claim
- [x] Contrary evidence acknowledged where found
- [x] Recommendation is actionable
- [x] Governance linkage established (informs guardrails, code review)

---

## Governance Linkage

This research informs:
- `governance/solution/guardrails.md` - Consider adding Rule of Three guideline
- Code review practices - Challenge premature abstractions
- Developer onboarding - Include pragmatic SOLID guidance

---

## References

### Very High Evidence Sources
- [Sandi Metz - The Wrong Abstraction](https://sandimetz.com/blog/2016/1/20/the-wrong-abstraction)
- [Real Python - SOLID Design Principles](https://realpython.com/solid-principles-python/)
- [Python Patterns - Composition Over Inheritance](https://python-patterns.guide/gang-of-four/composition-over-inheritance/)
- [PEP 544 - Protocols](https://peps.python.org/pep-0544/)
- [PEP 20 - The Zen of Python](https://peps.python.org/pep-0020/)
- [Refactoring Guru](https://refactoring.guru/)
- [Fluent Python - Luciano Ramalho](https://www.oreilly.com/library/view/fluent-python-2nd/9781492056348/)

See [evidence-catalog.md](sources/evidence-catalog.md) for complete source list.

---

*Research completed: 2026-02-05*
*Researcher: Rai (Claude Opus 4.5)*
