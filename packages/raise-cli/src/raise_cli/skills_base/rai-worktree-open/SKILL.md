---
name: rai-worktree-open
description: Open a new git worktree with full environment setup. Use to start parallel story work.
model: haiku

allowed-tools:
  - Read
  - Write
  - "Bash(git:*)"
  - "Bash(rai:*)"
  - "Bash(mkdir:*)"
  - "Bash(realpath:*)"
  - "Bash(grep:*)"
  - "Bash(find:*)"

license: MIT

metadata:
  raise.work_cycle: utility
  raise.frequency: per-worktree
  raise.fase: "setup"
  raise.prerequisites: "S4325.1"
  raise.next: "rai-session-start"
  raise.gate: ""
  raise.adaptable: "true"
  raise.version: "1.0.0"
  raise.visibility: public
  raise.inputs: |
    - topic: string, optional, argument — descripción libre del trabajo (e.g. "backlog Jira integration")
      slug = kebab-case del topic; branch = feature/{slug}
    - slug: string, optional, argument — worktree identifier explícito (omitir para inferir de topic)
    - branch: string, optional, argument — branch name explícito (omitir para inferir de topic)
    - merge_target: string, optional, argument — branch the worktree merges into (default: branches.development from manifest)
    - stories: string, optional, argument — comma-separated Jira keys (e.g. RAISE-4331,RAISE-4332)
---

# rai-worktree-open

## Purpose

Create a fully-configured sibling git worktree: correct branch, environment files
propagated, registered in the project DB, and a paste-ready briefing for the agent
— all in one invocation.

## Mastery Levels (ShuHaRi)

- **Shu**: Follow all steps, explain what each one does
- **Ha**: Fast-path when `.worktreeinclude` already exists (skip wizard)
- **Ri**: Single-pass execution, minimal output, briefing only

## Context

**When to use:** Starting parallel story work in a new worktree.

**When to skip:** Worktree already created and registered.

**Inputs:**
- `topic` (optional) — descripción libre del trabajo; `slug` y `branch` se infieren de ella
- `slug` (optional) — worktree identifier explícito; path becomes `.worktree/raise-commons-{slug}/`
- `branch` (optional) — new git branch to create in the worktree
- `merge_target` (optional) — defaults to `branches.development` from `.raise/manifest.yaml`
- `stories` (optional) — comma-separated Jira keys to associate with this worktree

If neither `topic` nor `slug`+`branch` are provided, ask the developer before proceeding.

## Steps

### Step 0: Infer slug and branch (skip if both provided explicitly)

If `slug` and `branch` are both present as explicit arguments, skip this step entirely.

Otherwise, derive them from the `topic` input (the free-text description of the work):

1. **slug** = kebab-case of topic: lowercase, spaces→dashes, drop special characters, keep only `[a-z0-9-]`, truncate to 50 chars.
   - `"backlog Jira integration"` → `backlog-jira-integration`
   - `"worktree for story RAISE-4330"` → `worktree-for-story-raise-4330`

2. **branch** = `feature/{slug}` unless the topic explicitly names a different convention
   (e.g. an epic branch like `e4325/rai-backlog`).

3. **Propose in one line and execute immediately** — do NOT ask for confirmation unless:
   - The derived path `{WORKTREE_PATH}` already exists → stop, present collision error (Step 1 handles it)
   - A story key is mentioned but appears incomplete (e.g. `RAISE-43`) → ask once for the full key

Example inline proposal:
> Inferring: slug=`backlog-jira-integration`, branch=`feature/backlog-jira-integration`. Proceeding…

<verification>
`slug` and `branch` are defined — either from explicit arguments or inferred from topic.
No confirmation prompt unless real ambiguity detected.
</verification>

### Step 1: Guard

Derive the worktree path and verify it does not already exist.

```bash
REPO_ROOT="$(git rev-parse --show-toplevel)"
REPO_NAME="$(basename "$REPO_ROOT")"
WORKTREE_PATH="${REPO_ROOT}/.worktree/${REPO_NAME}-{slug}"
```

Check if the path already exists (either as a registered worktree or as a
plain directory):

```bash
git worktree list --porcelain | grep -q "^worktree $WORKTREE_PATH$" || [ -d "$WORKTREE_PATH" ]
```

If the path is already in use, present this to the developer and stop:

```
Error: A worktree already exists at {WORKTREE_PATH}

Options:
  • Use a different slug
  • Remove the existing worktree: git worktree remove {WORKTREE_PATH} [--force]
```

Do not proceed until the conflict is resolved.

<verification>
`{WORKTREE_PATH}` is free. Confirmed that `git worktree list --porcelain` does not
contain that path.
</verification>

### Step 2: Setup Wizard (fallback — first time only)

> **Note:** rai init generates `.worktreeinclude` automatically with the RaiSE defaults
> for all supported agents (Claude, Hermes, Codex). This wizard only runs if the file is
> absent (e.g., existing project not yet re-initialized, or manual deletion).

Check whether `.worktreeinclude` exists in the repo root:

```bash
[ -f .worktreeinclude ] && echo "EXISTS" || echo "ABSENT"
```

**If EXISTS** — skip this step entirely and continue to Step 3.

**If ABSENT** — run the one-time setup wizard:

**Layer 1: detect recommended candidates** (check each against what exists):

```bash
for f in .env .env.local .mcp.json ".hermes/config.yaml" \
          ".claude/settings.local.json" ".claude/settings.json" ".venv/"; do
  [ -e "$f" ] && echo "FOUND $f"
done
```

Present the found files to the developer in the conversation. Default selection
is everything found except `.venv/` (large directory). Offer to show the full
gitignored file list if they want more options.

