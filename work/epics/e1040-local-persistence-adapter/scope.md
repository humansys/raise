---
epic_id: "E1040"
jira_key: "RAISE-1040"
title: "Local Persistence — Atomic I/O + Protections for Process-Critical Data"
status: "in-progress"
created: "2026-04-02"
---

# E1040: Local Persistence

## Objective

All process-critical writes in RaiSE use atomic I/O via FilesystemAdapter.
Session state, patterns, journal, and developer profile writes gain protections
against corruption (RAISE-697) and data loss. No new abstraction layer — domain
intelligence stays in CLI functions and migrates to Domain Gates in 3.0.

## Architecture

```
Skill → CLI (validation + orchestration) → FilesystemAdapter (atomic I/O)
```

In 3.0 (RAISE-650 Pluggable Domains):
```
Skill → Domain Gate (validation) → Adapter (atomic I/O)
```

The FilesystemAdapter is shared infrastructure that survives the 3.0 transition.
CLI validation logic migrates to Domain Gates. No intermediate layer to dismantle.

## Design Decisions

See `design-decisions.md` for full context. Summary:

| # | Decision | Status |
|---|----------|--------|
| DD-1 | ~~Steward + Adapter~~ → Adapter only, domain logic in CLI | Revised |
| DD-2 | Scope: session + memory + developer (work artifacts already have adapter) | Active |
| DD-3 | ~~Stewards own domain intelligence~~ → CLI owns until Domain Gates (3.0) | Revised |
| DD-4 | Single concrete FilesystemAdapter, no protocol until second backend | Active |
| DD-5 | CLI orchestrates flow and validation | Active (unchanged in practice) |
| DD-6 | Add missing protections to existing CLI functions | Active |
| DD-7 | Extensibility-ready: principle preserved, vehicle deferred to Domains | Revised |
| DD-8 | No Steward layer — aligns with Pluggable Domains (3.0) | New |

## Stories

| # | Jira Key | Summary | Size | Depends On | Status |
|---|----------|---------|------|------------|--------|
| 1 | RAISE-1041 | S1040.1: FilesystemAdapter — atomic I/O primitives | S | — | done |
| 2 | RAISE-1042 | S1040.2: Migrate CLI writes to FilesystemAdapter + protections | M | S1040.1 | backlog |
| 3 | RAISE-1043 | ~~S1040.3: Migrate CLI to stewards~~ | — | — | closed (unnecessary) |
| 4 | RAISE-1044 | S1040.4: Harden FilesystemDocsTarget — frontmatter validation | S | — | backlog |

```
S1040.1 (Adapter, done) ──→ S1040.2 (CLI migration + protections)
S1040.4 (Docs hardening) ─── independent ─────────────────────────
```

## Done Criteria

- [x] FilesystemAdapter provides atomic write/append/read/list with path containment
- [ ] Session state writes use FilesystemAdapter (atomic, no corruption)
- [ ] Timestamp comparison before session state overwrite (closes RAISE-697)
- [ ] Pattern, journal, session index writes use FilesystemAdapter (atomic append)
- [ ] Developer profile writes use FilesystemAdapter
- [ ] FilesystemDocsTarget validates frontmatter before writing work artifacts
- [ ] All existing tests pass
- [ ] File layout identical to current behavior (non-breaking)

## Implementation Plan

### Milestones

**M1: Atomic Foundation** — S1040.1 (done) + S1040.4
- FilesystemAdapter exists with atomic write/append/read/list
- FilesystemDocsTarget validates frontmatter

**M2: Epic Complete** — S1040.2
- All CLI writes migrated to FilesystemAdapter
- RAISE-697 timestamp protection active
- All tests pass, done criteria met

### Progress

| # | Story | Status | Milestone |
|---|-------|--------|-----------|
| 1 | S1040.1: FilesystemAdapter | done | M1 |
| 4 | S1040.4: Docs hardening | backlog | M1 |
| 2 | S1040.2: CLI migration + protections | backlog | M2 |

## References

- Design decisions: `design-decisions.md`
- Origin: `adapter-vision.md` §4 (Missing Protocols)
- Jira: RAISE-1040
- Closes: RAISE-697 (session state corruption)
- Strategic alignment: `pluggable-domains-vision.md` — adapter is shared infrastructure, validation migrates to Domain Gates in 3.0
- Evolution: 6 stories → 3 → 4 (steward) → 3 (adapter-only, domain-aligned)
