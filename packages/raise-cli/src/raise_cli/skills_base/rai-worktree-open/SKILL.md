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
    - merge_target: string, optional, argument — branch the worktree merges into (default: resolved from the manifest by `rai worktree resolve-base`)
    - work_type: string, optional, argument (default story) — passed to `rai worktree resolve-base --work-type` for release-line routing (RAISE-17066)
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
- `merge_target` (optional) — defaults to the branch resolved by `rai worktree resolve-base` from `.raise/manifest.yaml`
- `work_type` (optional, default `story`) — routing hint for `rai worktree resolve-base --work-type` when the manifest declares multiple `release_lines[]` (RAISE-17066)
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
REPO_ROOT="$(cd "$(git rev-parse --git-common-dir)/.." && pwd)"
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

**Governance note (RAISE-15764):** if `.claude/settings.json` is found, it MUST
be included and copied verbatim — its hooks (PreToolUse/PostToolUse/
UserPromptSubmit/SessionStart) are what makes the new worktree's session
governed. Stripping or omitting it silently produces an ungoverned worktree.

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

Resolve the base branch and ref via the shared resolver (RAISE-15825 Regla
1) — the single source of truth also used by the cockpit's `n` flow, so
base-branch resolution behaves identically everywhere a developer directs
worktree creation:

```bash
RESOLVED="$(rai worktree resolve-base --base "{merge_target}" --work-type "{work_type}" --project "$REPO_ROOT" -f json)" \
  || { echo "blocked: target branch ambiguous — pass merge_target or fix_version, or correct branches.release_lines"; exit 1; }
MERGE_TARGET="$(echo "$RESOLVED" | python3 -c "import json,sys; print(json.load(sys.stdin)['data']['branch'])")"
BASE_REF="$(echo "$RESOLVED" | python3 -c "import json,sys; print(json.load(sys.stdin)['data']['base_ref'])")"
```

The resolver handles, in order: (1) an explicit `merge_target` argument used
verbatim; (2) otherwise `RAISE_DEVELOPMENT_BRANCH` env, then the manifest's
declared topology — `branches.release_lines[]` (routed by `{work_type}` /
`fix_version`) or, in legacy single-line mode, `branches.development` —
resolved via `resolve_target()` (RAISE-17066), never inferred by sorting
`origin/release/*`; (3) if the resolved branch is currently checked out in
a sibling worktree — possibly local-only/unpushed — bases directly off that
local branch instead of fetching `origin` (a stale or absent remote ref
would otherwise silently drop the sibling's unpushed commits). It never
hard-blocks on divergence — worst case is a warning. Present any
`data.warnings` from `$RESOLVED` to the developer verbatim.

| Condition | Action |
|-----------|--------|
| `status: ok` or `warn` | Continue below using `$MERGE_TARGET` / `$BASE_REF`. |
| `status: blocked` (ambiguous target, e.g. unresolvable `fix_version` or no active release line) | **STOP** — show `data.warnings` verbatim and ask the developer to pass an explicit `merge_target` or `fix_version`, or fix `branches.release_lines` in the manifest. Do NOT guess. |

Ensure the `.worktree/` parent directory exists and is gitignored locally:

```bash
mkdir -p "${REPO_ROOT}/.worktree"
grep -qxF '.worktree/' "${REPO_ROOT}/.git/info/exclude" \
  || echo '.worktree/' >> "${REPO_ROOT}/.git/info/exclude"
```

Create the worktree with a new branch based on `$BASE_REF` (already
resolved above — no further fetch needed):

```bash
git worktree add "$WORKTREE_PATH" -b "{branch}" "$BASE_REF"
```

If the branch already exists in git, present an error and stop:

```
Error: Branch {branch} already exists.
Either use a different branch name or check out the existing branch:
  git worktree add {WORKTREE_PATH} {branch}   (without -b)
```

**Post-creation ancestry check** — verify the new worktree is actually based
on `$BASE_REF` (prevents silent divergence when resolution went wrong).
Checked against `$BASE_REF` itself, not `origin/$MERGE_TARGET` — when the
resolver used a local sibling-worktree branch (case 3 above), `$BASE_REF`
IS the local branch name, and no corresponding remote ref may exist at all:

```bash
cd "$WORKTREE_PATH"
if ! git merge-base --is-ancestor "$BASE_REF" HEAD 2>/dev/null; then
  ACTUAL_BASE=$(git log --oneline -1 HEAD)
  echo "ERROR: Worktree HEAD is not a descendant of $BASE_REF"
  echo "  Expected base: $BASE_REF"
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
`git merge-base --is-ancestor "$BASE_REF" HEAD` succeeds inside the worktree.
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

**Graph awareness (RAISE-16743)** — a freshly created worktree has its own
checkout-scoped graph partition (ADR-145), separate from the main checkout's,
and it starts empty (`never_built`). Do **not** run `rai graph build` here
automatically — on large projects a build can take a long time, and
provisioning must stay fast. `/rai-session-start` (run next, per the
briefing below) already surfaces a WARNING if this worktree's graph is
never-built or stale. If the developer wants semantic search available
immediately, mention that they can run `rai graph build` themselves once
inside the new worktree.

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

This worktree's knowledge graph is empty until built — run
`rai graph build` inside it for semantic search (rai graph query/context),
or let the first `/rai-session-start` remind you.

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
