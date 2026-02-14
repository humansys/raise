---
name: rai-project-create
description: >
  Guide greenfield project setup through conversation. Fills governance templates
  with project-specific content and builds the knowledge graph. Use after rai init
  on a new project.

license: MIT

metadata:
  raise.work_cycle: utility
  raise.frequency: on-demand
  raise.fase: ""
  raise.prerequisites: ""
  raise.next: "session-start"
  raise.gate: "raise memory build produces 30+ governance nodes"
  raise.adaptable: "true"
  raise.version: "1.0.0"
---

# Project Create: Greenfield Onboarding

## Purpose

Guide a developer through greenfield project setup via conversation. Collect project identity, requirements, constraints, and architecture context, then fill governance templates with parser-compatible content. Final gate: `rai memory build` produces 30+ governance nodes, making `/rai-session-start` immediately useful.

## Mastery Levels (ShuHaRi)

**Shu (守)**: Walk through every step with explanations. Show what each governance doc is for and why the format matters. Confirm each doc before writing.

**Ha (破)**: Collect info conversationally, confirm the full set before writing. Skip explanations of governance concepts.

**Ri (離)**: Collect all info in 1-2 exchanges. Write all docs. Build graph. Done.

## Context

**When to use:**
- After `rai init` on a new (greenfield) project
- When `governance/` exists but contains only placeholder templates
- When starting a project from scratch

**When to skip:**
- Project already has filled governance docs (non-placeholder content)
- Brownfield project with existing code → use `/rai-project-onboard` instead
- Project not yet initialized → run `rai init` first

**Inputs required:**
- A project with `rai init` already completed (`governance/` directory exists)
- Developer's knowledge of what they're building

**Output:**
- 6 governance docs filled with project-specific content
- Knowledge graph with 30+ governance nodes
- Project ready for `/rai-session-start`

## Steps

### Step 1: Verify Prerequisites (Poka-Yoke)

Check that the project is ready for greenfield onboarding.

```bash
ls governance/prd.md governance/vision.md governance/guardrails.md governance/backlog.md governance/architecture/system-context.md governance/architecture/system-design.md 2>/dev/null | wc -l
```

**Decision:**
- 6 files found → Continue (templates exist from `rai init`)
- 0 files → **STOP.** Tell the user: "Run `rai init` first to scaffold governance templates."
- Some but not all → Warn and continue with available templates

**Also check for existing content:**
```bash
grep -L "<!-- " governance/*.md governance/architecture/*.md 2>/dev/null
```

Files without HTML comment placeholders likely have real content already.

- All have placeholders → Fresh templates, proceed normally
- Some have content → Ask user: "These docs already have content: [list]. Overwrite or skip?"

**Also check for brownfield signals:**
```bash
ls src/ lib/ app/ *.py *.ts *.js 2>/dev/null | head -5
```

If source code exists, suggest: "This looks like an existing project. Consider `/rai-project-onboard` instead for brownfield analysis."

**Verification:** Governance templates exist and are ready to fill.

> **If you can't continue:** No governance/ → Run `rai init` first. Always.

### Step 2: Collect Project Identity

Ask the developer about their project. This is the foundation — everything else builds on it.

**Ask:**
> "What are you building? Give me:
> 1. **Project name** (one word or short phrase)
> 2. **One-paragraph description** — what it is, who it's for, why it exists"

**What you need from this:**
- Project name (used in all doc headers)
- Description paragraph (goes into `vision.md` Identity section)
- Enough context to ask good follow-up questions

**Verification:** You have a project name and a description paragraph.

> **If you can't continue:** User gives vague answer → Ask clarifying questions. "Who uses this? What problem does it solve?"

### Step 3: Collect Goals and Requirements

Ask about core capabilities. These become the RF-XX requirements in `prd.md`.

**Ask:**
> "What are the 3-5 core things [project name] must do? Think features, not implementation."

