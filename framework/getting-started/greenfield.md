# Greenfield Adoption Guide

> Starting a new project with RaiSE from day one

---

## Overview

Greenfield is the ideal RaiSE scenario—full governance from the start. You'll establish the complete structure before writing any code.

## Phase 1: Foundation (Hour 1)

### Step 1: Initialize Repository

```bash
# Create and initialize
mkdir my-project && cd my-project
git init

# Create three-directory structure
mkdir -p .raise governance work
mkdir -p work/features work/research
```

### Step 2: Copy RaiSE Engine

Copy or clone the `.raise/` engine from raise-commons:

```bash
# Option A: Copy from local raise-commons
cp -r /path/to/raise-commons/.raise/* .raise/

# Option B: Use raise-kit (when available)
raise init
```

### Step 3: Initialize Governance Index

Create `governance/index.yaml`:

```yaml
schema_version: "1.0.0"
solution:
  name: "Your Project Name"
  status: active
artifacts: []
```

---

## Phase 2: Solution Definition (Day 1)

### Step 4: Define Business Case

Run the `solution/discovery` kata:

```
/raise.solution.discovery
```

This produces `governance/business_case.md`:
- Problem statement
- Stakeholders
- Success metrics

### Step 5: Create Solution Vision

Run the `solution/vision` kata:

```
/raise.solution.vision
```

This produces `governance/vision.md`:
- Technical approach
- Architecture direction
- Key decisions

### Step 6: Establish Guardrails

Run the `setup/governance` kata:

```
/raise.governance
```

This produces `governance/guardrails.md`:
- Coding standards
- Review requirements
- Quality gates

---

## Phase 3: First Project (Week 1)

### Step 7: Create Project PRD

For your first deliverable, run `project/discovery`:

```
/raise.project.discovery
```

### Step 8: Technical Design

Run `project/design`:

```
/raise.project.design
```

### Step 9: Create Backlog

Run `project/backlog`:

```
/raise.project.backlog
```

---

## Phase 4: First Feature (Week 2+)

### Step 10: Implement Features

For each story in your backlog:

1. `feature/design` — Technical approach
2. `feature/stories` — Acceptance criteria
3. `feature/plan` — Task breakdown
4. `feature/implement` — Guided coding
5. `feature/review` — Gate validation

---

## Directory Structure After Setup

```
my-project/
├── .raise/
│   ├── katas/           # Guided workflows
│   ├── templates/       # Document templates
│   ├── gates/           # Validation criteria
│   └── agents/          # AI agent configs
├── governance/
│   ├── index.yaml       # Artifact manifest
│   ├── business_case.md # Solution-level
│   ├── vision.md        # Solution-level
│   ├── guardrails.md    # Solution-level
│   ├── prd.md           # Project-level
│   ├── design.md        # Project-level
│   └── backlog.md       # Project-level
├── work/
│   ├── stories/        # Feature work
│   └── research/        # Spikes, exploration
└── src/                 # Your source code
```

---

## What Success Looks Like

After greenfield setup:

- ✅ Clear governance from day one
- ✅ Every decision documented
- ✅ AI assistance channeled through katas
- ✅ Quality gates prevent drift
- ✅ Full traceability of artifacts

---

## Next Steps

1. Complete solution definition (Steps 4-6)
2. Plan your first project
3. Start implementing features

---

*See also: [Brownfield Guide](./brownfield.md) | [Artifacts Hierarchy](../concepts/artifacts.md)*
