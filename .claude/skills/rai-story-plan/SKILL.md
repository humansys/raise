---
name: rai-story-plan
description: Decompose story into atomic tasks with TDD verification. Use after story design.

allowed-tools:
  - Read
  - Grep
  - Glob
  - "Bash(rai:*)"

license: MIT

metadata:
  raise.work_cycle: story
  raise.frequency: per-story
  raise.fase: "5"
  raise.prerequisites: project-backlog
  raise.next: story-implement
  raise.gate: gate-plan
  raise.adaptable: "true"
  raise.version: "2.3.0"
  raise.visibility: public
  raise.inputs: |
    - design_md: file_path, optional, previous_skill
    - story_md: file_path, required, story-start
  raise.outputs: |
    - plan_md: file_path, next_skill
  raise.aspects: introspection
  raise.introspection:
    phase: story.plan
    context_source: design doc
    affected_modules: []
    max_tier1_queries: 3
    max_jit_queries: 2
    tier1_queries:
      - "decomposition patterns for {complexity} stories"
      - "TDD patterns for {affected_modules}"
      - "estimation calibration for {size} stories"
---

# Story Plan

## Purpose

Decompose a story into atomic executable tasks with dependencies, verification criteria, and a deterministic execution order.

## Mastery Levels (ShuHaRi)

- **Shu**: Decompose each story into atomic tasks with full verification criteria
- **Ha**: Adjust granularity based on complexity, parallelize when possible
- **Ri**: Custom planning patterns for specific stacks

## Context

**When to use:** After `/rai-story-design` has grounded integration decisions (or directly for simple stories).

**Prerequisite:** Design document at `work/epics/e{N}-{name}/stories/s{N}.{M}-design.md` (optional for simple stories).

**Inputs:** Story with acceptance criteria, design document (if exists).

## Steps

### PRIME (mandatory — do not skip)

Before starting Step 1, you MUST execute the PRIME protocol:

1. **Chain read**: Read story-design's learning record at `.raise/rai/learnings/rai-story-design/{work_id}/record.yaml`. Enrich story-design's record with `downstream: {plan_derivable: bool, tasks_clear: bool}`.
2. **Graph query**: Execute tier1 queries from this skill's metadata using `rai graph query`. If graph is unavailable, note in LEARN record and continue.
3. **Present**: Surface retrieved patterns as context. 0 results is valid — not a failure.

### Step 1: Verify Design

```bash
ls work/epics/e*/stories/{story_id}-design.md 2>/dev/null || echo "INFO: No design"
```

> **JIT**: Before verifying design completeness, query graph for complexity assessment patterns
> → `aspects/introspection.md § JIT Protocol`

| Condition | Action |
|-----------|--------|
| Design exists | Load and reference |
| No design + simple story | Continue |
| No design + complex story | Run `/rai-story-design` first |

<verification>
Design loaded or simple story confirmed.
</verification>

### Step 2: Decompose into Tasks

Divide story into atomic, individually verifiable tasks. One commit per task.

| Story Size | Tasks | Rationale |
|------------|:-----:|-----------|
| XS (1-2 SP) | 1-2 | Single-pass implementation |
| S (3-5 SP) | 2-3 | Avoid over-decomposition |
| M (5-8 SP) | 3-5 | Balance granularity and overhead |
| L (8+ SP) | 5-8 | Consider splitting the story |

**Per task:**
- Description, files to create/modify
- TDD cycle: RED (failing test) → GREEN (minimal code) → REFACTOR
- AC reference: link to `story.md` Gherkin scenario (if exists)
- Verification commands: use the **project-wide** command from `.raise/manifest.yaml` (`test_command`, `lint_command`, `type_check_command`). **Never use file-specific paths** (e.g. `pyright src/module/file.py`) — the project config already defines the correct scope including `tests/`. If manifest commands are absent, use language defaults (see `/rai-story-implement` Step 3).
- Size (XS/S/M/L) and dependencies

**Always include as final task:** Manual integration test — validate end-to-end with running software.

<verification>
Each task is atomic and verifiable. Final integration test included.
</verification>

### Step 3: Order & Dependencies

> **JIT**: Before ordering dependencies, query graph for risk-first ordering patterns
> → `aspects/introspection.md § JIT Protocol`

- Map dependencies (sequential vs parallel)
- Apply risk-first ordering (riskiest tasks early)
- Maximize parallelism where no mutual dependencies exist
- Verify no circular dependencies

<verification>
Execution order defined. Dependency graph is acyclic.
</verification>

### Step 4: Document Plan

Create `work/epics/e{N}-{name}/stories/s{N}.{M}-plan.md` with:
- Overview (story ID, size, date)
- Ordered task list with descriptions, files, verification, sizes, dependencies
- Execution order with rationale
- Risks and mitigations
- Duration tracking table (filled during implementation)

<verification>
Plan document complete and reviewable in <5 minutes.
</verification>

## Output

| Item | Destination |
|------|-------------|
| Implementation plan | `work/epics/e{N}-{name}/stories/s{N}.{M}-plan.md` |
| Next | `/rai-story-implement` |

### LEARN (mandatory — do not skip)

After completing the final step, you MUST produce a learning record. Write to `.raise/rai/learnings/rai-story-plan/{work_id}/record.yaml`:

```yaml
skill: rai-story-plan
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

**Rules:** Every cognitive skill execution MUST produce this record. Simple stories are not exempt — a record with 0 queries and 0 gaps is valid and expected. Missing records break the learning chain.

## Quality Checklist

- [ ] Design verified or simple story confirmed
- [ ] Tasks are atomic (one commit each) and verifiable
- [ ] TDD cycle specified per task (RED → GREEN → REFACTOR)
- [ ] Final manual integration test task included
- [ ] Dependencies mapped — no cycles
- [ ] Execution order follows risk-first approach
- [ ] NEVER over-decompose simple stories
- [ ] NEVER skip TDD guidance — tests define behavior
- [ ] LEARN record written to `.raise/rai/learnings/rai-story-plan/{work_id}/record.yaml`

## References

- Gate: `gates/gate-plan.md`
- Previous: `/rai-story-design`
- Next: `/rai-story-implement`
