---
name: rai-bugfix-close-enterprise
description: Push branch, create MR, verify artifacts complete. Phase 7 of bugfix pipeline.
model: haiku

allowed-tools:
  - Read
  - "Bash(git:*)"
  - "Bash(glab:*)"
  - "Bash(rai:*)"

license: MIT
metadata:
  raise.adaptable: 'true'
  raise.fase: '7'
  raise.frequency: per-bug
  raise.gate: ''
  raise.next: ''
  raise.prerequisites: bugfix-review
  raise.skillset: raise-maintainability
  raise.version: 2.4.0
  raise.visibility: public
  raise.work_cycle: bugfix
  raise.inputs: |
    - bug_id: string, required, argument
    - dev_branch: string, required, config
  raise.outputs: |
    - mr_url: string, terminal
---

# Bugfix Close

## Purpose

Push the bug branch, create a merge request targeting the development branch, and clean up the local branch. All artifacts must exist before closing.

## Mastery Levels (ShuHaRi)

- **Shu**: Follow all steps, verify all 4 artifacts, create MR
- **Ha**: Streamline for batch closures
- **Ri**: Automated close with CI/CD integration

## Context

**When to use:** After `/rai-bugfix-review` has produced the retrospective artifact.

**When to skip:** Never — closing is how bug work becomes visible to the team.

**Inputs:** Bug ID, `{dev_branch}` from `.raise/manifest.yaml`.

**Expected state:** On bug branch. All 4 canonical artifacts (scope.md, analysis.md, plan.md, retro.md) present, or legitimately skipped per ADR-116 proportionality. Gates passed in fix phase.

## Steps

### Pipeline Context Check (RAISE-10715)

Before executing any step, verify this skill was invoked via the pipeline engine:

1. Check if `Run ID:` appears in the context above (injected by `pipeline/prompt.py`)
2. If **present**: continue silently — pipeline is orchestrating
3. If **absent**: **STOP and present HITL gate:**

> **Standalone execution detected.** This skill is running outside the pipeline engine.
> Prior phases (review, PIR) may have been skipped.
>
> Options:
> 1. Continue anyway (acknowledge that prior phases were skipped)
> 2. Abort and investigate why the pipeline engine is not orchestrating

Wait for the user's explicit choice before proceeding. This gate fires even in Ri mode — standalone execution is a signal of broken infrastructure, not a routine gate.

### Step 1: Verify Completeness & Clean Tree

Verify the 4 canonical artifacts against their owning phase, not blind file
existence — ADR-116 proportionality legitimately skips phases (and therefore
their artifacts) for small bugs, and a static existence check cannot tell
"skipped by design" apart from "missing by error" (RAISE-11751).

Artifact → owning phase map:

| Artifact    | Owning phase |
|-------------|--------------|
| scope.md    | `start`      |
| analysis.md | `analyse`    |
| plan.md     | `plan`       |
| retro.md    | `review`     |

**If a Run ID is present in context** (per the Pipeline Context Check above —
pipeline-orchestrated):

1. Call the `pipeline_status` MCP tool (`mcp__rai-workspace__pipeline_status`)
   with the run's `run_id`. The response's `phases` array gives each phase's
   `id` and `status` — build a `{phase_id -> status}` map from it.
2. For each of the 4 artifacts:
   - File exists on disk → ✓ pass.
   - File absent AND its owning phase's `status == "skipped"` → ✓ pass
     (intentional by ADR-116 proportionality — do not block).
   - File absent AND owning phase status is anything else (ran, or not found
     in the map) → **STOP** — run the missing phase skill first.
3. Do not re-derive `size >= …` thresholds yourself — `pipeline_status` is
   the authoritative source; re-evaluating the `when` condition here would
   duplicate the engine's logic and reintroduce drift.

**If no Run ID is present** (standalone execution — already surfaced via the
Pipeline Context Check HITL gate above): keep the blind file-existence check,
since there is no pipeline run to consult and intent cannot be established:

```bash
for f in scope.md analysis.md plan.md retro.md; do
  [ -f "work/bugs/{issue_key}/$f" ] && echo "✓ $f" || echo "ERROR: Missing $f"
done
```

Then, regardless of path taken:

```bash
git status --short
```

| Condition | Action |
|-----------|--------|
| All 4 artifacts pass (present, or absent-and-skipped) + clean tree | Continue |
| Any artifact missing and not legitimately skipped | **STOP** — run the missing phase skill first |
| Uncommitted changes | Commit them before push |

<verification>
All 4 artifacts verified (present, or absent with owning phase confirmed
`skipped`). Working tree clean.
</verification>

### Step 1b: Architecture Review Gate

