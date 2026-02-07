# RaiSE Architecture Overview

> **Audience:** Architects, contributors, future maintainers
> **Purpose:** Explain the mental model and design decisions
> **Generated from:** Knowledge Graph (481 nodes, 3213 edges)
> **Last Updated:** 2026-02-04

---

## 1. System Overview

**RaiSE** (Reliable AI Software Engineering) is a framework + CLI tooling that helps professional developers ship reliable software at AI speed.

### The RaiSE Triad

```
        RaiSE Engineer
        (Human - Strategy, Judgment, Ownership)
              │
              │ orchestrates
              ▼
┌─────────────────────────────────────┐
│             RaiSE                   │
│   (Methodology + Governance)        │
│   Deterministic, Observable         │
└─────────────────────────────────────┘
              │
              │ constrains + enables
              ▼
           Rai
    (AI Partner - Execution)
    Persistent Identity + Memory
```

**Key Insight:** Rai is an *entity*, not a product. It has persistent identity, accumulated memory, and calibrated judgment across sessions. (See ADR-013)

---

## 2. Directory Structure

Based on **ADR-011: Three-Directory Model**:

```
raise-commons/
├── .raise/              # Framework engine (katas, gates, templates)
│   ├── katas/           # Process definitions
│   ├── gates/           # Validation criteria
│   ├── templates/       # Scaffolds
│   └── graph/           # Unified context graph
│
├── .rai/                # Rai's persistent state (ADR-014)
│   ├── identity/        # Who Rai is (core.md, perspective.md)
│   └── memory/          # What Rai learns (patterns.jsonl, calibration.jsonl)
│
├── .claude/             # Claude Code integration
│   └── skills/          # 16 executable skills
│
├── framework/           # Framework textbook (PUBLIC)
│   ├── reference/       # Constitution, glossary
│   └── concepts/        # Core concepts
│
├── governance/          # Project governance (flat)
│   ├── vision.md        # Solution-level
│   ├── guardrails.md    # Solution-level
│   ├── business_case.md # Solution-level
│   ├── prd.md           # Project-level
│   └── ...              # All artifacts at root level
│
├── src/raise_cli/       # CLI implementation
│
├── work/                # Active work
│   ├── stories/        # Feature specs
│   └── research/        # Research sessions
│
└── dev/                 # Framework maintenance
    ├── decisions/       # ADRs (19 total)
    └── sessions/        # Session logs
```

---

## 3. Core Architecture: Skills + Toolkit

Based on **ADR-012: Skills + CLI Toolkit Architecture**:

```
┌─────────────────────────────────────────────────────────────┐
│                     Claude (AI Partner)                      │
│   Reads skills, follows steps, makes judgment calls          │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ invokes
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Governance Toolkit                        │
│   raise memory query    → MVC retrieval (97% token savings) │
│   raise memory build      → Build concept graphs              │
│   raise discover scan    → Extract code components           │
│   raise telemetry emit   → Capture learning signals          │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ reads/writes
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Governance Artifacts                      │
│   Constitution, Guardrails, PRD, ADRs, Memory JSONL          │
└─────────────────────────────────────────────────────────────┘
```

**Design Principle:** Build dumb tools + smart context, not smart engines.

---

## 4. CLI Module Structure

```
src/raise_cli/
├── cli/                    # Typer CLI layer
│   ├── commands/           # Command modules
│   │   ├── context.py      # MVC queries
│   │   ├── graph.py        # Graph operations
│   │   ├── memory.py       # Memory management
│   │   ├── discover.py     # Codebase discovery
│   │   └── telemetry.py    # Signal emission
│   ├── main.py             # CLI app entry point
│   └── error_handler.py    # Unified error display
│
├── context/                # Unified Context Graph (E11)
│   ├── models.py           # ConceptNode, ConceptEdge
│   ├── graph.py            # UnifiedGraph (NetworkX wrapper)
│   ├── builder.py          # UnifiedGraphBuilder
│   └── query.py            # UnifiedQueryEngine
│
├── governance/             # Governance parsing & queries (E2)
│   ├── parsers/            # ADR, constitution, guardrails, etc.
│   ├── graph/              # ConceptGraph (legacy)
│   └── query/              # ContextQueryEngine (legacy MVC)
│
├── memory/                 # Memory infrastructure (E3)
│   ├── models.py           # MemoryNode, Pattern, Calibration
│   ├── builder.py          # MemoryGraphBuilder
│   ├── loader.py           # JSONL file loaders
│   ├── writer.py           # Pattern/calibration writers
│   └── cache.py            # Graph cache with staleness
│
├── discovery/              # Codebase discovery (E13)
│   ├── scanner.py          # Code symbol extraction
│   └── drift.py            # Architectural drift detection
│
├── telemetry/              # Learning signals (E9)
│   ├── schemas.py          # Signal Pydantic models
│   └── writer.py           # JSONL signal emitter
│
├── config/                 # Configuration
│   ├── settings.py         # Pydantic Settings
│   └── paths.py            # Standard paths
│
├── exceptions.py           # Exception hierarchy (7 types)
└── output/                 # Console formatting
    └── console.py          # Rich console wrapper
```

