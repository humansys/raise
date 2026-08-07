---
name: rai-story-plan
description: Decompose story into atomic tasks with TDD verification. Use after story design.
model: sonnet

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
raise.mastery:
  shu: "Decompose each story into atomic tasks with full verification criteria"
  ha: "Adjust granularity based on complexity, parallelize when possible"
  ri: "Custom planning patterns for specific stacks"
---

# Story Plan

## Purpose

Decompose a story into atomic executable tasks with dependencies, verification criteria, and a deterministic execution order.

## Mastery Levels (ShuHaRi)

See `raise.mastery` in frontmatter.

## Context

**When to use:** After `/rai-story-design` has grounded integration decisions (or directly for simple stories).

**Prerequisite:** Design document at `work/epics/e{N}-{name}/stories/s{N}.{M}-design.md` (optional for simple stories).

**Inputs:** Story with acceptance criteria, design document (if exists).

## Steps

### PRIME (mandatory — do not skip)

Before starting Step 1, you MUST execute the PRIME protocol:

1. **Graph query**: Execute tier1 queries from this skill's metadata using the `raise_graph_query` MCP tool with `cwd="{project_or_worktree_path}"`. If MCP tools are not available, fall back to:
   ```bash
   rai graph query
   ```
   0 results is valid.

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
- Verification: specify the rai gate check commands with explicit `--scope` (see Gate Policy below)
- Size (XS/S/M/L) and dependencies

**Always include as final task:** Manual integration test — validate end-to-end with running software.

**Gate Policy (mandatory in every plan):**

Include this section verbatim in the plan document — it keeps the test execution rules in context during `/rai-story-implement`:

| When | Command | Scope |
|------|---------|-------|
| Per task | `rai gate check gate-tests --scope <test_dir>/` | Only tests for the changed module (e.g. `packages/raise-cli/tests/storage/`) |
| Per task | rai gate check gate-lint | Full project (fast) |
| Per task | rai gate check gate-format | Full project (fast) |
| Per task | rai gate check gate-types | Full project |
| End of story | `rai gate check gate-tests --scope packages/<pkg>/` | Changed package only — NOT full suite |
| MR creation | `/rai-mr-create` | Full suite — the ONLY place where unscoped tests run |

**NEVER run test commands directly** (e.g. `uv run pytest`, `npm test`) — always use rai gate check. Direct invocation floods context with raw output and bypasses gate tracking.

Each task's Verification section MUST use `rai gate check gate-tests --scope <path>` with the concrete test path for that task. Generic or unscoped test commands are not acceptable.

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

Publish `work/epics/e{N}-{name}/stories/s{N}.{M}-plan.md` via CLI:

Use `raise_docs_write` MCP tool with doc_type="story-plan", title="S{N}.{M}: {story-name} plan", content="[plan content: overview, ordered task list, execution order, risks, duration tracking table]", output_path="work/epics/e{N}-{name}/stories/s{N}.{M}-plan.md", cwd="{project_or_worktree_path}".
If MCP tools are not available, fall back to:
```bash
rai docs write story-plan \
  --title "S{N}.{M}: {story-name} plan" \
  --stdin \
  --output-path work/epics/e{N}-{name}/stories/s{N}.{M}-plan.md << 'EOF'
[plan content below]
EOF
```

Content to include:
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
| Signal | WorkLifecycle event emitted (start on entry, complete here) |

Backlog transition to implement status is engine-owned (RAISE-15034):
Engine performs the transition via `apply_phase_transition` at phase completion.
No skill-initiated transition call required or allowed.

**STOP HERE.** Return your summary to the orchestrator. Do NOT invoke any further skill.

## Quality Checklist

- [ ] NEVER over-decompose simple stories
- [ ] NEVER skip TDD guidance — tests define behavior
- [ ] NEVER write `uv run pytest` / `npm test` in verification — always `rai gate check gate-tests --scope`
- [ ] Gate Policy section included in plan document with concrete --scope paths per task

## References

- Gate: `gates/gate-plan.md`
- Previous: `/rai-story-design`
- Next: `/rai-story-implement`
