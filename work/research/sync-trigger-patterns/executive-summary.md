# Executive Summary: Sync Trigger Patterns

**Date**: 2026-02-14
**Context**: RaiSE backlog synchronization design
**Read Time**: 5 minutes

---

## The Question

When and how should RaiSE trigger synchronization between the local unified graph and external issue trackers (Jira, Linear, GitHub Issues)?

---

## The Answer

**Three-tier hybrid sync strategy**:

1. **Manual commands** (MVP) - User control, simple implementation
2. **Lifecycle event triggers** (v2.1) - Automatic sync at epic start/close
3. **Periodic reconciliation** (Future) - Drift detection and recovery

Accept **eventual consistency** (seconds to minutes delay acceptable).

---

## Why This Works

### Industry Convergence
30+ sources, including production systems (Linear-Jira, GitHub-Jira, GitOps tools), converge on **hybrid architectures**:
- Webhooks for speed
- Reconciliation for reliability
- Manual commands for control

### Alignment with RaiSE Philosophy
- **CLI-first**: Manual commands are primary mechanism
- **HITL (Human in the Loop)**: User initiates and observes sync
- **Simple First**: Start with manual, add complexity as needed
- **Reliability over Magic**: Explicit sync > hidden failures

### CAP Theorem Acceptance
Backlog sync doesn't need strong consistency. Production tools explicitly trade consistency for availability and partition tolerance.

---

## The Recommendation

### Tier 1: Manual Commands (Ship First)

```bash
rai backlog sync --provider linear --direction pull  # Import from Linear
rai backlog sync --provider linear --direction push  # Export to Linear
rai backlog sync --provider linear --direction both  # Bidirectional
```

**Why**:
- User understands exactly when sync happens
- No infrastructure required (no webhooks, no background jobs)
- Works without provider configuration
- Predictable, deterministic behavior

**MVP Scope**:
- Unidirectional pull (import epics/stories from external tracker)
- Idempotent (detect existing issues, update vs create)
- Explicit output (what changed, errors, summary)

---

### Tier 2: Lifecycle Event Triggers (Add After MVP Validation)

Automatic sync at natural boundaries:

```python
# In /rai-epic-start skill
if config.backlog_sync_enabled and config.backlog_provider:
    sync_epic_to_provider(epic_metadata, direction="push")

# In /rai-epic-close skill
if config.backlog_sync_enabled:
    sync_epic_to_provider(epic_metadata, direction="both")
```

**Why**:
- Epic start/close are already commits (natural transaction boundaries)
- Skills are explicit (user sees sync happening in output)
- Conditional on config (opt-in per project)
- Graceful failure (warn, don't block)

**Trigger Points**:
- Epic Start → Push epic to external tracker
- Story Start → Push story to external tracker
- Epic Close → Pull final state, push retrospective

---

### Tier 3: Periodic Reconciliation (Future Work)

Optional drift detection:

```bash
rai backlog reconcile --dry-run  # Show differences
rai backlog reconcile --apply     # Apply reconciliation
```

**Why**:
- Detects external changes (someone updated Jira directly)
- Recovers from missed webhook events
- Provides eventual consistency guarantee

**Mechanisms**:
- State hash comparison (Merkle trees)
- Conflict detection with manual resolution
- Optional daily reconciliation (cron/config)

---

## Key Trade-offs

### Accepting
✅ Eventual consistency (not real-time)
✅ Manual as primary (user control)
✅ Simple implementation (no webhook infrastructure)
✅ Unidirectional first (pull OR push, not both)

### Rejecting
❌ Webhook-only (reliability issues, GitHub has no retries)
❌ Polling-only (resource waste, latency)
❌ Strong consistency (CAP theorem, unnecessary)
❌ Complex event infrastructure (YAGNI for MVP)

---

## Critical Findings

### 1. Hybrid is Production Standard
Pure webhook or pure polling rare. Production systems layer:
- Webhooks (fast path)
- Reconciliation (slow path)
- Manual commands (escape hatch)

**Sources**: Merge.dev, Linear-Jira, GitOps patterns

### 2. Eventual Consistency is Acceptable
Engineering tools explicitly accept seconds-to-minutes delay. Backlog sync doesn't need real-time consistency.

**Sources**: StackSync (bidirectional challenges), SSENSE-TECH (eventual consistency), Wikipedia

### 3. Lifecycle Events are Natural Sync Points
Tools sync at boundaries (issue creation, epic close), not continuous streaming.

**Sources**: Linear-Jira, GitHub-Jira, common data sync strategies

### 4. Retry Strategies are Well-Established
Exponential backoff with jitter, 3-7 retries, 1-3 day window, dead letter queue.

**Sources**: Hookdeck, Svix, Wellhub Tech

### 5. GitHub Webhooks Have Critical Limitations
No automatic retries, 10-second timeout, no failed event API. Must implement consumer-side reliability or polling fallback.

**Sources**: Hookdeck GitHub guide, GitHub Community discussions

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Sync failures go unnoticed | Explicit CLI output; `rai backlog status` command; optional notifications |
| Bidirectional conflicts | Start unidirectional (pull OR push); add conflict detection in v2.1 |
| Provider API rate limits | Exponential backoff on 429; respect `Retry-After` header; batch operations |
| Configuration complexity | Sane defaults; `rai backlog configure` guided setup; validate before sync |

---

## Implementation Path

**Phase 1: Manual Commands (MVP)**
1. `rai backlog sync` with provider selection
2. Unidirectional pull (import from tracker)
3. Idempotent sync (update vs create)
4. Sync status output

**Phase 2: Lifecycle Triggers**
1. Hooks in `/rai-epic-start` and `/rai-epic-close`
2. Conditional on `backlog_sync_enabled` config
3. Graceful failure handling
4. Dry-run mode

**Phase 3: Reconciliation (Future)**
1. `rai backlog reconcile` command
2. State hash comparison
3. Conflict detection and resolution UX
4. Optional scheduled reconciliation

---

## Evidence Strength

**Confidence**: HIGH

- **30+ sources** consulted
- **5 Very High** evidence (official docs: Linear, Azure, ACM, IBM, Airbyte)
- **14 High** evidence (production blogs, GitHub, integration platforms)
- **Triangulation**: Major claims supported by 3+ independent sources
- **Real-world validation**: Linear-Jira, GitHub-Jira, GitOps tools follow same pattern

---

## Recommended Next Steps

1. **Validate recommendation** with Emilio (alignment with RaiSE philosophy)
2. **Design sync command UX** (flags, output format, provider selection)
3. **Implement Tier 1 MVP** (manual `rai backlog sync` command)
4. **Document in ADR** (architectural decision record for future reference)
5. **Test with Linear integration** (first provider, simpler API than Jira)

---

## Full Research Artifacts

- **README.md** - 15-minute overview with navigation
- **sync-trigger-patterns-report.md** - Complete report (8 findings, patterns, gaps, recommendations)
- **sources/evidence-catalog.md** - 30+ sources with ratings and relevance
- **prompt.md** - Research prompt (reproducibility)

---

*Research conducted using epistemologically rigorous methodology*
*Triangulated claims, explicit confidence levels, contrary evidence acknowledged*
