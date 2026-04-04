---
name: rai-bugfix-plan
description: Decompose fix into atomic TDD tasks. Phase 4 of bugfix pipeline.

allowed-tools:
  - Read
  - Write
  - Grep
  - Glob
  - "Bash(rai:*)"

license: MIT
metadata:
  raise.adaptable: 'true'
  raise.fase: '4'
  raise.frequency: per-bug
  raise.gate: gate-plan
  raise.next: bugfix-fix
  raise.prerequisites: bugfix-analyse
  raise.skillset: raise-maintainability
  raise.version: 2.4.0
  raise.visibility: internal
  raise.work_cycle: bugfix
  raise.inputs: |
    - bug_id: string, required, argument
    - analysis_md: file_path, required, from_previous
  raise.outputs: |
    - plan_md: file_path, next_skill
  raise.aspects: introspection
  raise.introspection:
    phase: bugfix.plan
    context_source: analysis doc
    affected_modules: []
    max_tier1_queries: 2
    max_jit_queries: 2
    tier1_queries:
      - "TDD patterns for {affected_modules}"
      - "fix decomposition patterns for {bug_type} bugs"
---

# Bugfix Plan

## Purpose

Decompose the fix into atomic, independently committable tasks in TDD order. The regression test task comes first — proving the bug exists before fixing it.

## Mastery Levels (ShuHaRi)

- **Shu**: Follow template, regression test first, explicit verification per task
- **Ha**: Collapse plan for XS bugs (2 tasks: test + fix)
- **Ri**: Adaptive task granularity based on complexity signals

## Context

**When to use:** After `/rai-bugfix-analyse` has confirmed root cause and fix approach.

**When to skip:** Never — even a 1-task fix benefits from explicit planning (regression test + fix = 2 tasks minimum).

**Inputs:** Bug ID, `work/bugs/RAISE-{N}/analysis.md` with root cause and fix approach.

**Expected state:** On bug branch. Analysis artifact exists.

## Steps

### PRIME (mandatory — do not skip)

Before starting Step 1, you MUST execute the PRIME protocol:

1. **Chain read**: Read bugfix-analyse's learning record at `.raise/rai/learnings/rai-bugfix-analyse/{work_id}/record.yaml`.
2. **Graph query**: Execute tier1 queries from this skill's metadata using `rai graph query`. If graph is unavailable, note in LEARN record and continue.
3. **Present**: Surface retrieved patterns as context. 0 results is valid — not a failure.

### Step 1: Decompose into Tasks

> **JIT**: Before decomposing, query graph for TDD patterns in affected modules
> → `aspects/introspection.md § JIT Protocol`

Write `work/bugs/RAISE-{N}/plan.md`: atomic tasks in TDD order.

Each task must have:
- **Description:** What to do
- **Verification:** Command to run (test, lint, type check)
- **Commit message:** Following `fix(RAISE-{N}): {description}` convention

The regression test task MUST be first:

```markdown
## Tasks

### T1: Write regression test (RED)
- Write test that reproduces the bug
- Verify: `{test_command}` — test FAILS (proves bug exists)
- Commit: `test(RAISE-{N}): add regression test for {description}`

### T2: Fix {description} (GREEN)
- {specific change}
- Verify: `{test_command}` — test PASSES
- Commit: `fix(RAISE-{N}): {description}`

### T3: Refactor (if needed)
- {cleanup}
- Verify: all gates pass
- Commit: `refactor(RAISE-{N}): {description}`
```

**Always include as final task:** Manual verification — confirm the bug no longer reproduces in running software.

<verification>
Regression test task listed first. Each task independently committable. Final verification task included.
</verification>

<if-blocked>
Fix approach unclear → return to `/rai-bugfix-analyse` for deeper investigation.
</if-blocked>

### Step 2: Commit Plan

```bash
git add work/bugs/RAISE-{N}/plan.md
git commit -m "bug(RAISE-{N}): plan — {N} tasks, TDD order

Co-Authored-By: Rai <rai@humansys.ai>"
```

<verification>
Plan artifact committed.
</verification>

## Output

| Item | Destination |
|------|-------------|
| Plan | `work/bugs/RAISE-{N}/plan.md` |
| Next | `/rai-bugfix-fix` |

### LEARN (mandatory — do not skip)

After completing the final step, you MUST produce a learning record. Write to `.raise/rai/learnings/rai-bugfix-plan/{work_id}/record.yaml`:

```yaml
skill: rai-bugfix-plan
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

**Rules:** Every cognitive skill execution MUST produce this record. Missing records break the learning chain. Enrich bugfix-analyse's record with `downstream: {root_cause_actionable: bool, tasks_clear: bool}`.

## Quality Checklist

- [ ] Regression test is task #1
- [ ] Each task independently committable
- [ ] Verification command specified per task
- [ ] Commit message specified per task
- [ ] Final manual verification task included
- [ ] NEVER start fixing without a plan
- [ ] LEARN record written to `.raise/rai/learnings/rai-bugfix-plan/{work_id}/record.yaml`

## References

- Gate: `gates/gate-plan.md`
- Previous: `/rai-bugfix-analyse`
- Next: `/rai-bugfix-fix`
