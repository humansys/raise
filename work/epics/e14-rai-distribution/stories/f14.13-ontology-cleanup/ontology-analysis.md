# Ontological Analysis: CLI Commands & Skills

> Applying ontology engineering principles to evaluate coherence and simplicity.

## Current State

### CLI Commands (6 top-level, 22 subcommands)

```
raise
├── init                          # Project initialization
├── discover                      # Codebase analysis
│   ├── scan                      # Extract symbols
│   ├── build                     # Build unified graph
│   └── drift                     # Check architectural drift
├── memory                        # Rai's memory
│   ├── query                     # Query concepts
│   ├── build                     # Build memory index
│   ├── validate                  # Validate structure
│   ├── extract                   # Extract from governance
│   ├── list                      # List concepts
│   ├── add-pattern               # Add pattern
│   ├── add-calibration           # Add calibration
│   └── add-session               # Add session record
├── profile                       # Developer profile
│   ├── show                      # Display profile
│   ├── session-start             # Start session
│   └── session-end               # End session
├── status                        # [EMPTY - no subcommands]
└── telemetry                     # Local learning signals
    ├── emit-session              # Emit session event
    ├── emit-calibration          # Emit calibration event
    └── emit-work                 # Emit work lifecycle event
```

### Skills (20 total)

```
Session:     session-start, session-close
Epic:        epic-start, epic-design, epic-plan, epic-close
Feature:     story-start, story-design, story-plan,
             story-implement, story-review, story-close
Discovery:   discover-start, discover-scan, discover-validate, discover-complete
Other:       research, debug, framework-sync, scripts
```

---

## Ontology Engineering Analysis

### 1. Conceptual Clarity — ISSUES FOUND

**Principle:** Concepts should be clearly defined with non-overlapping semantics.

| Overlap | Commands/Skills | Issue |
|---------|-----------------|-------|
| Session management | `profile session-start`, `memory add-session`, `telemetry emit-session` | Three places touch "session" |
| Calibration | `memory add-calibration`, `telemetry emit-calibration` | Two places for same concept |
| Build | `discover build`, `memory build` | Same verb, different domains |

**Recommendation:** Consolidate session/calibration into one clear owner.

### 2. Taxonomic Consistency — ISSUES FOUND

**Principle:** Hierarchies should reflect natural categorization.

| Issue | Example | Problem |
|-------|---------|---------|
| Session under Profile | `profile session-start` | Sessions are workflows, not profile attributes |
| Emit verbs under Telemetry | `telemetry emit-*` | Telemetry is passive recording, not action commands |
| Empty category | `status` has no subcommands | Category exists without members |

**Current taxonomy confusion:**
```
profile
├── show         ← About developer (correct)
├── session-start ← About workflow (misplaced?)
└── session-end   ← About workflow (misplaced?)
```

### 3. Naming Conventions — INCONSISTENT

**Principle:** Names should follow consistent patterns.

| Pattern | Examples | Consistency |
|---------|----------|-------------|
| `noun-verb` | `session-start`, `session-close` | ✓ Skills |
| `verb-noun` | `add-pattern`, `add-session` | ✓ CLI (memory) |
| `verb-noun` | `emit-session`, `emit-work` | ✓ CLI (telemetry) |
| `verb` only | `scan`, `build`, `drift` | ✓ CLI (discover) |

**Issue:** CLI uses `add-*` and `emit-*` but skills use `*-start`, `*-close`.

### 4. Skill-CLI Mapping — INCOMPLETE

**Principle:** If skills exist, CLI support should match.

| Skill | CLI Equivalent | Status |
|-------|----------------|--------|
| `discover-start` | - | ❌ Missing |
| `discover-scan` | `discover scan` | ✓ |
| `discover-validate` | - | ❌ Missing |
| `discover-complete` | - | ❌ Missing |
| `session-start` | `profile session-start` | ⚠️ Different location |
| `session-close` | `profile session-end` | ⚠️ Different name |

### 5. Orthogonality — VIOLATIONS

**Principle:** Independent concepts should be independent in structure.

**Violation:** Session state is scattered:
- **Profile** owns session counter and current_session flag
- **Memory** can add session records
- **Telemetry** emits session events
- **Skills** (`session-start`, `session-close`) orchestrate all three

