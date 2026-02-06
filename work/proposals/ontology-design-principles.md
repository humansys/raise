# Ontology Engineering for Developer Tools: The RaiSE Approach

> How we apply ontology engineering principles to design coherent CLI commands and AI skills.

**Author:** Emilio Osorio & Rai
**Date:** February 2026
**Context:** F14.13 CLI/Skill Ontology Cleanup retrospective

---

## Introduction

When building developer tools that combine human-facing CLIs with AI-facing skills, inconsistent naming and organization creates friction. Users must memorize arbitrary structures. AI assistants hallucinate commands that don't exist. Maintenance becomes a game of whack-a-mole.

Ontology engineering—the discipline of formally representing knowledge domains—offers principles that bring order to this chaos. This post describes how we applied seven ontological principles during the RaiSE framework CLI redesign.

---

## The Seven Principles

### 1. Conceptual Clarity

**Principle:** Concepts should be clearly defined with non-overlapping semantics.

**Anti-pattern we found:**
```
Session concept scattered across:
├── profile session-start    ← Start session
├── memory add-session       ← Record session
└── telemetry emit-session   ← Emit session signal
```

Three commands touching "session" with subtly different meanings. Users asked: "Which one do I use?" The answer was "all of them, in sequence"—a sign of poor conceptual boundaries.

**Fix:** We unified session into a first-class command group:
```
session
├── start    ← Starts AND records
└── close    ← Closes AND emits
```

The skill orchestrates the internals; the user sees one concept, one location.

---

### 2. Taxonomic Consistency

**Principle:** Hierarchies should reflect natural categorization.

**Anti-pattern we found:**
```
profile
├── show           ← About developer identity (correct)
├── session-start  ← About workflow (why here?)
└── session-end    ← About workflow (why here?)
```

Sessions are workflows, not profile attributes. Placing them under `profile` is like filing "drive to work" under "driver's license."

**Fix:** Sessions became their own category, `profile` retained only identity-related commands:
```
profile
└── show           ← Developer identity only

session            ← NEW: Workflow as first-class citizen
├── start
└── close
```

**Heuristic:** If you're reaching for a concept and can't predict where it lives, the taxonomy is wrong.

---

### 3. Naming Conventions

**Principle:** Names should follow consistent patterns.

**Anti-pattern we found:**

| Pattern | Examples | Location |
|---------|----------|----------|
| `noun-verb` | `session-start`, `session-close` | Skills |
| `verb-noun` | `add-pattern`, `emit-session` | CLI |
| `verb` only | `scan`, `build`, `drift` | CLI (discover) |

Three patterns = three mental models.

**Fix:** We documented the intentional split:
- **CLI:** `verb-noun` for actions, bare `verb` for domain-scoped operations
- **Skills:** `noun-verb` (domain-action) consistently

And critically: **CLI and Skill names for the same concept must match**. We renamed `session-end` → `session-close` to align with the skill.

**Heuristic:** Say the command aloud. Does it describe what it does? "session close" vs "session end"—close implies completing properly, end implies abrupt stop.

---

### 4. Orthogonality

**Principle:** Independent concepts should be independent in structure.

**Anti-pattern we found:**

Session state was scattered across four systems:
- **Profile** owned the session counter
- **Memory** stored session records
- **Telemetry** emitted session events
- **Skills** orchestrated all three

Changing session behavior required touching four modules. Tests were fragile—mocking one missed the others.

**Fix:** We consolidated runtime state into `session` module, kept `memory` for persistence, removed `telemetry` as a separate concern (events emit as side effects of memory writes).

**Heuristic:** If changing concept X requires changes in modules A, B, and C, either X is poorly bounded or A/B/C should be one module.

---

### 5. Minimal Ontological Commitment

**Principle:** Assert only what's necessary. Don't create structures you don't need.

**Anti-pattern we found:**
```
status              ← EMPTY: Zero subcommands
└── (nothing)

telemetry           ← REDUNDANT: Duplicates memory add-*
├── emit-session
├── emit-calibration
└── emit-work
```

The `status` command existed because "we might need it." Telemetry existed as a separate top-level because "events are different from records" (an implementation detail, not a user concern).

