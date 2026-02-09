---
id: S7.1
title: "/onboard skill — guided project setup to RaiSE-ready"
epic: E7
type: story
status: design
size: M
module: mod-onboarding
domain: bc-experience
layer: skill (orchestrates existing CLI + discovery pipeline)
---

# /onboard — Guided Project Setup to RaiSE-Ready

## What & Why

**Problem:** After `pip install raise-cli`, a new user has no guided path to a fully functional RaiSE project. `raise init` creates infrastructure (manifest, profile, Rai base, skills) but leaves the **governance content layer empty** — no PRD, vision, guardrails, or architecture docs. Without these, the graph has no governance concepts, skills fly blind, and `/session-start` has no project context to work with.

**Value:** `/onboard` is the single entry point that takes a user from `pip install` to "ready to plan first epic." It handles both greenfield and brownfield seamlessly, leaving every project with a working graph, governance structure, and a warm welcome from Rai.

## Approach

A **Claude Code skill** (`.claude/skills/onboard/SKILL.md`) that orchestrates a guided conversation through five phases. No new Python code — the skill composes existing CLI commands, discovery skills, and Rai's inference to generate governance artifacts.

**Core principle:** Greenfield needs intent from the user (code doesn't exist yet). Brownfield needs analysis of what exists + intent for where it's going. Both converge on the same governance structure.

**Components:**
- **Create:** `.claude/skills/onboard/SKILL.md`
- **Create:** `src/raise_cli/skills_base/onboard/SKILL.md` (distributable copy)
- **Modify:** `src/raise_cli/skills_base/__init__.py` (add to DISTRIBUTABLE_SKILLS)

## Architectural Context

- **Module:** mod-onboarding (bc-experience domain, integration layer)
- **Pattern:** Thin inference skill over deterministic CLI (ADR-024)
- **Composes:** `raise init`, `raise discover scan`, `raise discover analyze`, `raise memory build`, discovery skills pipeline
- **Generates:** Governance docs in formats the graph parsers expect (see format specs below)

## Conversation Flow

```
/onboard
    │
    ├─ Phase 1: Welcome & Identity
    │   ├─ Introduce Rai
    │   ├─ Ask user's name
    │   └─ Confirm project directory
    │
    ├─ Phase 2: Infrastructure
    │   ├─ raise init (creates manifest, profile, Rai base, skills, MEMORY.md)
    │   ├─ Update profile name: raise session start --name "<name>" --project "$(pwd)"
    │   └─ Report what was created
    │
    ├─ Phase 3: Project Understanding (branches on type)
    │   │
    │   ├─ GREENFIELD (0 code files):
    │   │   ├─ Ask: "What will this project do?" (1-2 sentences)
    │   │   ├─ Ask: "What language/stack are you planning to use?"
    │   │   ├─ Ask: "Who will use it?" (users/actors)
    │   │   └─ Ask: "What are the 3-5 most important things it must do?" (initial requirements)
    │   │
    │   └─ BROWNFIELD (1+ code files):
    │       ├─ raise init --detect (convention detection + guardrails + CLAUDE.md)
    │       ├─ Run discovery pipeline:
    │       │   ├─ raise discover scan (extract symbols)
    │       │   └─ raise discover analyze (confidence scoring + categorization)
    │       ├─ Review discovery results with user (batch by module)
    │       ├─ Ask: "What is this project's purpose?" (code shows what IS, not what SHOULD BE)
    │       ├─ Ask: "Where is it headed? What are the next goals?"
    │       └─ Ask: "Who uses it?" (users/actors)
    │
    ├─ Phase 4: Governance Scaffolding
    │   ├─ Generate governance/vision.md (from conversation)
    │   ├─ Generate governance/prd.md (from conversation)
    │   ├─ Generate governance/guardrails.md (greenfield: language defaults; brownfield: from --detect)
    │   ├─ Generate governance/architecture/:
    │   │   ├─ system-context.md (from project understanding)
    │   │   ├─ system-design.md (greenfield: minimal; brownfield: from discovery)
    │   │   ├─ domain-model.md (greenfield: minimal; brownfield: from discovery)
    │   │   └─ modules/*.md (brownfield only: from discovery analysis)
    │   ├─ Present summary to user for review
    │   └─ User confirms or adjusts
    │
    ├─ Phase 5: Activation
    │   ├─ raise memory build (index everything into graph)
    │   ├─ Verify: raise memory query "project" (graph works)
    │   ├─ Report graph stats (nodes, edges, types)
    │   └─ "You're ready. Type /session-start to begin."
    │
    └─ Done
```

## Examples

### Greenfield Conversation

```
User: /onboard

Rai: Welcome! I'm Rai — your AI partner for reliable software engineering.

     Together we'll build software that's both fast and reliable. Let me
     get you set up.

     What's your name?

User: Sarah

Rai: Nice to meet you, Sarah. Let me initialize your project...

     [runs: raise init]
     [runs: raise session start --name "Sarah" --project "$(pwd)"]

     ✓ Created .raise/manifest.yaml
     ✓ Created ~/.rai/developer.yaml (personalized for Sarah)
     ✓ Bootstrapped Rai base (identity + 20 universal patterns)
     ✓ Installed 19 skills

     I see this is a fresh project — no code yet. Let me understand
     what you're building so I can set up your governance structure.

     What will this project do? (1-2 sentences)

User: It's a REST API for managing a pet adoption platform

Rai: Got it — a pet adoption API. What language and stack are you planning?

User: Python with FastAPI and PostgreSQL

Rai: Good choices. Who will use this system?

User: Shelter staff manage listings, adopters browse and apply,
     admins handle approvals

Rai: Clear. What are the 3-5 most important things it must do?

User: 1. Shelter staff can create/update pet listings with photos
     2. Adopters can search and filter available pets
     3. Adopters can submit adoption applications
     4. Staff can review and approve/reject applications
     5. Email notifications for application status changes

Rai: Got it. Let me generate your governance structure...

     [generates governance/vision.md]
     [generates governance/prd.md with RF-01 through RF-05]
     [generates governance/guardrails.md with Python/FastAPI defaults]
     [generates governance/architecture/system-context.md]
     [generates governance/architecture/system-design.md (minimal)]
     [generates governance/architecture/domain-model.md (minimal)]

     ✓ Generated 6 governance documents

     Here's what I created:

     **Vision:** Pet adoption platform connecting shelters with adopters
     **Requirements:** 5 initial requirements (RF-01 to RF-05)
     **Guardrails:** Python + FastAPI code standards (MUST/SHOULD)
     **Architecture:** System context with 3 actors, 2 external systems

     Review these files in governance/ and adjust as needed.
     Now let me build your knowledge graph...

     [runs: raise memory build]

     ✓ Graph built: 47 nodes, 62 edges
       - 5 requirements, 3 outcomes, 12 guardrails
       - 20 patterns, 5 principles, 2 architecture nodes

     You're all set, Sarah! Type /session-start to begin your first
     working session. I'll help you plan your first epic.
```

### Brownfield Conversation

```
User: /onboard

Rai: Welcome! I'm Rai — your AI partner for reliable software engineering.
     What's your name?

User: Marco

Rai: Nice to meet you, Marco. Let me initialize and analyze your project...

     [runs: raise init --detect]

     ✓ Detected: Brownfield project (287 code files)
     ✓ Conventions: Python, 4-space indent, double quotes (HIGH confidence)
     ✓ Generated governance/guardrails.md (from detected conventions)
     ✓ Generated CLAUDE.md (project context)

     Now let me understand your codebase structure...

     [runs: raise discover scan]
     [runs: raise discover analyze]

     Found 43 components across 8 modules:
       - api/ (12 components) — REST endpoints
       - models/ (8 components) — Data models
       - services/ (9 components) — Business logic
       - utils/ (6 components) — Helpers
       ...

     Does this module breakdown look right? Any modules I should
     rename or merge?

User: Looks good, but utils/ is really "infrastructure"

Rai: Noted — I'll label it as infrastructure in the architecture docs.

     The code tells me what your project IS, but I need to understand
     where it's GOING. What is this project's purpose?

User: It's our internal inventory management system

Rai: And what are the next goals for it?

User: We need to add barcode scanning, real-time stock alerts,
     and a supplier portal

Rai: Who uses the system?

User: Warehouse staff, procurement team, and suppliers (new, for the portal)

Rai: Great. Let me generate governance and architecture docs...

     [generates governance/vision.md]
     [generates governance/prd.md with current + planned requirements]
     [generates governance/architecture/system-context.md]
     [generates governance/architecture/system-design.md (from discovery)]
     [generates governance/architecture/domain-model.md (from discovery)]
     [generates governance/architecture/modules/*.md (8 module docs)]

     ✓ Generated 14 governance + architecture documents

     [runs: raise memory build]

     ✓ Graph built: 112 nodes, 198 edges
       - 8 requirements, 4 outcomes, 18 guardrails
       - 43 components, 8 modules, 3 bounded contexts
       - 20 patterns, 5 principles, 4 architecture nodes

     You're all set, Marco! Type /session-start to begin.
     I already know your codebase structure, conventions, and goals.
```

### Already Initialized

```
User: /onboard

Rai: [checks: .raise/manifest.yaml exists]

     This project is already initialized with RaiSE.

     [checks: governance/ directory]

     But I notice governance docs are missing. Want me to help
     set those up? Or if everything's ready, type /session-start.
```

## Generated Document Formats

**IMPORTANT:** These formats are what the graph parsers expect. The skill MUST generate documents matching these structures.

### governance/prd.md

```markdown
# Product Requirements: {Project Name}

> **Status**: Draft
> **Date**: {today}
> **Version**: 1.0.0

## 1. Problem

{1-2 sentences from user conversation}

## 2. Goals

| Goal | Metric |
|------|--------|
| {goal} | {how to measure} |

## 3. Requirements

### RF-01: {Requirement title}

{Description from user input}

**Acceptance criteria:**
- {criterion}

### RF-02: {Next requirement}
...
```

### governance/vision.md

```markdown
# Vision: {Project Name}

> **Status**: Draft
> **Date**: {today}
> **Version**: 1.0.0

## 1. Identity

**Type:** {product type — API, CLI, platform, etc.}
**Description:** {1-2 sentences from conversation}

## 2. Outcomes

| Outcome | Description |
|---------|-------------|
| **{Outcome name}** | {What success looks like} |

## 3. Scope

### Must Have (MVP)
- {from requirements}

### Out of Scope
- {explicit boundaries}
```

### governance/guardrails.md

```yaml
---
type: guardrails
version: "1.0.0"
constraint_scopes:
  default: all_bounded_contexts
---
```

```markdown
# Code Guardrails: {Project Name}

## Guardrails

### Code Quality

| ID | Level | Rule | Verification |
|----|-------|------|-------------|
| MUST-CODE-001 | MUST | {language-appropriate rule} | {command} |

### Testing
...

### Security
...
```

**Greenfield:** Generate sensible defaults for the detected language/framework.
**Brownfield:** Already generated by `raise init --detect`. Skill verifies it exists, does not regenerate.

### governance/architecture/system-context.md

```yaml
---
type: architecture_context
project: {project_name}
status: draft
tech_stack:
  language: "{language}"
  framework: "{framework}"
external_dependencies:
  - "{dependency}"
users:
  - "{actor}"
governed_by:
  - "governance/guardrails.md"
  - "governance/vision.md"
---
```

```markdown
# System Context: {Project Name}

## What This System Does

{1-2 sentences}

## Actors

| Actor | Type | Interaction |
|-------|------|-------------|
| {actor} | {human/system} | {what they do} |

## External Systems

| System | Purpose |
|--------|---------|
| {system} | {why} |
```

### governance/architecture/system-design.md

```yaml
---
type: architecture_design
project: {project_name}
status: draft
layers:
  - name: {layer_name}
    modules: [{module_list}]
    description: "{layer description}"
guardrails_reference: "governance/guardrails.md"
---
```

**Greenfield:** Single layer with placeholder modules.
**Brownfield:** Layers inferred from discovery analysis (e.g., api → presentation, services → domain, models → data).

### governance/architecture/domain-model.md

```yaml
---
type: architecture_domain_model
project: {project_name}
status: draft
bounded_contexts:
  - name: {context_name}
    modules: [{module_list}]
    description: "{what this context owns}"
shared_kernel:
  modules: [{shared_modules}]
---
```

**Greenfield:** Single bounded context from project description.
**Brownfield:** Contexts inferred from module clustering in discovery.

### governance/architecture/modules/{name}.md (brownfield only)

```yaml
---
type: module
name: {module_name}
purpose: "{from discovery analysis}"
status: current
depends_on: [{dependencies}]
depended_by: [{dependents}]
components: {count}
---
```

```markdown
# Module: {module_name}

{Purpose description from discovery}

## Components

| Component | Type | Description |
|-----------|------|-------------|
| {name} | {class/function} | {from discovery} |
```

## Acceptance Criteria

### MUST

1. Skill exists at `.claude/skills/onboard/SKILL.md` with valid frontmatter
2. Skill asks user's name and personalizes the developer profile
3. Skill handles both greenfield and brownfield paths seamlessly (detects from `raise init` output)
4. Skill generates governance docs (vision.md, prd.md) from user conversation in both paths
5. Skill generates architecture docs with correct YAML frontmatter so graph parsers work
6. Skill runs `raise memory build` and verifies graph has governance nodes
7. Skill ends with clear "type /session-start" guidance
8. Skill is included in `DISTRIBUTABLE_SKILLS` (bundled on `raise init`)

### SHOULD

1. For brownfield: run discovery pipeline (`raise discover scan` + `raise discover analyze`) and use results for architecture docs
2. For brownfield: skip guardrails generation (already done by `raise init --detect`)
3. Detect already-initialized projects (`.raise/manifest.yaml` exists) and offer to fill governance gaps
4. Adapt verbosity to experience level (Shu=detailed, Ri=concise)
5. Present governance summary for user review before building graph

### MUST NOT

1. Generate governance docs that the graph parsers can't parse (wrong frontmatter, wrong section format)
2. Overwrite existing governance docs without user confirmation
3. Skip the human intent questions — code analysis alone is insufficient for PRD/vision
4. Require user to run terminal commands manually — skill handles all CLI calls
