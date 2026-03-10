# Hotfix Scope: HF-1 Session Narrative

## Problem

Session handoff loses reasoning between conversations. The context bundle preserves "what to do next" (~30 tokens) but drops "why we decided this" (~550 tokens). PAT-E-279.

## Research

RES-SESSION-MEM-001 — Surveyed 6 agents (Cline, Claude Code, OpenClaw, OpenAI SDK, Cursor, Aider). Consensus: structured summaries > raw history, two-tier memory, "immediately resumable" as design goal.

## In Scope

- Add `SessionNarrative` Pydantic model to session state schema
- Wire `narrative` field through close flow (CloseInput → SessionState)
- Wire narrative into bundle assembly (load without truncation)
- Update session-close skill template to produce narrative
- Update session-start skill to mention narrative in bundle

## Out of Scope

- log_path wiring (existing dead field — separate cleanup)
- Vector search / Mem0-style recall
- Multi-session history loading
- Token budget enforcement
- Truncation changes for primes/patterns (separate improvement)

## Done Criteria

- [ ] SessionNarrative model exists with 5 fields (decisions, research, artifacts, branch_state, context)
- [ ] Session close persists narrative to session-state.yaml
- [ ] Session start loads narrative into context bundle (untruncated)
- [ ] Session-close skill template includes narrative guidance
- [ ] Session-start skill mentions narrative section
- [ ] All existing tests pass
- [ ] New tests cover narrative write/read roundtrip
- [ ] Retrospective complete
