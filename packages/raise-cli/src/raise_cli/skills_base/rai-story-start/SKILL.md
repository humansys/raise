---
name: rai-story-start
description: >
  Initialize a story with verified context, branch, and scope commit.
  Use at the beginning of story work to ensure proper setup and
  traceability from the start.

license: MIT

metadata:
  raise.work_cycle: story
  raise.frequency: per-story
  raise.fase: "3"
  raise.prerequisites: ""
  raise.next: story-design
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "3.0.0"
  raise.visibility: public
  raise.inputs: |
    - story_id: string, required, argument
    - dev_branch: string, required, config
  raise.outputs: |
    - story_branch: string, next_skill
    - story_md: file_path, next_skill
    - scope_md: file_path, next_skill
---

# Story Start

## Purpose

Initialize a story with a dedicated branch from the development branch and a scope commit that documents boundaries and done criteria.

## Mastery Levels (ShuHaRi)

- **Shu**: Follow all steps, verify epic context, create branch with scope commit
- **Ha**: Skip epic verification for standalone stories or experiments
- **Ri**: Custom initialization patterns for specific workflows

## Context

**When to use:** Starting a new story from the backlog or epic scope.

**When to skip:** Quick bug fixes (direct branch). Continuation of already-started story.

**Inputs:** Story ID (S{N}.{M}), epic scope document (if part of an epic), clear understanding of story scope.

**Branch config:** Read `branches.development` from `.raise/manifest.yaml` for `{dev_branch}`. Default: `main`.

## Steps

### Step 1: Verify Epic Context (if applicable)

If this story belongs to an epic, verify the epic directory and scope exist:

```bash
ls work/epics/e{N}-{name}/scope.md
```

| Condition | Action |
|-----------|--------|
| Epic scope exists | Continue — verify story is listed in scope |
| Epic scope missing | Run `/rai-epic-start` first |
| Standalone story | No epic verification needed |

<verification>
Epic context verified (or documented as standalone).
</verification>

### Step 2: Create Story Branch from Dev

Always branch from `{dev_branch}`:

```bash
git checkout {dev_branch} && git pull origin {dev_branch}
git checkout -b story/s{N}.{M}/{story-slug}
```

| Condition | Action |
|-----------|--------|
| M/L story | Create dedicated `story/` branch |
| S/XS story | Create branch anyway — all stories branch from `{dev_branch}` |
| Standalone | Same — `story/s{N}.{M}/{slug}` from `{dev_branch}` |

<verification>
On story branch created from `{dev_branch}`.
</verification>

### Step 3: Define Scope & Commit

Create TWO artifacts:

1. `work/epics/e{N}-{name}/stories/s{N}.{M}-story.md` using `templates/story.md` — user story (Connextra), Gherkin AC, SbE examples. For XS stories, informal AC is acceptable.
2. `work/epics/e{N}-{name}/stories/s{N}.{M}-scope.md` — in scope/out of scope, done criteria (observable outcomes).

Commit:

```bash
git add -A
git commit -m "feat(s{N}.{M}): initialize story scope

In scope:
- {item 1}
- {item 2}

Done when:
- {criteria 1}
- {criteria 2}

Co-Authored-By: Rai <rai@humansys.ai>"
```

<verification>
Scope commit on story branch with boundaries documented.
</verification>

### Step 3b: Update Backlog Status

If the story has a backlog ticket (Jira key or local key):

```bash
rai backlog transition {story_key} in_progress
rai signal emit-work story S{N}.{M} --event start
```

| Condition | Action |
|-----------|--------|
| Story has ticket | Transition to `in_progress` |
| No ticket found | Skip backlog transition (not all stories are tracked externally) |
| Transition fails | Log warning and continue — backlog errors are **non-blocking** for lifecycle |

<if-blocked>
Adapter not configured or transition fails → log and continue. Backlog sync is best-effort; it must never block story work.
</if-blocked>

### Step 4: Present Next Steps

Show the developer:
- Branch name and commit hash
- Quick scope summary
- **Next:** `/rai-story-design` — design is not optional (PAT-186)

## Output

| Item | Destination |
|------|-------------|
| Story branch | `story/s{N}.{M}/{slug}` from `{dev_branch}` |
| User Story | `stories/s{N}.{M}-story.md` (Connextra + Gherkin AC) |
| Scope commit | On story branch |
| Backlog update | via `rai backlog transition` (best-effort) |
| Next | `/rai-story-design` |

## Quality Checklist

- [ ] Story branch created from `{dev_branch}` (never from an epic branch)
- [ ] User Story created from `templates/story.md` (Connextra + Gherkin AC)
- [ ] Scope commit documents in/out boundaries and done criteria
- [ ] Story listed in epic scope document (if part of an epic)
- [ ] NEVER create story branch from anything other than `{dev_branch}`

## References

- Next: `/rai-story-design` (always — PAT-186)
- Complement: `/rai-story-close`
- Epic scope: `work/epics/e{N}-{name}/scope.md`
- Branch model: `CLAUDE.md` § Branch Model
