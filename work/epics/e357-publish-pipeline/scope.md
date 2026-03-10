---
epic_id: "E357"
title: "Release Pipeline Streamlining"
status: "draft"
created: "2026-03-06"
---

# E357: Release Pipeline Streamlining

## Objective

Unify the release process for RaiSE (code + docs + website + security) into a single
orchestrated pipeline. Every release should be reproducible, auditable, and require
minimal manual intervention beyond the decision to release.

## Current State

- `/rai-publish` handles version bump + changelog + PyPI publish
- Website deploy is manual (`wrangler pages deploy`)
- Docs version not verified against release
- No secret scanning gate
- No post-deploy verification
- Release steps are scattered across memory and skills

## Planned Stories

| # | Story | Size | Description |
|---|-------|------|-------------|
| S357.1 | Audit current release process | S | Document every manual step, identify gaps and risks |
| S357.2 | Secret scanning gate | S | Integrate git-secrets/trufflehog into pre-publish check |
| S357.3 | Automated website deploy on release | S | GitHub Actions: merge to main triggers site build+deploy |
| S357.4 | Docs version verification | S | Gate: verify docs/ content references correct version |
| S357.5 | Extend /rai-publish for full pipeline | M | Orchestrate: gates → bump → publish → deploy → verify |
| S357.6 | Post-deploy smoke test | XS | curl key URLs, verify version stamp, report status |
| S357.7 | Release notes automation | S | Generate draft from commit log + story retrospectives |

## Done Criteria

- [ ] Single command (`/rai-publish`) orchestrates entire release
- [ ] Secret scanning blocks release on findings
- [ ] Website deploys automatically as part of release
- [ ] Docs version verified before publish
- [ ] Post-deploy verification confirms live site matches release
- [ ] Process documented in governance/sops/
