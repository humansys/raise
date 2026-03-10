# Synthesis: Bidirectional Sync & Conflict Resolution

**Research Date**: 2026-02-14
**Researcher**: Claude Sonnet 4.5

---

## Major Claims (Triangulated)

### Claim 1: Three-Way Merge is the Production-Proven Standard for Backlog-Style Data

**Confidence**: HIGH

**Evidence**:
1. [The Magic of 3-Way Merge - Git Init](https://blog.git-init.com/the-magic-of-3-way-merge/) - Git uses three-way merge with common ancestor to auto-merge non-overlapping changes; battle-tested across millions of repos
2. [How to Resolve Merge Conflicts in Git | Atlassian](https://www.atlassian.com/git/tutorials/using-branches/merge-conflicts) - Official documentation validates three-way merge as foundational distributed collaboration pattern
3. [Two-way and three-way merges explained | Gearset](https://docs.gearset.com/en/articles/9325332-two-way-and-three-way-merges-explained) - Three-way merge "by far the better option" for change detection and intelligent conflict resolution

**Disagreement**: None found. Three-way merge is universally accepted as superior to two-way merge.

**Implication**: For RaiSE backlog sync (markdown + JSONL), three-way merge provides battle-tested conflict resolution without CRDT/OT complexity. Works well for document-style data with infrequent concurrent edits on same fields.

---

### Claim 2: CRDTs are Excellent for Real-Time Collaborative Editing but Overkill for Backlog Sync

**Confidence**: HIGH

**Evidence**:
1. [Diving into CRDTs | Redis](https://redis.io/blog/diving-into-crdts/) - CRDTs shine for "collaborative editing, chat, real-time competitive systems" where simultaneous character-level edits occur
2. [CRDTs vs. OT: How Google Docs Handles Collaborative Editing](https://systemdr.substack.com/p/crdts-vs-operational-transformation) - CRDT use cases are "co-editors, productivity tools, online auctions" requiring sub-second latency
3. [Why Cinapse Moved Away From CRDTs - PowerSync](https://www.powersync.com/blog/why-cinapse-moved-away-from-crdts-for-sync) - Company abandoned CRDTs due to complexity; "not worth the overhead" for their sync use case

**Disagreement**: Some sources (Redis, Ably) promote CRDTs broadly, but production case studies (Cinapse, Figma's rejection of full CRDT) show selective adoption.

**Implication**: RaiSE backlog doesn't need character-level conflict resolution. Stories/epics are coarse-grained entities with field-level updates, not real-time collaborative text editing. CRDT complexity unjustified.

---

### Claim 3: Dual Source of Truth Requires Entity Partitioning or Field-Level Ownership

**Confidence**: HIGH

**Evidence**:
1. [The Truth about Data Truth: SSoT vs MVoT - CSG Solutions](https://blog.csgsolutions.com/truth-data-truth-ssot-vs-mvot) - Multiple Versions of Truth (MVoT) is legitimate when "different systems own different aspects" of data
2. [Mastering the Dual: Strategic Data Synchronization](https://alok-mishra.com/2023/11/27/mastering-the-dual-strategic-data-synchronization-in-domain-api-architecture/) - Entity Partitioning strategy: "each system masters different stages" of lifecycle
3. [The Engineering Challenges of Bi-Directional Sync - StackSync](https://www.stacksync.com/blog/the-engineering-challenges-of-bi-directional-sync-why-two-one-way-pipelines-fail) - True bidirectional needs "unified transformation rules" and "shared state tracking" to prevent conflicts

**Disagreement**: None. All sources agree dual-truth requires clear ownership boundaries.

**Implication**: RaiSE should define explicit ownership:
- **Rai owns**: Workflow state (current_story, progress), task decomposition, learnings, session context
- **Team owns**: Assignments, comments, external status, time tracking
- **Shared**: Title, description (conflict resolution needed here)

---

### Claim 4: Offline-First Requires "Local-First, Sync-Later" with Pending Markers

**Confidence**: HIGH

**Evidence**:
1. [Offline-First Done Right: Sync Patterns - DevelopersVoice](https://developersvoice.com/blog/mobile/offline-first-sync-patterns/) - Pattern: "immediate local save + 'pending sync' marker + background queue"
2. [The Complete Guide to Offline-First Architecture in Android - droidcon](https://www.droidcon.com/2025/12/16/the-complete-guide-to-offline-first-architecture-in-android/) - "Local database is primary source of truth; network is optimization layer"
3. [Eventual Consistency - CouchDB Guide](https://guide.couchdb.org/editions/1/en/consistency.html) - Eventual consistency acceptable for offline scenarios: "all replicas converge if updates stop"

**Disagreement**: None. Consensus on local-first pattern for offline capability.

**Implication**: RaiSE CLI should:
1. Immediately write to local backlog.md + memory graph on changes
2. Mark entries with sync_status: "pending" | "synced" | "conflict"
3. Background process attempts sync when online
4. Eventual consistency acceptable (team doesn't need instant view of Rai's task decomposition)

---

### Claim 5: Hybrid Webhook + Polling is Standard for Heterogeneous Backend Integration

**Confidence**: HIGH

**Evidence**:
1. [Polling vs Webhooks: When to Use One Over the Other - Unified](https://unified.to/blog/polling_vs_webhooks_when_to_use_one_over_the_other) - "Many SaaS APIs either don't support webhooks or only for subset of objects"; hybrid common
2. [Webhook vs. API Polling in System Design - GeeksforGeeks](https://www.geeksforgeeks.org/system-design/webhook-vs-api-polling-in-system-design/) - "Systems combine both: webhooks for real-time events + periodic polling as backup to detect missed events"
3. [Comprehensive Guide to Webhooks and Event-Driven Architecture](https://apidog.com/blog/comprehensive-guide-to-webhooks-and-eda/) - Webhooks require "retry logic, HTTPS, HMAC signatures, at-least-once vs exactly-once semantics"

**Disagreement**: None. Universal agreement on hybrid approach.

**Implication**: RaiSE sync should:
- Use webhooks where available (JIRA, GitLab support them)
- Fall back to polling for limited backends (Odoo may not support all webhooks)
- Implement message queue (Redis/RabbitMQ) for reliable async processing
- Plan for webhook security (HMAC validation) and retry logic

---

### Claim 6: Last-Write-Wins is Simple but Loses Data; Vector Clocks Add Complexity

**Confidence**: MEDIUM

**Evidence**:
1. [Vector Clocks and Conflicting Data - DesignGurus](https://www.designgurus.io/course-play/grokking-the-advanced-system-design-interview/doc/vector-clocks-and-conflicting-data) - "LWW based on wall-clock can easily end up losing data"
2. [Vector Clocks in Distributed Systems - GeeksforGeeks](https://www.geeksforgeeks.org/computer-networks/vector-clocks-in-distributed-systems/) - "Vector clock size grows linearly with nodes; high overhead"
3. [Vector Clocks | Kevin Sookocheff](https://sookocheff.com/post/time/vector-clocks/) - Amazon Dynamo uses vector clocks (production validation)

**Disagreement**: Trade-off between simplicity (LWW) and correctness (vector clocks). No clear winner.

**Implication**: For RaiSE:
- LWW acceptable for fields where latest external value wins (e.g., assignee, external status)
- Three-way merge better than vector clocks for document-style backlog
- Vector clocks unnecessary complexity given infrequent concurrent edits

---

### Claim 7: Change Data Capture (CDC) + Message Queue is Core Pattern for Robust Sync

**Confidence**: HIGH

**Evidence**:
1. [Bidirectional Data Synchronization Patterns - Dev3lop](https://dev3lop.com/bidirectional-data-synchronization-patterns-between-systems/) - "Message queues (Kafka, RabbitMQ) essential for fault-tolerant sync"
2. [Building a Resilient Real-Time Data Sync Architecture - StackSync](https://www.stacksync.com/blog/building-a-resilient-real-time-data-sync-architecture-implementation-guide-for-technical-leaders) - "CDC for efficient synchronization; Write-Ahead Logs for consistency"
3. [Intro to Data Integration Patterns – Bi-Directional Sync | MuleSoft](https://blogs.mulesoft.com/api-integration/patterns/data-integration-patterns-bi-directional-sync/) - Core components: "Change Data Capture, conflict resolution, filtering, object mapping"

**Disagreement**: None. Industry standard pattern.

**Implication**: RaiSE should:
- Implement CDC on backlog.md + memory graph (file watchers or explicit change tracking)
- Queue sync events (Redis Streams or Python queue) for background processing
- Use Write-Ahead Log pattern (append-only memory graph JSONL already does this)

---

## Patterns & Paradigm Shifts

### Pattern 1: Simple Heuristics Over Complex Algorithms

**Observation**: Production systems (Linear, Notion, Figma) often reject pure CRDT/OT approaches in favor of simpler domain-specific heuristics.

**Sources**:
- [The Hard Things About Sync - Joy Gao](https://expertofobsolescence.substack.com/p/the-hard-things-about-sync) - "Figma rejected fully decentralized CRDTs"
- [Why Cinapse Moved Away From CRDTs - PowerSync](https://www.powersync.com/blog/why-cinapse-moved-away-from-crdts-for-sync) - Abandoned CRDTs for simpler sync

**Application**: RaiSE should prefer three-way merge + field-level LWW over CRDT libraries. Align with RaiSE Constitution Principle 11: "Simple heuristics over complex solutions."

---

### Pattern 2: Local-First with Eventual Consistency is New Standard

**Observation**: Modern apps (Linear, Notion, mobile apps) prioritize local responsiveness over strong consistency.

**Sources**:
- [Offline-First Done Right - DevelopersVoice](https://developersvoice.com/blog/mobile/offline-first-sync-patterns/)
- [The Hard Things About Sync - Joy Gao](https://expertofobsolescence.substack.com/p/the-hard-things-about-sync) - Linear uses "local-first with client-side storage"

**Application**: RaiSE CLI should write to local backlog.md immediately, sync asynchronously. Team sees Rai's state with delay (acceptable).

---

### Pattern 3: Hub-and-Spoke for Multi-System Sync

**Observation**: When syncing 3+ systems, centralized hub beats peer-to-peer.

**Sources**:
- [Bidirectional Data Synchronization Patterns - Dev3lop](https://dev3lop.com/bidirectional-data-synchronization-patterns-between-systems/) - "Hub-and-spoke architecture where one system acts as hub"
- [The Engineering Challenges of Bi-Directional Sync - StackSync](https://www.stacksync.com/blog/the-engineering-challenges-of-bi-directional-sync-why-two-one-way-pipelines-fail) - "Centralized change detection, unified transformation rules"

**Application**: RaiSE memory graph should be the hub:
- JIRA ↔ RaiSE ↔ GitLab ↔ Odoo (not JIRA ↔ GitLab direct)
- Simplifies transformation logic and conflict resolution

---

### Pattern 4: Conflict Resolution is Domain-Specific

**Observation**: No one-size-fits-all conflict strategy. Field-level decisions based on semantics.

**Sources**:
- [Mastering the Dual: Strategic Data Synchronization](https://alok-mishra.com/2023/11/27/mastering-the-dual-strategic-data-synchronization-in-domain-api-architecture/) - Entity partitioning by lifecycle stage
- [Intro to Data Integration Patterns – Bi-Directional Sync | MuleSoft](https://blogs.mulesoft.com/api-integration/patterns/data-integration-patterns-bi-directional-sync/) - "Filtering and object mapping critical"

**Application**: RaiSE needs field-level conflict strategy matrix:

| Field | Strategy | Reason |
|-------|----------|--------|
| `title` | Three-way merge | Both sides edit; merge intelligently |
| `description` | Three-way merge | Collaborative field |
| `status` (external) | LWW from external | Team owns workflow |
| `current_story` | LWW from Rai | Rai owns internal workflow |
| `assignee` | LWW from external | Team owns assignment |
| `tasks` | Rai-only (no sync) | Internal decomposition |
| `learnings` | Rai-only (no sync) | Internal knowledge capture |
| `comments` | Append-only sync | Never conflict (just merge lists) |

---

## Gaps & Unknowns

### Gap 1: Markdown Three-Way Merge Libraries

**Question**: What Python libraries exist for three-way merge of Markdown files?

**Status**: Not found in research. Git does line-based merge, but semantic Markdown merge (respecting structure) may need custom implementation or Git subprocess.

**Next Step**: Research Python libraries: `python-diff-match-patch`, `diff3`, or subprocess to `git merge-file`.

---

### Gap 2: JIRA/GitLab/Odoo Webhook Coverage

**Question**: Which specific entities support webhooks in each backend?

**Status**: General sources confirm webhooks exist, but granular API coverage not documented in research.

**Next Step**: Review official API docs:
- JIRA: [Atlassian webhooks](https://developer.atlassian.com/server/jira/platform/webhooks/)
- GitLab: [GitLab webhooks](https://docs.gitlab.com/ee/user/project/integrations/webhooks.html)
- Odoo: [Odoo webhooks](https://www.odoo.com/documentation/)

---

### Gap 3: Conflict Rate Estimation

**Question**: How often do conflicts actually occur in backlog-style sync?

**Status**: No empirical data found on conflict frequency for issue tracker bidirectional sync.

**Next Step**: Assume low conflict rate (developers rarely edit same issue field simultaneously). Monitor in production; optimize if conflicts become frequent.

---

### Gap 4: Performance at Scale

**Question**: How does sync perform with 1000+ backlog items across multiple backends?

**Status**: Sources discuss general scalability (CRDTs have overhead, polling is inefficient), but no specific benchmarks for issue sync.

**Next Step**: Prototype MVP with small dataset; measure latency and resource usage before scaling to 1000+ items.

---

## Key Takeaways for RaiSE

1. **Use three-way merge** for backlog.md conflicts (proven, simple, Git-compatible)
2. **Avoid CRDTs/OT** - overkill for coarse-grained backlog entities
3. **Local-first + eventual consistency** - write immediately to local, sync async
4. **Field-level ownership** - clear boundaries between Rai-owned and team-owned fields
5. **Hybrid webhook + polling** - webhooks where supported, polling as fallback
6. **Hub-and-spoke** - memory graph as central hub for all backends
7. **CDC + message queue** - file watchers + Redis/queue for reliable async sync
8. **Simple heuristics** - LWW for team-owned fields, three-way for collaborative fields

---

## References

See [Evidence Catalog](sources/evidence-catalog.md) for full source list.
