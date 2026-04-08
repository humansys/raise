---
name: rai-bugfix-analyse
description: Root cause analysis using the method best suited to the bug. Phase 3 of bugfix pipeline.

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
  raise.visibility: public
  raise.work_cycle: bugfix
  raise.inputs: |
    - bug_id: string, required, argument
    - scope_md: file_path, required, from_previous
  raise.outputs: |
    - analysis_md: file_path, next_skill
---

# Bugfix Analyse

## Purpose

Determine the root cause of the bug and decide a fix approach. Select the analysis method based on what information is available — not on an arbitrary complexity tier.

## Mastery Levels (ShuHaRi)

- **Shu**: Follow the selected method strictly, document every hypothesis
- **Ha**: Combine methods when signals overlap
- **Ri**: Domain-specific RCA methods (fault trees, SBFL)

## Context

**When to use:** After `/rai-bugfix-triage` has classified the bug in 4 dimensions.

**When to skip:** XS bugs where cause is self-evident — but still write `analysis.md` documenting the obvious cause.

**Inputs:** Bug ID, `work/bugs/RAISE-{N}/scope.md` with TRIAGE block.

**Expected state:** On bug branch. Scope with triage exists. Bug reproduces.

## Steps

### Step 1: Select Method Based on Available Signals

Read the scope artifact and determine which signals you have:

| Signal available | Best method |
|-----------------|-------------|
| Stack trace or error message with location | **Stack trace analysis** — follow the error path to origin |
| Bug appeared after a known change | **git bisect** — binary search commits to find the introducing change |
| Single suspected cause | **5 Whys** — trace one causal chain, each answer evidenced |
| Multiple possible causes, unclear which | **Hypothesis-driven** — list hypotheses, test each, eliminate |
| Cause is evident from reproduction | **Document directly** — write the cause and move on |

Choose the method that matches your signals. If uncertain, default to **hypothesis-driven** — it's the most general and what LLMs do naturally.

### Step 2: Analyse

Execute the selected method:

**Stack trace analysis:** Follow the error from the surface (exception/log) back through the call chain to the originating defect. Document the path.

**git bisect:** `git bisect start`, `git bisect bad HEAD`, `git bisect good {known-good-commit}`. Test at each step until the introducing commit is found.

**5 Whys:** Trace one factual causal chain — ask "Why?" up to five times, each answer evidenced by code. Stop at the actionable root cause.

**Hypothesis-driven:** List 2-5 hypotheses for the root cause. For each one, define a test (grep, read code, run command), execute it, and record the result:

| Hypothesis | Test | Result | Conclusion |
|------------|------|--------|------------|
| {what might cause it} | {how to verify} | {what you found} | confirmed / eliminated |

Narrow to one confirmed root cause. If two remain, escalate to human at GATE 2.

**Rule for all methods:** "Human error" is never a root cause — ask why the error was possible.

<verification>
Root cause stated with evidence. Fix approach decided — not implemented yet.
</verification>

<if-blocked>
Root cause unclear after analysis → document top 2 hypotheses, escalate to human at GATE 2.
</if-blocked>

### Step 3: Write Analysis Artifact

Write `work/bugs/RAISE-{N}/analysis.md` with: method used, root cause, evidence, and fix approach.

```bash
git add work/bugs/RAISE-{N}/analysis.md
git commit -m "bug(RAISE-{N}): analyse — root cause identified

Method: {method used}
Root cause: {one line}
Fix approach: {one line}

Co-Authored-By: Rai <rai@humansys.ai>"
```

<verification>
Analysis artifact committed with method, root cause, and fix approach.
</verification>

## Output

| Item | Destination |
|------|-------------|
| Analysis | `work/bugs/RAISE-{N}/analysis.md` |
| Next | `/rai-bugfix-plan` |

## Quality Checklist

- [ ] Method selected based on available signals (not arbitrary tier)
- [ ] Root cause confirmed with evidence (not guessed)
- [ ] Fix approach decided but not implemented
- [ ] Analysis artifact committed
- [ ] "Human error" never accepted as root cause
- [ ] NEVER fix before analysing — symptoms recur without root cause

## References

- Previous: `/rai-bugfix-triage`
- Next: `/rai-bugfix-plan`
