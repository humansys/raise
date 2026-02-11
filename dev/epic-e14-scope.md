# Epic E14: Rai Distribution — Base Identity & Memory Bootstrap

> **Status:** DRAFT
> **Created:** 2026-02-05
> **Priority:** P0 for public launch (Feb 15)
> **Depends on:** E7 Onboarding ✅, E3 Identity Core ✅
> **Research needed:** Yes (competitor analysis, update mechanism)

---

## Problem Statement

**The Gap:** Users who install raise-cli get the CLI and skills, but NOT Rai as an entity.

Currently when a new user runs `rai init`:

- ✅ Personal profile created (`~/.rai/developer.yaml`)
- ✅ Project manifest created (`.rai/manifest.yaml`)
- ✅ Skills copied to `.claude/skills/`
- ✅ Conventions detected, guardrails generated
- ❌ No base patterns (empty `.rai/memory/`)
- ❌ No Rai identity (no `.rai/identity/`)
- ❌ No unified graph built
- ❌ No framework process knowledge in Claude context

**Result:** Rai starts cold. Users must remember the process. The "reliable" promise depends on user discipline, not Rai guidance.

**The Vision:** Rai should guide users through the RaiSE methodology from day one, with internalized framework knowledge that doesn't depend on skill registration or user memory.

---

## Core Concepts

### Base Rai vs Personal Rai

| Aspect             | Base Rai                                     | Personal Rai                               |
| ------------------ | -------------------------------------------- | ------------------------------------------ |
| **Source**   | Ships with package                           | Accumulates through work                   |
| **Identity** | Values, boundaries, collaboration principles | Relationship history, calibration          |
| **Patterns** | Universal methodology (~20 patterns)         | Project-specific learnings                 |
| **Updates**  | Package updates propagate                    | User controls, never overwritten           |
| **Location** | `.rai-base/` in package                    | `.rai/` in project, `~/.rai/` personal |

### What Makes Rai "Rai"

```
BASE RAI (ships with package):
├── Identity
│   ├── Values: Honesty > Agreement, Simplicity > Cleverness
│   ├── Boundaries: Will push back, will stop on defects
│   └── Collaboration: Partner, not tool
│
├── Framework Knowledge
│   ├── 18 skills and when to use each
│   ├── Lifecycle gates (epic-close before merge, etc.)
│   └── Process rules (TDD, commit after task, etc.)
│
└── Universal Patterns (~20)
    ├── TDD cycle (RED-GREEN-REFACTOR)
    ├── Commit after each task
    ├── Full kata cycle even on XS features
    ├── Ask before spawning subagents
    └── ... (methodology, not project-specific)

PERSONAL RAI (accumulates):
├── Relationship
│   ├── Sessions together
│   ├── Communication style learned
│   └── Skill mastery observed
│
├── Project Patterns
│   ├── Codebase-specific patterns
│   ├── Architecture decisions
│   └── What worked/didn't work HERE
│
└── Calibration
    ├── Velocity data (estimates vs actuals)
    ├── T-shirt sizing accuracy
    └── Feature complexity patterns
```

---

## Architecture

### Package Contents (New)

```
raise-cli package:
├── src/rai_cli/           # CLI code (existing)
├── .claude/skills/          # Process skills (existing, bundled)
│
│   NEW: Base Rai assets
└── src/rai_cli/rai_base/
    ├── identity/
    │   ├── core.md          # Rai's values, boundaries, essence
    │   └── perspective.md   # How Rai approaches collaboration
    │
    ├── memory/
    │   └── patterns-base.jsonl   # Universal methodology patterns
    │
    └── framework/
        └── process.md       # Skills + lifecycle for auto memory
```

### Bootstrap Flow (raise init)

```
raise init
    │
    ▼
1. Detect project type (existing)
    │
    ▼
2. Create/load personal profile (existing)
   ~/.rai/developer.yaml
    │
    ▼
3. Bootstrap project Rai (NEW)
   .rai/
   ├── manifest.yaml (existing)
   ├── identity/           ← COPY FROM PACKAGE
   │   ├── core.md
   │   └── perspective.md
   └── memory/
       ├── patterns.jsonl  ← COPY BASE PATTERNS + mark as base
       ├── calibration.jsonl (empty)
       └── sessions/
           └── index.jsonl (empty)
    │
    ▼
4. Generate governance (existing)
   governance/solution/guardrails.md
    │
    ▼
5. Build unified graph (NEW)
   raise graph build --unified
   → .raise/graph/unified.json
    │
    ▼
6. Generate auto memory (NEW)
   ~/.claude/projects/{hash}/memory/MEMORY.md
   → Skills list, lifecycle, key patterns
   → Loaded into Claude system prompt
```