Verification only. The P1 drift / P2 Beck-R2 / P3 convention checklist runs
in `/rai-bugfix-review`, which writes the branch-and-session-scoped
attestation marker as its output. Close never creates or removes that
marker itself — attesting and verifying in the same command let the gate
pass unconditionally (RAISE-14326 / ADR-130: attestation and verification
must not be the same actor at the same instant; mirrors the story
pipeline's split, RAISE-14277). This step only checks:

```bash
rai gate check gate-ar-bugfix
```

> RAISE-12207: do **not** delete the marker here. The pipeline engine re-checks
> `gate-ar-bugfix` at the `before:bug:close` emit (when it marks the `close`
> phase done); the marker MUST still exist then or the engine blocks the close.
> The marker is session-scoped and cleaned up at session end.

Escape hatch (XS/docs/tooling — no production code changed):
```bash
RAISE_AR_SKIP_REASON="<reason>" rai gate check gate-ar-bugfix
```

| Condition | Action |
|-----------|--------|
| Gate passes | Continue to Step 2 |
| Gate fails (no session) | Set `RAISE_CC_SESSION_ID` or use escape hatch |
| Gate fails (no marker) | Run `/rai-bugfix-review`'s P1/P2/P3 checklist and attest first |
| Escape hatch used | Reason logged in gate result — continues |

<verification>
AR gate passed. Reason logged if escape hatch was used.
</verification>

### Step 2: Push & Create MR

**Never merge locally to `{dev_branch}`.**

```bash
git push origin bug/{issue_key}/{slug} -u

glab mr create \
  --source-branch bug/{issue_key}/{slug} \
  --target-branch {dev_branch} \
  --title "fix({issue_key}): {summary}" \
  --description "Root cause: {one line}

Co-Authored-By: Rai <rai@humansys.ai>" \
  --no-editor
```

If `glab` is not available, provide the GitLab URL from `git push` output for manual MR creation.

<verification>
MR created in GitLab targeting `{dev_branch}`.
</verification>

<if-blocked>
`glab` not available → provide push URL for manual MR creation.
</if-blocked>

### Step 2b: Enforce Jira consistency (RAISE-10966, code-enforced RAISE-11770)

1. Derive the active release version from the manifest `branches.development`
   (e.g. `release/3.1.0` → `3.1.0`) and assign it as the fixVersion:
   ```bash
   rai backlog update {bug_key} -F 'fixVersions=[{"name": "{version}"}]'
   ```
2. Do not run `gate-close-jira-sync` directly in this skill: Jira is not Done
   until the engine owns the transition. After the skill returns, the next
   `pipeline_advance` first applies `target_status: done` and then enforces
   the gate at `after:bug:close`. A `gate_failed` result is blocking and means
   **FAIL the close** — do not log-and-continue or substitute a manual read.

| Condition | Action |
|-----------|--------|
| No ticket | Skip |
| `gate-close-jira-sync` fails | **FAIL the close** — Jira must not diverge from git |
| fixVersion assignment fails | **FAIL the close** |

<if-blocked>
fixVersion assignment fails, or the `after:bug:close` postcondition
reports not-Done/fixVersion mismatch → **FAIL the close** (RAISE-10966,
code-enforced by RAISE-11770). The close cannot complete while Jira status
or version diverges from git. The MR still exists; fix the Jira sync and
re-run close.
</if-blocked>

> **Known follow-up (out of scope for RAISE-11770):** Step 2 (MR creation)
> still runs before this Jira-sync block, so a failure here cannot un-create
> the MR — it can only block the *close* from completing. Reordering Jira
> sync ahead of MR creation is a larger skill-restructuring change; tracked
> as a follow-up recommendation, not fixed here.

### Step 3: Cleanup

```bash
# Linked worktree? --git-dir differs from --git-common-dir only in a worktree.
if [ "$(git rev-parse --git-common-dir)" != "$(git rev-parse --git-dir)" ]; then
  echo "Worktree detected — leaving HEAD on $(git rev-parse --abbrev-ref HEAD); branch cleanup deferred to /rai-worktree-close."
else
  git checkout {dev_branch}
  git branch -D bug/{issue_key}/{slug}
fi
```

<verification>
Main checkout: local bug branch deleted, HEAD on `{dev_branch}`.
Worktree: HEAD unchanged (still on the bug branch), message shown, branch cleanup deferred to `/rai-worktree-close`.
</verification>

## Scope Constraints (CRITICAL)

Close is a **merge-request-only operation**:

- **NEVER edit source code, skill files, config, or governance docs**
- **NEVER create "fix" or "refactor" commits**
- **NEVER delete directories or files outside the bug branch**
- **NEVER revert or modify commits on `{dev_branch}`**

If something looks wrong, return it as a finding — do not act on it.

## Output

| Item | Destination |
|------|-------------|
| Merge request | GitLab MR: bug branch → `{dev_branch}` |
| Backlog update | fixVersion via `rai backlog update` + `gate-close-jira-sync` (blocking, code-enforced — RAISE-10966/RAISE-11770); Jira transition is engine-owned (RAISE-15027) |

**STOP HERE.** Return your summary to the orchestrator. Do NOT invoke any further skill.

## Quality Checklist

- [ ] All 4 artifacts verified before closing (present, or absent-and-confirmed-skipped per ADR-116)
- [ ] Working tree clean before push
- [ ] MR created in GitLab targeting `{dev_branch}`
- [ ] Local branch deleted after MR creation (non-worktree case) — worktree case defers to /rai-worktree-close
- [ ] No files modified outside scope constraints
- [ ] NEVER merge locally to `{dev_branch}` — always via MR

## References

- Previous: `/rai-bugfix-review`
- Complement: `/rai-bugfix-start`
- Branch model: `AGENTS.md` § Branch Model
