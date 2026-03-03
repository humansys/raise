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
  raise.fase: "9"
  raise.prerequisites: all stories complete
  raise.next: ""
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "2.3.0"
  raise.visibility: public
  raise.inputs: |
    - scope: file_path, required, previous_skill
    - all_retrospectives: boolean, required, git
    - dev_branch: string, required, config
  raise.outputs: |
    - retrospective: file_path, file
    - merge_commit: string, git
---

# Epic Close

## Purpose

Complete an epic by conducting a retrospective, merging to the development branch, and cleaning up all branches.

## Mastery Levels (ShuHaRi)

- **Shu**: Follow all steps, complete full retrospective template
- **Ha**: Adjust retrospective depth based on epic complexity
- **Ri**: Integrate with release workflows, automate metrics extraction

## Context

**When to use:** All stories complete and merged to epic branch. Ready to close the epic lifecycle.

**When to skip:** Epic abandoned (document why, delete branches without merge, update backlog as "Abandoned").

**Inputs:** Epic scope document, all story retrospectives, passing test suite.

**Branch config:** Read `branches.development` from `.raise/manifest.yaml` for `{dev_branch}`. Default: `main`.

## Steps

### Step 1: Verify Stories Complete

Check all stories are done in the epic scope document:

```bash
grep -E "^\s*-\s*\[ \]" "work/epics/e{N}-{name}/scope.md"
```

| Condition | Action |
|-----------|--------|
| All stories checked | Continue |
| Incomplete stories | Complete them first or explicitly descope |

<verification>
All stories marked complete in epic scope.
</verification>

### Step 2: Run Tests & Write Retrospective

```bash
uv run pytest --tb=short
```

Create retrospective at `work/epics/e{N}-{name}/retrospective.md` using `templates/retrospective.md`. Fill from story retrospectives and git history.

<verification>
Tests green. Retrospective created with metrics, patterns, and process insights.
</verification>

<if-blocked>
Tests failing → fix before merge.
</if-blocked>

### Step 3: Verify Clean Working Tree

```bash
git status --short
```

| Condition | Action |
|-----------|--------|
| Working tree clean | Continue to merge |
| Uncommitted epic artifacts (design docs, research, scope edits) | **Commit them** before merge |
| Unrelated changes | Stash or commit separately with `chore:` prefix |

**NEVER merge with uncommitted artifacts.** Design docs, research files, scope edits, and story artifacts that aren't committed will be orphaned on the target branch after the epic branch is deleted.

<verification>
`git status` shows clean working tree (or only unrelated files explicitly acknowledged).
</verification>

### Step 4: Merge & Clean Up Branches

```bash
git checkout {dev_branch} && git pull origin {dev_branch}
git merge --no-ff epic/e{N}/{name} -m "Merge epic/e{N}/{name}: {Epic Name}

Delivered: [key deliverables]
Stories: N stories, X SP, X.Xx velocity

Co-Authored-By: Rai <rai@humansys.ai>"
```

Delete epic and story branches (local and remote):

```bash
git branch -D epic/e{N}/{name}
git push origin --delete epic/e{N}/{name} 2>/dev/null || true
for branch in $(git branch | grep "story.*s{N}"); do
    git branch -D $branch && git push origin --delete $branch 2>/dev/null || true
done
```

<verification>
Merge commit on `{dev_branch}`. No epic/story branches remain.
</verification>

<if-blocked>
Merge conflicts → resolve preserving epic work.
</if-blocked>

### Step 5: Update Backlog & Context

1. Mark epic complete: `rai backlog transition {epic_key} done`
2. Update `CLAUDE.local.md` to reflect completion and next epic
3. Emit telemetry:

```bash
rai signal emit-work epic E{N} --event complete
```

<verification>
Backlog reflects completion. Local context updated.
</verification>

## Output

| Item | Destination |
|------|-------------|
| Retrospective | `work/epics/e{N}-{name}/retrospective.md` |
| Merge commit | `{dev_branch}` with `--no-ff` |
| Branch cleanup | All epic/story branches deleted |
| Backlog update | via `rai backlog transition` |
| Context update | `CLAUDE.local.md` |

## Quality Checklist

- [ ] All stories complete before merge (gate)
- [ ] Tests pass on epic branch before merge
- [ ] Retrospective captures metrics, patterns, and process insights
- [ ] Merge uses `--no-ff` to preserve epic history
- [ ] Working tree clean before merge — no orphaned artifacts
- [ ] All epic and story branches deleted after merge
- [ ] Backlog updated with completion status
- [ ] NEVER merge without retrospective — learnings compound across epics

## References

- Retrospective template: `templates/retrospective.md`
- Previous: All `/rai-story-close` completions
- Backlog: via `rai backlog` CLI
- Next: `/rai-epic-design` for next epic
