# Synthesis: Offline-First Sync Strategies

Research date: 2026-02-14
Evidence sources: 32 (see evidence-catalog.md)

---

## Major Claims (Triangulated)

### Claim 1: Local-first architecture prioritizes local data as source of truth with eventual consistency to remote systems

**Confidence**: HIGH

**Evidence**:
1. [Ink & Switch local-first paper](https://www.inkandswitch.com/local-first/) - "Treats the copy of the data on your local device as the primary copy, with servers holding secondary copies to assist with access from multiple devices"
2. [Android Offline-First Guide](https://www.droidcon.com/2025/12/16/the-complete-guide-to-offline-first-architecture-in-android/) - "Local database is the Single Source of Truth, ensuring that the UI is fast, consistent, and resilient under all conditions"
3. [Linear Sync Engine](https://linear.app/now/scaling-the-linear-sync-engine) - "Stores a copy of most data locally in IndexedDB and pushes updates over WebSockets"
4. [ElectricSQL](https://electric-sql.com/blog/2023/09/20/introducing-electricsql-v0.6) - "Apps read and write data directly from and to a local embedded SQLite database"

**Disagreement**: None found

**Implication**: RaiSE's local backlog as source of truth aligns with industry-converged pattern. External backends (Linear, Jira, GitHub) should be treated as collaboration layer, not source of truth.

---

### Claim 2: Delta-based incremental sync is the sustainable strategy for minimizing bandwidth and preserving state

**Confidence**: HIGH

**Evidence**:
1. [Offline-First Sync Patterns](https://developersvoice.com/blog/mobile/offline-first-sync-patterns/) - "Delta-sync is the sustainable strategy, where scalable apps rely on timestamp, version, or token-based delta mechanisms to minimize bandwidth"
2. [Linear Sync Engine](https://linear.app/now/scaling-the-linear-sync-engine) - "Uses incremental sync IDs; able to apply a range of changesets from one point in time to another using SyncActions"
3. [Netflix Delta Platform](https://netflixtechblog.com/delta-a-data-synchronization-and-enrichment-platform-e82c36a79aee) - "Delta-Connector captures changes from transaction logs; Delta table is your journal"
4. [CouchDB Replication Protocol](https://docs.couchdb.org/en/stable/replication/protocol.html) - "Uses sequence IDs for incremental replication; replicator reads changes since last sequence"
5. [AWS AppSync Delta Sync](https://docs.aws.amazon.com/appsync/latest/devguide/tutorial-delta-sync.html) - "Delta table stores records of changes; clients receive only data altered since their last query"

**Disagreement**: None found

**Implication**: RaiSE should implement delta sync using sequence IDs or timestamps, not full-state sync. Track "last synced" watermark per external system.

---

### Claim 3: Conflict resolution cannot be an afterthought; system must choose between Last-Write-Wins, CRDTs, or Operational Transformation

**Confidence**: HIGH

**Evidence**:
1. [Offline-First Sync Patterns](https://developersvoice.com/blog/mobile/offline-first-sync-patterns/) - "Conflict resolution cannot be an afterthought—while Last-Write-Wins (LWW) may suffice for preferences, collaborative apps demand CRDTs or Operational Transformation (OT)-like strategies"
2. [Linear Sync Engine](https://linear.app/now/scaling-the-linear-sync-engine) - "Conflicts are actually not that common in Linear, and for certain systems, conflict resolution isn't an urgent issue, making the LWW system enough"
3. [Figma Multiplayer](https://www.figma.com/blog/how-figmas-multiplayer-technology-works/) - "Not a true CRDT because it relies on a central server for ordering, but it's inspired by CRDT concepts—specifically the Last-Writer-Wins Register pattern"
4. [CouchDB Conflict Model](https://docs.couchdb.org/en/stable/replication/conflicts.html) - "Deterministic conflict resolution using revision tree depth + lexicographic sorting; conflicts exposed to application layer for manual resolution"
5. [Yjs Documentation](https://docs.yjs.dev/) - "Uses CRDT algorithms to merge changes automatically without conflicts, even when made offline"

**Disagreement**: None found (consensus that choice depends on use case)

**Implication**: RaiSE backlog sync to external systems can likely use LWW (similar to Linear's reasoning: conflicts are rare in task tracking). Full CRDT complexity is overkill for this use case.

---

### Claim 4: Three-way merge using common ancestor is the proven pattern for automatic conflict resolution when possible

**Confidence**: HIGH

**Evidence**:
1. [Git Merge Strategies](https://git-scm.com/docs/merge-strategies) - "ort strategy (default) uses 3-way merge algorithm; creates merged tree of common ancestors"
2. [3-Way Merge Explanation](https://blog.git-init.com/the-magic-of-3-way-merge/) - "Git uses three commits to generate merge: two branch tips and their common ancestor"
3. [Gearset 3-Way Merge](https://docs.gearset.com/en/articles/9325332-two-way-and-three-way-merges-explained) - "As long as changes are made in different parts of a file, Git uses a three-way merge strategy to figure out what to keep and merges automatically"
4. [Atlassian Git Tutorial](https://www.atlassian.com/git/tutorials/using-branches/git-merge) - "Non-overlapping changes are automatically incorporated into final merged result"

**Disagreement**: None found

**Implication**: For RaiSE backlog items, if local and remote both modified the same item, use 3-way merge with the last-synced state as common ancestor. Most field updates will auto-merge (title vs description, etc.).

---

### Claim 5: Network resilience requires exponential backoff with jitter for retry policies

**Confidence**: HIGH

**Evidence**:
1. [AWS Builders Library](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/) - "Exponential backoff with jitter prevents thundering herd; jitter adds randomness to spread retries around in time"
2. [Better Stack Backoff Guide](https://betterstack.com/community/guides/monitoring/exponential-backoff/) - "Formula: delay = base_delay * (2 ^ retry_count); add jitter to prevent synchronized retries"
3. [AWS Prescriptive Guidance](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/retry-backoff.html) - "Retry pattern improves application stability by transparently retrying operations that fail due to transient errors"
4. [HackerOne Retry Strategies](https://www.hackerone.com/blog/retrying-and-exponential-backoff-smart-strategies-robust-software) - "Exponential backoff balances need to retry with need to reduce load on service, making delay longer after each failed attempt"
5. [GeeksforGeeks Retry Strategies](https://www.geeksforgeeks.org/system-design/retries-strategies-in-distributed-systems/) - "Exponential backoff increases delay exponentially, reducing probability of many clients retrying simultaneously"

**Disagreement**: None found

**Implication**: RaiSE sync should implement exponential backoff (base 2s, max 5 minutes) with jitter (±25%) for retries when external API calls fail.

---

### Claim 6: CRDTs provide strong eventual consistency but add complexity and memory overhead

**Confidence**: HIGH

**Evidence**:
1. [Yjs vs Automerge Comparison](https://velt.dev/blog/best-crdt-libraries-real-time-data-sync) - "Yjs uses memory-efficient, binary-based approach with garbage collection mechanisms for better scalability"
2. [CRDT Benchmarks](https://github.com/dmonad/crdt-benchmarks) - "Yjs outperforms Automerge on document size and speed; Automerge 2.0 narrowed the gap"
3. [Cinapse Moving Away from CRDTs](https://www.powersync.com/blog/why-cinapse-moved-away-from-crdts-for-sync) - "CRDTs added complexity without benefits for their use case; simpler LWW was sufficient"
4. [Yjs Documentation](https://docs.yjs.dev/) - "Shared data types like Map and Array can be automatically merged without merge conflicts"
5. [What are CRDTs - Loro](https://loro.dev/docs/concepts/crdt) - "CRDTs feature eventual consistency by enabling processes to access data locally and later merge it asynchronously"

**Disagreement**: Trade-off between complexity vs automatic conflict resolution; consensus that CRDTs are not always necessary

**Implication**: RaiSE should avoid full CRDT implementation for backlog sync. The complexity and memory overhead are not justified for infrequent sync to external systems. LWW + 3-way merge is sufficient.

---

### Claim 7: Eventual consistency enables high availability and partition tolerance (AP in CAP theorem)

**Confidence**: HIGH

**Evidence**:
1. [CAP Theorem](https://en.wikipedia.org/wiki/CAP_theorem) - "Distributed systems must choose 2 of 3: Consistency, Availability, Partition Tolerance"
2. [Eventual Consistency Explanation](https://arpitbhayani.me/blogs/eventual-consistency/) - "Enables high availability and partition tolerance (AP in CAP); trades immediate consistency for resilience"
3. [Strong vs Eventual Consistency](https://blog.levelupcoding.com/p/strong-vs-eventual-consistency) - "Each node can serve reads and writes independently with synchronization happening in background"
4. [CouchDB Eventual Consistency](https://guide.couchdb.org/draft/consistency.html) - "Guarantees that, given enough time and no new updates, all replicas will converge to the same state"
5. [Demystifying CAP Theorem](https://medium.com/@marton.waszlavik/demystifying-cap-theorem-eventual-consistency-and-exactly-once-delivery-guarantee-ed20cf7cc877) - "Eventual Consistency is the most relaxed form; system will become consistent over time but may temporarily have inconsistencies"

**Disagreement**: None found

**Implication**: RaiSE's local-first architecture with eventual sync to external systems is theoretically sound. Accept temporary inconsistencies between local and remote; guarantee convergence when connected.

---

### Claim 8: SQLite is the de facto standard for local-first persistence on clients

**Confidence**: HIGH

**Evidence**:
1. [ElectricSQL](https://electric-sql.com/blog/2023/09/20/introducing-electricsql-v0.6) - "Postgres-to-SQLite active-active sync using logical replication"
2. [PowerSync](https://www.powersync.com) - "Backend DB - SQLite sync engine for Postgres, MongoDB, MySQL"
3. [SQLiteSync](https://github.com/sqliteai/sqlite-sync) - "Local-first SQLite extension using CRDTs for seamless, conflict-free data sync"
4. [SQLite Sync Engine Lessons](https://antoine.fi/sqlite-sync-engine-with-reactivity) - "SQLite triggers for change detection; BroadcastChannel for reactivity"
5. [Linear Sync Engine](https://linear.app/now/scaling-the-linear-sync-engine) - Uses IndexedDB (JavaScript equivalent; shows convergence on embedded DB pattern)

**Disagreement**: Web apps use IndexedDB instead of SQLite, but pattern is the same (embedded, transactional, queryable local store)

**Implication**: RaiSE's use of SQLite for local backlog aligns with industry standard. No need to reconsider this choice.

---

### Claim 9: Last-Write-Wins is simple but risky; requires clock synchronization and risks data loss

**Confidence**: MEDIUM

**Evidence**:
1. [LWW Implementation Guide](https://oneuptime.com/blog/post/2026-01-30-last-write-wins/view) - "LWW is simple but risks data loss with concurrent updates; requires clock synchronization"
2. [LWW in Database Systems](https://www.linkedin.com/pulse/last-write-wins-database-systems-yeshwanth-n-emc8c) - "Clocks on machines drift, and it is easy to get skewed results"
3. [LWW vs CRDTs](https://dzone.com/articles/conflict-resolution-using-last-write-wins-vs-crdts) - "LWW can be useful—and safe—if you are certain that there will be no concurrent updates"

**Disagreement**: Production systems (Linear, Figma) use LWW successfully despite risks; mitigated by rarity of true conflicts in their domains

**Implication**: RaiSE can use LWW for backlog sync because:
- True concurrent edits to same field on same item are rare (single-user editing sessions)
- Can use server timestamp (not client clock) to avoid drift issues
- Can fall back to manual resolution for detected conflicts

---

### Claim 10: Background sync with offline queue enables optimistic UI updates and resilient write-back

**Confidence**: HIGH

**Evidence**:
1. [Linear Sync Engine](https://linear.app/now/scaling-the-linear-sync-engine) - "Data syncs in the background through the server in realtime; network layer not required for application to function"
2. [PowerSync](https://www.powersync.com) - "Background write-back; apps read and write data directly from local database, writes immediately trigger reactivity"
3. [SQLite Sync Engine Lessons](https://antoine.fi/sqlite-sync-engine-with-reactivity) - "Writes trigger reactivity so data is visible and components re-render instantly, while data syncs in background"
4. [Building Offline-First Applications](https://www.sqliteforum.com/p/building-offline-first-applications) - "Offline queue for operations when network unavailable; retry when connection restored"

**Disagreement**: None found

**Implication**: RaiSE should queue sync operations (create, update, delete) when offline and process queue in background when connected. UI updates immediately from local state.

---

## Patterns & Paradigm Shifts

### Pattern 1: Shift from Cloud-First to Local-First (2019-2025)

The industry has moved from cloud-centric (data in cloud, cache locally) to local-first (data local, sync to cloud). Evidence:

- **2019**: Ink & Switch coins "local-first" term and principles
- **2023**: Linear, Figma publish sync engine details showing local-first architecture
- **2024**: ElectricSQL, PowerSync, SQLiteSync emerge as sync layer products
- **2025**: Android guide states "offline-first is baseline expectation, not premium feature"

This shift is driven by:
- User expectation for instant responsiveness (no loading spinners)
- Unreliable networks (mobile, intermittent connectivity)
- Data ownership concerns (privacy, vendor lock-in)

### Pattern 2: CRDT Adoption Tempered by Pragmatism

CRDTs were hyped (2017-2020) as the solution for conflict-free sync, but production systems show selective adoption:

- **Full CRDT**: Yjs, Automerge for real-time text collaboration (Google Docs use case)
- **CRDT-inspired**: Figma uses LWW Register pattern with central ordering, not distributed CRDT
- **LWW Sufficient**: Linear, Cinapse found LWW adequate for their domains (task tracking, user preferences)
- **Hybrid**: CouchDB/PouchDB expose conflicts for manual resolution, don't auto-merge

**Implication**: Don't over-engineer conflict resolution. Match strategy to conflict frequency and consequences.

### Pattern 3: Delta Sync Convergence

Every major sync system uses incremental/delta sync, not full-state sync:

- **Sequence IDs**: CouchDB, Linear (monotonically increasing integers)
- **Timestamps**: PowerSync, AWS AppSync (last_modified watermarks)
- **Version Vectors**: Git (commit SHAs), CRDTs (version vectors)
- **Transaction Logs**: Netflix Delta (CDC from database logs)

**Implication**: Delta sync is non-negotiable for performance. Choose mechanism based on data model (sequence IDs for append-only, timestamps for mutable).

### Pattern 4: SQLite as Local-First Persistence Layer

SQLite has become the de facto standard for client-side persistence:

- **Native apps**: Direct SQLite (iOS, Android, desktop)
- **Web apps**: IndexedDB (similar capabilities, different API)
- **Cross-platform**: ElectricSQL, PowerSync provide SQLite sync layers
- **Extensions**: SQLiteSync adds CRDT support as extension

**Why SQLite won**:
- Embedded (no server process)
- Transactional (ACID guarantees)
- Queryable (full SQL)
- Ubiquitous (ships with every OS)

### Pattern 5: Centralized Ordering for Simplicity

Pure distributed CRDTs are complex; production systems often use central server for ordering:

- **Figma**: Central server assigns operation order, not pure CRDT
- **Linear**: Server increments global lastSyncId, deterministic ordering
- **ElectricSQL**: Postgres logical replication log provides total order

**Trade-off**: Requires server availability for sync (not pure peer-to-peer), but simplifies implementation and debugging.

---

## Gaps & Unknowns

### Gap 1: Token Efficiency in AI-Driven Sync

**What's missing**: No sources address LLM token costs in sync operations. Questions:
- How to minimize token usage when syncing to/from external systems via AI?
- What's the token overhead of conflict resolution prompts?
- Can delta sync reduce tokens by only sending changed fields?

**Why it matters**: RaiSE's AI-driven architecture makes token efficiency a first-class concern, unlike traditional sync systems.

**Recommendation**: Measure token costs empirically; optimize by sending minimal deltas and structured data (not prose).

### Gap 2: Backlog-Specific Sync Patterns

**What's missing**: Most sources focus on:
- Real-time collaboration (text editing, design tools)
- Database replication (Postgres, MongoDB)
- File sync (Dropbox, Google Drive)

Very little on task/issue/backlog sync patterns specifically.

**Why it matters**: Backlog items have different semantics than documents or database rows:
- Rich relationships (dependencies, parent/child, links)
- Status transitions (state machine)
- Multi-field updates with different merge strategies per field

**Recommendation**: Look to Linear's sync engine (task tracking) as closest analog; adapt 3-way merge per field type.

### Gap 3: Long-Term Schema Evolution in Sync

**What's missing**: How do sync systems handle:
- Adding/removing fields (schema migration)
- Breaking changes (incompatible versions)
- Clients on different schema versions syncing

**Why it matters**: RaiSE will evolve over time; sync protocol must handle mixed versions gracefully.

**Recommendation**: Research separately; likely requires versioned sync protocol with compatibility matrix.

### Gap 4: Security & Access Control in Sync

**What's missing**: Minimal coverage of:
- How to sync partial data based on user permissions (row-level security)
- End-to-end encryption in sync (local encryption, server can't read)
- Audit logs for sync operations (who changed what when)

**Why it matters**: Enterprise customers will require security controls on synced data.

**Recommendation**: Out of scope for initial implementation; revisit when adding team collaboration features.

### Gap 5: Quantitative Performance Benchmarks

**What's missing**: Very few sources provide hard numbers:
- Sync latency (p50, p99)
- Throughput (ops/sec)
- Memory overhead (CRDT metadata size)
- Network bandwidth (bytes per sync operation)

**Why it matters**: Can't make data-driven decisions without benchmarks.

**Recommendation**: Build micro-benchmarks for RaiSE sync; measure against known workloads (sync 100 items, 1000 items, etc.).

---

## Key Architectural Insights

### Insight 1: Local-First ≠ Offline-Only

Local-first doesn't mean no server; it means:
- Local is primary, server is secondary
- App works fully offline
- Server provides multi-device sync, collaboration, backup
- Eventual consistency between local and remote

### Insight 2: Sync Complexity is in Conflicts, Not Protocol

The hard part isn't the network protocol (HTTP + JSON works fine); it's:
- Detecting conflicts (comparing local vs remote state)
- Resolving conflicts (merge strategies)
- Presenting conflicts to users (when manual resolution needed)

### Insight 3: Simplicity Beats Correctness for Most Apps

Pure CRDTs guarantee convergence, but:
- Add memory overhead (metadata per element)
- Add complexity (non-trivial to implement)
- May be overkill if conflicts are rare

LWW + manual fallback works for many domains (task tracking, preferences, settings).

### Insight 4: Reactivity is Essential for Good UX

Local-first apps must:
- Update UI immediately from local state (optimistic updates)
- Show sync status (syncing, synced, offline)
- Handle background sync without blocking UI

Requires reactive data layer (MobX, SQLite triggers, BroadcastChannel).

### Insight 5: Delta Sync is Table Stakes

Full-state sync doesn't scale past toy apps. Every production system uses:
- Sequence IDs or timestamps to track "last synced"
- Send only changes since last sync
- Apply changes incrementally

---

## Recommendations for RaiSE

Based on triangulated evidence, here's what RaiSE should do:

### 1. Use Delta Sync with Sequence IDs

**Rationale**: Linear, CouchDB, and others prove this scales. More reliable than timestamps (no clock skew).

**Implementation**:
- Track `last_sync_id` per external system (Linear, Jira, GitHub)
- Server assigns monotonically increasing `sync_id` to each change
- Client requests changes since `last_sync_id`

### 2. Use Last-Write-Wins for Conflict Resolution

**Rationale**: Conflicts are rare in single-user task editing (like Linear). LWW is simple and sufficient.

**Implementation**:
- Use server timestamp (not client) to determine "last"
- Expose conflicts to user when detected (show both versions)
- Allow manual resolution in rare cases

### 3. Use 3-Way Merge for Field-Level Updates

**Rationale**: Git proves this works. Enables auto-merge when different fields modified.

**Implementation**:
- Store last-synced state as "base" for each item
- Compare local vs remote vs base
- Auto-merge non-overlapping changes (title vs description)
- Flag conflicts when same field changed locally and remotely

### 4. Implement Exponential Backoff with Jitter

**Rationale**: AWS, Better Stack, and others converge on this pattern for resilience.

**Implementation**:
```python
delay = min(base_delay * (2 ** retry_count), max_delay)
jitter = delay * random.uniform(0.75, 1.25)
sleep(jitter)
```

### 5. Use Background Queue for Offline Writes

**Rationale**: Linear, PowerSync show this enables optimistic UI and offline resilience.

**Implementation**:
- Queue sync operations (create, update, delete) in local DB
- Process queue in background when connected
- Retry with backoff on failure
- Show sync status in UI (pending, syncing, synced)

### 6. Keep SQLite as Local Store

**Rationale**: Industry standard; RaiSE already uses it. No need to change.

**Implementation**: No change needed.

### 7. Avoid Full CRDT Implementation

**Rationale**: Cinapse, Linear show simpler approaches work. CRDT overhead not justified for RaiSE use case.

**Implementation**: Use LWW + 3-way merge instead.

---

## Open Questions

1. **Which field merge strategy for each backlog item property?**
   - Title: 3-way merge (text)
   - Description: 3-way merge (text)
   - Status: Server wins (state machine constraints)
   - Labels: Set union (merge both)
   - Dependencies: Set union with validation (no cycles)

2. **How to handle deletes in sync?**
   - Tombstones (mark deleted, sync tombstone, garbage collect later)
   - Or immediate delete with conflict detection (if both sides modified before delete)

3. **What's the sync frequency?**
   - On-demand (user clicks "sync now")
   - Periodic (every N minutes when connected)
   - Real-time (WebSocket for immediate push)

4. **How to sync partial backlog (not all items)?**
   - Sync only items in active sprint? Or all items?
   - Sync only user's assigned items? Or team items?

**Recommendation**: Defer these decisions until story design phase; evidence provides framework but not specific answers.

---

**Synthesis Metadata**:
- Research date: 2026-02-14
- Evidence sources: 32
- Major claims: 10 (all HIGH or MEDIUM confidence)
- Patterns identified: 5
- Gaps identified: 5
- Researcher: Claude (Sonnet 4.5)
