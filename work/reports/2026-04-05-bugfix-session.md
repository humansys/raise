# Bugfix Session Report — 2026-04-05

## Session Metrics

| Metric | Value |
|--------|-------|
| Bugs resolved | 5 (4 fixed, 1 closed as already resolved) |
| Story points | 8 SP delivered + RAISE-1063 (unestimated) |
| MRs created | 3 (!48, !55, !56) |
| Commits | ~20 across all bugs |
| Patterns added | 3 (PAT-E-599, PAT-E-600, +1 unnamed) |
| Time in pipeline | Full session (~4 hours) |

## Bug Summary

### RAISE-1008 (3 SP) — Daemon CPU Leak
- **Classification:** Logic / S1-High / Code / Incorrect
- **Pipeline:** Full 7-phase, all 3 gates
- **Root cause:** Duplicate PTB Application in build_daemon() + poll_interval=0.0 + verbose httpx logs
- **Fix:** Deferred handler wiring, poll_interval=2.0, httpx log suppression
- **E2E verified:** CPU from 50% → 4%
- **Merged directly** to release/2.4.0 (pre-MR, pushed)

### RAISE-1276 (2 SP) — Graph Index Unavailable in Worktrees
- **Classification:** Configuration / S2-Medium / Design / Missing
- **Pipeline:** Full 7-phase, all 3 gates
- **Root cause:** `.raise/rai/memory/` gitignored in TWO places (root + .raise/.gitignore)
- **Fix:** Remove ignore rules, commit memory directory as shared project state
- **GATE 2 adjustment:** User redirected from code fallback to simpler gitignore fix
- **MR:** !48

### RAISE-592 (1 SP) — Frontmatter Schemas Not Documented
- **Classification:** Interface / S2-Medium / Requirements / Missing
- **Pipeline:** Phases 3-7 (scope+triage pre-existing from prior session)
- **Root cause:** domain-model.md and system-design.md schemas lived only in parser code
- **Fix:** Added schema examples with pitfall warnings to rai-discover and rai-project-create
- **MR:** !55

### RAISE-1199 (2 SP) — Epic ID Collision Detection
- **Classification:** N/A — closed without fix
- **Pipeline:** Phase 0 (detect) only
- **Finding:** All 3 prevention measures already implemented: skill check (Step 2 in rai-epic-start), builder warn+skip (RAISE-648), no current collisions
- **Action:** Closed with comment, transitioned to Done

### RAISE-1063 (unestimated) — Stale raise-server Imports
- **Classification:** Interface / S2-Medium / Code / Incorrect
- **Pipeline:** Abbreviated (scope pre-existing, combined analyse+plan, fix+review)
- **Root cause:** Auth refactor renamed OrgContext→MemberContext, ApiKey→ApiKeyRow without updating raise-pro tests
- **Fix:** Updated 5 test files, 138 tests pass
- **MR:** !56

---

## Pipeline Compliance Analysis

### Phase Execution

| Phase | 1008 | 1276 | 592 | 1199 | 1063 |
|-------|:----:|:----:|:---:|:----:|:----:|
| Start | ✓ | ✓ | pre | skip | pre |
| Triage | ✓ | ✓ | pre | skip | pre |
| **GATE 1** | ✓ | ✓ | skip | skip | skip |
| Analyse | ✓ | ✓ | ✓ | skip | ✓ |
| **GATE 2** | ✓ | ✓* | skip | skip | skip |
| Plan | ✓ | ✓ | ✓ | skip | ✓ |
| Fix | ✓ | ✓ | ✓ | skip | ✓ |
| **GATE 3** | ✓ | ✓ | ✓ | skip | ✓ |
| Review | ✓ | ✓ | ✓ | skip | ✓ |
| Close | ✓ | ✓ | ✓ | ✓ | ✓ |

*GATE 2 on RAISE-1276: User adjusted strategy from code fallback to gitignore fix.

### Gate Effectiveness

| Gate | Fired | Adjustments | Value |
|------|:-----:|:-----------:|-------|
| GATE 1 (Scope) | 2 | 0 | Low — both scopes were correct |
| GATE 2 (Strategy) | 2 | 1 | **High** — RAISE-1276 strategy was wrong, user caught it |
| GATE 3 (Verification) | 4 | 0 | Low — all fixes were correct |

