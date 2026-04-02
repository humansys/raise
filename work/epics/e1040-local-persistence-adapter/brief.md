---
epic_id: "E1040"
title: "Local Persistence Adapter"
status: "draft"
created: "2026-04-02"
---

# Epic Brief: Local Persistence Adapter

## Hypothesis
For RaiSE lifecycle skills that write work artifacts and session state,
the Local Persistence Adapter is a unified typed protocol + filesystem backend
that enforces validation, correct location resolution, and atomic writes.
Unlike direct filesystem I/O scattered across 12+ skills, our solution
centralizes persistence governance and eliminates corruption bugs (RAISE-697).

## Success Metrics
- **Leading:** First skill migrated produces byte-identical output via adapter
- **Lagging:** Zero direct filesystem writes for work artifacts or session state in any skill; RAISE-697 closed by design

## Appetite
S — 3 stories (protocol, backend, migration)

## Scope Boundaries
### In (MUST)
- Unified LocalPersistenceAdapter protocol (work artifacts + session)
- FilesystemAdapter backend with validation and atomic writes
- Full migration of all lifecycle + session skills
- Identical file layout to current behavior (non-breaking)

### In (SHOULD)
- Frontmatter validation on write
- Location resolution (epic/story directory mapping)

### No-Gos
- Backend swappability to Jira/Confluence (3.0 scope)
- Release adapter (inline logic works for now)
- Metrics adapter (local JSONL is sufficient)
- Multi-backend fallback chains

### Rabbit Holes
- Over-abstracting the protocol for future backends that don't exist yet
- Separate protocols for work vs session (already decided: 1 unified protocol)
- Async variants (filesystem I/O is fast enough synchronous)
