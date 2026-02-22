---
epic: RAISE-247
title: "CLI Ontology Restructuring"
status: scoped
branch: v2
adr: ADR-038
date: 2026-02-21
size: M
---

# RAISE-247: CLI Ontology Restructuring

## Objective

Restructure the `rai` CLI from 10 groups / 36 commands to 9 groups / 27 commands by
decomposing the `memory` God Object into bounded contexts, killing redundancies, and
merging overlapping groups. The CLI is consumed by agents executing skills, not by
humans directly — precision and prevention of concern leakage take priority over
anthropomorphic naming.

## Current State

```
rai init
rai session    (3 commands)     ← clean
rai memory     (15 commands)    ← GOD OBJECT: graph + patterns + telemetry + deprecated
rai discover   (4 commands)     ← has graph merge step that belongs elsewhere
rai skill      (4 commands)     ← clean
rai backlog    (4 commands)     ← clean
rai publish    (2 commands)     ← overlaps with release
rai release    (1 command)      ← overlaps with publish
rai profile    (1 command)      ← singleton wrapper
rai base       (1 command)      ← singleton wrapper
```

## Target State

```
rai init                           # Project bootstrap
rai info                           # Package info (absorbs base show)
rai profile                        # Developer profile (flattened)

rai session start|context|close    # Temporal work state
rai graph build|validate|query|    # Knowledge graph structure
      context|list|viz|extract
rai pattern add|reinforce          # Learned knowledge
rai signal emit                    # Process telemetry

rai discover scan|analyze|drift    # Codebase understanding
rai skill list|validate|           # Skill governance
       check-name|scaffold
rai backlog auth|pull|push|status  # External sync
rai release check|publish|list     # Release management
```

## Stories

### S1: Create `graph` group (rename from `memory` core)

**What:** Create `rai graph` with commands: build, validate, query, context, list, viz,
extract. These are the 7 commands from `memory` that operate on the knowledge graph
structure.

**Includes:**
- New `cli/commands/graph.py` with the 7 commands
- Register in `main.py`
- Backward-compat alias: `rai memory <cmd>` → `rai graph <cmd>` + deprecation warning
- Update tests

**Size:** M

### S2: Create `pattern` group (extract from `memory`)

**What:** Create `rai pattern` with commands: add, reinforce. Extract from `memory`
commands that write/score patterns.

**Includes:**
- New `cli/commands/pattern.py`
- Backward-compat aliases for `rai memory add-pattern` and `rai memory reinforce`
- Update tests

**Size:** S

### S3: Create `signal` group (extract from `memory`)

**What:** Create `rai signal emit` unifying `emit-work`, `emit-session`, `emit-calibration`
into one command with positional type argument.

**Includes:**
- New `cli/commands/signal.py`
- Unified `rai signal emit <type>` interface
- Backward-compat aliases for all three `rai memory emit-*` commands
- Update tests

**Size:** S

### S4: Kill redundancies and deprecated commands

**What:** Remove 3 commands that are redundant or deprecated.

**Removes:**
- `memory generate` (deprecated, no consumers)
- `memory add-session` (redundant with `session close`)
- `memory add-calibration` (redundant with `signal emit calibration`)

**Includes:**
- Verify no skill references these commands
- Remove from CLI registration
- Update tests

**Size:** XS

### S5: Merge `publish` + `release`, flatten singletons

**What:** Consolidate release management into one group. Flatten singleton wrappers.

**Changes:**
- `publish check` + `publish release` → `release check` + `release publish`
- `release list` stays
- `base show` → `rai info` (top-level)
- `profile show` → `rai profile` (top-level, no subcommand)
- Backward-compat aliases for `publish` commands

**Size:** S

### S6: Absorb `discover build` into `graph build`

**What:** Make `graph build` consume discovery output directly. Remove `discover build`
as a standalone command.

**Includes:**
- Modify `graph build` to handle component merge (currently in `discover build`)
- Update discover-validate and discover-document skills
- Backward-compat alias

**Size:** S

### S7: Update all skills and generated docs

**What:** Mechanical find-replace across all 22 skills in `skills_base/`, plus CLAUDE.md
CLI Quick Reference and README.

**Includes:**
- Update all `rai memory` → `rai graph` / `rai pattern` / `rai signal` in skills_base/
- Regenerate CLAUDE.md from `.raise/` canonical source
- Update README.md CLI examples
- Run `rai init --force` to propagate to `.claude/skills/` and `.agent/skills/`
- Verify no stale references remain (grep gate)

**Size:** M

### S8: Remove backward-compat aliases (deferred)

**What:** After one release cycle with deprecation warnings, remove the `rai memory *`
aliases. **Not in this epic** — tracked here for completeness. Execute when all known
client projects have updated.

**Size:** XS (future)

## Dependency Order

```
S1 (graph) → S2 (pattern) → S3 (signal) → S4 (kill) → S5 (merge/flatten) → S6 (absorb) → S7 (skills)
```

S1-S6 are CLI changes. S7 is the propagation sweep — must go last.
S8 is deferred to a future release cycle.

## Decisions (from ADR-038 open questions)

1. **`graph extract` survives** as a public command. It's used in `project-create` and
   `project-onboard` skills for on-demand governance extraction.
2. **`pattern list` deferred.** Not day-one. `graph list --types pattern` covers it.
   Add when pattern curation becomes a real workflow.
3. **Branch model:** Stories branch directly from `v2` (branchless epic pattern, same
   as RAISE-144 Engineering Health).

## Verification Gate

```bash
# No stale references in canonical sources
grep -r "rai memory" src/rai_cli/skills_base/ && exit 1
grep -r "rai memory" CLAUDE.md && exit 1
grep -r "rai publish" src/rai_cli/skills_base/ && exit 1

# Backward compat works
rai memory query "test" 2>&1 | grep -q "DEPRECATED"
rai memory emit-work story S1 -e start -p design 2>&1 | grep -q "DEPRECATED"

# New commands work
rai graph query "test"
rai pattern add "test pattern" -c "test" -t technical
rai signal emit work S1 --event start --phase design
rai release list
rai info
rai profile
```

## References

- ADR-038: CLI Ontology Restructuring (full analysis)
- PAT-E-151: Large-scale renames have a long tail
- PAT-E-153: JSONL backward compat pattern
- SES-234: Ontological analysis session
