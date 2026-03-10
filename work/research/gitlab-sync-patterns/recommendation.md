# Recommendation: GitLab Sync Architecture

**Research ID**: gitlab-sync-20260214
**Decision Context**: RaiSE GitLab integration (second platform after JIRA)
**Date**: 2026-02-14

---

## Decision

Implement **hybrid polling + webhook architecture** with:
- **REST API for Issues** (stable, mature)
- **GraphQL Work Items API for Epics** (required, REST deprecated)
- **Polling-first strategy** with ETag caching (defensive, reliable)
- **Webhooks as optimization** (Phase 2, after MVP proves polling)
- **IID-based sync state** (stable across migrations)
- **Conflict detection with user resolution** (Phase 2, bidirectional)

**Phased Rollout**:
- **Phase 1 (MVP)**: Unidirectional Issues sync (GitLab → RaiSE), polling-only, REST API
- **Phase 2**: Add Epics (GraphQL), bidirectional sync, webhook acceleration
- **Phase 3**: Production hardening (OAuth, monitoring, batching)

---

## Confidence

**MEDIUM-HIGH**

**High confidence elements**:
- REST API for Issues (13 Very High evidence sources, mature API)
- Webhook fragility requiring polling fallback (3+ Very High sources, consistent findings)
- IID as stable identifier (3+ sources, official migration guide confirms)
- python-gitlab as implementation library (2.5k stars, official wrapper, proven patterns)

**Medium confidence elements**:
- Work Items API stability (recent migration in 17.0, limited production evidence)
- Conflict resolution UX (no clear industry patterns found, requires prototyping)
- Optimal sync frequency (needs benchmarking)

---

## Rationale

### Why Polling-First, Not Webhook-First?

**Evidence-based reasons**:

