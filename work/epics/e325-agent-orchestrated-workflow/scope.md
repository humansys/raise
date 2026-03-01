# Scope: E325 Agent-Orchestrated Workflow

**Epic:** [RAISE-325](https://humansys.atlassian.net/browse/RAISE-325)
**Branch:** `epic/e325/agent-orchestrated-workflow`
**Base:** `dev`
**Date:** 2026-03-01

---

## Objective

Transform the RaiSE interaction model from human-dispatched skill invocation to agent-orchestrated workflow execution with parametrized HITL, so the developer focuses on decisions while the agent handles process.

## In Scope

- Skills integration with `rai backlog` CLI (read/write backlog from skills)
- Skills integration with `rai docs` CLI (read/write governance docs from skills)
- Skill chaining model — define inputs/outputs so one skill can flow into the next
- HITL parametrization — configurable gates for when to pause and ask the developer
- Discovery/onboard compaction — reduce manual steps, use subagents for mechanical work
- Orchestrator skill or meta-skill that can run a full cycle (epic or story level)
- Token economy — CLI offloading for context-heavy operations

## Out of Scope

- Multi-agent orchestration (separate concern, RAISE-127)
- Workflow DSL or visual workflow editor
- Breaking backward compatibility with manual skill invocation
- Server-side orchestration (this is local-first, CLI + agent)
- Changes to `rai-server` or shared memory backend

## Planned Stories (preliminary — refined in /rai-epic-design)

1. Skill I/O contract definition — map inputs/outputs for all lifecycle skills
2. Backlog integration — skills read/write via `rai backlog`
3. Docs integration — skills read/write via `rai docs`
4. HITL parametrization model — configurable pause points
5. Discovery/onboard compaction — reduce steps, subagent offloading
6. Story-level orchestrator — single command runs full story cycle
7. Epic-level orchestrator — single command runs full epic cycle

## Done Criteria

- [ ] Developer can say "implement story X" and agent executes the full cycle
- [ ] HITL occurs only at pre-agreed decision/validation points
- [ ] Skills use `rai backlog` and `rai docs` without backend coupling
- [ ] Manual skill invocation still works (backward compatible)
- [ ] Discovery/onboard runs with minimal human dispatch
