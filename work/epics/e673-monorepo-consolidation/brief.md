---
epic_id: "E11"
title: "Monorepo Consolidation — rai-agent into raise-commons with uv workspaces"
status: "in-progress"
created: "2026-03-23"
jira_key: "RAISE-673"
initiative: "STRAT-24"
---

# Epic Brief: Monorepo Consolidation

## Hypothesis
For the RaiSE platform team (5 devs) who need to develop rai-agent alongside
raise-cli and raise-pro without cross-repo dependency hell,
the Monorepo Consolidation restructures raise-commons into a uv workspace monorepo
with packages/rai-agent alongside existing packages,
producing a single repo with atomic cross-package changes and selective publishing,
that enables faster iteration and simpler CI while keeping OSS/proprietary boundaries.
Unlike separate repos per product, our solution
gives every developer full context in one place and eliminates cross-repo versioning.

## Success Metrics
- **Leading:** `packages/rai-agent/` exists in raise-commons with passing CI (1 week)
- **Lagging:** `pip install rai-agent` installs from the monorepo package

## Appetite
M — estimated 5-7 stories

## Scope Boundaries
### In (MUST)
- Restructure raise-commons as uv workspace monorepo
- Move rai-agent code from this repo to packages/rai-agent/ in raise-commons
- Setup pyproject.toml with base + extras ([telegram], [gchat], [scheduling])
- CI/CD selective publishing per package
- Consolidate Jira to single RAISE project with components

### In (SHOULD)
- Docker Compose template for rai-agent self-hosting
- Apache 2.0 license for rai-agent package
- CONTRIBUTING.md and AGENTS.md

### Out (WON'T)
- scaleup/ module (client-specific, stays in personal repo)
- Personal config, session state, coaching data
- PyPI publishing (separate story post-E11)
- Web UI or desktop app

## Rabbit Holes
- uv workspace configuration may need research (emerging feature)
- Existing CI/CD in raise-commons needs to be workspace-aware
- raise-cli is currently the root package — needs restructuring to packages/raise-cli/
- Don't break existing raise-cli installations during transition

## Research
- work/research/rai-agent-distribution/ (SES-035: distribution patterns, package boundaries)
- AutoGen monorepo pattern (uv workspaces, coordinated releases)
- LangChain monorepo pattern (independent semver per package)
