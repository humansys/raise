# Implementation Plan: S18.5 GitHub Organization Setup

## Overview
- **Story:** S18.5
- **Size:** M
- **Type:** Infrastructure (no source code — all `gh` CLI + shell script)
- **Created:** 2026-02-13

## Tasks

### Task 1: Configure Org Profile & Create Repo
- **Description:** Set humansys org profile (name, description, blog URL). Create `humansys/raise` as a private repo with description, topics, and homepage.
- **Commands:**
  - `gh api -X PATCH /orgs/humansys` — org profile
  - `gh repo create humansys/raise --private` — repo creation
  - `gh repo edit humansys/raise` — topics, homepage, description
- **Verification:** `gh repo view humansys/raise` shows correct config; repo is private
- **Size:** S
- **Dependencies:** None

### Task 2: Create Team & Configure Permissions
- **Description:** Create `engineering` team under humansys. Add danieloliva-humansys, aquilesHs as members. Grant team write access to `humansys/raise`. Verify oemilio has admin via org ownership.
- **Commands:**
  - `gh api /orgs/humansys/teams` — create team
  - `gh api /orgs/humansys/teams/engineering/members` — add members
  - `gh api /orgs/humansys/teams/engineering/repos` — grant repo access
- **Verification:** `gh api /orgs/humansys/teams/engineering/members` lists correct members; team has write on raise repo
- **Size:** S
- **Dependencies:** Task 1 (repo must exist)

### Task 3: Branch Protection & PR Template
- **Description:** Configure branch protection on `main`: require PR reviews, no force push, no deletion. Add a PR template (`.github/pull_request_template.md`).
- **Verification:** `gh api /repos/humansys/raise/branches/main/protection` shows rules; PR template exists in repo
- **Size:** XS
- **Dependencies:** Task 5 (need main branch with content first)

### Task 4: Create Labels
- **Description:** Create standard labels for issue triage: `bug`, `enhancement`, `documentation`, `good first issue`, `help wanted`, `question`, `wontfix`, `priority:high`, `priority:medium`, `priority:low`, `scope:cli`, `scope:skills`, `scope:memory`.
- **Verification:** `gh label list -R humansys/raise` shows all labels
- **Size:** XS
- **Dependencies:** Task 1 (repo must exist)

### Task 5: Write Sync Script & Initial Push
- **Description:** Create `scripts/sync-github.sh` that:
  1. Takes source branch (default: main) and target branch (default: main) as args
  2. Creates a temp orphan branch from source
  3. Removes `work/`, `dev/`, `.raise/`, `archive/` via `git rm -rf`
  4. Commits and force-pushes to `github` remote target branch
  5. Cleans up temp branch, returns to original branch

  Add `github` as a remote pointing to `humansys/raise`. Run the script to push filtered content.
- **Files:** `scripts/sync-github.sh` (new)
- **Verification:** Script runs without error; `gh api /repos/humansys/raise/contents` shows src/, tests/, governance/ but NOT work/, dev/, .raise/, archive/
- **Size:** M
- **Dependencies:** Task 1 (repo must exist)

### Task 6: Manual Integration Test
- **Description:** Verify the full setup end-to-end:
  - Browse `humansys/raise` on GitHub — correct description, topics, homepage
  - Confirm repo is private
  - Check team access — engineering team has write
  - Check branch protection on main
  - Verify filtered content — no work/, dev/, .raise/, archive/
  - Verify issue templates render correctly
  - Verify labels exist
  - Run sync script a second time — idempotent, no errors
- **Verification:** All checks pass; HITL review
- **Size:** XS
- **Dependencies:** All previous tasks

## Execution Order

```
T1 (org + repo) ──→ T2 (team + permissions)
       │
       ├──→ T4 (labels)
       │
       └──→ T5 (sync script + push) ──→ T3 (branch protection + PR template)
                                                    │
                                                    ▼
                                              T6 (integration test)
```

1. **T1** — Foundation: org profile + repo creation
2. **T2, T4, T5** — Parallel after T1 (team, labels, sync script)
3. **T3** — After T5 (needs main branch with content for protection rules)
4. **T6** — Final validation

## Risks

| Risk | Mitigation |
|------|------------|
| Free org plan limits (teams, branch protection) | Check GitHub Free org features before executing; upgrade if needed |
| Sync script loses commits on re-run (force push) | By design — GitHub mirror is read-only target. Document clearly in script header. |
| `.claude/` directory exposes skill content | Skills are already distributed in PyPI package — public by design |

## Duration Tracking

| Task | Size | Actual | Notes |
|------|:----:|:------:|-------|
| T1: Org + repo | S | — | |
| T2: Team + permissions | S | — | |
| T3: Branch protection | XS | — | |
| T4: Labels | XS | — | |
| T5: Sync script + push | M | — | |
| T6: Integration test | XS | — | |
