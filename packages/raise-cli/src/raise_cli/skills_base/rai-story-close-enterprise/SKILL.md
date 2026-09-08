---
name: rai-story-close-enterprise
description: Merge story branch to dev and update tracking. Use after story review.

allowed-tools:
  - Read
  - Edit
  - Write
  - Grep
  - Glob
  - "Bash(rai:*)"
  - "Bash(git:*)"

license: MIT

metadata:
  raise.work_cycle: story
  raise.frequency: per-story
  raise.fase: "8"
  raise.prerequisites: story-review
  raise.next: ""
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "4.0.1"
  raise.visibility: public
  raise.inputs: |
    - retrospective_md: file_path, required, previous_skill
    - tests_passing: boolean, required, cli
    - dev_branch: string, required, config
  raise.outputs: |
    - merge_commit: string, git
raise.mastery:
  shu: "Explain each gate and the merge target before closing"
  ha: "Present only blocked/warn signals"
  ri: "Tool call → one-line confirmation → next"
---

# Story Close

## Purpose

Close a story in ONE composite call. The deterministic ritual (retro gate,
hygiene, 3-tier merge-target resolution, --no-ff merge, branch cleanup,
worktree restore, Done transition) runs in `raise-cli` — this skill keeps
only the judgment gates (ADR-093 / ADR-024).

## Steps

### Pipeline Context Check (RAISE-10715)

Before executing any step, verify this skill was invoked via the pipeline engine:

1. Check if `Run ID:` appears in the context above (injected by `pipeline/prompt.py`)
2. If **present**: continue silently — pipeline is orchestrating
3. If **absent**: **STOP and present HITL gate:**

> **Standalone execution detected.** This skill is running outside the pipeline engine.
> Prior phases (implement, quality review, architecture review) may have been skipped.
>
> Options:
> 1. Continue anyway (acknowledge that prior phases were skipped)
> 2. Abort and investigate why the pipeline engine is not orchestrating

Wait for the user's explicit choice before proceeding. This gate fires even in Ri mode — standalone execution is a signal of broken infrastructure, not a routine gate.

### Step 1: Judgment gates (before the call)

These need human/LLM criteria — they are NOT absorbed by the tool:

1. **Story-close gates** — `rai gate check --point before:story:close`.
   Do not use `rai gate check --all` here: `--all` includes release/publish
   gates such as coverage, eval, full tests, and integration checks that are
   intentionally too broad for story close on a busy developer runner.
   If implement/complete already ran on this commit, trust its scoped
   tests/lint/format/types evidence for code quality; story close validates
   close-specific governance only.
2. **AR gate** — verification only. The P1 drift / P2 Beck-R2 / P3 convention
   checklist runs in `/rai-story-review`, which writes the session-scoped
   attestation marker as its output. Close never creates or removes that
   marker itself — attesting and verifying in the same command let the gate
   pass unconditionally (RAISE-14277 / ADR-130: attestation and verification
   must not be the same actor at the same instant). This step only checks:
   ```bash
   rai gate check gate-ar-story
   ```
   Escape hatch (XS/docs):
   ```bash
   RAISE_AR_SKIP_REASON="<reason>" rai gate check gate-ar-story
   ```

### Step 2: Close (one call)

Use the `raise_story_close_full` MCP tool with story_id="S{N}.{M}",
slug="{story-slug}", epic_dir="e{N}-{name}", jira_key="{KEY}",
merge_summary="S{N}.{M}: {name} — {1-line}", cwd="{worktree_path}".

CLI fallback (ADR-084): `rai story close --story-id S{N}.{M} --slug {slug}
--epic-dir e{N}-{name} --jira-key {KEY} --summary "..." -f json`

Merge target resolves worktree DB → `worktree-e{N}*` branch → dev branch.
Telemetry is emitted server-side — do NOT emit signals from the skill.

### Step 3: Handle the report

