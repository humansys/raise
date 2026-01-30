# Dev Directory

> Internal tooling for framework maintainers

---

## Purpose

This directory contains **tools for maintaining the RaiSE framework**. These are NOT part of the framework that gets injected to consumer projects — they're how we BUILD and MAINTAIN RaiSE.

## Structure

```
dev/
├── README.md               # This file
├── framework-index.yaml    # Meta-index for change tracking
└── skills/                 # Governance maintenance skills
    ├── governance-sync.md  # Promote work → governance
    ├── governance-audit.md # Detect golden data drift
    └── impact-analysis.md  # Analyze change impact
```

## Skills

### governance-sync

Promotes artifacts from `work/` to `governance/` or `framework/` after gates pass.

```
/dev/governance-sync --source work/proposals/adr-011.md --level solution --type decision
```

### governance-audit

Detects drift between governance artifacts and reality.

```
/dev/governance-audit --scope full
/dev/governance-audit --scope framework --fix
```

### impact-analysis

Analyzes what needs updating when governance artifacts change.

```
/dev/impact-analysis --artifact framework/context/glossary.md --change-type modify
```

## framework-index.yaml

A meta-index that tracks:

- **Concepts**: Where terms are defined
- **Categories**: File types and their impact level
- **Propagation rules**: What to update when X changes

Used by the skills for automated change tracking.

## Typical Workflow

```
1. Make changes in work/
2. /dev/impact-analysis --artifact {changed file}
3. Review impact, make related changes
4. Pass gate
5. /dev/governance-sync --source {file}
6. /dev/governance-audit --scope full (periodic)
```

## What Doesn't Belong Here

- **Framework engine** → `.raise/`
- **Framework specification** → `framework/`
- **Project governance** → `governance/`
- **Active work** → `work/`

---

*Internal tooling. Not part of injected framework.*
