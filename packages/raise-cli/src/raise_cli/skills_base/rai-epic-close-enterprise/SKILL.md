---
name: rai-epic-close-enterprise
description: Close epic with retrospective, push, and merge request. Use after all stories done.

allowed-tools:
  - Read
  - Edit
  - Grep
  - Glob
  - "Bash(rai:*)"
  - "Bash(git tag *)"
  - "Bash(git add *)"
  - "Bash(git commit *)"
  - "Bash(git status *)"

license: MIT

metadata:
  raise.work_cycle: epic
  raise.frequency: per-epic
  raise.fase: "9"
  raise.prerequisites: all stories complete
  raise.next: ""
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "3.2.0"
  raise.visibility: public
  raise.inputs: |
    - scope: file_path, required, previous_skill
    - all_retrospectives: boolean, required, git
    - dev_branch: string, required, config
  raise.outputs: |
    - retrospective: file_path, file
    - tag: string, git
  raise.aspects: introspection
  raise.introspection:
    phase: epic.close
    context_source: all epic artifacts
    affected_modules: []
    max_tier1_queries: 2
    max_jit_queries: 3
    tier1_queries:
      - "retrospective patterns for {domain} epics"
      - "process improvement patterns from similar epics"
---

# Epic Close

## Purpose

Complete an epic by conducting a retrospective, tagging the milestone, and updating tracking. No branch merge needed — stories already merged to the development branch during story-close.

## Mastery Levels (ShuHaRi)

- **Shu**: Follow all steps, complete full retrospective template
- **Ha**: Adjust retrospective depth based on epic complexity
- **Ri**: Integrate with release workflows, automate metrics extraction

## Context

**When to use:** All stories complete and merged to `{dev_branch}`. Ready to close the epic lifecycle.

**When to skip:** Epic abandoned (document why, update backlog as "Abandoned").

**Inputs:** Epic scope document, all story retrospectives, passing test suite.

**Branch config:** Read `branches.development` from `.raise/manifest.yaml` for `{dev_branch}`. Default: `main`.

## Steps

### Pipeline Context Check (RAISE-10715)

Before executing any step, verify this skill was invoked via the pipeline engine:

1. Check if `Run ID:` appears in the context above (injected by `pipeline/prompt.py`)
2. If **present**: continue silently — pipeline is orchestrating
3. If **absent**: **STOP and present HITL gate:**

> **Standalone execution detected.** This skill is running outside the pipeline engine.
> Prior phases (docs, journal) may have been skipped.
>
> Options:
> 1. Continue anyway (acknowledge that prior phases were skipped)
> 2. Abort and investigate why the pipeline engine is not orchestrating

Wait for the user's explicit choice before proceeding. This gate fires even in Ri mode — standalone execution is a signal of broken infrastructure, not a routine gate.

### PRIME (mandatory — do not skip)

Before starting Step 1, you MUST execute the PRIME protocol:

1. **Chain read**: Read this epic's `scope.md` if present (rai-epic-plan appends the Implementation Plan / Milestones / Sequencing Risks sections there), and each completed story's `work/epics/e{N}-{name}/stories/s{N}.{M}-retrospective.md` if present. This provides context for the retrospective. If `scope.md` or story retrospectives are missing (legacy epic), note and continue.
2. **Graph query**: Execute tier1 queries from this skill's metadata using the `raise_graph_query` MCP tool with `cwd="{project_or_worktree_path}"`. If MCP tools are not available, fall back to:
   ```bash
   rai graph query
   ```
   If graph is unavailable, note and continue.
3. **Present**: Surface retrieved patterns as context. 0 results is valid — not a failure.

### Step 1: Verify Stories Complete + Scope Re-read (mandatory)

**1a. Check all stories are done** in the epic scope document:

```bash
grep -E "^\s*-\s*\[ \]" "work/epics/e{N}-{name}/scope.md"
```

| Condition | Action |
|-----------|--------|
| All stories checked | Continue to 1b |
| Incomplete stories | Complete them first or explicitly descope |

