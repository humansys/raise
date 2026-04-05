---
name: rai-bugfix-plan
description: Decompose fix into atomic TDD tasks. Phase 4 of bugfix pipeline.

allowed-tools:
  - Read
  - Write
  - Grep
  - Glob

license: MIT
metadata:
  raise.adaptable: 'true'
  raise.fase: '4'
  raise.frequency: per-bug
  raise.gate: ''
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

### Step 1: Decompose into Tasks

Write `work/bugs/RAISE-{N}/plan.md`: atomic tasks in TDD order.

Each task must have:
- **Description:** What to do
- **Verification:** Command to run (test, lint, type check)
- **Commit message:** Following `fix(RAISE-{N}): {description}` convention

Resolve verification commands from `.raise/manifest.yaml` (`test_command`, `lint_command`, `type_check_command`). If absent, use language defaults:

| Language | Test | Lint | Type Check |
|----------|------|------|------------|
| Python | `uv run pytest --tb=short` | `uv run ruff check` | `uv run pyright` |
| TypeScript | `npx vitest run` | `npx eslint src/` | `npx tsc --noEmit` |

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

<verification>
Regression test task listed first. Each task independently committable.
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

## Output

| Item | Destination |
|------|-------------|
| Plan | `work/bugs/RAISE-{N}/plan.md` |
| Next | `/rai-bugfix-fix` |

## Quality Checklist

- [ ] Regression test is task #1
- [ ] Each task independently committable
- [ ] Verification command specified per task
- [ ] Commit message specified per task
- [ ] NEVER start fixing without a plan

## References

- Previous: `/rai-bugfix-analyse`
- Next: `/rai-bugfix-fix`
