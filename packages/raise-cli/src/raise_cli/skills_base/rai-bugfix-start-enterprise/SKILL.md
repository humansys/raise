---
name: rai-bugfix-start-enterprise
description: Initialize bug branch, reproduce, and create scope artifact. Phase 1 of bugfix pipeline.
model: haiku

allowed-tools:
  - Read
  - Edit
  - Grep
  - Glob
  - "Bash(git fetch *)"
  - "Bash(git checkout -b *)"
  - "Bash(git rev-parse *)"
  - "Bash(git branch --show-current)"
  - "Bash(git status *)"
  - "Bash(git add *)"
  - "Bash(git commit *)"
  - "Bash(rai:*)"

license: MIT
metadata:
  raise.adaptable: 'true'
  raise.fase: '1'
  raise.frequency: per-bug
  raise.gate: ''
  raise.next: bugfix-triage
  raise.prerequisites: ''
  raise.skillset: raise-maintainability
  raise.version: 2.4.0
  raise.visibility: public
  raise.work_cycle: bugfix
  raise.inputs: |
    - bug_id: string, required, argument (e.g. RAISE-251)
    - dev_branch: string, required, config
    - fix_version: string, optional (disambiguates target release line — RAISE-17066)
  raise.outputs: |
    - bug_branch: string, next_skill
    - scope_md: file_path, next_skill
---

# Bugfix Start

## Purpose

Create a bug branch from the development branch, reproduce the bug, and write the scope artifact that defines what the bug is and when it's fixed.

## Mastery Levels (ShuHaRi)

- **Shu**: Follow all steps, reproduce bug, create scope with all 5 fields
- **Ha**: Streamline scope for well-understood bugs
- **Ri**: Custom initialization patterns for specific domains

## Context

**When to use:** A tracked bug (Jira issue) needs formal resolution with branch, artifacts, and traceability.

**When to skip:** Trivial fix (typo, obvious one-liner) — commit directly. Already started (scope.md exists).

**Inputs:** Bug ID (e.g., RAISE-251), problem statement or reproduction steps.

**Expected state:** On `{dev_branch}`, up to date with remote. No `work/bugs/{issue_key}/` directory yet.

**Branch config:** `{dev_branch}` is resolved from `.raise/manifest.yaml` (`branches.release_lines[]` / `branches.development`) via `rai worktree resolve-base` (see Step 0.5) — declared, never inferred from `origin/release/*`. Ambiguity (e.g. an unresolvable `fix_version`) fails loud instead of guessing.

## Steps

### Step 0: Verify Working Tree State (RAISE-11778)

Before touching git, confirm the working tree is the one you expect and is clean:

```bash
git rev-parse --show-toplevel
git status --short
```

| Condition | Action |
|-----------|--------|
| Toplevel matches the expected worktree/repo path, tree clean | Continue to Step 1 |
| Toplevel is unexpected, or tree has uncommitted/untracked changes | **STOP** — report "blocked: working tree not in expected state" with the actual output. Do NOT improvise a fix. |

<verification>
Working tree confirmed clean and on the expected path before any git mutation.
</verification>

<if-blocked>
**NEVER** run `git reset --hard`, `git clean -fd`, or any other destructive command to "fix" an unexpected working tree state — that state may hold someone else's uncommitted work. Report blocked and stop (RCA RAISE-11778: a Haiku-driven bugfix-start agent improvised `reset --hard` + `clean -fd` on an unexpected dirty tree, destroying an uncommitted skill and an epic directory that were never recovered from git objects — only recoverable by chance because copies existed in skill-sync mirrors and sibling worktrees).
</if-blocked>

### Step 0.5: Resolve dev branch from the manifest (RAISE-17066)

The target branch is *declared*, never inferred: `rai worktree resolve-base`
resolves it from `.raise/manifest.yaml` (`branches.release_lines[]` /
`branches.development`) through the same `resolve_target()` chain
`pipeline_start` uses — env override > `fix_version` mapping > work-type
default > fail loud. A newer `origin/release/*` branch than the manifest
does NOT silently win; an unresolvable topology is a hard block, not a
guess.

```bash
# RAISE-17066: target declared in .raise/manifest.yaml (branches.release_lines[] /
# branches.development), never inferred from origin/release/*. Ambiguity fails loud.
RESOLVED="$(rai worktree resolve-base --work-type bugfix ${fix_version:+--fix-version "$fix_version"} -f json)" \
  || { echo "blocked: target branch ambiguous — pass fix_version or fix branches.release_lines"; exit 1; }
DEV_BRANCH="$(echo "$RESOLVED" | python3 -c "import json,sys; print(json.load(sys.stdin)['data']['branch'])")"
BASE_REF="$(echo "$RESOLVED" | python3 -c "import json,sys; print(json.load(sys.stdin)['data']['base_ref'])")"
```

| Condition | Action |
|-----------|--------|
| `status: ok` or `warn` | Use `{dev_branch}` = `$DEV_BRANCH`, `{base_ref}` = `$BASE_REF`. Present `data.warnings` verbatim if any. Continue to Step 1. |
| `status: blocked` (e.g. unresolvable `fix_version`) | **STOP** — report the warning verbatim and ask the developer to pass `fix_version` or fix `branches.release_lines` in the manifest. Do NOT guess a branch. |

<verification>
`{dev_branch}`/`{base_ref}` resolved via `rai worktree resolve-base` before any branching.
</verification>