**1b. Scope re-read (mandatory — do not skip)**: open `work/epics/e{N}-{name}/scope.md` and the original epic brief. Go through the **"In scope"** and **"Done when"** sections **item by item** and verify each commitment against observable state of the code. Do not trust "all stories checked ⇒ scope fulfilled" — it's not the same claim.

Pay special attention to commitments with elimination verbs (*"eliminate X"*, *"remove Y"*, *"replace Z with …"*, *"consolidate A and B"*). For each such commitment, answer one of three explicitly in the retrospective:

- **Fulfilled** — reference commit/file showing the removal
- **Descoped** — say why and link to a new epic/story that owns the remaining work
- **Not fulfilled** — stop. Do not close. Either finish the work or explicitly re-scope before closing

This exists because RCA s2092.1 showed E1323 ("eliminate subprocess layer") closed Done while the layer was actually **amplified** — the tools shipped, the tests passed, nobody re-read the scope (pattern `refactor-declared-done-without-sweep` at epic-scale).

> **JIT**: Before descoping decisions, query graph for completion patterns and prior descoping outcomes
> → `aspects/introspection.md § JIT Protocol`

<verification>
All stories marked complete in epic scope AND each "In scope" / "Done when" item re-verified against code. Elimination commitments resolved (fulfilled | descoped-with-link | not-fulfilled-stop).
</verification>

### Step 1.5: Reconcile Jira Child Story Status (RAISE-1847)

Query Jira for child stories that are NOT in Done status:

```bash
rai backlog search "parent = {EPIC_KEY} AND status != Done"
```

| Condition | Action |
|-----------|--------|
| No results (all Done) | Continue to Step 2 |
| Drifted stories found | Present the list and offer resolution (see below) |
| No Jira adapter configured | Warn: "Jira reconciliation skipped — no adapter" and continue |
| No epic Jira key | Warn: "No Jira key for epic — skipping reconciliation" and continue |
| Query fails (network, auth) | Warn: "Jira query failed �� manual check recommended" and continue |

**When drifted stories are found, present:**

```
Jira drift detected: {N} child stories are not in Done status.

  {KEY-1}  {status}  {summary}
  {KEY-2}  {status}  {summary}
  ...

Options:
  1. Batch-transition to Done: rai backlog batch-transition {KEY-1},{KEY-2} done
  2. Descope explicitly (document in retrospective why they're not Done)
  3. Abort epic close and fix the stories first
```

**Do NOT proceed to Step 2 until the user has chosen an option.** This gate prevents silent Jira drift that was found in E1690 audit (5 stories locally done but Backlog in Jira).

<verification>
Jira child stories reconciled: all in Done, or user explicitly descoped with documented reason. (Or no Jira adapter — warned and continued.)
</verification>

### Step 1.6: Reconcile Parent Epic Status Parity (RAISE-10652)

After child reconciliation passes, query the parent epic itself:

```bash
rai backlog get {EPIC_KEY}
```

| Condition | Action |
|-----------|--------|
| Epic is already Done | Continue to Step 2 |
| all child stories are Done but the epic is not | Present the discrepancy and resolve it before continuing |
| Epic status cannot be read | Stop immediately — manual reconciliation required before epic close |

**When the epic is stale-open while all children are Done, present:**

```
Parent status drift detected: all child stories are Done but the epic is not.

Options:
  1. Transition the epic now, then verify the new status
  2. Abort epic close and investigate why the parent stayed open
```

**Do NOT proceed to Step 2** until the parent epic is in Done status or the close is aborted.

<verification>
Parent epic status reconciled: no stale-open epic passes into retrospective/write steps.
</verification>

### Step 2: Write Retrospective

Do **not** run the full suite here — the full gate runs once in Step 4 via `/rai-mr-create`
before push. Trust the scoped gates that passed during story-close.

> **JIT**: Before writing retrospective, query graph for process improvement patterns from similar epics
> → `aspects/introspection.md § JIT Protocol`

Publish retrospective to local path and docs adapter. Use `templates/retrospective.md` as structure, fill from story retrospectives and git history:

Use `raise_docs_write` MCP tool with doc_type="retrospective", title="E{N}: {Epic Name} — Retrospective", content="[content following templates/retrospective.md structure]", output_path="work/epics/e{N}-{name}/retrospective.md", cwd="{project_or_worktree_path}".
If MCP tools are not available, fall back to:
```bash
rai docs write retrospective \
  --title "E{N}: {Epic Name} — Retrospective" \
  --stdin \
  --output-path work/epics/e{N}-{name}/retrospective.md << 'EOF'
[content following templates/retrospective.md structure]
EOF
```

Emit the retrospective as a structured artifact so `epic.yaml`'s `close.validates` (RAISE-11088) can prove — in SQLite, issue-scoped by construction — that THIS epic's own retrospective exists before `close` can complete. A repo-wide `work/epics/**/retrospective.md` glob would be satisfied by ANY epic's retrospective already in the repo (epic directory numbering is not reliably Jira-key-derived); this sqlite record cannot be:

```
raise_artifact_emit(
    artifact_type="retro",
    story_id="{JIRA_KEY}",
    content=<JSON with fields: patterns_learned (list[str]), reinforcements (list[str]), velocity_ratio (optional float), notes (optional str)>,
    cwd="{project_or_worktree_path}"
)
```

**CRITICAL — identifier mismatch risk (same hazard as RAISE-11147's `implement` fix):** `story_id` here MUST be `{JIRA_KEY}` — the pipeline's **issue key** (the same value passed to `pipeline_start`, e.g. `"RAISE-11404"`), **NOT** the `e{N}` directory-number convention used by this step's `output_path` above (epic directories are not reliably Jira-key-derived — e.g. `e3-scaleup-agent` vs `e11404-...`). `epic.yaml`'s sqlite validate branch looks up `artifact_store.exists(run["issue_id"], "retro")`, and `run["issue_id"]` is always the Jira key. Emitting with the directory number instead would make the sqlite lookup never find the artifact, turning `close` into a permanent `artifact_missing` deadlock.

**Note:** The CLI fallback for artifact emission was removed in v3.0.0. MCP tool `raise_artifact_emit` is required. If MCP tools are not available, skip structured artifact emission — the pipeline will require it before `close` can complete.

<verification>
Tests green. Retrospective persisted locally and published via docs adapter. Metrics, patterns, and process insights included. Retro artifact emitted to SQLite, keyed by the epic's Jira issue key.
</verification>

### Step 3: Tag Epic Milestone

Tag the current `{dev_branch}` HEAD to mark epic completion:

```bash
git tag -a "epic/e{N}-complete" -m "Epic E{N}: {Epic Name} complete

Delivered: [key deliverables]
Stories: N stories

Co-Authored-By: Rai <rai@humansys.ai>"
```

Commit retrospective and any final artifacts (scoped to this epic's directory — RAISE-11778: `git add -A` in a shared checkout silently sweeps in unrelated uncommitted work from other sessions):

```bash
git add work/epics/e{N}-{name}/
git commit -m "epic(e{N}): close with retrospective

Co-Authored-By: Rai <rai@humansys.ai>"
```

<verification>
Tag created. Retrospective committed. `git status --short` shows no unrelated files were swept into the commit.
</verification>

### Step 4: Push and Create Merge Request

Invoke `/rai-mr-create` — it runs the full gate suite, rebases onto target if needed,
pushes, and creates the MR. This is the single point where the full test suite runs.

```
/rai-mr-create
  source_branch: {dev_branch}
  target_branch: {main_branch}
  title: "epic(e{N}): {Epic Name}"
  description: |
    ## Epic E{N}: {Epic Name}

    ### Stories delivered
    - S{N}.1: {name}
    ...

    ### Key changes
    - {summary of deliverables}

    Co-Authored-By: Rai <rai@humansys.ai>
```

| Condition | Action |
|-----------|--------|
| Full gate passes | `/rai-mr-create` pushes and creates MR |
| Gate fails | Fix before push — do not skip |
| No release planned | Push dev only via `/rai-mr-create` without MR |

<verification>
Full gate passed via `/rai-mr-create`. Branch pushed. MR URL presented to developer.
</verification>

### Step 5: Update Backlog & Mission

1. Epic close transition is engine-owned (RAISE-15034):
Engine transitions epic to Done via `apply_phase_transition` / terminal-close gate (RAISE-10966).
No skill-initiated transition call required or allowed.
If no Jira key is known, search first to confirm the key:
```bash
rai backlog search "summary ~ '{epic name}'"
```

Then **enforce Jira consistency (RAISE-10966) — blocking, not best-effort**:

1. Derive the active release version from the manifest `branches.development`
   (e.g. `release/3.1.0` → `3.1.0`) and assign it as the fixVersion:
   ```bash
   rai backlog update {JIRA_KEY} -F 'fixVersions=[{"name": "{version}"}]'
   ```
2. Re-read the epic and verify it landed in a Done category:
   ```bash
   rai backlog get {JIRA_KEY}
   ```
   If the status is not in a Done category, or the fixVersion assignment
   failed, **FAIL the close** — do not log-and-continue.

| Condition | Action |
|-----------|--------|
| Jira key known | statuses list → infer → transition |
| No Jira key | search → resolve key → transition |
| Transition fails / not Done on re-read | **FAIL the close** — epic close cannot complete with stale parent status |
| fixVersion assignment fails | **FAIL the close** |

2. **Verify worktree binding (ADR-130):**

The mission CLI was eliminated in ADR-130 — there are no longer "mission objectives" to mark.
The worktree binding survives as `worktrees.workitem_id`. Verify the worktree is correctly
associated with the epic's initiative:

```bash
rai worktree list   # confirm workitem_id reflects the linked initiative
```

If the worktree should be closed after this epic (mission complete), run:
```bash
rai worktree complete   # marks worktree status → closed
```

| Condition | Action |
|-----------|--------|
| Epic is last in this worktree's scope | `rai worktree complete` |
| More epics remain in this worktree | Skip `complete` — worktree stays open |
| No worktree registered | Skip silently |

<verification>
Backlog reflects completion. Worktree status updated if this was the final epic.
</verification>

## Scope Constraints (RAISE-11778)

- **NEVER** run `git reset --hard`, `git clean -fd`, or `git checkout -- .` to resolve an unexpected working tree state — STOP and report instead, it may hold someone else's uncommitted work
- **NEVER** `git add -A` — stage only `work/epics/e{N}-{name}/`

## Output

| Item | Destination |
|------|-------------|
| Retrospective | `work/epics/e{N}-{name}/retrospective.md` |
| Retro artifact | SQLite (`artifact_type=retro`, keyed by Jira issue key) |
| Tag | `epic/e{N}-complete` on `{dev_branch}` |
| Push | `{dev_branch}` pushed to origin |
| Merge request | GitLab MR: `{dev_branch}` → `{main_branch}` (if release) |
| Backlog update | Tracker via rai backlog CLI |

**STOP HERE.** Return your summary to the orchestrator. Do NOT invoke any further skill.

## Quality Checklist

- [ ] All stories complete before closing (gate)
- [ ] Jira child stories reconciled — all Done, or explicitly descoped (RAISE-1847)
- [ ] Tests pass before closing
- [ ] Retrospective captures metrics, patterns, and process insights
- [ ] Epic milestone tagged on `{dev_branch}`
- [ ] Dev pushed to origin with all epic commits
- [ ] Merge request created if targeting main (epic-level MR, not per story)
- [ ] Backlog transition delegated to engine (RAISE-15034); fixVersion assigned via rai backlog update
- [ ] Worktree binding verified (`rai worktree list`); `rai worktree complete` if final epic in this worktree
- [ ] No epic branch to clean up — epics are logical containers
- [ ] NEVER close without retrospective — learnings compound across epics
- [ ] NEVER create per-story MRs — one MR per epic at close time

## References

- Retrospective template: `templates/retrospective.md`
- Previous: All `/rai-story-close` completions
- Backlog: rai backlog CLI
- Next: `/rai-epic-design` for next epic
