---
name: rai-epic-start
description: >
  Initialize an epic with scope artifacts and tracker entry.
  Epics are logical containers — no epic branch is created.
  Story branches are created directly from the development branch.

license: MIT

metadata:
  raise.work_cycle: epic
  raise.frequency: per-epic
  raise.fase: "2"
  raise.prerequisites: ""
  raise.next: epic-design
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "3.0.0"
  raise.visibility: public
  raise.inputs: |
    - epic_id: string, required, argument
    - epic_slug: string, required, argument
    - dev_branch: string, required, config
  raise.outputs: |
    - brief: file_path, next_skill
    - scope: file_path, next_skill
---

# Epic Start

## Purpose

Initialize an epic with scope artifacts and a tracker entry. Epics are logical containers (directory + tracker), not branches. Story branches are created directly from the development branch.

## Mastery Levels (ShuHaRi)

- **Shu**: Follow all steps, verify each before proceeding
- **Ha**: Streamline scope for well-understood epics
- **Ri**: Integrate with release workflows and automated setup

## Context

**When to use:** Starting a new body of work (3-10 stories), beginning a planned epic from the backlog.

**When to skip:** Small fixes or single stories (no epic needed). Continuation of existing epic.

**Inputs:** Epic number (E{N}), epic name/slug, high-level objective.

**Branch config:** Read `branches.development` from `.raise/manifest.yaml` for `{dev_branch}`. Default: `main`.

## Steps

### Step 1: Verify Development Branch

Ensure on `{dev_branch}` (for creating scope artifacts):

```bash
git branch --show-current
```

| Condition | Action |
|-----------|--------|
| On `{dev_branch}` | Continue |
| On other branch | `git checkout {dev_branch} && git pull` |

<verification>
On `{dev_branch}`, up to date with remote.
</verification>

### Step 2: Define Scope & Commit

Create TWO artifacts:

1. `work/epics/e{N}-{name}/brief.md` using `templates/brief.md` — hypothesis, success metrics, appetite, rabbit holes.
2. `work/epics/e{N}-{name}/scope.md` — objective, in/out scope, planned stories, done criteria.

Commit:

```bash
git add -A
git commit -m "epic(e{N}): initialize {epic-name}

Objective: {1-line}

In scope:
- {item 1}
- {item 2}

Co-Authored-By: Rai <rai@humansys.ai>"
```

Register epic in the backlog tracker via CLI:

- **If Jira issue exists:** `rai backlog transition {JIRA_KEY} "In Progress" -a jira`
- **If new epic (no Jira key):** `rai backlog create "{title}" -p RAISE -t Epic -l epic`

Emit telemetry:

```bash
rai signal emit-work epic E{N} --event start
```

<verification>
Scope commit on `{dev_branch}`. Epic visible in backlog.
</verification>

<if-blocked>
CLI adapter not configured → log warning and continue. Backlog sync is best-effort.
</if-blocked>

### Step 3: Present Next Steps

Show the developer:
- Commit hash and epic directory path
- Quick scope summary (objective + story count)
- **Next:** `/rai-epic-design` to formalize scope and stories

## Output

| Item | Destination |
|------|-------------|
| Epic Brief | `work/epics/e{N}-{name}/brief.md` |
| Scope | `work/epics/e{N}-{name}/scope.md` |
| Scope commit | On `{dev_branch}` |
| Backlog entry | Tracker via `rai backlog` CLI |
| Next | `/rai-epic-design` |

## Quality Checklist

- [ ] Epic Brief created from `templates/brief.md`
- [ ] Scope commit includes objective and boundaries
- [ ] Epic registered in tracker via `rai backlog` CLI
- [ ] No epic branch created — epics are logical containers only
- [ ] NEVER create epic branches — story branches go directly from `{dev_branch}`

## References

- Next: `/rai-epic-design`
- Stories: `/rai-story-start` (branches from `{dev_branch}`)
- Close: `/rai-epic-close`
- Branch model: `CLAUDE.md` § Branch Model
