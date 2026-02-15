# Epic Scope: E-DEMO JIRA Sync Enabler

> **Type:** Enabler Epic (infrastructure/commercial feature validation)
> **Release:** N/A (Demo-scoped, not part of v2 release)
> **Target:** March 14, 2026 - Atlassian Webinar Demo
> **Branch:** `demo/atlassian-webinar` (never merges to v2)

---

## Objective

Build JIRA bidirectional sync prototype using full RaiSE process to:
1. Demonstrate Atlassian ecosystem integration at March 14 webinar
2. Dogfood RaiSE under timeline pressure (28-day deadline)
3. Validate commercial feature architecture (RaiSE PRO foundation)
4. Capture learnings for future raise-pro package

---

## In Scope

**MVP Features (Demo-Required):**
- One-way sync: Local backlog (governance/backlog.md) → JIRA
- OAuth 2.0 authentication with JIRA Cloud
- Entity properties for sync metadata tracking
- CLI command: `rai backlog sync --provider jira --direction push`
- Active epic detection (sync current epic only)
- Basic error handling and user feedback
- Dry-run mode: `--dry-run` flag

**Process Validation:**
- Full RaiSE epic lifecycle (design → plan → stories → close)
- TDD throughout (validate quality gates under pressure)
- Retrospectives capture learnings → patterns
- Research-backed architecture (6 parallel research outputs)

**Research Foundation:**
- `/work/research/bidirectional-sync/` - 28 sources, 1,464 lines
- `/work/research/jira-bidirectional-sync/` - 32 sources, 1,951 lines
- `/work/research/gitlab-sync-patterns/` - 28 sources
- `/work/research/offline-first-sync/` - 32 sources
- `/work/research/pm-sync-boundaries/` - 34 sources
- `/work/research/sync-trigger-patterns/` - 30+ sources

---

## Out of Scope

**Deferred to V3 / raise-pro:**
- ❌ Bidirectional sync (JIRA → Local)
- ❌ Conflict resolution UI
- ❌ Webhooks (real-time sync)
- ❌ Polling reconciliation
- ❌ GitLab/Odoo adapters
- ❌ Custom field mapping
- ❌ Multi-project sync
- ❌ Team/org sync (shared memory)
- ❌ Production hardening (retry policies, monitoring, SLOs)
- ❌ Enterprise auth (SSO, SAML)

**Deferred to Post-Demo:**
- Architecture decision (raise-pro package vs monorepo vs fork)
- Commercial pricing model
- Open-source retrofit decision

---

## Stories (Planned)

**Estimated: 6 stories, 28 days**

| ID | Story | Size | Priority |
|----|-------|------|----------|
| S-DEMO.1 | Research synthesis & architecture design | M | P0 |
| S-DEMO.2 | OAuth authentication & JIRA client setup | M | P0 |
| S-DEMO.3 | Entity properties & sync metadata schema | S | P0 |
| S-DEMO.4 | CLI command & sync engine (one-way) | L | P0 |
| S-DEMO.5 | Demo scenario validation & rehearsal | S | P0 |
| S-DEMO.6 | Epic retrospective & architecture decision | M | P1 |

---

## Done When

**Demo Success Criteria:**
- [ ] One epic syncs from local → JIRA without errors
- [ ] OAuth flow works (token acquisition + refresh)
- [ ] Entity properties track sync state correctly
- [ ] CLI provides clear feedback (progress, errors, dry-run)
- [ ] Demo rehearsed successfully (March 13 deadline)

**Process Success Criteria:**
- [ ] All stories follow full lifecycle (design → review → close)
- [ ] TDD maintained (tests pass before commits)
- [ ] Learnings captured in retrospectives
- [ ] Patterns added to memory (dogfooding validation)

**Post-Demo Decision:**
- [ ] Commercial architecture chosen (raise-pro vs monorepo vs fork)
- [ ] Code migrated or archived (April 1 target)

---

## Timeline

| Week | Dates | Focus | Gate |
|------|-------|-------|------|
| **1** | Feb 14-20 | Architecture + OAuth | Auth working |
| **2** | Feb 21-27 | Metadata + Sync engine start | One epic syncs |
| **3** | Feb 28-Mar 6 | Sync completion + Error handling | Reliable sync |
| **4** | Mar 7-13 | Demo validation + Polish | Demo-ready |
| **Demo** | Mar 14 | Atlassian webinar | ✅ Success |
| **Decision** | Mar 15-31 | Architecture choice | Migrate/archive |

---

## Constraints

**Hard Deadlines:**
- **March 2, 2026:** JIRA rate limit changes enforce (field filtering required)
- **March 14, 2026:** Atlassian webinar demo (28 days from start)

**Quality Gates (Non-Negotiable):**
- TDD (RED-GREEN-REFACTOR)
- Type annotations (pyright strict)
- Tests pass before commits
- Ruff linting passes

**Velocity Adaptations:**
- Aggressive sizing (bias toward S/M stories)
- Design concurrency (parallel story design when possible)
- Combined HITL checkpoints (review 2-3 stories together)
- Expedited review (same-day close when feasible)

---

## Success Metrics

**Demo Metrics:**
- Sync latency: <5s for typical epic (5-10 stories)
- Error rate: 0% for happy path
- OAuth success: 100% (no failed auth flows)
- Demo rehearsal: 3+ successful runs

**Process Metrics:**
- Story velocity: 1.5 stories/week (aggressive)
- TDD compliance: 100% (no commits without tests)
- Retrospective patterns: 3+ actionable learnings captured

**Strategic Metrics:**
- Webinar attendance/engagement (measured by Atlassian)
- Customer validation (post-demo interest in RaiSE PRO)
- Dogfooding learnings (# patterns added to memory)

---

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| JIRA API changes (March 2 deadline) | Medium | High | Implement field filtering from day 1 |
| OAuth complexity delays progress | Medium | Medium | S-DEMO.2 front-loaded, research complete |
| Timeline slip (28 days tight) | High | High | Aggressive sizing, daily progress checks |
| Demo failure (live issues) | Low | Critical | S-DEMO.5 rehearsal story, dry-run mode |
| Scope creep (bidirectional temptation) | Medium | Medium | Explicit out-of-scope list, HITL enforcement |

---

## Meta-Learning Goal

**Primary Question:** Can RaiSE handle commercial feature development under deadline pressure?

**What We're Testing:**
- Epic lifecycle under timeline constraints
- Story velocity when aggressive
- Quality gates vs speed trade-offs
- Dogfooding: using our own process to build our own features

**Expected Learnings:**
- Where process adds value vs friction
- What adaptations work (design concurrency, combined HITL)
- Pain points for time-pressured teams
- Commercial feature workflow patterns

---

## Related Documents

- **Strategy:** `DEMO-STRATEGY.md` (branch strategy, post-demo options)
- **Backlog:** `governance/backlog.md` §7 (demo & commercial strategy)
- **Research:** `/work/research/` (6 parallel research outputs)
- **Pattern:** PAT-E-289 (demo branch strategy for commercial features)

---

*Created: 2026-02-14*
*Epic Owner: Emilio + Rai*
*Type: Enabler Epic (infrastructure/validation)*
*Status: Active*
