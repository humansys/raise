# README.md Draft

**Status**: DRAFT - Structure paths TBD after WP0 analysis
**Date**: 2026-01-16

---

## Proposed README Content

```markdown
# RaiSE Commons

> The conceptual and ontological foundation for Reliable AI Software Engineering

## What is RaiSE?

RaiSE (Reliable AI Software Engineering) is a framework for building high-quality software with AI assistance. It provides principles, patterns, and practices that help development teams work effectively with AI coding assistants.

**This repository contains the conceptual foundation** — the "what" and "why" of RaiSE. It is not production code; it is the ontological model, terminology, methodology, and decision records that define the framework.

## Quick Start

| I want to... | Start here |
|--------------|------------|
| Understand the core principles | [Constitution](TBD/constitution.md) |
| Learn the terminology | [Glossary](TBD/glossary.md) |
| See the methodology | [Methodology](TBD/methodology.md) |
| Understand key decisions | [ADRs](TBD/adrs/) |
| Practice with exercises | [Katas](TBD/katas/) |
| Use document templates | [Templates](TBD/templates/) |

## Repository Structure

> **Note**: Structure TBD after ontological analysis in WP0

```text
raise-commons/
├── [TBD based on WP0 decision]
```

## RaiSE Ecosystem

This repository is part of a broader RaiSE ecosystem. Additional tools and implementations exist but are not detailed here. This repository serves as the canonical source of truth for RaiSE concepts and terminology.

## Key Concepts

### Canonical Terminology (v2.1)

RaiSE uses precise terminology. Key terms include:

- **Orquestador**: The human who directs AI-assisted development (not "Developer")
- **Validation Gate**: Quality checkpoints at each phase (not "DoD")
- **Guardrail**: Constraints that guide AI behavior (not "Rule")
- **Kata Levels**: Principio → Flujo → Patrón → Técnica (not L0-L3)

See the [Glossary](TBD/glossary.md) for complete definitions.

### Core Principles

1. **Semantic Coherence First** — All documentation maintains consistency with the ontology
2. **Governance as Code** — Policies and standards are versioned artifacts
3. **Validation at Each Phase** — Quality is continuous, not a final event
4. **Simplicity over Completeness** — Concise documentation that covers 80% of cases
5. **Continuous Improvement (Kaizen)** — The system learns from friction and improves

## Contributing

We welcome feedback and contributions! This is a conceptual repository, so contributions are primarily:

- Documentation improvements
- Terminology clarifications
- New Kata exercises
- Template enhancements

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Reporting Issues

Open a [GitLab Issue](TBD_GITLAB_URL/issues) for:
- Questions about RaiSE concepts
- Bug reports in documentation
- Suggestions for improvements

## License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.

---

*RaiSE Commons v2.1 | Part of the RaiSE Framework*
```

---

## CONTRIBUTING.md Draft

```markdown
# Contributing to RaiSE Commons

Thank you for your interest in contributing to RaiSE Commons!

## Understanding This Repository

**RaiSE Commons is a conceptual repository.** It contains:
- Ontological model and terminology
- Methodology documentation
- Architecture Decision Records (ADRs)
- Kata exercises for learning
- Document templates

It does **not** contain production code. Contributions focus on documentation quality and conceptual clarity.

## How to Provide Feedback

### Questions & Discussion
Open a [GitLab Issue](TBD_GITLAB_URL/issues) with the label `question`.

### Bug Reports
If you find errors in documentation (broken links, outdated information, inconsistencies):
1. Open an Issue describing the problem
2. Include the file path and specific text if applicable
3. Label with `bug`

### Suggestions
For improvements or new content:
1. Open an Issue describing your suggestion
2. Explain the value it would add
3. Label with `enhancement`

## Contribution Process

1. **Open an Issue first** — Discuss the change before investing time
2. **Fork the repository** — Create your own copy
3. **Create a feature branch** — `git checkout -b feature/your-change`
4. **Make your changes** — Follow the guidelines below
5. **Submit a Merge Request** — Reference the original Issue

## Style Guidelines

### Terminology
- Use canonical v2.1 terminology (see [Glossary](TBD/glossary.md))
- Avoid deprecated terms: DoD, Rule, Developer (as role), L0-L3
- Use: Validation Gate, Guardrail, Orquestador, Principio/Flujo/Patrón/Técnica

### Language
- Spanish and English are both acceptable
- Be consistent within a single document
- Technical terms may remain in English regardless of document language

### Formatting
- Use Markdown (CommonMark spec)
- Follow existing document structure
- Include date and version in formal documents

## Questions?

If you're unsure about anything, open an Issue and ask. We're happy to help!

---

*RaiSE Commons | Apache 2.0 License*
```

---

## Notes for Implementation

1. **All TBD paths** will be filled after WP0 structure decision
2. **GitLab URL** needs actual repo URL after public release
3. **README length** ~150 lines - intentionally concise per Principle IV
4. **CONTRIBUTING length** ~80 lines - low barrier for F&F users

---

*Quickstart draft prepared: 2026-01-16*
*Finalize after WP0 structure decision*
