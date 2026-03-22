# Implementation Plan: S-DEMO.6 — Demo Rehearsal & Retrospective

## Overview
- **Story:** S-DEMO.6
- **Story Points:** 1 SP (XS)
- **Feature Size:** XS
- **Created:** 2026-02-15
- **Deadline:** 2026-02-16 10:00 AM (1 hour before demo)

## Context

**Design:** Skipped (XS procedural validation story)

**Key Patterns:**
- PAT-E-024: Dogfooding is validation — rehearsal validates the framework under demo pressure
- Manual integration test validates end-to-end workflow (not just unit tests)

**Architectural Context:**
- **Modules:** mod-providers (JIRA client), mod-cli (backlog commands)
- **No code changes** — this story validates existing implementation

---

## Tasks

### Task 1: Create Rehearsal Checklist
- **Description:** Document step-by-step validation procedure for end-to-end workflow
- **Files:** `work/epics/e-demo-jira-sync/stories/s-demo.6-rehearsal/rehearsal-checklist.md`
- **TDD Cycle:** N/A (documentation task)
- **Verification:** Checklist covers all 6 workflow steps from epic scope
- **Size:** XS
- **Dependencies:** None

**Checklist structure:**
```markdown
## Pre-Rehearsal Setup
- [ ] JIRA credentials configured
- [ ] Sync state clean
- [ ] Test epic created in JIRA

## Workflow Steps
1. [ ] JIRA epic exists (manual verification in browser)
2. [ ] `rai backlog pull --source jira` succeeds
3. [ ] Epic appears in `governance/backlog.md`
4. [ ] Create local story design (manual: /rai-story-design)
5. [ ] `rai backlog push --source jira` succeeds
6. [ ] Stories visible in JIRA, linked to epic
7. [ ] Update story status in JIRA (manual)
8. [ ] `rai backlog pull --source jira` updates local status

## Post-Rehearsal
- [ ] Record issues encountered
- [ ] Timing measured (target: <15 min)
```

### Task 2: Execute Rehearsal 1 (Debug Run)
- **Description:** First end-to-end run, expect issues, debug as needed
- **Files:** `work/epics/e-demo-jira-sync/stories/s-demo.6-rehearsal/rehearsal-1-log.md`
- **TDD Cycle:** N/A (validation task)
- **Verification:** Workflow completes end-to-end OR issues documented for fixing
- **Size:** M (includes debugging)
- **Dependencies:** Task 1

**Capture:**
- Timestamp for each step
- Errors encountered
- Fixes applied
- Total duration

### Task 3: Execute Rehearsal 2 (Refinement Run)
- **Description:** Second run after fixes, refine timing and script
- **Files:** `work/epics/e-demo-jira-sync/stories/s-demo.6-rehearsal/rehearsal-2-log.md`
- **TDD Cycle:** N/A (validation task)
- **Verification:** Workflow completes with no errors, timing within 15-min target
- **Size:** S
- **Dependencies:** Task 2

**Focus:**
- Validate fixes from Rehearsal 1
- Refine demo narration timing
- Identify script improvements

### Task 4: Execute Rehearsal 3 (Validation Run)
- **Description:** Final confidence run, simulate demo conditions
- **Files:** `work/epics/e-demo-jira-sync/stories/s-demo.6-rehearsal/rehearsal-3-log.md`
- **TDD Cycle:** N/A (validation task)
- **Verification:** Clean run, no errors, timing confirmed
- **Size:** S
- **Dependencies:** Task 3

**Success criteria:**
- All 8 checklist items pass
- Total time <15 minutes
- No manual interventions needed

### Task 5: Create Demo Script
- **Description:** Write narrative script for demo delivery (Coppel-contextualized)
- **Files:** `work/epics/e-demo-jira-sync/stories/s-demo.6-rehearsal/demo-script.md`
- **TDD Cycle:** N/A (documentation task)
- **Verification:** Script includes intro, 6-step workflow, value articulation, Q&A prep
- **Size:** S
- **Dependencies:** Task 4 (informed by rehearsal learnings)

**Script structure:**
```markdown
## Introduction (1 min)
- Coppel context: Plan View → JIRA migration, governance scalability challenge
- Problem: 1:1 coaching doesn't scale to 150+ product teams
- Solution: RaiSE enables governance through workflow orchestration

## Workflow Demo (10 min)
[Step-by-step narration based on rehearsal timing]

## Value Articulation (2 min)
- Governance without coaching overhead
- JIRA adoption without governance loss
- AI-assisted PM workflow (not AI-replaced PM)

## Q&A Preparation
[Anticipated objections + responses]
```

### Task 6: JIRA Cleanup & Fresh Sync Setup
- **Description:** Delete test data, create fresh epic for demo, reset sync state
- **Files:** `.raise/rai/sync/state.json` (reset)
- **TDD Cycle:** N/A (cleanup task)
- **Verification:** JIRA project clean, fresh epic created, sync state empty
- **Size:** XS
- **Dependencies:** Task 5

