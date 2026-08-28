---
allowed-tools:
- Read
- Bash(git:*)
- Bash(rai:*)
- Bash(grep:*)
- Bash(awk:*)
description: Close a git worktree — mark it closed in DB and suggest /rai-mr-create
  if work is ready to ship. Works with or without a registered worktree.
model: haiku
license: MIT
metadata:
  raise.adaptable: 'true'
  raise.fase: close
  raise.frequency: per-worktree
  raise.gate: ''
  raise.inputs: '- (none) — all context auto-detected from CWD and manifest

    '
  raise.next: rai-mr-create
  raise.prerequisites: S4325.1
  raise.version: 1.1.0
  raise.visibility: public
  raise.work_cycle: utility
name: rai-worktree-close
---

# rai-worktree-close

## Purpose

Close the current git worktree: detect context from the DB, mark the worktree
as closed, and suggest `/rai-mr-create` if the work is ready to ship.

The MR is not a mandatory step — closing a worktree does not imply the work is
ready for review. The developer decides when to create the MR.

Works in two modes:
- **Registered worktree** (CWD matches a rai worktree register entry): reads
  `branch` and `worktree_id` from DB, marks closed.
- **Direct flow** (CWD not registered): presents branch context, skips DB step.

## Mastery Levels (ShuHaRi)

- **Shu**: Follow all steps, explain each one
- **Ha**: Fast-path — skip explanation, run commands directly
- **Ri**: Single-pass execution, minimal output

## Context

**When to use:** When you are done with this worktree as a workspace — whether
the work is ready to ship or not.

**When to skip:** Worktree already closed.

**Inputs:** None — all context auto-detected from CWD and manifest.

## Steps

### Step 1: Detect Context

Determine if the current CWD is a registered worktree:

```bash
rai worktree context 2>/dev/null
```

| Result | Action |
|--------|--------|
| Shows `worktree_id`, `branch`, `status: open` | Registered worktree — extract fields |
| Error / CWD not found | Direct flow — log and continue |
| `status: closed` | Already closed — stop with message |

Extract fields for registered worktree:

```bash
WORKTREE_ID=$(rai worktree context --field worktree_id 2>/dev/null)
BRANCH=$(rai worktree context --field branch 2>/dev/null)
```

For direct flow, get the current branch:

```bash
BRANCH=$(git branch --show-current)
```

If `BRANCH` is empty (detached HEAD), stop with:
```
Error: not on a branch. Checkout a branch before closing.
```

Read the development branch from the manifest:

```bash
MANIFEST_DEV=$(grep 'development:' .raise/manifest.yaml | awk '{print $2}' | tr -d ' ')
```

Present detected context to the developer:

```
Context detected:
  Mode:        [registered worktree | direct flow]
  Branch:      {BRANCH}
  Dev branch:  {MANIFEST_DEV}
  Worktree ID: {WORKTREE_ID or "—"}
```

<verification>
`BRANCH` is non-empty. Context presented.
</verification>

### Step 2: Mark Closed (registered worktree only)

Skip this step if running in direct flow (no `WORKTREE_ID`).

```bash
rai worktree complete --name "$WORKTREE_ID"
```

Verify:

```bash
rai worktree context --field status
```

Expected output: `closed`

<verification>
`rai worktree context --field status` returns `closed`.
</verification>

### Step 3: Sync from remote

Skip this step if `--no-rebase` was passed.

```bash
git pull --rebase origin "$MANIFEST_DEV"
```

| Result | Action |
|--------|--------|
| Clean rebase | Show: `✓ Branch is up to date with origin/{MANIFEST_DEV}` — continue to Step 4 |
| Conflict | Hard stop — show recovery instructions below, do NOT proceed to Step 4 |
| Network failure | Warn and continue to Step 4 |
| `--no-rebase` flag | Skip with notice: `⚠ Sync skipped (--no-rebase). Branch may be behind origin/{MANIFEST_DEV}.` |

**On conflict:**

