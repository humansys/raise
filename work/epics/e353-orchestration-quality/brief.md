---
epic_id: "E353"
title: "Orchestration Quality — Checkpoint & Fork pattern for context-isolated skill execution"
status: "draft"
created: "2026-03-03"
---

# Epic Brief: Orchestration Quality

## Hypothesis
For RaiSE developers who run full story/epic lifecycles via orchestrators,
the Checkpoint & Fork pattern is a quality preservation mechanism
that eliminates the 4.6x quality gap between orchestrated and standalone skill execution.
Unlike current inline execution, our solution forks heavy skills to fresh-context subagents
and checkpoints structured results to disk between phases.

## Success Metrics
- **Leading:** Quality review in orchestrated story-run produces comparable depth to standalone (>80% of standalone tool calls and output volume)
- **Lagging:** Developers stop preferring manual skill invocation over orchestrators

## Appetite
S — 2-4 stories (skill modifications, not new infrastructure)

## Scope Boundaries
### In (MUST)
- Update story-run to fork heavy phases (design, plan, implement, AR, QR, review) via subagents
- Update epic-run to fork story-run invocations
- Structured checkpoint data between phases (disk-based)
- Validate quality parity with before/after measurement

### In (SHOULD)
- Parallel execution where phases are independent (e.g., AR + QR could overlap)
- Research skill update to formalize parallel subagent pattern

### No-Gos
- Custom agent files (`.claude/agents/`) — use `context: fork` or Agent tool, not new infrastructure
- Agent Teams — experimental, overkill for sequential chains
- Changes to individual skill SKILL.md content — only orchestrator behavior changes

### Rabbit Holes
- Over-engineering the checkpoint format — keep it simple, YAML or existing markdown artifacts
- Trying to pass conversation context to forked subagents — the whole point is fresh context
- Building a generic orchestration framework — just modify the two existing orchestrators
