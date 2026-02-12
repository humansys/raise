---
name: rai-epic-close
description: >
  Complete an epic with retrospective, metrics capture, branch cleanup,
  and merge to development branch. Use after all stories are done
  to formally close the epic lifecycle.

license: MIT

metadata:
  raise.work_cycle: epic
  raise.frequency: per-epic
  raise.fase: "epic-close"
  raise.prerequisites: all stories complete
  raise.next: ""
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "1.0.0"
---

# Epic Close: Epic Completion & Retrospective

## Branch Configuration

**Read `branches.development` from `.raise/manifest.yaml`** to determine the project's development branch. All references to `{dev_branch}` below use this value. Default: `main`.

## Purpose

Complete an epic by conducting a retrospective, capturing metrics, cleaning up all branches, and merging to the development branch. This formally closes the epic lifecycle with learnings captured for continuous improvement.

**CRITICAL:** Never merge an epic without running this skill. The retrospective captures learnings that compound across epics.

## Mastery Levels (ShuHaRi)

**Shu (守)**: Follow all steps, complete full retrospective, clean all branches.

**Ha (破)**: Adjust retrospective depth based on epic complexity; batch small epics.

**Ri (離)**: Integrate with release workflows; automate metrics extraction.

## Context

**When to use:**
- All features in the epic are complete (merged to epic branch)
- Ready to merge epic work into development branch (`{dev_branch}`)
- Want to capture learnings before moving to next epic

**When to skip:**
- Epic abandoned (document why, delete branches, no merge)
- Epic continuing (not all stories done yet)

**Inputs required:**
- Epic scope document: `work/epics/e{N}-{name}/scope.md`
- All features complete with retrospectives
- Epic branch with all work merged
- Passing tests

**Output:**
- Epic retrospective document
- Epic merged to development branch
- All epic and story branches deleted
- Backlog updated (epic marked complete)
- Telemetry emitted

## Steps

### Step 1: Verify All Features Complete (REQUIRED)

Check that all stories are done:

```bash
SCOPE="work/epics/e{N}-{name}/scope.md"

# Review epic scope for feature checklist
cat "$SCOPE" | grep -E "^\s*-\s*\[.\]"

# Verify no incomplete features
if grep -E "^\s*-\s*\[ \]" "$SCOPE" | grep -i "F{epic_id}"; then
    echo "ERROR: Incomplete features found"
    exit 4
fi
```

**Verification:** All features marked complete in epic scope.

> **If you can't continue:** Incomplete features → Complete them first or explicitly descope.

### Step 2: Run Full Test Suite (REQUIRED)

Verify everything works together:

```bash
uv run pytest --tb=short
```

**Expected:** All tests pass.

**Verification:** Test suite green.

> **If you can't continue:** Tests failing → Fix before merge.

### Step 3: Create Epic Retrospective (REQUIRED)

Create retrospective: `work/epics/e{N}-{name}/retrospective.md`

Template:

```markdown
# Epic Retrospective: E{N} {Epic Name}

**Completed:** YYYY-MM-DD
**Duration:** X days (started YYYY-MM-DD)
**Features:** N features delivered

---

## Summary

[2-3 sentence summary of what was delivered and its impact]

---

## Metrics

| Metric | Value | Notes |
|--------|-------|-------|
| Features Delivered | N | |
| Story Points | X SP | |
| Tests Added | N | |
| Average Velocity | X.Xx | vs baseline |
| Calendar Days | N | |

### Feature Breakdown

| Feature | Size | SP | Velocity | Key Learning |
|---------|:----:|:--:|:--------:|--------------|
| F{N}.1 | S | 2 | 2.5x | [learning] |
| F{N}.2 | M | 3 | 3.0x | [learning] |

---

## What Went Well

- [Positive outcome 1]
- [Positive outcome 2]

## What Could Be Improved

- [Improvement area 1]
- [Improvement area 2]

## Patterns Discovered

| ID | Pattern | Context |
|----|---------|---------|
| PAT-XXX | [pattern description] | [when to apply] |

## Process Insights

- [Insight about RaiSE methodology]
- [Insight about collaboration]

---

## Artifacts

- **Scope:** `work/epics/e{N}-{name}/scope.md`
- **Features:** `work/epics/e{N}-{name}/stories/`
- **ADRs:** [list any ADRs created]
- **Tests:** N new tests

---

## Next Steps

- [What follows this epic]
- [Dependencies unblocked]

---

*Epic retrospective - captures learning for continuous improvement*
```

**Verification:** Retrospective document created with metrics and learnings.

> **If you can't continue:** No data → Review story retrospectives and git history.

### Step 4: Merge Epic to Development Branch (REQUIRED)

Merge the epic branch to `{dev_branch}`:

