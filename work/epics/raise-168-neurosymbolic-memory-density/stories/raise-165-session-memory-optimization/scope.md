## Story Scope: RAISE-165

**Epic:** RAISE-168 (Neurosymbolic Memory Density)
**Size:** S
**Priority:** P2
**Depends on:** RAISE-166 ✅ (compact format confirmed viable — Markdown-KV is top performer)

### Problem

Session start loads ~1,860 tokens of identity narrative (~80% human-readable prose, not behavioral primes), duplicates the skills list already in system-reminder, includes business milestones with zero coding utility, and omits the one thing that prevents CLI fumbling: `cli-reference.md`.

### In Scope

- Add `cli-reference.md` load to session-init hook
- Compress `identity/core.md` + `identity/perspective.md` to behavioral essentials (values, boundaries, principles)
- Remove skills list from `MEMORY.md` (duplicate of system-reminder)
- Remove business milestones from `MEMORY.md` (zero coding utility)
- Deduplicate PAT-198/PAT-199 (identical entries)
- Convert identity primes in context bundle to compact format (RAISE-166 confirmed Markdown-KV works)

### Out of Scope

- Memory query format changes (→ RAISE-166)
- `rai cli reference --compact` auto-generation command (parking lot)
- Token monitoring / programmatic context detection (parking lot)

### Done Criteria

- [ ] `cli-reference.md` loads at session start via hook
- [ ] Identity files compressed (behavioral essentials only)
- [ ] MEMORY.md pruned (no skills list, no milestones, no duplicate PATs)
- [ ] Context bundle identity primes converted to compact format
- [ ] Retrospective complete
