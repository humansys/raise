---
epic: RAISE-247
title: "CLI Ontology Restructuring"
status: in-progress
branch: epic/e247/cli-ontology
adr: ADR-038
date: 2026-02-21
size: M
stories_count: 6
---

# RAISE-247: CLI Ontology Restructuring

## Objective

Restructure the `rai` CLI from 11 groups / 41 commands to 10 groups / 31 commands by
decomposing the `memory` God Object into bounded contexts, killing redundancies, and
merging overlapping groups. The CLI is consumed by agents executing skills, not by
humans directly — precision and prevention of concern leakage take priority over
anthropomorphic naming.

**Value proposition:** Clean CLI namespace for Kurigage teams + prerequisite for
RAISE-248 (Hooks & Gates) which wires events to the new command names.

## Current State (post-E211)

```
rai init
rai adapters   (2 commands)     ← NEW from E211, clean
rai session    (3 commands)     ← clean
rai memory     (15 commands)    ← GOD OBJECT: graph + patterns + telemetry + deprecated
rai discover   (4 commands)     ← clean (discover build stays)
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
rai signal emit-work|              # Process telemetry
       emit-session|emit-calibration

rai adapters list|check            # Adapter inspection (from E211)
rai discover scan|analyze|         # Codebase understanding
         build|drift
rai skill list|validate|           # Skill governance
       check-name|scaffold
rai backlog auth|pull|push|status  # External sync
rai release check|publish|list     # Release management
```

## Stories

| ID | Story | Size | Status | Dependencies | Description |
|----|-------|:----:|:------:|:------------:|-------------|
| S1 | Create `graph` group | M | ✅ Done | None | Extract 7 graph commands from memory.py |
| S2 | Create `pattern` group | S | ✅ Done | None | Extract add-pattern + reinforce from memory.py |
| S3 | Create `signal` group | S | ✅ Done | None | Extract emit-work/session/calibration as 3 subcommands |
| S4 | Kill redundancies | XS | ✅ Done | None | Remove generate, add-session, add-calibration + coverage gate |
| S5 | Merge publish+release, flatten singletons | S | ✅ Done | None | Consolidate release mgmt, flatten base/profile |
| S6 | Update all skills and generated docs | M | Pending | S1-S5 | Mechanical find-replace across 22 skills + CLAUDE.md |

**Total:** 6 stories (down from 8 after arch review)

### S1: Create `graph` group (extract from `memory` core)

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

**What:** Create `rai signal` with 3 subcommands: emit-work, emit-session,
emit-calibration. Same signatures as current memory emit-* commands — no unification,
just re-homing to the correct bounded context.

**Rationale (arch review R1):** The three emit commands have different signatures.
Unifying into `rai signal emit <type>` adds Typer complexity for marginal gain.
Three subcommands in one group achieves the taxonomic goal without artificial coupling.

**Includes:**
- New `cli/commands/signal.py` with 3 subcommands
- Backward-compat aliases for `rai memory emit-*`
- Update tests

**Size:** S

### S4: Kill redundancies and deprecated commands

**What:** Remove 3 commands that are redundant or deprecated.

**Removes:**
- `memory generate` (deprecated, no consumers)
- `memory add-session` (redundant with `session close`)
- `memory add-calibration` (redundant with `signal emit-calibration`)

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

### S6: Update all skills and generated docs

**What:** Mechanical find-replace across all 22 skills in `skills_base/`, plus CLAUDE.md
CLI Quick Reference and README.

**Includes:**
- Update all `rai memory` → `rai graph` / `rai pattern` / `rai signal` in skills_base/
- Regenerate CLAUDE.md from `.raise/` canonical source
- Update README.md CLI examples
- Run `rai init` to propagate to `.claude/skills/` and `.agent/skills/`
- Verify no stale references remain (grep gate)

**Size:** M

### Deferred (not in this epic)

- **S7 (was): Local Skill Registry** → Deferred to RAISE-242/S0 (Skill Ecosystem).
  No custom skills in production yet; S6 can sweep directly. Trigger to promote:
  first custom skill in a client project. (Arch review Q1)
- **S9 (was): Remove backward-compat aliases** → Future release cycle.
- **S6 (was): Absorb discover build** → Kept in discover group.
  Coupling risk outweighs 1-command reduction. (Arch review R2)

## Dependency Order

```
S1 (graph) ──┐
S2 (pattern) ─┤
S3 (signal) ──┼── S6 (skill sweep)
S4 (kill) ────┤
S5 (merge) ──┘
```

S1-S5 are independent — all extract/restructure different parts of the CLI.
S6 (propagation sweep) must go last because it updates skills to use the new names.

## Decisions

1. **`graph extract` survives** as a public command. Used in `project-create` and
   `project-onboard` skills.