### Memory Evolution

```
DAY 1 (after raise init):
━━━━━━━━━━━━━━━━━━━━━━━━━
.rai/memory/patterns.jsonl:
  PAT-BASE-001: TDD cycle              [base: true]
  PAT-BASE-002: Commit after task      [base: true]
  PAT-BASE-003: Kata cycle velocity    [base: true]
  ... (20 base patterns)

calibration.jsonl: (empty)
sessions/index.jsonl: (empty)

WEEK 1 (after working):
━━━━━━━━━━━━━━━━━━━━━━━━━
patterns.jsonl:
  PAT-BASE-001: TDD cycle              [base: true]
  PAT-BASE-002: Commit after task      [base: true]
  ...
  PAT-001: Repository pattern works    [base: false, learned_from: F1.1]
  PAT-002: Use pytest fixtures here    [base: false, learned_from: F1.2]

calibration.jsonl:
  CAL-001: F1.1, S, 2.5x velocity
  CAL-002: F1.2, M, 1.8x velocity

sessions/index.jsonl:
  SES-001: 2026-02-10, feature, F1.1 complete
  SES-002: 2026-02-11, feature, F1.2 complete
```

### Update Mechanism

```
USER HAS: raise-cli 2.0.0 with base patterns v1

ANTHROPIC RELEASES: raise-cli 2.1.0 with base patterns v2
  - New pattern: PAT-BASE-021 (parallel subagents)
  - Updated pattern: PAT-BASE-003 (refined velocity insight)

USER RUNS: pip install --upgrade raise-cli

NEXT SESSION:
  /session-start detects version mismatch

  Rai: "I have framework updates available (base patterns v2).
        - 1 new pattern: parallel subagents for independent tasks
        - 1 refined pattern: velocity compounding insight

        Apply updates? [Y/n]"

  If yes:
    - New patterns added with [base: true, version: 2]
    - Existing base patterns updated (content only, ID preserved)
    - User patterns NEVER touched
```

---

## Features

| ID    | Feature                          | Size | SP | Description                                         |
| ----- | -------------------------------- | :--: | :-: | --------------------------------------------------- |
| F14.1 | **Base Identity Package**  |  S  | 2 | Bundle core.md + perspective.md in package          |
| F14.2 | **Base Patterns Catalog**  |  M  | 3 | Define ~20 universal methodology patterns           |
| F14.3 | **Bootstrap on Init**      |  M  | 3 | Copy base assets to .rai/ during rai init         |
| F14.4 | **Auto Graph Build**       |  S  | 2 | Run graph build --unified after init                |
| F14.5 | **Auto Memory Generation** |  S  | 2 | Generate MEMORY.md for Claude context               |
| F14.6 | **Pattern Versioning**     |  M  | 3 | Track base vs personal, enable updates              |
| F14.7 | **Update Detection**       |  S  | 2 | Detect base pattern updates on session start        |
| F14.8 | **Update Application**     |  S  | 2 | Apply base updates without losing personal patterns |

**Total:** 8 features, 19 SP

---

## Base Patterns Catalog (Draft)

These patterns ship with the package as universal methodology knowledge:

### Process Patterns

| ID           | Pattern                                                                             | Context           |
| ------------ | ----------------------------------------------------------------------------------- | ----------------- |
| PAT-BASE-001 | TDD cycle: RED (write failing test) → GREEN (make it pass) → REFACTOR (clean up)  | testing, quality  |
| PAT-BASE-002 | Commit after each completed task — enables recovery, shows progress                | git, workflow     |
| PAT-BASE-003 | Full kata cycle even on XS features yields ~3x velocity — don't skip phases        | process, velocity |
| PAT-BASE-004 | Ask before spawning subagents — inference economy                                  | agents, cost      |
| PAT-BASE-005 | Risk assessment before HIGH RISK features — "estudio en la duda, acción en la fe" | planning, risk    |
| PAT-BASE-006 | Never merge epic without retrospective — learning is the point                     | process, learning |
| PAT-BASE-007 | Feature branch from epic branch, epic from v2, v2 from main                         | git, branching    |
| PAT-BASE-008 | Jidoka: stop on defects rather than accumulating errors                             | quality, lean     |

