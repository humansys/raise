# Governance Directory

> Authoritative artifacts that govern this solution

---

## Purpose

This directory contains **curated, approved artifacts** that have passed validation gates. It is the single source of truth for:

- Solution-level decisions and vision
- Project-level approved designs
- Accepted ADRs (Architecture Decision Records)
- Shared context (glossary, constitution)

## Structure

```
governance/
├── index.yaml          # Manifest of all artifacts (for agents)
├── solution/           # Solution-level (endures across projects)
│   ├── vision.md       # What this solution IS
│   ├── business_case.md # Why it exists
│   └── guardrails.md   # Constraints and rules
├── projects/           # Project-level (time-bound initiatives)
│   └── {project-name}/
│       ├── vision.md   # Project approach
│       └── design.md   # Technical design
├── context/            # Shared wisdom
│   ├── glossary.md     # Canonical terminology
│   └── constitution.md # Core principles
└── decisions/          # Accepted ADRs
    └── adr-*.md
```

## The Index

`governance/index.yaml` is the **entry point for agents**. It lists all artifacts with:

- Path, type, version, status
- Relationships between artifacts
- Approval dates

Agents should read the index first, then only fetch artifacts they need.

## Lifecycle

Artifacts arrive here through **governance promotion**:

```
work/                              governance/
─────                              ───────────
work/proposals/adr-011.md    →     governance/decisions/adr-011.md
     (draft)                            (accepted)

work/projects/foo/vision.md  →     governance/projects/foo/vision.md
     (draft)                            (approved)
```

The gate determines promotion. When a gate passes, use the governance-sync skill to promote.

## Maintenance

To prevent "golden data drift", use the maintenance tools in `dev/skills/`:

- `governance-sync.md` - Promote work to governance
- `governance-audit.md` - Detect drift
- `impact-analysis.md` - Analyze change impact

---

*Part of the Three-Directory Model (ADR-011)*