**Steps:**
1. Delete rehearsal test data from JIRA (manual: JIRA web UI)
2. Create demo epic: "Product Governance Initiative"
3. `rm .raise/rai/sync/state.json` (reset sync state)
4. Verify clean state: `rai backlog status --source jira` shows no mappings

### Task 7: Backup Plan Documentation
- **Description:** Capture screenshots and recorded demo for fallback if live fails
- **Files:** `work/epics/e-demo-jira-sync/stories/s-demo.6-rehearsal/backup-plan.md`
- **TDD Cycle:** N/A (documentation task)
- **Verification:** Screenshots saved, recording captured, manual fallback procedure documented
- **Size:** S
- **Dependencies:** Task 4 (use Rehearsal 3 for recording)

**Deliverables:**
- Screenshots of each workflow step (8 images)
- Screen recording of Rehearsal 3 (full 15-min demo)
- Manual fallback procedure (if auth fails, show pre-recorded)

### Task 8: Epic Retrospective
- **Description:** Capture learnings from 42-hour sprint, framework validation insights
- **Files:** `work/epics/e-demo-jira-sync/stories/s-demo.6-rehearsal/retrospective.md`
- **TDD Cycle:** N/A (reflection task)
- **Verification:** Retrospective covers: what worked, what didn't, patterns captured, improvements identified
- **Size:** S
- **Dependencies:** Task 7

**Retrospective structure:**
```markdown
## 42-Hour Sprint Reflection
- Timeline adherence
- Framework validation under pressure
- ToC impact (session discipline gaps)

## What Worked
- [Key successes]

## What Didn't
- [Challenges encountered]

## Patterns Captured
- [New patterns for memory]

## Framework Improvements
- [Changes needed for next epic]

## Demo Outcome
- [Post-demo update: client reaction, questions, next steps]
```

### Task 9 (Final): Manual Integration Test
- **Description:** Validate entire demo workflow one final time before go-live
- **Files:** None (live validation)
- **TDD Cycle:** N/A (validation task)
- **Verification:** Execute full demo workflow with fresh JIRA epic, confirm all steps work
- **Size:** XS
- **Dependencies:** All previous tasks

**Final checklist:**
- [ ] Fresh JIRA epic exists
- [ ] `rai backlog pull` works
- [ ] Local design can be created
- [ ] `rai backlog push` works
- [ ] JIRA stories visible and linked
- [ ] Status sync works bidirectionally
- [ ] Total time <15 minutes
- [ ] Demo script ready
- [ ] Backup plan ready

---

## Execution Order

1. **Task 1** — Rehearsal checklist (foundation)
2. **Task 2** — Rehearsal 1 (debug run)
3. **Task 3** — Rehearsal 2 (refinement)
4. **Task 4** — Rehearsal 3 (validation)
5. **Task 5** — Demo script (parallel with Task 6)
6. **Task 6** — JIRA cleanup (parallel with Task 5)
7. **Task 7** — Backup plan (uses Rehearsal 3 artifacts)
8. **Task 8** — Epic retrospective (reflection)
9. **Task 9** — Final integration test (go/no-go gate)

**Parallelization:** Tasks 5-6 can run in parallel after Task 4.

---

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| JIRA auth fails during demo | Medium | Critical | Backup: recorded demo + screenshots (Task 7) |
| Workflow timing exceeds 15 min | Low | Medium | 3 rehearsals calibrate timing (Tasks 2-4) |
| API rate limit during rehearsals | Low | Medium | Use dry-run mode for script validation |
| Missing Coppel context in script | Medium | High | Research Zaira's role, governance pain points (Task 5) |
| Session discipline gap (no closure) | High | Low | Close SES-171 retroactively, start fresh session |

---

## Duration Tracking

| Task | Size | Planned | Actual | Notes |
|------|------|---------|--------|-------|
| 1 | XS | 15 min | -- | Checklist creation |
| 2 | M | 60 min | -- | Debug run + fixes |
| 3 | S | 45 min | -- | Refinement run |
| 4 | S | 30 min | -- | Validation run |
| 5 | S | 45 min | -- | Demo script |
| 6 | XS | 30 min | -- | JIRA cleanup |
| 7 | S | 30 min | -- | Backup plan |
| 8 | S | 30 min | -- | Retrospective |
| 9 | XS | 15 min | -- | Final validation |
| **Total** | **XS (1 SP)** | **4h 20min** | -- | Budgeted: 4h (Mon 06:00-10:00) |

**Note:** Total planned slightly exceeds budget (4h 20min vs 4h). Task 2 (debug run) is the buffer — if clean, saves time.

---

## Next Steps

After planning complete:
1. Emit plan complete telemetry: `rai memory emit-work story S-DEMO.6 -e complete -p plan`
2. Start implementation: `/rai-story-implement`
3. Begin with Task 1 (rehearsal checklist)

---

**Gate:** Plan complete when all tasks defined, dependencies mapped, execution order clear.
