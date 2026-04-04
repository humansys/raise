---
name: rai-bugfix-fix
description: Execute fix tasks with TDD and all validation gates. Phase 5 of bugfix pipeline.

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
  raise.fase: '5'
  raise.frequency: per-bug
  raise.gate: ''
  raise.next: bugfix-review
  raise.prerequisites: bugfix-plan
  raise.skillset: raise-maintainability
  raise.version: 2.4.0
  raise.visibility: internal
  raise.work_cycle: bugfix
  raise.inputs: |
    - bug_id: string, required, argument
    - plan_md: file_path, required, from_previous
  raise.outputs: |
    - code_commits: string, next_skill
---

# Bugfix Fix

## Purpose

Execute the planned fix tasks in strict TDD order: RED (failing regression test) → GREEN (minimal fix) → REFACTOR. Each task verified and committed independently.

## Mastery Levels (ShuHaRi)

- **Shu**: Follow plan tasks exactly, RED-GREEN-REFACTOR, run all 4 gates
- **Ha**: Combine related tasks when gates are stable
- **Ri**: Adaptive TDD (property tests, mutation testing)

## Context

**When to use:** After `/rai-bugfix-plan` has decomposed the fix into atomic tasks.

**When to skip:** Never — even if the fix seems trivial, follow the plan.

**Inputs:** Bug ID, `work/bugs/RAISE-{N}/plan.md` with atomic tasks.

**Expected state:** On bug branch. Plan artifact exists. All current gates pass.

## Steps

### Step 1: Resolve Verification Commands

Resolve verification commands using this priority chain:

1. **Check `.raise/manifest.yaml`** for `project.test_command`, `project.lint_command`, `project.type_check_command` — if set, use directly
2. **Detect language** from `project.project_type` in manifest, or scan file extensions
3. **Map language to default** (see `/rai-story-implement` Step 3 for the full table)

The manifest always wins when present.

### Step 2: Execute Tasks in Order

Per task from `plan.md`:

1. **Implement** the task
2. **Run ALL four gates** after each task:
   - Test: `{test_command}`
   - Lint: `{lint_command}`
   - Type check: `{type_check_command}`
   - Format: `{format_command}` (if configured)
3. **Commit** with the message from the plan

```bash
git add -A
git commit -m "{commit_message}

Co-Authored-By: Rai <rai@humansys.ai>"
```

<verification>
All tasks committed. All four gates pass. Bug no longer reproduces.
</verification>

<if-blocked>
3 attempts without fix → document partial state, create follow-up issue.
</if-blocked>

## Output

| Item | Destination |
|------|-------------|
| Code + commits | On bug branch |
| Next | `/rai-bugfix-review` |

## Quality Checklist

- [ ] RED test written first (proves bug exists)
- [ ] GREEN fix is minimal (addresses root cause, not symptoms)
- [ ] All four gates pass after each task (test, lint, type check, format)
- [ ] Each task committed independently
- [ ] Bug no longer reproduces after fix
- [ ] NEVER skip the regression test — it's the proof
- [ ] NEVER fix symptoms — address the root cause from analysis

## References

- Previous: `/rai-bugfix-plan`
- Next: `/rai-bugfix-review`
- Verification: `/rai-story-implement` Step 3 (language → command table)
