---
name: rai-story-implement
description: Execute plan tasks with TDD and validation gates. Use after story plan.

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
  raise.fase: '6'
  raise.frequency: per-story
  raise.gate: gate-code
  raise.inputs: '- plan_md: file_path, required, previous_skill

    '
  raise.next: story-review
  raise.outputs: '- code_commits: list, git

    '
  raise.prerequisites: story-plan
  raise.version: 2.4.0
  raise.visibility: public
  raise.work_cycle: story
  raise.aspects: introspection
  raise.introspection:
    phase: story.implement
    context_source: plan doc
    affected_modules: []
    max_tier1_queries: 3
    max_jit_queries: 3
    tier1_queries:
      - "implementation patterns for {affected_modules}"
      - "testing patterns for {test_type} in {language}"
      - "integration patterns for {upstream_dependencies}"
name: rai-story-implement
---

# Implement: Development Workflow

## Purpose

Execute the implementation plan task by task with TDD, producing verified code that passes all gates.

## Mastery Levels (ShuHaRi)

- **Shu**: Execute tasks strictly in order, verify each before proceeding
- **Ha**: Adjust plan based on discoveries during implementation
- **Ri**: Parallelize independent tasks, create stack-specific patterns

## Context

**When to use:** After `/rai-story-plan` has produced a plan document.

**Prerequisite:** Plan must exist at `work/epics/e{N}-{name}/stories/{story_id}/plan.md`. Run `/rai-story-plan` first if missing.

**Inputs:** Implementation plan, project guardrails (from graph context).

## Steps

### PRIME (mandatory — do not skip)

Before starting Step 1, you MUST execute the PRIME protocol:

1. **Chain read**: Read story-plan's learning record at `.raise/rai/learnings/rai-story-plan/{work_id}/record.yaml`.
2. **Graph query**: Execute tier1 queries from this skill's metadata using `rai graph query`. If graph is unavailable, note and continue.
3. **Present**: Surface retrieved patterns as context. 0 results is valid — not a failure.

### Step 1: Load Plan & Context

> **JIT**: Before loading context, query graph for implementation patterns in affected modules
> → `aspects/introspection.md § JIT Protocol`

Load the implementation plan and query relevant patterns:

```bash
rai graph query "testing coverage type annotations" --types pattern,guardrail --limit 5
```

If a design document exists, restate the design intent in 2-3 sentences and confirm with the human before proceeding. One unvalidated assumption can waste an entire task cycle.

### Step 2: Execute Task

For the next uncompleted task in plan order:

1. **RED** — Write a failing test that defines expected behavior
2. **GREEN** — Write minimal code to make the test pass
3. **REFACTOR** — Clean up while keeping tests green

Follow project rules, guardrails, and established patterns.

### Step 3: Verify Task

Run the verification defined in the plan. Resolve commands using this priority chain:

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

**Run ALL four gates** (test + lint + format + type check) after each task, not just the one mentioned in the plan. The goal is to catch errors locally before they reach CI.

If verification fails: fix and re-verify (max 3 attempts before escalating).

### Step 4: Commit & Checkpoint

1. Stage task files
2. Commit the completed task
3. Update progress log (`work/epics/.../stories/{story_id}/progress.md`)
4. Present to the human: what was completed, files changed, verification results
5. Wait for acknowledgment before continuing

### Step 5: Iterate or Finalize

| Condition | Action |
|-----------|--------|
| More tasks remain | Return to Step 2 |
| All tasks complete | Run full gate check, present summary |
| Task blocked | Document blocker, escalate to human |

## Output

| Item | Destination |
|------|-------------|
| Implemented code | Per project architecture |
| Progress log | `work/epics/.../stories/{story_id}/progress.md` |
| Next | `/rai-story-review` |

## Quality Checklist

- [ ] Plan loaded and design intent confirmed (if design exists)
- [ ] TDD cycle followed for each task (RED → GREEN → REFACTOR)
- [ ] Each task committed individually (not batched at story end)
- [ ] All four gates pass per task: tests, lint, format, type check
- [ ] NEVER commit without running all four gates — CI will catch what you skip
- [ ] Progress log updated with actuals
- [ ] Human acknowledged each task before proceeding
- [ ] NEVER skip a failing test — fix it or escalate
- [ ] NEVER accumulate errors — stop on defect (Jidoka)

## References

- Gate: `gates/gate-code.md`
- Next skill: `/rai-story-review`
- Progress template: `references/progress-template.md`
