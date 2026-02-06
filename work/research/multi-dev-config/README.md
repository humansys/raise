# Research: Multi-Developer Configuration Patterns

> **ID:** RES-MULTIDEV-001
> **Date:** 2026-02-05
> **Decision:** F14.15 Multi-Developer Architecture
> **Status:** Complete

## Question

How do AI coding assistants handle personal vs shared configuration in multi-developer repos?

## Executive Summary

**Finding:** The industry standard is a two-level hierarchy with automatic gitignoring of personal data:

1. **Personal data** → Home directory (`~/.<tool>/`) OR project subdirectory (gitignored)
2. **Shared data** → Project directory (`.<tool>/`) committed to git

**Key pattern:** Personal files are gitignored by default, not moved to a separate location.

**Recommendation:** Adopt the **Claude Code pattern** — keep personal data in `.raise/rai/personal/` (gitignored) rather than moving to `~/.rai/projects/{hash}/`. Simpler, proven, lower migration complexity.

## Tool Analysis

| Tool | Personal Location | Shared Location | Gitignore Pattern |
|------|-------------------|-----------------|-------------------|
| **Aider** | `~/.aider.conf.yml` | `.aider.conf.yml` | `.aider*` (auto) |
| **Continue** | `~/.continue/` | `.continuerc.json` | Manual |
| **Cursor** | (none explicit) | `.cursor/rules/` | `.cursorignore` |
| **Claude Code** | `.claude/settings.local.json` | `.claude/settings.json` | Auto-gitignored |
| **Copilot** | GitHub account (cloud) | `.github/copilot-instructions.md` | N/A |
| **Cody** | (enterprise config) | Context filters | Respects .gitignore |

## Key Patterns

### Pattern 1: Gitignore in Place (Claude Code, Aider)

```
.<tool>/
├── settings.json      # Committed (team)
└── settings.local.json # Gitignored (personal)
```

**Pros:** Simple, no migration, single location
**Cons:** Personal files still in project dir (hidden)

### Pattern 2: Home Directory Separation (Continue, Aider)

```
~/.<tool>/           # Personal (global)
./<tool>/            # Shared (project)
```

**Pros:** Clear separation, no gitignore needed
**Cons:** Requires project-hash for multi-project, more complex

### Pattern 3: Cloud-Based Personal (Copilot)

Personal settings stored in cloud service, project settings in repo.

**Pros:** No local personal files
**Cons:** Requires cloud service, not applicable to RaiSE

## Recommendation for RaiSE

### Revised Architecture

Instead of `~/.rai/projects/{hash}/`, adopt the simpler in-place gitignore pattern:

```
.raise/rai/
├── identity/           # SHARED (committed)
│   ├── core.md
│   └── perspective.md
├── memory/
│   ├── patterns.jsonl  # SHARED (curated project patterns)
│   └── index.json      # SHARED (memory index)
└── personal/           # PERSONAL (gitignored)
    ├── sessions/
    │   └── index.jsonl
    ├── telemetry/
    │   └── signals.jsonl
    ├── calibration.jsonl
    └── patterns.jsonl  # Personal learnings (future: promote)
```

### Gitignore Addition

```gitignore
# Personal Rai data (per-developer)
.raise/rai/personal/
```

### Why This is Better

| Aspect | Original Plan | Revised Plan |
|--------|---------------|--------------|
| Location | `~/.rai/projects/{hash}/` | `.raise/rai/personal/` |
| Migration | Complex (move + hash) | Simple (move within dir) |
| Discovery | Requires hash lookup | Obvious location |
| Precedent | Unique to RaiSE | Matches Claude Code |
| Multi-project | Hash collision risk | N/A (per-project) |
| Portability | Tied to machine | Can backup with project |

### Trade-offs

**Accepting:**
- Personal files exist in project directory (but gitignored)
- Developers must not accidentally commit `.raise/rai/personal/`

**Gaining:**
- Simpler implementation
- Industry-standard pattern
- No hash management
- Easier debugging (files are where you expect)

## References

- Evidence catalog: `sources/evidence-catalog.md`
- Claude Code docs: https://code.claude.com/docs/en/settings
- Aider config: https://aider.chat/docs/config/aider_conf.html
- Continue config: https://docs.continue.dev/customize/deep-dives/configuration
