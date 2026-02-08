---
id: "ADR-024"
title: "Deterministic Session Protocol — CLI Context Bundling and Platform Agnosticism"
date: "2026-02-08"
status: "Accepted"
related_to: ["ADR-019", "ADR-023"]
supersedes: []
research: ""
epic: "E15"
---

# ADR-024: Deterministic Session Protocol — CLI Context Bundling and Platform Agnosticism

## Context

### The Problem

Rai's session continuity is fragmented across platform-coupled artifacts and cached inference:

1. **CLAUDE.local.md** — Primary context source for session-start, but tied to Claude Code. Manually maintained, drifts between sessions. Violates the Constitution's Platform Agnosticism principle.

2. **Session bridges** (`session-bridge-*.md`) — Prose written by one Rai instance for the next. This is *cached inference* — a previous instance interpreting and freezing conclusions as text. The receiving instance inherits stale interpretation instead of interpreting fresh from deterministic data.

3. **Scattered reads** — Session-start skill runs 3+ CLI commands plus manual file reads to assemble context (~3300 tokens of mixed-quality input). The skill does data plumbing that should be deterministic CLI operations.

4. **No relationship persistence** — Coaching observations, corrections, trust trajectory, and communication notes are lost every session. Rai reconstructs the relationship from a few flat fields in `developer.yaml` instead of accumulated observations.

5. **No behavioral priming** — 186 patterns exist in the graph, but session-start doesn't surface the ones that should change Rai's behavior. Foundational patterns like PAT-183 (design always) get forgotten between sessions.

### The Principle

RaiSE's own architecture follows **deterministic data with inference interpretation**: CLI tools extract and structure data deterministically, AI interprets contextually. The session protocol violates this principle — skills (inference layer) do data plumbing, and the richest context source is vendor-locked.

### Ownership Clarification

`~/.rai/` is **Rai's space**, not the developer's. Like `.git` is git's directory, `.rai` is Rai's. `developer.yaml` is "Rai's model of the developer" — Rai writes it, Rai reads it, Rai owns it. The developer can inspect it (transparency), but authorship is Rai's.

This resolves the design question of where coaching observations belong: they extend the developer model because they are Rai's observations about the developer — same author, same file, same purpose.

## Decision

**Redesign the session protocol so the CLI assembles a complete, token-optimized context bundle from deterministic sources. Skills become thin inference layers that interpret the bundle, not data plumbing orchestrators.**

### Architecture

```
SESSION START:
┌─────────────────────────────────────────────────────────────┐
│  raise session start --project . --context                  │
│                                                             │
│  Reads:                                                     │
│  ├── ~/.rai/developer.yaml        → identity + coaching     │
│  ├── .raise/rai/session-state.yaml → working state          │
│  ├── .raise/graph/unified.json    → foundational patterns   │
│  └── governance artifacts          → (future: deadlines)    │
│                                                             │
│  Outputs:                                                   │
│  └── Token-optimized context bundle (~150 tokens)           │
│      to stdout                                              │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  Skill (thin inference layer)                               │
│  1. Receive context bundle                                  │
│  2. Interpret → propose focus                               │
│  Done.                                                      │
└─────────────────────────────────────────────────────────────┘


SESSION CLOSE:
┌─────────────────────────────────────────────────────────────┐
│  Skill (thin inference layer)                               │
│  1. Reflect on session → structured output                  │
│  2. Write state-file (YAML)                                 │
│  Done.                                                      │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│  raise session close --state-file output.yaml               │
│                                                             │
│  Writes (atomically):                                       │
│  ├── .raise/rai/session-state.yaml  → working state         │
│  ├── .raise/rai/memory/patterns.jsonl → new patterns        │
│  ├── ~/.rai/developer.yaml          → coaching updates      │
│  ├── .raise/rai/personal/sessions/  → session record        │
│  ├── .raise/rai/personal/telemetry/ → session event         │
│  └── ~/.rai/developer.yaml          → clear current_session │
│                                                             │
│  One command. All writes.                                   │
└─────────────────────────────────────────────────────────────┘
```

### New Artifacts

| Artifact | Location | Lifecycle | Purpose |
|----------|----------|-----------|---------|
| Session state | `.raise/rai/session-state.yaml` | Overwritten each close | Working state: current story, phase, branch, pending items |
| Coaching context | `~/.rai/developer.yaml` | Accumulates | Strengths, growth edge, corrections (FIFO 10), communication notes |
| Deadlines | `~/.rai/developer.yaml` | Updated when told | Operational context that modulates Rai's behavior |
| Context bundle | stdout | Transient | Token-optimized assembly of all sources |
| Foundational patterns | `patterns.jsonl` metadata | Human-curated | `foundational: true` tag on ~10 behavioral primes |

### Context Bundle Format

Optimized for LLM token economy — ~150 tokens vs ~3300 today (20x reduction):

```
# Session Context

Developer: Emilio (ri)
Epic: E15 Ontology Refinement [65%, 11/17 SP]
Story: S15.7 Deterministic Session Protocol [phase: design]
Branch: story/s15.7/session-protocol
Graph: 849 nodes, 6157 rels
Last: SES-097 (2026-02-08, feature) — session protocol design

# Deadlines
F&F: Feb 9 (1 day)

# Behavioral Primes
- PAT-187: Code as Gemba — observe before designing
- PAT-183: Design always, no size exemptions

# Coaching
Strengths: architectural vision, naming things
Growth edge: speed over process under pressure

# Pending
(none)
```

