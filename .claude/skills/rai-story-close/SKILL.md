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
  raise.version: "2.0.0"
  raise.visibility: public
---

# Story Close

## Purpose

Complete a story by verifying the retrospective, merging to the parent branch, cleaning up branches, and updating epic tracking.

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

### Step 2: Merge to Parent Branch

Determine parent: `story/s{N}.{M}/...` → `epic/e{N}/...` (or `{dev_branch}` for standalone).

```bash
git checkout {parent_branch}
git pull origin {parent_branch}
git merge --no-ff {story_branch} -m "feat(s{N}.{M}): merge {story-name}

Completed:
- [summary of deliverables]

Co-Authored-By: Rai <rai@humansys.ai>"
```

<verification>
Merge commit created on parent branch.
</verification>

<if-blocked>
Merge conflicts → resolve preserving story work.
</if-blocked>

### Step 3: Update Epic Scope

Mark story complete in `work/epics/e{N}-{name}/scope.md`:
- Check the story checkbox: `- [x] S{N}.{M} {name} ✓`
- Update progress tracking table (status, actual time, velocity)

<verification>
Epic scope reflects story completion.
</verification>

### Step 4: Delete Story Branch

```bash
git branch -D story/s{N}.{M}/{slug}
git push origin --delete story/s{N}.{M}/{slug} 2>/dev/null || true
```

<verification>
Story branch deleted (local and remote).
</verification>

### Step 5: Update Context & Emit

1. Update `CLAUDE.local.md` to reflect completion and next story
2. Emit telemetry: `rai signal emit-work story S{N}.{M} --event complete`

<verification>
Local context updated. Telemetry emitted.
</verification>

## Output

| Item | Destination |
|------|-------------|
| Merge commit | Parent branch with `--no-ff` |
| Epic update | `work/epics/e{N}-{name}/scope.md` |
| Branch cleanup | Story branch deleted |
| Context update | `CLAUDE.local.md` |

## Quality Checklist

- [ ] Retrospective complete before merge (gate)
- [ ] Tests pass before merge
- [ ] Merge uses `--no-ff` to preserve story history
- [ ] Story branch deleted after merge
- [ ] Epic scope updated with completion status
- [ ] NEVER merge without retrospective — learnings compound
- [ ] NEVER leave stale branches — clean as you go

## References

- Previous: `/rai-story-review`
- Complement: `/rai-story-start`
- Epic scope: `work/epics/e{N}-{name}/scope.md`