**What you need:**
- 3-5 features from the user, which you'll decompose into **5-8 RF-XX requirements** (split broad features into specific capabilities)
- Enough detail to write 2-3 sentence descriptions per requirement
- Understanding of the problem being solved (for PRD Problem section)

**Also collect:**
- What success looks like (PRD Goals section)
- Key outcomes (vision.md Outcomes table)

**Verification:** You have 3-5 capabilities and understand the problem space.

> **If you can't continue:** User lists implementation details instead of features → Redirect: "Those sound like HOW. What does the user GET?"

### Step 4: Collect Quality Constraints

Ask about standards and guardrails. These become entries in `guardrails.md`.

**Ask:**
> "What quality standards matter for [project name]? For example:
> - Testing: coverage targets, test types
> - Code quality: type safety, linting, style
> - Security: authentication, data handling
> - Performance: response times, throughput
> - Architecture: patterns, boundaries"

**What you need:**
- At least 5 guardrails across 2+ categories
- Each with: ID, level (MUST/SHOULD), description, verification command
- Categories map to guardrails.md sections (Code Quality, Testing, Security, etc.)

**Default guardrails** (include unless user opts out):
- `must-code-001`: Type hints on all public APIs → `pyright --strict`
- `must-code-002`: Linting passes → `ruff check .`
- `must-test-001`: All tests pass → `pytest`

**Verification:** You have 5+ guardrails with verification commands.

> **If you can't continue:** User unsure about standards → Offer language-appropriate defaults and let them adjust.

### Step 5: Collect Architecture Context

Ask about the system's shape. This fills `system-context.md` and `system-design.md`.

**Ask:**
> "Let's sketch the architecture:
> 1. **Who/what uses [project name]?** (users, other systems, APIs)
> 2. **What external systems does it talk to?** (databases, APIs, services)
> 3. **What are the main components inside?** (modules, layers, services)"

**What you need:**
- External actors and systems (system-context.md)
- External interfaces with direction and protocol (system-context.md table)
- Internal components with responsibilities and technology (system-design.md table)

**Verification:** You have external actors, interfaces, and internal components.

> **If you can't continue:** User hasn't thought about architecture yet → Help them think through it: "If someone drew a box for [project name], what goes in and what connects to it?"

### Step 5.5: Collect Branch Configuration

Ask about the project's branch model. This is stored in `.raise/manifest.yaml` and used by all workflow skills.

**Ask:**
> "What's your branch model?
> 1. **Main/stable branch name** — e.g., `main`, `master`
> 2. **Development/integration branch name** — e.g., `main`, `develop`, `dev`
>
> If you work directly on `main` with no separate development branch, both are `main`."

**Defaults:** If the user is unsure, default both to `main` (simplest model).

**What you need:**
- `branches.main` — the stable branch (default: `main`)
- `branches.development` — the integration branch (default: `main`)

**Update manifest:**
```bash
# The manifest was created by rai init. Update it with branch config.
# Add to .raise/manifest.yaml:
# branches:
#   development: {dev_branch}
#   main: {main_branch}
```

**Verification:** Branch names captured. Manifest updated.

> **If you can't continue:** User unsure → Default both to `main`. Can change later.

### Step 6: Generate and Write Governance Docs

Now write all 6 governance docs with the collected information. **CRITICAL:** Follow the exact format for each doc — the graph parsers use regex patterns to extract nodes.

#### 6a: Write `governance/vision.md`

```markdown
# Solution Vision: {project_name}

> Solution vision

## Identity

### Description

{One-paragraph description from Step 2}

## Outcomes

| **Outcome** | **Description** |
|-------------|-----------------|
| **{Outcome 1 Name}** | {Description from Step 3} |
| **{Outcome 2 Name}** | {Description from Step 3} |
| **{Outcome 3 Name}** | {Description from Step 3} |
```

