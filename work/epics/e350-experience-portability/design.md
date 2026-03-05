---
epic_id: "E350"
tracker: "RAISE-364"
adr: "ADR-044"
---

# E350: Rai Experience Portability — Design

## Gemba: Current State

### What Constitutes the Rai Experience
(Full inventory in research agent output, summarized here)

Three layers of context, six categories:

| Category | Files | Layer | Current Distribution |
|----------|-------|-------|---------------------|
| Identity | `core.md`, `perspective.md` | Universal | Git ✓ |
| Methodology | `methodology.yaml` | Universal | Git ✓ |
| Skills | 34 in `skills_base/` → `.claude/skills/` | Universal | Git ✓ (dpkg sync) |
| Patterns | `patterns.jsonl` (727) | Project | Git ✓ (merge pain) |
| Memory | `MEMORY.md`, `index.json` | Derived | MEMORY.md stale ✗ |
| CLAUDE.md | Project instructions | Derived | Generated once, drifts ✗ |
| Personal | sessions, calibration | Personal | .gitignore ✓ |
| Integrations | `jira.yaml`, creds mixed | Project | Creds leak risk ✗ |

### Session Load Flow
```
1. Claude Code loads: settings.json, CLAUDE.md
2. /rai-session-start loads: MEMORY.md, methodology, identity, patterns
3. Skills loaded on demand: .claude/skills/rai-*/SKILL.md
4. CLI commands use: jira.yaml, graph index, manifest
```

## Target Architecture (ADR-044)

### Context Lifecycle
```
rai init (idempotent)
  ├→ Detects first-time vs existing
  ├→ Projects skills (dpkg three-hash)
  ├→ Generates CLAUDE.md from .raise/ sources
  ├→ Loads base patterns to project if first-time
  ├→ Sanitizes .gitignore
  └→ Shows diff preview for conflicts

rai graph build
  ├→ Builds knowledge graph (existing)
  ├→ Regenerates index.json (existing)
  └→ [NEW] Hook: regenerates MEMORY.md

rai pattern add "content"
  └→ [CHANGE] Writes to personal/patterns.jsonl (not shared)

rai pattern promote PAT-123
  └→ [NEW] Moves from personal → project patterns.jsonl
```

### Three-Level Pattern Model
```
src/rai_cli/patterns_base/base.jsonl     ← ~50 first-principles
  ↓ (loaded at session start)
.raise/rai/memory/patterns.jsonl         ← curated project patterns
  ↓ (loaded at session start)
.raise/rai/personal/patterns.jsonl       ← per-dev accumulation
  ↓ (loaded at session start)
[merged in memory for session context]
```

### CLAUDE.md Generation
```
Sources:
  .raise/rai/identity/core.md        → ## Rai Identity section
  .raise/rai/framework/methodology.yaml → ## Process Rules section
  .raise/manifest.yaml               → ## Branch Model, CLI Reference
  .raise/jira.yaml                   → ## External Integrations

Output:
  CLAUDE.md (generated, git-tracked, never hand-edited)

Customization:
  CLAUDE.local.md (per-developer overrides, git-ignored)
```

## Key Contracts

### Hook: MemoryMdRegeneration
```python
# Listens to: GraphBuildEvent
# Calls: generate_memory_md() (already exists in onboarding/memory_md.py)
# Writes to: .raise/rai/memory/MEMORY.md
# Also updates: Claude Code instance copy (if detectable)
```

### Command: rai pattern promote
```python
# Reads: .raise/rai/personal/patterns.jsonl
# Filters: by pattern ID or interactive selection
# Appends to: .raise/rai/memory/patterns.jsonl
# Removes from: personal copy
# Output: "Promoted PAT-123 to project patterns"
```

### Enhanced rai init
```python
# Detects: first-time (no .raise/) vs existing (.raise/ present)
# First-time: full scaffold (existing behavior + base patterns + CLAUDE.md gen)
# Existing: skill sync + CLAUDE.md regen + .gitignore check + base patterns update
# Conflict resolution: dpkg three-hash for skills, diff preview for CLAUDE.md
```

## Components Changed

| Component | Change | Risk |
|-----------|--------|------|
| `src/rai_cli/hooks/builtin/` | New: memory_md_sync hook | Low |
| `src/rai_cli/onboarding/memory_md.py` | Extend: include all pattern levels | Low |
| `src/rai_cli/cli/commands/init.py` | Extend: CLAUDE.md regen, idempotent mode | Medium |
| `src/rai_cli/cli/commands/pattern.py` | New: `promote` subcommand | Low |
| `src/rai_cli/memory/patterns.py` | Change: `add` writes to personal/ | Low |
| `src/rai_cli/patterns_base/` | New: base.jsonl with ~50 patterns | Low |
| `.gitignore` | Update: add .claude/projects/, clean archive | Low |
| `CLAUDE.md` | Rewrite: generated from .raise/ sources | Medium |
