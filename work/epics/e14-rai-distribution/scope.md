# Epic E14: Rai Distribution — Scope

> **Status:** IN PROGRESS
> **Branch:** `epic/e14/rai-distribution`
> **Created:** 2026-02-05
> **Target:** F&F Release (Feb 9)

---

## Objective

Enable new users to experience Rai as a knowledgeable partner from day one, with base identity, universal patterns, and internalized framework knowledge.

**Value proposition:** Users get a capable AI partner immediately — Rai knows the methodology, enforces gates, and guides process. This differentiates from blank-slate tools.

---

## Architecture Overview (ADR-022)

**Pluggable Base Rai** — Base content can come from bundled package (default) or corporate git repo (V3).

```
F&F (this epic):
  raise-cli package bundles base Rai
  raise init → copies bundled base to .raise/rai/

Post-F&F:
  ~/.rai/config.yaml can specify base_source: <git-url>
  raise base update → pulls from corporate repo

V3:
  Full corporate documentation + team-level overrides
```

### Identity Stack

```
1. Base Rai (bundled or git)  ← E14 scope (bundled only for F&F)
2. Personal (~/.rai/)         ← E7 complete
3. Project (.raise/rai/)      ← E3/E7 complete
4. Team (.raise/rai/team/)    ← V3 scope
```

---

## Features

### F&F Scope (16 SP)

| ID | Feature | Size | SP | Status | Description |
|----|---------|:----:|:--:|:------:|-------------|
| F14.1 | Base Identity Package | S | 2 | ✅ Done | Bundle core.md + perspective.md in package |
| F14.2 | Base Patterns Catalog | M | 3 | ✅ Done | Define ~20 universal methodology patterns |
| F14.3 | Methodology Core | S | 2 | ✅ Done | methodology.yaml with skills, gates, rules |
| F14.4 | Bootstrap on Init | M | 3 | Pending | Copy bundled base to .raise/rai/ during raise init |
| F14.5 | Two-Part MEMORY.md | M | 3 | Pending | Generate MEMORY.md with static process + dynamic context |
| F14.6 | Pattern Versioning | S | 2 | Pending | Add base/version fields to pattern schema |
| F14.7 | Base Show Command | XS | 1 | Pending | `raise base show` displays current base info |
| F14.15 | Multi-Developer Architecture | L | 5 | ✅ Done | Separate personal data from shared project data |

**Total F&F:** 8 features, 19 SP

### Post-F&F (Deferred)

| ID | Feature | Size | Description |
|----|---------|:----:|-------------|
| F14.8 | Config Support | S | `~/.rai/config.yaml` with base_source setting |
| F14.9 | Git Source Resolution | M | Clone/pull from git URL when configured |
| F14.10 | Base Update Command | S | `raise base update` pulls latest + applies |
| F14.11 | Update Detection | S | Detect version mismatch on session-start |

---

## In Scope (F&F)

**MUST:**
- Base identity files (core.md, perspective.md) bundled in `src/raise_cli/rai_base/`
- Universal methodology patterns (~20 base patterns) in JSONL
- methodology.yaml with skills list, gates, process rules
- Bootstrap flow in `raise init` copies bundled base to `.raise/rai/`
- Two-part MEMORY.md generation (static process + dynamic context)
- Pattern versioning schema (base: true, version: N)
- `raise base show` command
- Legacy file cleanup (graph.json, migration artifacts)

**SHOULD:**
- Base version embedded in manifest for future update detection

---

## Out of Scope

### Deferred to Post-F&F

| Item | Rationale |
|------|-----------|
| Git-based corporate base source | Adds complexity, not needed for F&F users |
| `raise base update` command | Requires git source support |
| `~/.rai/config.yaml` | Only needed for base_source override |
| Update detection on session-start | Nice-to-have, not blocking |

### Deferred to V3/Future

| Item | Rationale | Destination |
|------|-----------|-------------|
| Team/org shared patterns | Complex multi-tenant | E10 Collective Intelligence |
| Pattern marketplace | Community feature | Future |
| Cross-project sync | Complex state management | Future |
| AI-generated base patterns | Trust/quality concern | Keep human-curated |
| Corporate base documentation | Needs real corporate users | V3 |

---

## Package Structure

```
src/raise_cli/rai_base/
├── identity/
│   ├── core.md           # Rai's values, boundaries, essence
│   └── perspective.md    # How Rai approaches collaboration
├── memory/
│   └── patterns-base.jsonl   # ~20 universal methodology patterns
└── framework/
    └── methodology.yaml  # Skills, gates, rules → generates MEMORY.md
```

### methodology.yaml Schema

