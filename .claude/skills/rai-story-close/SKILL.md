---
name: rai-story-close
description: >
  Complete a story with retrospective verification, local merge to dev,
  and tracking update. MRs are created at epic level, not per story.
  Use after review to formally close the story lifecycle.
disable-model-invocation: true

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

Complete a story by verifying the retrospective, merging locally to the development branch, and updating epic tracking. Remote push and merge requests happen at epic level (see `/rai-epic-close`).

## Mastery Levels (ShuHaRi)

- **Shu**: Follow all steps, verify retrospective, merge locally, update epic
- **Ha**: Skip epic update for standalone stories
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

### Step 3: Merge Locally to Dev

Merge the story branch into `{dev_branch}` locally with `--no-ff` to preserve story history:

```bash
git checkout {dev_branch}
git merge story/s{N}.{M}/{slug} --no-ff -m "Merge branch 'story/s{N}.{M}/{slug}' into {dev_branch}

S{N}.{M}: {story-name} — {1-line summary}

Tracker: {JIRA_KEY} / E{N}"
```

Remote push and merge requests are handled at epic level during `/rai-epic-close`.

| Condition | Action |
|-----------|--------|
| Merge succeeds | Continue to Step 4 |
| Merge conflicts | Resolve on story branch first, then retry merge |

<verification>
Story merged to `{dev_branch}` locally via `--no-ff`.
</verification>

### Step 4: Update Epic Scope

Mark story complete in `work/epics/e{N}-{name}/scope.md`:
- Check the story checkbox: `- [x] S{N}.{M} {name} ✓`
- Update progress tracking table (status, actual time, velocity)

<verification>
Epic scope reflects story completion.
</verification>

### Step 5: Local Cleanup

Delete the local story branch (already merged to `{dev_branch}`):

```bash
git branch -d story/s{N}.{M}/{slug}
```

<verification>
Local story branch deleted.
</verification>

### Step 6: Update Context & Emit

1. Emit telemetry: `rai signal emit-work story S{N}.{M} --event complete`
2. If the story has a backlog ticket: `rai backlog transition {story_key} done`

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
| Local merge | `{story_branch}` merged to `{dev_branch}` via `--no-ff` |
| Epic update | `work/epics/e{N}-{name}/scope.md` |
| Branch cleanup | Local story branch deleted |
| Backlog update | via `rai backlog transition` (best-effort) |
| Remote push + MR | Deferred to `/rai-epic-close` |

## Quality Checklist

- [ ] Retrospective complete before merge (gate)
- [ ] Tests pass before merge
- [ ] Story branch merged locally to `{dev_branch}` via `--no-ff`
- [ ] Local story branch deleted after merge
- [ ] Epic scope updated with completion status
- [ ] Working tree clean before merge — no orphaned artifacts
- [ ] NEVER merge without retrospective — learnings compound
- [ ] NEVER leave stale local branches — clean as you go
- [ ] Remote push and MR happen at epic level (`/rai-epic-close`), not per story

## References

- Previous: `/rai-story-review`
- Complement: `/rai-story-start`
- Epic scope: `work/epics/e{N}-{name}/scope.md`
