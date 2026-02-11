---
type: architecture_context
project: raise-cli
version: 2.0.0-alpha
status: current
tech_stack:
  language: "Python 3.12+"
  framework: "Pydantic AI"
  validation: "Pydantic v2"
  cli: "Typer"
  distribution: "uv + pipx"
  ast_analysis: "Python AST (stdlib) + ast-grep (shell)"
  search: "ripgrep (shell)"
  testing: "pytest"
  graph: "NetworkX"
  code_analysis: "Python AST (context/analyzers subpackage)"
external_dependencies:
  - "Git (version control, governance-as-code transport)"
  - "Python AST (code structure extraction)"
  - "ripgrep (fast content search)"
  - "ast-grep (AST pattern matching)"
users:
  - "RaiSE Engineers (human developers)"
  - "Rai (AI partner, reads architecture docs for grounding)"
governed_by:
  - "framework/reference/constitution.md"
  - "governance/guardrails.md"
  - "governance/vision.md"
---

# System Context

> C4 Level 1 — What is raise-cli, who uses it, how does it fit in the world?

## What Is raise-cli

raise-cli is the **deterministic toolkit** of the RaiSE framework. It provides CLI commands that extract, structure, query, and validate project knowledge — governance documents, codebase structure, developer memory, and architectural decisions.

It is **not** a code generator, not an AI agent, and not an IDE plugin. It is the tooling layer that makes AI-assisted software engineering **reliable and observable**.

## The RaiSE Triad

raise-cli exists within a three-part collaboration model:

```
        RaiSE Engineer
        (Human — Strategy, Judgment, Ownership)
              │
              │ collaborates with
              ▼
           Rai
   (AI Partner — Execution, Memory, Patterns)
   Reads skills, calls raise-cli, synthesizes
              │
              │ governed by
              ▼
        RaiSE Toolkit
   raise-cli + Skills + Governance artifacts
   Deterministic, Observable, Git-native
```

**The human** defines what to build and makes judgment calls. **Rai** (AI partner) executes skills, calls CLI tools, and maintains continuity across sessions. **raise-cli** provides the deterministic operations that Rai calls — no AI inference happens inside the CLI itself.

## Who Uses It

| Actor | How They Use raise-cli | Example |
|-------|----------------------|---------|
| **RaiSE Engineer** | Directly via terminal or indirectly through Rai | `rai init`, `rai memory query` |
| **Rai (AI Partner)** | Called from skills during collaborative sessions | Rai reads `/session-start` skill, calls `rai session start` |
| **CI/CD pipelines** | Drift detection, governance validation (future) | `rai discover drift` in pre-merge hook |

## External Systems

```
┌──────────────────────────────────────────────────────────────┐
│                     raise-cli boundary                        │
│                                                               │
│  Governance ←→ Concept Graph ←→ Memory ←→ Discovery          │
│                                                               │
└──────────┬───────────────┬───────────────┬───────────────────┘
           │               │               │
           ▼               ▼               ▼
    ┌────────────┐  ┌────────────┐  ┌─────────────┐
    │    Git     │  │  Python    │  │  ripgrep /  │
    │ (transport │  │  AST       │  │  ast-grep   │
    │  + truth)  │  │ (parsing)  │  │ (search)    │
    └────────────┘  └────────────┘  └─────────────┘
```

- **Git** — All governance artifacts, memory files, and architecture docs live in Git. Git is the transport and the source of truth. Platform-agnostic (GitHub, GitLab, Bitbucket — any Git host).
- **Python AST** — Used by the discovery module to extract symbols (classes, functions, constants) from Python source files. No external dependency — stdlib `ast` module.
- **ripgrep / ast-grep** — Called as shell subprocesses for fast content search and AST pattern matching. Optional — graceful degradation if not installed.
- **AI inference provider** — raise-cli does NOT call any AI API. Rai (the AI partner) runs on Claude Code, Cursor, or any capable LLM. The CLI is inference-free by design.

## What raise-cli Does

| Domain | Commands | What It Provides |
|--------|----------|-----------------|
| **Governance** | `rai context` | Extracts concepts from Markdown governance docs into a queryable graph |
| **Memory** | `rai memory build/query` | Builds unified knowledge graph with code-aware nodes, answers questions from it |
| **Discovery** | `rai discover scan/analyze/drift` | Scans codebase for components, detects architectural drift |
| **Onboarding** | `rai init`, `rai profile` | Bootstraps projects, manages developer profiles |
| **Telemetry** | `rai telemetry emit` | Records local JSONL signals for process improvement |
| **Session** | `rai session start` | Tracks session lifecycle for continuity |
| **Skills** | `rai skill list/show` | Locates and displays process guide skills |

## What raise-cli Does NOT Do

- **Generate code** — That is Rai's job (the AI partner)
- **Run AI inference** — All CLI operations are deterministic
- **Manage CI/CD** — Integrates via Git, does not replace pipelines
- **Replace project management** — No Jira/Linear features; integration only (future)
- **Enforce at runtime** — Governance is advisory; the human is the quality gate

## Design Philosophy

> "Bring value, get out of the way."

From the constitution (§1-§8):

1. **Humans Define, Machines Execute** — Specs are truth; code is expression
2. **Governance as Code** — Standards in Git; what's not in repo doesn't exist
3. **Platform Agnosticism** — Works where Git works
4. **Validation Gates** — Quality at each phase, not just at the end
5. **Lean / Jidoka** — Stop on defects; eliminate waste
6. **Observable Workflow** — Every decision traceable and auditable

## Quality Attributes

| Attribute | Target | Rationale |
|-----------|--------|-----------|
| CLI response time | < 5 seconds | Developer flow state preservation |
| Token efficiency | > 90% reduction via MVC | Inference economy — gather with tools, think with inference |
| Test coverage | > 90% | Guardrail MUST-TEST-001 |
| Zero secrets in code | Always | Guardrail MUST-SEC-001 |

## Governance Traceability

This document derives from:
- **Constitution** → `framework/reference/constitution.md` (§1-§8)
- **Solution Vision** → `governance/vision.md` (identity, triad, scope)
- **Guardrails** → `governance/guardrails.md` (quality standards)
- **ADR-012** → Skills + Toolkit pattern (no monolithic engines)
