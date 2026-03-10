---
epic_id: "E357"
title: "Release Pipeline Streamlining"
status: "draft"
created: "2026-03-06"
---

# Epic Brief: Release Pipeline Streamlining

## Hypothesis
For the RaiSE maintainers who release framework + website + docs as a coordinated unit,
a unified publish pipeline is a devsecops automation
that ensures nothing is forgotten, nothing leaks, and every release is reproducible.
Unlike the current manual checklist approach, our solution
makes the entire release a single orchestrated flow.

## Success Metrics
- **Leading:** Release checklist fully automated (0 manual steps beyond approval)
- **Lagging:** Release cycle time < 30 min from decision to published

## Appetite
M — 5-7 stories

## Scope Boundaries
### In (MUST)
- Unified release gate: code + docs + website + secrets audit in one flow
- Automated website deploy as part of release (not separate manual step)
- Docs version verification (docs/ matches release version)
- Secret scanning gate (pre-publish, block on findings)
- Build ID / version stamp in website footer (already done in E356)
- `/rai-publish` skill extended to orchestrate full pipeline

### In (SHOULD)
- Changelog auto-generation from commit history
- Release notes draft from story retrospectives
- Smoke test post-deploy (curl key URLs, verify version)
- Notification on release (Slack/email)

### No-Gos
- No product feature changes (this is pure devsecops)
- No CI/CD platform migration (stay on GitHub Actions)
- No multi-environment (staging/prod) — single production target for now

### Rabbit Holes
- Over-engineering the pipeline with too many gates
- Building a custom release orchestrator when GitHub Actions suffices
- Trying to automate Cloudflare dashboard operations that require manual auth
