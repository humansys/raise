# JIRA Bidirectional Sync Research

**Research Date**: 2026-02-14
**Status**: Complete
**Confidence**: HIGH
**Timeline**: Pre-March 14, 2026 demo; March 2, 2026 rate limit enforcement

---

## 15-Minute Overview

### The Question

How should RaiSE implement bidirectional sync with JIRA to support:
- Humansys (Atlassian Gold Partner) integration needs
- Coppel client (uses JIRA, first paying customer)
- March 14 webinar demo
- Production-ready reliability

### The Answer

**Implement webhook-first, polling-backup architecture** with entity properties for metadata, field-level conflict resolution, and idempotent event processing.

### Why This Matters

- **Business**: JIRA is primary integration target (Humansys partnership, Coppel client dependency)
- **Timeline**: March 2, 2026 new rate limits enforce (16 days from research)
- **Risk**: Getting sync wrong means data loss, duplicate work, or sync failures in production

### Key Findings

1. **Webhooks + Polling** is production standard (not either/or)
   - Webhooks: Real-time, JIRA retries 5x with backoff
   - Polling: Safety net, 15-min intervals, catches missed events

2. **Entity Properties > Custom Fields** for sync metadata
   - No performance impact on JIRA instance
   - Invisible to end users
   - Queryable via JQL and REST API
   - 32 KB JSON storage per entity

3. **Field-Level Conflict Resolution** required for correctness
   - Last-write-wins: descriptions, non-critical metadata
   - User-prompted: status, assignee, priority (business-critical)
   - Append-only: comments, attachments

4. **Idempotency is non-negotiable**
   - X-Atlassian-Webhook-Identifier for deduplication
   - Webhooks may deliver multiple times
   - Handlers must be idempotent (database checks before create)

5. **Rate Limits Change March 2, 2026** (URGENT)
   - New points-based model (not request-count)
   - Requires field filtering, pagination optimization, caching
   - Monitor X-RateLimit-Remaining, implement backoff

### Evidence Quality

- **32 sources** analyzed
- **28% Very High** evidence (Atlassian official docs)
- **41% High** evidence (Exalate, Unito, production implementations)
- **Temporal coverage**: 2020-2026

### Next Steps

1. **Immediate** (pre-March 2): Implement field filtering and rate limit monitoring
2. **Phase 1** (March 14 demo): One-way sync (RaiSE → JIRA) with webhook registration
3. **Phase 2** (post-demo): Bidirectional sync with conflict resolution and polling backup

---

## Document Structure

This research contains 4 main documents:

### 1. [Synthesis](synthesis.md) - FULL FINDINGS
**Read time**: 20 minutes

**What's in it**:
- 8 major claims with triangulated evidence (3+ sources each)
- Patterns & paradigm shifts identified across sources
- Gaps & unknowns requiring further investigation
- Detailed implications for RaiSE architecture

**When to read**: Deep dive into research findings; understanding trade-offs

---

### 2. [Recommendation](recommendation.md) - ACTIONABLE DECISION
**Read time**: 15 minutes

**What's in it**:
- Specific decision with confidence level
- Rationale based on evidence
- Trade-offs accepted/rejected
- Risks with mitigations
- Alternatives considered (and why rejected)
- Implementation roadmap (3 phases)
- Technical specifications (entity property schema, webhook events, API optimization)
- Success metrics

**When to read**: Making implementation decisions; planning architecture; writing ADR

---

### 3. [Evidence Catalog](sources/evidence-catalog.md) - SOURCE VERIFICATION
**Read time**: 30 minutes (skim), 90 minutes (full read)

**What's in it**:
- All 32 sources with metadata (type, evidence level, date, key finding, relevance)
- Summary statistics (evidence distribution, temporal coverage)
- Organized by topic (webhooks, API patterns, sync tools, conflict resolution, etc.)

**When to read**: Verifying claims; finding original sources; checking evidence quality

---

### 4. [Research Prompt](prompt.md) - REPRODUCIBILITY
**Read time**: 10 minutes

**What's in it**:
- Research question and decision context
- Search strategy and keywords used
- Evidence evaluation criteria
- Triangulation requirements
- Quality checklist

**When to read**: Reproducing research; understanding methodology; running similar research

---

## Quick Navigation

**I need to...**

- **Make a decision**: Read [Recommendation](recommendation.md)
- **Understand the evidence**: Read [Synthesis](synthesis.md)
- **Verify a claim**: Check [Evidence Catalog](sources/evidence-catalog.md)
- **Reproduce the research**: See [Research Prompt](prompt.md)
- **Get the gist**: You're reading it (this README)

---

## Key Insights Summary

### Architecture Pattern: Webhook + Polling Hybrid

```
┌─────────────┐                    ┌─────────────┐
│             │                    │             │
│    RaiSE    │◄───── Webhooks ────┤    JIRA     │
│             │       (primary)    │             │
│             │                    │             │
│             │─────► Polling ─────►│             │
│             │   (15-min backup)  │             │
└─────────────┘                    └─────────────┘
       │                                  │
       │                                  │
       └──── Entity Properties ───────────┘
             (sync metadata)
```

### Conflict Resolution Strategy