1. **Webhook Fragility** (HIGH confidence)
   - Auto-disabled after 4 consecutive failures (extends to 24h, then permanent)
   - No exponential retry (unlike Stripe, Shopify, GitHub)
   - Single failed delivery = lost event
   - Sources: [GitLab Webhooks Docs](https://docs.gitlab.com/user/project/integrations/webhooks/), [Hookdeck Guide](https://hookdeck.com/webhooks/platforms/guide-to-gitlab-webhooks-features-and-best-practices)

2. **CLI Tool Context** (HIGH confidence)
   - RaiSE is CLI tool, not always-on service
   - User may be offline when webhook fires
   - Polling aligns with user-initiated sync (`raise sync pull`)
   - Webhooks require infrastructure (server, queue, monitoring)

3. **ETag Caching Makes Polling Efficient** (HIGH confidence)
   - If-None-Match → 304 Not Modified (no DB query on GitLab side)
   - ETags stored in Redis, invalidated on resource change
   - python-gitlab handles automatically
   - Source: [GitLab ETag Polling Docs](https://docs.gitlab.com/development/polling/)

**Trade-off**: Polling has higher latency (minutes) vs webhook near-real-time (seconds)

**Mitigation**: Phase 2 adds webhooks as **optimization**, not replacement for polling

---

### Why REST for Issues, GraphQL for Epics?

**Evidence-based reasons**:

1. **Epics REST API Deprecated** (HIGH confidence)
   - Deprecated in GitLab 17.0, removal planned in API v5
   - Work Items API (GraphQL) is replacement
   - No choice for future-proofing
   - Sources: [Epics API Deprecated](https://docs.gitlab.com/api/epics/), [Work Items Migration Guide](https://docs.gitlab.com/api/graphql/epic_work_items_api_migration_guide/)

2. **Issues REST API Stable** (HIGH confidence)
   - Mature, well-documented, no deprecation plans
   - python-gitlab has excellent REST support
   - Lower complexity than GraphQL
   - Source: [Issues API Docs](https://docs.gitlab.com/api/issues/)

3. **GraphQL Learning Curve** (MEDIUM confidence)
   - Different error handling patterns
   - Query language complexity
   - Less familiar to most developers
   - Minimize usage to where required (Epics)

**Trade-off**: Dual API clients (REST + GraphQL) increases code complexity

**Mitigation**: python-gitlab supports both; isolate GraphQL to Epic sync module

---

### Why IID-Based Sync State?

**Evidence-based reasons**:

1. **IID Stable Across Migrations** (HIGH confidence)
   - Epic ID changes when migrated to Work Item
   - Epic IID = Work Item IID (stable)
   - Required for API requests: `GET /projects/42/issues/5` (IID=5, not ID)
   - Source: [Work Items Migration Guide](https://docs.gitlab.com/api/graphql/epic_work_items_api_migration_guide/)

2. **Human-Readable** (MEDIUM confidence)
   - IID = issue #123 in project
   - Easier for debugging, user communication
   - Global ID is opaque (46372891)

3. **Common Gotcha** (HIGH confidence)
   - ID vs IID confusion is top API pitfall
   - Avoiding by design (always use IID)
   - Source: [REST API Troubleshooting](https://docs.gitlab.com/api/rest/troubleshooting/)

**Implementation**: Store both `gitlab_id` (metadata) and `gitlab_iid` (primary key)

---

### Why Conflict Detection + User Resolution?

**Evidence-based reasons**:

1. **Bidirectional Sync Has Race Conditions** (HIGH confidence)
   - Acknowledged limitation in GitLab docs
   - No automatic resolution prevents data loss
   - Source: [Bidirectional Mirroring](https://docs.gitlab.com/user/project/repository/mirror/bidirectional/)

2. **CLI Context = Single User** (MEDIUM confidence)
   - Lower conflict likelihood than multi-user SaaS
   - User can resolve conflicts interactively
   - Terminal UI for conflict resolution (diffing, choosing version)

3. **Last-Write-Wins Too Naive** (MEDIUM confidence)
   - Silent data loss if user unaware
   - Violates RaiSE principle: respect user intent
   - Better UX: show conflict, let user decide

**Trade-off**: UX complexity (conflict resolution flow)

**Mitigation**: Phase 2 feature (not MVP); learn from Logseq/Obsidian sync UX

---

## Trade-offs

### Trade-off 1: Polling Latency vs Webhook Complexity

**Accepting**: Minutes of sync latency in MVP
**Gaining**: Simpler architecture, no webhook infrastructure
**Mitigating**: Phase 2 adds webhooks; user can trigger sync manually

**Justification**: CLI tool context + webhook fragility makes polling pragmatic

---

### Trade-off 2: Dual API Clients (REST + GraphQL)

**Accepting**: Code complexity (two API patterns)
**Gaining**: Stability (REST Issues) + Future-proofing (GraphQL Epics)
**Mitigating**: python-gitlab supports both; isolate to modules

**Justification**: Epics REST deprecation forces GraphQL; keeping REST for Issues avoids premature migration

---

### Trade-off 3: IID + ID Dual Storage

**Accepting**: Extra field in sync state (global ID stored but not used)
**Gaining**: Future flexibility if GitLab exposes global-ID-only APIs
**Mitigating**: SQLite storage is cheap

**Justification**: Defensive storage; minimal cost, potential future benefit

---

### Trade-off 4: Delayed Conflict Resolution (Phase 2)

**Accepting**: MVP is unidirectional (GitLab → RaiSE only)
**Gaining**: Faster MVP delivery, simpler first version
**Mitigating**: Clear roadmap to bidirectional in Phase 2

**Justification**: Unidirectional proves sync value; bidirectional adds complexity

---

## Risks

### Risk 1: Work Items API Instability

**What could go wrong**: Breaking changes in Work Items API before API v5

**Likelihood**: MEDIUM (new API, GitLab 17.0+)
**Impact**: HIGH (Epic sync breaks)

**Mitigation**:
- Delay Epic sync until Phase 2 (not MVP)
- Monitor GitLab release notes (17.x → 18.x)
- Test against multiple GitLab versions
- Version lock python-gitlab library
- Fallback: Use deprecated REST Epics API temporarily if Work Items breaks

**Detection**: CI tests against GitLab SaaS (latest version)

---

### Risk 2: Webhook Auto-Disable in Production

**What could go wrong**: Temporary outage or slow processing → permanent webhook disable

**Likelihood**: MEDIUM (4 failures = disable)
**Impact**: MEDIUM (sync lag, not total failure due to polling fallback)

**Mitigation**:
- Polling as primary mechanism (webhook is optimization)
- Monitor webhook status via API
- Auto-re-enable webhooks after resolution
- Async processing ensures <10s response time (avoid timeouts)

**Detection**: Webhook delivery metrics dashboard

---

### Risk 3: Rate Limit Unpredictability

**What could go wrong**: Self-hosted GitLab has stricter limits than SaaS

**Likelihood**: HIGH (instance-specific configuration)
**Impact**: MEDIUM (slower sync, not broken)

**Mitigation**:
- Respect Retry-After header (instance-specific)
- Exponential backoff when missing
- User-configurable sync rate (default: conservative)
- python-gitlab auto-handles (obeys 429 by default)

**Detection**: Log rate limit hits; adjust defaults if >5% of requests hit limits

---

### Risk 4: Bidirectional Sync Data Loss

**What could go wrong**: Concurrent edits overwrite each other silently

**Likelihood**: LOW (CLI = single user context)
**Impact**: HIGH (user data loss, trust erosion)

**Mitigation**:
- Conflict detection (compare `updated_at` timestamps)
- User resolution UI (show diff, choose version)
- Audit log of sync operations
- Dry-run mode (`raise sync pull --dry-run`)

**Detection**: Unit tests for conflict scenarios; manual QA with concurrent edits

---

### Risk 5: ETag Caching Broken on Some Endpoints

**What could go wrong**: ETag optimization doesn't work, every poll hits DB

**Likelihood**: MEDIUM (issue #371991 shows some endpoints broken)
**Impact**: LOW (performance degradation, not functional break)

**Mitigation**:
- Test ETag support per endpoint (Issues, Epics)
- Fallback to timestamp-based incremental sync if ETags unreliable
- Document which endpoints support ETags

**Detection**: Monitor 304 vs 200 response rates; <50% 304 = ETag not working

---

## Alternatives Considered

### Alternative 1: GraphQL-Only (REST + GraphQL)

**Why not chosen**:
- Issues REST API is stable, mature, well-documented
- GraphQL has learning curve, different error patterns
- No benefit for Issues (simple CRUD, no complex nesting)
- python-gitlab REST support more mature

**When to reconsider**: If Issues REST API deprecated (no signals of this)

---

### Alternative 2: Webhooks-Only (Polling + Webhooks)

**Why not chosen**:
- GitLab webhooks fragile (auto-disable after 4 failures)
- No exponential retry (lost events)
- CLI tool often offline (webhooks miss)
- Requires infrastructure (server, queue, monitoring)

**When to reconsider**: If RaiSE becomes SaaS (always-on server)

---

### Alternative 3: Last-Write-Wins Automatic Conflict Resolution (Conflict Detection + User Resolution)

**Why not chosen**:
- Silent data loss risk
- Violates user intent principle
- Low implementation cost to detect conflicts
- CLI context allows interactive resolution

**When to reconsider**: If conflict rate <0.1% in production (very rare)

---

### Alternative 4: File-Based Sync State (SQLite)

**Why not chosen**:
- Concurrent access issues (corruption risk)
- No transaction support
- No indexes for efficient queries
- YAML/JSON parsing overhead

**When to reconsider**: Never (SQLite is superior for structured data)

---

### Alternative 5: OAuth-Only Auth (Personal Tokens + OAuth)

**Why not chosen**:
- OAuth complexity for MVP (token refresh, PKCE flow)
- Personal tokens sufficient for CLI (user controls scope, expiration)
- OAuth better for multi-user SaaS, not single-user CLI

**When to reconsider**: Phase 3 (production hardening) or if enterprise deployment requires it

---

## Implementation Checklist

### Phase 1: MVP (Issues Only, Unidirectional)

**Scope**: GitLab Issues → RaiSE Stories (pull only)

- [ ] Set up python-gitlab client with personal token auth
- [ ] Design SQLite sync state schema (`gitlab_sync_state` table)
- [ ] Implement polling loop with ETag caching
- [ ] Implement incremental sync using `updated_at` timestamp
- [ ] Map GitLab Issue fields → RaiSE Story fields
- [ ] CLI command: `raise sync pull gitlab --project <id>`
- [ ] CLI command: `raise sync status gitlab` (show last sync time, count)
- [ ] Handle rate limits (respect Retry-After, exponential backoff)
- [ ] Error handling: retry 5xx, log 4xx, alert on auth failures
- [ ] Unit tests: sync logic, field mapping, error handling
- [ ] Integration tests: against GitLab test instance
- [ ] Documentation: setup guide, field mapping reference

**Acceptance Criteria**:
- Sync 100 issues in <30 seconds
- ETag caching reduces API calls by >50% on repeat sync
- Rate limit handling: no crashes, respects 429
- Data accuracy: 100% field mapping correctness

---

### Phase 2: Epics + Bidirectional + Webhooks

**Scope**: Add Epic sync, bidirectional, webhook acceleration

- [ ] GraphQL client for Work Items API
- [ ] Map GitLab Epic → RaiSE Epic
- [ ] Hierarchy sync: Epic → Issues (nested query)
- [ ] Bidirectional sync: RaiSE → GitLab push
- [ ] Conflict detection: timestamp comparison
- [ ] Conflict resolution UI: show diff, choose version
- [ ] Webhook endpoint (FastAPI/Flask)
- [ ] Async queue for webhook processing (Redis or SQLite-based)
- [ ] Webhook monitoring: delivery rate, failures
- [ ] Auto-re-enable webhooks after failures
- [ ] CLI command: `raise sync push gitlab` (RaiSE → GitLab)
- [ ] CLI command: `raise sync conflicts` (list unresolved conflicts)
- [ ] Integration tests: bidirectional sync, conflict scenarios

**Acceptance Criteria**:
- Webhook delivery success rate >95%
- Conflict detection: 100% of concurrent edits flagged
- Sync lag (webhook-triggered): <10 seconds

---

### Phase 3: Production Hardening

**Scope**: OAuth, monitoring, batching, optimization

- [ ] OAuth2 PKCE flow (replace personal tokens)
- [ ] GraphQL batching (multiple queries in single request)
- [ ] Monitoring dashboard: sync lag, rate limit hits, conflicts
- [ ] Audit log: all sync operations with timestamps
- [ ] Dry-run mode: `--dry-run` flag for safe testing
- [ ] Performance optimization: batch DB writes, parallel API calls
- [ ] Backup/restore sync state
- [ ] Migration tool: upgrade sync state schema
- [ ] Documentation: production deployment guide

**Acceptance Criteria**:
- OAuth flow <30s to complete
- Monitoring dashboard shows key metrics
- Backup/restore: <1min for 10k issues

---

## Success Metrics

### MVP (Phase 1)

| Metric | Target | Rationale |
|--------|--------|-----------|
| Sync time (100 issues) | <30s | User tolerance for CLI command |
| ETag cache hit rate | >50% | Validate optimization working |
| API error rate | <1% | Reliability (excluding rate limits) |
| Field mapping accuracy | 100% | Data integrity critical |

### Phase 2

| Metric | Target | Rationale |
|--------|--------|-----------|
| Webhook delivery success | >95% | Async processing prevents timeouts |
| Sync lag (webhook) | <10s | Near-real-time feel |
| Conflict detection accuracy | 100% | No silent data loss |
| User conflict resolution rate | >80% | User can resolve most conflicts |

### Phase 3

| Metric | Target | Rationale |
|--------|--------|-----------|
| OAuth adoption | >50% users | Better security posture |
| Sync lag (production) | <5s | Webhook + batching optimizations |
| Rate limit hit rate | <5% requests | Efficient API usage |

---

## Decision Authority

**Decision Maker**: Emilio (RaiSE creator)
**Consulted**: Claude (research + architecture design)
**Informed**: RaiSE early adopters (first client kick-off 2026-02-10)

**ADR Status**: Recommendation ready for review → ADR drafting

---

## References

- **Full Research Report**: [gitlab-sync-report.md](gitlab-sync-report.md)
- **Evidence Catalog**: [sources/evidence-catalog.md](sources/evidence-catalog.md)
- **GitLab Official Docs**: [REST API](https://docs.gitlab.com/api/rest/), [GraphQL API](https://docs.gitlab.com/api/graphql/), [Webhooks](https://docs.gitlab.com/user/project/integrations/webhooks/)
- **python-gitlab Library**: [GitHub](https://github.com/python-gitlab/python-gitlab), [Docs](https://python-gitlab.readthedocs.io/)

---

**Recommendation Version**: 1.0
**Created**: 2026-02-14
**Next Review**: After MVP implementation (Phase 1 complete)
