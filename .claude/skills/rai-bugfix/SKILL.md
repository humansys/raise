---
name: rai-bugfix
description: >
  Guide the developer through a formal 6-phase bug fix lifecycle
  (start → analyse → plan → fix → review → close) with the same
  rigor and traceability as a story. Use for tracked bugs that
  need full accountability from reproduction to close.

license: MIT

metadata:
  raise.work_cycle: utility
  raise.frequency: as-needed
  raise.fase: "0"
  raise.prerequisites: ""
  raise.next: ""
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "1.0.0"
  raise.visibility: internal
---

# Bugfix

## Purpose

Guide the developer through a formal 6-phase bug fix lifecycle — branch, analyse, plan, fix, review, close — producing the same artifacts and traceability as a story.

## Mastery Levels (ShuHaRi)

- **Shu**: Follow all 6 phases strictly; produce every named artifact
- **Ha**: Collapse plan into analyse for XS bugs; skip retro for trivial fixes
- **Ri**: Define domain-specific triage patterns; feed systemic findings to graph

## Context

**When to use:** Tracked bug (Jira issue) needs formal resolution: branch, artifact trail, retrospective.

**When to skip:** Trivial fix (typo, obvious one-liner) — commit directly. For RCA without lifecycle overhead, use `/rai-debug`.

**Inputs:** Bug ID (e.g., RAISE-251), problem statement or reproduction steps.

**Branch config:** Read `branches.development` from `.raise/manifest.yaml` for `{dev_branch}`.

## Steps

### Step 1: Start *(mirrors `rai-story-start`)*

```bash
git checkout {dev_branch}
git checkout -b bug/raise-{N}/{bug-slug}
```

Reproduce the bug — confirm it is observable. Write `bug-{N}-scope.md`:

```
WHAT:      [behavior observed]
WHEN:      [conditions / triggers]
WHERE:     [file:line or component]
EXPECTED:  [correct behavior]
Done when: [specific observable outcome]
```

<verification>
On `bug/raise-{N}/{slug}` branch. Bug reproduces. Scope artifact committed.
</verification>

### Step 2: Analyse *(mirrors `rai-story-design`)*

| Tier | Criteria | Method |
|------|----------|--------|
| XS | Cause evident | Skip to Step 3 |
| S | Single causal chain | 5 Whys |
| M/L | Multiple possible causes | Ishikawa |

Apply method. For deeper RCA, delegate to `/rai-debug`. Write `bug-{N}-analysis.md`: hypothesis confirmed with evidence, fix approach decided.

<verification>
Root cause stated with evidence. Fix approach decided — not implemented yet.
</verification>

### Step 3: Plan *(mirrors `rai-story-plan`)*

Write `bug-{N}-plan.md`: atomic tasks in TDD order (regression test task first), verification command and commit message per task.

<verification>
Regression test task listed first. Each task independently committable.
</verification>

### Step 4: Fix *(mirrors `rai-story-implement`)*

Execute plan tasks in order. Per task: RED (failing regression test) → GREEN (minimal fix) → REFACTOR. Verify and commit before moving on:

```bash
uv run pytest --tb=short
uv run ruff check src/
uv run pyright
```

<verification>
All tasks committed. All gates pass. Bug no longer reproduces.
</verification>

<if-blocked>
3 attempts without fix → document partial state, create follow-up issue.
</if-blocked>

### Step 5: Review *(mirrors `rai-story-review`)*

Verify: fix addresses root cause (not symptom), regression test green, no regressions introduced. Write `bug-{N}-retro.md`.

If bug class could recur:

```bash
rai pattern add "{causal insight}" --context "{keywords}" --type behavioral --from RAISE-{N}
```

<verification>
Retro written. Pattern emitted if applicable. All gates green.
</verification>

### Step 6: Close *(mirrors `rai-story-close`)*

```bash
git checkout {dev_branch}
git merge --no-ff bug/raise-{N}/{slug} -m "fix(RAISE-{N}): {summary}

Root cause: {one line}

Co-Authored-By: Rai <rai@humansys.ai>"
git branch -D bug/raise-{N}/{slug}
```

Update Jira: transition issue to Done.

<verification>
Merged to `{dev_branch}`. Branch deleted. Jira updated.
</verification>

## Output

| Artifact | Step | Purpose |
|----------|------|---------|
| `bug-{N}-scope.md` | 1 | Bug definition + done criteria |
| `bug-{N}-analysis.md` | 2 | Root cause + fix approach |
| `bug-{N}-plan.md` | 3 | Atomic tasks + test plan |
| Code + commits | 4 | Fix + regression tests |
| `bug-{N}-retro.md` | 5 | Learnings + optional pattern |
| Merge commit | 6 | Traceability in `{dev_branch}` |

## Quality Checklist

- [ ] Bug reproduces before any fix (Step 1)
- [ ] Root cause confirmed with evidence (Step 2)
- [ ] Regression test written RED-first (Step 4)
- [ ] All gates pass: pytest, ruff, pyright (Step 4)
- [ ] Fix verified against root cause — not symptom (Step 5)
- [ ] Branch deleted after merge (Step 6)
- [ ] NEVER fix before analysing — symptoms recur without root cause
- [ ] NEVER merge without retro — learnings compound

## References

- Step 1 mirrors: `/rai-story-start`
- Step 2 mirrors: `/rai-story-design` · deep RCA: `/rai-debug`
- Step 3 mirrors: `/rai-story-plan`
- Step 4 mirrors: `/rai-story-implement`
- Step 5 mirrors: `/rai-story-review`
- Step 6 mirrors: `/rai-story-close`
- Branch model: `CLAUDE.md` § Branch Model
