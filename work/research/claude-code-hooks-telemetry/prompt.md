---
research_id: "claude-code-hooks-telemetry-20260131"
primary_question: "What hooks/mechanisms does Claude Code provide for emitting custom telemetry events?"
decision_context: "Telemetry architecture for RaiSE Observable Workflow"
depth: "quick-scan"
created: "2026-01-31"
version: "1.0"
template: "research-prompt-v1"
---

# Research Prompt: Claude Code Hooks for Telemetry

## Role Definition

You are a **Research Specialist** with expertise in **Claude Code internals, hooks, and telemetry systems**.

## Research Question

**Primary**: What hooks/mechanisms does Claude Code provide for emitting custom telemetry events?

**Secondary**:
1. Can hooks emit events on skill invocation?
2. What data is available in hook context?
3. Can skill scripts write to custom telemetry locations?
4. Are there built-in telemetry formats or export mechanisms?

## Decision Context

**This research informs**: Telemetry architecture for RaiSE Observable Workflow (Constitution §8)

**Stakeholder**: RaiSE framework, raise-cli telemetry aggregation

**Impact**: Determines how RaiSE skills can emit events for Observable Workflow

## Keywords to Search

- "Claude Code hooks"
- "Claude Code telemetry"
- "Claude Code events"
- "Claude Code skill invocation events"
- "Claude Code settings hooks"
- "claude-code-guide hooks"

## Tool Selection

Using: WebSearch (fallback)

## Output

Produce artifacts in `work/research/claude-code-hooks-telemetry/`
