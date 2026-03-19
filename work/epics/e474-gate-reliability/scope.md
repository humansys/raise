---
epic_id: "E474"
title: "Gate Reliability: CI-Skills Parity"
tracker: "RAISE-474"
status: "in-progress"
target_version: "2.2.2"
---

# E474: Gate Reliability — CI-Skills Parity

## Objective

Eliminate the gap between CI validation and skill/gate verification so that lint, format, and type errors are caught locally before reaching CI. Audit the codebase against the code standard (S370.1) and enforce it.

## Root Cause (Ishikawa)

CI runs 4 commands (pytest, ruff check, ruff format --check, pyright) but skills/gates only verify tests + sometimes ruff check. No FormatGate exists. gate-code.md is stale (references npm). story-close and story-review don't invoke gate check.

## Stories

- [x] S474.1 (RAISE-477) — Fix existing lint/format/type errors (done, commit dbeee497)
- [x] S474.2 (RAISE-478) — Create FormatGate + update gate-code.md to Python stack
- [x] S474.3 (RAISE-479) — Code audit: apply S370.1 standard to codebase, fix violations
- [x] S474.4 (RAISE-480) — Pre-commit hook for lint+format+types
- [x] S474.5 (RAISE-481) — Document CI=Skills guardrail

## Dependencies

```
S474.1 (done)
  └── S474.2 (FormatGate)
        ├── S474.3 (code audit) ── S474.5 (guardrail)
        └── S474.4 (pre-commit hook)
```

## Out of Scope (deferred to E476: Skillset Evolution)

- raise-dev skillset creation (RAISE-476)
- Clean standard skills to be language-agnostic
- Skills invoke gates before merge (story-close, story-review, epic-close)

## A Considerar

- Changes to gate framework if analysis justifies it
- New CI jobs if a new gate requires it
- Ruff rule adjustments if they cause friction

## Done Criteria

1. `rai gate check --all` catches everything `.gitlab-ci.yml` test job checks
2. Codebase passes S370.1 code standard audit
3. Pre-commit hook prevents committing code that would fail CI
4. CI pipeline passes on dev branch
5. CI=Skills guardrail documented
