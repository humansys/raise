# RaiSE Katas

Process definitions for AI-assisted software development.

## What is a Kata?

A **Kata** is a structured process definition that describes HOW to execute a phase of the RaiSE methodology. Like martial arts katas, these are forms you adapt to your context—not rigid tutorials to follow blindly.

```
┌─────────────────────────────────────────────────────────────────┐
│   TEMPLATE              KATA                VALIDATION GATE     │
│   ─────────            ─────               ────────────────     │
│   WHAT to produce      HOW to do it        IS IT GOOD?          │
└─────────────────────────────────────────────────────────────────┘
```

- **Template**: Artifact structure (in `templates/`)
- **Kata**: Process to create the artifact (here)
- **Validation Gate**: Quality checklist (in `gates/`)

## Kata Levels

| Level | Question | Purpose |
|-------|----------|---------|
| **principles/** | Why? When? | Philosophy and meta-process |
| **flow/** | How does it flow? | Value sequences by methodology phase |
| **patterns/** | What shape? | Reusable structures |
| **techniques/** | How to do? | Specific instructions (future) |

---

## Kata Index

### Principles (Meta-level)

| Kata | Purpose |
|------|---------|
| [meta-kata](./principles/meta-kata.md) | What is a kata and how to use it |
| [execution-protocol](./principles/execution-protocol.md) | The 7 steps to execute any kata |

### Flow (By Methodology Phase)

| Kata | Phase | Output | Gate |
|------|-------|--------|------|
| [discovery](./flow/discovery.md) | 1 | PRD | gate-discovery |
| [solution-vision](./flow/solution-vision.md) | 2 | Solution Vision | gate-vision |
| [tech-design](./flow/tech-design.md) | 3 | Tech Design | gate-design |
| [backlog-creation](./flow/backlog-creation.md) | 4 | Backlog | gate-backlog |
| [implementation-plan](./flow/implementation-plan.md) | 5 | Implementation Plan | gate-plan |
| [development](./flow/development.md) | 6 | Code | gate-code |

### Patterns (Reusable Structures)

| Kata | Context |
|------|---------|
| [code-analysis](./patterns/code-analysis.md) | Brownfield projects |
| [ecosystem-discovery](./patterns/ecosystem-discovery.md) | Integration mapping |
| [tech-design-stack](./patterns/tech-design-stack.md) | Stack-aware design |
| [dependency-validation](./patterns/dependency-validation.md) | New library adoption |

### Techniques (Future)

*Technique-level katas will be created based on demand.*

---

## Getting Started

1. **Read** [meta-kata](./principles/meta-kata.md) to understand what katas are
2. **Study** [execution-protocol](./principles/execution-protocol.md) for the 7-step protocol
3. **Identify** your current methodology phase
4. **Select** the corresponding flow kata
5. **Execute** following the protocol

## Validation Gates

Gates are in `gates/`:

| Gate | Phase | Validates |
|------|-------|-----------|
| [gate-discovery](../gates/gate-discovery.md) | 1 | PRD complete and valid |
| [gate-vision](../gates/gate-vision.md) | 2 | Solution Vision aligned |
| [gate-design](../gates/gate-design.md) | 3 | Tech Design verifiable |
| [gate-backlog](../gates/gate-backlog.md) | 4 | Backlog prioritized |
| [gate-plan](../gates/gate-plan.md) | 5 | Plan atomic and verifiable |
| [gate-code](../gates/gate-code.md) | 6 | Code ready for merge |

---

## References

- [Kata Schema](../reference/kata-schema.md) - Kata structure definition
- [Methodology](../core/methodology.md) - RaiSE methodology overview
- [Glossary](../core/glossary.md) - Canonical terminology

---

*RaiSE Katas v2.1 | You orchestrate. AI assists. Quality emerges.*
