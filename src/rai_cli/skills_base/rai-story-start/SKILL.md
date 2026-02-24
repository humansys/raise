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
  raise.version: "2.1.0"
  raise.visibility: public
---

# Story Start

## Purpose

Initialize a story with a verified epic context, dedicated branch, and scope commit that documents boundaries and done criteria.

## Mastery Levels (ShuHaRi)

- **Shu**: Follow all steps, verify epic context, create branch with scope commit
- **Ha**: Skip epic verification for standalone stories or experiments
- **Ri**: Custom initialization patterns for specific workflows

## Context

**When to use:** Starting a new story from the backlog or epic scope.

**When to skip:** Quick bug fixes (direct branch). Continuation of already-started story.

**Inputs:** Story ID (S{N}.{M}), epic scope document, clear understanding of story scope.

**Branch config:** Read `branches.development` from `.raise/manifest.yaml` for `{dev_branch}`. Default: `main`.

## Steps

### Step 1: Verify Epic Branch

For epic stories, verify the epic branch exists:

```bash
git branch --list "epic/e{N}/*" | head -1
```

| Condition | Action |
|-----------|--------|
| Epic branch exists | Continue |
| Epic branch missing | Run `/rai-epic-start` first |
| Standalone story | Branch from `{dev_branch}` directly |

Also verify the story is listed in `work/epics/e{N}-{name}/scope.md`.

<verification>
Epic branch exists. Story listed in scope (or documented as standalone).
</verification>

### Step 2: Create Story Branch

```bash
git checkout -b story/s{N}.{M}/{story-slug}
```

| Condition | Action |
|-----------|--------|
| M/L story | Create dedicated `story/` branch |
| S/XS on epic branch | Stay on epic branch, state skip explicitly |
| Standalone | `story/standalone/{id}` from `{dev_branch}` |

<verification>
On story branch (or epic branch with skip stated).
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

### Step 4: Present Next Steps

Show the developer:
- Branch name and commit hash
- Quick scope summary
- **Next:** `/rai-story-design` — design is not optional (PAT-186)

## Output

| Item | Destination |
|------|-------------|
| Story branch | `story/s{N}.{M}/{slug}` (or epic branch for S/XS) |
| User Story | `stories/s{N}.{M}-story.md` (Connextra + Gherkin AC) |
| Scope commit | On story branch |
| Next | `/rai-story-design` |

## Quality Checklist

- [ ] Epic branch verified before creating story branch
- [ ] User Story created from `templates/story.md` (Connextra + Gherkin AC)
- [ ] Scope commit documents in/out boundaries and done criteria
- [ ] Story listed in epic scope document
- [ ] NEVER create story branch without verifying epic branch exists

## References

- Next: `/rai-story-design` (always — PAT-186)
- Complement: `/rai-story-close`
- Epic scope: `work/epics/e{N}-{name}/scope.md`
- Branch model: `CLAUDE.md` § Branch Model
