---
epic_id: "E353"
title: "Orchestration Quality"
status: "in-progress"
created: "2026-03-03"
backlog_key: "RAISE-398"
---

# Epic E353: Orchestration Quality — Scope

> **Status:** IN PROGRESS
> **Branch:** `epic/e353/orchestration-quality`
> **Created:** 2026-03-03

## Objective

Eliminate the 4.6x quality gap in orchestrated skill execution by implementing the Checkpoint & Fork pattern: heavy skills fork to fresh-context subagents, structured results checkpoint to disk between phases.

**Value:** Developers can trust `rai-story-run` and `rai-epic-run` to produce output quality identical to standalone skill invocations. No more manual phase-by-phase execution.

## Stories

| ID | Story | Size | Status | Description |
|----|-------|:----:|:------:|-------------|
| S353.1 | Checkpoint contract | XS | Pending | Define artifact I/O contract per phase and update skill prerequisites |
| S353.2 | story-run fork | S | Pending | Modify rai-story-run to fork heavy phases via Agent tool |
| S353.3 | epic-run fork | S | Pending | Modify rai-epic-run to fork story-run invocations via Agent tool |
| S353.4 | Quality validation | S | Pending | Measure orchestrated vs standalone quality parity (>80% target) |

**Total:** 4 stories

## Scope

**In scope (MUST):**
- Modify rai-story-run to fork heavy phases (design, plan, implement, AR, QR, review) to subagents
- Modify rai-epic-run to fork story-run invocations to subagents
- Existing artifacts (design.md, plan.md, etc.) serve as phase-to-phase contracts
- Phase detection (git-derived artifact scan) unchanged
- Delegation gates unchanged (main thread between forks)
- Quality parity validation >80% of standalone execution

**In scope (SHOULD):**
- Document artifact I/O contract per phase (what each phase reads/writes)

**Out of scope:**
- Custom agent infrastructure (`.claude/agents/`) → not needed, Agent tool suffices
- Changes to individual SKILL.md content → only orchestrator behavior changes
- Generic orchestration framework → just modify the two existing orchestrators
- Agent Teams → experimental, overkill for sequential chains
- Parallel phase execution (AR + QR) → future optimization, not needed for quality parity

## Done Criteria

**Per story:**
- [ ] Skill modifications in builtin (`src/rai_cli/skills_base/`) and deployment (`.claude/skills/`)
- [ ] Both copies verified identical (`diff`)
- [ ] Manual smoke test of modified skill

**Epic complete:**
- [ ] story-run forks heavy phases to subagents (when standalone)
- [ ] epic-run forks story-run invocations to subagents
- [ ] Quality measurement shows >80% parity with standalone execution
- [ ] Delegation gates still work correctly (main thread)
- [ ] Phase detection and resume still work correctly (artifact-based)
- [ ] ADR-043 accepted
- [ ] Epic retrospective done
- [ ] Merged to `dev`

## Dependencies

```
S353.1 (checkpoint contract)
  ↓
S353.2 ──┐
  ↓      │ (parallel after S353.1)
S353.3 ◄─┘
  ↓
S353.4 (validation — after S353.2 + S353.3)
```

**External:** None. Uses existing Claude Code Agent tool mechanism.

## Architecture

| Decision | ADR | Summary |
|----------|-----|---------|
| Checkpoint & Fork pattern | ADR-043 | Heavy phases fork to subagents, artifacts are the API between phases |

> Research: `work/research/orchestration-quality/report.md`

## Risks

| Risk | L/I | Mitigation |
|------|:---:|------------|
| Subagent doesn't have enough context for phase | M/M | Each skill already reads prior artifacts from disk; add explicit prereq list per phase |
| F5 constraint: story-run in epic-run can't fork phases | H/L | By design — epic-level isolation is the primary win; story-level inline is acceptable when nested |
| Agent tool behavior changes in Claude Code update | L/H | Pattern is simple (spawn agent with prompt + file reads); easy to adapt |

## Parking Lot

- Parallel phase execution (AR + QR simultaneously) → future epic if needed
- `context: fork` frontmatter support → investigate when Claude Code adds it for Skill tool
