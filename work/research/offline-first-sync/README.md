# Research: Offline-First Sync Strategies

**Research ID**: offline-first-sync-20260214
**Status**: Complete
**Date**: 2026-02-14
**Researcher**: Claude (Sonnet 4.5)
**Confidence**: HIGH

---

## 15-Minute Overview

### Research Question

What sync strategies do offline-first tools (Git, CouchDB, PouchDB, local-first software) use for reliable sync with eventual consistency? How do they handle conflicts, partial sync, and network failures?

### Context

Designing sync for RaiSE's local-first backlog architecture. Local backlog is always queryable (token-efficient, fast), external backends are for team collaboration.

### Recommendation

**Implement local-first delta sync using sequence IDs, Last-Write-Wins conflict resolution with 3-way merge fallback, exponential backoff retry policy, and background offline queue.**

**Confidence**: HIGH

### Key Findings

1. **Local-first is industry standard** (2024-2025): Local data is source of truth, server is secondary (Ink & Switch, Linear, Figma, ElectricSQL, PowerSync)
2. **Delta sync is non-negotiable**: All production systems use incremental sync (sequence IDs or timestamps), not full-state sync
3. **LWW is pragmatic for task tracking**: Linear, Figma show LWW works when conflicts are rare; CRDTs are overkill for this domain
4. **3-way merge enables auto-merge**: Git proves this scales to billions of operations; use last-synced state as merge base
5. **Exponential backoff + jitter is standard**: AWS, Better Stack converge on this for network resilience
6. **SQLite is de facto client store**: ElectricSQL, PowerSync, SQLiteSync all use SQLite for local-first persistence
7. **Eventual consistency is acceptable**: CAP theorem trade-off (choose AP over C for local-first)

### Evidence Quality

- **32 sources** (25% Very High, 47% High, 22% Medium, 6% Low)
- **10 major claims** triangulated with 3+ sources each
- **5 paradigm shifts** identified (cloud-first → local-first, CRDT pragmatism, delta sync convergence, SQLite standard, centralized ordering)
- **5 gaps** documented (token efficiency, backlog-specific patterns, schema evolution, security, quantitative benchmarks)

### What's Next

1. Create ADR documenting this decision
2. Design Phase 1 story (MVP: one-way sync to Linear)
3. Build POC to validate assumptions
4. Measure token costs, latency, conflict rate
5. Iterate based on learnings

---

## Navigation

- **[Recommendation](recommendation.md)** ← Start here (actionable decision)
- **[Synthesis](synthesis.md)** ← Deep dive (10 claims, 5 patterns, gaps)
- **[Evidence Catalog](sources/evidence-catalog.md)** ← All 32 sources with ratings
- **[Research Scope](research-scope.md)** ← Original question and constraints
- **[Research Prompt](prompt.md)** ← Reproducibility (how this was conducted)

---

## Files

```
offline-first-sync/
├── README.md                        ← You are here (navigation)
├── recommendation.md                ← Actionable decision (read this first)
├── synthesis.md                     ← Analysis (claims, patterns, gaps)
├── research-scope.md                ← Question definition
├── prompt.md                        ← Research prompt (reproducibility)
└── sources/
    └── evidence-catalog.md          ← All 32 sources
```

---

## Quick Reference

### Recommended Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ RaiSE Local Backlog (SQLite)                                │
│ - Source of truth                                           │
│ - Always queryable (offline)                                │
│ - Optimistic UI updates                                     │
└────────────────┬────────────────────────────────────────────┘
                 │
                 │ Background Sync
                 │ (Delta, Sequence IDs)
                 │
┌────────────────┴────────────────────────────────────────────┐
│ Sync Layer                                                  │
│ - Offline queue (SQLite table)                              │
│ - Exponential backoff retry                                 │
│ - LWW + 3-way merge conflict resolution                     │
│ - Per-system sequence ID tracking                           │
└────────────────┬────────────────────────────────────────────┘
                 │
                 │ HTTP APIs
                 │
     ┌───────────┼───────────┐
     │           │           │