| Field Type | Strategy | Rationale |
|------------|----------|-----------|
| Description | Last-write-wins | Low conflict risk; easy to revert manually |
| Comments | Append-only | Never overwrite; preserve all contributions |
| Status | User-prompted | Business-critical; requires human judgment |
| Assignee | User-prompted | Business-critical; affects accountability |
| Priority | User-prompted | Business-critical; affects prioritization |
| Labels | Merge (union) | Low conflict risk; multiple values supported |
| Attachments | Append-only | Never delete; preserve all uploads |

### Timeline-Critical Items

| Date | Event | Action Required |
|------|-------|-----------------|
| **2026-02-14** | Research complete | Review and approve recommendation |
| **2026-03-02** | New rate limits enforce | Field filtering, rate monitoring deployed |
| **2026-03-14** | Webinar demo | Phase 1 MVP (one-way sync) functional |
| **2026-03-31** | Post-demo enhancement | Phase 2 (bidirectional) deployed |

---

## Recommended Reading Order

### For Implementers (Developers)

1. **This README** (15 min) - Context and overview
2. **Recommendation > Technical Specifications** (10 min) - Entity property schema, webhook events, API calls
3. **Synthesis > Major Claims** (15 min) - Understand the evidence behind decisions
4. **Evidence Catalog** (skim) - Bookmark for reference during implementation

**Total**: 40 minutes upfront, save hours of trial-and-error

---

### For Decision Makers (Product/Eng Leads)

1. **This README** (15 min) - Context and overview
2. **Recommendation > Decision + Rationale** (10 min) - What we're doing and why
3. **Recommendation > Trade-offs** (5 min) - What we're accepting/rejecting
4. **Recommendation > Risks & Mitigations** (10 min) - What could go wrong and how we'll prevent it

**Total**: 40 minutes for informed decision

---

### For Researchers (Extending This Work)

1. **Research Prompt** (10 min) - Understand methodology
2. **Evidence Catalog** (90 min) - Review all sources
3. **Synthesis > Gaps & Unknowns** (10 min) - What's still missing
4. **Recommendation > Alternatives Considered** (10 min) - Why certain paths rejected

**Total**: 2 hours for deep understanding

---

## Research Metadata

**Tool/Model Used**: WebSearch (Claude Code built-in)
**Search Date**: 2026-02-14
**Prompt Version**: 1.0 (research-prompt-template.md)
**Researcher**: Claude (rai-research skill)
**Total Time**: 6 hours (evidence gathering, synthesis, recommendation)

**Search Queries Executed**:
1. "JIRA bidirectional sync best practices webhook polling"
2. "Atlassian JIRA REST API integration patterns external systems"
3. "Zapier Unito Exalate JIRA sync architecture conflict resolution"
4. "JIRA custom fields external integration recommended fields"
5. "JIRA sync state tracking eventual consistency"
6. "JIRA webhook reliability failures retry mechanism"
7. "JIRA API rate limits pagination best practices 2025"
8. "bidirectional sync conflict resolution last-write-wins operational transform"
9. "JIRA labels entity properties metadata external system tracking"
10. "sync engine architecture event sourcing change data capture"
11. "GitHub JIRA sync implementation sync-engine bidirectional"
12. "JIRA integration idempotency duplicate detection sync reliability"

---

## Quality Checklist

Research validated against RaiSE quality criteria:

**Question & Scope**
- [x] Research question is specific and falsifiable
- [x] Decision context clearly stated (RaiSE-JIRA sync, March 14 demo)
- [x] Scope boundaries defined (JIRA Cloud, not Data Center)

**Evidence Gathering**
- [x] 32 sources consulted (exceeds 15-30 standard depth target)
- [x] Mix of Atlassian official docs (9), production tools (13), community (10)
- [x] Sources include publication dates
- [x] Evidence catalog complete with all required fields

**Rigor & Validation**
- [x] Major claims triangulated (3+ sources per claim)
- [x] Confidence levels explicitly stated for each claim
- [x] Contrary evidence acknowledged (webhook vs polling debates, last-write-wins limitations)
- [x] Gaps and unknowns documented (6 gaps identified)

**Actionability**
- [x] Recommendation is specific and actionable (webhook+polling with entity properties)
- [x] Trade-offs explicitly acknowledged (5 accepted, 5 rejected)
- [x] Risks identified with mitigations (6 risks, each with 3-5 mitigations)
- [x] Clear link to decision context (sync architecture design for March demo)

**Reproducibility**
- [x] All 32 sources cited with URLs
- [x] 12 search keywords documented
- [x] Tool used recorded (WebSearch)
- [x] Research date recorded (2026-02-14)

---

## Contact & Governance

**Research Owner**: RaiSE Framework Team
**Stakeholders**: Humansys (Atlassian partnership), Coppel client (first customer)
**Decision Deadline**: 2026-03-02 (rate limit enforcement)
**ADR Required**: Yes (architectural decision)

**Related Documents**:
- ADR: [Pending] "JIRA Bidirectional Sync Architecture"
- Story: [Pending] "Implement JIRA OAuth Integration"
- Story: [Pending] "Create Webhook Endpoint for JIRA Events"
- Story: [Pending] "Build Field-Level Conflict Resolution Engine"

---

**Last Updated**: 2026-02-14
**Status**: Complete, pending review
**Next Review**: After Phase 1 implementation (post-March 14 demo)
