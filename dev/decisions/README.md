# Architecture Decision Records (ADRs)

> **Purpose:** Document significant architectural decisions
> **Format:** Lightweight decision records
> **Status:** Active (add ADRs as decisions are made)

---

## When to Write an ADR

Write an ADR when you make a decision about:
- Architectural patterns (layers, modules, boundaries)
- Technology choices (libraries, frameworks, tools)
- Significant trade-offs (performance vs simplicity)
- Non-functional requirements (security, scalability)

**Don't write ADRs for:**
- Implementation details (use docstrings)
- Obvious choices (use Python for Python project)
- Trivial decisions (variable naming)

---

## ADR Template

```markdown
# ADR-XXX: [Title]

**Date:** YYYY-MM-DD
**Status:** [Proposed | Accepted | Deprecated | Superseded by ADR-YYY]
**Deciders:** [Who was involved]

## Context

What is the issue we're facing? What constraints exist?

## Decision

What did we decide to do?

## Alternatives Considered

What other options did we evaluate and why didn't we choose them?

## Consequences

What are the trade-offs? What do we gain? What do we accept?

## References

- Links to research, RFCs, discussions
```

---

## Index

| ID | Title | Status | Date |
|----|-------|--------|------|
| [001](adr-001-three-layer-architecture.md) | Three-Layer Architecture | Accepted | 2026-01-31 |
| [002](adr-002-pydantic-everywhere.md) | Pydantic for All Data Models | Accepted | 2026-01-31 |
| [003](adr-003-rich-for-output.md) | Rich for CLI Output | Accepted | 2026-01-31 |
| [004](adr-004-xdg-directories.md) | XDG Directory Compliance | Accepted | 2026-01-31 |

---

*ADR index - update when new decisions are made*
