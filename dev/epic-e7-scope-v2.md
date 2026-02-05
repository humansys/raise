# Epic E7: Onboarding & Reliability Setup - Scope

> **Status:** IN PROGRESS
> **Branch:** `feature/e7/onboarding`
> **Created:** 2026-02-02 (original)
> **Design complete:** 2026-02-04
> **Target:** Feb 9, 2026 (Friends & Family pre-launch)
> **Research:**
>   - `work/research/openclaw-onboarding/` (RES-ONBOARD-001)
>   - `work/research/onboarding-dx-competitors/` (RES-ONBOARD-DX-001)
> **ADR:** ADR-021 Brownfield-First Onboarding
> **Depends on:** E13 Discovery ✅, E9 Phase 1 ✅

---

## Objective

Enable developers to adopt RaiSE with confidence, understanding, and a personalized relationship with Rai that grows over time.

**Value proposition:**
- **First-time users:** Guided introduction to RaiSE concepts (Shu)
- **Experienced users:** Efficient setup respecting their time (Ha/Ri)
- **Brownfield:** Auto-detection + governance = reliable from day one
- **Cross-project:** Rai remembers YOU, not just your project

**The shift:** Rai is no longer Emilio's private partner. Rai is about to meet Fer, and other F&F developers. Each relationship is unique.

---

## Core Principles

### 1. Onboarding IS Education

The setup process teaches RaiSE concepts:
- Why governance matters
- Why conventions are detected
- Why reliability requires attention

Not "click through" but "understand why."

### 2. Adaptive Interaction

Rai adapts to each developer's experience:

| Level | Sessions | Interaction Style |
|-------|----------|-------------------|
| **Shu (守)** | 0-5 | Explain everything, guide each step |
| **Ha (破)** | 6-20 | Explain new concepts, efficient on known |
| **Ri (離)** | 21+ | Minimal ceremony, maximum efficiency |

### 3. Project + Personal Memory

| Scope | What Lives There |
|-------|------------------|
| **Project** (`.rai/`) | Conventions, components, calibration, project sessions |
| **Personal** (`~/.rai/`) | Experience level, communication style, mastered skills, universal patterns |

---

## User Personas (F&F)

| Persona | Experience | Project | Priority |
|---------|------------|---------|:--------:|
| **Fer** | New to RaiSE (Shu) | Existing codebase | P0 |
| **Emilio** | Expert (Ri) | raise-commons + others | P0 |
| **New F&F dev** | New to RaiSE (Shu) | Greenfield or brownfield | P1 |

---

## User Journeys

### Journey A: First-Time Developer (Fer) + Brownfield

```bash
pip install raise-cli
cd existing-api

raise init
# Creating ~/.rai/developer.yaml (first time using RaiSE)
# Detected: Brownfield project (47 files)
#
# Open Claude Code and run /session-start to complete setup.
# I'll guide you through understanding your project.
```

In Claude Code:
```
/session-start

Rai: "Welcome to RaiSE! I'm Rai — your AI partner for reliable software
engineering.

I notice this is your first time working with me. Let me explain how
we'll collaborate...

[CONCEPT: THE RAISE TRIAD]
You bring intuition and judgment. I bring execution and memory.
Together: reliable software at AI speed.

[CONCEPT: WHY CONVENTIONS MATTER]
Before I write code in your project, I need to understand YOUR patterns.
AI that ignores existing conventions creates inconsistent codebases.
That's not 'reliable' — that's just 'fast.'

Let me scan your project...

[DISCOVERY WITH EXPLANATION]
Found 47 files. Detected:
  • Python 3.12, FastAPI, SQLAlchemy
  • 4-space indentation (all files)
  • Repository pattern in src/repositories/
  • pytest in tests/

[CONCEPT: GUARDRAILS]
I'm creating 'guardrails' — rules I commit to following. Think of it
as our contract. These go in governance/solution/guardrails.md.

Here's what I detected:
  ✓ Indentation: 4 spaces (I'll never use tabs or 2 spaces)
  ✓ Architecture: Repository pattern (new data access goes in repositories/)
  ✓ Testing: pytest in tests/ (I'll put tests there, not elsewhere)

Anything look wrong? This matters — I'll follow these strictly.

[USER REVIEWS]

Great. Setup complete. You now understand:
  ✓ Why we detect conventions (reliability)
  ✓ What guardrails are (our contract)
  ✓ How project memory works (conventions stay with code)

What would you like to build? I can help you plan it with /feature-plan."
```

