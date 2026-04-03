# Epic Retrospective: E1040 — Local Persistence

**Epic:** E1040 | **Jira:** RAISE-1040
**Started:** 2026-04-02 | **Closed:** 2026-04-03
**Stories:** 3 delivered (S1040.1, S1040.2, S1040.4), 1 closed as unnecessary (S1040.3)

## Objective

All process-critical writes in RaiSE use atomic I/O via FilesystemAdapter.
Session state, patterns, journal, and developer profile writes gain protections
against corruption (RAISE-697) and data loss.

## Deliverables

| Story | Summary | Tests | Commits |
|-------|---------|-------|---------|
| S1040.1 | FilesystemAdapter — atomic write/append/read/list + path containment | 18 | 6 |
| S1040.2 | Migrate 5 CLI write sites to adapter + RAISE-697 timestamp protection | 15 | 7 |
| S1040.3 | ~~Migrate to stewards~~ — closed, unnecessary after DD-8 | — | — |
| S1040.4 | FilesystemDocsTarget frontmatter validation | 10 | 5 |

**Total:** 43 new tests, 18 commits, 0 regressions.

## Metrics

| Metric | Value |
|--------|-------|
| Stories planned | 4 (6 originally, consolidated twice) |
| Stories delivered | 3 |
| Stories closed (unnecessary) | 1 |
| New tests | 43 |
| Files created | 2 (filesystem_adapter.py, test_filesystem_adapter.py) |
| Files modified | 5 (writer.py, state.py, journal.py, profile.py, filesystem_docs.py) |
| Pyright errors introduced | 0 |
| Design decisions | 8 (DD-1 through DD-8) |
| Patterns captured | 8 (PAT-E-701 through PAT-E-708) |

## Key Decisions

### DD-8: The Pivot (most impactful)

Mid-epic, we recognized that the proposed **Steward layer** (DD-1 through DD-7) conflicted
with the Pluggable Domains vision (RAISE-650, 3.0). A Steward is an amalgama of Domain Gates
+ Schema + orchestration. Building it in 2.4.0 would mean dismantling it in 3.0 to redistribute
logic into Domain components (gates/, schema/, adapters).

**Decision:** Remove the Steward layer. Keep domain intelligence in CLI functions (where it
already lives). FilesystemAdapter provides atomic I/O as shared infrastructure — it survives
the 3.0 transition unchanged. Validation migrates to Domain Gates when Pluggable Domains land.

**Impact:** Eliminated S1040.3 entirely. Simplified S1040.2 from M+ to M. Avoided a temporary
abstraction that would need teardown.

### Design evolution

```
v1: 6 stories (2 protocols × 2 backends × 2 migrations)     — original Jira
v2: 3 stories (1 unified protocol + backend + migration)     — first consolidation
v3: 4 stories (Steward + Adapter architecture)               — design session
v4: 3 stories (Adapter only, no Steward, domain-aligned)     — DD-8 pivot
```

Each iteration reduced scope while preserving the core value: atomic writes + protections.

## What Went Well

1. **Interactive design session produced better architecture.** Walking through design challenges
   one-by-one with the developer surfaced the Steward conflict with Domains *before* any code
   was written. The cheapest point to pivot.

2. **Audit-first design.** S1040.2's design phase audited actual code before planning. This
   revealed that work artifacts already had an adapter (DocumentationTarget), and that
   `_append_jsonl` was a single migration point covering 3 callers. Without the audit, we
   would have over-scoped the migration.

3. **QR as mandatory gate caught real bugs.** S1040.1: path traversal security defect and
   TOCTOU races. S1040.2: ISO timestamp string comparison latent bug. S1040.4: inconsistent
   error signaling. Three stories, three QR catches.

4. **Jidoka applied consistently.** Every QR finding was fixed before merge, not deferred.
   The result: cleaner code with zero accumulated tech debt from the epic.

## What Could Improve

1. **Subagent pyright reporting was unreliable.** Subagents reported "0 errors" but IDE
   diagnostics showed issues. Root cause: worktree venv mismatch. Real pyright (run from
   worktree root) was clean, but the discrepancy eroded trust. Need to verify gates from
   the orchestrator, not just trust subagent reports.

2. **Story evolution created stale Jira descriptions.** RAISE-1040 was updated 3 times (original,
   steward design, DD-8 pivot). RAISE-1041/1042 summaries referenced stewards after DD-8 removed
   them. Jira was eventually updated but the lag creates confusion for anyone reading the backlog
   mid-epic.

3. **`disable-model-invocation` bug blocked `/rai-story-run`.** The worktree had stale copies
   of skill files with the flag. Fix was applied to release/2.4.0 and rebased, but the flag
   reappeared for skills not in the fix commit. Need a systematic fix across all skill copies.

## Patterns Captured

| ID | Type | Summary |
|----|------|---------|
| PAT-E-701 | process | QR as mandatory gate after subagent implementation catches security defects |
| PAT-E-702 | technical | Atomic file writes via temp-in-same-dir + os.rename + fsync |
| PAT-E-703 | architecture | Path containment (_resolve) — centralized security check |
| PAT-E-704 | architecture | Single migration point — migrate shared low-level functions to cover all callers |
| PAT-E-705 | process | Design-phase strategic pivot — eliminate abstractions that conflict with future architecture |
| PAT-E-706 | technical | ISO 8601 timestamp comparison — always parse to datetime, never compare strings |
| PAT-E-707 | architecture | Consistent error signaling — don't mix exceptions and Result types |
| PAT-E-708 | process | Single-method surgical insertion for validation without protocol changes |

## Strategic Alignment

- **FilesystemAdapter** is shared infrastructure per `pluggable-domains-vision.md` §3
- **CLI validation logic** migrates to Domain Gates when RAISE-650 Phase 1 delivers the Work Domain
- **Steward concept** was the right abstraction at the wrong time — it becomes Domain Gates in 3.0
- **RAISE-697** closed by design (timestamp protection in save_session_state)

## Closes

- RAISE-1040 (epic)
- RAISE-697 (session state corruption — by design)