### Step 1: Create Bug Branch

```bash
git checkout -b bug/{issue_key}/{bug-slug} "$BASE_REF"
```

<verification>
On `bug/{issue_key}/{slug}` branch.
</verification>

<if-blocked>
Dev branch has conflicts → resolve before branching. **NEVER** `reset --hard` or `clean -fd` to force past a conflict — stop and report instead (see Step 0).
</if-blocked>

### Step 2: Reproduce & Write Scope

Reproduce the bug — confirm it is observable. Publish the scope artifact via CLI:

Use `raise_docs_write` MCP tool with doc_type="bugfix-scope", title="{issue_key}: scope", content="WHAT: {behavior observed}\nWHEN: {conditions / triggers}\nWHERE: {file:line or component}\nEXPECTED: {correct behavior}\nDone when: {specific observable outcome}", output_path="work/bugs/{issue_key}/scope.md", cwd="{project_or_worktree_path}".
If MCP tools are not available, fall back to:
```bash
rai docs write bugfix-scope \
  --title "{issue_key}: scope" \
  --stdin \
  --output-path work/bugs/{issue_key}/scope.md << 'EOF'
WHAT:      {behavior observed}
WHEN:      {conditions / triggers}
WHERE:     {file:line or component}
EXPECTED:  {correct behavior}
Done when: {specific observable outcome}
EOF
```

Commit the scope artifact:

```bash
git add work/bugs/{issue_key}/scope.md
git commit -m "bug({issue_key}): initialize scope

WHAT: {summary}
Done when: {criteria}

Co-Authored-By: Rai <rai@humansys.ai>"
```

<verification>
Bug reproduces. Scope artifact committed on bug branch.
</verification>

### Step 2b: Update Backlog Status

Query available statuses for this issue type:
```bash
rai backlog statuses list --issue-type Bug
```

Infer start status from output:
- Look for `category=indeterminate` states whose name suggests active work
  (Implement, In Progress, Started, Active, WIP, Doing…)
- Single clear candidate → use it silently
- Multiple candidates or ambiguous name → ask developer:
  *"Which status means 'work started'? Options: [list]"*

| Condition | Action |
|-----------|--------|
| No ticket | Skip silently |

### Step 2c: Bind Session to Jira Key

When the bug has a Jira key, bind it to the per-session context file:
Use the `raise_session_bind` MCP tool with key="RAISE_SESSION_JIRA_KEY", value="{bug_key}", cwd="{project_or_worktree_path}".
If MCP tools are not available, fall back to:
```bash
rai session bind RAISE_SESSION_JIRA_KEY "{bug_key}"
```

| Condition | Action |
|-----------|--------|
| Bug has Jira key | Bind via MCP (server emits event) |
| No Jira key | Skip silently |

<verification>
`.raise/rai/sessions/$RAISE_CC_SESSION_ID/context.env` contains `RAISE_SESSION_JIRA_KEY={bug_key}` (other keys preserved).
`session_bind` event emitted (or skipped silently if no server).
</verification>

## Scope Constraints (CRITICAL — RAISE-11778)

- **NEVER run `git reset --hard`, `git clean -fd`, or `git checkout -- .`** to resolve an unexpected working tree state — these are irreversible and may destroy someone else's uncommitted work
- **NEVER force past a blocked state** — an unexpected branch, dirty tree, or conflict is a STOP condition, not an obstacle to engineer around
- **NEVER delete files or directories outside `work/bugs/{issue_key}/`**

If something looks wrong, return it as a finding — do not act on it.

## Output

| Item | Destination |
|------|-------------|
| Bug branch | `bug/{issue_key}/{slug}` from `{dev_branch}` |
| Scope artifact | `work/bugs/{issue_key}/scope.md` |
| Backlog update | engine-owned — pipeline engine handles Jira transitions (RAISE-15027) |

**Standalone-mode notice** (RAISE-16988): When no pipeline run is active, the tracker is **not** moved — `apply_phase_transition` requires the engine. In standalone execution, report explicitly:
> "⚠️ Tracker not updated: this skill ran standalone (no active pipeline run). Backlog status unchanged. Run the pipeline or update the tracker manually."

**Engine behavior** (RAISE-16987): The engine checks `ExecutionContext` to determine mode:
- `mode: pipeline` — `apply_phase_transition` moves the tracker. No skill call required or allowed.
- `mode: standalone` — tracker is **not** moved. Report explicitly:
  > "⚠️ Tracker not updated: this skill ran standalone (no active pipeline run). Backlog status unchanged. Run the pipeline or update the tracker manually."

  To force a transition standalone: `rai backlog transition {key} --point {workflow_point}`

**STOP HERE.** Return your summary to the orchestrator. Do NOT invoke any further skill.

## Quality Checklist

- [ ] Working tree verified clean and on expected path before any git mutation (Step 0)
- [ ] Bug branch created from `{dev_branch}`
- [ ] Bug reproduces before any investigation
- [ ] Scope artifact committed with WHAT/WHEN/WHERE/EXPECTED/Done-when
- [ ] NEVER investigate before reproducing
- [ ] NEVER used reset --hard / clean -fd / checkout -- . to resolve an obstacle

## References

- Next: `/rai-bugfix-triage`
- Complement: `/rai-bugfix-close`
- Branch model: `AGENTS.md` § Branch Model
