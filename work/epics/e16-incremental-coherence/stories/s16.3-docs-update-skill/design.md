---
story_id: S16.3
title: Docs Update Skill
size: S
epic: E16
type: story_design
---

# S16.3: Docs Update Skill — Design

## What & Why

**Problem:** Architecture docs drift from code silently (PAT-196). The graph diff engine (S16.2) detects changes but nothing acts on them. Module doc frontmatter gets stale, narrative sections describe old responsibilities.

**Value:** `/docs-update` closes the coherence loop — graph changes automatically propagate to module docs with HITL review, eliminating the manual "check all module docs" step.

## Architectural Context

**Primary module:** `mod-skills_base` (new skill file)

**Layer:** Distributable asset (bc-distribution). No new CLI commands or source modules — the skill orchestrates existing CLI tools (`raise memory build`, `raise memory context`) and uses Claude's file editing capabilities directly.

**Key insight (PAT-172):** Skill-over-CLI for infrequent AI tasks. Frontmatter comparison is mechanical but runs rarely (per-story). A skill reading graph JSON directly beats building a CLI command that would add code surface for minimal benefit.

## Approach

### What We're Building

One thing: **`/docs-update` skill** (SKILL.md in `.claude/skills/docs-update/`)

The skill orchestrates the full coherence flow using existing infrastructure:

1. Run `raise memory build` → fresh graph + diff
2. For each affected module (from diff, or all modules if no diff):
   - Run `raise memory context mod-X --format json` → graph truth
   - Read `governance/architecture/modules/X.md` → current frontmatter
   - Compare machine-owned fields (`depends_on`, `depended_by`, `components`, `public_api`) against graph data
   - Update frontmatter fields directly via file editing
3. If diff shows structural changes (new modules, moved components), propose narrative section updates
4. HITL review before any changes are written

No new Python code. No new CLI command. The skill uses existing `raise memory` commands for data and Claude's editing tools for updates.

### Components Affected

| Component | Change | What |
|-----------|--------|------|
| `.claude/skills/docs-update/SKILL.md` | Create | Skill definition |

### Data Flow

```
raise memory build
        ↓
   index.json (graph) + last-diff.json
        ↓
raise memory context mod-X --format json  (per module)
        ↓
   Graph truth: code_imports, code_exports, code_components,
                depends_on edges, depended_by (reverse)
        ↓
Read governance/architecture/modules/X.md
        ↓
   Current frontmatter: depends_on, depended_by, components, public_api
        ↓
Compare → show diffs → HITL → apply via Edit tool
```

### Frontmatter Field Sources

```python
# Machine-owned fields (skill compares and updates):
{
    "depends_on": [...],    # from code_imports in graph metadata
    "depended_by": [...],   # from reverse depends_on edges in graph
    "components": N,        # from code_components in graph metadata
    "public_api": [...],    # from code_exports in graph metadata
}

# Human-owned fields (skill never touches):
# - purpose, constraints, status
```

## Examples

### Skill Invocation

```
User: /docs-update

Rai:
1. Building fresh graph... done (345 nodes)
2. Diff: 12 nodes changed, 3 modules affected (mod-memory, mod-context, mod-cli)
3. Comparing graph vs docs...

   mod-memory:
     depends_on: [config] → [config, schemas]
     components: 25 → 30

   mod-context:
     public_api: +GraphDiff, +diff_graphs
     components: 20 → 25

   mod-cli: no frontmatter changes

4. Apply frontmatter updates? [y/n]
   → Applied.
5. Structural changes detected — reviewing narrative for mod-context...
   [shows proposed narrative changes]
6. Apply narrative changes? [y/n]
```

## Acceptance Criteria

**MUST:**
- `/docs-update` skill builds graph, compares against module doc frontmatter
- Updates `depends_on`, `depended_by`, `components`, `public_api` from graph data
- HITL gate before writing any changes (frontmatter or narrative)
- Works standalone and as subagent from lifecycle skills

**SHOULD:**
- Use diff (last-diff.json) to scope to affected modules when available
- Fall back to all modules when no diff exists
- Show clear before/after for each field change

**MUST NOT:**
- Overwrite human-owned fields (`constraints`, `status`, `purpose`)
- Apply changes without HITL review
- Require new Python source code or CLI commands
