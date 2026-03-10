---
title: Knowledge Graph
description: The unified context graph that connects memory, governance, skills, and work into a single queryable structure.
---

The Knowledge Graph is the backbone of RaiSE's context system. It merges everything — memory patterns, governance documents, skills metadata, work tracking, and discovered components — into a single graph of connected concepts.

## What It Is

A directed graph where:
- **Nodes** are concepts — patterns, principles, requirements, skills, stories, components, modules
- **Edges** are relationships — "learned from", "governed by", "depends on", "constrained by"

When you run `rai graph build`, the CLI traverses all project sources and assembles this graph. When you query with `rai graph query` or `rai graph context`, you're searching this graph.

## Node Types

| Type | ID Pattern | Source | Example |
|------|-----------|--------|---------|
| Pattern | `PAT-*`, `BASE-*` | Memory JSONL files | "Use fixtures for database tests" |
| Calibration | `CAL-*` | Calibration records | Story S3.5: M size, 45 min actual |
| Session | `SES-*` | Session history | "Implemented auth module" |
| Principle | `§N` | Constitution | "Simple heuristics over complex ML" |
| Requirement | `RF-*` | PRD | "Marketing website with craftsman tone" |
| Guardrail | `GR-*` | Guardrails | "MUST: No vanity metrics as goals" |
| Skill | `/name` | SKILL.md files | `/rai-story-plan` — decompose into tasks |
| Story | `S*.*` | Work tracking | S8.6: Docs Getting Started |
| Epic | `E*` | Epic scopes | E8: Website v1 + Docs |
| Component | `comp-*` | Discovery scan | `SessionManager` class |
| Module | `mod-*` | Discovery analysis | `mod-memory` — memory subsystem |
| Decision | `ADR-*` | Architecture decisions | ADR-019: Unified context graph |

## Edge Types

Edges express how concepts relate:

| Edge | Meaning | Example |
|------|---------|---------|
| `learned_from` | Pattern came from this session | PAT-042 → SES-015 |
| `governed_by` | Requirement implements a principle | RF-01 → §2 |
| `implements` | Story implements a requirement | S8.6 → RF-05 |
| `part_of` | Story belongs to an epic | S8.6 → E8 |
| `depends_on` | Module depends on another | mod-session → mod-memory |
| `belongs_to` | Module belongs to a domain | mod-memory → bc-core |
| `constrained_by` | Domain is constrained by a guardrail | bc-core → GR-015 |
| `applies_to` | Pattern applies to a skill | PAT-001 → /rai-story-implement |

## Building the Graph

```bash
rai graph build
```

This merges all sources:
1. **Governance**: principles, requirements, guardrails from `governance/`
2. **Memory**: patterns, calibration, sessions from `.raise/rai/memory/`
3. **Work**: epic and story scopes from `work/epics/`
4. **Skills**: metadata from `.claude/skills/*/SKILL.md`
5. **Components**: discovered code from `work/discovery/`

The output is `.raise/rai/memory/index.json`.

## Querying the Graph

### Keyword Search

Find concepts by content:

```bash
rai graph query "testing patterns"
```

### Concept Lookup

Find a specific concept by ID:

```bash
rai graph query "PAT-001" --strategy concept_lookup
```

### Module Context

Get the full architectural context for a module — its domain, layer, constraints, and dependencies:

```bash
rai graph context mod-memory
```

This returns:
- **Bounded context**: which domain the module belongs to
- **Layer**: its position in the architecture (leaf, domain, integration, orchestration)
- **Constraints**: applicable guardrails (MUST and SHOULD)
- **Dependencies**: what it depends on and what depends on it

### Validation

Check the graph for structural issues:

```bash
rai graph validate
```

This detects cycles in dependency relationships, invalid edge types, and dangling references.

## Why a Graph

The graph structure enables **contextual queries** — not just "find this keyword" but "show me everything related to this module, including the rules that constrain it and the patterns learned while building it."

When your AI partner runs `rai session start --context`, the CLI assembles a context bundle by traversing this graph. The result is a compressed view of everything relevant to your current work — not a dump of all files, but a curated selection of the most important nodes and their relationships.