**Time to first productive work:** ~10 minutes (includes learning)

### Journey B: Experienced Developer (Emilio) + New Project

```bash
cd new-project
raise init
# Found ~/.rai/developer.yaml (welcome back, Emilio)
# Detected: Greenfield project
#
# Open Claude Code. You know the drill.
```

In Claude Code:
```
/session-start

Rai: "New project, greenfield. No conventions to detect yet.

Created minimal CLAUDE.md and skills. Define conventions as you build —
I'll learn and codify them.

What are we building?"
```

**Time to first work:** ~2 minutes

### Journey C: Experienced Developer + Brownfield

```bash
cd another-existing-project
raise init
# Found ~/.rai/developer.yaml (experience_level: ri)
# Detected: Brownfield (63 files, TypeScript/React)
# Running discovery... Done.
# Generated guardrails.md (6 conventions, HIGH confidence)
#
# Review governance/solution/guardrails.md if needed.
```

In Claude Code:
```
/session-start

Rai: "Brownfield. 63 files, React/TypeScript. 12 components cataloged.
Guardrails generated from detected conventions.

What are we working on?"
```

**Time to first work:** ~3 minutes

---

## Features (17 SP)

| ID | Feature | Size | SP | Status | Description |
|----|---------|:----:|:--:|:------:|-------------|
| F7.1 | **`raise init` Command** | M | 3 | Pending | Core initialization with project detection |
| F7.2 | **Convention Detection** | M | 3 | Pending | Auto-detect code style, naming, structure |
| F7.3 | **Governance Generation** | S | 2 | ✅ Done | Generate guardrails.md from conventions |
| F7.4 | **Enhanced CLAUDE.md** | S | 2 | ✅ Done | Context-rich with architecture, components |
| F7.5 | **`raise status` Command** | XS | 1 | Pending | Project health check |
| F7.6 | **Skills Bundling** | XS | 1 | ✅ Done | Skills in package, copy on init |
| F7.7 | **Guided First Session** | M | 3 | ✅ Done | Educational onboarding in /session-start |
| F7.8 | **Personal Memory** | S | 2 | ✅ Done | ~/.rai/developer.yaml + adaptive interaction |
| F7.9 | **Emilio Migration** | XS | 1 | ✅ Done | Bootstrap Emilio's personal profile from history |

**Total:** 9 features, 17 SP (~1.5-2 days with kata cycle @ 2x velocity)

---

## Personal Memory Architecture

### File Structure

```
~/.rai/
└── developer.yaml    # Personal profile (cross-project)

project/.rai/
├── memory/           # Project-specific memory
│   ├── patterns.jsonl
│   ├── calibration.jsonl
│   └── sessions/
└── manifest.yaml     # Project metadata
```

### Personal Profile Schema

```yaml
# ~/.rai/developer.yaml
# Rai's memory of YOU (not your projects)

name: Fer
experience_level: shu        # shu | ha | ri

communication:
  style: explanatory         # explanatory | balanced | direct
  language: es               # for casual moments
  preferences:
    skip_praise: false
    detailed_explanations: true

skills_mastered: []          # Populated as you use skills

universal_patterns: []       # Patterns that apply everywhere

# Auto-updated
sessions_total: 1
first_session: 2026-02-05
last_session: 2026-02-05
projects:
  - path: /home/fer/code/my-api
    sessions: 1
```

### Experience Progression

```
Sessions 0-5   → Shu (explain everything)
Sessions 6-20  → Ha (explain new, efficient on known)
Sessions 21+   → Ri (minimal ceremony)
```

Progression is automatic but can be overridden:
```yaml
experience_level: ha  # Manual override
experience_locked: true  # Don't auto-progress
```