```bash
# Ensure on epic branch with latest
git checkout epic/{epic_id}/{name}
git pull origin epic/{epic_id}/{name} 2>/dev/null || true

# Switch to development branch
git checkout {dev_branch}
git pull origin {dev_branch}

# Merge with descriptive commit
git merge --no-ff epic/{epic_id}/{name} -m "Merge epic/{epic_id}/{name}: {Epic Name}

Delivered:
- [Key deliverable 1]
- [Key deliverable 2]
- [Key deliverable 3]

Features: N features, X SP
Tests: N new tests
Velocity: X.Xx average

Retrospective: dev/epic-{epic_id}-retrospective.md

Co-Authored-By: Rai <rai@humansys.ai>"
```

**Verification:** Merge commit created on `{dev_branch}`.

> **If you can't continue:** Merge conflicts → Resolve carefully, preserving all epic work.

### Step 5: Clean Up All Branches (REQUIRED)

Delete the epic branch and any remaining story branches:

```bash
# List all branches for this epic
git branch | grep -E "(epic|feature).*{epic_id}"

# Delete epic branch (local and remote)
git branch -D epic/{epic_id}/{name}
git push origin --delete epic/{epic_id}/{name} 2>/dev/null || echo "No remote epic branch"

# Delete any remaining story branches
for branch in $(git branch | grep "feature.*{epic_id}"); do
    git branch -D $branch
    git push origin --delete $branch 2>/dev/null || true
done
```

**Why clean all:** Prevents branch accumulation. The merge commit preserves history.

**Verification:** No branches remain for this epic (local or remote).

> **If you can't continue:** Branch deletion fails → Ensure you're on `{dev_branch}`, not a branch being deleted.

### Step 6: Update Backlog (REQUIRED)

Mark the epic complete in `governance/backlog.md`:

```markdown
## Epics

| ID | Name | Status | Scope |
|----|------|--------|-------|
| E{N} | {Name} | ✅ Complete | `dev/epic-{id}-scope.md` |
```

**Verification:** Backlog reflects epic completion.

### Step 7: Emit Epic Complete Telemetry

Record the epic completion:

```bash
rai memory emit-work epic {epic_id} --event complete
```

**Verification:** Telemetry emitted.

> **If you can't continue:** CLI not available → Skip; telemetry is optional.

### Step 8: Update Local Context

Update `CLAUDE.local.md`:

```markdown
## Current Focus

| Field | Value |
|-------|-------|
| Epic | **E{N+1} {Next Epic}** |
| Completed Epics | E1 ✓, E2 ✓, ... E{N} ✓ |
```

**Verification:** Local context reflects completion and next epic.

## Output

- **Retrospective:** `work/epics/e{N}-{name}/retrospective.md`
- **Merge:** Epic merged to `{dev_branch}` with `--no-ff`
- **Cleanup:** All epic and story branches deleted (local and remote)
- **Backlog:** Epic marked complete
- **Telemetry:** `.raise/rai/personal/telemetry/signals.jsonl` (epic complete)
- **Context:** `CLAUDE.local.md` updated

## Epic Close Summary Template

```markdown
## Epic Closed: E{N} {Epic Name}

**Branch:** `epic/{epic_id}/{name}` → merged to `{dev_branch}`
**Merge commit:** {commit_hash}
**Duration:** X days

### Delivered
- N features
- X story points
- N new tests
- X.Xx average velocity

### Key Learnings
- [Learning 1]
- [Learning 2]

### Patterns Captured
- PAT-XXX: [description]

### Branches Cleaned
- epic/{epic_id}/{name} ✓
- [any story branches] ✓

### Next
- E{N+1}: {Next Epic Name}

Epic lifecycle complete.
```

## Notes

### Why Retrospectives Are Mandatory

The retrospective captures:
1. **Velocity data** — Calibrates future estimates
2. **Patterns** — Reusable insights for other work
3. **Process improvements** — Makes RaiSE better
4. **Team memory** — Learnings persist beyond individuals

Skipping retrospectives loses compound learning.

### Epic Lifecycle Summary

```
/rai-epic-design (scope, features, architecture)
      ↓
/rai-epic-plan (sequence, milestones, dependencies)
      ↓
[Feature cycles: start → design → plan → implement → review → close]
      ↓
/rai-epic-close (retrospective, merge, cleanup) ← YOU ARE HERE
```

### Branch Hygiene

**Clean as you go.** After this skill:
- No `epic/{epic_id}/*` branches should exist
- No `feature/{epic_id}/*` branches should exist
- All work is in `{dev_branch}` via merge commit

### Abandoned Epics

If epic is abandoned (not completed):
1. Document why in a note
2. Delete all branches without merge
3. Update backlog with status "Abandoned: [reason]"
4. Capture any partial learnings

## References

- Previous: All feature `/rai-story-close` completions
- Epic scope: `work/epics/e{N}-{name}/scope.md`
- Backlog: `governance/backlog.md`
- Next: `/rai-epic-design` for next epic
