# Epic Brief: Agent-Orchestrated Workflow

**Epic:** RAISE-325
**Branch:** `epic/e325/agent-orchestrated-workflow`
**Date:** 2026-03-01
**Problem Brief:** `work/problem-briefs/agent-orchestrated-workflow-2026-03-01.md`

---

## Hypothesis

If we transform the RaiSE interaction model from "human dispatches skills sequentially" to "agent orchestrates the full workflow with parametrized HITL", then developers will be able to declare objectives and delegate execution cycles to the agent, measured by reduction in manual commands per session and the agent's ability to complete a story-level cycle without dispatch intervention.

## Success Metrics

| Metric | Baseline | Target |
|--------|----------|--------|
| Manual skill invocations per story cycle | ~8-12 (`start`, `design`, `plan`, `implement`, `review`, `close` + repeats) | 1 (declare objective) |
| HITL touchpoints per story | Every step transition | Only decisions and gate validations |
| Time spent on process vs. decisions | ~40% process, 60% decisions | ~10% process, 90% decisions |

## Appetite

Large (L). This is a vision-level change to the interaction model. Expect 5-8 stories minimum, likely spanning multiple milestones.

## Rabbit Holes

- Over-engineering the orchestration engine (keep it simple — skill chaining, not a workflow DSL)
- Trying to eliminate ALL human interaction (HITL is the value, not a bug)
- Building a full autonomous agent framework when sequential skill calls suffice
- Scope creeping into multi-agent orchestration (that's a separate concern)

## Key Risks

| Risk | Mitigation |
|------|------------|
| Loss of developer control/trust | Parametrized HITL — developer chooses what to review |
| Token economy — long conversations burn context | CLI offloading for mechanical work, high-density semantic outputs |
| Skill interdependencies not well-defined | Map skill inputs/outputs before orchestrating |
| Breaking existing workflow for users who prefer manual | Opt-in — orchestrated mode alongside manual skills |
