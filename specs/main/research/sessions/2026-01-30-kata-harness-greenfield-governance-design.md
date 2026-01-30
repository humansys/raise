---
id: kata-harness-greenfield-governance-design
title: "Design Session: Kata Harness Greenfield Setup & Continuous Governance Model"
date: 2026-01-30
session_name: kata-harness-design
branch: kata-harness-greenfield-setup
participants: [Orchestrator, Claude Opus 4.5]
status: in-progress
artifacts_created:
  - specs/raise/adrs/adr-009-continuous-governance-model.md
  - specs/main/research/prompts/layered-grounding-hypothesis-research.md
---

# Design Session: Kata Harness Greenfield Setup & Continuous Governance Model

## Session Overview

**Date:** 2026-01-30
**Branch:** `kata-harness-greenfield-setup` (from `kata-harness`)
**Focus:** Designing the greenfield project setup process for RaiSE governance

---

## Problem Statement

The current RaiSE setup katas (`setup/analyze`, `setup/ecosystem`) are designed for **brownfield** scenarios (existing codebases). We need a process for **greenfield** projects that produces the same outputs:

1. Architectural documentation (for humans and agents)
2. Governance rules (guardrails)

**Key question:** Where should governance setup fit in the workflow? Before Solution Vision? Before Technical Design?

---

## Key Insights Developed

### 1. Governance vs. Rules Separation

Two distinct concerns were identified:

| Concept | Level | What It Defines | Scope |
|---------|-------|-----------------|-------|
| **Governance** | Policy | WHAT we enforce (guardrails) | Product-wide |
| **Rules** | Patterns | HOW we implement (conventions) | Codebase-specific |

**Governance = WHAT constraints apply (non-negotiable)**
**Rules = HOW to work within those constraints (implementation)**

### 2. Guardrails as Single Source of Truth (DRY)

**Insight:** A guardrail and its validation gate are two sides of the same coin.

```
GUARDRAIL (Single Definition)
├── Context section → Golden Context for generation
└── Verification section → Gate criteria for validation
```

**One definition, two uses.** This eliminates duplication between governance definitions and gate definitions.

### 3. Two Types of Validation

| Type | Purpose | Location |
|------|---------|----------|
| **Artifact Gates** | Structural completeness (template adherence) | Per kata: `gates/gate-{kata}.md` |
| **Governance Gates** | Rule compliance (guardrail adherence) | Derived from: `governance/guardrails/*.mdc` |

### 4. The Unified Setup Flow

Both brownfield and greenfield follow the same sequence:

```
setup/governance (product-wide guardrails)
    → setup/rules (codebase patterns, inherits governance)
        → setup/ecosystem (integration mapping)
```

Only the **mode** differs within each kata.

### 5. Architecture Model as Grounding

**Key insight from Orchestrator:** Guardrails should be **derived** from an Architecture Model, not defined directly.

```
ARCHITECTURE MODEL (abstract representation)
    ↓ grounds
AGENT REASONING (proposals, hypotheses)
    ↓ validates against
ACTUAL CODE (concrete reality)
```

The Architecture Model is the "map" that enables intelligent agent behavior.

### 6. The Layered Grounding Hypothesis

A fundamental design question emerged: Should agents be grounded in **Principles** or **Architecture**?

**Hypothesis:** Neither alone is sufficient. Effective grounding requires layers:

```
PRINCIPLES (Universal, Immutable)
    ↓ constrain + evaluate
ARCHITECTURE (System-Specific, Mutable)
    ↓ ground + contextualize
GUARDRAILS (Actionable, Derived)
    ↓ execute + validate
AGENT BEHAVIOR (Concrete Actions)
```

This hypothesis requires academic validation (research prompt created).

---

## Terminology Decisions

### Resolved Conflicts

| Problem | Resolution |
|---------|------------|
| "Solution Vision" (artifact) vs "Solution Level" (SAFe) | Keep "Solution Vision" for artifact; use "Governance" for product-wide rules (no "levels") |
| Multiple governance levels (Portfolio/Solution/Repo/PRD) | YAGNI - Only 2 layers: **Governance** (product) + **Codebase Rules** (repo) |
| `setup/analyze` naming | Rename to `setup/rules` for clarity |

### Canonical Terms