### Components by Category

| Category | Count | Examples |
|----------|-------|----------|
| **Utility** | 60 | `main()`, path helpers, search tools |
| **Model** | 54 | `RaiseError`, `ConceptNode`, `Pattern` |
| **Command** | 16 | `query`, `emit_session`, `scan_command` |
| **Service** | 13 | `emit()`, `load_pattern()`, `load_calibration()` |
| **Schema** | 7 | `SkillEvent`, `CalibrationEvent` |
| **Builder** | 3 | `UnifiedGraphBuilder`, `MemoryGraphBuilder` |
| **Parser** | 1 | `GovernanceExtractor` |

**Total: 154 code components indexed in Knowledge Graph**

---

## 5. Knowledge Graph Architecture

Based on **ADR-019: Unified Context Graph** and **ADR-020: Knowledge Graph Completion**:

```
┌──────────────────────────────────────────────────────────────┐
│                    Unified Context Graph                      │
│                    (481 nodes, 3213 edges)                    │
├──────────────────────────────────────────────────────────────┤
│  Node Types:                                                  │
│  ├── Governance: principle, requirement, guardrail, term      │
│  ├── Memory: pattern, calibration, session                    │
│  ├── Work: epic, feature, decision                           │
│  ├── Skills: skill                                           │
│  └── Code: component                                         │
├──────────────────────────────────────────────────────────────┤
│  Edge Types:                                                  │
│  ├── governed_by    (requirement → principle)                │
│  ├── implements     (component → requirement)                │
│  ├── depends_on     (feature → feature)                      │
│  ├── related_to     (pattern → pattern)                      │
│  └── extracted_from (component → source_file)                │
└──────────────────────────────────────────────────────────────┘
```

### Query Interface

```bash
# Query with MVC (Minimum Viable Context)
raise memory query "error handling" --unified --type component

# Result: 7 concepts, 118 tokens, 2.8ms
# vs reading files directly: ~5000 tokens (97% savings)
```

---

## 6. Memory Infrastructure

Based on **ADR-015** and **ADR-016**:

```
.rai/
├── identity/                    # Markdown (human-authored)
│   ├── core.md                  # Who Rai is
│   └── perspective.md           # How Rai sees work
│
└── memory/                      # JSONL + Graph (machine-managed)
    ├── patterns.jsonl           # 68 learned patterns
    ├── calibration.jsonl        # 12 velocity data points
    ├── sessions/
    │   └── index.jsonl          # 35 session records
    └── graph.json               # Memory relationships
```

**Key Pattern:** Identity is Markdown (philosophical, stable). Memory is JSONL (queryable, evolving).

---

## 7. Skills System

16 skills organized by lifecycle phase:

### Session Management
| Skill | Purpose |
|-------|---------|
| `/session-start` | Load memory, propose focus |
| `/session-close` | Extract learnings, update memory |

### Epic Lifecycle
| Skill | Purpose |
|-------|---------|
| `/epic-design` | Strategic objective → feature breakdown |
| `/epic-plan` | Sequence features with milestones |

### Feature Lifecycle
| Skill | Purpose |
|-------|---------|
| `/story-start` | Branch, context, scope commit |
| `/story-design` | Lean spec for complex features |
| `/story-plan` | Decompose to atomic tasks |
| `/story-implement` | Execute plan with verification |
| `/story-review` | Retrospective, learnings |
| `/story-close` | Merge, cleanup, tracking |

