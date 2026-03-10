# Next Actions: GitLab Sync Research

**Research ID**: gitlab-sync-20260214
**Status**: ✅ Complete
**Created**: 2026-02-14

---

## Governance Linkage

### Immediate Decision Path

1. **Review Recommendation** (Owner: Emilio)
   - Read: `recommendation.md` (10 min)
   - Validate: Trade-offs, risks, phased approach
   - Decision: Approve or request changes

2. **Draft ADR** (Owner: Emilio + Claude)
   - Template: `.raise/templates/decisions/adr-template.md`
   - Input: `recommendation.md` (rationale, trade-offs, risks)
   - Output: `docs/decisions/adr-NNN-gitlab-sync-architecture.md`
   - Status: PENDING (after recommendation review)

3. **Link to Backlog** (Owner: Emilio)
   - Epic: "GitLab Integration" (if not exists, create)
   - Stories:
     - S1: MVP - GitLab Issues Sync (REST, polling, unidirectional)
     - S2: GitLab Epics Sync (GraphQL Work Items)
     - S3: Bidirectional Sync + Conflict Resolution
     - S4: Webhook Acceleration
     - S5: Production Hardening (OAuth, monitoring)
   - Priority: After JIRA integration MVP (GitLab is second platform)

---

## Research Artifacts Inventory

### Navigation
- `README.md` - 15-min overview, file navigation

### Core Documents
- `gitlab-sync-report.md` - Full research with 10 triangulated claims (45 min read)
- `recommendation.md` - Decision, rationale, trade-offs, risks (10 min read)
- `sources/evidence-catalog.md` - 28 sources with evidence ratings (reference)

### Reproducibility
- `prompt.md` - Research prompt used (template-based)

### Future Derivatives
- `derivatives/` - Empty (future: decision matrix, specs, roadmaps)

---

## Key Outputs for ADR

### Decision Statement (from recommendation.md)

> Implement **hybrid polling + webhook architecture** with:
> - REST API for Issues (stable, mature)
> - GraphQL Work Items API for Epics (required, REST deprecated)
> - Polling-first strategy with ETag caching (defensive, reliable)
> - Webhooks as optimization (Phase 2)
> - IID-based sync state (stable across migrations)

### Confidence Level

**MEDIUM-HIGH** (13 Very High sources for REST Issues, but Work Items API newer)

### Trade-offs to Document in ADR

1. Polling latency vs webhook complexity
2. Dual API clients (REST + GraphQL) vs single API
3. IID + ID dual storage
4. Delayed conflict resolution (Phase 2)

### Risks to Document in ADR

1. Work Items API instability (MEDIUM likelihood, HIGH impact)
2. Webhook auto-disable (MEDIUM likelihood, MEDIUM impact)
3. Rate limit unpredictability (HIGH likelihood, MEDIUM impact)
4. Bidirectional sync data loss (LOW likelihood, HIGH impact)
5. ETag caching broken on some endpoints (MEDIUM likelihood, LOW impact)

---

## Implementation Checklist (from recommendation.md)

### Phase 1: MVP (Issues Only)
- [ ] python-gitlab client setup
- [ ] SQLite sync state schema
- [ ] Polling loop with ETag caching
- [ ] Incremental sync (timestamp-based)
- [ ] Field mapping (GitLab Issue → RaiSE Story)
- [ ] CLI: `raise sync pull gitlab`
- [ ] CLI: `raise sync status gitlab`
- [ ] Error handling + rate limits
- [ ] Tests (unit + integration)
- [ ] Documentation

**Target**: Sync 100 issues in <30s, >50% ETag cache hit rate

### Phase 2: Epics + Bidirectional
- [ ] GraphQL client for Work Items
- [ ] Epic → RaiSE Epic mapping
- [ ] Hierarchy sync (Epic → Issues)
- [ ] Bidirectional sync (push to GitLab)
- [ ] Conflict detection + resolution UI
- [ ] Webhook endpoint + async queue
- [ ] Webhook monitoring
- [ ] CLI: `raise sync push gitlab`
- [ ] CLI: `raise sync conflicts`
- [ ] Tests (conflict scenarios)

**Target**: Webhook success >95%, sync lag <10s, conflict detection 100%

### Phase 3: Production Hardening
- [ ] OAuth2 PKCE flow
- [ ] GraphQL batching
- [ ] Monitoring dashboard
- [ ] Audit log
- [ ] Dry-run mode
- [ ] Performance optimization
- [ ] Backup/restore sync state

**Target**: OAuth adoption >50%, sync lag <5s, rate limit hits <5%

---

## Follow-Up Research Needed

### High Priority
1. **Conflict Resolution UX Patterns**
   - Study: Linear, Logseq, Obsidian sync UX
   - Output: UI mockups for conflict resolution
   - Timeline: Before Phase 2 implementation

### Medium Priority
2. **Work Items API Stability Tracking**
   - Monitor: GitLab 17.x → 18.x release notes
   - Test: Against GitLab SaaS (latest version)
   - Timeline: Ongoing during Epic sync development

3. **Sync Performance Benchmarking**
   - Test: 100, 1k, 10k issues sync time
   - Identify: Bottlenecks (API latency, DB writes, mapping)
   - Timeline: After MVP implementation

### Low Priority
4. **Sparse Fieldsets Support**
   - Test: REST API `fields` parameter
   - Fallback: GraphQL if REST doesn't support
   - Timeline: Optimization phase (Phase 3)

---

## Success Criteria (Carry to ADR)

### MVP (Phase 1)
- Sync time (100 issues): <30s
- ETag cache hit rate: >50%
- API error rate: <1%
- Field mapping accuracy: 100%

### Phase 2
- Webhook delivery success: >95%
- Sync lag (webhook): <10s
- Conflict detection accuracy: 100%
- User conflict resolution rate: >80%

### Phase 3
- OAuth adoption: >50% users
- Sync lag (production): <5s
- Rate limit hit rate: <5% requests

---

## Questions for Emilio (Decision Review)

1. **Phasing**: Agree with MVP → Phase 2 → Phase 3 sequence? Or different priorities?
2. **Epics Priority**: How urgent is Epic sync vs Issues-only MVP?
3. **Bidirectional**: Needed for first client (2026-02-10) or later?
4. **Webhooks**: Phase 2 feature or MVP requirement?
5. **Trade-offs**: Any unacceptable trade-offs in recommendation?

---

## Archive Policy

**Keep**:
- All files in `work/research/gitlab-sync-patterns/` (permanent reference)
- Link from ADR to research (traceability)

**Update**:
- README.md with "Status: Archived after ADR-NNN implemented" when complete
- Add "Lessons Learned" section after implementation

**Don't Delete**:
- Evidence catalog (audit trail for decisions)
- Research report (context for future maintainers)

---

**Created**: 2026-02-14
**Owner**: Emilio (decision), Claude (research support)
**Status**: ✅ Research complete, awaiting decision review