2. **`pattern list` deferred.** `graph list --types pattern` covers it.
3. **Branch model:** Stories branch from `epic/e247/cli-ontology`.
4. **`adapters` group unchanged** — E211, already well-bounded.
5. **`discover build` stays** in discover group. (Arch review R2)
6. **`signal` uses 3 subcommands** not unified `emit <type>`. (Arch review R1)
7. **Skill Registry deferred** to RAISE-242. (Arch review Q1)
8. **S1-S5 are independent** — no artificial linear chain. (Arch review Q2)

## Done Criteria

### Per Story
- [ ] New commands work with correct output
- [ ] Backward-compat aliases print deprecation warning + delegate
- [ ] Tests pass (pyright, ruff, pytest)
- [ ] Retrospective complete

### Epic Complete
- [ ] No `rai memory` references in `skills_base/` or `CLAUDE.md`
- [ ] No `rai publish` references in `skills_base/`
- [ ] All backward-compat aliases work with deprecation warnings
- [ ] All new commands work
- [ ] Epic retrospective completed
- [ ] Merged to `v2`

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
rai signal emit-work story S1 --event start --phase design
rai release list
rai info
rai profile
```

---

## Implementation Plan

> Added by `/rai-epic-plan` — 2026-02-23

### Execution Order

| Order | Story | Size | Dependencies | Milestone | Rationale |
|:-----:|-------|:----:|:------------:|:---------:|-----------|
| 1 | S1: Create `graph` group | M | None | M1 | Largest extraction (7 cmds), proves the pattern |
| 2 | S2: Create `pattern` group | S | None | M1 | Same pattern as S1, smaller (2 cmds) |
| 3 | S3: Create `signal` group | S | None | M1 | Same pattern, 3 subcommands |
| 4 | S4: Kill redundancies | XS | None | M2 | ✅ Done — removed 3 commands + coverage gate |
| 5 | S5: Merge publish+release | S | None | M2 | Different pattern (merge, not extract) |
| 6 | S6: Skill + docs sweep | M | S1-S5 | M3 | Must go last — uses new names |

**Note:** S1-S5 are independent and could run in any order. Sequential execution
chosen for clean commits and incremental validation. S1 first because it's the
largest and establishes the extraction pattern (new file, register, backward-compat
shim) that S2-S3 replicate at smaller scale.

### Milestones

| Milestone | Stories | Success Criteria |
|-----------|---------|------------------|
| **M1: God Object Decomposed** | S1, S2, S3 | `memory` has 0 active commands. `graph` (7), `pattern` (2), `signal` (3) work. Backward-compat aliases work. |
| **M2: Clean Taxonomy** | S4, S5 | 3 dead commands removed. `publish` merged into `release`. `base`/`profile` flattened. |
| **M3: Epic Complete** | S6 | 0 stale refs in skills_base/ + CLAUDE.md. Verification gate passes. Ready for `/rai-epic-close`. |

### Parallel Work Streams

```
Time →
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
S1 (graph) → S2 (pattern) → S3 (signal) → S4 (kill) → S5 (merge) → S6 (sweep)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        M1 ─────────────────┘    M2 ──────┘   M3 ┘
```

Single-stream sequential. S1-S5 *could* parallelize but the extraction pattern
is the same for S1-S3 — doing S1 first establishes it, then S2-S3 are mechanical.
Context switching between parallel branches adds merge overhead that exceeds the
time saved for these small stories.

### Progress Tracking

| Story | Size | Status | Actual | Velocity | Notes |
|-------|:----:|:------:|:------:|:--------:|-------|
| S1: graph group | M | ✅ Done | 150 min | 1.6x | PAT-E-434/435/436 |
| S2: pattern group | S | ✅ Done | 45 min | 1.33x | PAT-E-440/441 |
| S3: signal group | S | ✅ Done | 21 min | 2.86x | PAT-E-442, M1 complete |
| S4: kill redundancies | XS | ✅ Done | 25 min | 0.8x | RAISE-253, PAT-E-444 |
| S5: merge+flatten | S | ✅ Done | 29 min | 2.07x | RAISE-254, PAT-E-446/447 |
| S6: skill sweep | M | Pending | - | - | RAISE-255 |

**Milestones:**
- [x] M1: God Object Decomposed (S1+S2+S3 — 2026-02-23)
- [x] M2: Clean Taxonomy (S4+S5 — 2026-02-23)
- [ ] M3: Epic Complete

### Risks

| Risk | L | I | Mitigation |
|------|:-:|:-:|------------|
| PAT-E-151: rename long tail (stale refs missed) | M | M | Grep verification gate in S6 + backward-compat aliases as safety net |
| Typer backward-compat: alias routing may have edge cases | L | M | Test each alias in S1 (first story validates the approach) |
| 22-skill sweep in S6 is tedious and error-prone | M | L | Mechanical find-replace + grep gate. No judgment needed. |

---

## References

- ADR-038: CLI Ontology Restructuring (Accepted)
- PAT-E-151: Large-scale renames have a long tail
- PAT-E-153: JSONL backward compat pattern
- SES-234: Ontological analysis session
- Architecture review: SES-254 (R1, R2, Q1, Q2 accepted)
