---
name: rai-project-create
description: Set up governance for a new project. Use after rai init on a greenfield project.

license: MIT

metadata:
  raise.work_cycle: utility
  raise.frequency: on-demand
  raise.fase: ""
  raise.prerequisites: ""
  raise.next: "session-start"
  raise.gate: "rai graph build produces 30+ governance nodes"
  raise.adaptable: "true"
  raise.version: "2.0.0"
  raise.visibility: public
---

# Project Create

## Purpose

Guide a developer through greenfield project setup via conversation. Collect project identity, requirements, constraints, and architecture, then fill 6 governance templates. Gate: `rai graph build` produces 30+ governance nodes.

## Mastery Levels (ShuHaRi)

- **Shu**: Walk through every step with explanations, confirm each doc before writing
- **Ha**: Collect info conversationally, confirm full set before writing
- **Ri**: Collect all info in 1-2 exchanges, write all docs, build graph

## Context

**When to use:** After `rai init` on a new (greenfield) project with placeholder governance templates.

**When to skip:** Brownfield project with existing code → use `/rai-project-onboard`. Project not initialized → run `rai init` first.

**Inputs:** Project with `rai init` completed (`governance/` exists). Developer's knowledge of what they're building.

## Steps

### Step 1: Verify Prerequisites

```bash
ls governance/prd.md governance/vision.md governance/guardrails.md governance/backlog.md governance/architecture/system-context.md governance/architecture/system-design.md 2>/dev/null | wc -l
```

| Result | Action |
|--------|--------|
| 6 files | Continue |
| 0 files | Stop: "Run `rai init` first." |
| Source code exists | Suggest `/rai-project-onboard` instead |

Check for existing non-placeholder content — ask before overwriting.

<verification>
Governance templates exist and ready to fill.
</verification>

### Step 2: Collect Project Info (Conversational)

Ask in sequence, adapting to ShuHaRi level:

1. **Identity:** Project name + one-paragraph description (who, what, why)
2. **Capabilities:** 3-5 core things it must do → decompose into 5-8 RF-XX requirements
3. **Quality:** Testing, code quality, security, performance constraints → 5+ guardrails
4. **Architecture:** External actors/systems, internal components, protocols
5. **Branches:** Main branch name, development branch name (default both to `main`)

<verification>
All governance fields covered from conversation.
</verification>

### Step 3: Write 6 Governance Docs

Write all docs following parser contracts exactly. Graph parsers use regex — format must match.

**Parser contracts (critical):**
- `vision.md`: Outcomes table with `| **{Bold Name}** | {description} |`. Regex: `\|\s*\*\*([^*]+)\*\*\s*\|\s*(.+?)\s*\|`
- `prd.md`: Requirements as `### RF-XX: Title`. Regex: `^### (RF-\d+):\s*(.+)$`
- `guardrails.md`: YAML frontmatter `type: guardrails`. Table with `| ID | Level | Guardrail | Verification | Derived from |`. ID format: `{level}-{category}-{NNN}`
- `backlog.md`: Header `# Backlog: {name}`. Epic rows `| E{N} | ... |`
- `system-context.md`: External interfaces table
- `system-design.md`: YAML frontmatter `type: architecture_design`. `layers` must be a list of dicts — each with `name`, `modules` (list), and optionally `description`. **NEVER write layers as plain strings** (causes `AttributeError: 'str' object has no attribute 'get'` in graph build). Example:
  ```yaml
  layers:
    - name: frontend
      modules: [ui, components]
      description: "User interface layer"
    - name: backend
      modules: [api, services]
      description: "Business logic layer"
  ```

Update `.raise/manifest.yaml` with branch configuration.

<verification>
All 6 docs written. No placeholder content remains.
</verification>

### Step 4: Build Graph & Verify Gate

```bash
rai graph build
rai graph query "requirement outcome guardrail" --types requirement,outcome,guardrail --limit 50
```

Need 30+ governance nodes total: requirements (~5-8), outcomes (~5-7), guardrails (~10-13), project (1), epics (~3-5).

| Result | Action |
|--------|--------|
| 30+ nodes | Gate passed → Step 5 |
| <30 nodes | Check format against parser contracts, fix specific doc, rebuild |

<verification>
Graph build succeeds. 30+ governance nodes extracted.
</verification>

### Step 5: Summary

```
## Project Created: {project_name}
Governance: {N} outcomes, {N} requirements, {N} guardrails, {N} epics
Graph: {total} governance nodes
Next: /rai-session-start
```

## Output

| Item | Destination |
|------|-------------|
| Governance docs | `governance/` (6 files) |
| Knowledge graph | `.raise/rai/memory/index.json` |
| Next | `/rai-session-start` |

## Quality Checklist

- [ ] Prerequisites verified before collecting info (poka-yoke)
- [ ] Parser contracts followed exactly (regex-compatible format)
- [ ] 30+ governance nodes gate passed
- [ ] Branch configuration saved to manifest
- [ ] Brownfield signals detected → suggest `/rai-project-onboard`
- [ ] NEVER overwrite existing non-placeholder governance content without asking

## References

- Prerequisite: `rai init`
- Sibling: `/rai-project-onboard` (brownfield)
- Parser sources: `src/raise_cli/governance/parsers/*.py`
- Template sources: `src/raise_cli/rai_base/governance/*.md`
- Next: `/rai-session-start`
