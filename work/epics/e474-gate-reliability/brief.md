---
epic_id: "E474"
title: "Gate Reliability: CI-Skills Parity"
status: "draft"
created: "2026-03-06"
---

# Epic Brief: Gate Reliability: CI-Skills Parity

## Hypothesis
For RaiSE developers who rely on skills and gates to catch errors before CI,
the gate reliability initiative is a process fix
that ensures lint, format, and type errors never escape to CI undetected.
Unlike the current state where CI runs 4 validations but skills only run 1-2,
our solution guarantees 1:1 parity between CI and local gates.

## Success Metrics
- **Leading:** `rai gate check --all` catches the same errors as `.gitlab-ci.yml` test job
- **Lagging:** Zero CI failures caused by lint/format/type errors for 10 consecutive pushes

## Appetite
S — 3-5 stories

## Scope Boundaries
### In (MUST)
- FormatGate implementation (`ruff format --check`)
- story-close invokes `rai gate check --all` before merge
- gate-code.md updated to reflect Python stack
- Pyright error fix (backlog.py walrus operator)
- Ruff format + import fixes committed (56 files)

### In (SHOULD)
- Pre-commit hook running lint+format+types
- CI=Skills principle documented as guardrail

### No-Gos
- Rewriting the gate framework itself
- Adding new CI stages or jobs
- Changing ruff configuration rules

### Rabbit Holes
- Over-engineering pre-commit hooks with caching/parallelism
- Trying to make gates run identically to CI (Docker image parity)
