---
epic_id: "E353"
title: "Orchestration Quality"
status: "in-progress"
created: "2026-03-03"
backlog_key: "RAISE-398"
---

# E353: Orchestration Quality

## Objective

Eliminate the 4.6x quality gap in orchestrated skill execution by implementing the Checkpoint & Fork pattern: heavy skills fork to fresh-context subagents, structured results checkpoint to disk between phases.

## In Scope
- Modify `rai-story-run` to fork heavy phases via subagents
- Modify `rai-epic-run` to fork story-run invocations
- Disk-based structured checkpoints between phases
- Quality parity validation (before/after measurement)

## Out of Scope
- Custom agent infrastructure (`.claude/agents/`)
- Changes to individual skill content (SKILL.md)
- Generic orchestration framework
- Agent Teams (experimental)

## Done Criteria
- [ ] story-run forks heavy phases (implement, AR, QR, review) to subagents
- [ ] epic-run forks story-run invocations to subagents
- [ ] Quality measurement shows >80% parity with standalone execution
- [ ] Existing delegation gates still work correctly
- [ ] Phase detection and resume still work correctly

## Research
- Evidence catalog: `work/research/orchestration-quality/evidence-catalog.md`
- Full report: `work/research/orchestration-quality/report.md`
- Session SES-319: lived the Checkpoint & Fork pattern during E354 ideation research
