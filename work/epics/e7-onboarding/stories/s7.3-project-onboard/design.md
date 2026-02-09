---
story_id: S7.3
title: "/project-onboard skill"
size: M
epic: E7
phase: design
---

# S7.3 Design: `/project-onboard` Skill

## What & Why

**Problem:** Brownfield projects have existing code, conventions, and architecture. `/project-create` asks "what do you want to build?" — but brownfield needs "what do you already have?" first, then fills governance from that understanding.

**Value:** Developers onboarding existing projects get governance docs pre-filled from actual codebase analysis, not just conversation. Discovery data flows into architecture docs. Convention detection flows into guardrails. The graph reflects reality from day one.

## Architectural Context

**Module:** New skill file in `.claude/skills/project-onboard/SKILL.md`
**Domain:** Onboarding (same as `/project-create`)
**Reuses:** Same governance doc format and parser contracts from S7.2. Same `raise memory build` gate.

**Key difference from `/project-create`:**

| Aspect | `/project-create` | `/project-onboard` |
|--------|-------------------|---------------------|
| Input | Conversation only | Discovery + conversation |
| Architecture docs | User describes | Discovered from code |
| Guardrails | User specifies | Detected conventions + user refinement |
| Prerequisite | `raise init` | `raise init --detect` |
| Discovery commands | None | `raise discover scan`, `raise discover analyze` |

## Approach

The skill orchestrates a **3-phase pipeline**: discover → converse → generate.

### Phase 1: Discover (deterministic CLI)
1. Verify `raise init --detect` was run (manifest exists, conventions detected)
2. Run `raise discover scan . -o json | raise discover analyze -o json` to get codebase structure
3. Present discovery summary to user — modules, components, architecture patterns

### Phase 2: Converse (inference)
4. Ask user to confirm/refine discovered architecture
5. Collect missing info: project vision, goals, requirements (same as project-create Steps 2-3)
6. Merge user intent with discovered reality

### Phase 3: Generate (write + validate)
7. Write 6 governance docs using combined discovery + conversation data
8. `raise memory build` — 30+ node gate (same as project-create)
9. Summary and next steps

**IMPORTANT:** The governance doc format is identical to `/project-create` — same parser contracts, same YAML frontmatter, same regex patterns. The difference is WHERE the content comes from (discovery vs pure conversation).

## Examples

### Invocation

```
User: /project-onboard
```

### Prerequisites Check

```bash
# Verify manifest exists (raise init was run)
ls .raise/manifest.yaml

# Verify conventions were detected (--detect flag was used)
# guardrails.md should already exist from raise init --detect
ls governance/guardrails.md
```

If `governance/guardrails.md` doesn't exist or has only placeholders:
```
"Run `raise init --detect` first — I need convention detection data to analyze your project."
```

### Discovery Output (presented to user)

```
## Codebase Analysis

**Project:** my-api (brownfield, 142 Python files)

**Detected Modules:**
| Module | Files | Classes | Functions |
|--------|-------|---------|-----------|
| api    | 23    | 8       | 45        |
| models | 15    | 12      | 3         |
| core   | 18    | 5       | 32        |

**Detected Conventions:**
- Type hints: 78% coverage (SHOULD guardrail)
- Testing: pytest, 65% coverage
- Linting: ruff configured

**Architecture signals:**
- FastAPI app with SQLAlchemy models
- Background tasks via Celery
- REST API with JWT auth

Does this look right? Anything to add or correct?
```

### Conversation (fills gaps)

After discovery, ask for what code can't tell us:

```
"I can see WHAT you built. Now tell me WHY:
1. One-paragraph description — what is my-api for, who uses it?
2. 3-5 core capabilities (I'll cross-reference with what I found in the code)"
```

### Generated Architecture Doc (enriched by discovery)

`governance/architecture/system-design.md`:
```markdown
# System Design: my-api

> C4 Level 2 — Container/component decomposition

## Architecture Overview

FastAPI-based REST API with SQLAlchemy ORM, Celery task queue, and JWT authentication.

## Components

| Component | Responsibility | Technology |
|-----------|---------------|------------|
| API Layer | HTTP endpoints, request validation | FastAPI, Pydantic |
| Models | Database schema, ORM mappings | SQLAlchemy |
| Core | Business logic, domain services | Python |
| Tasks | Background job processing | Celery, Redis |
| Auth | JWT token management, permissions | python-jose |
```

## Acceptance Criteria

### MUST
1. Skill file exists at `.claude/skills/project-onboard/SKILL.md` with valid YAML frontmatter
2. Skill runs discovery pipeline (`raise discover scan` + `raise discover analyze`) and presents results
3. Governance docs follow identical parser contracts as `/project-create` (same regex patterns)
4. `raise memory build` produces 30+ nodes after onboarding
5. Architecture docs are enriched with discovery data (components from actual code, not just conversation)

### SHOULD
1. Detected conventions from `raise init --detect` flow into guardrails refinement
2. Skill detects if prerequisites are missing and gives clear instructions
3. Discovery results presented concisely — summary, not raw dump

### MUST NOT
1. Modify any CLI commands (discovery, init, memory build)
2. Duplicate parser contracts — reference S7.2 patterns, same format
3. Run discovery commands without user awareness (show what's happening)

## Notes

- **PAT-201** applies: separate skills for greenfield vs brownfield produce better DX
- **PAT-202/203** apply: governance templates are the contract, same as S7.2
- Reuse S7.2 skill structure as template — same YAML frontmatter pattern, same step numbering convention
- Convention detection from `raise init --detect` already generates `guardrails.md` and `CLAUDE.md` — the skill enriches these, doesn't replace them