Example framing (adapt to your agent's conversational style):

> `.worktreeinclude` not found — I need to set it up before opening the worktree.
>
> Found these gitignored files that are typically propagated:
>   1. `.env`
>   2. `.mcp.json`
>   3. `.claude/settings.local.json`
>   4. `.venv/`  (directory — will be symlinked, saves space)
>
> There may be other gitignored files in this repo. Want me to show the full list?
>
> Which ones to include? Default: 1, 2, 3 (Enter to confirm, or list numbers):

**Layer 2 (only if developer asks for full list):**

```bash
EXCLUDE="__pycache__|dist/|build/|egg-info|htmlcov|\.coverage|pytest_cache\
|node_modules|target/|\.raise/|\.rai-state/|dev/transcripts"
grep -v "^#" .gitignore | grep -v "^$" | grep -Ev "$EXCLUDE" | while read p; do
  [ -e "$p" ] && echo "$p"
done
```

Present additional entries not already shown in Layer 1. Developer can add them
to the selection.

**AGENTS.md note:** If `AGENTS.md` appears in the list, note that it is a
generated file managed by rai init — it should not be copied to worktrees
directly. Skip it silently.

**Write `.worktreeinclude`** with the developer's selection using the Write tool.
One entry per line. Directories should end with `/` to signal symlink behavior.
Include a brief header comment.

<verification>
`.worktreeinclude` exists in the repo root (either it was already there or the
wizard just created it).
</verification>

### Step 3: git worktree add

Resolve `merge_target`. If not provided as argument, read from manifest:

```bash
MERGE_TARGET="${merge_target:-$(grep 'development:' .raise/manifest.yaml | awk '{print $2}' | tr -d ' ')}"
```

**Reconcile against remote (RAISE-14694).** The local manifest
`branches.development` is per-worktree checked-out config and silently goes stale
when a new release branch opens; a worktree based on a stale target silently
merges to an obsolete branch. When `merge_target` was NOT passed explicitly,
cross-check the manifest value against the newest remote release branch:

```bash
git fetch origin
REMOTE_DEV="$(git branch -r --list 'origin/release/*' | sed 's|.*origin/||' | sort -V | tail -1)"
```

| Condition | Action |
|-----------|--------|
| `merge_target` passed explicitly, or no `origin/release/*` exists | Keep `MERGE_TARGET` as resolved above. |
| `MERGE_TARGET` == `REMOTE_DEV` | Keep it. |
| `MERGE_TARGET` != `REMOTE_DEV` | **WARN** and default to remote-latest: "⚠ Local manifest has `${MERGE_TARGET}`, remote latest is `${REMOTE_DEV}`. Using `${REMOTE_DEV}`. Sync your manifest: `sed -i 's/development: .*/development: ${REMOTE_DEV}/' .raise/manifest.yaml && git add .raise/manifest.yaml && git commit -m 'chore: sync manifest dev branch'`." Set `MERGE_TARGET="$REMOTE_DEV"` unless the developer explicitly overrides. |

Ensure the `.worktree/` parent directory exists and is gitignored locally:

```bash
mkdir -p "${REPO_ROOT}/.worktree"
grep -qxF '.worktree/' "${REPO_ROOT}/.git/info/exclude" \
  || echo '.worktree/' >> "${REPO_ROOT}/.git/info/exclude"
```

Create the worktree with a new branch based on `origin/<merge_target>`
(stateless base, RAISE-15556). Fetch the merge target unconditionally and base
on the remote ref — the local `<merge_target>` branch may silently lag the
remote, and basing on it creates a stale worktree:

```bash
git fetch origin "$MERGE_TARGET"
git worktree add "$WORKTREE_PATH" -b "{branch}" "origin/$MERGE_TARGET"
```

If the branch already exists in git, present an error and stop:

```
Error: Branch {branch} already exists.
Either use a different branch name or check out the existing branch:
  git worktree add {WORKTREE_PATH} {branch}   (without -b)
```

**Post-creation ancestry check** — verify the new worktree is actually based on
the intended merge target (prevents silent divergence when MERGE_TARGET resolves
to the wrong branch). Checked against `origin/<merge_target>`, not the local
branch — the local ref could be stale and make this check trivially true:

```bash
cd "$WORKTREE_PATH"
if ! git merge-base --is-ancestor "origin/$MERGE_TARGET" HEAD 2>/dev/null; then
  ACTUAL_BASE=$(git log --oneline -1 HEAD)
  echo "ERROR: Worktree HEAD is not a descendant of origin/$MERGE_TARGET"
  echo "  Expected base: origin/$MERGE_TARGET"
  echo "  Actual HEAD:   $ACTUAL_BASE"
  echo ""
  echo "This means the worktree was created on the wrong base branch."
  echo "Remove it and retry with the correct merge_target:"
  echo "  git worktree remove $WORKTREE_PATH"
  # Return to repo root
  cd "$REPO_ROOT"
  exit 1
fi
cd "$REPO_ROOT"
```

| Condition | Action |
|-----------|--------|
| Ancestry check passes | Continue to Step 4 |
| Ancestry check fails | **STOP** — present error, do NOT register the worktree |

<verification>
`git worktree list` shows `{WORKTREE_PATH}` with branch `{branch}`.
`git merge-base --is-ancestor "origin/$MERGE_TARGET" HEAD` succeeds inside the worktree.
</verification>

### Step 4: Register + Briefing

Register the worktree in the project database and propagate `.worktreeinclude`
entries in a single command:

```bash
ABS_PATH="$(realpath "$WORKTREE_PATH")"

STORIES_ARG=""
[ -n "{stories}" ] && STORIES_ARG="--stories {stories}"

MISSION_ARG=""
[ -n "{mission}" ] && MISSION_ARG="--mission {mission}"

rai worktree register \
  --name "{slug}" \
  --path "$ABS_PATH" \
  --branch "{branch}" \
  --merge-target "$MERGE_TARGET" \
  $STORIES_ARG \
  $MISSION_ARG
```

Verify the registration succeeded:

```bash
rai worktree context --name "{slug}"
```

Present the briefing to the developer:

```
✓ Worktree ready

  Path:    {ABS_PATH}
  Branch:  {branch} → {MERGE_TARGET}
  Stories: {stories or "—"}

Enter the worktree now — do not skip this step:

  Claude Code  → call EnterWorktree with path: {ABS_PATH}
  Hermes/Codex → cd {ABS_PATH}

Note: .envrc/direnv only auto-activates in interactive shells. In
non-interactive/agent shells (Codex exec_command, CI, scripts), use
"uv run <cmd>" — it resolves the worktree's own venv cross-platform without
needing direnv or an interactive shell.

Then run /rai-session-start
```

<verification>
`rai worktree context --name {slug}` returns the expected branch and merge_target.
`.worktreeinclude` entries propagated (files copied, directories symlinked).
Briefing printed with correct absolute path.
</verification>

## Output

| Artifact | When |
|----------|------|
| Worktree path | Always |
| Branch name | Always |
| Agent briefing | After successful setup |

## Quality Checklist

- [ ] Worktree path is unique before creation
- [ ] Branch and merge target are explicit
- [ ] Environment files from `.worktreeinclude` are copied when configured
- [ ] Worktree registration is verified or failure is reported

## References

- CLI: `git worktree --help`
- CLI: `rai worktree --help`
- Config: `.raise/manifest.yaml`