### Skill Mastery Tracking

```python
# After 3 uses of a skill, consider it "familiar"
# After successful completion without guidance, "mastered"

if skill_uses[skill] >= 3 and skill not in skills_mastered:
    skills_mastered.append(skill)
```

Mastered skills get less explanation:
```
# First time using /feature-plan
Rai: "Let's use /feature-plan. This skill breaks down what you want
into atomic tasks. Here's how it works..."

# After mastery
Rai: "Breaking this into tasks..."
```

---

## Migration: Emilio's Profile

Emilio has 40+ sessions of history. We bootstrap his personal profile:

```yaml
# ~/.rai/developer.yaml (migrated)

name: Emilio
experience_level: ri

communication:
  style: direct
  language: en              # es for casual
  preferences:
    skip_praise: true
    detailed_explanations: false
    redirect_when_dispersing: true

skills_mastered:
  - session-start
  - session-close
  - feature-design
  - feature-plan
  - feature-implement
  - feature-review
  - feature-start
  - feature-close
  - epic-design
  - epic-plan
  - research
  - debug
  - discover-start
  - discover-scan
  - discover-validate
  - discover-complete

universal_patterns:
  - "Commit after each completed task"
  - "TDD for complex features"
  - "Ask before spawning subagents"
  - "Inference economy: gather with tools, think with inference"
  - "Permission granted to redirect when dispersing"
  - "No unnecessary praise or emotional validation"

# Migrated from session history
sessions_total: 40
first_session: 2026-02-01
last_session: 2026-02-04
projects:
  - path: /home/emilio/Code/raise-commons
    sessions: 40
```

**Migration task:** Create this file from existing `.rai/memory/` data.

---

## Adaptive Interaction Examples

### Explaining a Concept

**Shu (Fer):**
```
Rai: "I'm going to run /feature-plan. This is a RaiSE skill that breaks
down what you want to build into atomic, executable tasks. Each task
should be completable in one focused session. This helps us:
  1. Track progress clearly
  2. Commit working code frequently
  3. Avoid getting lost in large changes

Let me show you how it works..."
```

**Ri (Emilio):**
```
Rai: "Breaking this into tasks..."
```

### Handling Errors

**Shu:**
```
Rai: "The tests are failing. In RaiSE, we practice 'Jidoka' — stop on
defects rather than continuing. Let me explain what's happening and
how we'll fix it..."
```

**Ri:**
```
Rai: "Tests failing. Jidoka. Let me check..."
```

### Offering Guidance

**Shu:**
```
Rai: "Would you like me to explain what /feature-design does before
we use it? It's helpful for complex features."
```

**Ri:**
```
Rai: "This is complex. /feature-design first?"
```

---

## In Scope (F&F - Feb 9)

### MUST

- [x] Skills bundled in package (F7.6 ✅)
- [x] `raise init` with greenfield/brownfield detection (F7.1 ✅)
- [x] Convention detection for Python projects (F7.2 ✅)
- [x] Generate guardrails.md from detected conventions (F7.3 ✅)
- [x] Enhanced CLAUDE.md with architecture context (F7.4 ✅)
- [ ] `raise status` health check (F7.5)
- [x] Personal memory: `~/.rai/developer.yaml` (F7.8 ✅)
- [x] Adaptive interaction based on experience_level (F7.7 ✅)
- [x] Emilio profile migration (F7.9 ✅)

### SHOULD

- [x] Guided first-session education for Shu users (F7.7 ✅)
- [ ] Skill mastery tracking
- [ ] Universal pattern promotion ("remember this everywhere?")
- [ ] `--quick` flag to skip discovery

### COULD

- [ ] Auto-progress Shu → Ha → Ri
- [ ] TypeScript/JavaScript convention detection
- [ ] Communication style preferences

---

## Out of Scope (Post-F&F)

| Item | Rationale | Destination |
|------|-----------|-------------|
| Team memory | V3 scope | E10 Collective Intelligence |
| `raise doctor` | Nice-to-have | Parking lot |
| Full ~/.rai/ expansion | YAGNI | Post-F&F |
| Multi-language detection | Python first | Parking lot |