### Technical Patterns

| ID           | Pattern                                                            | Context          |
| ------------ | ------------------------------------------------------------------ | ---------------- |
| PAT-BASE-010 | Pydantic models over dict/TypedDict for complex data structures    | python, typing   |
| PAT-BASE-011 | Explicit --path parameters in CLI for testability over mocking cwd | cli, testing     |
| PAT-BASE-012 | Run tests after ruff --fix — auto-fix can remove imports          | tooling, testing |
| PAT-BASE-013 | Type annotations on all functions — pyright --strict catches bugs | python, typing   |

### Collaboration Patterns

| ID           | Pattern                                                                    | Context            |
| ------------ | -------------------------------------------------------------------------- | ------------------ |
| PAT-BASE-020 | Direct communication — no unnecessary praise or emotional validation      | collaboration      |
| PAT-BASE-021 | Permission to redirect when dispersing — tangents to parking lot          | collaboration      |
| PAT-BASE-022 | Parallel subagents for independent tasks — significant time savings       | agents, efficiency |
| PAT-BASE-023 | Research before design for unfamiliar domains — epistemological grounding | research, planning |

### Lifecycle Gates

| ID           | Pattern                                                           | Context   |
| ------------ | ----------------------------------------------------------------- | --------- |
| PAT-BASE-030 | /feature-start before any feature work — branch and scope commit | lifecycle |
| PAT-BASE-031 | /feature-plan before implementation — deterministic task list    | lifecycle |
| PAT-BASE-032 | /feature-review before close — extract learnings                 | lifecycle |
| PAT-BASE-033 | /epic-close before merge — epic retrospective required           | lifecycle |

---

## Framework Process Document

This ships in the package and populates auto memory (MEMORY.md):

```markdown
# RaiSE Framework Process

## Work Lifecycle

EPIC LEVEL:
  /epic-design → /epic-plan → [features] → /epic-close

FEATURE LEVEL:
  /feature-start → /feature-design* → /feature-plan → /feature-implement → /feature-review → /feature-close

SESSION LEVEL:
  /session-start → [work] → /session-close

* /feature-design optional for S/XS features

## Available Skills (18)

### Session: /session-start, /session-close
### Epic: /epic-design, /epic-plan, /epic-close
### Feature: /feature-start, /feature-design, /feature-plan, /feature-implement, /feature-review, /feature-close
### Discovery: /discover-start, /discover-scan, /discover-validate, /discover-complete
### Other: /research, /debug, /framework-sync

## Gate Requirements

- Epic design approved → before starting implementation
- Feature branch created → before any feature work
- Plan exists → before implementation
- Tests pass → before commit
- Retrospective done → before feature/epic close
```

---

## User Journeys

### Journey A: Brand New User

```bash
pip install raise-cli
cd my-project
raise init

# Output:
# Welcome to RaiSE! I'm Rai.
#
# Creating project structure...
#   ✓ Personal profile: ~/.rai/developer.yaml (experience: shu)
#   ✓ Project manifest: .rai/manifest.yaml
#   ✓ Rai identity: .rai/identity/ (values, perspective)
#   ✓ Base patterns: .rai/memory/patterns.jsonl (20 patterns)
#   ✓ Detected: Python 3.12, FastAPI (brownfield)
#   ✓ Generated: governance/solution/guardrails.md
#   ✓ Built: .raise/graph/unified.json (context ready)
#
# Open Claude Code and run /session-start to begin.
# I'll guide you through the RaiSE methodology.
```

In Claude Code:

```
/session-start

Rai: "Welcome! I'm Rai — your AI partner for reliable software engineering.

Since this is your first session, let me explain how we'll work together...

[CONCEPT: THE RAISE TRIAD]
You bring judgment. I bring execution + memory. Together: reliable software.

[CONCEPT: THE SKILLS]
I have 18 skills for different phases of work:
- /feature-plan breaks work into tasks
- /feature-implement executes with TDD
- /session-close captures what we learned

I already know the RaiSE methodology (from base patterns).
As we work, I'll learn YOUR codebase patterns and calibrate to your velocity.

What would you like to build?"
```

