# Recommendation: Skills Architecture Decision

> Research ID: skills-architecture-20260131
> Date: 2026-01-31
> Updated: 2026-01-31 (post-architecture clarification)

---

## Decision

**Migrate katas to Skills format (Option 3)** — RaiSE provides governance FOR Claude Code, not a competing executor.

**Confidence**: HIGH

---

## Strategic Context (Clarified)

### What RaiSE Is

RaiSE is a **governance layer** that teaches Claude Code HOW to work on projects:
- Methodology (katas → skills)
- Validation criteria (gates)
- Observable workflow (telemetry)
- Guardrails (CLAUDE.md)

### What RaiSE Is NOT

RaiSE is **not** a competing agentic runtime:
- Does not replace Claude Code
- Does not run its own inference
- Does not compete with Claude Code, Codex, Copilot

### The Natural Relationship

```
┌─────────────────────────────────────────────────────────────┐
│                      Claude Code (Rai)                       │
│                                                              │
│   ┌──────────────────────────────────────────────────────┐  │
│   │                   RaiSE Skills                        │  │
│   │                                                       │  │
│   │  - Methodology: How to design, plan, implement        │  │
│   │  - Gates: When is each phase "done"                   │  │
│   │  - Guardrails: Quality standards to follow            │  │
│   │  - ShuHaRi: Mastery progression guidance              │  │
│   │                                                       │  │
│   │  "Governance content that shapes Claude's work"       │  │
│   └──────────────────────────────────────────────────────┘  │
│                           │                                  │
│                           ▼                                  │
│                    Claude's Inference                        │
│                    (Anthropic API)                           │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ hooks / artifacts
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                       raise-cli                              │
│                                                              │
│   Developer tooling (NOT an executor):                       │
│                                                              │
│   - Scaffolding: raise init, rai skill new                │
│   - Validation: raise gate check (deterministic)            │
│   - Telemetry: Aggregation and reporting                    │
│   - Utilities: raise context, raise deps                    │
│                                                              │
│   "Helps humans manage RaiSE, stays out of Claude's way"    │
└─────────────────────────────────────────────────────────────┘
```

---

## Rationale

### 1. Skills is Claude Code's Native Format

Claude Code already understands Skills:
- Progressive disclosure (metadata → instructions → resources)
- Script execution without context cost
- Automatic invocation based on description matching

**Using Skills means zero translation layer.** Claude reads RaiSE governance natively.

### 2. RaiSE Augments, Doesn't Compete

Building an agentic executor would:
- Duplicate Claude Code functionality
- Require maintaining inference infrastructure
- Compete with Anthropic's own product

Instead, RaiSE provides the **content** (methodology) that makes Claude Code more effective on governed projects.

### 3. Single Source of Truth

With Skills format:
- One format for process definitions
- Works with Claude Code, Copilot, Codex (25+ platforms)
- No sync between internal (katas) and external (skills) formats

### 4. raise-cli Stays Focused

raise-cli becomes developer tooling, not an AI application:

| Command | Purpose | Inference Required |
|---------|---------|-------------------|
| `rai init` | Scaffold RaiSE structure | No |
| `rai skill new` | Create skill from template | No |
| `rai gate check` | Validate gate criteria | No |
| `rai validate` | Check governance artifacts | No |
| `rai telemetry` | Aggregate/report metrics | No |
| `rai context` | Preview what Claude sees | No |

**Pydantic stays in stack** for schema validation and structured parsing, not for inference.

### 5. Telemetry Architecture

Telemetry flows FROM Claude Code, aggregated BY raise-cli:

```
Claude Code                    raise-cli
     │                              │
     │  (executes skill)            │
     │                              │
     ├──► hooks emit events ───────►│
     │                              │
     ├──► skill scripts log ───────►│
     │                              │  .raise/telemetry/
     │                              │  ├── events.jsonl
     │                              │  ├── traces.jsonl
     │                              │  └── metrics.jsonl
     │                              │
     │                              ├──► raise telemetry summary
     │                              └──► raise telemetry export (OTel)
```

Observable Workflow is preserved — the telemetry just originates from Claude Code rather than raise-cli.

---

## Trade-offs Accepted

| Accepting | In Exchange For |
|-----------|-----------------|
| raise-cli is not an agentic executor | No competition with Claude Code |
| Telemetry depends on Claude Code hooks | Native integration, no duplicate execution |
| Skills format (not custom kata format) | Industry standard, ecosystem access |
| Less control over execution | Claude Code is better at execution anyway |

---

## Risks

### Risk 1: Claude Code Hooks May Be Limited

**Likelihood**: Medium
**Impact**: Medium (telemetry gaps)
**Mitigation**:
- Skill scripts can emit telemetry directly
- raise-cli helpers for manual checkpoints
- Monitor Claude Code hook capabilities as they evolve

### Risk 2: Skills Spec Evolution

**Likelihood**: Low (Linux Foundation governance)
**Impact**: Low
**Mitigation**:
- Use stable, documented fields
- RaiSE metadata in `metadata.raise.*` namespace
- Participate in community if needed