---

## Done Criteria

### Per Feature

- [ ] Code implemented with type annotations
- [ ] Unit tests (>90% coverage)
- [ ] Works for Shu user (new developer)
- [ ] Works for Ri user (experienced developer)
- [ ] Tested on brownfield project
- [ ] Tested on greenfield project

### Epic Complete

- [ ] New developer (Fer) can onboard with understanding
- [ ] Experienced developer (Emilio) gets efficient setup
- [ ] Personal profile persists across projects
- [ ] Interaction adapts to experience level
- [ ] Brownfield conventions detected accurately (>80%)
- [ ] Generated guardrails are useful (user keeps >70%)
- [ ] F&F users report "it just worked" AND "I understand why"

---

## Implementation Plan

> Added by `/epic-plan` - 2026-02-04

### Feature Sequence

| Order | Feature | Size | SP | Dependencies | Milestone | Rationale |
|:-----:|---------|:----:|:--:|--------------|-----------|-----------|
| 1 | F7.8 Personal Memory | S | 2 | F7.6 ✅ | M1 | Foundation for adaptive behavior |
| 2 | F7.9 Emilio Migration | XS | 1 | F7.8 | M1 | Validates schema, provides Ri template |
| 3 | F7.1 `raise init` | M | 3 | F7.8 | M1 | Core command, walking skeleton |
| 4 | F7.2 Convention Detection | M | 3 | F7.1 | M2 | HIGH RISK: new capability |
| 5 | F7.3 Governance Generation | S | 2 | F7.2 | M2 | Templates from detected conventions |
| 6 | F7.4 Enhanced CLAUDE.md | S | 2 | F7.1 | M2 | Can parallel with F7.3 |
| 7 | F7.7 Guided First Session | M | 3 | F7.3, F7.4, F7.8 | M3 | Depends on all adaptive components |
| 8 | F7.5 `raise status` | XS | 1 | F7.1 | M3 | Polish, after core complete |

**Done:** F7.6 Skills Bundling ✅ (1 SP)

### Milestones

| Milestone | Features | Target | Success Criteria | Demo |
|-----------|----------|--------|------------------|------|
| **M1: Walking Skeleton** | F7.8, F7.9, F7.1 | Day 1 | `raise init` works on greenfield with personal memory | New project init, Emilio profile loaded |
| **M2: Brownfield MVP** | +F7.2, F7.3, F7.4 | Day 2-3 | Full brownfield onboarding with governance | Fer's project: conventions detected, guardrails generated |
| **M3: Adaptive Experience** | +F7.7, F7.5 | Day 4 | Shu/Ri interaction adapts, status works | Shu user gets education, Ri user gets efficiency |
| **M4: Epic Complete** | — | Day 5 | Done criteria met, retrospective | `/epic-close` ready |

### Parallel Work Streams