**IMPORTANT — Parser contract for vision.md:**
- Outcomes table MUST have `| **Outcome** |` as header (bold first column)
- Each data row MUST be `| **{Bold Name}** | {description} |`
- Parser regex: `\|\s*\*\*([^*]+)\*\*\s*\|\s*(.+?)\s*\|`
- Aim for 3-5 outcome rows

#### 6b: Write `governance/prd.md`

```markdown
# PRD: {project_name}

> Product Requirements Document

---

## Problem

{Problem description from Step 3 — 2-3 sentences}

## Goals

{Success criteria from Step 3 — bullet list}

---

## Requirements

### RF-01: {Requirement 1 Title}

{2-3 sentence description of the capability}

### RF-02: {Requirement 2 Title}

{2-3 sentence description}

### RF-03: {Requirement 3 Title}

{2-3 sentence description}
```

**IMPORTANT — Parser contract for prd.md:**
- Each requirement MUST be `### RF-XX: Title` (### heading, RF- prefix, dash-digits, colon, space, title)
- Parser regex: `^### (RF-\d+):\s*(.+)$`
- Content below the heading is captured as the requirement body (up to next ### or 20 lines)
- Aim for 3-5 requirements (RF-01 through RF-05)

#### 6c: Write `governance/guardrails.md`

```markdown
---
type: guardrails
version: "1.0.0"
---

# Guardrails: {project_name}

> Code and architecture guardrails

---

## Guardrails Activos

### Code Quality

| ID | Level | Guardrail | Verification | Derived from |
|----|-------|-----------|--------------|--------------|
| must-code-001 | MUST | {description} | {command} | RF-01 |
| must-code-002 | MUST | {description} | {command} | RF-01 |

### Testing

| ID | Level | Guardrail | Verification | Derived from |
|----|-------|-----------|--------------|--------------|
| must-test-001 | MUST | {description} | {command} | RF-01 |

### Security

| ID | Level | Guardrail | Verification | Derived from |
|----|-------|-----------|--------------|--------------|
| must-sec-001 | MUST | {description} | {command} | RF-01 |
```

**IMPORTANT — Parser contract for guardrails.md:**
- MUST have YAML frontmatter with `type: guardrails`
- Table under `### {Section Name}` heading
- Table MUST have header: `| ID | Level | Guardrail | Verification | Derived from |`
- ID format: `{level}-{category}-{NNN}` (e.g., `must-code-001`, `should-perf-001`)
- Level: `MUST` or `SHOULD`
- Aim for 5-10 guardrails across 2-4 sections

#### 6d: Write `governance/backlog.md`

```markdown
# Backlog: {project_name}

> **Status**: Draft

## Epics

| ID | Epic | Status | Scope | Priority |
|----|------|--------|-------|----------|
| E1 | {First epic name} | Draft | — | P1 |
| E2 | {Second epic name} | Draft | — | P2 |
```

**IMPORTANT — Parser contract for backlog.md:**
- Header MUST be `# Backlog: {project_name}` (exact format)
- Epic table rows: `| E{N} | Name | Status | Scope | Priority |`
- Parser regex for header: `^# Backlog:\s*(.+)$`
- Parser regex for epics: `^\|\s*(E\d+)\s*\|`
- Aim for 2-4 epics derived from the requirements

#### 6e: Write `governance/architecture/system-context.md`

```markdown
# System Context: {project_name}

> C4 Level 1 — System Context diagram and description

## Overview

{High-level description from Step 5 — what is this system and who uses it?}

## Context Diagram

```
┌──────────┐       ┌──────────────┐       ┌──────────┐
│  {Actor}  │──────►│ {project_name} │◄──────│ {System} │
│          │       │              │       │          │
└──────────┘       └──────────────┘       └──────────┘
```

## External Interfaces

| System | Direction | Protocol | Description |
|--------|-----------|----------|-------------|
| {System 1} | {Inbound/Outbound/Both} | {HTTP/CLI/SQL/etc} | {What it does} |
| {System 2} | {Direction} | {Protocol} | {Description} |
```

#### 6f: Write `governance/architecture/system-design.md`

```markdown
# System Design: {project_name}

> C4 Level 2 — Container/component decomposition

## Architecture Overview

{Architecture description from Step 5}

## Components

| Component | Responsibility | Technology |
|-----------|---------------|------------|
| {Component 1} | {What it does} | {Tech stack} |
| {Component 2} | {What it does} | {Tech stack} |

## Key Decisions

- {Any architectural decisions mentioned in conversation}
```

**Verification:** All 6 governance docs written with project-specific content. No HTML comment placeholders remain.

> **If you can't continue:** Write fails → Check file permissions. Governance dir should be writable.

### Step 7: Build Graph and Verify (Gate)

Run the graph builder and verify the 30+ node gate.

```bash
rai memory build
```

**Expected output:** The build should show governance nodes extracted from each doc.

**Verification gate:**
```bash
rai memory query "requirement outcome guardrail" --types requirement,outcome,guardrail --limit 50
```

Count the governance nodes. You need **30+ total** across these types:
- Requirements (from prd.md): ~5-8 nodes (RF-01 through RF-05+)
- Outcomes (from vision.md): ~5-7 nodes (bold-pipe table rows)
- Guardrails (from guardrails.md): ~10-13 nodes (table rows across sections)
- Project (from backlog.md): 1 node
- Epics (from backlog.md): ~3-5 nodes (table rows)
- Architecture docs don't produce individual nodes but enrich the graph context

**Decision:**
- 30+ nodes → **Gate passed.** Continue to summary.
- <30 nodes → Investigate which docs didn't parse. Check format against parser contract in Step 6. Fix and rebuild.

**Verification:** `rai memory build` succeeds and produces 30+ governance nodes.

> **If you can't continue:** Nodes too low → Most common cause is format mismatch. Check RF-XX headings, bold-pipe tables, guardrail IDs, backlog header. Fix the specific doc and rebuild.

### Step 8: Summary and Next Steps

Present what was created and what to do next.

**Display:**
```
## Project Created: {project_name}

**Governance docs filled:**
- governance/vision.md — {N} outcomes
- governance/prd.md — {N} requirements
- governance/guardrails.md — {N} guardrails
- governance/backlog.md — {N} epics
- governance/architecture/system-context.md — context diagram + interfaces
- governance/architecture/system-design.md — components + decisions

**Graph:** {total} governance nodes extracted

**Next steps:**
1. Run `/rai-session-start` to begin your first working session
2. Review the generated governance docs and refine as needed
3. Start your first epic with `/rai-epic-design`
```

**Verification:** Summary displayed with node counts.

> **If you can't continue:** Everything should be done by now. If graph is still <30 nodes after fixes, proceed anyway with a warning — the user can refine docs later.

## Output

| Item | Destination |
|------|-------------|
| Filled governance docs | `governance/` (prd.md, vision.md, guardrails.md, backlog.md, architecture/) |
| Knowledge graph | `.raise/rai/memory/index.json` (via `rai memory build`) |
| Summary | Displayed to user |

## Notes

### Parser Contract

Generated content **MUST** match parser regex patterns exactly. The graph parsers extract nodes from specific Markdown structures — if the format is wrong, nodes won't be extracted and the 30+ gate will fail.

### Idempotency

The skill checks for existing non-placeholder content before writing. Docs that already have real content are skipped unless the user explicitly requests overwrite.

### Greenfield vs Brownfield

This skill is for **greenfield** projects only. It asks "what do you want to build?" — a creative conversation. For brownfield projects that need "what do you already have?", use `/rai-project-onboard` (S7.3).

## References

- Prerequisite: `rai init` (governance scaffolding from S7.1)
- Next: `/rai-session-start`
- Sibling: `/rai-project-onboard` (brownfield)
- Parser sources: `src/rai_cli/governance/parsers/*.py`
- Template sources: `src/rai_cli/rai_base/governance/*.md`
