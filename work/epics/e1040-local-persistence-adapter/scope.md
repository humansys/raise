---
epic_id: "E1040"
jira_key: "RAISE-1040"
title: "Local Persistence Adapter — Unified Protocol, Filesystem Backend, Full Skill Migration"
status: "in-progress"
created: "2026-04-02"
---

# E1040: Local Persistence Adapter

## Objective

Ensure no lifecycle skill writes first-order artifacts directly to filesystem.
All work artifacts (scope, design, plan, retro) and session state must pass
through a single unified adapter with validation, correct location resolution,
and atomic writes.

## Design Decisions (2026-04-02)

1. **1 protocol, not 2** — LocalPersistenceAdapter covers both work artifacts and session state
2. **Validation in the adapter** — frontmatter correctness, location resolution, atomic writes
3. **Full migration, no exceptions** — all skills migrate, no partial adoption
4. **No backend swappability yet** — Jira-native/Confluence backend is 3.0

## Stories

| # | Jira Key | Summary | Size | Depends On |
|---|----------|---------|------|------------|
| 1 | RAISE-1041 | S1040.1: LocalPersistenceAdapter Protocol — unified for work artifacts + session | S | — |
| 2 | RAISE-1042 | S1040.2: FilesystemAdapter — single backend, validation, atomic writes | M | S1040.1 |
| 3 | RAISE-1043 | S1040.3: Migrate all skills — lifecycle + session, zero direct writes | L | S1040.2 |

## Done Criteria

- [ ] No lifecycle skill has direct Write/Edit calls for work artifacts
- [ ] No session skill has direct writes to session-state.yaml
- [ ] FilesystemAdapter produces identical file layout to current behavior
- [ ] Atomic writes prevent data corruption (RAISE-697 closed by design)
- [ ] All existing tests pass

## References

- Origin: `adapter-vision.md` §4 (Missing Protocols)
- Jira: RAISE-1040
- Closes: RAISE-697 (session state corruption)
- Consolidated from 6 stories to 3 (2026-04-02 scope revision)
