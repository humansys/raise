# Research Summary: Sync Trigger Patterns

**Session**: 2026-02-14
**Skill**: /rai-research
**Status**: Complete
**Governance Link**: Parking Lot → "E-NEXT: Backlog Abstraction Layer (RaiSE PRO)"

---

## Context

RaiSE is designing backlog synchronization between:
- **Local unified graph** (raise memory)
- **External issue trackers** (Jira, Linear, GitHub Issues)

This research investigates when and how production engineering tools trigger sync, and what patterns apply to RaiSE.

---

## Research Question

**Primary**: When and how do engineering tools trigger synchronization between systems?

**Secondary**:
- What are the architectural patterns for sync triggers (manual, event-driven, scheduled, hybrid)?
- What are the latency vs reliability tradeoffs?
- How do production systems handle sync failures, retries, and eventual consistency?

---

## Key Finding

Production systems overwhelmingly adopt **hybrid sync architectures**:
1. **Webhooks** for low latency (fast path)
2. **Reconciliation** for reliability (slow path)
3. **Manual commands** for user control (escape hatch)

They explicitly accept **eventual consistency** (seconds to minutes delay) over strong consistency.

**Evidence Strength**: HIGH (30+ sources, triangulated claims)

---

## Recommendation for RaiSE

### Three-Tier Hybrid Sync Strategy

**Tier 1: Manual Commands (MVP)**
```bash
rai backlog sync --provider linear --direction pull
```
- User control, simple implementation
- No infrastructure required (no webhooks, no background jobs)
- Aligns with CLI-first, HITL philosophy

**Tier 2: Lifecycle Event Triggers (v2.1)**
- Automatic sync at epic start/close
- Natural boundaries for sync (already commits)
- Conditional on `backlog_sync_enabled` config

**Tier 3: Periodic Reconciliation (Future)**
- Optional drift detection
- Recovery from missed events
- Conflict resolution UX

---

## Trade-offs

### Accepting
✅ Eventual consistency (not real-time)
✅ Manual as primary (user control)
✅ Simple implementation (no webhook infrastructure)
✅ Unidirectional first (pull OR push, not both)

### Rejecting
❌ Webhook-only (reliability issues, GitHub has no retries)
❌ Polling-only (resource waste, latency)
❌ Strong consistency (CAP theorem, unnecessary)

---

## Critical Findings

1. **Hybrid is Production Standard** - Webhooks + reconciliation + manual
2. **Eventual Consistency Acceptable** - Seconds to minutes delay OK for backlog sync
3. **Lifecycle Events as Sync Points** - Issue creation, epic close (not continuous)
4. **Retry Strategies Established** - Exponential backoff + jitter, 3-7 retries, 1-3 days
5. **GitHub Webhooks Limited** - No retries, 10s timeout, need polling fallback

---

## Governance Linkage

### Related Items

**Parking Lot**:
- **E-NEXT: Backlog Abstraction Layer (RaiSE PRO)** - This research informs sync trigger design
- **Deterministic backlog sync via CLI** - Internal backlog sync (governance/backlog.md)

**Epics**:
- **E21: Platform Integration** (Planning, P1 for V3) - External tracker integrations

**ADRs**: None yet (recommendation: create ADR when implementing Tier 1)

---

## Next Steps

1. **Validate recommendation** with Emilio (alignment check)
2. **Design sync command UX** (flags, provider selection, output format)
3. **Implement Tier 1 MVP** (manual `rai backlog sync`)
4. **Create ADR** (document architectural decision)
5. **Test with Linear** (first provider, simpler API)

---

## Research Artifacts

All artifacts in `/home/emilio/Code/raise-commons/work/research/sync-trigger-patterns/`:

- **README.md** - 15-minute overview with navigation
- **executive-summary.md** - 5-minute stakeholder summary
- **sync-trigger-patterns-report.md** - Complete report (8 findings, patterns, gaps, recommendations)
- **sources/evidence-catalog.md** - 30+ sources with ratings and relevance
- **prompt.md** - Research prompt (reproducibility)

---

## Evidence Summary

**Sources**: 30+ consulted
**Evidence Levels**:
- Very High: 5 (official docs: Linear, Azure, ACM, IBM, Airbyte)
- High: 14 (production blogs, GitHub, integration platforms)
- Medium: 11 (community-validated approaches)
- Low: 0

**Triangulation**: Major claims supported by 3+ independent sources

---

## Key Sources

### Production Integration Patterns
- [Linear-Jira Integration](https://linear.app/docs/jira) - Webhook-driven bidirectional sync
- [GitHub-Jira Sync](https://github.com/canonical/sync-issues-github-jira) - Event-driven lifecycle triggers
- [GitOps Patterns](https://codefresh.io/blog/gitops-patterns-auto-sync-vs-manual-sync/) - Auto-sync + manual control

### Architecture Patterns
- [Merge.dev: Webhooks vs Polling](https://www.merge.dev/blog/webhooks-vs-polling) - Hybrid as pragmatic pattern
- [Hookdeck: GitHub Webhooks](https://hookdeck.com/webhooks/platforms/guide-github-webhooks-features-and-best-practices) - GitHub limitations
- [StackSync: Bi-Directional Sync](https://www.stacksync.com/blog/the-engineering-challenges-of-bi-directional-sync-why-two-one-way-pipelines-fail) - CAP theorem constraints

### Retry and Reliability
- [Hookdeck: Webhook Retry](https://hookdeck.com/webhooks/guides/webhook-retry-best-practices) - Exponential backoff, jitter
- [Azure: Compensating Transaction](https://learn.microsoft.com/en-us/azure/architecture/patterns/compensating-transaction) - Retry strategies
- [System Design School: Anti-Entropy](https://systemdesignschool.io/blog/anti-entropy) - Reconciliation mechanisms

---

*Research conducted using epistemologically rigorous methodology (/rai-research skill)*
*Triangulated claims, explicit confidence levels, contrary evidence acknowledged*