| Term | Definition |
|------|------------|
| **Governance** | Product-wide guardrails that define WHAT is enforced |
| **Guardrail** | Individual rule with level (MUST/SHOULD/MAY), context, and verification |
| **Codebase Rules** | Repo-specific patterns that implement governance |
| **Artifact Gate** | Validates structural completeness (template adherence) |
| **Governance Gate** | Validates rule compliance (derived from guardrails) |
| **Architecture Model** | Abstract representation of system structure that grounds agent reasoning |

---

## Design Decisions

### D1: Kata Structure for Setup

```
.raise/katas/setup/
├── governance.md    # NEW - Product-wide guardrails
├── rules.md         # RENAMED from analyze.md - Codebase patterns
└── ecosystem.md     # UNCHANGED - Integration mapping
```

### D2: Guardrail Schema (Single Source)

```yaml
# .raise/governance/guardrails/testing.mdc
---
id: MUST-TEST-001
level: MUST                    # MUST | SHOULD | MAY
scope: "**/*.ts"
---

# Test Coverage

## Rule
[What must be true]

## Context (for agents)
[Golden context for code generation]

## Verification (for gates)
```yaml
check: coverage
command: npm run test:coverage
threshold: 80
blocking: true
```
```

### D3: Severity = Gate Behavior

| Level | During Generation | During Validation |
|-------|-------------------|-------------------|
| **MUST** | "You must do this" | Blocking gate |
| **SHOULD** | "You should do this" | Warning gate |
| **MAY** | "You may do this" | No gate |

### D4: Progressive Greenfield Process

The greenfield governance kata must support:
- Multi-session (user can pause, discuss with team, resume)
- Incremental progress (partial governance is valid state)
- Agent proposals based on RaiSE constitution + Lean principles
- Human refinement before finalization

---

## Artifacts Created

### 1. ADR-009: Continuous Governance Model

**Location:** `specs/raise/adrs/adr-009-continuous-governance-model.md`
**Status:** Proposed

Documents:
- Guardrails as single source of truth
- Two-layer governance model (Governance + Codebase Rules)
- Artifact Gates vs Governance Gates distinction
- Kata updates for setup workflow

### 2. Research Prompt: Layered Grounding Hypothesis

**Location:** `specs/main/research/prompts/layered-grounding-hypothesis-research.md`
**Status:** Ready for execution

Explores:
- RQ1: Cognitive science - How do experts reason?
- RQ2: AI/LLM agents - What grounding works?
- RQ3: Organizational theory - Espoused vs in-use values
- RQ4: Lean/TPS - Principles and practices
- RQ5: Philosophy - Symbol grounding problem
- RQ6: Software engineering - Principles → Patterns → Practices

---

## Open Questions

### For Research

1. Does the layered grounding hypothesis hold under academic scrutiny?
2. How do expert architects actually reason - principles or patterns?
3. What evidence exists for/against architecture-first vs principles-first?

### For Design

1. What is the minimal schema for the Architecture Model?
2. How should the Architecture Model evolve as the system changes?
3. How do we keep the model in sync with reality (brownfield)?
4. Should SAR analysis produce the same model structure as greenfield Q&A?

### For Implementation

1. What questions should the greenfield governance kata ask?
2. How to persist partial progress across sessions?
3. How should agent propose defaults based on constitution?

---

## Next Steps

1. **Commit current artifacts** to `kata-harness-greenfield-setup` branch
2. **Execute research prompt** to validate layered grounding hypothesis
3. **Draft `setup/governance` kata** based on decisions made
4. **Draft `setup/rules` kata** (renamed from analyze, enhanced for greenfield)
5. **Define Architecture Model schema** (minimal viable structure)

---

## Key Quotes from Session

> "In both brownfield and greenfield, we need the governance first, and codebase rules later. I don't see those 2 processes separated."

> "Those 'questions' that we need to answer to obtain governance rules at each level can be 'answered' through SAR analysis (brownfield) or generate new proposals (greenfield)."

> "The Architecture Model is a set of documents that represent the architecture 'as is' in an abstract manner... to 'ground' itself for initial proposals or 'solution' hypothesis that the agent can later validate in the actual code."

> "I can hear some ex-colleagues telling that NO, architecture should not ground everything, but PRINCIPLES!"

---

## Session Metadata

**Duration:** ~2 hours
**Model:** Claude Opus 4.5
**Tools Used:** Read, Write, Edit, Bash, Glob, Task (Explore)
**Commits:** Pending

---

*Session preserved: 2026-01-30*
