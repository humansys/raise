---
story_id: "S7.2"
title: "/project-create skill"
epic_ref: "E7 Onboarding"
story_points: 8
complexity: "moderate"
status: "draft"
version: "1.0"
created: "2026-02-08"
updated: "2026-02-08"
template: "lean-feature-spec-v2"
---

# Feature: `/project-create` skill — greenfield onboarding

> **Epic**: E7 - Onboarding
> **Complexity**: moderate | **SP**: 8

---

## Architectural Context

- **Module:** mod-onboarding (bc-experience domain, integration layer)
- **Pattern:** Skills orchestrate conversation; CLI provides deterministic structure (ADR-012, ADR-024)
- **Key constraint:** Governance doc **structure** is deterministic (templates from S7.1). Governance doc **content** is inference (this skill fills templates from conversation).
- **Dependencies:** S7.1 (governance scaffolding — done), mod-skills_base, mod-rai_base

---

## 1. What & Why

**Problem**: After `rai init`, governance docs exist but contain only placeholder comments. The project has structure but no meaning — the graph has no useful nodes, `/session-start` has no context, and RaiSE provides no value until someone fills those docs.

**Value**: A guided conversation turns an empty project into a RaiSE-ready one. The developer describes their project once; Rai fills all governance docs with parser-compatible content. The graph comes alive with 30+ nodes, and `/session-start` becomes useful immediately.

---

## 2. Approach

**How we'll solve it**: A SKILL.md file that guides a multi-step conversation — collecting project identity, goals, requirements, constraints, and architecture — then writes filled governance docs back to `governance/`. Each doc is filled with content that matches the parser regex patterns (RF-XX headings, bold-pipe outcome tables, guardrail ID tables). Final gate: `rai memory build` produces 30+ governance nodes.

**Components affected**:
- **`src/rai_cli/skills_base/project-create/SKILL.md`**: Create — the skill file
- **`src/rai_cli/skills_base/__init__.py`**: Modify — add `"project-create"` to `DISTRIBUTABLE_SKILLS`

**IMPORTANT**: This is a **skill-only** story. No new CLI commands. No new Python modules. The skill reads existing templates, conducts conversation, writes filled docs, and calls existing CLI commands (`rai memory build`).

---

## 3. Interface / Examples

### Skill Invocation

```
User: /project-create
```

The skill triggers when invoked on a project that has `rai init` already run (governance/ directory exists with templates).

### Conversation Flow

```
Step 1: Verify prerequisites
  - Check governance/ exists (raise init was run)
  - Check templates have placeholder content (not already filled)
  - If brownfield detected → recommend /project-onboard instead

Step 2: Collect project identity
  Rai asks: "What are you building? Give me a name and a one-paragraph description."
  User: "TaskFlow — a CLI task management tool for developers who prefer terminal workflows."

Step 3: Collect goals and requirements
  Rai asks: "What are the 3-5 core capabilities TaskFlow must have?"
  User: "1. Create/manage tasks from CLI  2. Filter by status/priority  3. Sync with GitHub issues"
  → Maps to RF-01, RF-02, RF-03 in prd.md

Step 4: Collect quality constraints
  Rai asks: "What quality standards matter? (e.g., test coverage, type safety, performance targets)"
  User: "100% type safe, >90% coverage, CLI response <200ms"
  → Maps to guardrails table entries

Step 5: Collect architecture context
  Rai asks: "Who/what interacts with TaskFlow? Any external systems?"
  User: "Developers use the CLI. It syncs with GitHub API. Data stored locally in SQLite."
  → Maps to system-context.md and system-design.md

Step 6: Generate and write all governance docs
  - Fill each template with conversation content
  - Ensure parser-compatible format (RF-XX headings, bold-pipe tables, etc.)
  - Write to governance/

Step 7: Build graph and verify
  $ rai memory build
  → Verify 30+ governance nodes extracted

Step 8: Summary and next steps
  Rai shows: what was created, node count, recommends /session-start
```

### Generated Content Example — prd.md (filled)

```markdown
# PRD: TaskFlow

> Product Requirements Document

---

## Problem

Developers who prefer terminal workflows lack a lightweight task management tool that integrates with their existing GitHub-based workflow. Existing tools require browser context-switching or heavy IDE plugins.

## Goals

- Provide fast, keyboard-driven task management from the terminal
- Integrate bidirectionally with GitHub Issues for team visibility
- Keep data portable with local-first storage

---

## Requirements

### RF-01: Task CRUD Operations

Create, read, update, and delete tasks from the command line with intuitive subcommands. Support bulk operations and piped input.

### RF-02: Filtering and Search

Filter tasks by status, priority, assignee, and labels. Support compound filters and saved filter presets.

### RF-03: GitHub Issue Sync

Bidirectional sync between local tasks and GitHub Issues. Conflict resolution favors the most recent change. Sync runs on explicit command, not automatically.
```

### Generated Content Example — guardrails.md (filled)

