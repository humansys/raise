---
name: rai-mr-create
description: Run full gate suite, push branch to origin, and create GitLab MR. The single point where full tests run before remote.
model: haiku

allowed-tools:
  - Bash
  - Read

license: MIT

metadata:
  raise.work_cycle: epic
  raise.frequency: per-epic
  raise.fase: "9"
  raise.prerequisites: epic-close
  raise.next: null
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "1.0.0"
  raise.visibility: public
  raise.inputs: |
    - source_branch: string, required, current branch
    - target_branch: string, required, e.g. release/3.1.0
    - title: string, required, MR title
    - description: string, optional, MR body
  raise.outputs: |
    - mr_url: string, GitLab MR URL
raise.mastery:
  shu: "Follow all steps, full gate required"
  ha: "Skip gate if implement already ran full suite in same commit"
  ri: "Integrate with release automation"
---

# MR Create

## Purpose

Run the full test/lint/format/types suite, push the branch to origin, and create a GitLab
merge request. This is the **only point** in the story/epic lifecycle where the full suite
runs — all other checks are package-scoped.

**Callable from:** `/rai-epic-close`, hotfix flows, housekeeping MRs, mid-epic pushes.

## Mastery Levels (ShuHaRi)

- **Shu**: Run every gate, explain failures, and only push after all checks pass
- **Ha**: Reuse verified gate results for the same commit when allowed
- **Ri**: Execute the MR path with minimal output and explicit blockers only

## Context

**When to use:** Immediately before pushing a branch to remote and opening an MR.

**When NOT to use:** Per-task or per-story verification — those use scoped `gate-tests --scope`.

## Steps

### Step 1: Full Gate

Run the complete gate suite. Commands come from `.raise/manifest.yaml`; null keys skip automatically:

```bash
rai gate check gate-tests
rai gate check gate-lint
rai gate check gate-format
rai gate check gate-types
```

**Skip condition (Ha/Ri):** If `rai-story-implement` already ran the full package-scoped suite
on the current HEAD commit (signal: `implement/complete` emitted for this commit in this session),
skip `gate-tests` and run only lint/format/types. Gate on commit hash, not elapsed time.

| Condition | Action |
|-----------|--------|
| All gates pass | Continue to Step 2 |
| gate-tests fails | Fix before push — CI will reject the same errors |
| gate-lint / gate-format fails | Fix (usually auto-fixable with `--fix` flag) |
| gate-types fails | Fix — type errors in CI block merge |

<verification>
All four gates pass (or skip logged with commit hash).
</verification>

### Step 2: Rebase onto target (if behind)

Check if the source branch is behind the target:

```bash
git fetch origin {target_branch}
BEHIND=$(git rev-list --count HEAD..origin/{target_branch})
echo "Behind by $BEHIND commits"
```

| Condition | Action |
|-----------|--------|
| Behind > 0 | `git merge origin/{target_branch} --no-edit` — resolve any conflicts |
| Behind = 0 | Continue |

**After merge, ALWAYS re-run Step 1 (full gate).** A clean merge does NOT guarantee test compatibility — the target branch may contain new tests that reference APIs your branch modified (renamed functions, new required attributes, changed query signatures). This is not hypothetical: E3937 had 61 test failures from a clean merge because the target branch brought tests patching `_get_conn` which the epic renamed to `_get_conn_and_pid`.

| Condition | Action |
|-----------|--------|
| Merge brought new commits | Re-run full gate (Step 1) — mandatory, no exceptions |
| Gate fails after merge | Fix before push — these are real incompatibilities |
| Behind = 0 (no merge needed) | Skip re-run — HEAD unchanged |

<verification>
Branch is up-to-date with target. No pending conflicts. Full gate passes POST-MERGE.
</verification>

### Step 3: Push

```bash
git push origin {source_branch}
```

| Condition | Action |
|-----------|--------|
| Push succeeds | Continue to Step 4 |
| Push rejected (non-fast-forward) | `git pull --rebase origin {source_branch}`, then re-push |
| Push rejected (protected branch) | Check branch permissions |

<verification>
Branch pushed to origin.
</verification>

### Step 4: Create MR

Before creating the MR, resolve the rai metadata values (best-effort — omit any value that cannot be determined):

```bash
# Resolve worktree path
RAI_WORKTREE=$(git rev-parse --show-toplevel 2>/dev/null || echo "$PWD")

# Harness is always this runtime
RAI_HARNESS="claude_code"

# Resolve session id from rai context
RAI_SESSION=$(rai session context --sections governance 2>/dev/null \
  | grep -o 'session_id:[[:space:]]*[^[:space:]]*' \
  | awk '{print $2}' \
  | head -1)
```

Build the metadata comment block from the resolved values. Include only keys whose values are non-empty:

```bash
RAI_META="<!-- rai:"
[ -n "$RAI_WORKTREE" ] && RAI_META="$RAI_META worktree=$RAI_WORKTREE,"
[ -n "$RAI_HARNESS" ]  && RAI_META="$RAI_META harness=$RAI_HARNESS,"
[ -n "$RAI_SESSION" ]  && RAI_META="$RAI_META session=$RAI_SESSION,"
RAI_META="${RAI_META%,} -->"   # strip trailing comma
```

Append the block at the **end** of the MR description, after all human-readable content, separated by a blank line. The block must not appear before the human-readable body so that it does not disrupt readability in GitLab's UI.

```bash
FULL_DESCRIPTION="{description}

$RAI_META"

glab mr create \
  --source-branch {source_branch} \
  --target-branch {target_branch} \
  --title "{title}" \
  --description "$FULL_DESCRIPTION" \
  --no-editor
```

If `glab` returns 401: session expired — ask developer to run `glab auth login --hostname gitlab.com` and retry.

If `glab` is unavailable: provide the MR creation URL from `git push` output (GitLab prints it).

Present the MR URL to the developer.

<verification>
MR created. URL presented to developer. Description ends with `<!-- rai: ... -->` block (or was omitted when no values resolved).
</verification>

## Output

| Item | Destination |
|------|-------------|
| Full gate result | Presented inline |
| MR URL | Presented to developer |

## Quality Checklist

- [ ] Full gate (tests + lint + format + types) passes before push — no exceptions
- [ ] Branch up-to-date with target before push
- [ ] MR URL presented to developer
- [ ] NEVER push without passing full gate — CI failure after push wastes everyone's time
- [ ] NEVER run full gate for per-task or per-story scoped checks — use `gate-tests --scope`

## References

- Called by: `/rai-epic-close` (Step 4)
- Also callable from: hotfix flows, housekeeping MRs
- Scoped checks: `/rai-story-implement` (Step 3, Step 5)
