# Core Concepts

> Understanding the fundamentals of RaiSE

---

## The Five Key Concepts

RaiSE is built on five interconnected concepts. Understanding these will help you use the framework effectively.

| Concept | One-Liner | Learn More |
|---------|-----------|------------|
| **Governance** | Why explicit rules matter | [governance.md](./governance.md) |
| **Work Cycles** | The five phases of work | [work-cycles.md](./work-cycles.md) |
| **Katas** | Guided step-by-step workflows | [katas.md](./katas.md) |
| **Gates** | Validation checkpoints | [gates.md](./gates.md) |
| **Artifacts** | The document hierarchy | [artifacts.md](./artifacts.md) |

## How They Connect

```
                    GOVERNANCE
                   (the "why")
                        │
                        ▼
    ┌───────────────────────────────────────┐
    │            WORK CYCLES                │
    │   (setup → solution → project →       │
    │    feature → maintenance)             │
    └───────────────────────────────────────┘
                        │
            ┌───────────┴───────────┐
            ▼                       ▼
         KATAS                   GATES
    (how to do work)      (how to validate)
            │                       │
            └───────────┬───────────┘
                        ▼
                   ARTIFACTS
              (what gets produced)
```

## Reading Order

**If you're new to RaiSE**, read in this order:

1. **[Governance](./governance.md)** — Understand the "why" first
2. **[Work Cycles](./work-cycles.md)** — See the big picture
3. **[Katas](./katas.md)** — Learn how work gets done
4. **[Gates](./gates.md)** — Understand quality control
5. **[Artifacts](./artifacts.md)** — Know what you'll produce

## Quick Definitions

| Term | Definition |
|------|------------|
| **Governance** | Explicit rules and standards that guide work |
| **Work Cycle** | A phase of work with specific purpose and artifacts |
| **Kata** | A guided workflow with verification at each step |
| **Gate** | A validation checkpoint that must pass before proceeding |
| **Artifact** | A document or asset produced by following a kata |
| **Guardrail** | A rule that constrains behavior (MUST/SHOULD/MAY) |

---

*For complete terminology, see the [Glossary](../reference/glossary.md)*
