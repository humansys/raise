# Epic E1136: Introspection Hardening

> **Status:** IN PROGRESS
> **Created:** 2026-04-03
> **Branch:** release/2.4.0

## Objective

Fix the 3 adoption failures discovered during E1133 dogfood: agents skip PRIME/LEARN, records drift from schema, records don't persist. Make introspection work reliably in every story run.

## Findings (from E1133 S1133.5 + S1133.6 dogfood)

| Finding | Evidence | Impact |
|---------|----------|--------|
| **Adoption gap** | E1134 (4 stories): 0 LEARN records. Agent said "too simple". | Introspection is dead letter in simple stories |
| **Schema drift** | S1064.8: nested schema instead of flat. Agent improvised. | Records not parseable by aggregation |
| **No persistence** | Records in worktree local disk only. Lost on worktree cleanup. | No data accumulates for metrics |

## Stories

| ID | Story | Size | Deps | Description |
|----|-------|------|------|-------------|
| S1136.1 | PRIME/LEARN mandatory in skills | S | — | Change markers to mandatory instructions, add schema inline, add to quality checklist ✓ |
| S1136.2 | `rai learn write` CLI + schema validation | XS | S1136.1 | CLI command that validates against Pydantic model and writes record ✓ |
| S1136.3 | Auto-commit learning records | XS | S1136.1 | Include learnings in git add during task commits |
| S1136.4 | `rai learn push` — server persistence | M | S1136.2 | `rai learn write` CLI + schema validation | XS | S1136.1 | CLI command that validates against Pydantic model and writes record ✓ |
| S1136.5 | Dogfood round 2 | S | S1136.1, S1136.2, S1136.3 | 3+ stories with fixes, measure vs baseline |

## Done Criteria

- [ ] ≥5 learning records produced across ≥2 epics
- [ ] All records pass schema validation (flat, ~10 fields)
- [ ] Records committed to git (persist across worktrees)
- [ ] Acceptance rate measurable (target: improve from 33% baseline)
- [ ] Server endpoint accepts learning records (S1136.4)

## Baseline Metrics (from S1133.5)

| Metric | Value | N |
|--------|-------|---|
| Acceptance rate | 33% | 3 patterns |
| Gap rate | 100% | 1 query |
| Pattern utility | 100% | 1 pattern |
| Records produced | 3 total | 2 épicas |

## References

- E1133: Skill Introspection (parent epic)
- ADR-014: Skill Introspection Aspect
- `aspects/introspection.md`
- `packages/raise-cli/src/raise_cli/memory/learning.py`
- RAISE-1199: Epic ID collision (infrastructure bug found during dogfood)