```yaml
version: 1

skills:
  session:
    - name: /session-start
      purpose: Begin session with context loading
      when: Start of any working session
    # ...

  epic:
    - name: /epic-start
      purpose: Create epic branch and scope commit
      when: Starting new epic
    # ...

gates:
  blocking:
    - before: epic design
      require: Epic branch exists (/epic-start)
    - before: feature work
      require: Feature branch and scope commit (/feature-start)
    # ...

principles:
  - name: TDD Always
    rule: RED-GREEN-REFACTOR, no exceptions
  # ...
```

---

## Bootstrap Flow (F&F)

```
raise init
    │
    ├── (existing) detect project, create manifest
    │
    ├── (NEW) Resolve base source
    │   F&F: always bundled (importlib.resources)
    │
    ├── (NEW) Copy base identity (if not exists)
    │   rai_base/identity/ → .raise/rai/identity/
    │
    ├── (NEW) Copy base patterns (merge with base: true)
    │   patterns-base.jsonl → .raise/rai/memory/patterns.jsonl
    │   Mark all with: base: true, version: 1
    │
    ├── (NEW) Generate MEMORY.md (two-part)
    │   Part 1: Static process from methodology.yaml
    │   Part 2: Dynamic context from project state
    │   Output: ~/.claude/projects/{hash}/memory/MEMORY.md
    │
    └── (existing) build graph, generate guardrails
```

---

## Done Criteria

### Per Feature
- [ ] Code implemented with type annotations
- [ ] Docstrings on all public APIs
- [ ] Component catalog updated (`dev/components.md`)
- [ ] Unit tests passing (>90% coverage)
- [ ] Quality checks pass (ruff, pyright, bandit)

### Epic Complete (F&F)
- [ ] All 8 F&F features complete
- [ ] `raise init` creates `.raise/rai/` with base identity + patterns
- [ ] Two-part MEMORY.md generated (process + context)
- [ ] Pattern versioning schema working (base: true)
- [ ] `raise base show` displays base info
- [ ] Legacy files cleaned up (graph.json, migration artifacts)
- [ ] New user simulation test passes
- [ ] Epic retrospective completed (`/epic-close`)
- [ ] Merged to v2

---

## Dependencies

```
F14.15 (Multi-Dev) ─── Foundation: personal vs shared paths
        │
        ↓
F14.1 (Identity) ──┐
F14.2 (Patterns) ──┼── F14.4 (Bootstrap) ── F14.5 (MEMORY.md)
F14.3 (Methodology)┘         │
                             ↓
                      F14.6 (Versioning)
                             ↓
                      F14.7 (Base Show)
```

**External:** None — builds on E3, E7, E11 (all complete)
**Sequencing:** F14.15 first — establishes path architecture for remaining features

---

## Milestones

| Milestone | Features | Target | Success Criteria |
|-----------|----------|--------|------------------|
| **M1: Base Assets** | F14.1, F14.2, F14.3 | Day 1-2 | Identity + patterns + methodology created |
| **M2: Bootstrap** | F14.4, F14.5 | Day 2-3 | `raise init` creates full .raise/rai/ + MEMORY.md |
| **M3: CLI** | F14.6, F14.7 | Day 3-4 | Versioning schema + `raise base show` |
| **M4: Validation** | — | Day 4 | New user simulation passes |

---

## Architecture References

| Decision | Document | Key Insight |
|----------|----------|-------------|
| Distribution mechanism | ADR-022 | Pluggable: bundled (F&F) or git (V3) |
| Identity structure | ADR-014 | Four-layer architecture |
| Memory format | ADR-016 | JSONL for patterns, MD for identity |

---

## Research Foundation

| Unknown | Synthesis | Key Finding |
|---------|-----------|-------------|
| Identity Layering | unknown-1-identity.md | Four layers, V3-ready schema |
| Framework Internalization | unknown-2-internalization.md | Hybrid: core in identity, details queryable |
| First Contact | unknown-3-first-contact.md | Progressive reveal (work first) |

**Research:** `work/research/rai-distribution/`

---

## Risks

| Risk | L | I | Mitigation |
|------|:-:|:-:|------------|
| Base patterns too opinionated | M | H | Start with ~20, iterate with feedback |
| MEMORY.md too large | M | M | Keep concise, link to details |
| Identity feels artificial | M | M | Keep authentic to E3 identity work |
| methodology.yaml schema wrong | M | M | Start simple, evolve based on MEMORY.md needs |

---

## Notes

### Why This Epic Matters

Without E14, users get CLI + skills but NOT Rai. The "reliable" promise depends on user discipline, not Rai guidance. With E14, Rai guides from day one.

