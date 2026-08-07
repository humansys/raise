---
name: rai-story-implement
description: Execute plan tasks with TDD and validation gates. Use after story plan.
model: sonnet

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
  raise.prerequisites: story-design|story-plan
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
raise.mastery:
  shu: "Execute tasks strictly in order, verify each before proceeding"
  ha: "Adjust plan based on discoveries during implementation"
  ri: "Parallelize independent tasks, create stack-specific patterns"
---

# Implement: Development Workflow

## Purpose

Execute the implementation plan task by task with TDD, producing verified code that passes all gates.

## Mastery Levels (ShuHaRi)

See `raise.mastery` in frontmatter.

## Context

**When to use:** After `/rai-story-design` (lean pipeline) or `/rai-story-plan` (full pipeline) has produced an anchor document.

**Prerequisite:** Design or plan must exist — check for `work/epics/**/stories/*-design.md` (lean pipeline anchor) or `work/epics/e{N}-{name}/stories/{story_id}/plan.md` (full pipeline). In the lean pipeline, design.md serves as the implementation anchor. Run `/rai-story-plan` only if neither exists in a full pipeline.

**Inputs:** Implementation plan, project guardrails (from graph context).

## Steps

### PRIME (mandatory — do not skip)

Before starting Step 1, you MUST execute the PRIME protocol:

1. **Graph query**: Execute tier1 queries from this skill's metadata using the `raise_graph_query` MCP tool with `cwd="{project_or_worktree_path}"`. If MCP tools are not available, fall back to:
   ```bash
   rai graph query
   ```
   0 results is valid.
2. **Code orientation**: Load SA-ranked code symbols for the current branch using the `raise_session_context` MCP tool with sections="code_context", `cwd="{project_or_worktree_path}"`.
   If MCP tools are not available, fall back to:
   ```bash
   rai session context -s code_context -p .
   ```
   Returns ~20 symbols ranked by structural proximity to active work modules. Empty result is valid — branch name may not match any module. Use these symbols as starting points for code exploration, not as exhaustive scope.

### Step 1: Load Plan & Context

> **JIT**: Before loading context, query graph for implementation patterns in affected modules
> → `aspects/introspection.md § JIT Protocol`

Load the implementation plan and query relevant patterns using the `raise_graph_query` MCP tool with `cwd="{project_or_worktree_path}"`, query "testing coverage type annotations" (limit 5).

If MCP tools are not available, fall back to:
```bash
rai graph query "testing coverage type annotations" --types pattern,guardrail --limit 5
```

If a design document exists, restate the design intent in 2-3 sentences and confirm with the human before proceeding. One unvalidated assumption can waste an entire task cycle.

> **JIT**: For deeper code exploration beyond the orientation map, use the `raise_graph_query` MCP tool with `cwd="{project_or_worktree_path}"` or fall back to CLI:
> ```bash
> rai graph query "symbol_name" --types symbol --limit 10
> rai graph query "module_name" --module mod-raise-cli--session
> rai graph query "callers of function_name" --types symbol
> ```
> Use `--file path/to/file.py` to scope results to a specific file.

### Step 2: Execute Task

**Environment setup (mandatory — eliminates RC2 path errors, RAISE-15430 AC1):**
```bash
WORKTREE_ROOT=$(git rev-parse --show-toplevel)
```
Use absolute paths for all file operations: `$WORKTREE_ROOT/<relative-path>`.
This variable stays in scope for all bash blocks in this step.

**Interface lookup (RC1, RAISE-15431) — query before you guess.** Before invoking any `rai <cmd>` subcommand or `raise_cli` import you have NOT verified this session:
1. Query the graph: `rai graph query "<cmd> <subcommand>" --types symbol --limit 3`
   - For Jira transitions/priorities: `rai graph query "jira transition workflow" --types pattern` (PAT-F-1826 has the RAISE workflow; PAT-E-9996..9998 have priority/issue-type/transition values)
   - For SCM tools (glab, gh): `rai graph query "glab/gh <cmd> <subcommand>" --types pattern --limit 3` (glab/gh have no Python symbols — PAT-E-10000..10009 cover flags, 409/404 errors, glab vs gh distinctions)
   - For SQLite/raise.db schema: `rai graph query "raise.db <table> schema" --types pattern --limit 3` (schema is not in code symbols — PAT-E-9999..10007 have column lists)
2. Fallback if 0 results: `rai <cmd> --help` | for SCM tools: `glab/gh <cmd> --help` | for DB: `sqlite3 db ".schema"`
Skip when the interface was already verified this session. One query beats a spiral of guessed-flag retries (70% of RC1 errors spiral).

For the next uncompleted task in plan order:

1. **RED** — Call `raise_session_topic(kind="implement", topic="red")` first, then write a failing test that defines expected behavior
2. **GREEN** — Call `raise_session_topic(kind="implement", topic="green")` first, then write minimal code to make the test pass
3. **REFACTOR** — Call `raise_session_topic(kind="implement", topic="refactor")` first, then clean up while keeping tests green

Follow project rules, guardrails, and established patterns.

### Step 3: Complete Task (one call)

The deterministic per-task ritual — scoped gates, branch assert, stage,
commit, signal — runs in raise-cli. Call it once per completed task.

**Pre-format (mandatory — eliminates gate-format retry, RAISE-15429 AC1):**
```bash
uv run ruff format packages/<changed-package>/
git add -u
```
If `git add -u` stages nothing, proceed — code was already clean. This runs
before `raise_task_complete` so the internal gate-format check passes on the
first call instead of blocking and requiring a restage retry.

> **schema.sum carve-out:** if this task modified `project.schema.file`, run
> `rai schema sum update && git add .raise/schema.sum` BEFORE the call, and
> include that file in `files`.

Use the `raise_task_complete` MCP tool with:

- `work_id` — story identifier, e.g. `"S8370.1"`
- `task_name` — free-text task description, e.g. `"T1: rewrite Steps 3-4"`
- `expected_branch` — e.g. `"story/s8370.1/my-slug"` (asserted before any git mutation)
- `commit_message` — full message including `Co-Authored-By` line (LLM authors this)
- `gate_scope` — changed test dir, e.g. `"packages/raise-cli/tests/task/"`;
  `""` = full suite — prefer scoped
- `files` — space-separated paths to stage; `""` = `git add -u` (tracked changes only)
- `cwd` — worktree path. Required — omitting it returns an explicit error;
  the MCP server's own CWD is pinned to the main worktree and is never a
  valid substitute (RAISE-11004)

Gates run server-side, output captured — do NOT run gate checks,
`git add`, `git commit`, or `uv run pytest` by hand here. Do NOT emit signals.

**Blocked-status response table:** the report carries five per-step fields —
`gates`, `branch`, `stage`, `commit`, `signal` — each `ok|warn|blocked`. The
first blocked step stops the chain; later steps are skipped.

| Condition | Action |
|-----------|--------|
| `status: ok` | Present task summary, continue to Step 4 |
| `gates: blocked` (gate fail, < 3 retries on same gate) | Fix the failing gate, re-run Step 2 if needed, call `raise_task_complete` again. Applies to the **1st and 2nd** failure of a given gate only |
| `gates: blocked` (≥ 3 retries on same gate) | **STOP — do NOT call `raise_task_complete` again.** Self-recovery has failed. Count the failures for this gate, then present to the human: *"Gate {gate_id} failed {N} times; cannot self-recover."* plus options — **(a)** investigate gate dependencies (missing tool/env, upstream breakage), **(b)** escalate to a senior engineer, **(c)** `RAISE_AR_SKIP_REASON=<reason>` — requires documented justification, not a default or autonomous choice. Wait for the human's selection |
| `branch: blocked` (branch mismatch) | STOP — wrong branch; surface to human, do not force. Fix branch, retry |
| `stage: blocked` (`git-add-failed`) | STOP — a path in `files` is wrong/missing; surface stderr, fix the path, retry. Never auto-resolve |
| `commit: blocked` (dirty tree / no landing) | STOP — present state; never auto-stash or discard |
| `warn` | Mention; continue |

### Step 4: Iterate or Finalize

| Condition | Action |
|-----------|--------|
| More tasks remain | Return to Step 2 |
| All tasks complete | **Run package-scoped tests + full lint/format/types** (see below) |
| Task blocked | Document blocker, escalate to human |

**End-of-story gates** — scope tests to the changed package, keep lint/format/types full-project:

```bash
# Identify changed package (usually known from plan; verify with git diff if needed)
rai gate check gate-tests --scope packages/<changed_package>/
rai gate check gate-lint
rai gate check gate-format
rai gate check gate-types
```

If the story touches multiple packages, run `rai gate check gate-tests --scope packages/<pkg>/` once per changed package. Only fall back to unscoped `rai gate check gate-tests` when the changed package is genuinely ambiguous.

**Protocol implementor sweep (Jidoka — mandatory, blocking)** — after gates pass, check whether any changed source file defines a `@runtime_checkable` Protocol. If yes, grep the entire monorepo for every implementor of that Protocol and verify each one implements all required methods. This is a **stop-the-line** gate: Pyright does NOT catch missing method implementations in non-inheriting implementors of `runtime_checkable` Protocols (structural subtyping is runtime-only via `isinstance()`). RCA: RAISE-8110 (second recurrence of the same cross-package gap).

