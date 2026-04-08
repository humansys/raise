# RaiSE Framework

> **Reliable AI Software Engineering** — Explicit governance for AI-assisted development

---

## What is RaiSE?

RaiSE is a methodology framework that makes AI-assisted software development **reliable** through explicit governance. Instead of hoping AI tools do the right thing, RaiSE provides structured guidance that ensures consistency, quality, and traceability.

**The core insight:** AI coding assistants are powerful but unpredictable. RaiSE channels that power through well-defined workflows, validation gates, and governance artifacts.

## Who is RaiSE for?

- **Development teams** using AI coding assistants (Copilot, Claude, Cursor, etc.)
- **Tech leads** who need predictable, auditable AI-assisted workflows
- **Organizations** requiring governance and compliance in AI-augmented development

## Core Principles

1. **Governance as Code** — All policies, decisions, and standards are versioned artifacts in Git
2. **Explicit over Implicit** — No magic, no hidden behavior, everything documented
3. **Validation Gates** — Quality checkpoints that must pass before work proceeds
4. **Observable Workflow** — Every step produces traceable artifacts

## How RaiSE Works

RaiSE organizes work into **five cycles**, each with specific katas (guided workflows) and gates (validation checkpoints):

| Cycle | Purpose | Example Katas |
|-------|---------|---------------|
| **Setup** | Onboard and configure | Analyze codebase, establish governance |
| **Solution** | Define the big picture | Business case, solution vision |
| **Project** | Plan specific initiatives | PRD, technical design, backlog |
| **Feature** | Build incrementally | User stories, implementation, review |
| **Maintenance** | Sustain and improve | Refactoring, documentation |

## Quick Start

**New to RaiSE?** Start here:

- [Getting Started Guide](./getting-started/README.md) — Your first steps
- [Core Concepts](./concepts/README.md) — Understand the fundamentals

**Looking for specifics?**

- [Reference Documentation](./reference/) — Glossary, principles, detailed specs
- [Vision Document](./vision.md) — Full framework vision

## Directory Structure

```
framework/
├── README.md            # This file - framework overview
├── getting-started/     # How to adopt RaiSE
├── concepts/            # Core concepts explained simply
├── reference/           # Dense reference material
├── vision.md            # Full framework vision
└── index.yaml           # Artifact manifest
```

## The RaiSE Promise

With RaiSE, you get:

- ✅ **Predictable AI assistance** — Guided workflows, not random suggestions
- ✅ **Quality gates** — Catch issues before they compound
- ✅ **Full traceability** — Every decision documented, every artifact versioned
- ✅ **Adaptable structure** — Start strict (Shu), adapt with experience (Ha), innovate (Ri)

---

*RaiSE Framework v2.5 — [Constitution](./reference/constitution.md) | [Glossary](./reference/glossary.md)*
