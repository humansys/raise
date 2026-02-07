# Governance Directory

> Authoritative artifacts that govern this project

---

## Purpose

This directory contains **curated, approved artifacts** that have passed validation gates. It is the single source of truth for:

- Product vision and strategy
- Code standards and guardrails
- Requirements and technical design
- Accepted ADRs (Architecture Decision Records)

## Structure

```
governance/
├── index.yaml          # Manifest of all artifacts (for agents)
├── vision.md           # What this product IS
├── business_case.md    # Why it exists
├── guardrails.md       # Code quality standards
├── guardrails-stack.md # Stack best practices
├── prd.md              # Product requirements
├── design.md           # Technical architecture
├── backlog.md          # Epics and roadmap
├── context/            # Shared wisdom
└── decisions/          # Accepted ADRs
    └── adr-*.md
```

All governance artifacts live at the root level. When multiple projects
are needed (enterprise), add a `projects/` subdirectory — root-level
artifacts automatically become shared across projects.

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
```

The gate determines promotion. When a gate passes, use the governance-sync skill to promote.

## Maintenance

To prevent "golden data drift", use the maintenance tools in `dev/skills/`:

- `governance-sync.md` - Promote work to governance
- `governance-audit.md` - Detect drift
- `impact-analysis.md` - Analyze change impact

---

*Part of the Three-Directory Model (ADR-011)*
