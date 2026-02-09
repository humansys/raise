---
story_id: S16.3
title: Docs Update Skill
size: M
epic: E16
type: story_design
---

# S16.3: Docs Update Skill — Design

## What & Why

**Problem:** Architecture docs drift from code silently (PAT-196). The graph diff engine (S16.2) detects changes but nothing acts on them. Module doc frontmatter gets stale, narrative sections describe old responsibilities.

**Value:** `/docs-update` closes the coherence loop — graph changes automatically propagate to module docs with HITL review, eliminating the manual "check all module docs" step.

## Architectural Context

**Primary modules:** `mod-skills_base` (new skill file), `mod-cli` (new command for deterministic frontmatter), `mod-context` (consumes graph + diff data)

**Layer:** The skill itself is a distributable asset (bc-distribution). The CLI command that supports it lives in the orchestration layer (cli module).

**ADR-025 two-layer principle:**
1. **Deterministic layer** — CLI command reads graph, computes correct frontmatter fields, writes them. No inference needed.
2. **Inference layer** — Skill reads diff + current doc, uses AI judgment to update narrative sections (Purpose, Architecture, Key Files, Conventions).

## Approach

### What We're Building

Two things:

1. **`raise docs update` CLI command** — deterministic frontmatter updater
   - Reads graph (index.json) and code analysis data
   - For each affected module: computes correct `depends_on`, `depended_by`, `components`, `public_api`, `entry_points` from graph
   - Writes updated frontmatter to module doc files
   - Pure deterministic — no inference, no HITL needed

2. **`/docs-update` skill** (SKILL.md in `.claude/skills/docs-update/`)
   - Step 1: Run `raise memory build` to get fresh graph + diff
   - Step 2: Run `raise docs update --dry-run` to see what frontmatter changes
   - Step 3: Run `raise docs update` to apply deterministic frontmatter
   - Step 4: If diff shows structural changes (new modules, moved components), use inference to update narrative sections of affected module docs
   - Step 5: HITL review before any narrative changes are saved

### Components Affected

| Component | Change | What |
|-----------|--------|------|
| `src/raise_cli/cli/commands/docs.py` | Create | New `raise docs update` command |
| `src/raise_cli/docs/updater.py` | Create | Deterministic frontmatter updater logic |
| `src/raise_cli/docs/__init__.py` | Create | Module init |
| `.claude/skills/docs-update/SKILL.md` | Create | Skill definition |
| `src/raise_cli/cli/main.py` | Modify | Register `docs_app` sub-app |

### Data Flow

```
raise memory build
        ↓
   index.json (graph) + last-diff.json
        ↓
raise docs update [--modules mod-X mod-Y] [--dry-run]
        ↓
   Reads graph → extracts module nodes with metadata
   Reads code analysis → imports, exports, component counts
   Reads current frontmatter → parses existing YAML
        ↓
   Computes diff per field (old frontmatter vs graph truth)
        ↓
   --dry-run: prints what would change
   default: writes updated frontmatter to module .md files
```

## Examples

### CLI Command — Dry Run

```bash
$ raise docs update --dry-run
Module: mod-memory
  depends_on: [config] → [config, schemas]  (added: schemas)
  components: 25 → 30  (changed)

Module: mod-context
  public_api: added GraphDiff, diff_graphs
  components: 20 → 25  (changed)

2 modules would be updated
```

### CLI Command — Apply

```bash
$ raise docs update
✓ mod-memory: updated depends_on, components
✓ mod-context: updated public_api, components
2 modules updated
```

### CLI Command — Specific Modules

```bash
$ raise docs update --modules mod-memory mod-context
✓ mod-memory: updated depends_on, components
✓ mod-context: updated public_api, components
```

### Skill Invocation

```
User: /docs-update

Rai:
1. Building fresh graph... done (345 nodes)
2. Diff: 12 nodes changed (5 added, 2 removed, 5 modified), 3 modules affected
3. Frontmatter updates (deterministic):
   - mod-memory: depends_on, components
   - mod-context: public_api, components
   Applied.
4. Structural changes detected — reviewing narrative for mod-context...
   [shows proposed narrative changes]
5. HITL: Apply narrative changes? [y/n]
```

### Frontmatter Field Sources

```python
# What the updater computes from graph data:
{
    "depends_on": ["config", "schemas"],        # from code_imports in graph metadata
    "depended_by": ["cli", "session"],          # from reverse dependency edges
    "components": 30,                           # from discovery component count
    "public_api": ["UnifiedGraph", "..."],      # from code_exports in graph metadata
    "entry_points": ["raise memory build"],     # from CLI command registration
}

# What it does NOT touch (human-owned):
# - purpose (hybrid — skill can suggest updates)
# - constraints (human domain knowledge)
# - status (human decision)
```

## Acceptance Criteria

**MUST:**
- `raise docs update` reads graph and updates module doc frontmatter deterministically
- `raise docs update --dry-run` shows changes without writing
- Updates `depends_on`, `depended_by`, `components`, `public_api` from graph data
- `/docs-update` skill orchestrates build → frontmatter update → narrative review
- HITL gate before any inference-based narrative changes

**SHOULD:**
- `--modules` flag to scope updates to specific modules
- Preserve YAML field ordering in frontmatter when rewriting
- Show clear diff output for both dry-run and apply modes

**MUST NOT:**
- Overwrite human-owned fields (`constraints`, `status`) deterministically
- Apply narrative changes without HITL review
- Require a diff to exist — should work from graph alone (diff enhances, doesn't gate)
