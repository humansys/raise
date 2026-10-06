---
name: rai-story-start-enterprise
description: Create story branch and scope commit. Use to begin story work.
model: haiku

allowed-tools:
  - Read
  - Edit
  - Grep
  - Glob
  - "Bash(rai:*)"

license: MIT

metadata:
  raise.work_cycle: story
  raise.frequency: per-story
  raise.fase: "3"
  raise.prerequisites: ""
  raise.next: story-design
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "4.0.0"
  raise.visibility: public
  raise.inputs: |
    - story_id: string, required, argument
    - dev_branch: string, required, config
  raise.outputs: |
    - story_branch: string, next_skill
    - story_md: file_path, next_skill
    - scope_md: file_path, next_skill
raise.mastery:
  shu: "Explain each check result and the scope content before opening"
  ha: "Present only blocked/warn signals"
  ri: "Tool call → one-line confirmation → next"
---

# Story Start

## Purpose

Open a story in ONE composite call. The deterministic ritual (epic check,
worktree detection, branch, docs write, scope commit, backlog transition,
session bind) runs in `raise-cli` — this skill only authors the content
and presents the result (ADR-093 / ADR-024).

## Steps

### Step 0: Sync base branch (Ri: auto; Shu/Ha: confirm)

Before authoring any content, sync the dev branch by delegating to the
tested Python decision in `story.open_service.sync_dev_branch` — never run
raw `git fetch`/`git merge` here:

```bash
rai story sync-dev-branch -f json
```

Inside ANY worktree (registered or not), this command **never touches
HEAD** — no branch-selection logic runs inside a worktree at all (Regla 2,
RAISE-15825). The worktree's HEAD already reflects the branch context it
was created with (e.g. an epic branch); fast-forwarding it against the dev
branch — even trivially, before the two have diverged — would silently
collapse that context. Outside any worktree, behavior is unchanged: fetch +
`--ff-only` merge against the global dev branch.

| `status` (JSON) | Action |
|------------------|--------|
| `ok` with `data.skipped: true` | Inside a worktree — HEAD untouched, correct. Continue. |
| `ok` (no skip) | Synced against the dev branch. Report "Sync: +N commits from {dev_branch}" if `data.dev_branch` is present; continue. |
| `warn` | Fetch failed but non-blocking (intermittent network, no `origin` configured). Mention briefly; continue. |
| `blocked` (`dev-branch-diverged`) | **STOP** — escalate to developer; do NOT force-merge |
| **Ri** level | Run the command; report the one-line result, no confirmation prompt |
| **Shu/Ha** level | Mention the pending sync and ask confirmation before running the command |

### Step 1: Author content (judgment)

Write the two markdown bodies (this is the LLM's contribution):
- **story_content** — Connextra user story, Gherkin AC, SbE examples
  (structure: `templates/story.md`). Source: backlog issue + epic scope.
  Set frontmatter `jira_key` to the same key used as `jira_key="{KEY}"` in
  Step 2 (empty string if none) — `gate-backlog-sync` reads this field to
  verify the story's Jira linkage structurally instead of by title text
  (RAISE-14588).
- **scope_content** — `## In Scope`, `## Out of Scope`, `## Done when`
  (observable outcomes).

### Step 2: Open (one call)

Use the `raise_story_open` MCP tool with story_id="S{N}.{M}",
slug="{story-slug}", epic_dir="e{N}-{name}" (empty for standalone),
jira_key="{KEY}" (empty if none), story_content, scope_content,
cwd="{project_or_worktree_path}".

CLI fallback (ADR-084): `rai story open --story-id S{N}.{M} --slug {slug}
--epic-dir e{N}-{name} --jira-key {KEY} --story-file /tmp/story.md
--scope-file /tmp/scope.md -f json`

Telemetry is emitted server-side — do NOT emit signals from the skill.

### Step 3: Handle the report

Every step returns `status: ok|warn|blocked`.

| Condition | Action |
|-----------|--------|
| `status: ok` | Present summary (Step 4) |
| `epic: blocked` | **STOP** — run `/rai-epic-start` first |
| `branch: blocked` (`branch-exists`) | **STOP** — ask: resume previous attempt or delete branch? Never auto-resolve |
| `commit: blocked` | Present reason (wrong-branch / staged orphans); wait for the human |
| `backlog: blocked` (multiple candidates) | Present candidates, ask which status means "work started" — engine uses the clarified status; no skill-side CLI call |
| `backlog/bind: warn` | Mention briefly; continue |

### Step 4: Present

```
## Story S{N}.{M}: {name}
**Branch:** {branch} @ {sha}
**Scope:** {1-line summary} · **Jira:** {KEY} → {transitioned}
**Next:** /rai-story-design (PAT-186 — design is not optional)
```

**STOP HERE.** Return your summary to the orchestrator.

## Quality Checklist

- [ ] ONE composite call — no manual bash sequence
- [ ] `blocked` always escalates to the human with options verbatim
- [ ] No telemetry calls from the skill

## References

- Service: `raise_cli/story/open_service.py` · Next: `/rai-story-design`

## Backlog tracker

**Engine behavior** (RAISE-16987): The engine checks `ExecutionContext` to determine mode:
- `mode: pipeline` — engine active; `apply_phase_transition` moves the tracker. No skill call required.
- `mode: standalone` — no active run; tracker is **not** moved automatically.

If standalone (`mode == standalone` via `ExecutionContext`):
```bash
rai backlog transition {key} --point after:story:start
```
