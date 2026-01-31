---
id: solution-foundation-session
title: "Session: RaiSE Solution Foundation (Business Case, Vision, Guardrails)"
date: 2026-01-30
session_name: solution-foundation
branch: solution-foundation
participants: [Emilio Osorio (Orchestrator), Claude Opus 4.5]
katas_executed:
  - solution/discovery
  - solution/vision
  - setup/governance
status: completed
artifacts_created:
  - governance/solution/business_case.md
  - governance/solution/vision.md
  - governance/solution/guardrails.md
merged_to: v2
---

# Session: RaiSE Solution Foundation

## Executive Summary

In this session, we completed the entire solution-level governance foundation for RaiSE by executing three katas sequentially. The session produced 1,030+ lines of governance documentation across three artifacts, establishing the "why," "what," and "how" for RaiSE as a product.

**Duration:** ~3 hours
**Model:** Claude Opus 4.5
**Approach:** Guided facilitation with structured questions

---

## Session Context

### Why This Session

Before proceeding with project-level work (kata-harness), we needed to establish the solution-level foundation per RaiSE methodology (ADR-010). This ensures all future projects are constrained by approved governance.

### Branch Strategy

Initially planned as branch-per-kata, consolidated to single branch:

```
v2 ←── solution-foundation
           │
           │ Contains all 3 katas:
           │ ├── solution/discovery (Business Case)
           │ ├── solution/vision (Solution Vision)
           │ └── setup/governance (Guardrails)
           │
           ▼ merged
          v2 (2dcda70)
```

---

## Katas Executed

### 1. solution/discovery → Business Case

**Output:** `governance/solution/business_case.md`
**Status:** ✅ APPROVED (2026-01-30)

#### Key Decisions

| Decision | Choice |
|----------|--------|
| Primary Stakeholder | Emilio Osorio (Founder/CEO, humansys.ai) |
| Target Market | Professional software devs in any industry |
| Primary Segment | Financial services, Telecom (regulated) |
| Value Proposition | "From Concept to Value — a single engineer, with RaiSE and you" |
| Top Differentiators | 1. Deterministic governance, 2. Compliance-ready, 3. Brownfield-native |
| Competitive Stance | New category: "Reliable AI Software Engineering" |
| Business Model | Open Core (MIT license) |
| Adoption Model | Bottom-up (individuals → teams → orgs) |
| Y1 Target | 100-500 active projects |
| Team | Small team forming (internal hires) |
| Funding | Seeking external funding (ASAP) |
| Recommendation | **GO** |

#### Research Evidence Used

- Veracode 2025: 45% AI code security failure rate
- GitClear 2025: 5.7% code churn post-merge
- Google DORA 2024: 7.2% stability decrease with AI
- METR Study 2025: +20% perceived / -19% actual productivity

---

### 2. solution/vision → Solution Vision

**Output:** `governance/solution/vision.md`
**Status:** ✅ APPROVED (2026-01-30)

#### Key Decisions

| Decision | Choice |
|----------|--------|
| System Type | Framework + Multi-Interface Tooling |
| Description | "RaiSE helps professional developers ship reliable software at AI speed — with governance that works naturally" |
| Mission | "Raise your craft, feature by feature." |
| Philosophy | "Bring value, get out of the way." |
| v2 Interface | CLI only (MCP, SaaS future) |
| Project Modes | Both greenfield and brownfield |

#### Technical Stack

| Layer | Technology | Rationale |
|-------|------------|-----------|
| Language | Python 3.12+ | Pydantic AI alignment, AI ecosystem |
| Core Framework | Pydantic AI | Agentic orchestration vision |
| Validation | Pydantic v2 | Type-safe governance schemas |
| CLI | Typer | Modern, type-safe DX |
| Distribution | uv + pipx | Fast Python distribution |
| AST Analysis | ast-grep | Rust performance for SAR |
| Search | ripgrep | Rust performance |
| Testing | pytest | Standard |

#### Architecture

- **Pattern:** Modular monolith → Plugin-ready when needed
- **Principle:** Engines are stable, interfaces come and go, content grows organically
- **Package:** `raise-cli` (PyPI) → `raise` (CLI command)

#### Core Capabilities (7 MUST)

