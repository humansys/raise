---
title: Governance
description: The rule system that keeps AI output reliable — from principles to requirements to enforceable guardrails.
---

Governance is how RaiSE ensures your AI partner doesn't drift. It's a layered system: high-level principles flow down into concrete requirements, which become enforceable guardrails. The AI loads these at session start and follows them throughout.

## The Three Layers

### Constitution (Principles)

The highest level — foundational principles that don't change often. These express *values* and *philosophy*.

Example principles:
- "Simple heuristics over complex ML"
- "Tests alongside implementation, not after"
- "Honesty over agreement"

Constitution lives in `governance/constitution.md` (or equivalent). Principles get IDs like `§1`, `§2`, etc.

### PRD (Requirements)

The middle layer — concrete requirements derived from principles. These express *what the project must do*.

Example requirements:
- `RF-01`: Marketing website with craftsman tone
- `RF-02`: Content strategy with hypothesis testing
- `RF-05`: Onboarding flow from discovery to productivity

Requirements live in `governance/prd.md` and link back to the principles they implement.

### Guardrails (Enforcement)

The bottom layer — specific, verifiable rules. These express *what you must and must not do*.

Guardrails have two levels:

| Level | Meaning | Example |
|-------|---------|---------|
| **MUST** | Non-negotiable. Violation is a defect. | "Every content piece has a documented hypothesis" |
| **SHOULD** | Recommended. Skip with justification. | "SEO-optimized headings and meta descriptions" |

Guardrails live in `governance/guardrails.md` and each links to the requirement it enforces.

## How Governance Flows

```
Principles (§)     →  "Why we do things this way"
     ↓
Requirements (RF)  →  "What we need to build"
     ↓
Guardrails (GR)    →  "What rules to follow"
     ↓
Code / Content     →  "What we actually produce"
```

Each layer is traceable to the one above. When someone asks "why do we have this guardrail?" you can trace it: guardrail → requirement → principle.

## Governance in Practice

When you run `rai session start --context`, the context bundle includes governance primes — the active guardrails relevant to your current work. Your AI partner sees these at the start of every session and applies them throughout.

For example, if you're working on content, the context bundle might include:

```
# Governance Primes
- must-content-001: Every content piece has a documented hypothesis
- must-content-002: One core idea per content piece
- must-brand-001: Consistent craftsman voice — no hype, no buzzwords
```

The AI doesn't need to remember these — they're loaded fresh every session from the governance files.

## Project Structure

After `rai init`, your governance directory looks like:

```
governance/
├── constitution.md    # Principles (or vision.md)
├── prd.md             # Requirements
├── guardrails.md      # Enforceable rules
├── backlog.md         # Work items
└── architecture/
    ├── system-context.md
    └── system-design.md
```

## Convention Detection

For existing projects, `rai init --detect` analyzes your codebase and generates guardrails automatically:

```bash
rai init --detect
```

This scans for patterns like:
- Coding conventions (naming, formatting, imports)
- Testing patterns (framework, directory structure)
- Architecture patterns (module organization, dependency direction)

The generated guardrails are a starting point — review and adjust them to match your team's actual standards.

## Key Idea

Governance isn't about control. It's about **consistency**. When your AI partner follows the same rules every session, you get predictable output. When the rules are explicit and traceable, you can evolve them deliberately instead of hoping for the best.
