---
type: architecture_index
project: raise-cli
generated: "2026-02-08"
modules: 13
components: 309
---

# raise-cli Architecture

> Compact index for AI context loading. Full module docs: `governance/architecture/modules/`

## System Overview

raise-cli is a Python CLI toolkit for the RaiSE framework. It provides deterministic governance operations, codebase discovery, and memory management for AI-assisted software engineering. The architecture follows a **layered hub-and-spoke** pattern: leaf modules (core, config, schemas) at the base, domain modules (governance, discovery, memory) in the middle, integration (context) pulling everything together, and the CLI as the sole orchestrator.

## Module Map

| Module | Purpose | Depends On | Components |
|--------|---------|-----------|------------|
| `cli` | Typer CLI commands and entry points | config, context, discovery, governance, memory, onboarding, output, rai_base, skills, telemetry | 42 |
| `config` | Settings cascade and XDG directory resolution | — | 18 |
| `context` | Unified knowledge graph — merges all domains | config, core, governance, memory | 18 |
| `core` | Subprocess wrappers for git, ripgrep, ast-grep | — | 18 |
| `discovery` | Code scanning, analysis, and drift detection | — | 26 |
| `governance` | Markdown governance extraction to concept graph | core | 29 |
| `memory` | Pattern/calibration/session JSONL management | config, context | 30 |
| `onboarding` | Project init, profile, convention detection | config, core, rai_base, skills_base | 60 |
| `output` | Format-aware output (human, JSON, table) | discovery, skills | 19 |
| `rai_base` | Base identity and patterns for distribution | — | 0 |
| `schemas` | Shared Pydantic models (minimal) | — | 0 |
| `skills` | Skill parsing, location, validation, scaffolding | — | 25 |
| `skills_base` | 18 distributable SKILL.md files | — | 0 |
| `telemetry` | Local JSONL signal emission | config | 13 |

## Data Flow

```
Governance markdown → extractor → concept nodes ─────┐
Source code         → scanner   → analyzer → comps   ├→ UnifiedGraph → raise memory query
JSONL memory        → loader    → pattern/cal nodes  │
Architecture docs   → frontmatter parser → mod nodes ┘
```

## Architectural Constraints

- `core`, `config`, `schemas` have no internal dependencies (leaf modules)
- `cli` depends on everything but nothing depends on `cli`
- `governance` and `discovery` are independent of each other
- All CLI output goes through `output` formatters
- No circular imports — strictly acyclic dependency graph
- Maximum dependency depth: 4 levels (cli → context → governance → core)
