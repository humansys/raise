# Recommendation: RaiSE Backlog Sync Strategy

Research date: 2026-02-14
Based on: 32 sources, 10 triangulated claims (see synthesis.md)

---

## Decision

**Implement a local-first delta sync architecture using sequence IDs, Last-Write-Wins conflict resolution with 3-way merge fallback, exponential backoff retry policy, and background offline queue.**

**Confidence**: HIGH

---

## Rationale

This recommendation is based on convergent evidence from production systems (Linear, Figma, CouchDB/PouchDB, ElectricSQL, PowerSync) and foundational research (Ink & Switch, IEEE, CAP theorem).

### Why Local-First?

**Evidence**: 8 sources converge on local-first architecture (S01, S02, S07, S09, S11, S13, S14, S24)

- **Local is source of truth**: RaiSE's SQLite backlog is primary; external systems (Linear, Jira, GitHub) are secondary collaboration layer
- **Eventual consistency**: Accept temporary divergence; guarantee convergence when connected (CAP theorem: choose Availability + Partition Tolerance over immediate Consistency)
- **Offline resilience**: App works fully offline; sync happens in background when connected

**Aligns with**: RaiSE's design constraint (local backlog always queryable, token-efficient, fast)

### Why Delta Sync?

**Evidence**: 5 sources converge on delta sync (S02, S09, S16, S23, S30)

- **Performance**: Only sync changed items since last sync, not full state (bandwidth, latency, token efficiency)
- **Scalability**: Linear, Netflix, CouchDB use this at production scale
- **Mechanism**: Use sequence IDs (monotonically increasing integers) per external system

**Alternative considered**: Timestamp-based sync (PowerSync, AWS AppSync)
**Why not**: Sequence IDs avoid clock synchronization issues; more reliable

### Why Last-Write-Wins?

**Evidence**: 3 sources show LWW works for task tracking (S09, S11, S26)

- **Conflict rarity**: Linear states "conflicts are actually not that common" in task tracking (similar domain to RaiSE)
- **Simplicity**: LWW is trivial to implement; CRDTs add complexity without benefit for this use case
- **Pragmatism**: Cinapse moved away from CRDTs; LWW was sufficient

**Risk mitigation**: Use server timestamp (not client) to avoid clock drift; expose conflicts to user when detected

### Why 3-Way Merge for Fields?

**Evidence**: 4 sources prove 3-way merge works (S05, Git sources)

- **Auto-merge**: Different fields on same item can auto-merge (title vs description)
- **Proven**: Git uses this for billions of merge operations; extremely robust
- **Common ancestor**: Use last-synced state as merge base

**Fallback**: If same field changed locally and remotely, use LWW or prompt user

### Why Exponential Backoff?

**Evidence**: 5 sources converge on exponential backoff with jitter (S15, S21, S29, GeeksforGeeks, HackerOne)

- **Resilience**: Retries handle transient failures (network blips, API rate limits)
- **Load reduction**: Exponential delay prevents thundering herd
- **Jitter**: Randomness prevents synchronized retries across clients

**Formula**: `delay = min(base_delay * (2 ** retry_count), max_delay) * jitter`
**Parameters**: base_delay=2s, max_delay=5min, jitter=random(0.75, 1.25)

### Why Background Offline Queue?

**Evidence**: 4 sources show this pattern (S09, S14, S20, S23)

- **Optimistic UI**: Local writes succeed immediately; sync happens asynchronously
- **Offline work**: Queue operations when offline; process when connected
- **User experience**: No blocking; user sees instant updates

**Implementation**: Queue sync operations (create, update, delete) in SQLite; background worker processes queue

---

## Trade-offs

What we're accepting/sacrificing with this choice:

### 1. Eventual Consistency (not Strong Consistency)

**Accept**: Temporary divergence between local and remote
**Sacrifice**: Immediate consistency guarantees
**Why OK**: RaiSE is single-user tool with occasional team sync; eventual consistency is acceptable (CAP theorem: AP over C)

### 2. Last-Write-Wins (not CRDTs)

