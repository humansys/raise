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
| S353.1 | Checkpoint contract | XS | Done | Define artifact I/O contract per phase and update skill prerequisites |
| S353.2 | story-run fork | S | Done | Modify rai-story-run to fork heavy phases via Agent tool |
| S353.3 | epic-run checkpoint | S | Done | Modify rai-epic-run to checkpoint between stories and keep main thread thin for story-run forks |
| S353.4 | Quality validation | S | Done | Measure orchestrated vs standalone quality parity (>80% target) |

**Total:** 4 stories

## Scope

**In scope (MUST):**
- Modify rai-story-run to fork heavy phases (design, plan, implement, AR, QR, review) to subagents
- Modify rai-epic-run to keep story-run inline (main thread) with thin checkpoints between stories
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
- [ ] epic-run invokes story-run inline (main thread) with thin checkpoints between stories
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
| Main thread context grows across stories in epic-run | M/L | Epic-run is thin (summaries only between stories); heavy phase output lives in discarded subagent contexts |
| Agent tool behavior changes in Claude Code update | L/H | Pattern is simple (spawn agent with prompt + file reads); easy to adapt |

## Implementation Plan

### Sequencing Strategy: Walking Skeleton

Prove the fork pattern on story-run first (where the 4.6x gap was measured), then extend to epic-run, then validate.

| # | Story | Strategy | Rationale | Enables |
|:-:|-------|----------|-----------|---------|
| 1 | S353.1 — Checkpoint contract | Quick win | Foundation: defines phase I/O contracts. XS effort, unblocks everything. | S353.2, S353.3 |
| 2 | S353.2 — story-run fork | Risk-first | Primary quality fix. The 4.6x gap was measured here. Proves the pattern. | S353.3, S353.4 |
| 3 | S353.3 — epic-run checkpoint | Dependency-driven | Keeps story-run in main thread (so it can fork) with thin checkpoint between stories. | S353.4 |
| 4 | S353.4 — Quality validation | Verification | Validates both orchestrators against >80% parity target. | Epic close |

**Critical path:** S353.1 → S353.2 → S353.4
**Parallel opportunities:** S353.3 could run parallel to S353.2 (different files), but sequential is safer for 4 stories — marginal benefit vs coordination cost.

### Milestones

| Milestone | Stories | Success Criteria |
|-----------|---------|------------------|
| **M1: Pattern Proven** | S353.1 + S353.2 | story-run forks heavy phase via Agent tool, produces artifact on disk, manual smoke test shows quality improvement |
| **M2: Epic Complete** | S353.3 + S353.4 | Both orchestrators fork. Quality measurement >80% parity. All done criteria met. |

### Progress Tracking

| Story | Status | Started | Completed | Notes |
|-------|:------:|---------|-----------|-------|
| S353.1 — Checkpoint contract | Done | 2026-03-03 | 2026-03-03 | Gemba found 5 discrepancies, AR/QR inline-only finding |
| S353.2 — story-run fork | Done | 2026-03-03 | 2026-03-03 | v2.0.0, 6 fork + 2 inline, Agent prompt template |
| S353.3 — epic-run checkpoint | Done | 2026-03-03 | 2026-03-03 | F5 constraint, checkpoint protocol, verify-and-fill pattern |
| S353.4 — Quality validation | Done | 2026-03-03 | 2026-03-03 | 94% weighted parity (>80% target), validation report published |

### Sequencing Risks

| Risk | Mitigation |
|------|------------|
| Agent tool spawn prompt too complex → subagent misinterprets instructions | Start with simplest heavy phase (design) in S353.2, iterate prompt before tackling implement |
| Smoke testing is subjective (how to judge "quality improvement"?) | S353.4 defines objective metrics (tool calls, output volume, artifact depth) |
| S353.1 contract becomes speculative without testing | Keep contract lightweight — document current reality, not aspirational format |

## Parking Lot

- Parallel phase execution (AR + QR simultaneously) → future epic if needed
- `context: fork` frontmatter support → investigate when Claude Code adds it for Skill tool
