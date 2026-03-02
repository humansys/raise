---
description: 'Initialize an epic with branch and scope commit. Creates the epic branch
  from the development branch that story branches will nest under.

  '
license: MIT
metadata:
  raise.adaptable: 'true'
  raise.fase: '2'
  raise.frequency: per-epic
  raise.gate: ''
  raise.next: epic-design
  raise.prerequisites: ''
  raise.version: 2.1.0
  raise.visibility: public
  raise.work_cycle: epic
name: rai-epic-start
---

# Epic Start

## Purpose

Initialize an epic with a dedicated branch from the development branch and a scope commit that documents boundaries.

## Mastery Levels (ShuHaRi)

- **Shu**: Follow all steps, verify each before proceeding
- **Ha**: Streamline scope for well-understood epics
- **Ri**: Integrate with release workflows and automated branch setup

## Context

**When to use:** Starting a new body of work (3-10 stories), beginning a planned epic from the backlog.

**When to skip:** Small fixes or single stories (branch from `{dev_branch}` directly). Continuation of existing epic.

**Inputs:** Epic number (E{N}), epic name/slug, high-level objective.

**Branch config:** Read `branches.development` from `.raise/manifest.yaml` for `{dev_branch}`. Default: `main`.

## Steps

### Step 1: Verify Development Branch

Ensure starting from `{dev_branch}`:

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

### Step 2: Create Epic Branch

```bash
git checkout -b epic/e{N}/{epic-slug}
```

Naming: `epic/e14/rai-distribution`, `epic/e15/telemetry-insights`.

| Condition | Action |
|-----------|--------|
| Branch is new | Continue to Step 3 |
| Branch exists | `git checkout epic/e{N}/{slug}`, verify scope commit exists |

<verification>
On new epic branch.
</verification>

### Step 3: Define Scope & Commit

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

Register epic in `governance/backlog.md` — add or update the row with status `In Progress`.

<verification>
Scope commit on epic branch. Epic visible in backlog.
</verification>

<if-blocked>
Backlog file missing → create it. Row already exists → update status only.
</if-blocked>

### Step 4: Present Next Steps

Show the developer:
- Branch name and commit hash
- Quick scope summary (objective + story count)
- **Next:** `/rai-epic-design` to formalize scope and stories

## Output

| Item | Destination |
|------|-------------|
| Epic branch | `epic/e{N}/{slug}` from `{dev_branch}` |
| Epic Brief | `work/epics/e{N}-{name}/brief.md` |
| Scope commit | On epic branch |
| Backlog entry | `governance/backlog.md` |
| Next | `/rai-epic-design` |

## Quality Checklist

- [ ] Branch created from `{dev_branch}` (not from another epic or story branch)
- [ ] Epic Brief created from `templates/brief.md`
- [ ] Scope commit includes objective and boundaries
- [ ] Epic registered in `governance/backlog.md`
- [ ] NEVER create epic branch from wrong base — causes merge pain

## References

- Next: `/rai-epic-design`
- Stories: `/rai-story-start` (verifies epic branch exists)
- Close: `/rai-epic-close`
- Branch model: `CLAUDE.md` § Branch Model
