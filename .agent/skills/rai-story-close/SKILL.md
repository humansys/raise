---
name: rai-story-close
description: >
  Complete a story with retrospective verification, merge to dev,
  cleanup, and tracking update. Use after review to formally close
  the story lifecycle.

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

Complete a story by verifying the retrospective, merging to the development branch, cleaning up the story branch, and updating epic tracking.

## Mastery Levels (ShuHaRi)

- **Shu**: Follow all steps, verify retrospective, merge with --no-ff, update epic
- **Ha**: Adjust merge strategy for small fixes, skip epic update for standalone
- **Ri**: Integrate with CI/CD pipelines, automate cleanup workflows

## Context

**When to use:** After `/rai-story-review` retrospective is complete. Story is verified and tests pass.

**When to skip:** Story abandoned (document why, delete branch without merge, update epic as "Abandoned").

**Inputs:** Completed retrospective, passing test suite, story branch ready for merge.

**Branch config:** Read `branches.development` from `.raise/manifest.yaml` for `{dev_branch}`. Default: `main`.

## Steps

### Step 1: Verify Retrospective & Tests

```bash
RETRO="work/epics/e{N}-{name}/stories/{story_id}-retrospective.md"
[ -f "$RETRO" ] && echo "✓ Retrospective" || echo "ERROR: Run /rai-story-review first"

uv run pytest --tb=short
```

| Condition | Action |
|-----------|--------|
| Retro exists + tests green | Continue |
| Retro missing | Run `/rai-story-review` first — no exceptions |
| Tests failing | Fix before merge |

Check for structural drift: if this story added modules or changed directory structure, update module docs in `governance/architecture/modules/` before closing.

<verification>
Retrospective exists. Tests pass. No undocumented structural changes.
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

### Step 3: Merge to Development Branch

Always merge to `{dev_branch}`:

```bash
git checkout {dev_branch}
git pull origin {dev_branch}
git merge --no-ff {story_branch} -m "feat(s{N}.{M}): merge {story-name}

Completed:
- [summary of deliverables]

Co-Authored-By: Rai <rai@humansys.ai>"
```

<verification>
Merge commit created on `{dev_branch}`.
</verification>

<if-blocked>
Merge conflicts → resolve preserving story work.
</if-blocked>

### Step 4: Update Epic Scope

Mark story complete in `work/epics/e{N}-{name}/scope.md`:
- Check the story checkbox: `- [x] S{N}.{M} {name} ✓`
- Update progress tracking table (status, actual time, velocity)

<verification>
Epic scope reflects story completion.
</verification>

### Step 5: Delete Story Branch

```bash
git branch -D story/s{N}.{M}/{slug}
git push origin --delete story/s{N}.{M}/{slug} 2>/dev/null || true
```

<verification>
Story branch deleted (local and remote).
</verification>

### Step 6: Update Context & Emit

1. Emit telemetry: `rai signal emit-work story S{N}.{M} --event complete`
3. If the story has a backlog ticket: `rai backlog transition {story_key} done`

| Condition | Action |
|-----------|--------|
| Transition succeeds | Continue |
| Transition fails | Log warning and continue — backlog errors are **non-blocking** for lifecycle |
| No ticket | Skip backlog transition |

<verification>
Telemetry emitted.
</verification>

<if-blocked>
Adapter not configured or transition fails → log and continue. Backlog sync is best-effort; it must never block story close.
</if-blocked>

## Output

| Item | Destination |
|------|-------------|
| Merge commit | `{dev_branch}` with `--no-ff` |
| Epic update | `work/epics/e{N}-{name}/scope.md` |
| Branch cleanup | Story branch deleted |
| Backlog update | via `rai backlog transition` (best-effort) |

## Quality Checklist

- [ ] Retrospective complete before merge (gate)
- [ ] Tests pass before merge
- [ ] Merge uses `--no-ff` to preserve story history
- [ ] Story branch deleted after merge
- [ ] Epic scope updated with completion status
- [ ] Working tree clean before merge — no orphaned artifacts
- [ ] Always merge to `{dev_branch}` — never to an epic branch
- [ ] NEVER merge without retrospective — learnings compound
- [ ] NEVER leave stale branches — clean as you go

## References

- Previous: `/rai-story-review`
- Complement: `/rai-story-start`
- Epic scope: `work/epics/e{N}-{name}/scope.md`
