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
  raise.aspects: introspection
  raise.introspection:
    phase: bugfix.analyse
    context_source: scope doc with triage
    affected_modules: []
    max_tier1_queries: 3
    max_jit_queries: 3
    tier1_queries:
      - "root cause patterns in {affected_modules}"
      - "prior analyses for {bug_type} bugs"
      - "failure modes for {origin} defects"
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

### PRIME (mandatory — do not skip)

Before starting Step 1, you MUST execute the PRIME protocol:

1. **Chain read**: Read bugfix-triage's learning record at `.raise/rai/learnings/rai-bugfix-triage/{work_id}/record.yaml`.
2. **Graph query**: Execute tier1 queries from this skill's metadata using `rai graph query`. If graph is unavailable, note in LEARN record and continue.
3. **Present**: Surface retrieved patterns as context. 0 results is valid — not a failure.

### Step 1: Select Analysis Method

> **JIT**: Before selecting method, query graph for root cause patterns in affected modules
> → `aspects/introspection.md § JIT Protocol`

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

> **JIT**: Before writing analysis, query graph for prior analyses of similar bug types
> → `aspects/introspection.md § JIT Protocol`

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

### LEARN (mandatory — do not skip)

After completing the final step, you MUST produce a learning record. Write to `.raise/rai/learnings/rai-bugfix-analyse/{work_id}/record.yaml`:

```yaml
skill: rai-bugfix-analyse
work_id: {work_id}
version: "2.4.0"
timestamp: {ISO 8601 UTC}
primed_patterns: [{list of pattern IDs from PRIME}]
tier1_queries: {count}
tier1_results: {count}
jit_queries: {count}
pattern_votes:
  {PATTERN_ID}: {vote: 1|0|-1, why: "reason"}
gaps:
  - "description of missing knowledge"
artifacts: [{list of files produced}]
commit: {current commit hash or null}
branch: {current branch}
downstream: {}
```

**Rules:** Every cognitive skill execution MUST produce this record. Missing records break the learning chain. Enrich bugfix-triage's record with `downstream: {classification_accurate: bool}`.

## Quality Checklist

- [ ] Root cause confirmed with evidence (not guessed)
- [ ] Fix approach decided but not implemented
- [ ] Analysis artifact committed
- [ ] "Human error" never accepted as root cause
- [ ] NEVER fix before analysing — symptoms recur without root cause
- [ ] LEARN record written to `.raise/rai/learnings/rai-bugfix-analyse/{work_id}/record.yaml`

## References

- Previous: `/rai-bugfix-triage`
- Next: `/rai-bugfix-plan`
