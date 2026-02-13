---
id: ADR-026
title: Filtered GitHub Mirror via Sync Script
status: accepted
date: 2026-02-13
decision_makers: [emilio]
story: S18.5
---

# ADR-026: Filtered GitHub Mirror via Sync Script

## Context

RaiSE uses GitLab as its source of truth (raise-commons). For public distribution, we need a GitHub mirror at `humansys/raise`. The mirror must exclude internal directories (`work/`, `dev/`, `.raise/`, `governance/`, `.claude/`, `scripts/`, `blog/`, `docs/`, `archive/`) that contain story artifacts, memory state, telemetry, session data, and internal governance docs.

## Decision

**Use a custom sync script (`scripts/sync-github.sh`) instead of GitLab's native repository mirroring.**

The script creates an orphan commit from the source branch, removes excluded directories/files, and force-pushes to GitHub. No git history is carried — the public repo shows only the current state as a single commit.

Sync is triggered manually via `./scripts/sync-github.sh v2 main`. CI automation (GitLab CI job on push to `v2`) is planned as a follow-up.

## Alternatives Considered

| Alternative | Pros | Cons |
|-------------|------|------|
| **GitLab native mirror** | Zero config, automatic | No filtering — pushes ALL content including internal dirs |
| **Git subtree / sparse checkout** | Standard git tooling | Complex setup, doesn't cleanly exclude multiple scattered dirs |
| **Separate public repo with copy** | Full separation | Manual sync burden, easy to drift, duplicate maintenance |
| **`.gitattributes` export-ignore** | Built into git | Only works with `git archive`, not push-based mirroring |

## Consequences

### Positive

- Internal content never reaches GitHub (no secrets, no internal process artifacts)
- Orphan commit means no history leakage — even if a file was briefly tracked, it won't appear
- Script is idempotent and auditable (`bash -x` for debugging)
- Simple to extend exclusion list as project evolves

### Negative

- Manual sync until CI automation is added
- Force-push means GitHub PRs/issues don't carry commit history context
- Script requires `github` remote configured locally
- Exclusion list must be maintained in the script (not declarative)

### Risks

- Forgetting to sync after important changes (mitigated by CI automation in S18.3)
- Exclusion list drift — new internal dirs added without updating the script (mitigated by PAT-E-273: review exclusions on each sync)

## Implementation

- Script: `scripts/sync-github.sh`
- Source branch: `v2` (development)
- Target: `github` remote → `main` branch
- Excluded dirs: `work/`, `dev/`, `.raise/`, `archive/`, `blog/`, `docs/`, `governance/`, `.claude/`, `scripts/`
- Excluded files: `.claude.json`, `.cursorindexingignore`, `CLAUDE.md`, `CLAUDE.local.md`

## Future Evolution

- **CI trigger:** GitLab CI job on push to `v2` runs the sync script automatically
- **Declarative exclusions:** Move exclusion list to a config file (e.g., `.github-mirror.conf`)
- **Public flip:** When repo goes public, enable branch protection and GitHub Actions

## References

- S18.5 design: `work/epics/e18-prelaunch-repo/stories/s18.5-github-org-setup/design.md`
- PAT-E-272: `git rm --ignore-unmatch` for defensive scripting
- PAT-E-273: Exclusion lists evolve — update docs each time