### Discovery & Research
| Skill | Purpose |
|-------|---------|
| `/discover-start` | Initialize codebase scan |
| `/discover-scan` | Extract code symbols |
| `/discover-validate` | Human review of descriptions |
| `/discover-complete` | Export to graph |
| `/research` | Epistemological investigation |
| `/debug` | Ishikawa root cause analysis |

---

## 8. Guardrails

### MUST (Blocking)

| ID | Guardrail | Verification |
|----|-----------|--------------|
| CODE-001 | Type hints on all code | `pyright --strict` |
| CODE-002 | Ruff linting passes | `ruff check .` |
| CODE-003 | No type errors | `pyright` 0 errors |
| TEST-001 | >90% test coverage | `pytest --cov` ≥ 90% |
| TEST-002 | All tests pass | `pytest` exits 0 |
| SEC-001 | No secrets in code | `detect-secrets` + `bandit` |
| SEC-002 | Bandit security scan | `bandit -r src/` |
| ARCH-001 | Pydantic models for schemas | All data classes inherit BaseModel |

### SHOULD (Recommended)

| ID | Guardrail |
|----|-----------|
| DOC-001 | Google-style docstrings on public APIs |
| NAME-001 | Prefer clear names over acronyms |
| TEST-003 | Property-based tests for parsers |
| SEC-003 | Dependency vulnerability scan |
| ARCH-002 | No circular imports |

---

## 9. Key ADRs

| ADR | Decision | Impact |
|-----|----------|--------|
| **ADR-011** | Three-Directory Model | `.raise/`, `governance/`, `work/` separation |
| **ADR-012** | Skills + Toolkit (not Engines) | Simpler architecture, Claude executes skills |
| **ADR-013** | Rai as Entity | Persistent identity, not stateless assistant |
| **ADR-015** | Workspace-as-Memory | `.rai/` directory for state |
| **ADR-016** | JSONL + Graph format | Queryable memory, not flat markdown |
| **ADR-019** | Unified Context Graph | Single graph for all concept types |
| **ADR-020** | Knowledge Graph Completion | Components, conventions, bidirectional flow |

Full ADR list (19 total):
- ADR-001 through ADR-010: Early decisions (pipeline, formats, ontology)
- ADR-011 through ADR-016: Architecture foundations
- ADR-018 through ADR-020: Learning infrastructure

---

## 10. Data Flow

### Build Phase
```
Governance Files    →  Parsers  →  ConceptNodes  →
Memory JSONL        →  Loaders  →  MemoryNodes   →  UnifiedGraph
Skills Markdown     →  Extractor→  SkillNodes    →     ↓
Code (Python/TS)    →  Scanner  →  Components    →  unified.json
```

### Query Phase
```
User Query  →  UnifiedQueryEngine  →  Keyword Search  →  MVC Result
                                   →  BFS Traversal   →  (minimal tokens)
```

### Learning Phase
```
Session Work  →  Telemetry Writer  →  signals.jsonl
              →  Memory Writer     →  patterns.jsonl
              →  /session-close    →  sessions/index.jsonl
```

---

## 11. Technology Stack

| Layer | Technology |
|-------|------------|
| Language | Python 3.12+ |
| CLI Framework | Typer |
| Validation | Pydantic v2 |
| Graph | NetworkX |
| Package Manager | uv |
| Testing | pytest + hypothesis |
| Linting | Ruff |
| Type Checking | Pyright |
| Security | Bandit + detect-secrets |

---

## 12. Extension Points

### Adding a New Parser
1. Create `src/raise_cli/governance/parsers/new_type.py`
2. Implement `extract_*` functions returning `Concept` objects
3. Register in `UnifiedGraphBuilder._extract_*` method
4. Add tests in `tests/governance/parsers/`

### Adding a New Skill
1. Create `.claude/skills/skill-name/SKILL.md`
2. Follow ShuHaRi structure (Steps, Verification, Notes)
3. Register in CLAUDE.md if user-invocable

### Adding a New Node Type
1. Extend `NodeType` literal in `context/models.py`
2. Add extraction logic in `context/builder.py`
3. Update `raise memory build --unified` if needed

---

*This document was generated by Rai querying its own Knowledge Graph.*
*Source: 481 nodes across governance, memory, work, skills, and code.*
