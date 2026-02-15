# Epic E-DEMO: Implementation Plan

> **Created:** 2026-02-14, 16:45 (Saturday)
> **Demo:** 2026-02-16, 11:00 (Monday)
> **Time Available:** 42 hours (minus sleep = ~29 working hours)
> **Velocity Target:** 10 SP/day (hyper-aggressive dogfooding)

---

## Feature Sequence (Critical Path - All Sequential)

| Order | Feature | Size | Dependencies | Milestone | Start | Target Complete | Rationale |
|:-----:|---------|:----:|--------------|-----------|-------|-----------------|-----------|
| **1** | S-DEMO.1 | M (3 SP) | ✅ Done | M1 | Sat 16:00 | **✅ Sat 17:00** | ADRs complete, foundation set |
| **2** | S-DEMO.2 | M (3 SP) | S-DEMO.1 | M1 | Sat 17:00 | Sat 23:00 | OAuth critical path, highest risk |
| **3** | S-DEMO.3 | M (3 SP) | S-DEMO.2 | M2 | Sun 08:00 | Sun 12:00 | Bidirectional JIRA client (read + write) |
| **4** | S-DEMO.4 | S (2 SP) | S-DEMO.3 | M2 | Sun 12:00 | Sun 16:00 | Entity properties schema |
| **5** | S-DEMO.5 | L (4 SP) | S-DEMO.4 | M3 | Sun 16:00 | Mon 06:00 | Sync engine (pull + push, epic/story) |
| **6** | S-DEMO.6 | XS (1 SP) | S-DEMO.5 | M4 | Mon 06:00 | Mon 10:00 | Coppel demo rehearsal + script |

**Total:** 16 SP, 6 stories, 29 hours

**Critical Path:** S-DEMO.1 → S-DEMO.2 → S-DEMO.3 → S-DEMO.4 → S-DEMO.5 → S-DEMO.6

**No parallel opportunities:** Each story blocks the next. OAuth must work before JIRA client. JIRA client must work before entity properties. Entity properties must exist before sync engine can use them.

---

## Milestones (Sprint Gates)

### M1: Authentication Working (Saturday 23:00)

**Features Complete:**
- ✅ S-DEMO.1: Research synthesis & ADRs (DONE)
- S-DEMO.2: OAuth 2.0 authentication

**Success Criteria:**
- [ ] OAuth flow completes (browser redirect → token acquisition)
- [ ] Token stored encrypted in `~/.rai/credentials.json`
- [ ] Token refresh works (automatic background refresh)
- [ ] JIRA API call succeeds with acquired token

**Demo Capability:** `rai backlog auth --provider jira` → "✓ Authenticated as user@example.com"

**Blocker Risk:** OAuth complexity (PKCE flow, token storage). **Mitigation:** Use `atlassian-python-api` library (proven), reference research (32 sources).

**Gate:** Cannot proceed to S-DEMO.3 without working auth. If blocked past midnight Saturday, escalate to user for strategy pivot.

---

### M2: JIRA API Working (Sunday 16:00)

**Features Complete:**
- S-DEMO.3: JIRA client (bidirectional)
- S-DEMO.4: Entity properties & sync metadata

**Success Criteria:**
- [ ] **Read:** JIRA client reads epic from JIRA (by key or JQL)
- [ ] **Write:** JIRA client creates story linked to epic
- [ ] **Read:** JIRA client reads status updates from JIRA
- [ ] Entity properties read/write working
- [ ] Rate limiting handled (field filtering implemented)
- [ ] Idempotency check works (query entity properties before create)

**Demo Capability:**
```bash
rai backlog test-jira --provider jira
# Reads test epic from JIRA
# Creates test story in JIRA
# Reads story status back
# Shows entity properties in JIRA UI
```

**Demo Validation:** Check JIRA UI, see test epic + story with `com.humansys.raise.sync` property visible in developer tools.

**Gate:** Cannot proceed to S-DEMO.5 without bidirectional JIRA operations working. If blocked past 18:00 Sunday, reduce to one-way push only (defer pull to post-demo).

---

### M3: Bidirectional Sync Working (Monday 06:00 AM)

**Features Complete:**
- S-DEMO.5: Sync engine (pull + push, epic/story granularity)

