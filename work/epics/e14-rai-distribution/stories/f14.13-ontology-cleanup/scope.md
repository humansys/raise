# F14.13: Framework Ontology Cleanup

> Pre-distribution cleanup of terminology inconsistencies + CLI/Skill restructure.

## Context

Before distributing Rai to F&F users, we need consistent terminology and coherent ontology across CLI and skills.

**Phase 1 (COMPLETE):** Archive historical artifacts, fix CLAUDE.md terminology.
**Phase 2 (NEW):** CLI command restructure based on ontology engineering analysis.

---

## Phase 1: Terminology Cleanup ✅ COMPLETE

### Done

- [x] CLAUDE.md terminology section matches glossary
- [x] CLAUDE.md architecture paths match actual code structure
- [x] No `graph build/query` references in active docs
- [x] Archive directory created with historical artifacts (88 files)
- [x] Active docs use consistent terminology

---

## Phase 2: CLI/Skill Ontology Restructure

### Problem Statement

Ontological analysis revealed violations of core principles:

| Principle | Violation |
|-----------|-----------|
| **Orthogonality** | Session scattered across profile, memory, telemetry |
| **Taxonomic Consistency** | `status` empty; sessions under `profile` is awkward |
| **Naming Conventions** | `session-end` vs skill `session-close` |
| **Minimal Commitment** | Empty commands, redundant emit-* |

### Target State (Option A: Domain-Centric)

```
raise
├── init                    # Setup (unchanged)
├── discover                # Codebase analysis (unchanged)
│   ├── scan
│   ├── build
│   └── drift
├── memory                  # All persistent data
│   ├── query
│   ├── build
│   ├── list
│   └── add <type>          # Unified: pattern, calibration, session
├── session                 # NEW: First-class workflow state
│   ├── start               # Move from profile
│   └── close               # Move from profile, rename from end
├── profile                 # Developer identity only
│   └── show                # Remove session-* commands
└── [REMOVE status]         # Empty, provides no value
└── [REMOVE telemetry]      # Merge emit-* into memory add
```

### Changes Required

#### CLI Changes

| Change | Type | Files |
|--------|------|-------|
| Create `rai session` command group | New | `cli/commands/session.py` |
| Move session-start/end from profile | Refactor | `cli/commands/profile.py` |
| Rename session-end → session-close | Rename | - |
| Remove `rai status` | Delete | `cli/commands/status.py` |
| Remove `rai telemetry` | Delete | `cli/commands/telemetry.py` |
| Merge telemetry emit into memory add | Refactor | `cli/commands/memory.py` |
| Unify memory add-* into single command | Refactor | `cli/commands/memory.py` |

#### Skill Updates

| Change | Type | Files |
|--------|------|-------|
| Update session-start to use new CLI | Update | `skills/session-start/SKILL.md` |
| Update session-close to use new CLI | Update | `skills/session-close/SKILL.md` |
| Move `scripts/` out of skills | Move | `skills/scripts/` → `dev/scripts/` |
| Update any skill referencing telemetry | Update | Multiple |

#### Test Updates

| Area | Estimated Tests |
|------|-----------------|
| New session commands | ~15 |
| Refactored memory add | ~10 |
| Remove status tests | -5 |
| Remove telemetry tests | -20 |
| Update integration tests | ~10 |

### Migration Path

1. **Add new commands** (session, unified memory add)
2. **Deprecate old commands** (profile session-*, telemetry emit-*)
3. **Update skills** to use new commands
4. **Remove deprecated** after verification
5. **Update documentation**

### Risks

| Risk | Mitigation |
|------|------------|
| Breaking existing workflows | Deprecation period with warnings |
| Skills depend on telemetry | Update skills before removal |
| Test coverage drop | Add new tests before removing old |

### Done Criteria (Phase 2)

- [x] `rai session start` and `rai session close` work
- [x] `rai memory emit-*` commands work (telemetry merged into memory)
- [x] `rai status` removed
- [x] `rai telemetry` removed (functionality in memory)
- [x] `profile` only has `show` command
- [x] All skills updated to new CLI
- [x] `scripts/` moved out of skills
- [x] Tests pass (905 passing)
- [x] Documentation updated

### Size

**M** — Significant refactoring, ~10-15 files, need fresh context.

### Dependencies

- Phase 1 complete ✅

---

## References

- Ontology analysis: `ontology-analysis.md` (same directory)
- ADR-012: Skills + Toolkit architecture
- Glossary: `framework/reference/glossary.md`