```markdown
---
type: guardrails
version: "1.0.0"
---

# Guardrails: TaskFlow

> Code and architecture guardrails

---

## Guardrails Activos

### Code Quality

| ID | Level | Guardrail | Verification | Derived from |
|----|-------|-----------|--------------|--------------|
| must-code-001 | MUST | Type hints on all public APIs | pyright --strict | RF-01 |
| must-code-002 | MUST | Ruff linting passes | ruff check . | RF-01 |

### Testing

| ID | Level | Guardrail | Verification | Derived from |
|----|-------|-----------|--------------|--------------|
| must-test-001 | MUST | >90% test coverage | pytest --cov ≥ 90% | RF-01 |
| must-test-002 | MUST | All tests pass | pytest exits 0 | RF-01 |

### Performance

| ID | Level | Guardrail | Verification | Derived from |
|----|-------|-----------|--------------|--------------|
| should-perf-001 | SHOULD | CLI response <200ms | benchmark test | RF-02 |
```

### Generated Content Example — vision.md (filled)

```markdown
# Solution Vision: TaskFlow

> Solution vision

## Identity

### Description

TaskFlow is a terminal-native task management tool for developers. It replaces browser-based project boards with fast CLI commands that integrate with GitHub Issues, keeping developers in their flow while maintaining team visibility.

## Outcomes

| **Outcome** | **Description** |
|-------------|-----------------|
| **Developer Flow** | Developers manage tasks without leaving the terminal |
| **Team Visibility** | Tasks sync to GitHub Issues for non-CLI team members |
| **Data Portability** | SQLite local storage enables offline work and backup |
```

### Parser Contract (Critical)

Each generated doc **MUST** match its parser's regex patterns:

| Doc | Parser expects | Pattern |
|-----|---------------|---------|
| `prd.md` | `### RF-XX: Title` headings | `^### (RF-\d+):\s*(.+)$` |
| `vision.md` | Bold-pipe outcome table rows | `\|\s*\*\*([^*]+)\*\*\s*\|\s*(.+?)\s*\|` |
| `guardrails.md` | YAML frontmatter `type: guardrails` + ID table rows | Frontmatter + `\|\s*(must\|should)-` |
| `backlog.md` | `# Backlog: Name` + epic table | `^# Backlog:\s*(.+)$` |
| `system-context.md` | External interfaces table | Table with System/Direction/Protocol/Description |
| `system-design.md` | Components table | Table with Component/Responsibility/Technology |

---

## 4. Acceptance Criteria

### Must Have

- [ ] Skill file `project-create/SKILL.md` follows standard skill structure (frontmatter, steps, verification)
- [ ] Skill collects project info through conversation (not all-at-once prompt)
- [ ] Generated governance docs match parser regex patterns (RF-XX, bold-pipe, guardrail IDs)
- [ ] `rai memory build` produces 30+ governance nodes after skill completes
- [ ] Skill added to `DISTRIBUTABLE_SKILLS` in `skills_base/__init__.py`
- [ ] Poka-yoke: verifies `governance/` exists before starting; recommends `/project-onboard` if existing code detected

### Should Have

- [ ] Shu/Ha/Ri adaptive verbosity (Shu: explain each step; Ri: just ask and write)
- [ ] Generates at least 3 RF-XX requirements, 3 outcomes, 5 guardrails, 2 architecture components
- [ ] Backlog.md populated with at least one epic derived from requirements

### Must NOT

- [ ] Must NOT create new CLI commands or Python modules — this is skill-only
- [ ] Must NOT overwrite governance docs that already have non-placeholder content
- [ ] Must NOT hardcode project-specific content — all content comes from conversation
- [ ] Must NOT skip the graph build verification gate

---

<details>
<summary><h2>5. Detailed Scenarios</h2></summary>

### Scenario 1: Happy Path — Fresh Greenfield

```gherkin
Given a project with `rai init` completed (governance/ has templates)
When user invokes /project-create
Then Rai asks about project identity, requirements, constraints, architecture
And fills all 6 governance docs with parser-compatible content
And runs `rai memory build` producing 30+ nodes
And displays summary with node count and recommends /session-start
```

### Scenario 2: Already Filled — Idempotency

```gherkin
Given governance docs already contain non-placeholder content
When user invokes /project-create
Then Rai detects existing content and asks whether to overwrite or skip
And skips docs the user wants to preserve
```

### Scenario 3: No governance/ — Missing Prerequisites

```gherkin
Given `rai init` has not been run (no governance/ directory)
When user invokes /project-create
Then Rai stops with clear message: "Run `rai init` first"
And does not proceed with conversation
```

</details>

---

## References

**Related ADRs**:
- ADR-012: Skills + Toolkit Architecture (skills orchestrate, CLI provides data)
- ADR-024: Deterministic Session Protocol (CLI bundles, skills interpret)

**Related Stories**:
- S7.1: Governance scaffolding CLI (dependency — done)
- S7.3: `/project-onboard` skill (parallel — brownfield)

**Parser sources** (for content format validation):
- `src/rai_cli/governance/parsers/prd.py` — RF-XX heading regex
- `src/rai_cli/governance/parsers/vision.py` — bold-pipe outcome regex
- `src/rai_cli/governance/parsers/guardrails.py` — YAML frontmatter + ID table
- `src/rai_cli/governance/parsers/backlog.py` — Backlog heading + epic table

**Template sources** (what we're filling):
- `src/rai_cli/rai_base/governance/*.md` — S7.1 templates

---

**Created**: 2026-02-08
**Based on**: S7.1 implementation analysis, parser contract reverse-engineering