```bash
# Re-read manifest vars (PAT-129)
_CFG=$(rai manifest env)
CODE_ROOT_GLOB=$(echo "$_CFG" | python3 -c "import json,sys; print(json.load(sys.stdin).get('code',{}).get('root_glob','') or 'packages/*/src/')")
DEV_BRANCH=$(echo "$_CFG" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('branches',{}).get('development','main'))")

# Detect runtime_checkable Protocols touched in this story
changed_files=$(git diff --name-only HEAD...$(git merge-base HEAD "$DEV_BRANCH") -- "$CODE_ROOT_GLOB")
for f in $changed_files; do
  protocols=$(grep -oP '(?<=class )\w+(?=\([^)]*Protocol[^)]*\))' "$f" 2>/dev/null)
  if grep -q "@runtime_checkable" "$f" 2>/dev/null && [ -n "$protocols" ]; then
    for proto in $protocols; do
      echo "▶ Protocol sweep: $proto (defined in $f)"
      grep -rn "class .*$proto\b\|$proto\b" packages/ --include="*.py" \
        | grep -v "^$f:" \
        | grep -v "test_\|_test\." \
        | grep "class " || true
      echo "→ Verify each implementor above has all methods required by $proto before continuing."
      echo "BLOCKED until sweep confirmed: $proto implementors in monorepo"
    done
  fi
done
```

| Result | Action |
|--------|--------|
| No `@runtime_checkable` Protocol touched | Skip silently |
| Protocols found, all implementors current | Document sweep result, continue |
| Implementor missing required methods | **STOP.** Update the implementor. Re-run gates. Do NOT skip. |

**Orphaned test check (Jidoka — mandatory, blocking)** — after gates pass, verify no test files that import from changed modules were left untouched. This is a **stop-the-line** gate: if orphaned tests exist, you MUST read each one and either update it or confirm it still passes. Do NOT proceed to emit implement-complete until resolved.

```bash
# Re-read manifest vars (PAT-129)
_CFG=$(rai manifest env)
# tier-2: configurable with default — preserves packages/*/src/ for raise-commons
CODE_ROOT_GLOB=$(echo "$_CFG" | python3 -c "import json,sys; print(json.load(sys.stdin).get('code',{}).get('root_glob','') or 'packages/*/src/')")

# List source modules changed in this story (vs epic/dev branch)
orphans=0
changed_modules=$(git diff --name-only HEAD...$(git merge-base HEAD {dev_branch}) -- "$CODE_ROOT_GLOB" | sed 's|.*/src/||; s|/[^/]*$||' | sort -u)
for mod in $changed_modules; do
  mod_dotted=$(echo "$mod" | tr '/' '.')
  grep -rl "from $mod_dotted" packages/*/tests/ 2>/dev/null | while read tf; do
    if ! git diff --name-only HEAD...$(git merge-base HEAD {dev_branch}) -- "$tf" | grep -q .; then
      echo "BLOCKED: $tf imports $mod_dotted but was not touched by this story"
      orphans=$((orphans + 1))
    fi
  done
done
```

| Result | Action |
|--------|--------|
| No orphans | Continue to emit implement-complete |
| Orphans found | **STOP.** Read each flagged test. Run it. If it fails, fix it. If it passes, document why no change was needed. Do NOT skip. |

Zero broken windows. RCA: RAISE-2564 and S2161.1 both left integration tests orphaned because this check did not exist.

**Doc creation check** — runs only if `project.docs.product.primary_dir` is declared and story added new primary docs or CLI commands:

```bash
DEV_BRANCH=$(python3 -c "import yaml; print(yaml.safe_load(open('.raise/manifest.yaml'))['branches']['development'])" 2>/dev/null || echo "release/3.1.0")

# Re-read manifest vars — this block runs in a fresh bash context at end-of-story
_CFG=$(rai manifest env)
PRIMARY_DOCS=$(echo "$_CFG" | python3 -c "import json,sys; print(json.load(sys.stdin).get('docs',{}).get('product',{}).get('primary_dir',''))")
TRANSLATIONS_DIR=$(echo "$_CFG" | python3 -c "import json,sys; print(json.load(sys.stdin).get('docs',{}).get('product',{}).get('translations_dir',''))")
PARITY_CHECK=$(echo "$_CFG" | python3 -c "import json,sys; print(json.load(sys.stdin).get('docs',{}).get('product',{}).get('parity_check',''))")

if [ -n "$PRIMARY_DOCS" ]; then
  if [ -n "$TRANSLATIONS_DIR" ]; then
    NEW_DOCS=$(git diff --name-only $(git merge-base HEAD "$DEV_BRANCH")..HEAD -- "$PRIMARY_DOCS" | grep -v "^${TRANSLATIONS_DIR}/" | wc -l | xargs)
  else
    NEW_DOCS=$(git diff --name-only $(git merge-base HEAD "$DEV_BRANCH")..HEAD -- "$PRIMARY_DOCS" | wc -l | xargs)
  fi
  NEW_CLI=$(git diff --name-only $(git merge-base HEAD "$DEV_BRANCH")..HEAD -- 'packages/raise-cli/src/raise_cli/cli/commands/' | wc -l | xargs)
  if [ "$((NEW_DOCS + NEW_CLI))" -gt 0 ]; then
    echo "▶ Doc creation check ($NEW_DOCS new primary docs, $NEW_CLI new CLI commands)"
    if [ -n "$PARITY_CHECK" ]; then
      $PARITY_CHECK --fix
      [ -n "$TRANSLATIONS_DIR" ] && git add "$TRANSLATIONS_DIR/"
      git diff --cached --quiet && echo "✓ parity ok — no stubs needed" || \
        git commit -m "docs: add stubs for new pages (auto-generated)"
    fi
  fi
fi
```

| Condition | Action |
|-----------|--------|
| `project.docs.product.primary_dir` absent in manifest | Skip silently — tier-3 |
| No new primary docs or CLI commands | Skip silently |
| Stubs generated | Committed before implement-complete signal |
| Parity already ok | No commit (guard prevents empty commit) |

**Emit implement artifact (mandatory, blocking — RAISE-11147)** — after all gates above pass, record proof that this phase actually produced work. `story.yaml`'s `implement.validates` checks for this artifact in SQLite before the pipeline can advance past `implement`; without it, `pipeline_advance` returns `artifact_missing`/`gate_proof_required`.

```bash
# Re-read manifest vars (PAT-129)
_CFG=$(rai manifest env)
DEV_BRANCH=$(echo "$_CFG" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('branches',{}).get('development','main'))")

# Reuse the same changed-file diff as the Protocol sweep above
files_changed=$(git diff --name-only HEAD...$(git merge-base HEAD "$DEV_BRANCH"))
tests_added=$(echo "$files_changed" | grep -E '(^|/)tests?/' || true)
```

Call `raise_artifact_emit` with the computed lists:

```
raise_artifact_emit(
    artifact_type="implement",
    story_id="{issue_id}",
    content=<JSON string with fields: files_changed (list[str]), tests_added (list[str]), coverage_percent (optional float)>,
    cwd="{project_or_worktree_path}"
)
```

**CRITICAL — identifier mismatch risk:** `story_id` here MUST be the pipeline's **issue key** (the same value passed to `pipeline_start`, e.g. `"RAISE-1281"` — available in-session as `{issue_id}`), **NOT** the `S{N}.{M}` story-number convention used by `rai-story-design`'s/`rai-story-plan`'s own `raise_artifact_emit` calls. `story.yaml`'s sqlite validate branch looks up `artifact_store.exists(run["issue_id"], "implement")` — `run["issue_id"]` is always the Jira key. If a future edit "corrects" this back to `S{N}.{M}` to match the design/plan convention, the sqlite lookup will **never** find the artifact, turning today's silent hollow-pass into a **permanent `gate_proof_required` deadlock** for every story pipeline (RAISE-11147 AR finding).

**Note:** The CLI fallback for artifact emission was removed in v3.0.0. MCP tool `raise_artifact_emit` is required. If MCP tools are not available, skip structured artifact emission — the pipeline will require it before advancing past `implement`.

After all gates pass, emit the implement-complete signal — commit is auto-resolved from git HEAD and stored in SQLite for story-close to read.

Gate runner reads commands from `.raise/manifest.yaml` for any stack. Configure with `rai init --detect` or set `project.{test,lint,format,type_check}_command` manually.

<verification>
All plan tasks committed. Package-scoped gates pass. Orphaned test check clean. Implement artifact emitted (files_changed/tests_added). implement-complete signal emitted for current HEAD.
</verification>

## Output

| Item | Destination |
|------|-------------|
| Implemented code | Per project architecture |
| Implement artifact | SQLite (`artifact_type=implement`, keyed by issue key) |
| Signal | WorkLifecycle event emitted (start on entry, complete here) |

**STOP HERE.** Return your summary to the orchestrator. Do NOT invoke any further skill.

## Quality Checklist

- [ ] NEVER bypass `raise_task_complete` with manual `git commit` — gates run inside it
- [ ] NEVER skip a failing test — fix it or escalate
- [ ] NEVER accumulate errors — stop on defect (Jidoka)

## References

- Gate: `gates/gate-code.md`
