# Recommendation: RaiSE Backlog Sync Architecture

**Research Date**: 2026-02-14
**Researcher**: Claude Sonnet 4.5
**Confidence**: HIGH

---

## Decision

**Implement a Local-First, Hub-and-Spoke Bidirectional Sync Architecture with Three-Way Merge and Field-Level Ownership.**

### Architecture Components

1. **Local-First Storage**
   - `governance/backlog.md` + memory graph (JSONL) as immediate write targets
   - Changes written locally first, marked with `sync_status: pending`
   - No blocking network calls during CLI operations

2. **Hub-and-Spoke Topology**
   - RaiSE memory graph as central hub
   - All backends sync through RaiSE (not peer-to-peer)
   - Simplifies transformation logic and conflict resolution

3. **Conflict Resolution Strategy (Field-Level)**
   - **Three-way merge**: `title`, `description` (collaborative fields)
   - **Last-Write-Wins (external)**: `assignee`, `external_status`, `priority` (team owns)
   - **Last-Write-Wins (Rai)**: `current_story`, `progress`, `workflow_state` (Rai owns)
   - **Rai-only (no sync)**: `tasks`, `learnings`, `session_context` (internal only)
   - **Append-only**: `comments`, `attachments` (merge lists, never conflict)

4. **Sync Mechanisms**
   - **Inbound**: Hybrid webhooks (JIRA, GitLab) + polling fallback (Odoo)
   - **Outbound**: REST API calls via background queue
   - **Infrastructure**: Redis Streams or Python queue for async processing

5. **Change Detection**
   - File watchers on `governance/backlog.md` for local changes
   - Memory graph JSONL append-only (Write-Ahead Log pattern)
   - Timestamp + hash tracking for change detection

---

## Rationale

### Why Three-Way Merge Over CRDTs/OT?

