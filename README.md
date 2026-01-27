# RaiSE Commons

The conceptual foundation for reliable AI-assisted software engineering.

> *You orchestrate. AI assists. Quality emerges.*

## What is RaiSE?

**RaiSE** (Reliable AI Software Engineering) is a framework for building software with AI assistance. You remain in control as the **Orquestador**—defining requirements, setting Guardrails, and validating outputs at every phase.

This repository contains the methodology, terminology, and exercises that define how RaiSE works. It's not code; it's the "why" and "how" behind effective human-AI collaboration.

## Quick Start

| I want to... | Start here |
|--------------|------------|
| Understand RaiSE principles | [Constitution](docs/core/constitution.md) |
| Learn the terminology | [Glossary](docs/core/glossary.md) |
| See how it works | [Methodology](docs/core/methodology.md) |
| Execute a workflow phase | [Katas](docs/katas/README.md) |
| Use artifact templates | [Templates](docs/templates/) |
| Validate my work | [Gates](docs/gates/) |

## Repository Structure

```
raise-commons/
├── docs/
│   ├── core/           # Foundation: Constitution, Glossary, Methodology
│   ├── katas/          # Process definitions (the HOW)
│   ├── templates/      # Artifact structures (the WHAT)
│   ├── gates/          # Validation criteria (the QUALITY)
│   └── reference/      # Technical reference
├── README.md           # You are here
├── LICENSE             # Apache 2.0
└── CONTRIBUTING.md     # Contribution guidelines
```

## The RaiSE Triad

Every phase follows this pattern:

```
┌─────────────────────────────────────────────────────────────────┐
│   TEMPLATE              KATA                VALIDATION GATE     │
│   ─────────            ─────               ────────────────     │
│   WHAT to produce      HOW to do it        IS IT GOOD?          │
└─────────────────────────────────────────────────────────────────┘
```

- **Templates** define artifact structure
- **Katas** guide the process to create artifacts
- **Gates** validate quality before proceeding

## Core Terminology

| Term | Definition |
|------|------------|
| **Orquestador** | The human who directs AI-assisted development |
| **Kata** | Structured process definition for a methodology phase |
| **Validation Gate** | Quality checkpoint with specific criteria |
| **Guardrail** | Constraint that guides AI behavior |

See the full [Glossary](docs/core/glossary.md) for canonical terminology.

## RaiSE Ecosystem

This repository is part of the broader RaiSE framework. It focuses on the conceptual foundation—methodology, terminology, and exercises—that other RaiSE tools implement.

## Contributing

We welcome feedback and contributions. See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Report issues**: Use [GitLab Issues](../../issues)

## License

[Apache 2.0](LICENSE) - See LICENSE file for details.

---

*RaiSE Commons | Reliable AI Software Engineering*