This is not orthogonal — session is one concept implemented across four systems.

### 6. Completeness — GAPS

**Principle:** Ontology should cover the domain adequately.

| Domain | CLI Coverage | Skill Coverage |
|--------|--------------|----------------|
| Project setup | ✓ `init` | - |
| Discovery | Partial (3/4) | ✓ (4 skills) |
| Memory | ✓ Full | - |
| Session | Scattered | ✓ |
| Epic workflow | - | ✓ (4 skills) |
| Feature workflow | - | ✓ (6 skills) |
| Research | - | ✓ |
| Debug | - | ✓ |

**Gap:** Epic/Feature workflow has no CLI presence (by design — skills-only).

### 7. Minimal Ontological Commitment — OVER-COMMITTED

**Principle:** Assert only what's necessary.

**Over-commitment examples:**
- `status` command exists but does nothing
- `telemetry emit-*` duplicates what `memory add-*` could do
- Three ways to record session data

---

## Proposed Simplification

### Option A: Domain-Centric (Recommended)

Reorganize around clear domains:

```
raise
├── init                    # Setup
├── discover                # Codebase analysis
│   ├── scan
│   ├── build
│   └── drift
├── memory                  # All persistent data
│   ├── query
│   ├── build
│   ├── list
│   └── add <type>          # Unified: pattern, calibration, session
├── session                 # NEW: Workflow state
│   ├── start               # Currently in profile
│   └── end                 # Currently in profile
├── profile                 # Developer identity only
│   └── show
└── [remove status]         # Empty, not needed
└── [remove telemetry]      # Merge into memory
```

**Changes:**
- Create `session` as first-class command
- Merge `telemetry emit-*` into `memory add` (telemetry is impl detail)
- Remove empty `status`
- Keep `profile` for identity only

### Option B: Minimal (Less Disruption)

Keep structure, fix naming:

```
raise
├── init
├── discover
├── memory
│   ├── query | build | list
│   └── add <type>          # Unified add command
├── profile
│   ├── show
│   ├── session start       # Subcommand group
│   └── session end
└── [remove status, telemetry]
```

### Option C: Status Quo + Cleanup

Minimal changes:
1. Remove empty `status` command
2. Rename `profile session-end` → `profile session-close` (match skill)
3. Document the three-system session pattern as intentional

---

## Skill Structure Analysis

### Current Naming: Consistent ✓

```
{domain}-{action}
├── session-start, session-close
├── epic-start, epic-design, epic-plan, epic-close
├── story-start, story-design, story-plan, story-implement, story-review, story-close
└── discover-start, discover-scan, discover-validate, discover-complete
```

### Lifecycle Completeness

| Domain | Start | Design | Plan | Implement | Review | Close |
|--------|-------|--------|------|-----------|--------|-------|
| Session | ✓ | - | - | - | - | ✓ |
| Epic | ✓ | ✓ | ✓ | - | - | ✓ |
| Feature | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Discovery | ✓ | - | - | - | ✓ (validate) | ✓ (complete) |

**Observation:** Feature has full lifecycle, Epic is missing implement/review (by design — epics contain features).

### Anomalies

| Skill | Issue |
|-------|-------|
| `discover-scan` | Verb differs from pattern (`scan` vs `design/plan/implement`) |
| `scripts` | Not a skill, seems misplaced |
| `framework-sync` | Utility, not workflow |

---

## Recommendations

### High Priority (Do Now)

1. **Remove `rai status`** — Empty command, no value
2. **Rename `profile session-end` → `profile session-close`** — Match skill naming
3. **Document session architecture** — Intentional three-system split

### Medium Priority (Consider for F&F)

4. **Consolidate telemetry into memory** — `memory add` with event emission as side effect
5. **Move `scripts/` out of skills** — It's not a skill

### Low Priority (Post-F&F)

6. **Create `rai session` command group** — First-class session management
7. **Unify `add-*` commands** — `rai memory add --type pattern "..."` vs separate commands

---

## Decision Required

Which option for F14.13?

- **A) Full restructure** — Cleaner ontology, more work, potential breaking changes
- **B) Minimal cleanup** — Remove status, fix naming, document
- **C) Status quo** — Document only, defer changes

**Recommendation:** Option B for F&F timeline. Option A for V3.