┌────▼────┐ ┌────▼────┐ ┌───▼─────┐
│ Linear  │ │  Jira   │ │ GitHub  │
│  API    │ │  API    │ │   API   │
└─────────┘ └─────────┘ └─────────┘
```

### Sync Algorithm

1. **On local write**: Queue operation (create/update/delete) in offline queue
2. **Background worker**: Process queue when connected
3. **Delta sync**: Fetch changes from external system since `last_sync_id`
4. **Conflict detection**: Compare local vs remote vs last-synced
5. **Merge**:
   - Different fields: Auto-merge (3-way)
   - Same field: Last-Write-Wins (server timestamp)
   - Conflict: Expose to user for manual resolution
6. **Update**: Apply merged state to local DB
7. **Advance watermark**: Update `last_sync_id`
8. **Retry on failure**: Exponential backoff with jitter

### Implementation Phases

1. **Phase 1 (MVP)**: One-way sync (RaiSE → Linear) for create operations
2. **Phase 2**: Bidirectional sync with 3-way merge
3. **Phase 3**: Multi-system support (Linear, Jira, GitHub)
4. **Phase 4**: Conflict resolution UI, advanced features
5. **Phase 5**: Optimization (token costs, performance, monitoring)

---

## Research Metadata

- **Tool/model**: WebSearch (Claude Code)
- **Search date**: 2026-02-14
- **Prompt version**: 1.0 (research-prompt-template)
- **Researcher**: Claude (Sonnet 4.5)
- **Total time**: ~6 hours
- **Searches conducted**: 14 WebSearch queries
- **Sources gathered**: 32 unique high-value sources
- **Evidence distribution**: Very High (25%), High (47%), Medium (22%), Low (6%)
- **Temporal coverage**: 2019-2026 (81% from 2024-2026)

---

## Quality Checklist

- [x] Research question is specific and falsifiable
- [x] Decision context clearly stated (ADR for RaiSE backlog sync)
- [x] Scope boundaries defined (focus on sync patterns, not real-time collaboration)
- [x] Minimum source count met (32 sources > 15-30 target for standard depth)
- [x] Mix of academic, official, and practitioner sources
- [x] Sources include publication/update dates
- [x] Evidence catalog complete with all required fields
- [x] Major claims triangulated (10 claims, all 3+ sources)
- [x] Confidence levels explicitly stated for each claim
- [x] Contrary evidence acknowledged (Cinapse moving away from CRDTs)
- [x] Gaps and unknowns documented (5 gaps)
- [x] Recommendation is specific and actionable
- [x] Trade-offs explicitly acknowledged (5 trade-offs)
- [x] Risks identified with mitigations (5 risks)
- [x] Clear link to decision context (next step: create ADR)
- [x] All sources cited with URLs
- [x] Search keywords documented (in prompt.md)
- [x] Tool/model used recorded (WebSearch, Claude Sonnet 4.5)
- [x] Research date recorded (2026-02-14)

---

## Sources Highlights

### Foundational (Very High Evidence)

1. **Ink & Switch**: [Local-first software: You own your data, in spite of the cloud](https://www.inkandswitch.com/local-first/) (2019)
   - Defines 7 principles for local-first software
   - Theoretical foundation for the field

2. **CouchDB Docs**: [Replication Protocol](https://docs.couchdb.org/en/stable/replication/protocol.html) (2024)
   - 15+ years of production experience
   - Delta sync with sequence IDs

3. **Git Docs**: [Merge Strategies](https://git-scm.com/docs/merge-strategies) (2024)
   - Billions of merge operations
   - 3-way merge with common ancestor

### Production Systems (High Evidence)

4. **Linear**: [Scaling the Linear Sync Engine](https://linear.app/now/scaling-the-linear-sync-engine) (2024)
   - Task tracking (similar to RaiSE)
   - LWW + incremental sync IDs

5. **Figma**: [How Figma's multiplayer technology works](https://www.figma.com/blog/how-figmas-multiplayer-technology-works/) (2023)
   - CRDT-inspired, not pure CRDT
   - Central server for ordering

6. **Netflix**: [Delta Synchronization Platform](https://netflixtechblog.com/delta-a-data-synchronization-and-enrichment-platform-e82c36a79aee) (2019)
   - Large-scale eventual consistency
   - CDC pattern

### Sync Infrastructure (High Evidence)

7. **ElectricSQL**: [Introducing ElectricSQL v0.6](https://electric-sql.com/blog/2023/09/20/introducing-electricsql-v0.6) (2023)
   - Postgres-SQLite active-active sync
   - CRDTs for reconciliation

8. **PowerSync**: [Backend DB - SQLite sync engine](https://www.powersync.com) (2024)
   - Partial sync with dynamic partitioning
   - Background write-back

### Resilience Patterns (High Evidence)

9. **AWS**: [Timeouts, retries and backoff with jitter](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/) (2023)
   - Production-proven retry strategy
   - Exponential backoff + jitter

10. **Better Stack**: [Mastering Exponential Backoff](https://betterstack.com/community/guides/monitoring/exponential-backoff/) (2024)
    - Concrete implementation guidance
    - Formula and examples

---

## Governance Linkage

**Next step**: Create ADR (Architecture Decision Record)

**File**: `decisions/adr-NNN-backlog-sync-strategy.md`

**Status**: Recommendation complete; awaiting ADR approval

**Dependencies**: None (greenfield sync implementation)

**Related work**:
- Epic: E2.5 (Team Collaboration - Backlog Sync)
- Story: TBD (Phase 1 MVP implementation)

---

## Contact

Questions or need clarification? This research was conducted by Claude (Sonnet 4.5) on 2026-02-14. Refer to `prompt.md` for reproducibility details.

---

**Last Updated**: 2026-02-14
**Status**: Complete ✓
**Confidence**: HIGH