### Design Principles

1. **F&F-scoped, V3-ready** — Bundled now, pluggable later (ADR-022)
2. **Additive updates only** — Personal patterns never modified
3. **Hybrid internalization** — Core knowledge in MEMORY.md, details queryable
4. **No friction first contact** — Work immediately, explain after value

### Base Patterns Preview (~20)

**Process:** TDD cycle, commit after task, full kata cycle, ask before subagents
**Technical:** Pydantic models, explicit CLI paths, type annotations
**Collaboration:** Direct communication, redirect when dispersing
**Lifecycle:** epic-start before design, feature-start before work, epic-close before merge

### Post-F&F Roadmap

```
F&F Complete
    ↓
Post-F&F: Git source support (F14.8-F14.11)
    ↓
V3: Corporate documentation + team overrides
```

---

## Implementation Plan

> Added by `/epic-plan` — 2026-02-05

### Feature Sequence

| Order | Feature | Size | Dependencies | Milestone | Rationale |
|:-----:|---------|:----:|--------------|-----------|-----------|
| 0 | F14.15 Multi-Dev Arch | M | None | M0 | Foundation: personal vs shared paths |
| 1 | F14.1 Base Identity | S | F14.15 | M1 | Content creation, can parallel |
| 2 | F14.2 Base Patterns | M | F14.15 | M1 | Content creation, can parallel |
| 3 | F14.3 Methodology | S | F14.15 | M1 | Content creation, can parallel |
| 4 | F14.4 Bootstrap | M | F14.1-3 | M2 | Integration, needs all content |
| 5 | F14.6 Versioning | S | F14.2 | M3 | Schema work, enables update tracking |
| 6 | F14.5 MEMORY.md | M | F14.3, F14.4 | M3 | Generation from methodology.yaml |
| 7 | F14.7 Base Show | XS | F14.4 | M4 | CLI polish, needs bootstrap |

### Milestones

| Milestone | Features | Target | Success Criteria | Demo |
|-----------|----------|--------|------------------|------|
| **M0: Multi-Dev** | F14.15 | Day 1 | Personal data separated from shared | No merge conflicts on sessions |
| **M1: Base Assets** | F14.1, F14.2, F14.3 | Day 1-2 | All content in `src/raise_cli/rai_base/` | Files exist, valid format |
| **M2: Bootstrap** | F14.4 | Day 2-3 | `raise init` copies base to `.raise/rai/` | Init creates identity + patterns |
| **M3: MEMORY.md** | F14.5, F14.6 | Day 3 | Auto-generated with skills/gates | MEMORY.md has full process |
| **M4: Complete** | F14.7 + validation | Day 4 | New user simulation passes | Full flow demo |

### Parallel Work Streams

```
Day 1 (Architecture + Content):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
F14.15 (Multi-Dev) ──────────► M0: Personal/Shared separation
        │
        ├── F14.1 (Identity)    ─────┐
        ├── F14.2 (Patterns)    ─────┼─► M1: Base Assets
        └── F14.3 (Methodology) ─────┘

Day 2 (Integration):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
F14.4 (Bootstrap) ───────────► M2: Bootstrap Working
F14.6 (Versioning) ──► (parallel, schema only)

Day 3 (Generation):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
F14.5 (MEMORY.md) ───────────► M3: MEMORY.md
F14.7 (Base Show) ──► (parallel, CLI only)

Day 4 (Validation):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
New user simulation ─────────► M4: Epic Complete
Buffer for fixes
```

### Progress Tracking

| Feature | Size | Status | Actual | Velocity | Notes |
|---------|:----:|:------:|:------:|:--------:|-------|
| F14.0 DX Quality Gate | M | ✅ Done | ~6 sessions | — | -5200 lines, graph consolidated |
| F14.1 Base Identity | S | ✅ Done | 1 session | — | Generic base identity |
| F14.2 Base Patterns | M | ✅ Done | 1 session | — | 20 universal patterns |
| F14.3 Methodology | S | ✅ Done | 1 session | — | 20 skills, gates, principles |
| F14.4 Bootstrap | M | Pending | — | — | |
| F14.5 MEMORY.md | M | Pending | — | — | |
| F14.6 Versioning | S | Pending | — | — | |
| F14.7 Base Show | XS | Pending | — | — | |
| F14.12 Memory Ontology | XS | ✅ Done | 1 session | — | graph→memory, simpler CLI |
| F14.13 Ontology Cleanup | M | ✅ Done | 90 min | 1.33x | CLI restructure, /skill-create, 9 patterns |
| F14.14 Skill CLI | M | ✅ Done | ~3 sessions | 1.5x | 4 CLI commands, skill audit, 79 new tests |
| F14.15 Multi-Dev Arch | L | ✅ Done | 2 sessions | — | Personal data separation |

