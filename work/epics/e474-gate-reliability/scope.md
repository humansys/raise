---
epic_id: "E474"
title: "Gate Reliability: CI-Skills Parity"
tracker: "RAISE-474"
status: "in-progress"
target_version: "2.2.2"
---

# E474: Gate Reliability — CI-Skills Parity

## Objective

Eliminate the gap between CI validation and skill/gate verification so that lint, format, and type errors are caught locally before reaching CI.

## Root Cause (Ishikawa)

CI runs 4 commands (pytest, ruff check, ruff format --check, pyright) but skills/gates only verify tests + sometimes ruff check. No FormatGate exists. gate-code.md is stale (references npm). story-close and story-review don't invoke gate check.

## Stories

- [ ] S474.1 — Fix existing lint/format/type errors (the immediate CI fix)
- [ ] S474.2 — Create FormatGate and update gate-code.md
- [ ] S474.3 — Update close/review skills to invoke `rai gate check --all`
- [ ] S474.4 — Pre-commit hook for lint+format+types
- [ ] S474.5 — Document CI=Skills guardrail

## Done Criteria

1. `rai gate check --all` catches everything `.gitlab-ci.yml` test job checks
2. story-close refuses to merge if gates fail
3. Pre-commit hook prevents committing code that would fail CI
4. CI pipeline passes on dev branch
