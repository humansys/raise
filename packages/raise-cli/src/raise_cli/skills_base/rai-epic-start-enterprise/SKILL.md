---
name: rai-epic-start-enterprise
description: Initialize epic directory, brief, and tracker entry. Use to begin a new epic.
model: haiku

allowed-tools:
  - Read
  - Edit
  - Grep
  - Glob
  - "Bash(rai:*)"
  - "Bash(git branch --show-current)"
  - "Bash(git checkout *)"
  - "Bash(git pull)"
  - "Bash(git status *)"
  - "Bash(git add *)"
  - "Bash(git commit *)"

license: MIT

metadata:
  raise.work_cycle: epic
  raise.frequency: per-epic
  raise.fase: "2"
  raise.prerequisites: ""
  raise.next: epic-design
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "3.0.0"
  raise.visibility: public
  raise.inputs: |
    - epic_id: string, required, argument
    - epic_slug: string, required, argument
    - dev_branch: string, required, config
  raise.outputs: |
    - brief: file_path, next_skill
    - scope: file_path, next_skill
---

# Epic Start

## Purpose

Initialize an epic with scope artifacts and a tracker entry. Epics are logical containers (directory + tracker), not branches. Story branches are created directly from the development branch.

## Mastery Levels (ShuHaRi)

- **Shu**: Follow all steps, verify each before proceeding
- **Ha**: Streamline scope for well-understood epics
- **Ri**: Integrate with release workflows and automated setup

## Context

**When to use:** Starting a new body of work (3-10 stories), beginning a planned epic from the backlog.

**When to skip:** Small fixes or single stories (no epic needed). Continuation of existing epic.

**Inputs:** Epic number (E{N}), epic name/slug, high-level objective.

**Branch config:** Read `branches.development` from `.raise/manifest.yaml` for `{dev_branch}`. Default: `main`.

## Steps

### Step 1: Verify Working Tree State + Development Branch (RAISE-11778)

Before switching branches, confirm the working tree is clean — an unexpected dirty tree may hold someone else's uncommitted work:

```bash
git status --short
git branch --show-current
```

| Condition | Action |
|-----------|--------|
| Tree clean, on `{dev_branch}` | Continue |
| Tree clean, on other branch | `git checkout {dev_branch} && git pull` |
| Tree has uncommitted/untracked changes | **STOP** — report "blocked: working tree not clean" with the actual `git status` output. Do NOT improvise a fix. |

<verification>
Working tree confirmed clean. On `{dev_branch}`, up to date with remote.
</verification>

<if-blocked>
**NEVER** run `git reset --hard`, `git clean -fd`, `git stash` (without explicit developer confirmation), or any other command to force past a dirty tree or failed checkout — that state may hold someone else's uncommitted work. Report blocked and stop (RCA RAISE-11778: a destructive-recovery incident in a sibling skill destroyed uncommitted work this way).
</if-blocked>

### Step 2: Verify No Directory Collision

Before creating the epic directory, check that no existing directory would collide:

```bash
ls work/epics/ | grep -i "^e{N}-"
```

| Condition | Action |
|-----------|--------|
| No match | Continue — safe to create |
| Match found | **STOP** — directory `e{N}-*` already exists. Ask the developer to choose a different epic number |

This prevents ID collisions in the knowledge graph (RAISE-1199, RAISE-1204).

<verification>
No existing directory matches `e{N}-*` pattern.
</verification>

### Step 3: Define Scope & Commit

Create TWO artifacts via CLI:

1. `work/epics/e{N}-{name}/brief.md` — hypothesis, success metrics, appetite, rabbit holes:

Use `raise_docs_write` MCP tool with doc_type="epic-brief", title="E{N}: {epic-name} brief", content="[brief content following templates/brief.md]", output_path="work/epics/e{N}-{name}/brief.md", cwd="{project_or_worktree_path}".
**Verify result:** If `result.status != "ok"`, stop immediately with error:
  `Epic brief write failed: {result.error}. Cannot continue without docs sync in connected mode.`
If MCP tools are not available, fall back to:
```bash
rai docs write epic-brief \
  --title "E{N}: {epic-name} brief" \
  --stdin \
  --output-path work/epics/e{N}-{name}/brief.md << 'EOF'
[brief content following templates/brief.md]
EOF
```
**If exit code != 0, stop immediately** — do not proceed to scope creation.

2. `work/epics/e{N}-{name}/scope.md` — objective, in/out scope, planned stories, done criteria:

Use `raise_docs_write` MCP tool with doc_type="epic-scope", title="E{N}: {epic-name} scope", content="[scope content: objective, in/out scope, planned stories, done criteria]", output_path="work/epics/e{N}-{name}/scope.md", cwd="{project_or_worktree_path}".
**Verify result:** If `result.status != "ok"`, stop immediately with error:
  `Epic scope write failed: {result.error}. Cannot continue without docs sync in connected mode.`
If MCP tools are not available, fall back to:
```bash
rai docs write epic-scope \
  --title "E{N}: {epic-name} scope" \
  --stdin \
  --output-path work/epics/e{N}-{name}/scope.md << 'EOF'
[scope content: objective, in/out scope, planned stories, done criteria]
EOF
```
**If exit code != 0, stop immediately** — do not proceed to commit.