**Milestone Progress:**
- [x] M0: Multi-Dev Architecture (Day 1)
- [x] M1: Base Assets (Day 1-2)
- [ ] M2: Bootstrap (Day 2-3)
- [ ] M3: MEMORY.md (Day 3)
- [ ] M4: Epic Complete (Day 4)

### Sequencing Risks

| Risk | L | I | Mitigation |
|------|:-:|:-:|------------|
| Pattern curation takes longer than expected | M | M | Start with 15, add more later |
| methodology.yaml schema needs iteration | M | M | Start simple, evolve |
| MEMORY.md generation complex | M | H | Template-based, not dynamic |

### Velocity Assumptions

- **Baseline:** 3x multiplier with kata cycle (PAT-082)
- **Day 1:** Content creation is fast (mostly copying/editing)
- **Day 2-3:** Integration work, normal velocity
- **Buffer:** Day 4 for validation and fixes

---

*Plan created: 2026-02-05*
*Next: F14.15 (multi-dev arch), then F14.1-F14.7*

---

## Legacy Cleanup (Pre-Epic Complete)

> **Added:** 2026-02-05 (drift review)
> **When:** Before M4 validation

### Files to Remove

| File | Location | Reason |
|------|----------|--------|
| `graph.json` | `.raise/rai/memory/` | Replaced by `index.json` (123KB legacy) |
| `index.jsonl.backup` | `.raise/rai/memory/sessions/` | Migration artifact from F14.15 |

### Verification

```bash
# Confirm index.json is working
uv run raise memory query "test" --limit 1

# Then remove legacy files
rm .raise/rai/memory/graph.json
rm .raise/rai/memory/sessions/index.jsonl.backup
rmdir .raise/rai/memory/sessions  # if empty
```

### Gitignore Updates (if not already done)

Ensure `.gitignore` includes:
```
.raise/rai/personal/
```

---

## F14.15: Multi-Developer Architecture

> **Priority:** HIGH — Must fix before F&F to avoid architectural debt
> **Size:** L (5 SP) — Upgraded after research showed memory system impact
> **Added:** 2026-02-05
> **Research:** RES-MULTIDEV-001 (config patterns), RES-MULTIDEV-002 (memory impact)

### Problem

Current architecture stores personal data in `.raise/rai/` (committed to git):
- `memory/sessions/index.jsonl` — 68 personal session entries
- `telemetry/signals.jsonl` — 1507 personal telemetry entries
- `memory/patterns.jsonl` — Mixed personal/project patterns

**Multi-developer issues:**
1. Merge conflicts on every PR (both devs modify sessions)
2. Mixed telemetry (Dev A's velocity mixed with Dev B's)
3. Privacy leak (session topics visible to all)
4. Pattern pollution (personal learnings become project patterns)

### Solution (Option B: Expanded Global Identity)

Three-tier architecture separating global developer identity from project data:

```
GLOBAL (~/.rai/) — Follows developer across repos:
  developer.yaml         # Identity, preferences, experience
  calibration.jsonl      # How Rai works with ME (universal)
  patterns.jsonl         # MY universal learnings

SHARED (.raise/rai/) — Project's Rai, committed:
  identity/              # Rai's project identity
  memory/
    patterns.jsonl       # Curated project patterns
    index.json           # Memory index

PERSONAL (.raise/rai/personal/) — My work HERE, gitignored:
  sessions/
    index.jsonl          # My sessions in this repo
  telemetry/
    signals.jsonl        # My signals in this repo
  calibration.jsonl      # Project-specific calibration
  patterns.jsonl         # Project-specific learnings
```

### Key Architectural Principle

**Graph as abstraction layer:** The memory graph is the PRIMARY query interface. Agents should NOT know which JSON file data came from. The graph:
1. Loads from all sources (global, shared, personal)
2. Merges with precedence rules
3. Returns unified results with provenance as metadata
4. Hides file system complexity from consumers

```
Agent queries: "patterns about TDD"
     ↓
Memory Graph (unified view)
     ↓
Returns: [{content: "...", source: "global"}, {content: "...", source: "project"}]
```

### In Scope

