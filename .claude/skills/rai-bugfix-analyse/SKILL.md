---
name: rai-bugfix-analyse
description: Root cause analysis using 5 Whys or Ishikawa. Phase 3 of bugfix pipeline.

allowed-tools:
  - Read
  - Edit
  - Write
  - Grep
  - Glob
  - Bash

license: MIT
metadata:
  raise.adaptable: 'true'
  raise.fase: '3'
  raise.frequency: per-bug
  raise.gate: ''
  raise.next: bugfix-plan
  raise.prerequisites: bugfix-triage
  raise.skillset: raise-maintainability
  raise.version: 2.4.0
  raise.visibility: internal
  raise.work_cycle: bugfix
  raise.inputs: |
    - bug_id: string, required, argument
    - scope_md: file_path, required, from_previous
  raise.outputs: |
    - analysis_md: file_path, next_skill
---

# Bugfix Analyse

## Purpose

Determine the root cause of the bug using structured analysis methods. The output is a confirmed root cause and a decided fix approach — not the fix itself.

## Mastery Levels (ShuHaRi)

- **Shu**: Follow analysis method strictly, document every hypothesis
- **Ha**: Select method based on bug complexity; skip Ishikawa for single-chain causes
- **Ri**: Domain-specific RCA methods (fault trees, failure mode analysis)

## Context

**When to use:** After `/rai-bugfix-triage` has classified the bug in 4 dimensions.

**When to skip:** XS bugs where cause is self-evident — but still write `analysis.md` documenting the obvious cause.

**Inputs:** Bug ID, `work/bugs/RAISE-{N}/scope.md` with TRIAGE block.

**Expected state:** On bug branch. Scope with triage exists. Bug reproduces.

## Steps

### Step 1: Select Analysis Method

| Tier | Criteria | Method |
|------|----------|--------|
| XS | Cause evident | Document directly |
| S | Single causal chain | 5 Whys |
| M/L | Multiple possible causes | Ishikawa |

### Step 2: Analyse

**5 Whys (S):** Trace one factual causal chain — ask "Why?" five times, each answer evidenced. Stop at actionable root cause. Record: `Problem → Why1 → Why2 → Why3 → Why4 → Root cause → Countermeasure`.

**Ishikawa (M/L):** Explore 6 M's: Method, Machine, Material, Measurement, Manpower, Milieu. State each hypothesis, test it, confirm or eliminate:

| Hypothesis | Test | Result | Conclusion |
|------------|------|--------|------------|

Rule for both: "Human error" is never a root cause — ask why the error was possible.

<verification>
Root cause stated with evidence. Fix approach decided — not implemented yet.
</verification>

<if-blocked>
Root cause unclear after analysis → document top 2 hypotheses, escalate to human for judgment.
</if-blocked>

### Step 3: Write Analysis Artifact

Write `work/bugs/RAISE-{N}/analysis.md`: confirmed root cause + fix approach.

```bash
git add work/bugs/RAISE-{N}/analysis.md
git commit -m "bug(RAISE-{N}): analyse — root cause identified

Root cause: {one line}
Fix approach: {one line}

Co-Authored-By: Rai <rai@humansys.ai>"
```

<verification>
Analysis artifact committed with root cause and fix approach.
</verification>

## Output

| Item | Destination |
|------|-------------|
| Analysis | `work/bugs/RAISE-{N}/analysis.md` |
| Next | `/rai-bugfix-plan` |

## Quality Checklist

- [ ] Root cause confirmed with evidence (not guessed)
- [ ] Fix approach decided but not implemented
- [ ] Analysis artifact committed
- [ ] "Human error" never accepted as root cause
- [ ] NEVER fix before analysing — symptoms recur without root cause

## References

- Previous: `/rai-bugfix-triage`
- Next: `/rai-bugfix-plan`