**Success Criteria (Coppel Workflow):**
- [ ] **Pull:** Read JIRA epic → Write to `governance/backlog.md` + memory graph
- [ ] **Push:** Read local stories → Create JIRA issues → Link to epic
- [ ] **Pull:** Read JIRA status updates → Update local backlog
- [ ] Entity properties set on all items (epic/story IDs)
- [ ] Idempotent (re-running sync doesn't duplicate)
- [ ] Dry-run mode works (`--dry-run` shows what would sync)

**Demo Capability (Full Workflow):**
```bash
# 1. PM creates epic in JIRA (manual step)

# 2. Rai pulls epic
rai backlog pull --source jira --dry-run
# Shows: Will import "Product Governance Initiative" epic

rai backlog pull --source jira
# Epic appears in governance/backlog.md

# 3. Rai designs epic locally (manual: /rai-epic-design)

# 4. Rai pushes stories to JIRA
rai backlog push --source jira --dry-run
# Shows: Will create 5 stories linked to epic

rai backlog push --source jira
# 5 stories appear in JIRA

# 5. Team updates story status in JIRA (manual)

# 6. Rai syncs status back
rai backlog pull --source jira
# Status updated in local backlog
```

**Demo Validation:** End-to-end workflow works. JIRA epic → local backlog → local design → JIRA stories → status sync back.

**Gate:** This is the CRITICAL milestone. If not reached by 06:00 Monday, we have 5 hours to debug before demo. Fallback: Demo with push only (skip pull workflow).

---

### M4: Demo Ready (Monday 10:00 AM)

**Features Complete:**
- S-DEMO.6: Demo rehearsal & Coppel script

**Success Criteria:**
- [ ] Coppel workflow rehearsed 3+ times successfully
- [ ] Demo script written (tailored to Zaira's governance scalability needs)
- [ ] JIRA project cleaned up (delete test data)
- [ ] Fresh sync for demo (clean JIRA state)
- [ ] Backup plan documented (if live demo fails, show screenshots)

**Demo Script (Coppel Context):**

**Intro (1 min):** "We're showing how RaiSE enables product governance at scale—addressing Coppel's challenge of migrating from Plan View to JIRA while maintaining governance without 1:1 coaching."

**Workflow (10 min):**
1. **PM creates epic in JIRA** (pre-created: "Product Governance Initiative")
   - "This is how your product managers start initiatives in JIRA today"

2. **Rai pulls epic** (`rai backlog pull --source jira`)
   - Show epic appears in local backlog
   - "Rai is notified and brings the epic into the governance framework"

3. **Rai designs epic** (show `/rai-epic-design` process)
   - Show 5 stories created locally
   - "Rai guides the design with governance principles built-in"

4. **Rai pushes stories to JIRA** (`rai backlog push --source jira`)
   - Show 5 stories appear in JIRA linked to epic
   - "Team sees structured stories in their existing JIRA workflow"

5. **Team approves story** (manually update status in JIRA)
   - "Team collaboration happens in JIRA as normal"

6. **Rai syncs status back** (`rai backlog pull --source jira`)
   - Show status updated in RaiSE backlog
   - "Governance and execution stay in sync automatically"

**Forge Vision (2 min):** Cross-project intelligence, systemic insights, value measurement

**Q&A (2 min)**

**Demo Duration:** 15 minutes total

**Gate:** Demo must rehearse successfully by 10:00 AM. If any issues, we have 1 hour buffer to fix before 11:00 AM demo with Zaira.

---

## Risk-First Sequencing Rationale

### Why S-DEMO.2 (OAuth) is Second?

**Risk Level:** HIGH
- New technology for this codebase (OAuth PKCE flow)
- Browser interaction in CLI tool (complexity)
- Token storage security (encryption, XDG paths)

**Why Early:**
- Highest uncertainty → tackle when energy is high
- If it fails, we have Sunday + Monday to pivot
- Blocks all other work (can't call JIRA API without auth)

**Fallback:** If OAuth blocked past midnight Saturday → pivot to API tokens (hardcoded, less secure, but faster)

---

### Why S-DEMO.5 (Sync Engine) is Largest?

**Complexity:**
- **Bidirectional operations:** Both pull (JIRA → local) and push (local → JIRA)
- Parse multiple file formats (backlog.md for epics, epic scope for stories)
- Handle hierarchy (epic → story)
- Create JIRA issues (epic, story) and link them
- Idempotency logic (don't duplicate on re-run)
- Entity properties integration (track sync state)
- Dry-run mode (preview without execution)
- Error handling (API failures, partial sync, network issues)

**Why Late:**
- Foundation built (auth, JIRA client, entity properties all working)
- Learning accumulated (patterns from earlier stories)
- Most time available (14 hours Sunday evening/Monday morning)

**Fallback:** If running behind → reduce to one-way push only (defer pull to post-demo)

---

## Parallel Work Opportunities

**None.** Timeline is too tight for parallelism. Sequential critical path is the fastest route with single developer.

**Why No Parallel:**
- OAuth blocks JIRA client (can't test API without auth)
- JIRA client blocks entity properties (need API to set properties)
- Entity properties blocks sync engine (sync depends on metadata schema)

**Context Switching Cost:** Even with AI assistance, switching between stories adds overhead. Stay focused on one story until complete.

---

## Progress Tracking (Live Updates)

| Feature | Size | Status | Start | Complete | Actual Time | Velocity | Notes |
|---------|:----:|:------:|-------|----------|:-----------:|:--------:|-------|
| **S-DEMO.1** | M (3 SP) | ✅ **DONE** | Sat 14:00 | Sat 17:00 | **3h** | **1.0 SP/h** | ADRs + scope complete |
| **S-DEMO.2** | M (3 SP) | ✅ **DONE** | Sat 17:00 | Sat 17:44 | **44m** | **6.8x** | OAuth + PKCE + token storage |
| **S-DEMO.3** | M (3 SP) | ✅ **DONE** | Sat 19:00 | Sat 21:15 | **135m** | **1.33x** | Bidirectional JIRA client |
| **S-DEMO.4** | S (2 SP) | ✅ **DONE** | Sun ~01:00 | Sun ~02:50 | **110m** | **1.22x** | Entity properties + integration tests |
| **S-DEMO.5** | L (4 SP) | 🔄 **IN PROGRESS** | Sun 06:00 | - | - | - | Sync engine: Tasks 1-5 done, Task 6 (integration test) pending |
| **S-DEMO.6** | XS (1 SP) | Pending | - | Target: Mon 10:00 | - | - | Coppel demo rehearsal |

### Milestone Progress

- [x] **M1: Authentication Working** (Target: Sat 23:00) ✅
  - [x] S-DEMO.1 complete ✅
  - [x] S-DEMO.2 complete ✅

- [x] **M2: JIRA API Working** (Target: Sun 16:00) ✅
  - [x] S-DEMO.3 complete ✅
  - [x] S-DEMO.4 complete ✅

- [ ] **M3: Full Sync Working** (Target: Mon 06:00) — **CURRENT**
  - [ ] S-DEMO.5 in progress (Tasks 1-5 done, Task 6 pending)

- [ ] **M4: Demo Ready** (Target: Mon 10:00)
  - [ ] S-DEMO.6 pending

### Cumulative Progress

- **SP Complete:** 12 / 16 (75%) — S-DEMO.5 partially complete
- **Time Elapsed:** ~14h / 29h (48%)
- **Velocity:** ~0.86 SP/hour (sustainable pace)
- **Burn Rate:** Ahead of schedule (75% complete vs 48% time elapsed)

**Next:** Complete S-DEMO.5 Task 6 (integration test), then S-DEMO.6 (rehearsal)

---

## Sequencing Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation | Fallback |
|------|:----------:|:------:|------------|----------|
| **OAuth complexity delays M1** | Medium | High | Use `atlassian-python-api` library (proven). Timebox to 6h. | Pivot to API tokens (hardcoded) if blocked past midnight Sat |
| **Bidirectional sync complexity** | Medium | High | S-DEMO.3 sized as M (3 SP) for read + write operations. | Reduce to one-way push only (defer pull to post-demo) |
| **JIRA API rate limits hit** | Low | Medium | Implement field filtering (S-DEMO.3). Batch API calls. | Sync fewer items (epic only, not stories) |
| **Demo environment failure** | Low | Critical | Rehearse 3+ times. Backup: Screenshots + recorded demo. | Show recorded demo if live JIRA fails |
| **Sleep deprivation errors** | High | Medium | Stop at 2am Sunday. 6h sleep minimum. Fresh start Monday. | Accept reduced scope if exhausted |

---

## Velocity Assumptions

**Historical Data:** "Days where we do 20 SP" (user confirmation)

**This Sprint:**
- **Target:** 15 SP / 1.5 days = 10 SP/day
- **Achieved (so far):** 3 SP / 3h = 1.0 SP/hour = **24 SP/day** (unsustainable, but good start)
- **Realistic:** 10-12 SP/day with full focus

**Adjustment Triggers:**
- If velocity drops below 0.5 SP/hour → reduce scope (skip tasks)
- If M1 slips past midnight Saturday → escalate to user
- If M3 not reached by 08:00 Monday → emergency scope cut

**Buffer:** 1 hour built into each milestone for integration/testing

---

## Next Action

**Immediate:** Start S-DEMO.2 (OAuth authentication)

**Command:** `/rai-story-start S-DEMO.2`

**Expected Output:**
- Story branch created: `story/s-demo.2/oauth-authentication`
- Scope commit with story boundaries
- Design phase (if needed for OAuth complexity)
- Plan with atomic tasks
- Ready to implement

**Target:** OAuth working by Saturday 23:00 (M1 gate)

---

*Plan created: 2026-02-14, 16:45*
*Next: `/rai-story-start` for S-DEMO.2*
*Demo: Monday 11:00 AM (42 hours from now)*
