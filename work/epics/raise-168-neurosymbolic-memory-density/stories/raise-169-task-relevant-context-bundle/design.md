---
story: RAISE-169
title: Task-relevant context bundle
epic: RAISE-168
size: M
phase: design
---

# Design: RAISE-169 — Task-relevant context bundle

## What & Why

**Problem:** The context bundle loads ~1200 tokens of fixed primes (governance, behavioral, coaching, deadlines, progress) regardless of session type. Research RES-MEMORY-002 (RQ2) shows irrelevant content degrades LLM accuracy by up to 21.4%.

**Value:** By separating orientation (always needed) from priming (task-dependent), the skill can compose only the context it needs — saving ~450 tokens per session and improving accuracy through relevance filtering.

## Architectural Context

**Module:** mod-session (session lifecycle — state persistence, context bundle assembly)
**Dependencies:** mod-memory, mod-context, mod-cli, mod-schemas

## Approach

Split the monolithic bundle into two orthogonal concerns:

1. **Orientation** — "where are we?" (always needed)
2. **Priming** — "how should I behave?" (task-dependent, skill-driven)

`rai session start --context` becomes lean: orientation + manifest of available sections.
New subcommand `rai session context --sections X,Y` loads specific priming sections deterministically.
The skill (not the CLI) decides what to load based on session focus.

**Design principle:** CLI is deterministic plumbing. Skill is composing intelligence. Each does what it does best.

## Section Taxonomy

### Always-on (orientation) — in `rai session start --context`

| Section | Source | Purpose |
|---------|--------|---------|
| Developer identity | profile | Who am I talking to |
| Session ID | generated | Traceability |
| Work context | state | Story, epic, branch, phase |
| Last session | state | Immediate continuity |
| Recent sessions | index.jsonl | Broader continuity |
| Narrative | state | Cross-session decisions, artifacts |
| Next session prompt | state | Forward-looking guidance |
| Pending | state | Blockers, decisions, next actions |

### Queryable (priming) — via `rai session context --sections`

| Section Name | Source | Filter | Typical Tokens |
|-------------|--------|--------|----------------|
| `governance` | graph | `always_on=true`, not `RAI-VAL-*`/`RAI-BND-*` | ~350 |
| `behavioral` | graph | `type=pattern`, `foundational=true` | ~250 |
| `coaching` | profile | `coaching.*` fields | ~80 |
| `deadlines` | profile | `deadlines` list | ~60 |
| `progress` | state | `progress` + `completed_epics` | ~40 |

**Section names are the contract** between CLI and skill. Adding a new section means adding a name, a source, and a format function.

## Manifest Format

`rai session start --context` appends a manifest after orientation:

```
# Available Context
- governance: 14 items (~350 tokens)
- behavioral: 12 items (~250 tokens)
- coaching: active (~80 tokens)
- deadlines: 0 active
- progress: RAISE-168 2/5 stories
```

The manifest is self-describing: section name, item count, estimated token cost. When a count is 0, the skill knows there's nothing to load (and can flag the gap).

## CLI Interface

### Modified: `rai session start --context`

Output changes from full bundle to orientation + manifest. No new flags needed.

```bash
rai session start --project "$(pwd)" --context
# Returns: orientation (~400 tokens) + manifest (~50 tokens)
```

### New subcommand: `rai session context`

```bash
rai session context --sections governance,behavioral --project .
# Returns: formatted priming sections (~600 tokens)
```

**Implementation:** Reuses existing `_format_*` functions from `bundle.py`. The `--sections` flag maps section names to format functions deterministically.

```python
SECTION_REGISTRY: dict[str, Callable] = {
    "governance": _format_governance_section,
    "behavioral": _format_behavioral_section,
    "coaching": _format_coaching_section,
    "deadlines": _format_deadlines_section,
    "progress": _format_progress_section,
}
```

Each function loads its own data source (graph, profile, or state) and returns formatted text. No keyword search — direct metadata filtering.

### Backward Compatibility

`rai session start --context` changes output (lean instead of full). The session-start skill is updated in the same story. No other consumers exist.

## Skill Integration

The session-start skill flow becomes:

```
Step 1: rai session start --context --project .
        → orientation + manifest

Step 2: Interpret orientation (work state, narrative, next prompt)
        Ask human: "What are we doing today?"

Step 3: Based on focus, decide sections:
        - implement → governance, behavioral, coaching
        - research  → coaching (lean context)
        - debug     → behavioral
        - design    → governance, behavioral, coaching

Step 4: rai session context --sections <selected> --project .
        → formatted priming sections

Step 5: Interpret full context, present session summary
```

**IMPORTANT:** The section selection in Step 3 is heuristic, not hardcoded. The skill provides guidance ("governance = coding standards, useful when writing code") and Rai decides based on the human's stated focus. The manifest counts inform the decision (if governance has 0 items, don't request it).

**Grounding check:** If a requested section returns empty or a manifest shows 0 items where content is expected, Rai flags it: "No governance primes found in the graph — where can I find grounding for coding standards?"

## Examples

### Session start output (lean)

```
# Session Context

Developer: Emilio (ha)
Communication: language: es, style: direct, skip_praise, redirect_when_dispersing

Session: SES-211

Story: RAISE-169 [design]
Epic: RAISE-168
Branch: story/raise-169/task-relevant-context-bundle

Last: SES-210 (2026-02-18, Emilio) — Started RAISE-169, design phase.

Recent:
- SES-210: Started RAISE-169...
- SES-209: Completed RAISE-165...

# Session Narrative
## Decisions
- Option B selected: sectioned bundle with manifest...

# Next Session Prompt
Continue with RAISE-169 implementation...

# Pending
Next:
- Complete design for RAISE-169

# Available Context
- governance: 14 items (~350 tokens)
- behavioral: 12 items (~250 tokens)
- coaching: active (~80 tokens)
- deadlines: 0 active
- progress: RAISE-168 2/5 stories
```

### Section query output

```bash
$ rai session context --sections governance,behavioral --project .
```

```
# Governance Primes
- guardrail-must-code-001: [MUST] Type hints on all code — Verify: pyright --s...
- guardrail-must-code-002: [MUST] Ruff linting passes — Verify: ruff check .` ...
...

# Behavioral Primes
- PAT-E-149: Single source of truth: remove redundant counters when authoritati...
- PAT-E-150: Drift review before implementation catches stale scopes...
...
```

## Acceptance Criteria

**MUST:**
- [ ] `rai session start --context` outputs orientation + manifest (no priming sections)
- [ ] `rai session context --sections X,Y` returns formatted priming sections
- [ ] Section names are the contract: governance, behavioral, coaching, deadlines, progress
- [ ] Manifest shows item count and token estimate per section
- [ ] Existing tests pass; new tests cover both commands
- [ ] Session-start skill updated to two-phase flow

**SHOULD:**
- [ ] Empty section in manifest triggers grounding check guidance in skill
- [ ] Token estimates in manifest are within 20% of actual

**MUST NOT:**
- [ ] CLI must not contain session-type logic (no "implement profile" or "research profile")
- [ ] Skill must not hardcode section selection as rigid rules (heuristics, not tables)
