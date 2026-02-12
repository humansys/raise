---
name: rai-story-close
description: >
  Complete a story with retrospective verification, merge, cleanup,
  and tracking update. Use after review to formally close the story
  lifecycle.

license: MIT

metadata:
  raise.work_cycle: story
  raise.frequency: per-story
  raise.fase: "8"
  raise.prerequisites: story-review
  raise.next: ""
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "1.1.0"
---

# Close: Feature Completion

## Purpose

Complete a feature by verifying the retrospective is done, merging to the parent branch, cleaning up the story branch, and updating tracking. This formally closes the story lifecycle with full traceability.

## Mastery Levels (ShuHaRi)

**Shu (守)**: Follow all steps, verify retrospective, merge with no-ff, update epic.

**Ha (破)**: Adjust merge strategy for small fixes; skip epic update for standalone.

**Ri (離)**: Integrate with CI/CD pipelines; automate cleanup workflows.

## Context

**When to use:**
- After `/rai-story-review` retrospective is complete
- Feature implementation is verified and tests pass
- Ready to merge work into parent branch

**When to skip:**
- Feature abandoned (use explicit abandon workflow)
- Feature continuing in next session (not complete yet)

**Inputs required:**
- Completed retrospective: `work/epics/e{N}-{name}/stories/f{N}.{M}-{name}/retrospective.md`
- Passing tests
- Feature branch ready for merge

**Output:**
- Feature merged to parent branch
- Feature branch deleted (local)
- Epic scope updated (feature marked complete)
- Telemetry emitted

## Steps

### Step 0.1: Verify Prerequisites (REQUIRED)

Retrospective and tests are required before closing:

```bash
RETRO="work/epics/e{N}-{name}/stories/{story_id}/retrospective.md"
if [ ! -f "$RETRO" ]; then
    echo "ERROR: Retrospective not found: $RETRO"
    echo "Run /rai-story-review first"
    exit 4  # ArtifactNotFoundError
fi

# Check tests pass
uv run pytest --tb=no -q || {
    echo "ERROR: Tests must pass before close"
    exit 10  # GateFailedError
}
```

**No skip:** Retrospective captures learnings; tests verify quality.

**Verification:** Retrospective exists and tests pass.

> **If you can't continue:** Run `/rai-story-review` first. No exceptions.

### Step 1: Verify Feature Ready

Confirm feature is complete:

```bash
FEATURE_DIR="work/epics/e{N}-{name}/stories/{story_id}"

# Show feature artifacts
ls -la "$FEATURE_DIR/"

# Check for required artifacts
[ -f "$FEATURE_DIR/plan.md" ] && echo "✓ Plan exists"
[ -f "$FEATURE_DIR/retrospective.md" ] && echo "✓ Retrospective exists"
```

**Required artifacts:**
- `plan.md` — Implementation plan (always)
- `retrospective.md` — Learnings captured (always)
- `design.md` — Optional (for complex features)
- `progress.md` — Optional (implementation tracking)

**Verification:** Required artifacts present.

> **If you can't continue:** Missing artifacts → Complete the missing phase first.

### Step 1.5: Check for Structural Drift

If this story added new modules, changed directory structure, or altered data flow paths, the architecture docs must be updated before closing.

```bash
# Compare source modules vs documented modules
SOURCE_MODULES=$(ls -d src/rai_cli/*/ 2>/dev/null | sed 's|src/rai_cli/||;s|/$||' | grep -v __pycache__ | sort)
DOC_MODULES=$(ls governance/architecture/modules/*.md 2>/dev/null | sed 's|governance/architecture/modules/||;s|\.md$||' | sort)

# Show any undocumented modules
MISSING=$(comm -23 <(echo "$SOURCE_MODULES") <(echo "$DOC_MODULES"))
if [ -n "$MISSING" ]; then
    echo "WARNING: Undocumented modules detected:"
    echo "$MISSING"
    echo "Create module docs in governance/architecture/modules/ before closing."
fi
```

**Also check manually:**
- Did this story change where data is written (paths, directories)?
- Did this story move data between scopes (project → personal, memory → personal)?
- Did this story add new inter-module dependencies?

If any of the above: update the relevant module doc in `governance/architecture/modules/` so the graph carries the correct structure to future sessions.

**Why this matters:** New code in future sessions uses the graph as its map. Stale architecture docs cause path bugs and rework (PAT-151).

**Verification:** No undocumented modules. Module docs reflect current paths and data flow.

> **If drift detected:** Update the module doc now. This is a 5-minute task that prevents hours of rework.

### Step 2: Identify Parent Branch

Determine the merge target:

```bash
# Get current branch
CURRENT=$(git branch --show-current)
echo "Current branch: $CURRENT"

# Determine parent (epic or main development branch)
# Pattern: feature/{epic}/{feature} → epic/{epic}/...
# Pattern: feature/standalone/... → {dev_branch}
```

**Branch hierarchy:**
- `feature/e12/f12-2` → merges to `epic/e12/...`
- `feature/standalone/fx` → merges to `{dev_branch}` (read from `.raise/manifest.yaml` → `branches.development`)
- `epic/e12/...` → eventually merges to `{dev_branch}`

**Verification:** Parent branch identified.

> **If you can't continue:** Unclear parent → Ask or default to development branch.

### Step 3: Final Test Run

Run full test suite before merge:

```bash
uv run pytest --tb=short
```

**Expected:** All tests pass.

**Verification:** Test suite green.

> **If you can't continue:** Tests failing → Fix before merge. Do not merge broken code.