**Key insight:** GATE 2 was the only gate that caught an error this session. The proposed code fallback for RAISE-1276 was over-engineered — user redirected to the simpler gitignore fix. This validates GATE 2 as the highest-value checkpoint.

### Pipeline Shortcuts Taken

| Bug | Shortcut | Justification | Risk |
|-----|----------|---------------|------|
| RAISE-592 | Skipped GATE 1 | Scope+triage pre-existing, already validated | None |
| RAISE-1199 | Skipped entire pipeline | Already resolved | None |
| RAISE-1063 | Combined phases, skipped GATE 1+2 | Clear scope, obvious fix | Low — but missed plan for "team" vs "pro" |

**Observation:** RAISE-1063 required a second iteration because the initial fix used `plan="pro"` but routes require `plan="team"`. A proper GATE 2 would have caught this if we'd analyzed the auth dependency chain more carefully. The abbreviated pipeline works for simple fixes but masks dependency chain complexity.

### TDD Compliance

| Bug | RED→GREEN | Notes |
|-----|:---------:|-------|
| RAISE-1008 | N/A | Cherry-pick port, E2E verified manually |
| RAISE-1276 | ✓ | 2 regression tests (gitignore assertions) |
| RAISE-592 | N/A | Documentation-only fix |
| RAISE-1063 | N/A | Existing 138 tests served as regression suite |

---

## Skill Improvement Recommendations

### 1. GATE 2 is the critical gate — optimize for it

GATE 2 (Strategy) was the only gate that caught an error. Consider:
- Make GATE 2 present **multiple fix approaches** with trade-offs, not just the recommended one
- The user chose "just commit the file" over "write worktree fallback code" — simpler was better

### 2. Pipeline abbreviation protocol needed

For pre-triaged bugs (scope+triage exist from prior sessions), the pipeline spent time re-reading skills it didn't need. Recommendation:
- Phase detection already works (detected resume points)
- Add explicit "abbreviated pipeline" mode that skips GATE 1 when scope+triage are pre-existing
- Still require GATE 2 and GATE 3 always

### 3. "Already resolved" detection should be earlier

RAISE-1199 required creating a worktree, merging release/2.4.0, and reading code before discovering it was already fixed. Recommendation:
- Add a **Step 0.5: Check if fix already exists** between phase detection and worktree creation
- Check: Jira comments, git log for related commits, code search for mentioned fixes

### 4. Cross-package impact check missing

RAISE-1063 happened because an auth refactor didn't update downstream tests. The bugfix pipeline should include:
- During analyse phase: "What other packages consume the changed API?"
- During fix phase: "Run downstream test suites, not just the changed package"

### 5. Worktree overhead is real

Each worktree required: create → merge release/2.4.0 → install deps → work → push → exit → remove. For RAISE-1199 (already resolved), this was entirely wasted.
- Consider lightweight pre-check before entering worktree
- For 1 SP documentation fixes (RAISE-592), worktree isolation may be overkill

### 6. Skills distribution sync should be automatic

RAISE-592 fix included a skills sync step (T3) that exists only because skills_base/ doesn't auto-sync. The pre-commit gate added earlier today helps, but the sync step in every skill-touching bug is overhead.

---

## Patterns Extracted

| ID | Pattern | From |
|----|---------|------|
| PAT-E-599 | Shared project state must be committed, not gitignored, even if regenerable | RAISE-1276 |
| PAT-E-600 | Frontmatter schemas consumed by parsers must be documented in generating skills | RAISE-592 |

---

## Triage Accuracy

| Bug | Initial Triage | Post-Fix Assessment | Accurate? |
|-----|---------------|---------------------|:---------:|
| RAISE-1008 | Logic/S1-High/Code/Incorrect | Correct | ✓ |
| RAISE-1276 | Config/S2-Medium/Design/Missing | Correct | ✓ |
| RAISE-592 | Interface/S2-Medium/Requirements/Missing | Correct | ✓ |
| RAISE-1063 | Interface/S2-Medium/Code/Incorrect | Should be S3-Low (tests only) | ✗ |

Triage accuracy: 3/4 (75%). RAISE-1063 severity was overrated — broken tests in a non-shipped package are lower impact than broken production code.

---

*Report generated for continuous improvement of the rai-bugfix-run skill pipeline.*
