---
name: rai-forward-merge
description: >
  Compute and land the forward-merge chain that propagates a bugfix from an
  older release line to every newer, non-sunset line — one reviewable MR per
  hop, never a direct push to release/* or main.
model: haiku

allowed-tools:
  - Bash
  - Read
  - Write

license: MIT

metadata:
  raise.work_cycle: epic
  raise.frequency: per-propagation
  raise.fase: ""
  raise.prerequisites: "mr-merge"
  raise.next: ""
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "1.0.0"
  raise.visibility: public
  raise.inputs: |
    - source_branch: string, required, the release line the fix landed on
    - work_id: string, required, Jira key, used to name hop branches and MRs
    - dry_run: boolean, optional, default false — print the plan and stop
  raise.outputs: |
    - mr_urls: list[string], one MR per prepared hop, oldest hop first
raise.mastery:
  shu: "Run plan, then one prepare+MR per hop in order; stop and report on the first conflict"
  ha: "Re-run after a HITL conflict resolution; it resumes from the resolved hop"
  ri: "Trigger from a bugfix-close pipeline; report only blockers"
---

# Forward Merge

## Purpose

RAISE-17066 (S4): with two or more concurrent release lines, a bugfix merged
on an older line does not reach a newer line unless someone cherry-picks it
by hand — the non-deterministic step the epic exists to remove. This skill
computes the propagation chain from a source line to every newer, non-sunset
line, prepares each hop's merge without checking out the target, and opens
one MR per hop through the `rai-mr-create` forward-merge contract. Landing
stays with `rai-mr-merge` — this skill only opens MRs.

## Mastery Levels (ShuHaRi)

- **Shu**: Run every step in order; stop and report at the first conflict
- **Ha**: Re-run after resolving a conflict by hand — it resumes from that hop
- **Ri**: Trigger from a bugfix-close pipeline; report blockers only

## Context

**When to use:** immediately after a bugfix MR merges into a release line
that is not the newest — typically called from `/rai-bugfix-close` once the
fix has landed.

**When NOT to use:** propagating feature work (forward-merge only carries
bugfixes forward, per epic scope); merging an already-open forward-merge MR
(`rai-mr-merge` does that); a single-release-line project (`plan` exits 2 —
nothing to propagate).

**Inputs:** `source_branch` (required, e.g. `release/X.Y.Z`), `work_id`
(required, the Jira key), `dry_run` (optional).

## Steps

### Step 1: Compute the chain

```bash
rai forward-merge plan --source "$SOURCE_BRANCH" --work-id "$WORK_ID" -f json
```

- Exit 2 (E013): the source is unknown, sunset, a declared release line is
  malformed, or the manifest has no `branches.release_lines[]` — report the
  stderr message and **stop**. There is nothing this skill can automate on a
  single-release-line project.
- `"hops": []` (exit 0): the source is already the newest line — report "no
  newer release line to propagate to" and **stop**. Nothing to do.
- Otherwise: hops are ordered oldest -> newest. Report any `skipped` sunset
  lines (they are excluded from the chain by design, not silently dropped).

**Verification:** the plan JSON is parsed; hops (possibly empty) and skipped
lines are known.

### Step 2: Dry run stops here

If `dry_run` is true, print the plan (hop count, each `source -> target`,
skipped lines) and **stop** — no branch is created, no MR is opened.

### Step 3: Prepare and open an MR per hop, in order

For each hop, oldest first (`index` ascending):

```bash
rai forward-merge prepare \
  --source "$HOP_SOURCE" \
  --target "$HOP_TARGET" \
  --work-id "$WORK_ID" \
  ${PREV_HOP_BRANCH:+--base-ref "$PREV_HOP_BRANCH"} \
  -f json
```

`--base-ref` is only passed from the second hop onward — its value is the
*previous* hop's `branch` (D3: hops are stacked, so hop N+1 already contains
hop N's content regardless of whether MR N has merged yet).

- Exit 2 (`"status":"conflict"`): print the conflicting paths and the HITL
  recipe from `prepare`'s own output verbatim, then **stop the whole chain**
  — no later hop is attempted or opened as an MR. Re-running this skill
  after the conflict is resolved by hand resumes cleanly (D8).
- `"status":"prepared"` or `"status":"existing"`: continue.

Write the MR title and description with the **Write** tool (never
interpolated into shell source):

- Title: `forward-merge({work_id}): {hop.source} -> {hop.target} [{hop.index}/{total_hops}]`
- Description: hop index/chain position, `commits_ahead` from `prepare`,
  the propagated commit log (`git log --oneline --no-merges
  origin/{hop.target}..{hop.branch}`, capped at 50 lines), and **"Merge
  method: merge commit — do NOT squash (squash breaks propagation
  ancestry)."**

Then run the `rai-mr-create` forward-merge contract with the environment
bound:

```bash
RAI_SOURCE_BRANCH="$HOP_BRANCH" \
RAI_TARGET_BRANCH="$HOP_TARGET" \
RAI_WORK_ID="$WORK_ID" \
RAI_TITLE_FILE="$TITLE_FILE" \
RAI_DESCRIPTION_FILE="$DESCRIPTION_FILE" \
bash <<'CONTRACT'
# ... the RAISE_FORWARD_MERGE_CONTRACT_BEGIN/END block from rai-mr-create ...
CONTRACT
```

Collect the printed MR URL. A non-zero exit here means **no MR was created**
for this hop — report the stderr message and **stop the chain** (do not
attempt later hops on top of an unopened MR).

**Verification:** every hop up to a conflict (or all of them) produced an
MR URL; no ref was pushed for a hop that failed admission or conflicted.

### Step 4: Report and hand off to landing

Print a summary table: hop index, `source -> target`, MR URL (or "stopped —
see above" for hops after a conflict/failure). Instruct the human to land
each MR with `/rai-mr-merge`, **oldest hop first** — merging out of order is
still correct (a newer hop already contains the older hop's content, D3),
but oldest-first keeps the release-line history closest to a straight line.

This skill never merges. It never pushes to `release/*` or `main` directly
— pushes only happen inside the `rai-mr-create` forward-merge contract,
scoped to `forward-merge/*` source branches. It never calls the provider CLI
(`glab`/`gh`) directly.

## Output

| Item | Destination |
|------|-------------|
| Forward-merge chain (hops, skipped lines) | Presented inline |
| One MR URL per successfully prepared hop | Presented inline, oldest first |
| Conflict/failure escalation (recipe, conflicting paths) | Presented inline; chain stops |

## Quality Checklist

- [ ] `plan` ran before any `prepare`; sunset/unknown source stopped the skill (exit 2)
- [ ] `dry_run` prints the plan and stops before any branch or MR is created
- [ ] Hops processed oldest -> newest; hop N+1's `--base-ref` is hop N's branch (D3)
- [ ] A conflict at hop N stops the chain — hops N+1.. are never attempted
- [ ] MR title/description written with the Write tool, never shell-interpolated
- [ ] MR opened only via the `rai-mr-create` forward-merge contract (never a direct provider CLI call)
- [ ] MR description states "merge commit — do NOT squash"
- [ ] No direct push to `release/*`/`main`; no direct `glab`/`gh` call
- [ ] Landing is left to `/rai-mr-merge`, oldest MR first

## References

- Chain/admission logic: `rai forward-merge plan|prepare|admit` (RAISE-17076)
- MR creation: `rai-mr-create`'s forward-merge contract (source-prefix-scoped, D9)
- Landing: `/rai-mr-merge`
- ADR-033 amendment: propagation branch naming, no-squash invariant (RAISE-17066)
