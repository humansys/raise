# Demo Rehearsal Checklist — E-DEMO (Coppel JIRA Sync)

**Purpose:** Validate end-to-end workflow for Coppel demo (2026-02-16 11:00 AM)

**Target Duration:** <15 minutes (full workflow)

---

## Pre-Rehearsal Setup

- [ ] **JIRA credentials configured**
  - `rai backlog auth --provider jira` succeeds
  - OAuth token valid and not expired

- [ ] **Sync state clean**
  - `.raise/rai/sync/state.json` exists OR is empty
  - No stale mappings from previous tests

- [ ] **Test epic created in JIRA**
  - Epic exists in JIRA project
  - Epic key noted (e.g., "DEMO-123")
  - Epic summary: "Product Governance Initiative" (or test name)

- [ ] **Local environment ready**
  - On branch: `demo/atlassian-webinar`
  - Tests passing: `pytest -xvs`
  - No uncommitted changes blocking demo flow

---

## Workflow Validation (6 Core Steps)

### Step 1: Verify JIRA Epic Exists (Manual)
- [ ] Open JIRA in browser
- [ ] Navigate to project (e.g., "DEMO")
- [ ] Confirm epic visible with correct summary
- [ ] Note epic key: `___________`

**Expected:** Epic visible, key captured for pull command.

---

### Step 2: Pull Epic from JIRA → Local Backlog
- [ ] Run command: `rai backlog pull --source jira`
- [ ] Command succeeds (exit code 0)
- [ ] Output shows: "✓ Pulled epic DEMO-XXX"

**Verification:**
```bash
grep -i "product governance" governance/backlog.md
```

- [ ] Epic row appears in `governance/backlog.md`
- [ ] Status: "In Progress" (or JIRA status mapped correctly)

**Expected:** Epic visible in local backlog file.

---

### Step 3: Design Epic Locally (Manual Simulation)
- [ ] Simulate local design work:
  - Read epic scope from backlog
  - Identify 2-3 sample user stories
  - Document story titles (no full design needed for demo)

**Example stories:**
1. "As PM, I want governance templates, so I can document decisions"
2. "As team lead, I want backlog sync, so JIRA reflects RaiSE state"
3. "As stakeholder, I want epic status visibility, so I can track progress"

- [ ] Stories documented (can be in scratch notes, not formal backlog)

**Expected:** Local story concepts exist (simulates `/rai-epic-design` output).

---

### Step 4: Push Stories to JIRA
- [ ] Dry-run first: `rai backlog push --source jira --dry-run`
- [ ] Output shows: "Will create 3 stories linked to epic DEMO-XXX"
- [ ] Verify story titles in output

- [ ] Execute push: `rai backlog push --source jira`
- [ ] Command succeeds (exit code 0)
- [ ] Output shows: "✓ Created 3 stories in JIRA"

**Verification:**
```bash
rai backlog status --source jira
```

- [ ] Status shows 3 mapped stories
- [ ] Local IDs → JIRA keys mapping visible

**Expected:** Stories created in JIRA, mapped in local state.

---

### Step 5: Verify Stories in JIRA (Manual)
- [ ] Refresh JIRA browser
- [ ] Navigate to epic view
- [ ] Confirm 3 stories visible
- [ ] Stories linked to epic (parent link exists)
- [ ] Story statuses: "To Do" (or initial workflow state)

**Expected:** Stories visible in JIRA, correctly linked to epic.

---

### Step 6: Update Story Status in JIRA (Manual)
- [ ] Select first story in JIRA
- [ ] Transition to "In Progress" (or next workflow state)
- [ ] Confirm status updated in JIRA UI

**Expected:** JIRA shows story status changed.

---

### Step 7: Pull Status Updates Back to Local
- [ ] Run command: `rai backlog pull --source jira`
- [ ] Command succeeds (exit code 0)
- [ ] Output shows: "✓ Updated 1 story status"

**Verification:**
```bash
grep -A5 "Story 1 Title" governance/backlog.md
```

- [ ] Story status updated in local backlog file
- [ ] Status reflects JIRA state ("In Progress")

**Expected:** Local backlog reflects JIRA status change.

---

### Step 8: Bidirectional Sync Validation
- [ ] Confirm round-trip complete:
  - JIRA epic → Local backlog (Step 2)
  - Local stories → JIRA (Step 4)
  - JIRA status → Local backlog (Step 7)

- [ ] No data loss or corruption
- [ ] Sync state consistent: `cat .raise/rai/sync/state.json`

**Expected:** Full bidirectional workflow validated.

---

## Post-Rehearsal

### Timing Measurement
- [ ] Total duration measured: `_____ minutes`
- [ ] Target met (<15 min): YES / NO
- [ ] If over time, identify bottleneck: `_________________`

### Issues Encountered
- [ ] List any errors or failures:
  1. `_______________________________`
  2. `_______________________________`
  3. `_______________________________`

- [ ] Fixes applied (if any): `_________________`

### Demo Readiness Assessment
- [ ] Workflow executed cleanly: YES / NO
- [ ] All 8 steps passed: YES / NO
- [ ] Timing acceptable: YES / NO
- [ ] Ready for next rehearsal: YES / NO

**If NO to any:** Document blockers and required fixes before Rehearsal 2.

---

## Rehearsal Log Template

**Rehearsal #:** `___`
**Date/Time:** `___________`
**Duration:** `_____ min`

### Step Results

| Step | Status | Time | Notes |
|------|--------|------|-------|
| 1. JIRA epic exists | ☐ Pass ☐ Fail | __ min | |
| 2. Pull epic | ☐ Pass ☐ Fail | __ min | |
| 3. Design stories | ☐ Pass ☐ Fail | __ min | |
| 4. Push stories | ☐ Pass ☐ Fail | __ min | |
| 5. Verify in JIRA | ☐ Pass ☐ Fail | __ min | |
| 6. Update status | ☐ Pass ☐ Fail | __ min | |
| 7. Pull status | ☐ Pass ☐ Fail | __ min | |
| 8. Validate sync | ☐ Pass ☐ Fail | __ min | |

**Overall:** ☐ SUCCESS ☐ PARTIAL ☐ FAILED

**Issues:**
- `_______________________________`

**Fixes Applied:**
- `_______________________________`

**Next Steps:**
- `_______________________________`

---

## Success Criteria (All Rehearsals)

- [ ] **Rehearsal 1:** Workflow completes OR issues documented for fixing
- [ ] **Rehearsal 2:** Workflow completes with no errors, timing refined
- [ ] **Rehearsal 3:** Clean run, <15 min, no manual interventions

**Final Gate:** All 3 rehearsals completed successfully → Demo ready.

---

**Created:** 2026-02-15
**Epic:** E-DEMO (JIRA Sync Enabler)
**Demo Date:** 2026-02-16 11:00 AM (Coppel)
