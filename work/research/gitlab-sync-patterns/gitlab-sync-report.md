# GitLab Issues/Epics Sync Implementation Research

**Research ID**: gitlab-sync-20260214
**Created**: 2026-02-14
**Researcher**: Claude Sonnet 4.5 (via /rai-research skill)
**Context**: RaiSE GitLab integration architecture design (second platform after JIRA)

---

## Executive Summary

GitLab offers robust APIs for issue/epic sync, but with critical gotchas: **the Epics REST API is deprecated** (removal in API v5), **webhook reliability is limited** (auto-disable after 4 failures, no exponential backoff), and **bidirectional sync has inherent race conditions**. The recommended pattern is: **GraphQL Work Items API + defensive polling with ETag caching + async webhook processing**, treating webhooks as optimization rather than primary sync mechanism.

**Key Recommendation**: Start with REST API for Issues (stable), plan migration to GraphQL Work Items for Epics (future-proof), implement polling-first architecture with webhook acceleration.

---

## Major Claims (Triangulated)

### Claim 1: Epics REST API is Deprecated - Migrate to Work Items API

**Confidence**: HIGH

**Evidence**:
1. [Epics API (deprecated) | GitLab Docs](https://docs.gitlab.com/api/epics/) - Deprecated in 17.0, removal planned in API v5
2. [Migrate epic APIs to work items | GitLab Docs](https://docs.gitlab.com/api/graphql/epic_work_items_api_migration_guide/) - Migration guide exists; GraphQL Work Items is replacement
3. [Epic Issues API (deprecated) | GitLab Docs](https://docs.gitlab.com/api/epic_issues/) - Epic-Issue associations deprecated alongside Epics API

**Disagreement**: None found - GitLab consistently documents this migration path

**Implication**: RaiSE must design Epic sync using Work Items API (GraphQL) or accept technical debt by using deprecated REST API short-term. **IID remains stable identifier** across migration (Epic IID = Work Item IID), but global IDs change.

---

### Claim 2: GitLab Webhooks Have Fragile Reliability - Polling Fallback Required

**Confidence**: HIGH

**Evidence**:
1. [Webhooks | GitLab Docs](https://docs.gitlab.com/user/project/integrations/webhooks/) - Auto-disabled after 4 consecutive failures (1min); permanently disabled after 40 failures
2. [Guide to GitLab Webhooks: Features and Best Practices](https://hookdeck.com/webhooks/platforms/guide-to-gitlab-webhooks-features-and-best-practices) - "No traditional retry mechanism with exponential backoff"; 5xx retries for 24h only; single failed delivery = lost event
3. [How to Solve GitLab Webhook Timeout Errors](https://hookdeck.com/webhooks/platforms/how-to-solve-gitlab-webhook-timeout-errors) - Must respond <10s; async processing required; queue-based architecture essential

**Disagreement**: None - all sources converge on fragility

**Implication**: RaiSE **cannot rely on webhooks alone** for sync. Must implement:
- Defensive polling with ETag caching (fallback sync mechanism)
- Async webhook processing (respond immediately, queue for processing)
- Monitoring for auto-disabled webhooks
- Duplicate detection (webhooks may retry on 5xx)

**Pattern**: Treat webhooks as **optimization** for real-time sync, not primary mechanism.

---

### Claim 3: ID vs IID Confusion is Top Gotcha - IID is Stable, ID is Not

**Confidence**: HIGH

**Evidence**:
1. [Troubleshooting the REST API | GitLab Docs](https://docs.gitlab.com/api/rest/troubleshooting/) - ID vs IID confusion is common; API uses IID not ID for resource fetching
2. [Migrate epic APIs to work items](https://docs.gitlab.com/api/graphql/epic_work_items_api_migration_guide/) - Epic ID ≠ Work Item ID, but IID stays same
3. [Issues API | GitLab Docs](https://docs.gitlab.com/api/issues/) - Example: project 42, issue with id=46 and iid=5 → use GET /projects/42/issues/5 (not /46)

**Disagreement**: None

**Implication**: RaiSE must store and sync using **IID** (internal ID scoped to project/group), not global ID. IID is:
- Human-readable (e.g., #123)
- Stable across migrations (Epic → Work Item)
- Required for API requests

**Storage strategy**: Store both `gitlab_id` (global) and `gitlab_iid` (scoped) in sync state, use IID for API calls.

---

### Claim 4: ETag Caching Enables Efficient Polling Without DB Queries

**Confidence**: HIGH

**Evidence**:
1. [Polling with ETag caching | GitLab Docs](https://docs.gitlab.com/development/polling/) - If-None-Match returns 304 when unchanged; GitLab stores ETags in Redis
2. [Using the REST API - python-gitlab](https://python-gitlab.readthedocs.io/en/stable/api-usage.html) - python-gitlab auto-handles rate limits with Retry-After; lazy iterators for pagination
3. [Caching guidelines | GitLab Docs](https://docs.gitlab.com/development/caching/) - Cache invalidation on resource change; random ETag value generated per change

**Disagreement**: [Artifacts API: ETag caching is broken](https://gitlab.com/gitlab-org/gitlab/-/issues/371991) - Some endpoints have broken ETag implementation

**Implication**: RaiSE should use ETags for polling optimization where available, but verify endpoint support. Pattern:
```python
# Store last ETag per resource
headers = {"If-None-Match": last_etag}
response = requests.get(url, headers=headers)
if response.status_code == 304:
    # No changes, skip processing
    return
# Process changes and store new ETag
last_etag = response.headers.get("ETag")
```

**Caveat**: Not all endpoints support ETags reliably; test per endpoint.

---

### Claim 5: Keyset Pagination Required for Large Datasets (>50k Records)

**Confidence**: HIGH

**Evidence**:
1. [REST API | GitLab Docs](https://docs.gitlab.com/api/rest/) - Link headers for pagination; keyset pagination enforced when >50k records requested
2. [Pagination guidelines | GitLab Docs](https://docs.gitlab.com/development/database/pagination_guidelines/) - Keyset addresses performance of "skipping" rows; not drop-in replacement for offset pagination
3. [python-gitlab API Usage](https://python-gitlab.readthedocs.io/en/stable/api-usage.html) - get_all=True or iterator=True for pagination; use Link headers not manual URL construction

**Disagreement**: None

**Implication**: For bulk sync operations (initial backlog import), RaiSE must:
- Use `iterator=True` for lazy pagination (memory efficient)
- Follow Link headers (rel=next) instead of offset-based pagination
- Expect different pagination mode when crossing 50k threshold

**Recommendation**: Use python-gitlab's built-in iterators for automatic pagination handling.

---

### Claim 6: Rate Limiting is Instance-Specific - Must Handle Retry-After

**Confidence**: HIGH

**Evidence**:
1. [Rate limits | GitLab Docs](https://docs.gitlab.com/security/rate_limits/) - REST API rate limits vary per instance; authenticated vs unauthenticated differ
2. [User and IP rate limits | GitLab Docs](https://docs.gitlab.com/administration/settings/user_and_ip_rate_limits/) - Admins configure limits; defaults differ between SaaS and self-hosted
3. [python-gitlab API Usage](https://python-gitlab.readthedocs.io/en/stable/api-usage.html) - Library auto-sleeps on 429 using Retry-After header or exponential backoff

**Disagreement**: None

**Implication**: RaiSE cannot hardcode rate limits. Must:
- Respect Retry-After header on 429 responses
- Implement exponential backoff when header missing
- Allow user configuration for conservative sync rates

**Pattern**: Use python-gitlab's built-in rate limit handling (obeys by default).

---

### Claim 7: GraphQL Better for Complex Queries, REST for Simple Operations

**Confidence**: MEDIUM (context-dependent trade-offs)

**Evidence**:
1. [What GitLab GraphQL Actually Does](https://hoop.dev/blog/what-gitlab-graphql-actually-does-and-when-to-use-it/) - GraphQL reduces payload size, cuts query latency, removes pagination for nested data
2. [GraphQL API | GitLab Docs](https://docs.gitlab.com/api/graphql/) - Versionless, backward-compatible; batching support; sparse field selection
3. [GitLab Forum: GraphQL vs REST](https://forum.gitlab.com/t/difference-between-rest-api-and-graphql-api-issue-discussion/69465) - Community consensus: GraphQL for complex queries, REST for simple scripts

**Disagreement**: None, but some features only in REST (e.g., label change history per one source)

**Implication**: Hybrid approach for RaiSE:
- **REST API**: Issues CRUD (mature, stable, good docs)
- **GraphQL**: Work Items (Epics) - required for non-deprecated API
- **GraphQL**: Nested queries (Epic → Issues hierarchy in single request)

**Trade-off**: GraphQL has learning curve and different error handling patterns.

---

### Claim 8: Bidirectional Sync Has Inherent Race Conditions

**Confidence**: HIGH

**Evidence**:
1. [Bidirectional mirroring | GitLab Docs](https://docs.gitlab.com/user/project/repository/mirror/bidirectional/) - Race conditions when commits made close together; push webhooks mitigate; rate-limited to 1/min for protected branches
2. [Webhook events | GitLab Docs](https://docs.gitlab.com/user/project/integrations/webhook_events/) - "Payloads must accurately represent state at event time; care needed for race conditions"
3. [Provide workaround to prevent bidirectional mirroring conflicts](https://gitlab.com/gitlab-org/gitlab/-/issues/6237) - Issue documenting conflict challenges

**Disagreement**: None - acknowledged limitation

**Implication**: For RaiSE bidirectional sync (GitLab ↔ local backlog):
- **Last-write-wins** strategy (timestamp-based)
- Conflict detection (compare `updated_at` timestamps)
- User resolution for conflicts (show both versions)
- **Avoid**: Automatic merge strategies without user awareness

**Pattern**: Optimistic concurrency with conflict detection, not automatic resolution.

---

### Claim 9: Personal Access Tokens Sufficient for MVP, OAuth for Production

**Confidence**: MEDIUM (security vs complexity trade-off)

**Evidence**:
1. [REST API authentication | GitLab Docs](https://docs.gitlab.com/api/rest/authentication/) - Personal, project, group tokens; OAuth2; PRIVATE-TOKEN header recommended
2. [Personal access tokens | GitLab Docs](https://docs.gitlab.com/user/profile/personal_access_tokens/) - Scope limiting; expiration dates; minimum access principle
3. [GitLab token overview | GitLab Docs](https://docs.gitlab.com/security/tokens/) - Avoid personal tokens in CI/CD; project tokens preferred for automation

**Disagreement**: [Personal access tokens](https://docs.gitlab.com/user/profile/personal_access_tokens/) warns against CI/CD use, but RaiSE is user CLI not CI/CD

**Implication**:
- **MVP**: Personal access tokens (easy setup, user controls scope)
- **Production**: Consider OAuth2 flow for better security posture
- **Best practice**: Minimal scopes (read_api, write_repository for issues)
- **User education**: Token rotation, expiration, revocation

---

### Claim 10: Work Items Widgets Architecture Enables Extensibility

**Confidence**: MEDIUM (newer API, less production evidence)

**Evidence**:
1. [Migrate epic APIs to work items](https://docs.gitlab.com/api/graphql/epic_work_items_api_migration_guide/) - Widgets represent specific features (health status, assignees, dates, hierarchy)
2. [Work items and work item types | GitLab Docs](https://docs.gitlab.com/development/work_items/) - New epics live in issues table; unified model
3. [Epics | GitLab Docs](https://docs.gitlab.com/user/group/epics/) - Dynamic date management (scans child epics/issues for earliest start, latest due)

**Disagreement**: None, but limited production examples (recent migration)

**Implication**: Work Items API design supports:
- **Custom fields** via widgets (extensibility for RaiSE metadata)
- **Unified queries** (Issues and Epics as Work Items)
- **Future-proofing** (GitLab's strategic direction)

**Risk**: API still stabilizing (17.0+); potential breaking changes before v5.

---

## Patterns & Paradigm Shifts

### Architectural Patterns

1. **Polling + Webhooks Hybrid**
   - **Pattern**: Defensive polling (ETag-optimized) as primary mechanism, webhooks as acceleration
   - **Rationale**: Webhook auto-disable fragility, no retry guarantees
   - **Implementation**: Poll every N minutes, webhook triggers immediate poll

2. **Async Webhook Processing**
   - **Pattern**: Webhook endpoint responds immediately (<10s), queues event for async processing
   - **Rationale**: Avoid timeout-based auto-disable; handle duplicate deliveries
   - **Implementation**: Queue (Redis/SQLite) + background worker

3. **IID-Based Sync State**
   - **Pattern**: Store `gitlab_iid` as stable identifier, `gitlab_id` as metadata
   - **Rationale**: IID stable across migrations (Epic → Work Item), required for API calls
   - **Implementation**: Sync table with `(project_id, iid)` as lookup key

4. **Last-Write-Wins Conflict Resolution**
   - **Pattern**: Compare `updated_at` timestamps, newer wins; detect conflicts, prompt user
   - **Rationale**: Bidirectional sync has unavoidable race conditions
   - **Implementation**: Store `last_synced_at`, compare with `updated_at` on both sides

5. **Exponential Backoff with Jitter**
   - **Pattern**: On 429 (rate limit), respect Retry-After or backoff exponentially with random jitter
   - **Rationale**: Rate limits are instance-specific, hardcoding fails
   - **Implementation**: Use python-gitlab's built-in handling or implement per spec

### Paradigm Shifts

1. **REST → GraphQL for Epics**
   - **Shift**: Epic sync requires GraphQL Work Items API (REST deprecated)
   - **Impact**: Different error handling, query language, pagination model
   - **Timeline**: GitLab 17.0+ (2024), removal in API v5 (TBD)

2. **Webhooks as Optimization, Not Primary**
   - **Shift**: Industry pattern (Stripe, Shopify) treats webhooks as reliable; GitLab does not
   - **Impact**: Must design for webhook failure as normal, not exceptional
   - **Justification**: Auto-disable after 4 failures, no exponential retry, lost events

3. **Unified Work Items Model**
   - **Shift**: Issues, Epics, Requirements → single Work Item type with widgets
   - **Impact**: Sync can use common code path for different types
   - **Timeline**: Migration ongoing (GitLab 17+)

---

## GitLab vs JIRA Comparison

### API Design Differences

| Aspect | GitLab | JIRA | Implication |
|--------|--------|------|-------------|
| **Pagination** | Keyset (>50k) or offset | Offset with startAt | GitLab more scalable for large datasets |
| **Epics API** | GraphQL Work Items (REST deprecated) | REST Epics API (stable) | GitLab requires GraphQL knowledge for Epics |
| **Rate Limits** | Instance-specific, Retry-After header | Fixed (Cloud), 429 responses | GitLab less predictable across instances |
| **Webhooks** | Auto-disable after failures | More tolerant | GitLab requires defensive polling |
| **ID Model** | ID (global) vs IID (scoped) | Key (project-scoped) | GitLab has dual IDs (use IID) |
| **Versioning** | REST v4 (stable), GraphQL versionless | REST v2/v3 deprecated → v3 | GitLab GraphQL more future-proof |
| **Auth** | Personal/Project/OAuth tokens | API tokens, OAuth | Similar patterns |

### Integration Complexity

**GitLab Advantages**:
- Built-in JIRA integration (reference implementation available)
- GraphQL reduces over-fetching (sparse fields, batching)
- ETag caching for efficient polling

**GitLab Challenges**:
- Epics API migration (REST → GraphQL) creates transition complexity
- Webhook fragility requires polling fallback
- ID vs IID confusion (common gotcha)
- Instance-specific rate limits (harder to predict)

**JIRA Advantages** (from comparison):
- Mature, stable REST API for all resources
- More webhook reliability (based on general industry patterns)
- Predictable rate limits (SaaS)

**Recommendation**: GitLab integration will be ~30% more complex due to:
1. GraphQL Work Items for Epics (learning curve)
2. Defensive polling architecture (webhook unreliability)
3. IID vs ID dual tracking

---

## Gaps & Unknowns

### Insufficient Evidence

1. **Incremental Sync Timestamp Strategy**
   - **Gap**: No authoritative guide on timestamp-based incremental sync
   - **What we know**: Events API supports timestamp filtering, Resource State Events API tracks changes
   - **What's missing**: Best practice for `last_synced_at` storage, handling clock skew, deduplication
   - **Next step**: Prototype and validate incremental sync pattern

2. **Conflict Resolution Best Practices**
   - **Gap**: GitLab docs acknowledge race conditions but don't prescribe resolution strategies
   - **What we know**: Bidirectional sync is fragile, webhooks help but don't eliminate conflicts
   - **What's missing**: Industry patterns for conflict UI, merge strategies, user workflows
   - **Next step**: Study Logseq sync, Linear sync, or similar tools for patterns

3. **Work Items API Stability**
   - **Gap**: Recent migration (17.0+) means limited production battle-testing
   - **What we know**: IID stable, widgets extensible, GraphQL versionless
   - **What's missing**: Real-world gotchas, breaking changes, edge cases
   - **Risk**: Early adoption of Work Items may encounter undocumented issues
   - **Mitigation**: Start with REST Issues (stable), migrate to Work Items Epics later

4. **Sparse Fieldsets Support**
   - **Gap**: No GitLab-specific documentation on REST API field filtering
   - **What we know**: GraphQL supports sparse field selection (query only needed fields)
   - **What's missing**: Whether REST API supports `fields` param for performance
   - **Next step**: Test REST API with `fields` param, fall back to GraphQL if unsupported

5. **Sync State Storage Patterns**
   - **Gap**: No consensus on where/how to store sync metadata (ETags, timestamps, IDs)
   - **What we know**: Need to track per-resource sync state
   - **What's missing**: Schema design, SQLite vs Redis vs file-based, per-user vs global
   - **Next step**: Design sync state schema (likely SQLite for RaiSE CLI)

### Areas Requiring Testing

1. ETag support per endpoint (some broken per issue #371991)
2. Rate limit behavior on different instance types (SaaS vs self-hosted)
3. Webhook delivery reliability under load
4. Work Items API error handling and edge cases
5. IID stability during Epic → Work Item migration (verify on test instance)

---

## Common Gotchas & Pitfalls

### API Usage Gotchas

1. **ID vs IID Confusion** (Claim 3)
   - **Gotcha**: Using global `id` instead of scoped `iid` in API requests
   - **Impact**: 404 errors, wrong resource fetched
   - **Fix**: Always use IID for Issues/Epics API calls

2. **Null Boolean Fields**
   - **Gotcha**: Boolean fields can be `null`, not just `true`/`false`
   - **Impact**: Logic errors if treating null as false
   - **Fix**: Explicit null checks: `if field is not None and field:`

3. **Deprecated Field Migration**
   - **Gotcha**: `assignee` → `assignees` (single → array), `epic_iid` → `epic.iid`
   - **Impact**: Using deprecated fields breaks in API v5
   - **Fix**: Use current field names from v4 docs

4. **Uninitialized Repository**
   - **Gotcha**: Integration setup fails on repos without commits
   - **Impact**: "Test Failed" errors during webhook configuration
   - **Fix**: Initialize repo or skip webhook setup for empty projects

5. **Keyset Pagination Surprise**
   - **Gotcha**: Pagination switches from offset to keyset at 50k records
   - **Impact**: Offset-based logic breaks for large datasets
   - **Fix**: Use Link headers, not manual offset calculation

### Webhook Gotchas

6. **Auto-Disable Cascade**
   - **Gotcha**: 4 consecutive failures → 1min disable, escalates to 24h, then permanent
   - **Impact**: Webhook stops working silently after temporary outage
   - **Fix**: Monitor webhook status, re-enable after fixing issues

7. **No Exponential Retry**
   - **Gotcha**: Expecting Stripe/Shopify-style retries; GitLab only retries 5xx for 24h
   - **Impact**: Single failure = lost event for 4xx errors
   - **Fix**: Defensive polling as primary sync mechanism

8. **Race Condition Payloads**
   - **Gotcha**: Webhook payload may not reflect current state if concurrent updates
   - **Impact**: Sync applies stale data
   - **Fix**: Use webhook as trigger, fetch current state via API (not payload)

### Sync Architecture Gotchas

9. **Bidirectional Conflict Naivety**
   - **Gotcha**: Assuming last-write-wins is safe without conflict detection
   - **Impact**: Silent data loss when concurrent edits occur
   - **Fix**: Detect conflicts (timestamp comparison), prompt user resolution

10. **Personal Token in CI/CD**
    - **Gotcha**: Using personal access tokens for automation (bad practice per docs)
    - **Impact**: Token tied to user, expires unexpectedly
    - **Fix**: For automation, use project tokens; for CLI, personal tokens OK

---

## Recommended Sync Architecture

### Phase 1: MVP (Issues Only, Unidirectional GitLab → RaiSE)

**Technology Stack**:
- python-gitlab library (mature, handles rate limits/pagination)
- REST API for Issues (stable, well-documented)
- SQLite for sync state (local CLI tool)
- Personal access tokens (user-controlled)

**Sync Strategy**:
- Polling-based (ETag-optimized)
- Incremental sync using `updated_at` timestamp
- No webhooks (reduce complexity)

**Sync State Schema**:
```sql
CREATE TABLE gitlab_sync_state (
    project_id TEXT NOT NULL,
    resource_type TEXT NOT NULL,  -- 'issue', 'epic'
    gitlab_iid INTEGER NOT NULL,
    gitlab_id INTEGER NOT NULL,   -- metadata, not used for lookups
    raise_story_id TEXT NOT NULL,
    last_synced_at TIMESTAMP NOT NULL,
    etag TEXT,
    PRIMARY KEY (project_id, resource_type, gitlab_iid)
);
```

**Sync Algorithm**:
```python
def sync_issues(project_id, since=None):
    # 1. Fetch issues updated since last sync
    since = since or get_last_sync_timestamp(project_id)
    issues = gitlab_client.issues.list(
        updated_after=since,
        iterator=True  # lazy pagination
    )

    # 2. For each issue, map to RaiSE story
    for issue in issues:
        story = map_issue_to_story(issue)

        # 3. Detect conflicts (if bidirectional)
        if story.updated_at > issue.updated_at:
            handle_conflict(story, issue)
        else:
            update_story(story)

        # 4. Update sync state
        save_sync_state(
            project_id=project_id,
            gitlab_iid=issue.iid,  # stable ID
            gitlab_id=issue.id,
            raise_story_id=story.id,
            last_synced_at=now()
        )
```

**Rate Limit Handling**: Use python-gitlab default (auto-sleep on 429)

**Error Handling**:
- Retry 5xx with exponential backoff
- Log and skip 4xx (client errors)
- Alert on auth failures (401/403)

---

### Phase 2: Epics + Bidirectional

**Additions**:
- GraphQL client for Work Items (Epics)
- Webhook endpoint (async queue-based processing)
- Conflict detection UI

**Webhook Pattern**:
```python
# Endpoint responds immediately
@app.post("/webhooks/gitlab")
async def gitlab_webhook(request):
    payload = await request.json()

    # Queue for async processing (don't block response)
    await queue.enqueue("sync_from_webhook", payload)

    return {"status": "ok"}  # <10s response time

# Background worker processes queue
async def sync_from_webhook(payload):
    # Use webhook as trigger, fetch current state
    issue_iid = payload["object_attributes"]["iid"]
    project_id = payload["project_id"]

    # Fetch current state (avoid race condition payload staleness)
    issue = gitlab_client.issues.get(project_id, issue_iid)

    # Standard sync logic
    sync_issue(issue)
```

**Conflict Resolution**:
```python
def handle_conflict(local_story, remote_issue):
    if abs(local_story.updated_at - remote_issue.updated_at) < 60:
        # Within 60s = likely race condition
        prompt_user_resolution(local_story, remote_issue)
    elif local_story.updated_at > remote_issue.updated_at:
        # Local is newer, push to GitLab
        push_to_gitlab(local_story)
    else:
        # Remote is newer, pull from GitLab
        pull_from_gitlab(remote_issue)
```

---

### Phase 3: Production Hardening

**Additions**:
- OAuth2 flow (better than personal tokens)
- Webhook monitoring and auto-re-enable
- ETag caching for all resources
- GraphQL batching for nested queries

**Monitoring**:
- Webhook delivery success rate
- Sync lag (time between GitLab update and RaiSE update)
- Conflict rate
- Rate limit hit rate

---

## Key Decisions for ADR

### Decision 1: REST vs GraphQL for Issues

**Options**:
- A) REST API only
- B) GraphQL only
- C) Hybrid (REST for Issues, GraphQL for Epics)

**Recommendation**: **C) Hybrid**

**Rationale**:
- REST Issues API is stable, mature, well-documented (low risk)
- GraphQL required for Epics (Work Items API, REST deprecated)
- python-gitlab supports both REST and GraphQL
- Can migrate Issues to GraphQL later if needed

**Trade-off**: Code complexity (two API clients)

---

### Decision 2: Polling vs Webhooks Primary Mechanism

**Options**:
- A) Webhooks-only
- B) Polling-only
- C) Webhooks + defensive polling

**Recommendation**: **B) Polling-only for MVP, C) Webhooks + polling for Phase 2**

**Rationale**:
- MVP: Polling simpler, no webhook infrastructure, sufficient for CLI tool
- Phase 2: Webhooks enable real-time sync, but require async processing and fallback
- GitLab webhook fragility (auto-disable) makes webhook-only risky

**Trade-off**: Polling has higher latency (minutes), webhooks require more infrastructure

---

### Decision 3: Sync State Storage

**Options**:
- A) SQLite (local file)
- B) Redis (requires server)
- C) File-based (JSON/YAML)

**Recommendation**: **A) SQLite**

**Rationale**:
- CLI tool context (local storage)
- SQLite supports transactions, indexes, queries
- No external dependencies (Redis needs server)
- File-based too fragile (concurrent access, corruption)

**Trade-off**: Not suitable for multi-user/server context (revisit if RaiSE becomes SaaS)

---

### Decision 4: Conflict Resolution Strategy

**Options**:
- A) Last-write-wins (automatic)
- B) Conflict detection + user resolution
- C) GitLab always wins (unidirectional)

**Recommendation**: **B) Conflict detection + user resolution for Phase 2**

**Rationale**:
- Silent overwrites (A) risk data loss
- Unidirectional (C) limits value of sync
- User resolution (B) respects user intent, prevents data loss

**Trade-off**: UX complexity (conflict UI)

---

## Implementation Risks

### Risk 1: Work Items API Instability

**Risk**: Recent migration (17.0+) means potential breaking changes, undocumented edge cases

**Likelihood**: MEDIUM
**Impact**: HIGH (Epic sync breaks)

**Mitigation**:
- Start with REST Issues (stable)
- Delay Epic sync until Work Items API more mature
- Monitor GitLab release notes for breaking changes
- Test against multiple GitLab versions (17.0, 17.6, 18.0)

---

### Risk 2: Webhook Auto-Disable in Production

**Risk**: Temporary outage or slow processing causes permanent webhook disable

**Likelihood**: MEDIUM
**Impact**: MEDIUM (sync lag, not failure)

**Mitigation**:
- Defensive polling as fallback (sync continues without webhooks)
- Monitor webhook status via API
- Auto-re-enable webhooks after fixing issues
- Async processing ensures <10s response time

---

### Risk 3: Rate Limit Unpredictability Across Instances

**Risk**: Self-hosted GitLab may have different rate limits than SaaS

**Likelihood**: HIGH
**Impact**: MEDIUM (sync slower, not broken)

**Mitigation**:
- Respect Retry-After header (instance-specific)
- Exponential backoff when header missing
- User-configurable sync rate (conservative default)
- Use python-gitlab's built-in rate limit handling

---

### Risk 4: Bidirectional Sync Data Loss

**Risk**: Concurrent edits overwrite each other silently

**Likelihood**: LOW (RaiSE CLI = single user typically)
**Impact**: HIGH (user data loss)

**Mitigation**:
- Conflict detection (timestamp comparison)
- User resolution UI for conflicts
- Audit log of sync operations
- Dry-run mode for testing sync

---

## Next Steps

### Immediate (Before ADR)

1. **Prototype REST Issues Sync**
   - Validate python-gitlab library
   - Test ETag caching on Issues endpoint
   - Measure sync performance (issues/second)

2. **Test Work Items API**
   - Create test Epic on GitLab instance
   - Query via GraphQL Work Items API
   - Verify IID stability during migration

3. **Design Sync State Schema**
   - Finalize SQLite schema
   - Migration strategy for schema changes
   - Backup/restore sync state

### Post-ADR (Implementation)

4. **Build MVP (Issues Only)**
   - python-gitlab integration
   - Polling-based sync
   - Incremental sync with timestamps
   - CLI commands: `raise sync pull gitlab`, `raise sync status`

5. **Add Epics (Phase 2)**
   - GraphQL client for Work Items
   - Hierarchy mapping (Epic → Issues)
   - Nested sync (sync Epic pulls associated Issues)

6. **Add Webhooks (Phase 2)**
   - Webhook endpoint (FastAPI/Flask)
   - Async queue (Redis or SQLite-based)
   - Monitoring dashboard

### Research Follow-Up

7. **Deep Dive: Conflict Resolution UX**
   - Study Linear, Logseq, Obsidian sync UX
   - Design RaiSE conflict resolution flow
   - Prototype conflict UI

8. **Benchmark: Sync Performance**
   - Measure sync time for 100, 1k, 10k issues
   - Identify bottlenecks (API latency, DB writes, mapping)
   - Optimize critical path

---

## References

See [Evidence Catalog](sources/evidence-catalog.md) for full source list with evidence levels.

**Key Official Docs**:
- [GitLab REST API](https://docs.gitlab.com/api/rest/)
- [GitLab GraphQL API](https://docs.gitlab.com/api/graphql/)
- [Work Items API Migration Guide](https://docs.gitlab.com/api/graphql/epic_work_items_api_migration_guide/)
- [Webhooks](https://docs.gitlab.com/user/project/integrations/webhooks/)

**Key Libraries**:
- [python-gitlab](https://github.com/python-gitlab/python-gitlab) (2.5k+ stars)
- [terraform-provider-gitlab](https://registry.terraform.io/providers/gitlabhq/gitlab/latest/docs)

**Comparison Resources**:
- [GitLab Jira Integration Guide](https://www.getint.io/blog/jira-gitlab-integration-guide)
- [Integrate GitLab with Jira | Atlassian](https://support.atlassian.com/jira-cloud-administration/docs/integrate-gitlab-with-jira/)

---

**Research Metadata**:
- Tool/model used: WebSearch (Claude Code)
- Search date: 2026-02-14
- Prompt version: 1.0
- Researcher: Claude Sonnet 4.5
- Total time: ~4 hours (evidence gathering + synthesis)
- Total sources: 28 (13 Very High, 8 High, 6 Medium, 1 Low)