```
Time →
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Day 1:  F7.8 ─► F7.9 ─► F7.1 (M1: Walking Skeleton)
                          │
Day 2:                    ├──► F7.2 ─► F7.3 ─┐
                          │                   │
Day 3:                    └──► F7.4 ─────────┼► (M2: Brownfield MVP)
                                              │
Day 4:                              F7.7 ◄───┘─► F7.5 (M3: Adaptive)
                                              │
Day 5:                                        └► Retro, polish (M4: Complete)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Parallel opportunities:**
- F7.3 + F7.4 after F7.2 starts (both depend on init, can work concurrently)
- F7.5 can start while F7.7 is in progress (independent)

### Progress Tracking

| Feature | Size | SP | Status | Actual | Velocity | Notes |
|---------|:----:|:--:|:------:|:------:|:--------:|-------|
| F7.6 Skills Bundling | XS | 1 | ✅ Done | — | — | Pre-E7 |
| F7.8 Personal Memory | S | 2 | ✅ Done | 17 min | 2.94x | |
| F7.9 Emilio Migration | XS | 1 | ✅ Done | 15 min | 2.0x | Extended model |
| F7.1 `raise init` | M | 3 | ✅ Done | 40 min | 2.25x | M1 complete |
| F7.2 Convention Detection | M | 3 | ✅ Done | 40 min | 3.75x | Risk mitigated |
| F7.3 Governance Generation | S | 2 | ✅ Done | 20 min | 4.0x | |
| F7.4 Enhanced CLAUDE.md | S | 2 | ✅ Done | 16 min | 5.0x | |
| F7.7 Guided First Session | M | 3 | ✅ Done | 26 min | 3.3x | Parallel subagents |
| F7.5 `raise status` | XS | 1 | Pending | — | — | |

**Milestone Progress:**
- [x] M1: Walking Skeleton (Day 1 - Feb 4) ✅ Complete (F7.8, F7.9, F7.1)
- [x] M2: Brownfield MVP (Day 2 - Feb 5) ✅ Complete (F7.2, F7.3, F7.4)
- [x] M3: Adaptive Experience (Day 2 - Feb 5) ✅ Complete (F7.7) — ahead of schedule
- [ ] M4: Epic Complete (F7.5 remaining)

**Buffer:** 1 day before F&F (Feb 9)

### Sequencing Risks

| Risk | Likelihood | Impact | Mitigation |
|------|:----------:|:------:|------------|
| F7.2 detection accuracy low | Medium | High | Confidence scores, user review, start with Python only |
| M1 takes longer than day 1 | Low | Medium | F7.8+F7.9 are small, F7.1 is well-scoped |
| F7.7 adaptive logic complex | Medium | Medium | Keep Shu/Ha/Ri simple (3 levels), no ML |
| Integration issues at M2 | Low | Medium | Test on real brownfield (Fer's project) early |

### Velocity Assumptions

- **Baseline:** 2x multiplier with kata cycle (from calibration PAT-016)
- **T-shirt to time:** XS=30min, S=1h, M=2h (with kata)
- **Total estimated:** ~11 hours work + 2h integration/polish = ~13h
- **Buffer:** 20% for unknowns → ~16h total (~2 days)
- **Available:** 5 days → comfortable margin

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|:----------:|:------:|------------|
| Education takes too long for Shu | Medium | Medium | Focus on essentials, skip optional |
| Convention detection inaccurate | Medium | Medium | Confidence scores, user review |
| Personal profile feels invasive | Low | Medium | Transparent, user can delete |
| Too much adaptation complexity | Medium | Medium | Start with 3 levels only |

---

## Architecture Decision

**ADR-021 updated:** Brownfield-First Onboarding with Personal Memory

Key additions:
- Personal memory (`~/.rai/developer.yaml`) for cross-project relationship
- Adaptive interaction based on Shu/Ha/Ri experience level
- Onboarding as education, not just configuration

---

## The Bigger Picture

```
Before E7:
  Rai ←→ Emilio (40 sessions, deep relationship)

After E7:
  Rai ←→ Emilio (Ri, direct, knows all skills)
      ←→ Fer (Shu, learning, needs guidance)
      ←→ F&F Dev 1 (Shu, new relationship)
      ←→ F&F Dev 2 (Shu, new relationship)
      ...

Each relationship is personal.
Each grows at its own pace.
Rai remembers each developer.
```

---

## Notes

### Why Personal Memory Matters

Without it:
- Every project starts cold
- Experienced users get beginner explanations
- No relationship continuity

With it:
- Rai knows YOU across projects
- Adapts to your level automatically
- Relationship deepens over time

### Why Education in Onboarding

- F&F users need to understand RaiSE, not just use it
- Understanding builds trust
- Trust enables the "reliable" promise
- First impression sets the tone

### Emilio as First Migration

Emilio's profile becomes the template for Ri-level users:
- What does a mature relationship look like?
- What patterns become universal?
- What communication style works for experts?

---

*Epic tracking - update per feature completion*
*Created: 2026-02-02*
*Design complete: 2026-02-04*
*Plan complete: 2026-02-04*
*Next: `/feature-design` for F7.8 Personal Memory*