### Step 4: Merge to Parent Branch

Merge with a clear merge commit:

```bash
# Switch to parent branch
git checkout {parent_branch}

# Merge with no-ff to preserve feature history
git merge --no-ff {feature_branch} -m "feat({story_id}): merge complete feature

Completed:
- [summary of what was delivered]

Artifacts:
- {FEATURE_DIR}/plan.md
- {FEATURE_DIR}/retrospective.md

Co-Authored-By: Rai <rai@humansys.ai>"
```

**Why `--no-ff`:** Preserves story branch history as a unit; enables easy revert if needed.

**Verification:** Merge commit created on parent branch.

> **If you can't continue:** Merge conflicts → Resolve conflicts, then complete merge.

### Step 5: Update Epic Scope (If Epic Feature)

Mark the story complete in the epic scope:

```bash
# In epic scope (work/epics/e{N}-{name}/scope.md), update feature status
# Change: - [ ] F12.2 Guardrails Extractor
# To:     - [x] F12.2 Guardrails Extractor ✓
```

**Update patterns:**

1. **Feature checklist** (if present):
```markdown
## Features
- [x] F12.1 ADR Extractor ✓ (completed 2026-02-03)
- [x] F12.2 Guardrails Extractor ✓ (completed 2026-02-03)
- [ ] F12.3 Term Extractor — In progress
```

2. **Progress Tracking table** (if present):
```markdown
| Feature | Size | SP | Status | Actual | Velocity | Notes |
|---------|:----:|:--:|:------:|:------:|:--------:|-------|
| F7.2 Convention Detection | M | 3 | ✅ Done | 40 min | 3.75x | |
| F7.3 Governance Generation | S | 2 | ✅ Done | 20 min | 4.0x | ← UPDATE |
```

**Verification:** Epic scope reflects feature completion (both formats if present).

> **If you can't continue:** Standalone feature → Skip epic update.

### Step 6: Delete Feature Branch (REQUIRED)

Clean up the story branch after merge:

```bash
# Delete local branch (use -D since merge is verified)
git branch -D {feature_branch}

# Delete remote branch if it exists
git push origin --delete {feature_branch} 2>/dev/null || echo "No remote branch to delete"
```

**Why `-D` not `-d`:** After Step 4's merge, the branch content is in the parent. Using `-d` fails if there's a remote tracking branch, leading to branch accumulation. Since we've verified the merge, `-D` is safe.

**Why delete remote:** Prevents branch accumulation. The merge commit preserves history; the branch is no longer needed.

**Verification:** Feature branch deleted (local and remote).

> **If you can't continue:** Branch deletion fails → Check you're not on the story branch (should be on parent after Step 4).

### Step 7: Emit Feature Complete (Telemetry)

Record the completion of the entire story lifecycle:

```bash
rai memory emit-work story {story_id} --event complete --phase review
```

**Example:** `rai memory emit-work story S15.1 -e complete -p review`

**Verification:** Telemetry emitted.

> **If you can't continue:** CLI not available → Skip; telemetry is optional.

### Step 8: Update Local Context

Update `CLAUDE.local.md` to reflect completion:

```markdown
## Current Focus

| Field | Value |
|-------|-------|
| Feature | F12.3 Term Extractor ← NEXT |
| Completed | F12.2 ✓ |
```

**Verification:** Local context reflects completion and next focus.

## Output

- **Merge:** Feature merged to parent branch with `--no-ff`
- **Cleanup:** Feature branch deleted locally
- **Epic:** Feature marked complete in epic scope
- **Telemetry:** `.raise/rai/personal/telemetry/signals.jsonl` (story complete)
- **Context:** `CLAUDE.local.md` updated

## Feature Close Summary Template

```markdown
## Feature Closed: {story_id}

**Branch:** `feature/{epic_id}/{story_id}` → merged to `{parent}`
**Merge commit:** {commit_hash}

### Delivered
- [Key deliverable 1]
- [Key deliverable 2]

### Artifacts
- `{FEATURE_DIR}/plan.md`
- `{FEATURE_DIR}/retrospective.md`


### Epic Progress
- **{epic_id}:** N/M features complete (X%)

### Next Feature
- **{next_story_id}:** {description}

Feature lifecycle complete.
```

## Notes

### Feature Lifecycle Summary

```
/rai-story-start (fase 3)
      ↓
/rai-story-design (fase 4)
      ↓
/rai-story-plan (fase 5)
      ↓
/rai-story-implement (fase 6)
      ↓
/rai-story-review (fase 7)
      ↓
/rai-story-close (fase 8) ← YOU ARE HERE
```

### Branch Hygiene Philosophy

**Clean as you go.** Branches are deleted immediately after merge because:
1. The merge commit preserves all history
2. Accumulated branches create confusion and technical debt
3. "I'll clean later" leads to 20+ stale branches (learned 2026-02-05)

If your workflow requires preserving remote branches (PR automation, audit trails), adjust Step 6 to skip remote deletion.

### Quick Close (Minimal)

For urgency, minimum viable close:
1. Verify tests pass
2. Merge to parent
3. Emit telemetry

Epic update and branch cleanup can be batched.

### Abandoned Features

If feature is abandoned (not completed):
1. Document why in a note
2. Delete branch without merge
3. Emit telemetry with `--event abandoned`
4. Update epic scope with note

## References

- Previous skill: `/rai-story-review`
- Complement: `/rai-story-start`
- Epic scope: `work/epics/e{N}-{name}/scope.md`