**MUST:**
- [ ] Add `get_personal_project_dir(project_root)` to `paths.py`
- [ ] Migrate session writing to personal dir
- [ ] Migrate telemetry writing to personal dir
- [ ] Migrate calibration to personal dir
- [ ] Add `.raise/rai/memory/sessions/` to `.gitignore`
- [ ] Add `.raise/rai/telemetry/` to `.gitignore`
- [ ] Migration: move existing personal data on first access
- [ ] Update `raise session` commands to use personal paths
- [ ] Update `raise memory emit-*` to use personal paths
- [ ] Update context builder to load from personal paths

**SHOULD:**
- [ ] Add `personal: true` field to pattern schema (future: promote to project)

### Out of Scope

- Pattern promotion workflow (personal → project)
- Cross-developer pattern sharing (V3/E10)
- Telemetry aggregation across developers

### Files to Modify

| File | Change |
|------|--------|
| `config/paths.py` | Add `get_personal_project_dir()` |
| `memory/writer.py` | Write sessions/calibration to personal |
| `telemetry/writer.py` | Write signals to personal |
| `context/builder.py` | Load sessions from personal |
| `cli/commands/memory.py` | Use personal paths |
| `cli/commands/session.py` | Use personal paths |
| `onboarding/migration.py` | Migrate existing data |
| `.gitignore` | Add personal data paths |

### Migration Strategy

On first access to personal data:
1. Check if `~/.rai/projects/{hash}/` exists
2. If not, create and migrate from `.raise/rai/`:
   - Copy `sessions/index.jsonl`
   - Copy `telemetry/signals.jsonl`
   - Copy `calibration.jsonl`
3. After migration, data stays in personal dir

**Existing `.raise/rai/` files:** Left in place (git history), but gitignored for future.

### Done Criteria

- [ ] Personal data written to `~/.rai/projects/{hash}/`
- [ ] Personal paths gitignored
- [ ] Existing data migrated on first access
- [ ] `raise session start` works with new paths
- [ ] `raise memory emit-*` works with new paths
- [ ] Tests for migration and new paths
- [ ] No merge conflicts on sessions/telemetry in multi-dev scenario

---

## F14.5: Two-Part MEMORY.md Generation

> **Size:** M (3 SP)
> **Dependencies:** F14.3 (methodology.yaml), F14.4 (bootstrap)
> **Clarified:** 2026-02-05 (drift review)

### Problem

MEMORY.md serves two purposes that conflict with simple auto-generation:

1. **Static process knowledge** — Skills, gates, rules (from methodology.yaml)
2. **Dynamic project context** — Current epic, patterns, deadlines (from project state)

Original scope said "generate from methodology.yaml" which would lose dynamic context.

### Solution: Two-Part Architecture

MEMORY.md has two distinct sections:

```markdown
# Rai Memory — {project_name}

> Permanent knowledge for this project. Loaded into system prompt.

---

## PART 1: RaiSE Process (from methodology.yaml)

### Work Lifecycle
[Generated from methodology.yaml skills section]

### Gate Requirements
[Generated from methodology.yaml gates section]

### Available Skills
[Generated from methodology.yaml skills list]

### Critical Process Rules
[Generated from methodology.yaml principles section]

---

## PART 2: Project Context (from project state)

### Current State
[Generated from: active epic, feature, deadlines]

### Key Patterns
[Generated from: top N patterns by relevance]

### Branch Model
[Generated from: manifest.yaml or detected git structure]

---

*Last updated: {timestamp}*
```

### Generation Logic

**Part 1 (Static):** Generated once during `raise init`, updated on `raise base update` (post-F&F)

**Part 2 (Dynamic):** Regenerated on:
- `raise memory build` (explicit)
- `raise session start` (optional flag: `--refresh-memory`)
- When stale (>24h since last update)

### In Scope

**MUST:**
- [ ] Parse methodology.yaml to generate Part 1
- [ ] Query project state for Part 2 (epic, patterns, deadlines from CLAUDE.local.md)
- [ ] Generate to `~/.claude/projects/{hash}/memory/MEMORY.md`
- [ ] Preserve user edits in designated "custom" section (if present)
- [ ] Add `raise memory generate` command (explicit generation)

**SHOULD:**
- [ ] Auto-refresh on `raise session start`

### Out of Scope

- Real-time updates (too complex for F&F)
- Per-session MEMORY.md variants

### Files to Modify

| File | Change |
|------|--------|
| `memory/generator.py` | NEW: MEMORY.md generation logic |
| `cli/commands/memory.py` | Add `generate` subcommand |
| `onboarding/init.py` | Call generator after bootstrap |

### Done Criteria

- [ ] `raise init` generates two-part MEMORY.md
- [ ] `raise memory generate` regenerates from current state
- [ ] Part 1 matches methodology.yaml content
- [ ] Part 2 reflects current epic/patterns
- [ ] Tests for generation logic
