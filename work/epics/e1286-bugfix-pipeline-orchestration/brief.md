---
epic_id: "E1286"
title: "Bugfix Pipeline Orchestration"
status: "draft"
created: "2026-04-04"
---

# Epic Brief: Bugfix Pipeline Orchestration

## Hypothesis
For AI agents executing `/rai-bugfix` who skip steps (77% adoption failure documented in E1133 F1),
the orchestrated bugfix pipeline is a skill-chain orchestrator
that enforces all 7 phases via subagent isolation and HITL gates.
Unlike the monolithic skill where the agent decides what to skip, our solution makes phases structurally non-skippable.

## Success Metrics
- **Leading:** Triage custom fields populated in Jira for 100% of bugs processed through `/rai-bugfix-run` (vs 1/80+ baseline)
- **Lagging:** Full artifact completeness (scope+analysis+plan+retro) ≥90% for bugs processed (vs 38% baseline)

## Appetite
S — 4-5 stories

## Scope Boundaries
### In (MUST)
- 7 atomic skills extracted from monolithic `/rai-bugfix` (start, triage, analyse, plan, fix, review, close)
- `/rai-bugfix-run` orchestrator skill following `/rai-story-run` pattern
- Mandatory HITL gate after triage (even in AUTO delegation)
- MCP custom field population baked into triage skill
- Phase detection from `work/bugs/RAISE-{N}/` artifacts for resume capability

### In (SHOULD)
- Benchmarking against top dev agents (Devin, Cursor, Windsurf, Copilot Workspace) bug-handling workflows
- Compatibility with E1065 pipeline engine `bugfix.yaml` skill references

### No-Gos
- No pipeline engine dependency — this runs on 2.4.0 via skill orchestration
- No changes to the pipeline engine code (that's 3.0.0)
- No retroactive processing of historical bugs

### Rabbit Holes
- Over-engineering state persistence between phases — artifacts on disk are the state
- Trying to make the orchestrator handle edge cases the individual skills should handle
