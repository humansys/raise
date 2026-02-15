# Research: Bidirectional Sync & Conflict Resolution

**Research Date**: 2026-02-14
**Researcher**: Claude Sonnet 4.5 (via `/rai-research` skill)
**Status**: Complete
**Confidence**: HIGH

---

## Quick Navigation

**15-Minute Overview**: Read this README
**Full Report**: [recommendation.md](recommendation.md) (15-20 min)
**Detailed Findings**: [synthesis.md](synthesis.md) (30 min)
**All Sources**: [sources/evidence-catalog.md](sources/evidence-catalog.md) (reference)

---

## Research Question

**Primary**: What are production-proven patterns for bidirectional synchronization between heterogeneous systems with dual-truth ownership?

**Context**: Designing sync architecture for RaiSE's local backlog (governance/backlog.md + memory graph) with external backends (JIRA, GitLab, Odoo). Local is source of truth for Rai workflows, external is source of truth for team collaboration.

---

## Key Findings (15-Minute Version)

### 1. Use Three-Way Merge, Not CRDTs

**Finding**: CRDTs (Conflict-Free Replicated Data Types) are excellent for real-time collaborative text editing (Google Docs, Figma), but overkill for backlog sync.

**Evidence**:
- Git's three-way merge is battle-tested across millions of repos
- Production companies (Cinapse, even Figma) abandon or limit CRDT use due to complexity
- RaiSE backlog has coarse-grained entities (stories, epics), not character-level edits

**Recommendation**: Use Git's three-way merge algorithm for `title` and `description` fields where both Rai and team may edit.

**Sources**: 7 sources (Very High to High evidence)

---

### 2. Local-First + Eventual Consistency

**Finding**: Modern apps (Linear, Notion) prioritize local responsiveness over strong consistency.

**Pattern**: "Local-first, sync-later"
1. Write changes to local backlog.md immediately
2. Mark with `sync_status: pending`
3. Background process syncs when online
4. Team sees Rai's state with acceptable delay (seconds to minutes)

**Recommendation**: RaiSE CLI should never block on network calls during story operations.

**Sources**: 5 sources (High evidence)

---

### 3. Field-Level Ownership, Not Single Master

**Finding**: Dual source of truth is valid when different systems own different aspects of data.

**Ownership Matrix**:

| Field | Owner | Conflict Strategy | Reason |
|-------|-------|-------------------|--------|
| `title`, `description` | Both | Three-way merge | Collaborative fields |
| `assignee`, `external_status` | Team | LWW (external wins) | Team owns collaboration |
| `current_story`, `progress` | Rai | LWW (Rai wins) | Rai owns workflow |
| `tasks`, `learnings` | Rai | No sync (local only) | Internal to Rai |
| `comments`, `attachments` | Both | Append-only | Never conflict |

**Recommendation**: Define explicit ownership boundaries to prevent silent data overwrites.

**Sources**: 4 sources (High evidence)

---

### 4. Hub-and-Spoke Topology

**Finding**: When syncing 3+ systems, centralized hub beats peer-to-peer.

**Architecture**: RaiSE memory graph as hub
- JIRA ↔ RaiSE ↔ GitLab ↔ Odoo (not JIRA ↔ GitLab direct)
- Simplifies transformation logic (single place for business rules)
- Prevents N×(N-1) integration explosion

**Recommendation**: Memory graph is canonical source; all backends sync through it.

**Sources**: 3 sources (High to Medium evidence)

---

### 5. Hybrid Webhooks + Polling

**Finding**: Real-world integrations combine both techniques.

**Pattern**:
- Use webhooks where available (JIRA, GitLab support them)
- Fall back to polling for limited backends (Odoo may not support all entities)
- Polling as backup catches missed webhook events

**Infrastructure**: Message queue (Redis Streams or RabbitMQ) for reliable async processing

**Recommendation**: Start with polling MVP, add webhooks incrementally.

**Sources**: 5 sources (High evidence)

---

## Decision

**Implement a Local-First, Hub-and-Spoke Bidirectional Sync Architecture with Three-Way Merge and Field-Level Ownership.**

See [recommendation.md](recommendation.md) for full rationale, trade-offs, risks, and implementation guidance.

---

## Evidence Summary

- **Total Sources**: 28
- **Evidence Distribution**: Very High (25%), High (39%), Medium (29%), Low (7%)
- **Triangulation**: All major claims have 3+ independent sources
- **Confidence**: HIGH (convergent evidence, no significant contrary findings)

---

