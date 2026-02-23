---
id: "ADR-038"
title: "CLI Ontology Restructuring — Bounded Contexts for Agent Consumption"
date: "2026-02-21"
status: "Accepted"
---

# ADR-038: CLI Ontology Restructuring

## Context

The `rai` CLI has 11 command groups and 41 subcommands (post-E211, which added `adapters`). The primary consumer of the CLI
is not the human developer — it is the AI agent executing skills. Skills are authored by
the skill creator skill and reviewed by humans (HITL). This means the CLI namespace must
optimize for:

1. **Semantic precision** — so the agent doesn't confuse concerns
2. **God Object prevention** — so future skills don't dump unrelated concerns into one group
3. **Skill legibility** — so the human reviewer understands what a skill does at a glance

The current `rai memory` group has 15 subcommands spanning 4 distinct bounded contexts:

| Concern | Commands |
|---------|----------|
| Graph structure | build, validate, extract, list, viz, generate* |
| Knowledge retrieval | query, context |
| Knowledge capture | add-pattern, add-calibration, add-session, reinforce |
| Telemetry/signals | emit-work, emit-session, emit-calibration |

*deprecated

This conflation occurred because "memory" was vague enough to absorb anything. The
anthropomorphic metaphor ("Rai's memory") served the product narrative but failed as an
engineering taxonomy. Specific problems:

- `rai memory emit-work` is a telemetry signal, not memory. It writes to `signals.jsonl`.
- `rai memory add-calibration` and `rai memory emit-calibration` record the same data to
  two different destinations — a redundancy the agent cannot reason about.
- `rai memory add-session` duplicates what `rai session close` already does.
- `rai memory viz` visualizes a graph. "Visualize memory" is semantically wrong.
- `rai memory generate` is deprecated but still present.

Additional issues outside `memory`:

- `publish` and `release` are two groups for one concern (release management).
- `base show` and `profile show` are singleton command groups (bureaucratic wrappers).
- `discover build` is a graph merge step that belongs in the graph pipeline, not discovery.

## Decision

### Principle: each CLI group = one bounded context

Restructure from 11 groups / 41 commands to 10 groups / 30 commands. The `adapters` group
(added in E211) is already well-bounded and unchanged.

### 1. `memory` → split into `graph`, `pattern`, `signal`

**`rai graph`** — Knowledge graph structure (7 commands)

```
rai graph build        # Merge all sources → index.json
rai graph validate     # Check integrity (cycles, orphan edges)
rai graph query        # Search concepts by keyword/concept
rai graph context      # Architectural context for a module
rai graph list         # Enumerate concepts
rai graph viz          # Interactive D3.js visualization
rai graph extract      # Extract concepts from governance markdown
```

**`rai pattern`** — Learned knowledge (2 commands)

```
rai pattern add        # Add pattern to patterns.jsonl
rai pattern reinforce  # Vote on pattern quality (Wilson scoring)
```

Patterns are RaiSE's core differentiator — what Rai learns from each story. They deserve
first-class citizenship, not burial inside a God Object. Future commands (`list`, `prune`,
`curate`) have a natural home.

**`rai signal`** — Process telemetry (1 command with type argument)

```
rai signal emit work {id} --event start --phase design
rai signal emit session --type feature --outcome success
rai signal emit calibration {story} -s S -e 30 -a 15
```

Unifies the three `emit-*` commands into one with a positional type argument. "Signal" (6
chars) chosen over "telemetry" (9 chars) — these are lifecycle signals, and brevity matters
for a command that appears in 10 of 22 skills.

### 2. Kill redundancies

| Command | Action | Reason |
|---------|--------|--------|
| `memory generate` | Delete | Deprecated, no consumers |
| `memory add-session` | Delete | `session close` already writes to `sessions/index.jsonl` |
| `memory add-calibration` | Delete | Redundant with `signal emit calibration` |

### 3. Absorb `discover build` into `graph build`

Current pipeline: `discover scan → discover analyze → discover build → memory build`.
The `discover build` step merges components into the graph — that's a graph concern.
`graph build` should consume `discover analyze` output directly.

`discover` retains: `scan`, `analyze`, `drift`.

### 4. Merge `publish` + `release`

One concern, one group:

```
rai release check      # Run quality gates
rai release publish    # Full release workflow
rai release list       # List releases from graph
```

### 5. Flatten singletons

```
rai profile            # Display developer profile (no subcommand)
rai info               # Display package info (absorbs `base show`)
```

### Unchanged groups

- `rai init` — clean, single responsibility
- `rai adapters` — clean (list, check) — added in E211
- `rai session` — clean (start, context, close)
- `rai skill` — clean (list, validate, check-name, scaffold)
- `rai backlog` — clean (auth, pull, push, status)