Commit (scoped to this epic's directory — RAISE-11778: `git add -A` in a shared checkout silently sweeps in unrelated uncommitted work from other sessions):

```bash
git add work/epics/e{N}-{name}/
git commit -m "epic(e{N}): initialize {epic-name}

Objective: {1-line}

In scope:
- {item 1}
- {item 2}

Co-Authored-By: Rai <rai@humansys.ai>"
```

Register epic in the backlog tracker:

**If Jira issue exists** — backlog transition is engine-owned (RAISE-15034):
Engine transitions epic to start status via `apply_phase_transition` at phase completion.
No skill-initiated transition call required or allowed.
**Standalone-mode notice** (RAISE-16988): When no pipeline run is active, the tracker is **not** moved — `apply_phase_transition` requires the engine. In standalone execution, report explicitly:
> "⚠️ Tracker not updated: this skill ran standalone (no active pipeline run). Backlog status unchanged. Run the pipeline or update the tracker manually."

**Engine behavior** (RAISE-16987): The engine checks `ExecutionContext` to determine mode:
- `mode: pipeline` — `apply_phase_transition` moves the tracker. No skill call required or allowed.
- `mode: standalone` — tracker is **not** moved. Report explicitly:
  > "⚠️ Tracker not updated: this skill ran standalone (no active pipeline run). Backlog status unchanged. Run the pipeline or update the tracker manually."

  To force a transition standalone: `rai backlog transition {key} --point {workflow_point}`

**If new epic (no Jira key)** — verify credentials, read project key from backlog.yaml and create:

> **Credentials check (mandatory before creating):** Verify `JIRA_API_TOKEN` or `JIRA_API_TOKEN_HUMANSYS` is set in the environment. If not, source the project `.env` (`set -a && source .env && set +a`) or stop and ask the developer. **Never run `rai backlog create` without credentials** — it creates a local-only entry that silently syncs as a duplicate on the next credentialed invocation.

```bash
BACKLOG_PROJECT=$(python3 -c "
import yaml
cfg = yaml.safe_load(open('.raise/backlog.yaml'))
orgs = cfg.get('jira', {}).get('organizations', {}).values()
projs = next(iter(orgs), {}).get('projects', [])
print(projs[0] if projs else '')
" 2>/dev/null)
rai backlog create "{title}" \
  -p "${BACKLOG_PROJECT}" \
  -t Epic \
  -l epic \
  -d "{objective — 1-line from the brief}"
```

5. **Persist the Jira key in scope.md** — after creating (or when the key is already known), ensure `scope.md` contains the epic's Jira key so downstream skills (e.g. `rai-story-start`) can resolve the parent. Add or update a line in scope.md:

```markdown
## Jira

Epic: {JIRA_KEY}
```

This is the canonical reference for story-start to find the epic parent key. Without it, stories are created as orphans in Jira.

| Condition | Action |
|-----------|--------|
| Jira key exists | statuses list → infer → transition. Persist key in scope.md if not already there |
| No key, adapter configured | create with BACKLOG_PROJECT. Persist returned key in scope.md |
| No adapter configured | Skip entirely — no warning needed |
| Create fails | Stop immediately — "Backlog create failed: cannot continue without tracker entry." |
| Transition fails | Stop immediately — "Lifecycle transition failed: check adapter connection." |

<verification>
Scope commit on `{dev_branch}`. Epic visible in backlog. Jira key persisted in scope.md for downstream story creation.
</verification>

<if-blocked>
Adapter not configured → skip silently. Backlog sync is best-effort; it must never block epic work.
</if-blocked>

### Step 3b: Create Epic Worktree Branch (when using a dedicated worktree)

If this epic is being developed in a dedicated git worktree, create the per-epic intermediate branch now:

```bash
git checkout -b worktree-{epic-slug} {dev_branch}
```

Stories will merge to this branch (not to `{dev_branch}` directly). Only `rai-epic-close` merges `worktree-{epic-slug}` → `{dev_branch}` via MR.

| Condition | Action |
|-----------|--------|
| Epic uses a dedicated git worktree | Create `worktree-{epic-slug}` from `{dev_branch}` — mandatory |
| Standalone epic on the main worktree | Skip — no intermediate branch needed |

<verification>
Worktree branch `worktree-{epic-slug}` created (or skip documented for standalone epic).
</verification>

### Step 4: Present Next Steps

Show the developer:
- Commit hash and epic directory path
- Quick scope summary (objective + story count)
- **Next:** `/rai-epic-design` to formalize scope and stories

## Scope Constraints (RAISE-11778)

- **NEVER** run `git reset --hard`, `git clean -fd`, or `git checkout -- .` to resolve an unexpected working tree state — STOP and report instead, it may hold someone else's uncommitted work
- **NEVER** `git add -A` — stage only `work/epics/e{N}-{name}/`

## Output

| Item | Destination |
|------|-------------|
| Epic Brief | `work/epics/e{N}-{name}/brief.md` |
| Scope | `work/epics/e{N}-{name}/scope.md` |
| Scope commit | On `{dev_branch}` |
| Backlog entry | Tracker via rai backlog CLI |
| Next | `/rai-epic-design` (user-facing epics then continue through `/rai-epic-ux-design` before planning) |

**STOP HERE.** Return your summary to the orchestrator. Do NOT invoke any further skill.

## Quality Checklist

- [ ] Working tree verified clean before any branch switch (Step 1)
- [ ] Epic Brief created from `templates/brief.md`
- [ ] Scope commit includes objective and boundaries
- [ ] Epic registered in tracker via rai backlog CLI
- [ ] Epic worktree branch `worktree-{epic-slug}` created when using a dedicated worktree
- [ ] NEVER skip worktree branch — stories must not merge directly to `{dev_branch}` in a dedicated worktree
- [ ] NEVER used reset --hard / clean -fd / git add -A to resolve an obstacle

## References

- Next: `/rai-epic-design` (user-facing epics then continue through `/rai-epic-ux-design` before planning)
- Stories: `/rai-story-start` (branches from `{dev_branch}`)
- Close: `/rai-epic-close`
- Branch model: `AGENTS.md` § Branch Model
