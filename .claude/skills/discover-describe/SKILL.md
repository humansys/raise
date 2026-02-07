# Discover Describe

## Purpose

Generate architecture documentation from discovery data. Produces human-readable module docs with machine-parseable YAML frontmatter for graph integration.

## Mastery Levels (ShuHaRi)

**Shu**: Generate all modules, explain each section.
**Ha**: Generate with targeted updates for changed modules.
**Ri**: Incremental regeneration, preserve human sections.

## Context

**When to use:**
- After `raise discover scan` + `raise discover analyze` pipeline
- When architecture has changed significantly
- When onboarding new contributors

**When to skip:**
- Minor code changes that don't affect module structure
- Within same epic unless modules added/removed

**Inputs required:**
- `work/discovery/components-validated.json` — validated component catalog
- Source tree at `src/raise_cli/` — module structure and imports
- Module `__init__.py` docstrings — self-described purpose

**Output:**
- `governance/architecture/index.md` — compact index (<2K tokens)
- `governance/architecture/modules/*.md` — per-module docs with YAML frontmatter

## Steps

### Step 1: Load Discovery Data

Read `work/discovery/components-validated.json` and count components per module.

### Step 2: Analyze Module Structure

For each directory under `src/<package>/` with `__init__.py`:
1. Read `__init__.py` docstring for self-described purpose
2. Scan imports to build dependency map (`from <package>.X import`)
3. Count components from validated JSON
4. Identify entry points (CLI commands that import this module)
5. List key files and public API

### Step 3: Generate Module Docs

For each module, write `governance/architecture/modules/<name>.md` with:

**YAML frontmatter** (machine-parseable):
```yaml
---
type: module
name: <module_name>
purpose: "<one-line purpose>"
status: current
depends_on: [<list of module names>]
depended_by: [<list of module names>]
components: <count>
---
```

**Markdown body** (human-readable):
- **Purpose** — What this module does and why it exists (2-3 sentences)
- **Architecture** — How it works internally, key data flows
- **Key Files** — Important files with one-line descriptions
- **Dependencies** — Table of what it depends on and why
- **Conventions** — Module-specific patterns and rules

Write genuine explanatory prose. A new contributor should understand the module's role, constraints, and how to work with it.

### Step 4: Generate Compact Index

Write `governance/architecture/index.md` with:
- System overview (2-3 sentences)
- Module map table (name, purpose, depends_on, components)
- Data flow diagram (text-based)
- Key constraints

Target: under 2K tokens for session-loadable context.

### Step 5: Validate

- All modules documented
- YAML frontmatter parses cleanly
- Index under 2K tokens
- Dependency map is accurate (cross-check with imports)

### Step 6: Rebuild Graph

```bash
uv run raise memory build
```

Verify module nodes appear in graph:
```bash
uv run raise memory query "module dependencies"
```

## YAML Frontmatter Schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| type | string | Yes | Always "module" |
| name | string | Yes | Module name (directory name) |
| purpose | string | Yes | One-line purpose description |
| status | string | No | "current", "deprecated", or "planned" |
| depends_on | list[str] | Yes | Module names this depends on |
| depended_by | list[str] | No | Module names that depend on this |
| entry_points | list[str] | No | CLI commands using this module |
| public_api | list[str] | No | Key exported symbols |
| components | int | No | Component count from discovery |
| constraints | list[str] | No | Architectural constraints |

## Notes

- **No AI inference in CLI** — the CLI graph builder parses frontmatter deterministically
- **AI synthesizes prose** — this skill generates the human-readable sections
- **Preserve human edits** — on re-run, check for sections not in template and append them
- **Skip placeholders** — modules with no real code (engines, handlers) can be omitted

## References

- Graph builder: `src/raise_cli/context/builder.py` (`load_architecture()`)
- Components: `work/discovery/components-validated.json`
- Design: `work/stories/discover-document/design.md`
- Research: `work/research/architecture-knowledge-layer/`
