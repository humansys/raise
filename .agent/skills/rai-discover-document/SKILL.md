---
description: 'Generate architecture documentation from discovery data. Produces system-level
  docs (C4 Context + Container), per-module docs with YAML frontmatter, and a compact
  index for AI context loading.

  '
license: MIT
metadata:
  raise.adaptable: 'true'
  raise.fase: '5'
  raise.frequency: per-project
  raise.gate: ''
  raise.next: ''
  raise.prerequisites: discover-validate
  raise.version: 2.0.0
  raise.visibility: public
  raise.work_cycle: discovery
name: rai-discover-document
---

# Discover Document

> **Deprecated:** Use `/rai-discover` instead, which runs the full pipeline (detect → extract → describe → document → build) in one pass. This skill is kept for backward compatibility.

## Purpose

Generate architecture documentation from discovery data: system-level C4 docs, per-module docs with YAML frontmatter, domain model, and a compact index for AI context loading.

## Mastery Levels (ShuHaRi)

- **Shu**: Generate all levels, explain each section
- **Ha**: Targeted updates for changed modules only
- **Ri**: Incremental regeneration, preserve human-written sections

## Context

**When to use:** After discover-scan + discover-validate pipeline completes, or when architecture changes significantly.

**When to skip:** Minor code changes that don't affect module structure.

**Inputs:** `work/discovery/components-validated.json`, source tree, governance docs (`guardrails.md`, `vision.md`, optionally `constitution.md`).

## Steps

### Step 1: Analyze Module Structure

Check `work/discovery/context.yaml` for detected language, then for each module:

| Language | Module marker | Strategy |
|----------|--------------|----------|
| Python | `__init__.py` | Read docstring, scan `from pkg.X import` |
| C# | `.csproj` + namespaces | Group by top-level layer directory |
| PHP | `composer.json` PSR-4 | Group by namespace segment |

Per module: count components, build dependency map, identify entry points, list public API.

<verification>
All modules identified with dependency data.
</verification>

### Step 2: Generate Module Docs

Write `governance/architecture/modules/{name}.md` per module:

**YAML frontmatter:** type, name, purpose, status, depends_on, depended_by, components.

**Body sections:** Purpose (2-3 sentences), Architecture, Key Files, Dependencies table, Conventions.

Write genuine explanatory prose — a new contributor should understand the module's role.

<verification>
All modules have docs with valid YAML frontmatter.
</verification>

### Step 3: Generate System Docs & Index

**System Context** (`system-context.md`): From `governance/vision.md` — what, who, why, external systems, non-goals.

**System Design** (`system-design.md`): From `governance/guardrails.md` + module deps — layers, data flows, constraints, drift detection.

**Domain Model** (`domain-model.md`): From module deps + component catalog — bounded contexts, context map, design decision guidance.

**Index** (`index.md`): System overview, module map table, data flow diagram, key constraints. Target: <2K tokens.

<verification>
All 4 system-level docs exist. Index under 2K tokens.
</verification>

### Step 4: Validate & Rebuild Graph

- All modules documented, frontmatter parses cleanly
- Dependency map matches actual imports
- Guardrails/constitution references are current

```bash
rai graph build
rai graph query "module dependencies"
```

<verification>
Module nodes appear in graph. No stale references.
</verification>

## Output

| Item | Destination |
|------|-------------|
| Module docs | `governance/architecture/modules/*.md` |
| System context | `governance/architecture/system-context.md` |
| System design | `governance/architecture/system-design.md` |
| Domain model | `governance/architecture/domain-model.md` |
| Index | `governance/architecture/index.md` |

## Quality Checklist

- [ ] Module frontmatter includes all required fields (type, name, purpose, depends_on)
- [ ] Prose explains WHY, not just WHAT (new contributor test)
- [ ] Index under 2K tokens for session-loadable context
- [ ] On re-run, preserve human-edited sections (append, don't overwrite)
- [ ] NEVER generate placeholder docs for modules with no real code

## References

- Previous: `/rai-discover-validate`
- Graph builder: `src/raise_cli/context/builder.py` (`load_architecture()`)
- Components: `work/discovery/components-validated.json`
- Governance: `governance/guardrails.md`, `governance/vision.md`
