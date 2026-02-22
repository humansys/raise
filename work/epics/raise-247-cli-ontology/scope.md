---
epic: RAISE-247
title: "CLI Ontology Restructuring"
status: scoped
branch: v2
adr: ADR-038
date: 2026-02-21
size: L
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

### S7: Local Skill Registry

**What:** Create a persistent skill index at `.raise/rai/skills/registry.json` that tracks
installed skills with metadata, ownership, and version — so the CLI manages skills as
entities, not loose files.

**The registry knows:**
- **What's installed:** skill name, version, work_cycle, path
- **Ownership:** `framework` (from `skills_base/`, updatable by `rai init`) vs `custom`
  (created by user/org, never overwritten) vs `org` (installed via future `rai skill pull`)
- **Version drift:** installed version vs available version from `skills_base/`
- **Frontmatter cache:** work_cycle, prerequisites, fase — queryable without re-parsing

**Why it's prerequisite for S8 (skill sync post-rename):**
Without registry, `rai init --force` after the ontology rename would overwrite custom
skills that clients have created. The registry's ownership field (`framework` vs `custom`)
is what makes selective sync safe: update framework skills, preserve custom ones.

**Includes:**
- `RegistryEntry` Pydantic model (name, version, ownership, work_cycle, path, installed_at)
- `SkillRegistry` class: load, save, register, unregister, diff_against_base
- `rai skill list` reads from registry instead of filesystem scan
- `rai init` populates registry when scaffolding skills
- `rai skill scaffold` registers new skill as `custom`
- Migration: first run builds registry from existing filesystem state

**Does NOT include:**
- `rai skill pull` / org sources (future, parking lot)
- `rai skill prepare` (rejected — coupling)
- Skill marketplace integration

**Size:** M

### S8: Update all skills and generated docs

**What:** Mechanical find-replace across all 22 skills in `skills_base/`, plus CLAUDE.md
CLI Quick Reference and README.

**Includes:**
- Update all `rai memory` → `rai graph` / `rai pattern` / `rai signal` in skills_base/
- Regenerate CLAUDE.md from `.raise/` canonical source
- Update README.md CLI examples
- Run `rai init` to propagate to `.claude/skills/` and `.agent/skills/` (registry-aware,
  only updates `framework` ownership skills)
- Verify no stale references remain (grep gate)

**Size:** M

### S9: Remove backward-compat aliases (deferred)

**What:** After one release cycle with deprecation warnings, remove the `rai memory *`
aliases. **Not in this epic** — tracked here for completeness. Execute when all known
client projects have updated.

**Size:** XS (future)

## Dependency Order

```
S1 (graph) → S2 (pattern) → S3 (signal) → S4 (kill) → S5 (merge/flatten) → S6 (absorb)
  → S7 (registry) → S8 (skills)
```

S1-S6 are CLI changes. S7 is the registry (enables safe sync). S8 is the propagation
sweep — must go last because it uses the registry to avoid overwriting custom skills.
S9 is deferred to a future release cycle.

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

# Registry exists and tracks ownership
test -f .raise/rai/skills/registry.json
rai skill list --format json | python -c "import sys,json; d=json.load(sys.stdin); assert any(s.get('ownership')=='framework' for s in d)"
```

## References

- ADR-038: CLI Ontology Restructuring (full analysis)
- PAT-E-151: Large-scale renames have a long tail
- PAT-E-153: JSONL backward compat pattern
- SES-234: Ontological analysis session
