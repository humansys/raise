---
name: feature-close
description: >
  Complete a feature with retrospective verification, merge, cleanup,
  and tracking update. Use after review to formally close the feature
  lifecycle.

license: MIT

metadata:
  raise.work_cycle: feature
  raise.frequency: per-feature
  raise.fase: "8"
  raise.prerequisites: feature-review
  raise.next: ""
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "1.1.0"

hooks:
  Stop:
    - hooks:
        - type: command
          command: "RAISE_SKILL_NAME=feature-close \"$CLAUDE_PROJECT_DIR\"/.claude/skills/scripts/log-skill-complete.sh"
---

# Close: Feature Completion

## Purpose

Complete a feature by verifying the retrospective is done, merging to the parent branch, cleaning up the feature branch, and updating tracking. This formally closes the feature lifecycle with full traceability.

## Mastery Levels (ShuHaRi)

**Shu (守)**: Follow all steps, verify retrospective, merge with no-ff, update epic.

**Ha (破)**: Adjust merge strategy for small fixes; skip epic update for standalone.

**Ri (離)**: Integrate with CI/CD pipelines; automate cleanup workflows.

## Context

**When to use:**
- After `/feature-review` retrospective is complete
- Feature implementation is verified and tests pass
- Ready to merge work into parent branch

**When to skip:**
- Feature abandoned (use explicit abandon workflow)
- Feature continuing in next session (not complete yet)

**Inputs required:**
- Completed retrospective (see Path Convention below)
- Passing tests
- Feature branch ready for merge

**Path Convention (ISSUE-004):**
| Epic | Feature Artifacts Location |
|------|---------------------------|
| E14+ (new) | `work/epics/e{N}-{name}/features/f{N}.{M}-{name}/` |
| E1-E13 (legacy) | `work/features/{feature-id}/` |

**Output:**
- Feature merged to parent branch
- Feature branch deleted (local)
- Epic scope updated (feature marked complete)
- Telemetry emitted

## Steps

### Step 0.1: Verify Prerequisites (REQUIRED)

Retrospective and tests are required before closing:

```bash
# Check retrospective exists (E14+ tree or legacy)
RETRO=$(ls work/epics/e*/features/{feature_id}/retrospective.md 2>/dev/null || \
        ls work/features/{feature_id}/retrospective.md 2>/dev/null)
if [ -z "$RETRO" ]; then
    echo "ERROR: Retrospective not found for {feature_id}"
    echo "Run /feature-review first"
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

> **If you can't continue:** Run `/feature-review` first. No exceptions.

### Step 1: Verify Feature Ready

Confirm feature is complete:

```bash
# Determine feature artifacts path (E14+ tree or legacy)
FEATURE_DIR=$(ls -d work/epics/e*/features/{feature_id} 2>/dev/null || \
              ls -d work/features/{feature_id} 2>/dev/null)

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

### Step 2: Identify Parent Branch

Determine the merge target:

```bash
# Get current branch
CURRENT=$(git branch --show-current)
echo "Current branch: $CURRENT"

# Determine parent (epic or main development branch)
# Pattern: feature/{epic}/{feature} → epic/{epic}/...
# Pattern: feature/standalone/... → v2 (or main)
```

**Branch hierarchy:**
- `feature/e12/f12-2` → merges to `epic/e12/...`
- `feature/standalone/fx` → merges to `v2`
- `epic/e12/...` → eventually merges to `v2`

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
git merge --no-ff {feature_branch} -m "feat({feature_id}): merge complete feature

Completed:
- [summary of what was delivered]

Artifacts:
- {FEATURE_DIR}/plan.md
- {FEATURE_DIR}/retrospective.md

Co-Authored-By: Rai <rai@humansys.ai>"
```

**Why `--no-ff`:** Preserves feature branch history as a unit; enables easy revert if needed.

**Verification:** Merge commit created on parent branch.

> **If you can't continue:** Merge conflicts → Resolve conflicts, then complete merge.

### Step 5: Update Epic Scope (If Epic Feature)

Mark the feature complete in the epic scope:

```bash
# In epic scope (E14+: work/epics/.../scope.md or legacy: dev/epic-{epic_id}-scope.md), update feature status
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

Clean up the feature branch after merge:

```bash
# Delete local branch (use -D since merge is verified)
git branch -D {feature_branch}

# Delete remote branch if it exists
git push origin --delete {feature_branch} 2>/dev/null || echo "No remote branch to delete"
```

**Why `-D` not `-d`:** After Step 4's merge, the branch content is in the parent. Using `-d` fails if there's a remote tracking branch, leading to branch accumulation. Since we've verified the merge, `-D` is safe.

**Why delete remote:** Prevents branch accumulation. The merge commit preserves history; the branch is no longer needed.

**Verification:** Feature branch deleted (local and remote).

> **If you can't continue:** Branch deletion fails → Check you're not on the feature branch (should be on parent after Step 4).

### Step 7: Emit Feature Complete (Telemetry)

Record the completion of the entire feature lifecycle:

```bash
uv run raise telemetry emit feature {feature_id} --event complete --phase review
```

**Example:** `raise telemetry emit feature F12.2 -e complete -p review`

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
- **Telemetry:** `.raise/rai/telemetry/signals.jsonl` (feature complete)
- **Context:** `CLAUDE.local.md` updated

## Feature Close Summary Template

```markdown
## Feature Closed: {feature_id}

**Branch:** `feature/{epic_id}/{feature_id}` → merged to `{parent}`
**Merge commit:** {commit_hash}

### Delivered
- [Key deliverable 1]
- [Key deliverable 2]

### Artifacts
- `{FEATURE_DIR}/plan.md`
- `{FEATURE_DIR}/retrospective.md`

*Note: FEATURE_DIR is `work/epics/.../features/{feature_id}` for E14+ or `work/features/{feature_id}` for legacy*

### Epic Progress
- **{epic_id}:** N/M features complete (X%)

### Next Feature
- **{next_feature_id}:** {description}

Feature lifecycle complete.
```

## Notes

### Feature Lifecycle Summary

```
/feature-start (fase 3)
      ↓
/feature-design (fase 4)
      ↓
/feature-plan (fase 5)
      ↓
/feature-implement (fase 6)
      ↓
/feature-review (fase 7)
      ↓
/feature-close (fase 8) ← YOU ARE HERE
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

- Previous skill: `/feature-review`
- Complement: `/feature-start`
- Epic scope:
  - E14+: `work/epics/e{N}-{name}/scope.md`
  - E1-E13 (legacy): `dev/epic-{id}-scope.md`
