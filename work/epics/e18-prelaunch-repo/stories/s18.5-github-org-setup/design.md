---
story_id: S18.5
title: GitHub Organization Setup
type: infrastructure
complexity: moderate
components: [github-org, github-repo, sync-script]
---

# S18.5: GitHub Organization Setup — Design

## Problem

RaiSE has no public GitHub presence. The codebase lives in GitLab (raise-commons) and PyPI (`rai-cli`), but developers expect to find the repo on GitHub. Without it, README links, blog posts, and Show HN all point nowhere.

## Value

Unblocks the public launch (GTM E7 S7.6/S7.7). Every distribution channel (HN, Reddit, LinkedIn, Dev.to) needs a GitHub URL to point to. The org also provides team collaboration infrastructure for Daniel, Aquiles, and Fernando.

## Approach

Set up the humansys GitHub org with a filtered mirror of raise-commons. The repo starts **private** and flips to public on launch day (target: Feb 18). Internal directories (`work/`, `dev/`, `.raise/`) are excluded from the public repo — the public sees the product, not the workshop.

### Decisions

| # | Decision | Rationale |
|---|----------|-----------|
| D1 | Repo name: `humansys/raise` | Clean, matches `rai-cli` package. Prior decision from GTM E7. |
| D2 | Start private, flip public on launch | Standard practice. Configure and test before exposure. |
| D3 | Filtered sync (exclude work/, dev/, .raise/) | Public sees product, not internal artifacts. |
| D4 | Dual-remote + filter script for sync | Simplest approach for current team size. Automate via CI later. |
| D5 | Single `engineering` team with write access | Daniel, Aquiles, Fernando. oemilio stays org owner. |

### Components

| Component | Action | Description |
|-----------|--------|-------------|
| humansys org profile | Configure | Name, description, URL, avatar |
| `humansys/raise` repo | Create | Private repo, description, topics, homepage |
| `engineering` team | Create | Write access to raise repo |
| Branch protection | Configure | main: require PR, no force push, require status checks |
| Labels | Create | Standard issue labels for triage |
| Sync script | Create | `scripts/sync-github.sh` — filtered push to GitHub |
| GitHub remote | Add | `github` remote in local raise-commons clone |

### Sync Script Design

```bash
# scripts/sync-github.sh
# Syncs filtered raise-commons content to humansys/raise on GitHub
#
# What it does:
# 1. Checks out the source branch (default: main)
# 2. Creates a temp branch
# 3. Removes internal directories (work/, dev/, .raise/)
# 4. Force-pushes to github remote's target branch
# 5. Cleans up temp branch
#
# Usage: ./scripts/sync-github.sh [source-branch] [target-branch]
# Default: ./scripts/sync-github.sh main main
```

**Excluded directories:**
- `work/` — story artifacts, research, retrospectives
- `dev/` — internal dev docs, parking lot, happy path guides
- `.raise/` — memory graph, telemetry, session state
- `archive/` — historical artifacts
- `blog/` — article drafts (published via raise-gtm)
- `docs/` — internal research notes

**Included (everything else):**
- `src/` — source code
- `tests/` — test suite
- `governance/` — public governance docs
- `.claude/` — skills (distributed in package anyway)
- `.github/` — issue templates, community health
- Root files: README, LICENSE, CONTRIBUTING, CODE_OF_CONDUCT, CHANGELOG, pyproject.toml, etc.

## Acceptance Criteria

**MUST:**
- `humansys/raise` repo exists (private initially)
- Org profile configured (name, description, URL)
- `engineering` team with Daniel, Aquiles, Fernando having write access
- Branch protection on main (require PR, no force push)
- Sync script works: filtered content pushed to GitHub
- Labels created for issue triage

**SHOULD:**
- Repo topics set (python, ai, software-engineering, methodology, cli)
- Repo description and homepage URL configured
- PR template added

**MUST NOT:**
- Push `work/`, `dev/`, `.raise/`, `archive/`, `blog/`, `docs/` to GitHub
- Make repo public before explicit go-ahead
