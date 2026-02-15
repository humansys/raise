# Sync Trigger Patterns Research

**Research Question**: When and how do engineering tools trigger synchronization between systems?

**Status**: Complete
**Date**: 2026-02-14
**Confidence**: HIGH

---

## Quick Navigation

### 15-Minute Overview
Read this file + [Executive Summary](#executive-summary) below.

### Full Research Report
[sync-trigger-patterns-report.md](sync-trigger-patterns-report.md) - Complete findings, evidence, and recommendations

### Evidence Catalog
[sources/evidence-catalog.md](sources/evidence-catalog.md) - 30+ sources with ratings and relevance

---

## Executive Summary

### Key Finding

Production systems overwhelmingly adopt **hybrid sync architectures** that combine:
1. **Event-driven webhooks** for low latency
2. **Periodic reconciliation** for reliability
3. **Manual commands** for user control

They explicitly accept **eventual consistency** over strong consistency.

### Recommendation for RaiSE

Implement a **three-tier hybrid sync strategy**:

**Tier 1: Manual Commands (MVP)**
```bash
rai backlog sync --provider linear --direction pull
```
- Full user control
- Simple implementation
- No infrastructure required
- Aligns with CLI-first philosophy

**Tier 2: Lifecycle Event Triggers (v2.1)**
- Automatic sync at epic start/close
- Natural boundaries for sync
- Conditional on config (`backlog_sync_enabled`)

**Tier 3: Periodic Reconciliation (Future)**
- Optional drift detection
- Recovery from missed events
- Conflict resolution UX

### Evidence Strength

- **30+ sources** consulted
- **5 Very High** evidence sources (official docs, Azure, ACM, IBM)
- **14 High** evidence sources (production integration blogs, GitHub)
- **Major claims triangulated** with 3+ independent sources

### Key Patterns Discovered

1. **Hybrid is Production Standard** - Pure webhook or pure polling rare in production
2. **Lifecycle Events as Sync Boundaries** - Sync at meaningful points (issue creation, epic close), not continuous
3. **Eventual Consistency Acceptable** - Seconds to minutes delay acceptable for backlog sync
4. **Reliability Through Redundancy** - Layer multiple mechanisms with different failure modes

### Critical Limitations Found

- **GitHub webhooks have no retries** - Must implement consumer-side reliability
- **Webhook retry behavior varies by vendor** - 3-7 retries typical, but not guaranteed
- **Bidirectional sync is complex** - CAP theorem constraints; eventual consistency only guarantee

---

## Application to RaiSE Backlog Sync

### Context
RaiSE needs to synchronize between:
- Local unified graph (raise memory)
- External issue trackers (Jira, Linear, GitHub Issues)

### Design Implications

**Start Simple (Manual)**:
- `rai backlog sync` as primary mechanism
- User-initiated, predictable behavior
- Works without provider configuration

**Add Automation (Lifecycle)**:
- Hook into `/rai-epic-start` and `/rai-epic-close` skills
- Conditional on project configuration
- Graceful failure handling

**Future Enhancement (Reconciliation)**:
- Detect drift from external changes
- Recover from missed webhook events
- Provide eventual consistency guarantee

### Trade-offs Accepted

✅ **Accepting**:
- Eventual consistency over real-time sync
- Manual commands as primary mechanism
- Simple implementation over complex event infrastructure

❌ **Rejecting**:
- Webhook-only approach (reliability issues)
- Polling-only approach (resource waste)
- Strong consistency (CAP theorem, unnecessary)

---

## Research Artifacts

```
sync-trigger-patterns/
├── README.md                           ← You are here (15-min overview)
├── sync-trigger-patterns-report.md     ← Full report with findings
├── sources/
│   └── evidence-catalog.md             ← 30+ sources with ratings
└── prompt.md                           ← Research prompt (reproducibility)
```

---

## Next Steps

1. **Review recommendation** with stakeholders (Emilio)
2. **Validate against RaiSE constraints** (CLI-first, HITL, simple)
3. **Design sync command UX** (flags, output format, error handling)
4. **Implement Tier 1** (manual commands) as MVP
5. **Document sync strategy** in ADR for future reference

---

## Key Sources

### Production Integration Patterns
- [Linear-Jira Integration](https://linear.app/docs/jira) - Webhook-driven bidirectional sync
- [GitHub-Jira Sync](https://github.com/canonical/sync-issues-github-jira) - Event-driven with lifecycle triggers
- [GitOps Patterns](https://codefresh.io/blog/gitops-patterns-auto-sync-vs-manual-sync/) - Auto-sync + manual control

### Webhook vs Polling
- [Merge.dev: Webhooks vs Polling](https://www.merge.dev/blog/webhooks-vs-polling) - Hybrid as pragmatic pattern
- [Hookdeck: GitHub Webhooks Guide](https://hookdeck.com/webhooks/platforms/guide-github-webhooks-features-and-best-practices) - GitHub limitations and mitigation

### Retry and Failure Handling
- [Hookdeck: Webhook Retry Best Practices](https://hookdeck.com/webhooks/guides/webhook-retry-best-practices) - Exponential backoff, 3-7 retries
- [Azure: Compensating Transaction Pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/compensating-transaction) - Retry strategies

### Eventual Consistency
- [StackSync: Bi-Directional Sync Challenges](https://www.stacksync.com/blog/the-engineering-challenges-of-bi-directional-sync-why-two-one-way-pipelines-fail) - CAP theorem constraints
- [System Design School: Anti-Entropy](https://systemdesignschool.io/blog/anti-entropy) - Reconciliation mechanisms

---

*Research conducted using epistemologically rigorous methodology (rai-research skill)*
