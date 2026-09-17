---
name: rai-mr-merge
description: Bring an open merge request up to date with its target, wait for CI to go green, and merge it through the SCM adapter. The single point where a branch lands.
model: haiku

allowed-tools:
  - Bash
  - Read

license: MIT

metadata:
  raise.work_cycle: epic
  raise.frequency: per-mr
  raise.fase: "10"
  raise.prerequisites: mr-create
  raise.next: null
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "1.0.0"
  raise.visibility: public
  raise.inputs: |
    - mr_url: string, required, the MR/PR to merge
    - source_branch: string, required, the MR's source branch
    - target_branch: string, required, e.g. release/X.Y.Z
  raise.outputs: |
    - merged: boolean, the MR is merged and the source branch deleted
raise.mastery:
  shu: "Run all five phases in order; never merge without a green CI verdict"
  ha: "Batch several MRs in dependency order, one worktree each, phases unchanged"
  ri: "Integrate with release automation and queue-based merge trains"
---

# MR Merge

## Purpose

Land an MR that already exists: bring it up to date with its target, resolve the
conflicts that are known to be mechanical, wait for CI, and merge — through the
adapter, never through a hand-typed `glab`/`gh` call.

## Mastery Levels (ShuHaRi)

- **Shu**: Run every phase; never merge without a green CI verdict
- **Ha**: Batch several MRs in dependency order, one worktree each, phases unchanged
- **Ri**: Drive from release automation, reporting blockers only

## Context

**When to use:** an MR is open, reviewed, and ready to land. Callable from
`/rai-story-close`, `/rai-epic-close`, batch merge sessions, and hotfix flows.

**When NOT to use:** creating the MR (`rai-mr-create`) or checking work in progress
(`gate-tests --scope`).

## Pipeline Contract

Five ordered phases. Each phase's `<verification>` block is the entry condition of the next.

| # | Phase | Produces the evidence that | Entry condition |
|---|-------|----------------------------|-----------------|
| 1 | `gate` | the branch is mergeable at all | — |
| 2 | `rebase` | the branch carries the target's commits | phase 1 verified |
| 3 | `push` | origin has what CI will build | phase 2 verified |
| 4 | `ci-wait` | CI ran on the merged content and passed | phase 3 verified |
| 5 | `merge` | the MR is merged and the branch cleaned up | phase 4 verified |

**No phase may be skipped or reordered.** Phase 4 in particular cannot move before
phase 3: CI that ran on the pre-merge tree has not tested what is about to land, and
that is the failure this pipeline exists to prevent. Phases 4 and 5 are a single
command so the ordering between them cannot be got wrong by an agent reading steps
out of order.

## Steps (Pipeline Phases)

### Phase 1/5 — `gate`: Mergeability checks

Dependency-free checks only. **No local type/lint/test run happens here** — CI owns that
verdict (epic design D7). Replicating the gate suite inside a throwaway worktree needs
the whole toolchain installed there, and a gate that is sometimes skipped because the
toolchain was missing is not a gate.

```bash
git fetch origin {target_branch}
BEHIND=$(git rev-list --count HEAD..origin/{target_branch})
echo "Behind target by $BEHIND commits"
git diff --check   # conflict markers already committed — a merge cannot fix these
```

If `git diff --check` reports markers, STOP: a `<<<<<<<` was committed and must be
fixed on the branch. Otherwise continue — phase 2 is a no-op when `$BEHIND` is 0.

<verification>
`git diff --check` is silent. `$BEHIND` is known.
</verification>

### Phase 2/5 — `rebase`: Merge the target in

```bash
git merge origin/{target_branch} --no-edit
if [ -n "$(git diff --name-only --diff-filter=U)" ]; then
  rai scm resolve-conflicts
  case $? in
    0) git commit --no-edit ;;                 # every conflict had a rule
    2) echo "Conflicts remain — resolve manually, git add, then git commit" ;;
    1) echo "ERROR .raise/conflict-resolution.yaml is invalid — fix it first" ;;
  esac
fi
```

**Never rebase here despite the phase name.** `rai scm resolve-conflicts` is
direction-sensitive: `theirs` means the target branch only because the merge runs on
the source branch. A rebase swaps the sides and every automatic resolution would be
exactly backwards. On exit 1, fix the config — do NOT hand-resolve around it.

<verification>
`git diff --name-only --diff-filter=U` is empty. No merge is in progress.
</verification>

### Phase 3/5 — `push`: Push the merged branch

```bash
git push origin {source_branch}
```

This is what makes phase 4 meaningful: CI must run on the post-merge tree. Pushing
after CI passes would mean the verdict describes a tree that no longer exists. If the
push is rejected as non-fast-forward, `git pull --rebase origin {source_branch}` and
return to phase 2.

<verification>
`git rev-parse HEAD` matches `git rev-parse origin/{source_branch}`.
</verification>

### Phases 4/5 and 5/5 — `ci-wait` + `merge`: One command

```bash
rai scm merge-mr --mr-url {mr_url}
```

Polls the MR's CI status through the adapter and merges only on `success`. Both phases
are one call because the gap between "CI passed" and "merge" is exactly where a
hand-run pipeline goes wrong.

**Fail-closed** — anything that is not `success` blocks the merge and `merge_mr()` is
never reached: failed/cancelled/skipped/manual/blocked (GitLab), failure/neutral/
action_required (GitHub), timeout (default 30 min), and no-CI-configured.

| Exit | Meaning | Action |
|------|---------|--------|
| 0 | Merged, source branch deleted | Report the MR as landed |
| 3 | CI refused or timed out | Read the pipeline, fix the branch, restart at phase 2 |
| 1 | Adapter or provider-CLI error | Message names the cause, including the `glab auth login` / `gh auth login` command when it is auth |

Flags: `--no-delete-source-branch` (default is delete), `--poll-timeout N` (1800),
`--poll-interval N` (30), `--no-ci-override`.

**`--no-ci-override` is a bypass, not a judgement call.** The adapter Protocol reports
"no CI configured" and "CI ran and failed" as the same `failed`, so the flag skips the
poll entirely rather than trying to tell them apart. Using it on a repository that does
have CI merges an unverified branch. Never reach for it because CI is red.

**Do not fall back to `glab mr merge` or `gh pr merge`** — that is the ad-hoc dispatch
this phase replaced, and it merges without the CI gate.

<verification>
`rai scm merge-mr` exited 0. The MR shows as merged and the source branch is gone.
</verification>

## Output

| Item | Destination |
|------|-------------|
| Behind-count and conflict resolution report | Presented inline |
| CI verdict and merge confirmation | Presented inline (stderr of `rai scm merge-mr`) |

## Quality Checklist

- [ ] All five phases ran in order, each entered only after the previous one verified
- [ ] Target merged in and pushed BEFORE the CI wait — CI must judge the post-merge tree
- [ ] Conflicts resolved via `rai scm resolve-conflicts`, never by rebasing
- [ ] Merged via `rai scm merge-mr` — NEVER `glab`/`gh` directly, which skips the CI gate
- [ ] `--no-ci-override` used only where there is genuinely no CI, never to pass a red pipeline
- [ ] Source branch deleted after merge
- [ ] NEVER merge on a non-`success` verdict — exit 3 means fix the branch, not retry the merge

## References

- Preceded by: `rai-mr-create` (opens the MR, runs the full local gate)
- Called by: `/rai-story-close`, `/rai-epic-close`, batch merge sessions
- Conflict policy: `.raise/conflict-resolution.yaml` (RAISE-16772)
- Adapter contract: ADR-2026-08-29 `ScmAdapter` (RAISE-16773)