**Format design principles:**
- Flat key-value pairs on single lines (no JSON/YAML nesting overhead)
- Inline metadata in brackets: `[65%, 11/17 SP]`
- Section headers as semantic anchors
- Patterns as one-liners (graph has full detail if needed)
- Zero prose — only facts

### Telemetry Ownership

CLI commands emit their own telemetry. Skills do not call `emit-session`, `emit-work`, or `add-session` separately. `raise session close` performs all writes atomically — session record, telemetry, patterns, coaching, state.

### Backward Compatibility

- `raise session start` without `--context` preserves current behavior
- `raise session close` without flags preserves current behavior
- `developer.yaml` without `coaching`/`deadlines` loads cleanly (defaults to empty)
- CLAUDE.local.md continues to work as optional vendor bridge

## Consequences

### Positive

1. **Platform agnosticism** — Session protocol works with any AI client (Claude Code, Cursor, MCP, future tools). No vendor-specific file dependencies.
2. **20x token reduction** — ~150 tokens vs ~3300 for session context loading.
3. **Relationship persistence** — Coaching observations, corrections, and trust trajectory accumulate across sessions. Rai shows up knowing the developer.
4. **Behavioral priming** — Foundational patterns surfaced at session start prevent repeated mistakes (e.g., PAT-183 forgotten between sessions).
5. **Deterministic state** — Session-state.yaml is facts, not cached inference. Each Rai instance interprets fresh.
6. **Atomic writes** — One CLI command at close performs all writes. No partial state from interrupted skills.
7. **Thin skills** — Session skills reduce from 4-6 steps to 2 steps each. Less complexity, fewer failure modes.

### Negative

1. **Migration effort** — Existing session bridges become obsolete. CLAUDE.local.md loses its data role. Transition period where both old and new coexist.
2. **Schema change in developer.yaml** — Existing profiles need backward-compatible extension.
3. **CLI complexity** — `raise session start/close` commands grow significantly. More code, more tests.

### Neutral

1. **CLAUDE.local.md remains** — As optional vendor bridge and human scratch space, not as a data dependency.
2. **Session bridges stop** — No new bridges written. Existing ones can be archived.
3. **Graph rebuild not required** — Foundational pattern tagging uses existing metadata field.

## Alternatives Considered

### Alternative 1: Enhanced Session Bridges

Keep prose-based bridges but add structured YAML frontmatter.

**Rejected because:**
- Still cached inference (prose body)
- Still accumulates files per session
- Doesn't solve platform coupling
- Doesn't solve relationship persistence

### Alternative 2: CLAUDE.local.md as Primary State

Formalize CLAUDE.local.md as the session state document with structured sections.

**Rejected because:**
- Platform-coupled to Claude Code (violates Constitution)
- Mixed authorship (human and Rai both edit)
- Not programmatically writable by CLI without brittle parsing

### Alternative 3: Separate Coaching File

Store coaching observations in `~/.rai/coaching.md` separate from `developer.yaml`.

**Rejected because:**
- `~/.rai/` is all Rai's space — no authorship conflict to resolve
- Separate file adds read overhead and drift risk
- PAT-158 (progressive structure) — one developer doesn't need file separation
- Coaching is part of Rai's model of the developer — same concept, same file

### Alternative 4: Deadlines in Governance Artifacts

Parse deadlines from governance docs at session-start time.

**Rejected because:**
- Deadlines are operational context that modulates Rai's behavior, not governance artifacts
- Would require structured deadline format in governance docs (migration overhead)
- Rai updates deadlines when told — simpler to store in Rai's space
- Can graduate to governance parsing later if needed

## Validation

### Success Criteria

| Metric | Target |
|--------|--------|
| Context bundle token count | <200 tokens |
| Session-start skill steps | 2 (call CLI, interpret) |
| Session-close skill steps | 2 (reflect, feed CLI) |
| CLAUDE.local.md reads in session-start | 0 |
| Coaching fields persisted | strengths, growth_edge, corrections, communication_notes |
| Foundational patterns surfaced | ~10 curated patterns in bundle |
| Backward compat | Existing `raise session start/close` without flags unchanged |

### Test Scenario

```bash
# Close a session with full state
raise session close --state-file output.yaml

# Start next session — verify continuity
raise session start --project . --context
# Should output: developer model, current work from session-state.yaml,
# foundational patterns from graph, coaching context, deadlines
# All in ~150 tokens, no CLAUDE.local.md read needed
```

## References

- **Constitution:** Platform Agnosticism (Principle #3)
- **PAT-146:** Three-tier data architecture
- **PAT-149:** Single source of truth
- **PAT-158:** Progressive directory structure
- **PAT-187:** Code as Gemba — observe before designing
- **PAT-188:** Deterministic data + inference interpretation for session protocol
- **ADR-019:** Unified Context Graph Architecture
- **ADR-023:** Ontology Graph Extension
- **E14 Evidence:** Platform coupling identified during distribution epic
- **S15.7:** Implementation story for this decision

---

**Status**: Accepted (2026-02-08)

**Approved by**: Emilio Osorio, Rai

**Next steps**:
1. Implement S15.7 (8 tasks — schema, profile, bundle, CLI, patterns, skills)
2. Validate with full session lifecycle
3. Archive session bridges after validation
4. Generalize CLI context bundling to other skills (future)
