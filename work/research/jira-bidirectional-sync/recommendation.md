# Recommendation: RaiSE-JIRA Bidirectional Sync Architecture

**Decision Date**: 2026-02-14
**Research ID**: jira-bidirectional-sync-20260214
**Confidence**: HIGH
**Impact**: Strategic (affects March 14 demo, Coppel client, and all future JIRA integrations)

---

## Decision

Implement **webhook-first, polling-backup architecture** with **entity properties for metadata storage**, **field-level conflict resolution**, and **idempotent event processing**.

---

## Rationale

### 1. Webhook-First Architecture (PRIMARY)

**Based on**:
- [Best practices on working with WebHooks in Jira Data Center](https://support.atlassian.com/jira/kb/best-practices-on-working-with-webhooks-in-jira-data-center/) - Webhooks reduce server load and bandwidth
- [New Jira Cloud Webhook Retry Policy](https://community.developer.atlassian.com/t/new-jira-cloud-webhook-retry-policy/30554) - JIRA retries up to 5 times with backoff
- [A Practical Use for Setting Up Jira to ServiceNow Bi-Directional Integration](https://www.servicenow.com/community/developer-articles/a-practical-use-for-setting-up-jira-to-servicenow-bi-directional/ta-p/3160262) - Production implementation of webhook-based bidirectional sync

**Why**: Real-time sync with built-in retry mechanism. JIRA Cloud guarantees delivery with X-Atlassian-Webhook-Identifier for deduplication.

### 2. Polling Backup (SECONDARY)

**Based on**:
- [Sync Jira issues without using webhooks](https://support.productboard.com/hc/en-us/articles/42207565943443-Sync-Jira-issues-without-using-webhooks) - 15-minute polling is reliable and ensures compliance
- [Guide to Webhooks](https://www.merge.dev/blog/guide-to-webhooks-with-examples-from-jira) - Polling catches deletions that webhooks might miss

**Why**: Safety net for missed webhooks, initial bulk sync, and periodic reconciliation. 15-minute interval balances freshness with API consumption.

### 3. Entity Properties for Metadata

**Based on**:
- [Jira entity properties](https://developer.atlassian.com/cloud/jira/platform/jira-entity-properties/) - Key-value stores attached to JIRA entities, queryable via JQL
- [Entity Property - Jira Cloud platform](https://developer.atlassian.com/cloud/jira/platform/modules/entity-property/) - Max 32 KB JSON storage per entity

**Why**: Avoids custom field proliferation (performance impact), invisible to end users, supports complex metadata (JSON), queryable via REST and JQL.

### 4. Field-Level Conflict Resolution

**Based on**:
- [Two-Way Sync Demystified](https://www.stacksync.com/blog/two-way-sync-demystified-key-principles-and-best-practices) - Field-level merging provides granular control
- [The Complete Guide to Two Way Sync](https://www.stacksync.com/blog/the-complete-guide-to-two-way-sync-definitions-methods-and-use-cases) - Last-write-wins can override business decisions

**Why**: Different fields have different conflict semantics. Comments should append; status should prompt user; description can use last-write-wins.

### 5. Idempotent Event Processing

**Based on**:
- [Webhooks - Jira Cloud platform](https://developer.atlassian.com/cloud/jira/platform/webhooks/) - X-Atlassian-Webhook-Identifier for retry deduplication
- [Idempotency in Distributed Systems](https://medium.com/javarevisited/idempotency-in-distributed-systems-preventing-duplicate-operations-85ce4468d161) - Idempotency enables safe retries

**Why**: Webhooks may deliver multiple times. Handlers must be idempotent to prevent duplicate operations (double-posting comments, creating duplicate issues).

---

## Trade-offs

### What We're Accepting

| Trade-off | Acceptance Rationale |
|-----------|---------------------|
| **Eventual consistency** | JIRA changes may take seconds to sync to RaiSE (and vice versa). ACCEPTABLE: Users understand distributed systems have propagation delay. UI shows "syncing..." indicator. |
| **Polling cost** | 15-minute polling consumes API quota even when no changes. ACCEPTABLE: Safety net worth the cost; optimized with field filtering and pagination. |
| **Complexity over simplicity** | Field-level resolution is more complex than entity-level last-write-wins. ACCEPTABLE: Correctness matters more than simplicity for business-critical fields. |
| **JIRA Cloud only (initially)** | Webhook retries only work on JIRA Cloud, not Data Center. ACCEPTABLE: Target market (Coppel, Humansys clients) uses Cloud; Data Center support deferred to Phase 3. |
| **Storage overhead** | Entity properties add 1-5 KB per issue for sync metadata. ACCEPTABLE: 32 KB limit sufficient; cost negligible compared to issue data. |

### What We're NOT Accepting

- **Strong consistency**: Would require distributed transactions → infeasible across external systems
- **Synchronous sync**: Would block user operations → unacceptable UX
- **Duplicate issue creation**: Prevented via idempotency checks
- **Data loss on conflict**: Prevented via field-level resolution and user prompts
- **Infinite sync loops**: Prevented via sync markers in entity properties

---

## Risks & Mitigations

### Risk 1: Rate Limiting (March 2, 2026 Enforcement)

**Impact**: HIGH (could break all sync operations if limits exceeded)

**Probability**: MEDIUM (new points-based limits less forgiving)

**Mitigations**:
1. **Field filtering**: Request only necessary fields (reduce points per request)
2. **Monitor X-RateLimit-Remaining**: Implement exponential backoff at 20% threshold
3. **Caching with ETags**: Avoid re-fetching unchanged data
4. **Batch operations**: Group updates to reduce request count
5. **Test in sandbox**: Validate against new limits before March 2

**References**:
- [Rate limiting - Jira Cloud platform](https://developer.atlassian.com/cloud/jira/platform/rate-limiting/)
- [Scaling responsibly: evolving our API rate limits](https://www.atlassian.com/blog/platform/evolving-api-rate-limits)

---

### Risk 2: Webhook Delivery Failures

**Impact**: MEDIUM (missed updates create divergence)

**Probability**: LOW (JIRA retries 5 times with backoff)

**Mitigations**:
1. **Idempotent handlers**: Safe to retry, deduplication via X-Atlassian-Webhook-Identifier
2. **Polling backup**: 15-minute reconciliation catches missed events
3. **Failure alerting**: Monitor webhook error rates, alert on sustained failures
4. **Manual resync**: Admin UI to trigger full reconciliation if divergence detected

**References**:
- [New Jira Cloud Webhook Retry Policy](https://community.developer.atlassian.com/t/new-jira-cloud-webhook-retry-policy/30554)
- [Webhooks - Jira Cloud platform](https://developer.atlassian.com/cloud/jira/platform/webhooks/)

---

### Risk 3: Sync Conflicts Confuse Users

**Impact**: MEDIUM (user frustration, support burden)

**Probability**: MEDIUM (conflicts inevitable with bidirectional sync)

**Mitigations**:
1. **Field-level resolution**: Most fields auto-resolve (last-write-wins for descriptions, append for comments)
2. **User prompts for critical fields**: Status, assignee, priority require user decision
3. **Clear UI**: Show conflict state, present both versions, allow selection
4. **Audit log**: All conflict resolutions logged for review
5. **Documentation**: Help docs explain sync behavior and conflict handling

**References**:
- [Two-Way Sync Demystified](https://www.stacksync.com/blog/two-way-sync-demystified-key-principles-and-best-practices)
- [Conflict Resolution - MongoDB Docs](https://www.mongodb.com/docs/atlas/app-services/sync/details/conflict-resolution/)

---

### Risk 4: Infinite Sync Loops

**Impact**: HIGH (runaway API consumption, rate limit exhaustion, data corruption)

**Probability**: LOW (preventable with sync markers)

**Mitigations**:
1. **Sync markers in entity properties**: Mark updates as originating from sync (don't sync back)
2. **Circuit breakers**: Stop sync if >10 updates/minute detected on single issue
3. **Webhook filtering**: Configure JIRA webhooks to exclude sync-originated updates
4. **Testing**: Integration tests for common loop scenarios (automation rules, cascading updates)

**References**:
- [Jira entity properties](https://developer.atlassian.com/cloud/jira/platform/jira-entity-properties/)
- [How To Implement Jira Issue Sync](https://exalate.com/blog/jira-issue-sync/)

---

### Risk 5: Initial Bulk Sync Performance

**Impact**: MEDIUM (slow onboarding for large JIRA instances)

**Probability**: MEDIUM (Coppel may have 1000s of issues)

**Mitigations**:
1. **Async bulk sync**: Background job with progress indicator
2. **Pagination optimization**: Use maxResults=100-500 (balance page size vs request count)
3. **Field filtering**: Fetch only fields needed for RaiSE (not full issue object)
4. **Incremental sync**: Offer "sync last 3 months" option for faster onboarding
5. **Rate limit awareness**: Pause/resume based on X-RateLimit-Remaining

**References**:
- [Batch Processing Issues in Jira with API Pagination](https://reintech.io/blog/batch-processing-pagination-jira-api)
- [How to use the maxResults API parameter](https://support.atlassian.com/jira/kb/how-to-use-the-maxresults-api-parameter-for-jira-issue-search-rest-api/)

---

### Risk 6: Multi-Tenant Data Isolation

**Impact**: CRITICAL (data leak between customers)

**Probability**: LOW (preventable with architecture discipline)

**Mitigations**:
1. **Tenant-scoped credentials**: Each customer has separate JIRA OAuth tokens
2. **Database-level isolation**: Tenant ID in all queries (enforce with RLS if Postgres)
3. **Webhook validation**: Verify webhook origin matches tenant's JIRA instance
4. **Security review**: Penetration testing for cross-tenant access
5. **Audit logging**: All cross-system operations logged with tenant ID

**References**:
- [Integrate Jira issues with your application](https://developer.atlassian.com/cloud/jira/platform/integrate-jira-issues-with-your-application/)
- [How to integrate Jira with other tools](https://www.oneio.cloud/blog/how-to-integrate-jira-with-other-tools)

---

## Alternatives Considered

### Alternative 1: Polling-Only (No Webhooks)

**Pros**:
- Simpler implementation (no webhook endpoint, no retry handling)
- Works with JIRA Data Center and Cloud uniformly
- Predictable API consumption

**Cons**:
- Higher latency (15-minute intervals vs seconds)
- More API calls (poll even when no changes)
- Worse UX (users wait for sync)

**Why Rejected**: Real-time sync is table stakes for modern integrations. Webhook-first with polling backup gives best of both worlds.

---

### Alternative 2: Last-Write-Wins for All Fields

**Pros**:
- Simplest conflict resolution (no user prompts needed)
- Fastest implementation
- No conflict UI required

**Cons**:
- Can silently override important decisions (status changes, assignments)
- Users may not notice conflicts occurred
- Data loss potential (comments overwritten vs appended)

**Why Rejected**: Unacceptable for business-critical fields. Field-level resolution provides correctness without excessive complexity.

---

### Alternative 3: Custom Fields for Metadata (Instead of Entity Properties)

**Pros**:
- Visible to users (transparency)
- Simpler to query in JQL
- Familiar pattern

**Cons**:
- Custom field proliferation impacts JIRA performance
- Clutters user UI with sync internals
- Not designed for machine-readable metadata
- 1000+ custom fields can degrade JIRA instance

**Why Rejected**: Entity properties are purpose-built for external integration metadata. Custom fields should be reserved for user-facing data.

**Reference**: [7 Custom Fields Every Jira Application Needs](https://www.jirastrategy.com/custom-fields-every-jira-application-needs/)

---

### Alternative 4: Centralized ESB/Middleware

**Pros**:
- Single point of control
- Familiar enterprise pattern
- Centralized monitoring

**Cons**:
- Single point of failure
- Scaling bottleneck
- Complex operational overhead
- Worse for multi-tenant isolation

**Why Rejected**: Modern sync tools use distributed architecture (Exalate pattern). RaiSE can embed sync logic in application tier without separate middleware layer.

**Reference**: [How To Implement Jira Issue Sync [2026]](https://exalate.com/blog/jira-issue-sync/)

---

## Implementation Roadmap

### Phase 1: MVP (Target: March 14 Demo)

**Scope**: One-way sync (RaiSE → JIRA) with basic webhook registration

**Deliverables**:
- [ ] OAuth integration with JIRA Cloud
- [ ] Story creation in JIRA from RaiSE backlog
- [ ] Entity property storage for RaiSE story ID
- [ ] Webhook registration (preparation for bidirectional)
- [ ] Field mapping: summary, description, issue type (Story)
- [ ] Rate limit monitoring (X-RateLimit-Remaining)

**Success Criteria**:
- Demo: Create story in RaiSE, appears in JIRA within 5 seconds
- No rate limit errors during demo (monitor console)
- Duplicate story creation prevented (idempotency check)

---

### Phase 2: Bidirectional Sync (Target: March 31, Post-Demo)

**Scope**: Enable JIRA → RaiSE sync with conflict resolution

**Deliverables**:
- [ ] Webhook endpoint for JIRA events
- [ ] Idempotent webhook handlers (X-Atlassian-Webhook-Identifier tracking)
- [ ] Status sync (JIRA status → RaiSE story state)
- [ ] Comment sync (bidirectional, append-only)
- [ ] Field-level conflict resolution (last-write-wins for description)
- [ ] User prompt for status conflicts (if both changed)
- [ ] Polling backup (15-minute reconciliation)
- [ ] Sync status UI (last sync time, conflict count)

**Success Criteria**:
- JIRA status change appears in RaiSE within 30 seconds
- Comments added in either system appear in other within 1 minute
- No duplicate webhooks processed (idempotency verified)
- Polling catches 100% of missed events (tested with webhook downtime)

---

### Phase 3: Advanced Features (Target: Q2 2026)

**Scope**: Custom fields, bulk sync, workflow mapping

**Deliverables**:
- [ ] Custom field mapping UI
- [ ] Workflow state mapping (JIRA workflows ≠ RaiSE states)
- [ ] Bulk sync for existing projects (paginated, rate-limited)
- [ ] Attachment sync
- [ ] Label sync (bidirectional)
- [ ] Multi-project sync (sync multiple JIRA projects to one RaiSE workspace)
- [ ] Scripting engine for advanced transformations (future consideration)

**Success Criteria**:
- Bulk sync 1000 issues without rate limit errors
- Custom fields mapped correctly
- Workflow states map to RaiSE states (configurable)

---

## Technical Specifications

### Entity Property Schema

```json
{
  "raise_sync": {
    "story_id": "s1.2",
    "epic_id": "e1",
    "last_sync_timestamp": "2026-02-14T10:30:00Z",
    "last_sync_source": "raise",
    "raise_workspace": "customer-abc",
    "conflict_state": null,
    "sync_version": "1"
  }
}
```

**Fields**:
- `story_id`: RaiSE story identifier
- `epic_id`: RaiSE epic identifier (if applicable)
- `last_sync_timestamp`: ISO 8601 timestamp of last sync
- `last_sync_source`: "raise" or "jira" (for loop prevention)
- `raise_workspace`: Multi-tenant isolation
- `conflict_state`: "resolved" | "pending_user" | null
- `sync_version`: Schema version for migrations

---

### Webhook Event Types

Register for these JIRA events:

| Event | Purpose | Handler |
|-------|---------|---------|
| `jira:issue_created` | Detect new issues in JIRA | Create story in RaiSE |
| `jira:issue_updated` | Detect field changes | Update story fields |
| `jira:issue_deleted` | Detect deletions | Archive story in RaiSE |
| `comment_created` | Detect new comments | Sync comment to RaiSE |
| `comment_updated` | Detect comment edits | Update comment in RaiSE |

---

### API Call Optimization

**Field Filtering** (reduce points consumed):
```
GET /rest/api/3/issue/{issueIdOrKey}?fields=summary,description,status,updated,comment
```

**Pagination** (balance page size vs request count):
```
GET /rest/api/3/search?jql=project=ABC&maxResults=100&fields=id,key,summary,updated
```

**Rate Limit Monitoring**:
```python
remaining = int(response.headers.get('X-RateLimit-Remaining', 100))
if remaining < 20:  # 20% threshold
    backoff_seconds = 60 * (1 - remaining / 100)  # Exponential backoff
    await asyncio.sleep(backoff_seconds)
```

---

## Success Metrics

### Sync Performance

- **Latency**: 95th percentile sync time < 30 seconds (webhook-based)
- **Throughput**: Support 100 issues/minute sync rate
- **Reliability**: 99.9% webhook delivery success (with retries)
- **Polling catch rate**: 100% of missed events caught within 15 minutes

### API Efficiency

- **Rate limit compliance**: 0 rate limit errors in production
- **Points efficiency**: <50 points per issue sync (under new limits)
- **Cache hit rate**: >70% for unchanged issue fetches (ETags)

### Conflict Resolution

- **Auto-resolution rate**: >80% of conflicts resolved automatically (field-level)
- **User resolution time**: <2 minutes median time to resolve prompted conflict
- **Conflict frequency**: <5% of syncs result in user-visible conflict

### User Experience

- **Sync awareness**: 100% of syncs show UI indicator ("syncing...", "synced")
- **Error recovery**: 100% of sync failures logged and recoverable via admin UI
- **Onboarding time**: <5 minutes to connect JIRA workspace (OAuth flow)

---

## References

**Key Sources** (Top 10 by Evidence Level):

1. [Jira entity properties](https://developer.atlassian.com/cloud/jira/platform/jira-entity-properties/) - Very High
2. [Rate limiting - Jira Cloud platform](https://developer.atlassian.com/cloud/jira/platform/rate-limiting/) - Very High
3. [Webhooks - Jira Cloud platform](https://developer.atlassian.com/cloud/jira/platform/webhooks/) - Very High
4. [New Jira Cloud Webhook Retry Policy](https://community.developer.atlassian.com/t/new-jira-cloud-webhook-retry-policy/30554) - Very High
5. [Integrate Jira issues with your application](https://developer.atlassian.com/cloud/jira/platform/integrate-jira-issues-with-your-application/) - Very High
6. [How To Implement Jira Issue Sync [2026]](https://exalate.com/blog/jira-issue-sync/) - High
7. [Two-Way Sync Demystified](https://www.stacksync.com/blog/two-way-sync-demystified-key-principles-and-best-practices) - High
8. [Distributed Data for Microservices — Event Sourcing vs. CDC](https://debezium.io/blog/2020/02/10/event-sourcing-vs-cdc/) - Very High
9. [Idempotency in Distributed Systems](https://medium.com/javarevisited/idempotency-in-distributed-systems-preventing-duplicate-operations-85ce4468d161) - High
10. [Conflict Resolution - MongoDB Docs](https://www.mongodb.com/docs/atlas/app-services/sync/details/conflict-resolution/) - Very High

**Full Evidence Catalog**: See `sources/evidence-catalog.md` (32 sources total)

---

## Governance Linkage

**ADR Required**: Yes (sync architecture is architectural decision)

**Backlog Items**:
- Story: "Implement JIRA OAuth integration"
- Story: "Create webhook endpoint for JIRA events"
- Story: "Implement entity property storage for sync metadata"
- Story: "Build field-level conflict resolution engine"
- Story: "Create polling reconciliation job"

**Parking Lot**:
- Future: Scripting engine for advanced transformations (deferred to Phase 3+)
- Future: JIRA Data Center support (Cloud sufficient for target market)
- Future: Real-time collaborative editing with OT (beyond current scope)

---

**Recommendation Version**: 1.0
**Author**: Claude (rai-research skill)
**Reviewed By**: [Pending human review]
**Approved By**: [Pending approval]
**Status**: DRAFT
