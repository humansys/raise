---
allowed-tools:
- Read
- Bash(rai:*)
- Bash(git:*)
- Bash(cat:*)
- Bash(ls:*)
description: Connect a repository to the RaiSE server. Detects what's done, guides
  through what's missing.
model: haiku
license: MIT
metadata:
  raise.adaptable: 'true'
  raise.fase: ''
  raise.frequency: once-per-repo
  raise.gate: 4-checkpoint status
  raise.inputs: '- project_root: path, optional (defaults to CWD)

    '
  raise.next: rai-session-start
  raise.outputs: '- server_connection: ~/.rai/server.json

    - manifest: .raise/manifest.yaml

    - registered_repo: on raise-server

    - project_link: on raise-server

    '
  raise.prerequisites: ''
  raise.version: 3.0.0
  raise.visibility: public
  raise.work_cycle: utility
name: rai-onboard-repo
---

# Onboard Repo

## Purpose

Guide a developer through connecting their repository to the RaiSE server. Detect what's already done, show a clear status, and execute only the missing steps. This is the first thing a new developer runs after installing the CLI.

## Mastery Levels (ShuHaRi)

- **Shu**: Walk through every step, explain what each command does
- **Ha**: Show status, execute missing steps with brief confirmation
- **Ri**: Status + auto-execute, report only

## Context

**When to use:** First time setting up a repo with RaiSE, or to verify onboarding is complete.

**When to skip:** Already fully onboarded (all 4 checkpoints pass).

**Key difference from `/rai-project-onboard`:** This skill connects the repo to the server (infrastructure). `/rai-project-onboard` sets up governance (docs, discovery, guardrails).

## Steps

### Step 1: Detect Status (4 Checkpoints)

Run all 4 checks and present a summary before doing anything:

**Check 1 — Server Connection:**
```bash
cat ~/.rai/server.json 2>/dev/null
```
Parse `server_url` and `org_name` from the JSON. If file missing or empty → not connected.

**Check 2 — Project Initialized:**
```bash
ls .raise/manifest.yaml 2>/dev/null
```
If exists, read the `name` field. If missing → not initialized.

**Check 3 — Repository Registered:**
```bash
rai repo list
```
Match the current repo by comparing `git remote get-url origin` against the listed git remote URLs, or by matching the directory name against slugs. If no match → not registered.

**Check 4 — Project Linked:**
```bash
rai project list
```
Check if any project exists that could be linked to this repo. Then verify the link:
```bash
# If the repo slug matches a project slug, it's likely linked (1:1 convention)
```
Note: There is no `rai project get <slug>` command yet to verify links directly. Use the convention that project slug = repo slug as a heuristic. If the project exists with the same slug, assume linked.

**Present the status:**

```
--- Onboarding Status ---
✓ Connected to api.raise.sh (org: humansys)
✓ Project initialized (raise-commons)
✗ Repository not registered on server
✗ Not linked to any project

2 steps remaining. Continue? [Y/n]
```

| Condition | Action |
|-----------|--------|
| All 4 pass | Check graph status (see below), then suggest next steps |
| Some missing | Show status, ask to continue |
| User declines | Exit cleanly |

**When all 4 pass — graph check:**

Even when infrastructure onboarding is complete, the knowledge graph may not exist yet. Before declaring "Already onboarded", check and run graph build+push if missing:

```bash
rai graph build --check 2>/dev/null
```

If `--check` is not available, probe via the graph query CLI (reads the global DB — never open per-project `.db` files directly, S8204.2):

```bash
rai graph query "module" --limit 1 --format compact >/dev/null 2>&1 \
  && echo "GRAPH_OK" || echo "NO_GRAPH"
```

| Condition | Action |
|-----------|--------|
| `GRAPH_OK` | Print "Already onboarded ✓" |
| `NO_GRAPH` | Run Step 5b (graph build + push), then print summary |

This ensures that re-running `/rai-onboard-repo` on an already-onboarded project still completes the graph if it was missed.

<verification>
Status of all 4 checkpoints presented. User confirmed to proceed (or all passed). Graph existence verified.
</verification>

### Step 2: Connect (if missing) — HARD STOP

If Check 1 failed, **do not attempt the device flow**. Print instructions and exit:

```
Not connected to a RaiSE server.

To connect, run:
  rai connect <org-slug>

Your org admin will need to approve the device. Once connected,
run /rai-onboard-repo again to continue.
```

**Exit here.** The device flow requires browser interaction and possibly admin approval — it does not belong inside a skill.

<verification>
If connect missing: instructions printed, skill exited. No device flow attempted.
</verification>

### Step 3: Initialize Project (if missing)

If Check 2 failed:

1. Detect the project name from the directory:
```bash
basename $(git rev-parse --show-toplevel 2>/dev/null || pwd)
```

2. Ask the developer:
```
No RaiSE project found in this directory.
Detected name: raise-commons

Initialize with this name? [Y/n/custom]
```

3. Execute based on response:

| Response | Action |
|----------|--------|
| Y (default) | run init with detected name |
| n | Exit with note: "Run rai init manually when ready" |
| custom text | run init with custom name |

```bash
rai init --name <detected-or-custom> --detect
```

<verification>
`.raise/manifest.yaml` exists after this step.
</verification>

### Step 3b: Auto-configure Adapters (if env vars present)

After project initialization, attempt zero-prompt adapter setup if Atlassian env vars are available:

```bash
# Check if Jira env vars are set
if [ -n "$JIRA_URL" ] && [ -n "$JIRA_API_TOKEN" ] && [ -n "$JIRA_USERNAME" ]; then
  echo "Atlassian credentials detected — configuring adapters..."
  rai adapter setup auto
else
  echo "⊘ No Atlassian env vars — skipping adapter auto-setup"
  echo "  To configure later: rai adapter setup auto"
  echo "  Required: JIRA_URL, JIRA_API_TOKEN, JIRA_USERNAME"
fi
```

| Condition | Action |
|-----------|--------|
| JIRA_URL + token + username set | Run `rai adapter setup auto` (includes Confluence if those vars are set too) |
| Any Jira var missing | Skip with note — not an error |
| Auto-setup fails | Warn and continue — adapters can be configured later |

This step is **best-effort** — adapter config is not required for onboarding to succeed. The developer can always run the setup commands manually later.

<verification>
Adapter auto-setup attempted (or skipped with clear message). Failure does not block onboarding.
</verification>

### Step 4: Register Repository (if missing)

If Check 3 failed:

1. Detect git remote and repo name:
```bash
git remote get-url origin
```

2. Extract name from remote URL (last path component, strip `.git`).

3. Present and confirm:
```
Repository not registered on server.
  Name:   raise-commons
  Remote: git@gitlab.com:humansys/raise-commons.git
  Slug:   raise-commons

Register? [Y/n]
```

4. Execute:

| Response | Action |
|----------|--------|
| Y (default) | register the repo |
| n | Skip — note that project linking will also be skipped |

```bash
rai repo register <name> --url <remote>
```

**If register returns 409** (already exists): treat as success — the repo was registered by someone else or in a previous attempt.

**If no git remote found:**
```
No git remote 'origin' detected.
Enter repository name manually: ___
```

<verification>
Repository appears in `rai repo list` output.
</verification>

### Step 5: Link to Project (if missing)

If Check 4 failed:

1. Present options:
```
Repository 'raise-commons' is not linked to any project.

  1. Create new project 'raise-commons' and link (Recommended)
  2. Link to existing project
  3. Skip — I'll do this later

Choice [1]:
```

2. Execute based on choice:

**Option 1 — Create and link (default):**
```bash
rai project create <repo-name>
rai project link-repo <repo-slug> <repo-slug> --primary
```
If `project create` returns 409 (already exists), continue to link-repo.

**Option 2 — Link to existing:**
```bash
rai project list
```
Show the list and ask:
```
Available projects:
  1. raise-commons
  2. raise-server
  3. raise-admin

Link to which project? [number or slug]: ___
```
Then:
```bash
rai project link-repo <chosen-project> <repo-slug> --primary
```

**Option 3 — Skip:**
Note in summary that project linking was skipped.

<verification>
Repository linked to a project (or explicitly skipped by user).
</verification>

### Step 5b: Build and Push Knowledge Graph

After project linking, build the local knowledge graph and sync it to the server so team members can query cross-repo context:

```bash
rai graph build
```

If the build succeeds and the server is connected (Check 1 passed), push:

```bash
rai graph push
```

| Condition | Action |
|-----------|--------|
| Build succeeds + server connected | Push to server |
| Build succeeds + no server | Skip push, note graph is local-only |
| Build fails | Warn and continue — `rai graph build` can be run later |
| Push fails | Warn and continue — `rai graph push` can be retried later |

This step is **best-effort** — graph sync completes the data loop but is not required for onboarding to succeed.

<verification>
Graph built locally. Push attempted if server connected. Failures are warnings, not blockers.
</verification>

### Step 6: Summary

Present final status:

```
--- Onboarding Complete ---
✓ Connected to api.raise.sh (org: humansys)
✓ Project initialized (raise-commons)
✓ Repository registered (raise-commons)
✓ Linked to project raise-commons (primary)
✓ Knowledge graph built (843 nodes) and synced to server

Next steps:
  - Run /rai-session-start to begin working
  - Run /rai-project-onboard for governance setup (discovery + docs)
```

If any steps were skipped:
```
--- Onboarding Partial ---
✓ Connected to api.raise.sh (org: humansys)
✓ Project initialized (raise-commons)
✓ Repository registered (raise-commons)
⊘ Project link skipped
⊘ Graph push skipped (no project link)

Run /rai-onboard-repo again to complete remaining steps.
```

## Output

| Item | Destination |
|------|-------------|
| Connection | `~/.rai/server.json` (via rai connect, not this skill) |
| Manifest | `.raise/manifest.yaml` (via rai init) |
| Adapter configs | `.raise/backlog.yaml` + `.raise/docs.yaml` (via rai adapter setup auto, best-effort) |
| Registered repo | raise-server API |
| Project link | raise-server API |
| Knowledge graph | `.raise/rai/memory/index.json` (local) + raise-server (remote) |
| Next | `/rai-session-start` or `/rai-project-onboard` |

## Quality Checklist

- [ ] All 4 checkpoints verified before any action
- [ ] Status summary shown before executing anything
- [ ] Connect missing = hard stop with instructions (no device flow)
- [ ] Each step confirms before executing
- [ ] 409 responses treated as success (idempotent)
- [ ] No git remote = graceful fallback to manual input
- [ ] Summary shows final state with next steps
- [ ] NEVER execute rai connect inside this skill

## References

- Commands used: rai connect, rai init, rai repo register, rai project create, rai project link-repo
- Sibling: `/rai-project-onboard` (governance onboarding)
- Next: `/rai-session-start`