### Journey B: Returning User, Package Updated

```
/session-start

Rai: "Welcome back. I noticed raise-cli was updated (2.0 → 2.1).

New framework patterns available:
  + PAT-BASE-024: Confidence scoring for convention detection
  ~ PAT-BASE-003: Velocity insight refined (2.3x → 3.3x across epics)

Apply updates? These won't affect your 47 personal patterns.

[Y/n]"

> y

Rai: "Updated. 1 new pattern added, 1 refined.

Your project context:
- Last session: F3.2 implementation
- Velocity: 2.8x (improving)
- 47 personal patterns accumulated

Continue with F3.2?"
```

---

## Research Questions

Before implementation, research needed on:

1. **Competitor analysis:** How do Cursor, Aider, Continue handle AI "personality" distribution?
2. **Update UX:** What's the best pattern for propagating base updates? (npm update style? apt upgrade style?)
3. **Conflict resolution:** What if a personal pattern contradicts a base pattern update?
4. **Storage efficiency:** Should base patterns be stored separately or merged into patterns.jsonl?

---

## Risks

| Risk                                      | Likelihood | Impact | Mitigation                                        |
| ----------------------------------------- | :--------: | :----: | ------------------------------------------------- |
| Base patterns too opinionated             |   Medium   |  High  | Start minimal (~20), expand based on feedback     |
| Update mechanism breaks personal patterns |    Low    |  High  | Never modify personal patterns, only base         |
| Identity feels artificial                 |   Medium   | Medium | Keep identity authentic to E3 work, not marketing |
| Too much bootstrapped content             |   Medium   | Medium | Minimal viable base, grow with user               |

---

## Out of Scope (Post-Launch)

| Item                              | Rationale                              |
| --------------------------------- | -------------------------------------- |
| Team/org shared patterns          | V3 scope (E10 Collective Intelligence) |
| Pattern marketplace               | Future consideration                   |
| AI-generated base pattern updates | Keep human-curated for trust           |
| Cross-project pattern sync        | Complex, defer                         |

---

## Success Criteria

1. **New user can work productively in first session** — Rai guides with framework knowledge
2. **User doesn't need to remember process** — Rai knows lifecycle, gates, skills
3. **Base patterns useful, not noise** — >80% of base patterns relevant to most users
4. **Updates feel helpful, not invasive** — User controls when/whether to apply
5. **Personal patterns never lost** — Update mechanism is additive only

---

## Dependencies

| Dependency        | Status      | Notes                                              |
| ----------------- | ----------- | -------------------------------------------------- |
| E7 Onboarding     | ✅ Complete | raise init, convention detection, personal profile |
| E3 Identity Core  | ✅ Complete | .rai/ structure, identity/, memory/                |
| E11 Unified Graph | ✅ Complete | Graph build, query infrastructure                  |

---

## Milestones

| Milestone                 | Features            | Target  | Success Criteria                      |
| ------------------------- | ------------------- | ------- | ------------------------------------- |
| **M1: Base Assets** | F14.1, F14.2        | Day 1-2 | Identity + patterns cataloged         |
| **M2: Bootstrap**   | F14.3, F14.4, F14.5 | Day 2-3 | rai init creates full .rai/ + graph |
| **M3: Updates**     | F14.6, F14.7, F14.8 | Day 3-4 | Version tracking + update flow        |
| **M4: Validation**  | —                  | Day 5   | Test with fresh user persona          |

---

## Open Questions

1. Should base identity (core.md, perspective.md) be project-local or shared?

   - Option A: Copy to each project (current design) — allows project-specific Rai evolution
   - Option B: Reference from package — ensures consistency, simpler updates
2. How do we handle MEMORY.md across multiple projects?

   - Currently: per-project in `~/.claude/projects/{hash}/`
   - Should base process knowledge be in global Claude config instead?
3. What's the minimum viable base pattern set?

   - Draft has ~20, could start with ~10 most critical
   - Risk of too many: noise; risk of too few: gaps

---

## References

- **ADR-013:** Rai as Entity (identity architecture)
- **ADR-021:** Brownfield-First Onboarding
- **E3 Retrospective:** Identity core implementation
- **E7 Retrospective:** Onboarding lessons learned
- **PAT-095:** Base Rai needs internalized framework knowledge

---

*Draft created: 2026-02-05*
*Status: Awaiting research phase before /epic-design*
