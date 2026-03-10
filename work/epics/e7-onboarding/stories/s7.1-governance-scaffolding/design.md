---
id: S7.1
title: "Governance Scaffolding CLI"
epic: E7
size: S
status: design
---

# S7.1: Governance Scaffolding CLI — Design

## What & Why

**Problem:** `rai init` creates infrastructure (`.raise/`, profile, skills) but leaves `governance/` empty. Without governance docs, the knowledge graph has zero governance nodes, and onboarding skills (S7.2/S7.3) have no templates to fill.

**Value:** After this story, `rai init` produces a `governance/` directory with parser-compatible templates. `rai memory build` can immediately produce governance nodes from them — unblocking both onboarding skills.

## Architectural Context

- **Module:** mod-onboarding (bc-experience, lyr-integration)
- **Touches:** mod-cli (orchestration — calls the scaffolding), rai_base (new asset package)
- **Pattern:** CLI provides deterministic structure; skills provide content (ADR-012)
- **Key constraint:** Templates MUST match parser extraction patterns (PAT-059)

## Approach

**Templates as bundled assets** — following the established `rai_base` pattern (bootstrap.py).

Governance templates live as **markdown files** in `src/rai_cli/rai_base/governance/`, the exact files that parsers need. `scaffold_governance()` copies them to `governance/` via `importlib.resources`, rendering `{project_name}` placeholders. This makes templates the **contract** between scaffolding and parsing — if a parser changes, the template changes with it, and the integration test catches drift.

**Components:**
- `src/rai_cli/rai_base/governance/` — **create**: template markdown files (the contract)
- `src/rai_cli/onboarding/governance.py` — **modify**: add `scaffold_governance()` that copies from rai_base
- `src/rai_cli/cli/commands/init.py` — **modify**: call `scaffold_governance()`, add skill recommendation to output
- Tests — **create**: unit + integration tests

**Why not Python strings?** Templates are inspectable markdown. They serve as single source of truth. They can be validated independently against parsers. Follows the existing `rai_base` asset distribution pattern.

## Examples

### CLI Usage

```bash
# Greenfield project
$ raise init
# ... existing output ...
# Created: governance/           — governance templates (6 docs)
#
# Next step:
#   /project-create  — fill governance from conversation (greenfield)

# Brownfield project
$ raise init
# ... existing output ...
# Created: governance/           — governance templates (6 docs)
#
# Next step:
#   /project-onboard — analyze codebase and fill governance (brownfield)
```

### Asset Package Structure

```
src/rai_cli/rai_base/
├── governance/              # NEW — governance templates
│   ├── __init__.py
│   ├── prd.md
│   ├── vision.md
│   ├── guardrails.md
│   ├── backlog.md
│   └── architecture/
│       ├── __init__.py
│       ├── system-context.md
│       └── system-design.md
├── identity/                # existing
├── memory/                  # existing
└── framework/               # existing
```

### Scaffolded Directory (target project)

```
governance/
├── prd.md            # Product Requirements Document
├── vision.md         # Solution Vision
├── guardrails.md     # Code & Architecture Guardrails
├── backlog.md        # Epic/Feature Backlog
└── architecture/
    ├── system-context.md    # System Context (C4 Level 1)
    └── system-design.md     # System Design (C4 Level 2)
```

### Template: rai_base/governance/prd.md

Parser expects: `### RF-XX: Title` headings (regex `^### (RF-\d+):\s*(.+)$`).

```markdown
# PRD: {project_name}

> Product Requirements Document — fill with /project-create or /project-onboard

---

## Problem

<!-- Describe the problem this project solves -->

## Goals

<!-- What success looks like -->

---

## Requirements

### RF-01: Core Functionality

<!-- Describe the primary capability this project must provide -->

### RF-02: User Experience

<!-- Describe how users interact with the project -->
```

### Template: rai_base/governance/vision.md

Parser expects: table rows `| **Outcome Name** | Description |` (bold first column).

```markdown
# Solution Vision: {project_name}

> Solution vision — fill with /project-create or /project-onboard

## Identity

### Description

<!-- One-paragraph description of what this project is and why it exists -->

## Outcomes

| **Outcome** | **Description** |
|-------------|-----------------|
| **Core Value** | <!-- Primary value delivered to users --> |
| **Quality** | <!-- Quality standards this project meets --> |
```

### Template: rai_base/governance/guardrails.md

Parser expects: YAML frontmatter with `type: guardrails`, then tables under `###` sections with `| ID | Level | Guardrail | Verification | Derived from |`.

```markdown
---
type: guardrails
version: "1.0.0"
---

# Guardrails: {project_name}

> Code and architecture guardrails — fill with /project-create or /project-onboard

---

## Guardrails Activos

### Code Quality

| ID | Level | Guardrail | Verification | Derived from |
|----|-------|-----------|--------------|--------------|
| must-code-001 | MUST | Type hints on all public APIs | pyright --strict | RF-01 |
```

### Template: rai_base/governance/backlog.md

Parser expects: `# Backlog: ProjectName` header and epic table `| E\d+ | **Name** | ...`.

```markdown
# Backlog: {project_name}

> **Status**: Draft

## Epics

| ID | Epic | Status | Scope | Priority |
|----|------|--------|-------|----------|
```

### Function Signature

```python
def scaffold_governance(
    project_path: Path,
    project_name: str,
) -> GovernanceScaffoldResult:
    """Scaffold governance/ from bundled rai_base templates.

    Copies template files via importlib.resources, rendering
    {project_name} placeholders. Per-file idempotency: existing
    files are never overwritten.

    Follows bootstrap.py pattern for asset distribution.
    """
```

```python
class GovernanceScaffoldResult(BaseModel):
    """Result of governance scaffolding."""
    already_existed: bool
    files_created: int
    files_skipped: int
    path: Path
```

### Integration Test (M1 Gate)

```python
def test_scaffold_then_build_produces_nodes(tmp_path):
    """S7.1 M1 gate: scaffold → build → verify governance nodes."""
    # 1. Scaffold governance templates
    result = scaffold_governance(tmp_path, "test-project")
    assert result.files_created >= 4

    # 2. Build graph
    builder = UnifiedGraphBuilder(tmp_path)
    graph = builder.build()

    # 3. Verify governance nodes exist
    governance_types = {n.type for n in graph.nodes if n.type in {
        "requirement", "outcome", "guardrail"
    }}
    assert "requirement" in governance_types
    assert "outcome" in governance_types
    assert "guardrail" in governance_types
```

## Acceptance Criteria

**MUST:**
- Governance templates live as files in `src/rai_cli/rai_base/governance/` (not Python strings)
- `rai init` scaffolds `governance/` with 6 template files (prd, vision, guardrails, backlog, system-context, system-design)
- Templates have exact patterns for existing parsers (RF-XX headings, bold table cells, YAML frontmatter)
- `rai memory build` produces governance nodes from scaffolded templates
- Per-file idempotency: existing files never overwritten (follows bootstrap.py pattern)
- `rai init` output recommends `/project-create` (greenfield) or `/project-onboard` (brownfield)

**SHOULD:**
- Templates include HTML comments as placeholders for skill content
- `{project_name}` substituted in template headers

**MUST NOT:**
- Overwrite existing `governance/` files
- Embed template content as Python strings
- Generate content (that's S7.2/S7.3 — skills provide content, CLI provides structure)
- Add YAML frontmatter to files whose parsers don't expect it (only guardrails.md gets frontmatter)