### Risk 3: Loss of "Engine" Differentiation

**Likelihood**: Low
**Impact**: Medium
**Mitigation**:
- RaiSE value is METHODOLOGY (content), not runtime
- Gates, ShuHaRi, Observable Workflow are the differentiators
- These transfer to Skills format unchanged

---

## Implementation Plan

### Phase 1: Foundation

1. **Create ADR** documenting this architectural decision
2. **Define namespace convention**: `metadata.raise.*` for RaiSE-specific fields
3. **Create skill template** for converting katas

### Phase 2: Pilot Migration

4. **Convert pilot skill**: `tools/research` (well-tested, we just used it)
5. **Test with Claude Code**: Verify I can invoke and follow it
6. **Validate telemetry**: Ensure events can be captured

### Phase 3: Full Migration

7. **Convert remaining katas** incrementally
8. **Update raise-cli** to read from `.claude/skills/`
9. **Deprecate `.raise/katas/`** path (keep gates separate or migrate)
10. **Update documentation**: CLAUDE.md, guardrails, README

### Phase 4: Telemetry Integration

11. **Implement Claude Code hooks** for event emission (if available)
12. **Add skill script helpers** for telemetry logging
13. **Build raise-cli telemetry commands** for aggregation/reporting

---

## Skill Format Specification (RaiSE Convention)

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
  # Workflow
  raise.work_cycle: feature
  raise.frequency: per-story-as-needed
  raise.fase: "4"

  # Chaining
  raise.prerequisites: project-backlog
  raise.next: story-plan

  # Validation
  raise.gate: gate-design

  # Adaptability
  raise.adaptable: "true"
  raise.version: "1.0.0"
---

# Design: Feature Specification

## Purpose

Create a lean story specification that optimizes for both human
understanding and AI alignment.

## Mastery Levels (ShuHaRi)

**Shu (守)**: Follow template completely; include all required sections.

**Ha (破)**: Skip optional sections for simple features; adjust detail
to complexity.

**Ri (離)**: Create custom spec patterns for specialized domains.

## Context

**When to use:**
- Before planning complex features (>3 components, >5 SP)
- When feature requires architectural decisions

**When to skip:**
- Simple features (<3 components, obvious implementation)
- Bug fixes, minor refactoring

## Steps

### Step 1: Load Context
...

### Step 2: Draft Specification
...

## Gate: gate-design

Before proceeding to planning, validate:
- [ ] Problem statement is clear
- [ ] Success criteria are measurable
- [ ] Technical approach is sound

## Output

- **Artifact**: `work/stories/{feature}/design.md`
- **Next**: `/story-plan`
```

---

## Directory Structure (After Migration)

```
.claude/
└── skills/
    ├── feature/
    │   ├── design/
    │   │   ├── SKILL.md
    │   │   └── references/
    │   │       └── tech-design-template.md
    │   ├── plan/
    │   │   └── SKILL.md
    │   ├── implement/
    │   │   └── SKILL.md
    │   └── review/
    │       └── SKILL.md
    ├── project/
    │   ├── vision/
    │   ├── backlog/
    │   └── ...
    ├── tools/
    │   ├── research/
    │   │   ├── SKILL.md
    │   │   └── references/
    │   │       └── research-prompt-template.md
    │   └── ...
    └── gates/
        ├── gate-code/
        │   └── SKILL.md      # Gate as a validation skill
        └── ...

.raise/
├── telemetry/                 # Telemetry storage
│   ├── events.jsonl
│   └── traces.jsonl
└── config.toml                # RaiSE configuration
```

---

## What Stays in .raise/

| Artifact | Location | Rationale |
|----------|----------|-----------|
| Telemetry data | `.raise/telemetry/` | Local storage, not a skill |
| Configuration | `.raise/config.toml` | Engine config, not methodology |
| Templates | `.claude/skills/*/references/` | Bundled with skills |

---

## Quality Checklist

- [x] Research question is specific and falsifiable
- [x] 18 sources consulted (standard depth target: 15-30)
- [x] Evidence catalog created with levels
- [x] Major claims triangulated (5 claims, 3+ sources each)
- [x] Confidence level explicitly stated (HIGH)
- [x] Contrary evidence acknowledged
- [x] Recommendation is specific and actionable
- [x] Architecture clarified (RaiSE augments Claude Code)
- [x] Governance linkage: ADR to be created

---

## Research Metadata

- **Tool/model used**: WebSearch (built-in fallback)
- **Search date**: 2026-01-31
- **Prompt version**: 1.0
- **Researcher**: Rai (Claude Opus 4.5)
- **Total sources**: 18
- **Architecture clarification**: Conversation with Emilio (2026-01-31)

---

## Next Steps

1. **Emilio approves** this recommendation
2. **Create ADR**: `dev/decisions/ADR-00X-skills-format-adoption.md`
3. **Pilot migration**: Convert `tools/research` kata to skill
4. **Validate**: Test skill invocation in Claude Code
5. **Iterate**: Refine format based on pilot learnings
6. **Full migration**: Convert remaining katas

---

*Recommendation complete. Awaiting human approval.*
