# Epic E1136 Retrospective: Introspection Hardening

## Outcome

**All 5 done criteria met.** Introspection went from dead letter (0 records in E1134, 33% acceptance in E1133) to a working system (30 records, 76% acceptance, 5 epics).

## Stories Delivered

| Story | Summary | Outcome |
|-------|---------|---------|
| S1136.1 | PRIME/LEARN mandatory in skills | Adoption driver — mandatory > optional |
| S1136.2 | `rai learn write` CLI + schema | Validation at write time |
| S1136.3 | Auto-commit learning records | Eliminated persistence gap |
| S1136.4 | `rai learn push` server persistence | Server-side accumulation enabled |
| S1136.5 | Dogfood round 2 | 30 records analyzed, 3 bugs filed |

## Key Metrics

| Metric | Before (E1133) | After (E1136) |
|--------|-----------------|---------------|
| Learning records | 3 | 30 |
| Epics with records | 2 | 5 |
| Pattern acceptance | 33% | 76% |
| Schema consistency | Drifting | Stable |
| Git persistence | None | 100% |
| Server persistence | None | Available |

## What Worked

1. **Mandatory > Optional** — Changing PRIME/LEARN from markers to mandatory instructions was the single biggest lever. Acceptance jumped from 33% to 76%.
2. **Auto-commit eliminated a class of failure** — S1136.3 was XS effort but solved persistence completely.
3. **Decision B (reuse agent_events)** — S1136.4 shipped with zero server changes. Client-side Pydantic validation was sufficient.
4. **Dogfood with real data** — Analyzing 30 records from 5 epics revealed systemic issues (graph index, autonomous mode) that no amount of unit testing would catch.

## What Didn't Work / Gaps

1. **Autonomous mode compliance** — 58% record loss when agents run without HITL. Filed as RAISE-1277.
2. **Graph index in worktrees** — Tier1 queries dead in worktree context (~60% of records). Filed as RAISE-1276.
3. **Work ID normalization** — Casing creates duplicates. Filed as RAISE-1278.

## Spawned Work

- **RAISE-1275**: E1137 — Introspection Improvements (v3.0)
  - RAISE-1276: Graph index in worktrees
  - RAISE-1277: Autonomous mode LEARN enforcement
  - RAISE-1278: Work ID casing normalization

## Patterns

- **Mandatory instructions >> optional markers** for AI agent compliance
- **Zero-change server integration** via generic event endpoints + client-side validation
- **Dogfood on real multi-session data** reveals systemic issues invisible to unit tests
- **Auto-commit as persistence strategy** — simplest solution to "records get lost"
