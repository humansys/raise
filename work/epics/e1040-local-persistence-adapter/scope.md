---
epic_id: "E1040"
jira_key: "RAISE-1040"
title: "Steward + Adapter — Reliability Governance for Process-Critical Data"
status: "in-progress"
created: "2026-04-02"
---

# E1040: Steward + Adapter

## Objective

All process-critical data in RaiSE is managed by a Steward — a domain-aware
component that validates, protects integrity, and delegates I/O to a backend
Adapter. No skill or CLI function writes process data directly to filesystem.

## Architecture

```
Skill → CLI → Steward (domain rules, validation, protection)
                 → Adapter (atomic I/O, backend-specific)
```

## Design Decisions

See `design-decisions.md` for full context. Summary:

| # | Decision |
|---|----------|
| DD-1 | Steward + Adapter two-layer architecture |
| DD-2 | Scope: session + memory + developer (work artifacts already have adapter) |
| DD-3 | Stewards own domain intelligence, adapters are dumb I/O |
| DD-4 | Single concrete FilesystemAdapter, no protocol until second backend |
| DD-5 | CLI orchestrates flow, stewards handle persistence |
| DD-6 | Absorb existing Pydantic validation, add missing protections |

## Stories

| # | Jira Key | Summary | Size | Depends On |
|---|----------|---------|------|------------|
| 1 | RAISE-1041 | S1040.1: FilesystemAdapter — atomic I/O primitives | S | — |
| 2 | RAISE-1042 | S1040.2: SessionSteward + MemorySteward + DeveloperSteward | M | S1040.1 |
| 3 | RAISE-1043 | S1040.3: Migrate CLI to stewards — replace direct writes, delete old functions | M | S1040.2 |
| 4 | RAISE-1044 | S1040.4: Harden FilesystemDocsTarget — frontmatter validation | S | — |

```
S1040.1 (Adapter) ──→ S1040.2 (Stewards) ──→ S1040.3 (Migration)
S1040.4 (Docs hardening) ─── independent ─────────────────────────
```

## Done Criteria

- [ ] SessionSteward manages state, index, journal with timestamp protection (RAISE-697)
- [ ] MemorySteward manages patterns with ID generation and validation
- [ ] DeveloperSteward manages profile with defensive merge
- [ ] FilesystemAdapter provides atomic write/append for all stewards
- [ ] Zero direct filesystem writes for session/memory/developer data in CLI
- [ ] FilesystemDocsTarget validates frontmatter before writing work artifacts
- [ ] All existing tests pass
- [ ] File layout identical to current behavior (non-breaking)

## References

- Design decisions: `design-decisions.md`
- Origin: `adapter-vision.md` §4 (Missing Protocols)
- Jira: RAISE-1040
- Closes: RAISE-697 (session state corruption)
- Evolution: 6 stories → 3 consolidated → 4 redesigned (Steward architecture)
