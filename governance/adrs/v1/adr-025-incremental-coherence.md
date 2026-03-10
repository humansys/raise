---
id: "ADR-025"
title: "Incremental Coherence — Graph Diffing and AI-Driven Doc Regeneration"
date: "2026-02-08"
status: "Proposed"
related_to: ["ADR-019", "ADR-023"]
supersedes: []
research: ""
epic: "E16"
---

# ADR-025: Incremental Coherence — Graph Diffing and AI-Driven Doc Regeneration

## Context

### The Problem

Architecture documentation drifts from code silently. The current system has no incremental update path — only full discovery (overwrite) or manual vigilance.

Evidence from SES-118:
- `rai discover drift` produces 383 warnings on raise-commons, near-zero actionable
- Full discovery overwrites human-validated baselines — no merge capability
- `rai memory build` overwrites `unified.json` with no change report
- Story-close Step 1.5 checks for structural drift but cannot fix it
- PAT-196: stale architecture docs cause new sessions to use wrong paths

### The Tension

Two valid approaches exist:

1. **Template-based regeneration** — Deterministic rewrite of factual sections (frontmatter fields) from code analysis. Predictable, fast, but limited to structured data.

2. **AI-driven regeneration** — Subagent interprets graph diff, regenerates affected docs intelligently. Flexible, handles narrative updates, but non-deterministic and requires HITL review.

### What We Know About the Docs

Module docs (`governance/architecture/modules/*.md`) have clear separation:

| Section | Owner | Auto-generable? |
|---------|-------|-----------------|
| `name`, `depends_on`, `depended_by` | Machine | Yes — from imports |
| `entry_points`, `public_api` | Machine | Yes — from CLI/`__all__` |
| `components` count | Machine | Yes — from discovery |
| `purpose` | Hybrid | Partial — draft from docstring, human refines |
| `constraints` | Human | No — domain-specific rules |
| Body content | Human | No — rationale, conventions, diagrams |

High-level docs (`system-design.md`, `domain-model.md`) contain both factual structure (layer assignments, module groupings) and intentional design (bounded context boundaries, architectural decisions).

## Decision

**Implement a two-layer coherence system:**

1. **CLI layer (deterministic):** Graph diffing produces a structured change set. Factual frontmatter fields in module docs are updated deterministically from code analysis. This is fast, predictable, and needs no review.

2. **Skill layer (inference):** When the graph diff indicates structural changes beyond frontmatter (new modules, moved responsibilities, changed high-level architecture), a subagent regenerates affected narrative sections. This requires HITL review before commit.

**Integration point:** Story-close, after existing Step 1.5 (structural drift check), as Step 1.75.

**Validation:** Full discovery workflow serves as reconciliation audit — rerun periodically to verify incremental updates haven't drifted.

## Consequences

### Positive

- Drift prevented at source (small batches, not big-bang rediscovery)
- Human validation effort preserved (incremental updates, not full overwrite)
- Graph diff enables change-aware tooling beyond just docs
- Clear machine/human ownership boundary in docs
- Fits existing lifecycle (story-close integration)

### Negative

- Graph diffing adds complexity to the context module
- AI-generated doc sections require review discipline
- Two-layer system means two failure modes to handle
- Graph diff format becomes a contract — changes need migration

### Neutral

- Full discovery remains useful as validation, not primary update path
- Module doc format gains implicit contract (frontmatter = machine, body = human)
- Story-close gets slightly longer but catches drift earlier

## Alternatives Considered

1. **Full discovery on every story-close** — Too expensive, overwrites human validation, no incremental benefit.

2. **Template-only (no AI)** — Handles frontmatter well but can't update narrative sections, high-level docs, or cross-module implications. Insufficient for real architectural changes.

3. **Manual discipline only** — Current state. Doesn't scale, produces PAT-196 repeatedly.

4. **Post-hoc audit only** (`rai doctor`) — Detects but doesn't prevent. Drift accumulates between audits.
