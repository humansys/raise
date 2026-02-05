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
  raise init → copies bundled base to .rai/

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
3. Project (.rai/)            ← E3/E7 complete
4. Team (.rai/team/)          ← V3 scope
```

---

## Features

### F&F Scope (16 SP)

| ID | Feature | Size | SP | Status | Description |
|----|---------|:----:|:--:|:------:|-------------|
| F14.1 | Base Identity Package | S | 2 | Pending | Bundle core.md + perspective.md in package |
| F14.2 | Base Patterns Catalog | M | 3 | Pending | Define ~20 universal methodology patterns |
| F14.3 | Methodology Core | S | 2 | Pending | methodology.yaml with skills, gates, rules |
| F14.4 | Bootstrap on Init | M | 3 | Pending | Copy bundled base to .rai/ during raise init |
| F14.5 | Auto MEMORY.md Generation | M | 3 | Pending | Generate Claude auto memory from methodology.yaml |
| F14.6 | Pattern Versioning | S | 2 | Pending | Add base/version fields to pattern schema |
| F14.7 | Base Show Command | XS | 1 | Pending | `raise base show` displays current base info |

**Total F&F:** 7 features, 16 SP

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
- Bootstrap flow in `raise init` copies bundled base to `.rai/`
- Auto MEMORY.md generation for Claude context
- Pattern versioning schema (base: true, version: N)
- `raise base show` command

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
    ├── (NEW) Copy base identity
    │   rai_base/identity/ → .rai/identity/
    │
    ├── (NEW) Copy base patterns
    │   patterns-base.jsonl → .rai/memory/patterns.jsonl
    │   Mark all with: base: true, version: 1
    │
    ├── (NEW) Generate MEMORY.md
    │   Parse methodology.yaml → ~/.claude/projects/{hash}/memory/MEMORY.md
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
- [ ] All 7 F&F features complete
- [ ] `raise init` creates `.rai/` with base identity + patterns
- [ ] MEMORY.md generated with skills and gates
- [ ] Pattern versioning schema working (base: true)
- [ ] `raise base show` displays base info
- [ ] New user simulation test passes
- [ ] Epic retrospective completed (`/epic-close`)
- [ ] Merged to v2

---

## Dependencies

```
F14.1 (Identity) ──┐
F14.2 (Patterns) ──┼── F14.4 (Bootstrap) ── F14.5 (MEMORY.md)
F14.3 (Methodology)┘         │
                             ↓
                      F14.6 (Versioning)
                             ↓
                      F14.7 (Base Show)
```

**External:** None — builds on E3, E7, E11 (all complete)

---

## Milestones

| Milestone | Features | Target | Success Criteria |
|-----------|----------|--------|------------------|
| **M1: Base Assets** | F14.1, F14.2, F14.3 | Day 1-2 | Identity + patterns + methodology created |
| **M2: Bootstrap** | F14.4, F14.5 | Day 2-3 | `raise init` creates full .rai/ + MEMORY.md |
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
| 1 | F14.1 Base Identity | S | None | M1 | Content creation, can parallel |
| 2 | F14.2 Base Patterns | M | None | M1 | Content creation, can parallel |
| 3 | F14.3 Methodology | S | None | M1 | Content creation, can parallel |
| 4 | F14.4 Bootstrap | M | F14.1-3 | M2 | Integration, needs all content |
| 5 | F14.6 Versioning | S | F14.2 | M3 | Schema work, enables update tracking |
| 6 | F14.5 MEMORY.md | M | F14.3, F14.4 | M3 | Generation from methodology.yaml |
| 7 | F14.7 Base Show | XS | F14.4 | M4 | CLI polish, needs bootstrap |

### Milestones

| Milestone | Features | Target | Success Criteria | Demo |
|-----------|----------|--------|------------------|------|
| **M1: Base Assets** | F14.1, F14.2, F14.3 | Day 1 | All content in `src/raise_cli/rai_base/` | Files exist, valid format |
| **M2: Bootstrap** | F14.4 | Day 2 | `raise init` copies base to `.rai/` | Init creates identity + patterns |
| **M3: MEMORY.md** | F14.5, F14.6 | Day 3 | Auto-generated with skills/gates | MEMORY.md has full process |
| **M4: Complete** | F14.7 + validation | Day 4 | New user simulation passes | Full flow demo |

### Parallel Work Streams

```
Day 1 (Content Creation — All Parallel):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
F14.1 (Identity)    ─────┐
F14.2 (Patterns)    ─────┼─► M1: Base Assets
F14.3 (Methodology) ─────┘

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
| F14.1 Base Identity | S | Pending | — | — | |
| F14.2 Base Patterns | M | Pending | — | — | |
| F14.3 Methodology | S | Pending | — | — | |
| F14.4 Bootstrap | M | Pending | — | — | |
| F14.5 MEMORY.md | M | Pending | — | — | |
| F14.6 Versioning | S | Pending | — | — | |
| F14.7 Base Show | XS | Pending | — | — | |

**Milestone Progress:**
- [ ] M1: Base Assets (Day 1)
- [ ] M2: Bootstrap (Day 2)
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
*Next: F14.1, F14.2, F14.3 (parallel)*
