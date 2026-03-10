# E352: Doctor — Retrospective

## Summary

Delivered `rai doctor` CLI + `/rai-doctor` skill for RaiSE self-diagnostics. 5 stories: infrastructure, environment checks, project checks, auto-fix with backup, report generation via mailto.

## Metrics

| Metric | Value |
|--------|-------|
| Stories | 5 |
| Tests added | 92 |
| ADRs | 1 (ADR-045: DoctorCheck protocol separate from gates) |
| Research | 8 tools analyzed, 11 patterns extracted |

## What Went Well

- Research-first approach (competitive analysis of 8 tools) grounded all design decisions
- ADR-045 kept doctor checks separate from workflow gates — cleaner separation of concerns
- `--fix` with automatic `.bak` backup gives confidence to auto-remediate
- Parallel story execution via worktree isolation worked well for independent stories

## What Could Improve

- Graph path was `.rai/graph/` in tests but actual output is `.raise/rai/memory/index.json` — always verify actual CLI output paths
- DISTRIBUTABLE_SKILLS registry is manual — new skills must be explicitly added or they don't deploy

## Patterns

- Doctor and migration are the same tool — config version detection should be built into doctor
- Subagent worktrees need careful merge — they may rewrite shared files causing conflicts