**Accept**: Potential data loss on true concurrent edits
**Sacrifice**: Automatic conflict-free resolution guarantees
**Why OK**: Conflicts are rare in task tracking (Linear's experience); LWW simplicity outweighs CRDT complexity for this domain

### 3. Sequence IDs (not Timestamps)

**Accept**: Must maintain per-system sequence ID watermarks
**Sacrifice**: Slightly more complex state tracking than single global timestamp
**Why OK**: More reliable than timestamps (no clock skew); worth the extra state

### 4. Background Sync (not Real-Time)

**Accept**: Not instant push to collaborators; sync happens periodically or on-demand
**Sacrifice**: Real-time collaboration (Google Docs-style)
**Why OK**: RaiSE is not a real-time collaboration tool; eventual sync is sufficient

### 5. No End-to-End Encryption (Initial)

**Accept**: Synced data visible to external system servers (Linear, Jira, GitHub)
**Sacrifice**: Maximum privacy (local-only)
**Why OK**: External systems already require API access; E2E encryption can be added later if needed

---

## Risks

What could go wrong:

### Risk 1: Conflict Frequency Higher Than Expected

**What if**: Conflicts are more common than Linear's experience (multiple team members editing same item concurrently)

**Likelihood**: LOW (RaiSE is primarily single-user tool; team sync is secondary use case)

**Impact**: MEDIUM (data loss if LWW discards changes)

**Mitigation**:
- Detect conflicts (compare last-synced vs local vs remote)
- Expose conflicts to user with manual resolution UI
- Log conflict rate; if high, upgrade to 3-way merge or CRDTs

### Risk 2: External API Rate Limits

**What if**: External systems (Linear, Jira, GitHub) rate-limit sync requests

**Likelihood**: MEDIUM (all APIs have rate limits)

**Impact**: MEDIUM (sync delays, user frustration)

**Mitigation**:
- Exponential backoff automatically reduces request rate
- Batch sync operations (sync N items per request, not 1)
- Respect rate limit headers (X-RateLimit-Remaining)
- Show sync status in UI (rate limited, retrying in X seconds)

### Risk 3: Token Cost Explosion

**What if**: Sync operations consume excessive LLM tokens (AI-driven field mapping, conflict resolution prompts)

**Likelihood**: MEDIUM (unique to AI-driven architecture)

**Impact**: HIGH (cost, performance)

**Mitigation**:
- Use structured data (JSON) for sync, not prose (minimize tokens)
- Pre-define field mappings (RaiSE field → Linear field) without AI
- Use AI only for ambiguous mappings or conflict resolution
- Monitor token usage; optimize prompts

### Risk 4: Schema Evolution Breaks Sync

**What if**: RaiSE schema changes (add field, remove field, rename field) break sync with external systems

**Likelihood**: HIGH (schemas will evolve)

**Impact**: HIGH (sync failures, data loss)

**Mitigation**:
- Version sync protocol (v1, v2, etc.)
- Support multiple schema versions simultaneously (backward compatibility)
- Graceful degradation (ignore unknown fields, provide defaults for missing fields)
- Test schema migration with real data before release

### Risk 5: Offline Queue Grows Unbounded

**What if**: User works offline for extended period; queue grows to thousands of operations

**Likelihood**: MEDIUM (possible for heavy offline usage)

**Impact**: MEDIUM (memory, performance, sync delay when reconnected)

**Mitigation**:
- Compact queue (merge consecutive updates to same item into single operation)
- Set queue size limit (warn user if exceeding, e.g., 1000 ops)
- Batch processing (sync N ops at a time, not all at once)
- Show queue size in UI (X items pending sync)

---

## Mitigations Summary

| Risk | Mitigation Strategy |
|------|---------------------|
| High conflict frequency | Detect + expose conflicts to user; log rate; upgrade to CRDT if needed |
| API rate limits | Exponential backoff, batching, respect headers, UI feedback |
| Token cost explosion | Structured data, pre-defined mappings, minimize AI usage, monitor |
| Schema evolution | Versioned protocol, backward compatibility, graceful degradation |
| Unbounded offline queue | Queue compaction, size limits, batching, UI feedback |

---

## Alternatives Considered

### Alternative 1: Full CRDT Implementation (Yjs, Automerge)

**Why not**:
- **Complexity**: CRDTs are non-trivial to implement correctly; high learning curve
- **Overhead**: Memory metadata (version vectors, tombstones); network overhead (sync metadata)
- **Overkill**: Cinapse found CRDTs unnecessary for their use case (similar to RaiSE)
- **Evidence**: S06, S17, S18, S19, S26

**When to reconsider**: If conflict rate is high (>5% of syncs) and manual resolution is painful

### Alternative 2: Operational Transformation (OT)

**Why not**:
- **Complexity**: Even more complex than CRDTs; Figma explicitly avoided OT
- **Server dependency**: Requires central server for operation ordering (though RaiSE has server anyway)
- **No performance benefit**: OT solves real-time text editing (not RaiSE's use case)
- **Evidence**: S11 (Figma avoided OT)

**When to reconsider**: Never (not applicable to task tracking)

### Alternative 3: Full-State Sync (Send Entire Backlog)

**Why not**:
- **Performance**: Doesn't scale; network bandwidth, API rate limits, token costs
- **No production examples**: Every major system uses delta sync
- **Evidence**: S02, S09, S16, S23, S30 (all use delta sync)

**When to reconsider**: Never (fundamentally doesn't scale)

### Alternative 4: Timestamp-Based Delta Sync

**Why not**:
- **Clock skew**: Client clocks drift; server clocks may not be synchronized
- **Unreliable**: Sequence IDs are deterministic; timestamps are not
- **Evidence**: S09 (Linear uses sequence IDs), S02 (CouchDB uses sequence IDs)

**When to reconsider**: If external system doesn't support sequence IDs (then use timestamps as fallback)

### Alternative 5: Real-Time WebSocket Sync

**Why not**:
- **Overkill**: RaiSE doesn't need real-time collaboration (not Google Docs)
- **Complexity**: Requires persistent connections, reconnection logic, server infrastructure
- **Cost**: WebSocket servers are more expensive than HTTP APIs
- **Evidence**: S09 (Linear uses WebSockets but RaiSE doesn't need real-time)

**When to reconsider**: If adding real-time team collaboration feature

---

## Implementation Roadmap

Phased approach to reduce risk:

### Phase 1: Foundation (MVP)
- Delta sync with sequence IDs (per external system)
- LWW conflict resolution (server timestamp)
- Exponential backoff retry (base=2s, max=5min, jitter=±25%)
- Background offline queue (SQLite table)
- Basic UI feedback (sync status: syncing, synced, offline, error)

**Deliverable**: One-way sync (RaiSE → Linear) for create operations only

### Phase 2: Bidirectional Sync
- Sync from external system → RaiSE (poll periodically)
- 3-way merge for field-level updates
- Conflict detection + logging
- Update and delete operations (not just create)

**Deliverable**: Full bidirectional sync with Linear

### Phase 3: Multi-System Support
- Abstract sync layer (support Linear, Jira, GitHub)
- Per-system field mappings (RaiSE fields ↔ external fields)
- Per-system sequence ID tracking

**Deliverable**: Sync with 3 external systems

### Phase 4: Advanced Features
- Conflict resolution UI (show both versions, let user choose)
- Queue compaction (merge consecutive updates)
- Partial sync (only active items, only assigned items)
- Schema versioning (forward/backward compatibility)

**Deliverable**: Production-ready sync with conflict handling

### Phase 5: Optimization
- Token usage optimization (structured data, minimal AI)
- Batch operations (sync N items per request)
- Metrics + monitoring (conflict rate, token cost, sync latency)
- Performance benchmarks (100 items, 1000 items, 10k items)

**Deliverable**: Optimized sync with <1s latency, <$0.01 token cost per 100 items

---

## Success Metrics

How to measure if this works:

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Zero data loss** | 0 confirmed data loss incidents | User reports, automated testing |
| **Sync success rate** | >99% (excl. rate limits) | Log success/failure ratio |
| **Conflict rate** | <5% of sync operations | Log conflicts / total syncs |
| **Sync latency** | <1s p95 for 100 items | Client-side timing |
| **Token cost** | <$0.01 per 100 items synced | Track token usage per sync |
| **Offline queue size** | <1000 ops p95 | Track queue length |
| **User satisfaction** | >4/5 on sync reliability | User surveys |

---

## Next Steps

1. **Create ADR**: Document this decision in `decisions/adr-NNN-backlog-sync-strategy.md`
2. **Design story**: Use /rai-story-design to create detailed spec for Phase 1
3. **Spike**: Build proof-of-concept for Linear sync (one-way create) to validate assumptions
4. **Measure**: Instrument token usage, latency, conflict rate in POC
5. **Iterate**: Refine approach based on POC learnings

---

## References

- Evidence catalog: `sources/evidence-catalog.md` (32 sources)
- Synthesis: `synthesis.md` (10 triangulated claims, 5 patterns)
- Research scope: `research-scope.md`

---

**Recommendation Metadata**:
- Decision: Local-first delta sync with LWW + 3-way merge
- Confidence: HIGH
- Rationale: Convergent evidence from 8 production systems + academic research
- Trade-offs: Eventual consistency, LWW risks, no real-time
- Risks: 5 identified with mitigations
- Alternatives: 5 considered and rejected
- Implementation: 5 phases (MVP → Production → Optimization)
- Success metrics: 7 defined
- Research date: 2026-02-14
- Researcher: Claude (Sonnet 4.5)