**Fix:**
- Removed `status` entirely
- Merged telemetry into `memory emit-*` commands

**Heuristic:** YAGNI applies to ontologies. Empty categories are technical debt. Separate systems for the same concept are architectural waste.

---

### 6. Completeness

**Principle:** The ontology should cover the domain adequately.

**What we audited:**

| Domain | CLI Coverage | Skill Coverage | Gap? |
|--------|--------------|----------------|------|
| Project setup | `init` | - | No |
| Codebase discovery | `discover` (3 cmds) | 4 skills | Partial |
| Memory/context | `memory` (8 cmds) | - | No |
| Session workflow | Scattered | 2 skills | Yes → Fixed |
| Epic workflow | - | 4 skills | By design |
| Feature workflow | - | 6 skills | By design |

**Design decision:** Epic and Feature workflows are skill-only—they're AI-executed processes, not user-facing commands. This is intentional incompleteness, documented as such.

**Heuristic:** Gaps are acceptable if intentional. Accidental gaps accumulate into user confusion.

---

### 7. Domain-Centric Organization

**Principle:** Organize around business domains, not technical layers.

**Anti-pattern we found:**
```
# Technical organization (how we found it)
memory/       ← Persistence layer
telemetry/    ← Event layer
profile/      ← User data layer
```

**Domain organization (what we built):**
```
# Domain organization (what users care about)
session/      ← Workflow lifecycle
memory/       ← All persistent knowledge
profile/      ← Developer identity
discover/     ← Codebase analysis
```

Users think in domains ("I want to query my patterns") not layers ("I need to access the persistence subsystem").

---

## The Audit Process

How do you find ontological violations? We developed a checklist:

### 1. Overlap Detection
```
For each concept (session, calibration, pattern...):
  Count how many top-level commands touch it
  If > 1: Evaluate if split is justified
```

### 2. Naming Consistency Check
```
Extract all command names
Group by pattern (verb-noun, noun-verb, bare-verb)
If multiple patterns: Document the rationale or unify
```

### 3. Empty Category Scan
```
For each command group:
  If zero subcommands: Remove or justify
```

### 4. Skill-CLI Alignment
```
For each skill:
  Does a corresponding CLI command exist?
  Do the names match?
  If skill uses "close", CLI shouldn't use "end"
```

### 5. Taxonomy Gut Check
```
For each concept, ask:
  "If I didn't know where this lived, could I guess?"
  If no: The taxonomy needs work
```

---

## Results

After applying these principles to F14.13:

| Metric | Before | After |
|--------|--------|-------|
| Top-level commands | 6 | 5 |
| Total subcommands | 22 | 17 |
| Empty categories | 1 | 0 |
| Naming inconsistencies | 3 | 0 |
| Session touchpoints | 4 systems | 2 systems |

More importantly: new team members can now predict where commands live without memorizing the structure.

---

## Principles for Your Projects

1. **Audit before building.** Ontological debt compounds. Fix it before you ship.

2. **Name things for users, not implementers.** "emit-session" is an implementation detail. "session close" is what users do.

3. **One concept, one location.** If users can't predict where something lives, your taxonomy failed.

4. **Empty categories are lies.** They promise functionality that doesn't exist. Remove them.

5. **Document intentional gaps.** If Epic has no CLI commands by design, say so. Undocumented gaps become bug reports.

6. **Match AI and human interfaces.** If skills use `session-close`, the CLI should too. Mismatches cause hallucinations.

7. **Prefer domain organization.** Users think in problems (sessions, features, discoveries), not in layers (persistence, events, state).

---

## Conclusion

Ontology engineering isn't academic philosophy—it's practical hygiene for developer tools. The principles are simple: clear concepts, consistent naming, minimal structure, domain alignment.

The payoff is a system where humans can predict behavior and AI can generate correct commands. That's worth the audit.

---

*This post emerged from the F14.13 CLI/Skill Ontology Cleanup feature in the RaiSE framework. The full analysis is at `work/epics/e14-rai-distribution/features/f14.13-ontology-cleanup/ontology-analysis.md`.*
