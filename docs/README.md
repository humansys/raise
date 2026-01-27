# RaiSE Documentation

The conceptual foundation for reliable AI-assisted software engineering.

## Quick Navigation

| I want to... | Start here |
|--------------|------------|
| Understand RaiSE principles | [Constitution](./core/constitution.md) |
| Learn the terminology | [Glossary](./core/glossary.md) |
| See how it works | [Methodology](./core/methodology.md) |
| Execute a workflow phase | [Katas](./katas/README.md) |
| Use artifact templates | [Templates](./templates/) |
| Validate my work | [Gates](./gates/) |

---

## Documentation Structure

```
docs/
├── core/           # Foundation: principles, terminology, methodology
├── katas/          # Process definitions: HOW to do each phase
├── templates/      # Artifact structures: WHAT to produce
├── gates/          # Validation criteria: quality checkpoints
├── guides/         # Implementation guides for specific tools
└── reference/      # Technical reference documents
```

## The RaiSE Triad

Every phase of RaiSE methodology follows this pattern:

```
┌─────────────────────────────────────────────────────────────────┐
│   templates/           katas/              gates/               │
│   ──────────          ───────             ───────               │
│   WHAT to produce     HOW to do it        IS IT GOOD?           │
│   (artifact)          (process)           (validation)          │
└─────────────────────────────────────────────────────────────────┘
```

## Core Concepts

### Orquestador

The human who directs AI-assisted development. You define requirements, set Guardrails, select Katas, and validate outputs.

### Kata

A structured process definition describing how to execute a methodology phase. Not a tutorial—a form you adapt to your context.

### Validation Gate

A quality checkpoint with specific criteria. Pass the gate before proceeding to the next phase.

### Guardrail

A constraint that guides AI behavior within defined boundaries.

---

## Getting Started

1. **Read the Constitution** - Understand the "why" behind RaiSE
2. **Review the Glossary** - Learn canonical terminology
3. **Explore the Methodology** - See how phases connect
4. **Try a Kata** - Execute a process for your current phase

---

*RaiSE Commons | You orchestrate. AI assists. Quality emerges.*