**Evidence-backed reasons**:
1. **Battle-tested**: Git's three-way merge handles millions of repos successfully ([Atlassian Git Tutorial](https://www.atlassian.com/git/tutorials/using-branches/merge-conflicts))
2. **Appropriate complexity**: RaiSE backlog has coarse-grained entities (stories, epics), not character-level collaborative editing ([CRDTs vs. OT](https://systemdr.substack.com/p/crdts-vs-operational-transformation))
3. **Production reality**: Companies like Cinapse abandoned CRDTs due to unnecessary complexity ([Why Cinapse Moved Away From CRDTs](https://www.powersync.com/blog/why-cinapse-moved-away-from-crdts-for-sync))
4. **RaiSE Principle 11**: "Simple heuristics over complex solutions" (Constitution)

**Trade-off**: Three-way merge requires common ancestor tracking, but RaiSE already has memory graph with temporal history.

---

### Why Local-First + Eventual Consistency?

**Evidence-backed reasons**:
1. **Modern standard**: Linear, Notion use local-first architecture ([The Hard Things About Sync](https://expertofobsolescence.substack.com/p/the-hard-things-about-sync))
2. **Offline capability**: Developers work offline; CLI must function without network ([Offline-First Sync Patterns](https://developersvoice.com/blog/mobile/offline-first-sync-patterns/))
3. **Performance**: No blocking on external API calls during `rai story start`, `rai story close`, etc.
4. **Acceptable latency**: Team doesn't need instant view of Rai's internal task decomposition

**Trade-off**: Team sees Rai's state with delay (seconds to minutes). Acceptable for backlog sync; not acceptable for real-time chat.

---

### Why Field-Level Ownership Over Single Master?

**Evidence-backed reasons**:
1. **Dual source of truth is valid**: MVoT pattern when "different systems own different aspects" ([SSoT vs MVoT](https://blog.csgsolutions.com/truth-data-truth-ssot-vs-mvot))
2. **Entity partitioning**: Rai owns workflow lifecycle, team owns collaboration ([Mastering the Dual](https://alok-mishra.com/2023/11/27/mastering-the-dual-strategic-data-synchronization-in-domain-api-architecture/))
3. **Prevents conflicts**: Clear boundaries reduce ambiguity and data loss

**Trade-off**: Requires explicit ownership matrix. But this clarity prevents silent data overwrites.

---

### Why Hub-and-Spoke Over Peer-to-Peer?

**Evidence-backed reasons**:
1. **Multi-system standard**: When syncing 3+ systems, hub-and-spoke wins ([Bidirectional Sync Patterns](https://dev3lop.com/bidirectional-data-synchronization-patterns-between-systems/))
2. **Unified transformation**: Single place for business logic instead of N×(N-1) integrations ([Bi-Directional Sync Challenges](https://www.stacksync.com/blog/the-engineering-challenges-of-bi-directional-sync-why-two-one-way-pipelines-fail))
3. **RaiSE already has the hub**: Memory graph is canonical source for all Rai data

**Trade-off**: RaiSE becomes critical path (if down, sync stops). But RaiSE is already required for CLI operations.

---

### Why Hybrid Webhooks + Polling?

**Evidence-backed reasons**:
1. **API reality**: Not all backends support webhooks for all entities ([Polling vs Webhooks](https://unified.to/blog/polling_vs_webhooks_when_to_use_one_over_the_other))
2. **Reliability**: Polling as backup catches missed webhook events ([Webhook vs. API Polling](https://www.geeksforgeeks.org/system-design/webhook-vs-api-polling-in-system-design/))
3. **Production pattern**: "Systems combine both techniques" is industry standard

**Trade-off**: Polling adds latency and API usage. Mitigate with smart intervals (exponential backoff, max 1/min).

---

## Trade-offs

| Aspect | Chosen Approach | Alternative | Trade-off Accepted |
|--------|----------------|-------------|-------------------|
| **Conflict Resolution** | Three-way merge | CRDT | CRDT complexity unnecessary for coarse-grained data |
| **Consistency Model** | Eventual | Strong | Team sees Rai state with delay (acceptable) |
| **Topology** | Hub-and-spoke | Peer-to-peer | RaiSE is critical path (already required for CLI) |
| **Sync Trigger** | Hybrid webhook + polling | Webhooks only | Polling adds latency (acceptable for backlog) |
| **Field Ownership** | Dual master (field-level) | Single master | Requires ownership matrix (worth the clarity) |

---

## Risks & Mitigations

### Risk 1: Three-Way Merge Library Availability

**Risk**: Python may lack robust Markdown three-way merge libraries.

**Mitigation**:
1. Use Git subprocess (`git merge-file`) - battle-tested, handles text well
2. Fallback: Line-based merge with `difflib` (Python stdlib)
3. If semantic Markdown merge needed: Custom implementation using AST parser

**Confidence**: MEDIUM (Git subprocess is proven, but adds dependency)

---

### Risk 2: Webhook Reliability (Missed Events)

**Risk**: Webhooks can fail silently (network issues, endpoint downtime).

**Mitigation**:
1. Periodic polling as backup (every 5-15 minutes)
2. Compare local vs external timestamps to detect missed updates
3. Idempotent sync operations (handle duplicate events gracefully)

**Confidence**: HIGH (polling backup is standard pattern)

---

### Risk 3: Conflict Rate Higher Than Expected

**Risk**: If developers frequently edit same fields simultaneously, conflicts increase.

**Mitigation**:
1. Monitor conflict rate in production
2. If >5% of syncs conflict: Implement field-level locking or optimistic concurrency
3. User education: "Rai owns workflow, team owns collaboration"

**Confidence**: HIGH (backlog edits are rarely simultaneous)

---

### Risk 4: Performance at Scale (1000+ Items)

**Risk**: Syncing 1000+ backlog items across 3+ backends may be slow.

**Mitigation**:
1. Incremental sync (only changed items, not full backlog)
2. Background queue with parallelization (N workers)
3. Batch API calls where supported (JIRA REST API supports batch)
4. Lazy sync (only active stories/epics, not entire backlog)

**Confidence**: MEDIUM (need to prototype and measure)

---

### Risk 5: External Backend API Changes

**Risk**: JIRA/GitLab/Odoo APIs evolve; breaking changes break sync.

**Mitigation**:
1. Version-specific adapters (e.g., `JiraAdapter_v3`, `JiraAdapter_v4`)
2. Graceful degradation (log errors, continue CLI operations)
3. Integration tests against live API (detect breakage early)

**Confidence**: HIGH (standard API integration practice)

---

## Alternatives Considered

### Alternative 1: CRDT-Based Sync (Automerge/Yjs)

**Pros**: Automatic conflict resolution, peer-to-peer possible, offline-first

**Cons**:
- Overkill for coarse-grained backlog entities
- Performance issues at scale ([Automerge 2.0](https://news.ycombinator.com/item?id=34586433))
- Complexity violates RaiSE Principle 11
- Production abandonment cases ([Cinapse](https://www.powersync.com/blog/why-cinapse-moved-away-from-crdts-for-sync))

**Why Not Chosen**: Complexity unjustified for backlog use case.

---

### Alternative 2: Single Master (External System Wins)

**Pros**: Simple (no conflict resolution needed), aligns with external system

**Cons**:
- Loses Rai-specific state (task decomposition, learnings, session context)
- Forces Rai to poll constantly for state (can't work offline)
- External systems don't model Rai workflows (current_story, progress, etc.)

**Why Not Chosen**: Defeats purpose of local-first Rai workflows.

---

### Alternative 3: Strong Consistency (Distributed Locks)

**Pros**: No conflicts (only one writer at a time per field)

**Cons**:
- Requires network for all writes (can't work offline)
- Latency (lock acquisition delays CLI operations)
- Complexity (distributed lock coordination, deadlock prevention)

**Why Not Chosen**: Violates offline-first requirement; adds unacceptable latency.

---

### Alternative 4: Operational Transformation (OT)

**Pros**: Proven for real-time collaborative editing (Google Docs)

**Cons**:
- Requires central server coordination ([Building Real-Time Collaboration](https://www.tiny.cloud/blog/real-time-collaboration-ot-vs-crdt/))
- Complex transformation functions for each operation type
- Overkill for backlog sync (not character-level edits)

**Why Not Chosen**: Complexity unjustified; requires always-online server.

---

## Implementation Guidance

### Phase 1: Local-First Foundation (MVP)

**Goal**: RaiSE CLI writes to local backlog.md + memory graph with sync_status markers.

**Components**:
- `sync_status` field in memory graph: `pending` | `synced` | `conflict`
- File watcher on `governance/backlog.md` for change detection
- Background queue (Python `queue.Queue` or Redis Streams)

**Validation**: CLI operations work offline; changes marked as pending.

---

### Phase 2: Single Backend Sync (JIRA)

**Goal**: Prove architecture with one backend before generalizing.

**Components**:
- JIRA REST API adapter (`JiraAdapter`)
- Webhook receiver for JIRA events (Flask/FastAPI endpoint)
- Three-way merge implementation (Git subprocess)
- Field-level conflict resolution (hardcoded JIRA field mappings)

**Validation**: Create story in Rai → syncs to JIRA; edit in JIRA → syncs to Rai.

---

### Phase 3: Multi-Backend (GitLab, Odoo)

**Goal**: Generalize adapter pattern; validate hub-and-spoke topology.

**Components**:
- Generic `BackendAdapter` interface
- `GitLabAdapter`, `OdooAdapter` implementations
- Polling fallback for backends without webhooks
- Unified transformation logic in memory graph hub

**Validation**: Story syncs across all 3 backends; conflicts resolve correctly.

---

### Phase 4: Production Hardening

**Goal**: Handle edge cases, optimize performance.

**Components**:
- Idempotent sync operations (handle duplicates)
- Exponential backoff for failed syncs
- Conflict rate monitoring and alerting
- Batch API calls for performance
- Integration tests against live APIs

**Validation**: 1000+ item backlog syncs in <30s; conflict rate <5%.

---

## Success Criteria

1. **Offline-first works**: CLI operations succeed without network
2. **Bidirectional sync works**: Changes propagate both directions (Rai ↔ External)
3. **No data loss**: Field-level ownership prevents silent overwrites
4. **Acceptable latency**: Sync completes within 30s for typical backlog (50-100 items)
5. **Low conflict rate**: <5% of syncs require manual conflict resolution
6. **Robust error handling**: Failed syncs don't break CLI; logged and retried

---

## References

See [Synthesis](synthesis.md) and [Evidence Catalog](sources/evidence-catalog.md) for detailed sources.

---

## Next Steps

1. **Create ADR**: Document this decision in `architecture/decisions/ADR-XXX-backlog-sync.md`
2. **Create Story**: `S2.XX: Implement local-first sync foundation (Phase 1)`
3. **Prototype**: Build Git subprocess three-way merge PoC
4. **Research Gap**: Python libraries for Markdown three-way merge (or confirm Git subprocess)
5. **API Review**: Check JIRA/GitLab/Odoo webhook coverage for backlog entities
