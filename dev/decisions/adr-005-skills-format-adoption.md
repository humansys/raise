# ADR-005: Skills Format Adoption for RaiSE Katas

**Date:** 2026-01-31
**Status:** Accepted
**Deciders:** Emilio Osorio, Rai

---

## Context

RaiSE uses "katas" — markdown files with YAML frontmatter that define methodology (how to design, plan, implement features). These katas need to be:

1. **Consumable by AI agents** (Claude Code, Copilot, Codex)
2. **Portable** across platforms and tools
3. **Maintainable** without duplication

The Agent Skills specification (agentskills.io) has emerged as the industry standard for defining reusable AI agent capabilities, adopted by 25+ platforms and governed by the Linux Foundation's Agentic AI Foundation.

**Key question:** Should RaiSE maintain its own kata format, create a wrapper layer, or migrate to Skills format?

---

## Decision

**Migrate katas to Agent Skills format** with RaiSE-specific metadata extensions in the `metadata.raise.*` namespace.

**Architectural clarification:** RaiSE is a governance layer FOR Claude Code, not a competing agentic runtime.

```
┌─────────────────────────────────────────────────┐
│              Claude Code (Executor)              │
│                                                  │
│   ┌──────────────────────────────────────────┐  │
│   │           RaiSE Skills                    │  │
│   │  Methodology + Gates + Guardrails         │  │
│   └──────────────────────────────────────────┘  │
│                      │                          │
│                      ▼                          │
│              Claude's Inference                 │
└─────────────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────┐
│           raise-cli (Developer Tooling)         │
│                                                 │
│   Scaffolding, validation, telemetry aggregation│
│   (NO inference — not a competing runtime)      │
└─────────────────────────────────────────────────┘
```

**Directory change:** `.raise/katas/` → `.claude/skills/`

---

## Alternatives Considered

### Alternative 1: Keep Custom Kata Format

**Rejected because:**
- Requires translation layer for Claude Code
- Not portable to other AI agents (Copilot, Codex)
- Proprietary format in era of standardization
- Violates platform agnosticism principle

### Alternative 2: Skills as Interface Layer (Dual Format)

**Rejected because:**
- Violates Single Source of Truth principle
- Requires synchronization between `.raise/katas/` and `.claude/skills/`
- Maintenance burden of two formats
- Wrapper adds unnecessary indirection when formats are compatible

### Alternative 3: Build Agentic Executor in raise-cli

**Rejected because:**
- Competes with Claude Code (Anthropic's own product)
- Requires maintaining inference infrastructure
- Duplicates functionality that Claude Code does better
- Against "augment, don't compete" strategy

---

## Consequences

### Positive

- **Native format:** Claude Code understands Skills natively (zero translation)
- **Industry standard:** Works with 25+ platforms (Copilot, Codex, etc.)
- **Single source of truth:** One format, one location
- **Ecosystem access:** 71,000+ skills in marketplace
- **Future-proof:** Linux Foundation governance, broad adoption
- **Platform agnostic:** Aligns with RaiSE principles

### Negative

- **Migration effort:** One-time cost to convert existing katas
- **Metadata constraints:** Skills metadata is string→string (less semantic richness)
- **Dependency on spec:** Skills spec evolution affects RaiSE

### Mitigations

- **Migration effort:** Incremental conversion, start with pilot
- **Metadata constraints:** Use `metadata.raise.*` namespace, serialize complex structures
- **Spec dependency:** Use stable fields only, monitor spec evolution

---

## RaiSE Skill Format Convention

```yaml
---
# === Required by Agent Skills Spec ===
name: story-design
description: >
  Create lean story specifications optimized for human understanding
  and AI alignment. Use when designing features before implementation.

# === Optional Agent Skills Fields ===
license: MIT

# === RaiSE Governance Extensions ===
metadata:
  raise.work_cycle: feature
  raise.frequency: per-story-as-needed
  raise.fase: "4"
  raise.prerequisites: project-backlog
  raise.next: story-plan
  raise.gate: gate-design
  raise.adaptable: "true"
  raise.version: "1.0.0"
---

# Feature Design

## Purpose
...

## Mastery Levels (ShuHaRi)

**Shu (守)**: Follow template completely.
**Ha (破)**: Adapt to complexity.
**Ri (離)**: Create new patterns.

## Steps
...

## Gate: gate-design
...
```

---

## Directory Structure

```
.claude/
└── skills/
    ├── feature/
    │   ├── design/
    │   │   └── SKILL.md
    │   ├── plan/
    │   └── implement/
    ├── project/
    │   ├── vision/
    │   └── backlog/
    └── tools/
        └── research/

.raise/
├── telemetry/          # Telemetry storage (not a skill)
└── config.toml         # RaiSE configuration
```

---

## Implications for raise-cli

raise-cli is **developer tooling**, not an agentic executor:

| Command | Purpose | Inference |
|---------|---------|-----------|
| `rai init` | Scaffold RaiSE structure | No |
| `rai skill new` | Create skill from template | No |
| `rai gate check` | Validate gate criteria | No |
| `rai telemetry` | Aggregate/report metrics | No |

**Pydantic AI** stays in stack for schema validation, not inference.

**Telemetry** originates from Claude Code hooks and skill scripts, aggregated by raise-cli.

---

## References

- Research: `work/research/skills-architecture-decision/`
- Agent Skills Spec: https://agentskills.io/specification
- Agentic AI Foundation: https://intuitionlabs.ai/articles/agentic-ai-foundation-open-standards
- Constitution §8: Observable Workflow

---

*ADR-005 - Skills format adoption*
