---
name: rai-story-close
description: >
  Complete a story with retrospective verification, push to origin,
  create merge request, and update tracking. Use after review to
  formally close the story lifecycle.

license: MIT

metadata:
  raise.work_cycle: story
  raise.frequency: per-story
  raise.fase: "8"
  raise.prerequisites: story-review
  raise.next: ""
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "3.0.0"
  raise.visibility: public
  raise.inputs: |
    - retrospective_md: file_path, required, previous_skill
    - tests_passing: boolean, required, cli
    - dev_branch: string, required, config
  raise.outputs: |
    - merge_commit: string, git
---

# Story Close

## Purpose

Complete a story by verifying the retrospective, pushing the story branch to origin, creating a merge request to the development branch, and updating epic tracking.

## Mastery Levels (ShuHaRi)

- **Shu**: Follow all steps, verify retrospective, push + create MR, update epic
- **Ha**: Adjust MR description for small fixes, skip epic update for standalone
- **Ri**: Integrate with CI/CD pipelines, automate cleanup workflows

## Context

**When to use:** After `/rai-story-review` retrospective is complete. Story is verified and tests pass.

**When to skip:** Story abandoned (document why, delete branch without merge, update epic as "Abandoned").

**Inputs:** Completed retrospective, passing test suite, story branch ready for merge.

**Branch config:** Read `branches.development` from `.raise/manifest.yaml` for `{dev_branch}`. Default: `main`.

## Steps

### Step 1: Verify Retrospective & All Gates

```bash
RETRO="work/epics/e{N}-{name}/stories/{story_id}-retrospective.md"
[ -f "$RETRO" ] && echo "✓ Retrospective" || echo "ERROR: Run /rai-story-review first"
```

Run **all four gates** before pushing. Resolve commands from `.raise/manifest.yaml` or use defaults (see `/rai-story-implement` Step 3 for the full table):

1. **Tests** — `project.test_command` or language default
2. **Lint** — `project.lint_command` or language default
3. **Format** — `project.format_command` or language default (e.g. `uv run ruff format --check src/ tests/`)
4. **Type check** — `project.type_check_command` or language default (e.g. `uv run pyright`)

| Condition | Action |
|-----------|--------|
| Retro exists + all 4 gates green | Continue |
| Retro missing | Run `/rai-story-review` first — no exceptions |
| Any gate failing | Fix before push — CI will reject the same errors |

Check for structural drift: if this story added modules or changed directory structure, update module docs in `governance/architecture/modules/` before closing.

<verification>
Retrospective exists. All four gates pass (test, lint, format, types). No undocumented structural changes.
</verification>

### Step 2: Verify Clean Working Tree

```bash
git status --short
```

| Condition | Action |
|-----------|--------|
| Working tree clean | Continue to merge |
| Uncommitted changes from this story | **Commit them** before merge — artifacts must not be orphaned |
| Unrelated changes | Stash or commit separately with `chore:` prefix |

**NEVER merge with uncommitted story artifacts.** Files created during design, plan, or implementation that aren't committed will be silently lost or orphaned on the target branch.

<verification>
`git status` shows clean working tree (or only unrelated files explicitly acknowledged).
</verification>

### Step 3: Push and Create Merge Request

**Never merge locally to `{dev_branch}`.** Push the story branch and create a merge request in GitLab.

```bash
# Push story branch to origin
git push origin {story_branch} -u

# Create merge request via glab
glab mr create \
  --source-branch {story_branch} \
  --target-branch {dev_branch} \
  --title "feat(s{N}.{M}): {story-name}" \
  --description "## Completed
- [summary of deliverables]

Co-Authored-By: Rai <rai@humansys.ai>" \
  --no-editor
```

Present the MR URL to the developer for review.

| Condition | Action |
|-----------|--------|
| MR created | Continue to Step 4 |
| `glab` not available | Provide the GitLab URL from `git push` output for manual MR creation |
| Push rejected (branch behind) | `git pull --rebase origin {dev_branch}` on story branch, resolve conflicts, push again |

<verification>
MR created in GitLab targeting `{dev_branch}`. MR URL presented to developer.
</verification>

<if-blocked>
Push fails → check remote permissions or network. Never fall back to local merge.
</if-blocked>

### Step 4: Update Epic Scope

Mark story complete in `work/epics/e{N}-{name}/scope.md`:
- Check the story checkbox: `- [x] S{N}.{M} {name} ✓`
- Update progress tracking table (status, actual time, velocity)

<verification>
Epic scope reflects story completion.
</verification>

### Step 5: Local Cleanup

Delete the local story branch. The remote branch will be deleted by GitLab when the MR is merged (configure "Delete source branch" in MR settings).

```bash
git branch -D story/s{N}.{M}/{slug}
```

<verification>
Local story branch deleted. Remote branch managed by GitLab MR.
</verification>

### Step 6: Update Context & Emit

1. Update `CLAUDE.local.md` to reflect completion and next story
2. Emit telemetry: `rai signal emit-work story S{N}.{M} --event complete`
3. If the story has a backlog ticket: `rai backlog transition {story_key} done`

| Condition | Action |
|-----------|--------|
| Transition succeeds | Continue |
| Transition fails | Log warning and continue — backlog errors are **non-blocking** for lifecycle |
| No ticket | Skip backlog transition |

<verification>
Local context updated. Telemetry emitted.
</verification>

<if-blocked>
Adapter not configured or transition fails → log and continue. Backlog sync is best-effort; it must never block story close.
</if-blocked>

## Output

| Item | Destination |
|------|-------------|
| Merge request | GitLab MR: `{story_branch}` → `{dev_branch}` |
| Epic update | `work/epics/e{N}-{name}/scope.md` |
| Branch cleanup | Local branch deleted; remote via MR merge |
| Backlog update | via `rai backlog transition` (best-effort) |
| Context update | `CLAUDE.local.md` |

## Quality Checklist

- [ ] Retrospective complete before push (gate)
- [ ] Tests pass before push
- [ ] Story branch pushed to origin — never merge locally to `{dev_branch}`
- [ ] Merge request created in GitLab targeting `{dev_branch}`
- [ ] Local story branch deleted after MR creation
- [ ] Epic scope updated with completion status
- [ ] Working tree clean before push — no orphaned artifacts
- [ ] NEVER merge locally to `{dev_branch}` — always via MR
- [ ] NEVER merge without retrospective — learnings compound
- [ ] NEVER leave stale local branches — clean as you go

## References

- Previous: `/rai-story-review`
- Complement: `/rai-story-start`
- Epic scope: `work/epics/e{N}-{name}/scope.md`
