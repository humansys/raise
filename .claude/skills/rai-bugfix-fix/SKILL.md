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
  raise.gate: gate-code
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
    - code_commits: list, git
  raise.aspects: introspection
  raise.introspection:
    phase: bugfix.fix
    context_source: plan doc
    affected_modules: []
    max_tier1_queries: 3
    max_jit_queries: 3
    tier1_queries:
      - "implementation patterns for {affected_modules}"
      - "testing patterns for {test_type} in {language}"
      - "fix patterns for {bug_type} defects"
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

### PRIME (mandatory — do not skip)

Before starting Step 1, you MUST execute the PRIME protocol:

1. **Chain read**: Read bugfix-plan's learning record at `.raise/rai/learnings/rai-bugfix-plan/{work_id}/record.yaml`.
2. **Graph query**: Execute tier1 queries from this skill's metadata using `rai graph query`. If graph is unavailable, note in LEARN record and continue.
3. **Present**: Surface retrieved patterns as context. 0 results is valid — not a failure.

### Step 1: Resolve Verification Commands

> **JIT**: Before loading context, query graph for implementation patterns in affected modules
> → `aspects/introspection.md § JIT Protocol`

Resolve verification commands using this priority chain:

1. **Check `.raise/manifest.yaml`** for `project.test_command`, `project.lint_command`, `project.type_check_command` — if set, use directly
2. **Detect language** from `project.project_type` in manifest, or scan file extensions
3. **Map language to default:**

| Language | Test | Lint | Format | Type Check |
|----------|------|------|--------|------------|
| Python | `uv run pytest --tb=short` | `uv run ruff check src/ tests/` | `uv run ruff format --check src/ tests/` | `uv run pyright` |
| TypeScript | `npx vitest run` | `npx eslint src/` | `npx prettier --check src/` | `npx tsc --noEmit` |
| JavaScript | `npx vitest run` | `npx eslint src/` | `npx prettier --check src/` | — |
| C# | `dotnet test` | `dotnet format --check` | — | `dotnet build` |
| Go | `go test ./...` | `golangci-lint run` | `gofmt -l .` | `go vet ./...` |
| PHP | `vendor/bin/phpunit` | `php-cs-fixer check` | — | `vendor/bin/phpstan` |
| Dart | `flutter test` | `dart fix --dry-run` | `dart format --set-exit-if-changed .` | `dart analyze` |

The manifest always wins when present. The table is a fallback.

### Step 2: Execute Tasks in Order

Per task from `plan.md`:

1. **RED** — Write a failing test that defines expected behavior
2. **GREEN** — Write minimal code to make the test pass
3. **REFACTOR** — Clean up while keeping tests green

**Run ALL four gates** (test + lint + format + type check) after each task — not just the one mentioned in the plan. The goal is to catch errors locally before they reach CI.

If verification fails: fix and re-verify (max 3 attempts before escalating).

### Step 3: Commit & Checkpoint

1. Stage task files **and** any learning records: `git add .raise/rai/learnings/`
2. Commit the completed task with the message from the plan
3. Update progress in `work/bugs/RAISE-{N}/progress.md` (task status, actual time)
4. Present to the human: what was completed, files changed, verification results
5. Wait for acknowledgment before continuing

### Step 4: Iterate or Finalize

| Condition | Action |
|-----------|--------|
| More tasks remain | Return to Step 2 |
| All tasks complete | Run full gate check, present summary |
| Task blocked | Document blocker, escalate to human |

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
| Progress log | `work/bugs/RAISE-{N}/progress.md` |
| Next | `/rai-bugfix-review` |

### LEARN (mandatory — do not skip)

After completing the final step, you MUST produce a learning record. Write to `.raise/rai/learnings/rai-bugfix-fix/{work_id}/record.yaml`:

```yaml
skill: rai-bugfix-fix
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

**Rules:** Every cognitive skill execution MUST produce this record. Missing records break the learning chain. Enrich bugfix-plan's record with `downstream: {plan_followed: bool, deviations: list[str]}`.

## Quality Checklist

- [ ] RED test written first (proves bug exists)
- [ ] GREEN fix is minimal (addresses root cause, not symptoms)
- [ ] All four gates pass after each task (test, lint, type check, format)
- [ ] Each task committed independently
- [ ] Progress log updated with actuals
- [ ] Human acknowledged each task before proceeding
- [ ] Bug no longer reproduces after fix
- [ ] NEVER skip the regression test — it's the proof
- [ ] NEVER fix symptoms — address the root cause from analysis
- [ ] LEARN record written to `.raise/rai/learnings/rai-bugfix-fix/{work_id}/record.yaml`

## References

- Gate: `gates/gate-code.md`
- Previous: `/rai-bugfix-plan`
- Next: `/rai-bugfix-review`
- Verification: `/rai-story-implement` Step 3 (language → command table)