1. Kata execution engine
2. Governance gates
3. Skills library
4. Observable metrics
5. Golden context management
6. Brownfield analysis (SAR)
7. Template scaffolding

---

### 3. setup/governance → Guardrails

**Output:** `governance/solution/guardrails.md`
**Status:** ✅ APPROVED (2026-01-30)

#### Guardrail Summary

| Category | MUST | SHOULD |
|----------|------|--------|
| Code Quality | 3 | 1 |
| Testing | 2 | 1 |
| Security | 2 | 1 |
| Architecture | 2 | 1 |
| Development | 2 | 1 |
| **Total** | **11** | **5** |

#### Key Guardrails

| ID | Level | Rule |
|----|-------|------|
| MUST-CODE-001 | MUST | Type hints on all code |
| MUST-CODE-002 | MUST | Ruff linting passes |
| MUST-CODE-003 | MUST | No type errors (pyright strict) |
| MUST-TEST-001 | MUST | >90% test coverage |
| MUST-SEC-001 | MUST | No secrets in code |
| MUST-SEC-002 | MUST | Bandit security scan passes |
| MUST-ARCH-001 | MUST | Engine/content separation |
| MUST-ARCH-002 | MUST | Pydantic models for all schemas |
| MUST-DEV-001 | MUST | Pre-commit hooks configured |

#### Toolchain

```
pre-commit
├── ruff (linting + formatting)
├── pyright (type checking)
├── bandit (security)
└── detect-secrets (secret scanning)
```

---

## Dogfooding Findings

Issues discovered by using RaiSE to build RaiSE:

| Finding | Description | Action |
|---------|-------------|--------|
| Missing gate | `gate-solution-discovery.md` doesn't exist | Create solution-level discovery gate |
| Missing gate | `gate-solution-vision.md` doesn't exist | Create solution-level vision gate |
| Gate derivation | Applied gates from kata step verifications | Formalize as gate files |

---

## Git History

```
solution-foundation branch:
├── 55e3a8b feat(solution): Complete solution/discovery kata - Business Case
├── 48cb286 docs(solution): Approve Business Case
├── aa0f9cc feat(solution): Complete solution/vision kata - Solution Vision
└── fe63faf feat(governance): Complete setup/governance kata - Guardrails

Merged to v2:
└── 2dcda70 Merge branch 'solution-foundation' into v2
```

---

## Artifacts Summary

| Artifact | Lines | Sections |
|----------|-------|----------|
| `governance/solution/business_case.md` | 238 | 10 sections |
| `governance/solution/vision.md` | 310 | 9 sections |
| `governance/solution/guardrails.md` | 369 | 16 guardrails detailed |
| **Total** | **917** | — |

---

## Key Quotes from Session

> "The actual name was part of a research in names that I casually did a while ago. RaiSE kind of stayed because as an engineer, I raise my capacities feature by feature."

> "Bring value, get out of the way. RaiSE should feel natural. Organic."

> "Even a monkey can vibe-code an MVP with current models. The real challenge is evolution."

> "We are obviously building a lean kiss dry yagni mvp, but I think that it should be informed by future scenarios."

> "Pydantic all the way!"

---

## Session Methodology

### Approach: Guided Facilitation

1. **One question at a time** — After initial question dump, switched to single questions with options
2. **Options-based decisions** — Presented 3-4 options per decision point
3. **Clarification welcomed** — User could clarify/expand before answering
4. **Research integration** — Used existing research for evidence-based Business Case
5. **Gate validation** — Applied derived gates to validate artifacts before approval

### Tools Used

- Read (kata files, research)
- Write (artifacts)
- Edit (approvals)
- Bash (git operations)
- AskUserQuestion (guided decisions)
- TaskCreate/TaskUpdate (progress tracking)
- Task with Explore agent (research extraction)

---

## Next Steps

With solution foundation complete, the project is ready for:

1. **Project-level work** — kata-harness can now proceed with governance constraints
2. **CLI development** — `raise-cli` package can be scaffolded following guardrails
3. **Community sharing** — Artifacts ready for investor/community review

---

## Session Metadata

**Started:** 2026-01-30
**Completed:** 2026-01-30
**Branch:** `solution-foundation`
**Merged to:** `v2`
**Commit count:** 5 (including merge)
**Lines added:** 1,030+

---

*Session log created: 2026-01-30*