| Condition | Action |
|-----------|--------|
| `status: ok` | Continue to Step 4 |
| `retro: blocked` | **STOP** — run `/rai-story-review` first, no exceptions |
| `hygiene: blocked` (staged orphans) | **STOP** — present `discard / stash / keep`; never auto-resolve |
| `merge: blocked` (`merge-conflict`) | Merge was aborted, repo is clean. Resolve on story branch, retry |
| `backlog: blocked` (multiple candidates) | Present candidates, ask which means "done" |
| `backlog: blocked` (transition failed / fixVersion failed) | **STOP** — Jira must not diverge from git; fix the sync and retry |
| `cleanup/restore: warn` | Mention; fix manually if needed |

> **Jira-sync enforcement (RAISE-10966)** for story close lives in tested code,
> not this skill text: `raise-cli`'s `transition_backlog(kind="done")` blocks on
> a failed Done transition and assigns `fixVersion` = active release. A `backlog:
> blocked` report means that invariant tripped — do not log-and-continue.

### Step 4: Epic scope update (judgment)

Mark the story complete in `work/epics/e{N}-{name}/scope.md` (checkbox +
progress table) and commit on the merge target.

> **Standalone story only** (epic_dir vacío): verifica que el worktree refleje
> el workitem correcto tras el cierre:
> ```bash
> rai worktree list   # confirmar workitem_id y status del worktree activo
> ```
> (El comando mission accomplish fue eliminado en ADR-130 — el binding vive en
> `worktrees.workitem_id`; no existe concepto de "objetivos de misión".)
> En stories dentro de una épica, esto se hace en `/rai-epic-close` Step 5.

### Step 4.5: Regenerate skills catalog if skills changed [G]

Check whether any skill files changed in this story. If so, regenerate
`docs/skills/index.md` (and the ES mirror) and commit if dirty.

```bash
# RAISE-17066: declared, never inferred — CI env > registered worktree target > manifest. Fail loud.
DEV_BRANCH="${RAISE_DEVELOPMENT_BRANCH:-$(rai worktree context --field merge_target 2>/dev/null || true)}"
[ -n "$DEV_BRANCH" ] || DEV_BRANCH="$(rai manifest env | python3 -c "import json,sys; print(json.load(sys.stdin)['branches']['development'])")"
[ -n "$DEV_BRANCH" ] || { echo "ERROR: cannot resolve target branch — set branches.development in .raise/manifest.yaml"; exit 1; }
SKILLS_CHANGED=$(git diff --name-only "$(git merge-base HEAD "${DEV_BRANCH}")..HEAD" \
  | grep -E "skills_base/|\.claude/skills/|\.agent/skills/" | head -1)
if [ -n "$SKILLS_CHANGED" ]; then
  python3 scripts/generate_skills_catalog.py
  DIRTY=$(git status --short docs/skills/ docs/es/skills/)
  if [ -n "$DIRTY" ]; then
    git add docs/skills/ docs/es/skills/
    git commit -m "docs: regenerate skills catalog after skill changes

Co-Authored-By: Rai <rai@humansys.ai>"
  fi
fi
```

Failure (script exits non-zero): stop and report; do not continue.

### Step 5: Present

```
## Story S{N}.{M} closed
**Merged:** {branch} → {target} @ {sha} ({tier})
**Jira:** {KEY} → {transitioned} · **Cleanup:** {deleted}
```

**STOP HERE.** Return your summary to the orchestrator.

## Quality Checklist

- [ ] Gates + AR review BEFORE the composite call
- [ ] `blocked` always escalates with options verbatim
- [ ] Epic worktree never left on the dev branch (tool restores it)

## References

- Service: `raise_cli/story/close_service.py` · Complement: `/rai-story-start`

## Backlog tracker

**Engine behavior** (RAISE-16987): The engine checks `ExecutionContext` to determine mode:
- `mode: pipeline` — engine active; `apply_phase_transition` moves the tracker. No skill call required.
- `mode: standalone` — no active run; tracker is **not** moved automatically.

If standalone (`mode == standalone` via `ExecutionContext`):
```bash
rai backlog transition {key} --point after:story:close
```