### Final taxonomy

```
rai init                           # Project bootstrap
rai info                           # Package info
rai profile                        # Developer profile

rai session start|context|close    # Temporal work state
rai graph build|validate|query|    # Knowledge graph structure
      context|list|viz|extract
rai pattern add|reinforce          # Learned knowledge
rai signal emit                    # Process telemetry

rai adapters list|check            # Adapter inspection (E211)
rai discover scan|analyze|drift    # Codebase understanding
rai skill list|validate|           # Skill governance
       check-name|scaffold
rai backlog auth|pull|push|status  # External sync
rai release check|publish|list     # Release management
```

10 groups + 2 top-level = 30 commands. 27% reduction in surface area.

### Migration strategy

1. **CLI aliases for backward compatibility.** `rai memory query` → routes to `rai graph
   query` with a deprecation warning. Follows PAT-E-153 (read new key first, fall back to
   old key).
2. **`rai init --force` propagates.** Skills in `.claude/skills/` and `.agent/skills/` are
   regenerated from `skills_base/` on init. Existing projects update by running `rai init`.
3. **Internal file paths unchanged.** `.raise/rai/memory/index.json` keeps its path — the
   directory name "memory" is an internal detail that doesn't need to match the CLI group.
4. **Work artifacts are historical.** Files in `work/`, `dev/`, `governance/` reference old
   command names — they are documentation of past decisions, not active instructions.

### Blast radius

| Change | Canonical files | Occurrences | Mechanical |
|--------|----------------|-------------|------------|
| `memory` → `graph` (6 commands) | 16 skills + CLAUDE.md + README | ~37 | find-replace |
| `emit-*` → `signal emit` | 10 skills | ~32 | find-replace + arg reorder |
| `add-pattern/reinforce` → `pattern` | 1 skill (story-review) | ~8 | find-replace |
| Kill redundancies (3 commands) | 1 skill (session-close) | ~1 | remove line |
| `publish` → `release` | 1 skill (rai-publish) | ~4 | find-replace |
| `discover build` → absorb | 2 skills (discover-validate, discover-document) | ~3 | remove/update |

Total: ~26 canonical files, ~85 occurrences. All mechanical find-replace.

Three distribution locations update automatically via `rai init`:
- `.claude/skills/` (Claude Code)
- `.agent/skills/` (generic agents)
- Agent-specific dirs (`.cursor/skills/`, `.windsurf/skills/`, etc.)

## Consequences

### Positive

- **God Object eliminated.** `memory` (15 commands, 4 concerns) → 3 focused groups.
- **Semantic precision.** Agent executing `rai graph query` knows it's reading the graph.
  Agent executing `rai signal emit` knows it's writing telemetry. No ambiguity.
- **Future-proofing.** `pattern` group can grow (list, prune, curate) without polluting
  graph operations. `signal` can grow (status, analyze) without polluting knowledge.
- **Redundancies removed.** 3 commands killed, 0 functionality lost.
- **25% surface area reduction.** 36 → 27 commands. Less for skill authors to learn.

### Negative

- **Breaking change for all skills.** 22 SKILL.md files need updating. Mitigated by
  backward-compat aliases and `rai init` propagation.
- **CLAUDE.md CLI Quick Reference needs regeneration.** Mitigated by the existing
  generation pipeline from `.raise/` canonical source.
- **Cognitive cost for the team.** Emilio and Fernando need to update muscle memory for
  `rai graph` instead of `rai memory`. Small cost given early adoption stage.

### Neutral

- Internal file paths (`.raise/rai/memory/`) remain unchanged. The rename is CLI surface
  only, not storage layer.
- Historical work artifacts retain old command names. They are records, not instructions.

## Open Questions (Resolved)

1. **`graph extract` survives.** Used in `project-create` and `project-onboard` skills
   for on-demand governance extraction. Not internal-only.
2. **`pattern list` deferred.** Not day-one. `graph list --types pattern` covers it.
   Add when pattern curation becomes a real workflow.
3. **Timing: dedicated epic RAISE-247.** Decided SES-234: shipped as v2.1 before
   RAISE-248 (Hooks & Gates), which depends on the new ontology.

## References

- ADR-012: CLAUDE.md as projection from `.raise/` canonical source
- ADR-023: Ontology graph extension
- PAT-E-151: Large-scale renames have a long tail
- PAT-E-153: JSONL backward compat pattern (read new, fall back to old)
- RAISE-144: Engineering Health epic
- SES-234: Ontological analysis session (2026-02-21)
