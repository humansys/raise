# Work Directory

> The workbench for governed work-in-progress

---

## Purpose

This directory contains **active work** that has not yet been promoted to `governance/`. It is the workbench where:

- Features are developed
- ADRs are drafted
- Research spikes happen
- Any governed work-in-progress lives

## Structure

```
work/
├── features/           # Feature-level work
│   └── NNN-feature-name/
│       ├── spec.md     # Feature specification
│       ├── plan.md     # Implementation plan
│       └── tasks.md    # Task breakdown
├── proposals/          # Draft ADRs and proposals
│   └── adr-NNN-*.md
├── research/           # Spikes and investigations
│   └── {topic}/
├── analysis/           # Code and system analysis
│   └── {topic}/
└── projects/           # Draft project-level work
    └── {project-name}/
        ├── vision.md   # Draft project vision
        └── design.md   # Draft tech design
```

## Lifecycle

Work here is **transient**. It either:

1. **Gets promoted** to `governance/` after passing a gate
2. **Gets archived** if abandoned
3. **Stays ephemeral** (feature work that doesn't produce governance artifacts)

```
work/                              governance/
─────                              ───────────
Draft ADR           →  gate  →     Accepted ADR
Draft Project Vision →  gate  →     Approved Project Vision
Feature spec/plan   →  done  →     (nothing - ephemeral)
```

## Naming Conventions

### Features

```
work/features/NNN-short-name/
```

- `NNN` = sequential number (001, 002, ...)
- `short-name` = kebab-case description

### Proposals

```
work/proposals/adr-NNN-descriptive-title.md
```

- Follow ADR naming convention
- Use next available number

### Research

```
work/research/YYYY-MM-topic-name/
```

- Date prefix for chronological ordering
- Topic in kebab-case

## What Doesn't Belong Here

- **Approved artifacts** → `governance/`
- **Framework definitions** → `framework/`
- **Source code** → `src/`
- **Configuration** → `.raise/`

---

*Part of the Three-Directory Model (ADR-011)*
