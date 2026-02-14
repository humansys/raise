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
| **3** | S-DEMO.3 | S (2 SP) | S-DEMO.2 | M2 | Sun 08:00 | Sun 12:00 | JIRA client needed before sync |
| **4** | S-DEMO.4 | S (2 SP) | S-DEMO.3 | M2 | Sun 12:00 | Sun 16:00 | Entity properties schema |
| **5** | S-DEMO.5 | L (4 SP) | S-DEMO.4 | M3 | Sun 16:00 | Mon 06:00 | Sync engine (epic/story/task) |
| **6** | S-DEMO.6 | XS (1 SP) | S-DEMO.5 | M4 | Mon 06:00 | Mon 10:00 | Demo rehearsal + polish |

**Total:** 15 SP, 6 stories, 29 hours

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
- S-DEMO.3: JIRA client & API wrapper
- S-DEMO.4: Entity properties & sync metadata

**Success Criteria:**
- [ ] JIRA client creates test issue via API
- [ ] Entity properties read/write working
- [ ] Rate limiting handled (field filtering implemented)
- [ ] Idempotency check works (query entity properties before create)

**Demo Capability:**
```bash
rai backlog test-jira --provider jira
# Creates test epic in JIRA
# Shows entity properties in JIRA UI
```

**Demo Validation:** Check JIRA UI, see test epic with `com.humansys.raise.sync` property visible in developer tools.

**Gate:** Cannot proceed to S-DEMO.5 without JIRA API calls working. If blocked past 18:00 Sunday, reduce sync scope (epic/story only, skip tasks).

---

### M3: Full Sync Working (Monday 06:00 AM)

**Features Complete:**
- S-DEMO.5: Sync engine (epic/story/task granularity)

**Success Criteria:**
- [ ] Parse E-DEMO epic from `governance/backlog.md`
- [ ] Parse 6 stories from epic branch
- [ ] Parse tasks from each story's `plan.md`
- [ ] Create JIRA Epic → Stories → Subtasks hierarchy
- [ ] Entity properties set on all items (epic/story/task IDs)
- [ ] Idempotent (re-running sync doesn't duplicate)
- [ ] Dry-run mode works (`--dry-run` shows what would sync)

**Demo Capability:**
```bash
rai backlog sync --provider jira --dry-run
# Shows: Will create 1 epic, 6 stories, ~30 tasks

rai backlog sync --provider jira
# Actually creates hierarchy in JIRA
```

**Demo Validation:** Open JIRA, see full E-DEMO epic with 6 stories, each with subtasks. Click into entity properties (dev tools), see RaiSE metadata.

**Gate:** This is the CRITICAL milestone. If not reached by 06:00 Monday, we have 5 hours to debug before demo. Fallback: Demo with partial sync (epic/story only).

---

### M4: Demo Ready (Monday 10:00 AM)

**Features Complete:**
- S-DEMO.6: Demo validation & retrospective

**Success Criteria:**
- [ ] Demo rehearsed 3+ times successfully
- [ ] Demo script written (what to say, what to show)
- [ ] JIRA project cleaned up (delete test data)
- [ ] Fresh sync for demo (clean JIRA state)
- [ ] Backup plan documented (if live demo fails, show screenshots)

**Demo Script:**
1. Show RaiSE working locally (this epic, stories, tasks in plan.md)
2. Run `rai backlog sync --provider jira --dry-run` (show what will sync)
3. Run `rai backlog sync --provider jira` (create in JIRA)
4. Open JIRA UI → show epic → stories → subtasks
5. Click into story → dev tools → show entity properties (RaiSE metadata)
6. Explain Forge vision (cross-project intelligence)

**Demo Duration:** 10-15 minutes

**Gate:** Demo must rehearse successfully by 10:00 AM. If any issues, we have 1 hour buffer to fix before 11:00 AM demo.

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
- Parse multiple file formats (backlog.md, plan.md)
- Handle hierarchy (epic → story → task)
- Create 3 JIRA issue types (epic, story, subtask)
- Idempotency logic (don't duplicate on re-run)
- Error handling (API failures, partial sync)

**Why Late:**
- Foundation built (auth, JIRA client, entity properties all working)
- Learning accumulated (patterns from earlier stories)
- Most time available (10+ hours Sunday night/Monday morning)

**Fallback:** If running behind → reduce granularity (epic + story only, skip tasks)

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
| **S-DEMO.2** | M (3 SP) | 🔄 NEXT | Sat 17:00 | Target: 23:00 | - | - | OAuth auth flow |
| **S-DEMO.3** | S (2 SP) | Pending | Sun 08:00 | Target: 12:00 | - | - | JIRA API wrapper |
| **S-DEMO.4** | S (2 SP) | Pending | Sun 12:00 | Target: 16:00 | - | - | Entity properties |
| **S-DEMO.5** | L (4 SP) | Pending | Sun 16:00 | Target: Mon 06:00 | - | - | Full sync engine |
| **S-DEMO.6** | XS (1 SP) | Pending | Mon 06:00 | Target: 10:00 | - | - | Demo rehearsal |

### Milestone Progress

- [x] **M1: Authentication Working** (Target: Sat 23:00) — **NEXT GATE**
  - [x] S-DEMO.1 complete ✅
  - [ ] S-DEMO.2 in progress

- [ ] **M2: JIRA API Working** (Target: Sun 16:00)
  - [ ] S-DEMO.3 pending
  - [ ] S-DEMO.4 pending

- [ ] **M3: Full Sync Working** (Target: Mon 06:00)
  - [ ] S-DEMO.5 pending

- [ ] **M4: Demo Ready** (Target: Mon 10:00)
  - [ ] S-DEMO.6 pending

### Cumulative Progress

- **SP Complete:** 3 / 15 (20%)
- **Time Elapsed:** 3h / 29h (10%)
- **Velocity:** 1.0 SP/hour (on track for 10 SP/day target)
- **Burn Rate:** Ahead of schedule (20% complete vs 10% time elapsed)

**Next Checkpoint:** Saturday 23:00 (M1: Auth working)

---

## Sequencing Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation | Fallback |
|------|:----------:|:------:|------------|----------|
| **OAuth complexity delays M1** | Medium | High | Use `atlassian-python-api` library (proven). Timebox to 6h. | Pivot to API tokens (hardcoded) if blocked past midnight Sat |
| **JIRA API rate limits hit** | Low | Medium | Implement field filtering (S-DEMO.3). Batch API calls. | Sync fewer items (epic only, not stories/tasks) |
| **Task parsing complexity** | Medium | Medium | Parse plan.md early (Sunday). Test with real task data. | Skip task sync, do epic + story only (reduces scope by 30%) |
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
