---
epic_id: "RAISE-247"
title: "CLI Ontology Restructuring"
status: "draft"
created: "2026-02-23"
---

# Epic Brief: CLI Ontology Restructuring

## Hypothesis
For AI agents executing RaiSE skills who encounter a `memory` group with 15 commands
spanning graph operations, pattern management, and telemetry,
the CLI Ontology Restructuring is a bounded-context decomposition
that delivers precise, non-leaking command groups aligned to single responsibilities.
Unlike the current God Object where agents must know which of 15 subcommands belong
to which concern, our solution maps each command to exactly one bounded context.

## Success Metrics
- **Leading:** `rai memory` subcommand count drops from 15 to 0 (all redistributed)
- **Lagging:** RAISE-248 (Hooks & Gates) wires events without renaming; skill update sweep (S8) is mechanical find-replace with zero ambiguity

## Appetite
L — 8 implementable stories (S1-S8), S9 deferred to future release cycle.
Estimated ~4-5 hours across 2 sessions.

## Scope Boundaries
### In (MUST)
- Decompose `memory` into `graph`, `pattern`, `signal` groups
- Kill 3 deprecated/redundant commands
- Merge `publish` into `release`, flatten `base` and `profile` singletons
- Absorb `discover build` into `graph build`
- Local skill registry with ownership tracking
- Update all 22 skills + CLAUDE.md + README with new command names
- Backward-compat aliases with deprecation warnings for all renamed commands

### In (SHOULD)
- `rai info` as top-level package info command
- Registry migration from filesystem state on first run

### No-Gos
- Removing backward-compat aliases (S9, deferred to future release)
- `rai skill pull` / org skill sources (parking lot)
- Skill marketplace integration
- Changing `adapters` group (E211, already well-bounded)

### Rabbit Holes
- Over-designing the skill registry — it's a JSON file with Pydantic models, not a database
- Trying to make `signal emit` support future event types not yet defined
- Attempting cross-cutting refactors beyond the CLI command layer (internals stay stable)