## Major Claims (Triangulated)

1. **Three-Way Merge is Production Standard** (HIGH confidence, 3 sources)
2. **CRDTs Overkill for Backlog Sync** (HIGH confidence, 3 sources)
3. **Dual Source of Truth Requires Field Ownership** (HIGH confidence, 3 sources)
4. **Offline-First Needs Local-First Pattern** (HIGH confidence, 3 sources)
5. **Hybrid Webhook + Polling is Standard** (HIGH confidence, 3 sources)
6. **LWW Loses Data; Vector Clocks Add Complexity** (MEDIUM confidence, 3 sources)
7. **CDC + Message Queue Core Pattern** (HIGH confidence, 3 sources)

See [synthesis.md](synthesis.md) for detailed evidence and implications.

---

## Patterns Identified

1. **Simple Heuristics Over Complex Algorithms** - Production systems reject pure CRDT/OT for domain-specific solutions
2. **Local-First with Eventual Consistency** - Modern standard for offline-capable apps
3. **Hub-and-Spoke for Multi-System Sync** - Centralized hub when syncing 3+ systems
4. **Conflict Resolution is Domain-Specific** - Field-level strategies based on semantics

---

## Gaps & Next Steps

### Gaps Identified

1. **Python Markdown three-way merge libraries** - Need to research or use Git subprocess
2. **JIRA/GitLab/Odoo webhook coverage** - Review official API docs for entity-level support
3. **Conflict rate estimation** - No empirical data; monitor in production
4. **Performance at scale** - Prototype needed for 1000+ item benchmarks

### Next Steps

1. **Create ADR**: Document decision in `architecture/decisions/ADR-XXX-backlog-sync.md`
2. **Create Story**: S2.XX for local-first sync foundation (Phase 1)
3. **Prototype**: Git subprocess three-way merge PoC
4. **API Review**: Check webhook support for backlog entities

---

## Implementation Phases

### Phase 1: Local-First Foundation (MVP)
- CLI writes to local backlog.md with sync_status markers
- File watchers + background queue
- **Validation**: Offline operations work

### Phase 2: Single Backend Sync (JIRA)
- JIRA REST API adapter
- Webhook receiver
- Three-way merge implementation
- **Validation**: Bidirectional sync with JIRA

### Phase 3: Multi-Backend (GitLab, Odoo)
- Generic BackendAdapter interface
- Polling fallback
- Hub-and-spoke topology
- **Validation**: Sync across all 3 backends

### Phase 4: Production Hardening
- Idempotent operations
- Exponential backoff
- Conflict monitoring
- Batch API calls
- **Validation**: 1000+ items in <30s, <5% conflict rate

---

## Research Metadata

**Tool Used**: WebSearch (Claude Code built-in)
**Search Date**: 2026-02-14
**Prompt Version**: 1.0 (research-prompt-template.md)
**Total Searches**: 13
**Total Sources**: 28
**Research Time**: ~4 hours (standard depth)

---

## Quality Checklist

- [x] Research question is specific and falsifiable
- [x] Decision context clearly stated (ADR for RaiSE backlog sync)
- [x] Minimum source count met (28 sources, target 15-30 for standard depth)
- [x] Mix of academic, official, and practitioner sources
- [x] Major claims triangulated (3+ sources each)
- [x] Confidence levels explicitly stated
- [x] Contrary evidence acknowledged (CRDT abandonment cases)
- [x] Gaps and unknowns documented
- [x] Recommendation is specific and actionable
- [x] Trade-offs explicitly acknowledged
- [x] Risks identified with mitigations
- [x] All sources cited with URLs
- [x] Reproducibility metadata included

---

## References

**Key Sources**:
- [Martin Fowler: Patterns of Distributed Systems](https://martinfowler.com/articles/patterns-of-distributed-systems/) (Very High)
- [Atlassian: How to Resolve Merge Conflicts in Git](https://www.atlassian.com/git/tutorials/using-branches/merge-conflicts) (Very High)
- [The Hard Things About Sync - Joy Gao](https://expertofobsolescence.substack.com/p/the-hard-things-about-sync) (High)
- [Why Cinapse Moved Away From CRDTs](https://www.powersync.com/blog/why-cinapse-moved-away-from-crdts-for-sync) (High)
- [Offline-First Sync Patterns - DevelopersVoice](https://developersvoice.com/blog/mobile/offline-first-sync-patterns/) (High)

**Full Catalog**: [sources/evidence-catalog.md](sources/evidence-catalog.md)