```
✗ Rebase conflict detected.
  To cancel:   git rebase --abort
  To inspect:  git status
  To continue: git rebase --continue
  Then re-run /rai-worktree-close to complete.
```

**On network failure:**

```
⚠ Could not reach origin — sync skipped. Continuing to summary.
```

<verification>
Branch is rebased cleanly onto origin/{MANIFEST_DEV}, OR --no-rebase was passed,
OR network failure was warned. On conflict: execution stopped, Step 4 not shown.
</verification>

### Step 4: Present Summary + Suggest Next Step

Present the close summary and, if work appears ready to ship, suggest
`/rai-mr-create`:

```
✓ Worktree closed

  Branch:      {BRANCH}
  Dev branch:  {MANIFEST_DEV}
  Worktree ID: {WORKTREE_ID} → closed

If the work is ready for review:
  /rai-mr-create
    source_branch: {BRANCH}
    target_branch: {MANIFEST_DEV}
```

For direct flow (no worktree registered):

```
Branch in scope: {BRANCH}
Dev branch:      {MANIFEST_DEV}

If the work is ready for review:
  /rai-mr-create
    source_branch: {BRANCH}
    target_branch: {MANIFEST_DEV}
```

The developer decides whether to run `/rai-mr-create` — do NOT invoke it
automatically.

### Step 5: Check for Active Session

Before physically removing the worktree, verify no session is active.
Closing the container before the content causes CWD mismatch when
`/rai-session-close` runs later (RAISE-5521, RAISE-5563).

```bash
rai session context --field status 2>/dev/null
```

| Result | Action |
|--------|--------|
| `active` | **Stop** — warn: "Active session detected. Close the session first (`/rai-session-close`) before removing this worktree." |
| Empty/error | No active session — proceed to Step 6 |

The correct semantic order is:
1. `/rai-session-close` — while CWD exists
2. `/rai-worktree-close` Step 6 — physical cleanup

The worktree is the container, the session is the content. Content closes before container.

<verification>
No active session in this worktree, OR developer acknowledged and will close session first.
</verification>

### Step 6: Physical Cleanup

Remove the worktree directory and delete the local branch. Must run from the
main repo — `git worktree remove` cannot target the currently checked-out
worktree from within it.

```bash
WORKTREE_PATH=$(pwd)
MAIN_REPO=$(dirname $(git rev-parse --git-common-dir))
```

Check if the remote branch still exists:

```bash
git ls-remote --exit-code origin "$BRANCH" &>/dev/null
```

| Result | Action |
|--------|--------|
| Exit 0 (remote exists) | MR not yet merged — use `-d` (safe delete) |
| Exit non-zero (remote gone) | MR merged and pruned — use `-D` (safe, already merged) |

Execute cleanup:

```bash
git -C "$MAIN_REPO" worktree remove "$WORKTREE_PATH"

if git ls-remote --exit-code origin "$BRANCH" &>/dev/null; then
    git -C "$MAIN_REPO" branch -d "$BRANCH"
else
    git -C "$MAIN_REPO" branch -D "$BRANCH"
fi
```

| Condition | Action |
|-----------|--------|
| `worktree remove` fails (uncommitted changes) | Stop — commit or stash changes first, then re-run |
| `branch -d` fails (not fully merged, remote still exists) | Stop — MR not yet merged. Create MR first via `/rai-mr-create` |
| Both succeed | Worktree closed and workspace cleaned |

<verification>
Worktree directory removed. Local branch deleted. No manual cleanup required.
</verification>

## Output

| Artifact | When |
|----------|------|
| Closure summary | Always |
| MR recommendation | When branch has shippable work |

## Quality Checklist

- [ ] Active session checked before worktree removal
- [ ] Current branch is detected before closing
- [ ] Registered worktree state is updated when available
- [ ] Direct-flow close does not mutate DB state
- [ ] MR creation is suggested, not forced

## References

- CLI: `git worktree --help`
- CLI: `rai worktree --help`
- Skill: `rai-mr-create`
