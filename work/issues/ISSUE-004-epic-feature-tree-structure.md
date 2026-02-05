# ISSUE-004: Epic/Feature Tree Structure

> **Status:** Open
> **Priority:** Medium (DX improvement, not blocking)
> **Created:** 2026-02-05
> **Related:** ISSUE-003 (directory ontology)

---

## Problem Statement

Epics and features are stored in flat structures with inconsistent naming. This makes navigation difficult and obscures the epic→feature containment relationship.

**Current pain:**
- Finding all artifacts for an epic requires searching
- Feature naming is inconsistent (uppercase, lowercase, with/without names)
- No clear visual hierarchy in file explorer
- Some features have both directory AND file with same name

---

## Current Structure (Problematic)

### Epics: Flat in `dev/`

```
dev/
├── epic-e1-scope.md
├── epic-e2-scope.md
├── epic-e2-retrospective.md
├── epic-e3-scope.md
├── epic-e3-retrospective.md
├── epic-e7-scope.md
├── epic-e7-scope-v2.md          # Why v2 as separate file?
├── epic-e7-retrospective.md
├── epic-e8-scope.md
├── epic-e9-scope.md
├── epic-e10-scope.md
├── epic-e11-scope.md
├── epic-e12-scope.md
├── epic-e13-scope.md
├── epic-e14-scope.md
├── architecture-overview.md     # Mixed with non-epic files
├── components.md
├── parking-lot.md
└── ... (30+ other files)
```

**Problems:**
- Epic files mixed with unrelated files
- Scope and retrospective are separate files
- No grouping of epic artifacts
- Hard to see "what belongs to E7?"

### Features: Flat in `work/features/`

```
work/features/
├── 006-katas-normalization      # Old numeric prefix
├── 007-public-repo-readiness
├── F11.1                        # Uppercase, no name
├── f11.2-graph-builder          # Lowercase, with name
├── f12-2                        # Missing dot
├── F12.3                        # Uppercase again
├── f13.3
├── f13.5
├── f1.3-configuration
├── f2.1-concept-extraction
├── f3.1-identity-core-structure
├── f7-1-raise-init              # Directory
├── f7-1-raise-init.md           # AND file!
└── ... (30 items)
```

**Problems:**
- No grouping by epic
- Inconsistent naming conventions
- Can't tell which features belong to which epic without reading content
- Directory AND file with same name (f7-1-raise-init)

---

## Proposed Structure (Tree)

```
work/
└── epics/
    ├── e01-foundation/
    │   ├── scope.md
    │   ├── retrospective.md
    │   └── features/
    │       ├── f01.1-cli-structure/
    │       │   ├── spec.md
    │       │   └── plan.md
    │       ├── f01.2-config/
    │       └── ...
    │
    ├── e02-governance/
    │   ├── scope.md
    │   ├── retrospective.md
    │   └── features/
    │       ├── f02.1-concept-extraction/
    │       ├── f02.2-graph-builder/
    │       └── f02.3-mvc-query/
    │
    ├── e07-onboarding/
    │   ├── scope.md
    │   ├── retrospective.md
    │   └── features/
    │       ├── f07.1-raise-init/
    │       ├── f07.2-convention-detection/
    │       └── ...
    │
    └── e14-rai-distribution/
        ├── scope.md
        ├── plan.md              # If separate from scope
        ├── retrospective.md     # Created at epic-close
        └── features/
            ├── f14.1-base-identity/
            ├── f14.2-base-patterns/
            └── ...
```

### Naming Convention

| Element | Pattern | Example |
|---------|---------|---------|
| Epic directory | `e{NN}-{short-name}/` | `e14-rai-distribution/` |
| Feature directory | `f{NN}.{M}-{short-name}/` | `f14.1-base-identity/` |
| Scope file | `scope.md` | (always same name) |
| Retrospective | `retrospective.md` | (always same name) |
| Feature spec | `spec.md` | (if design exists) |
| Feature plan | `plan.md` | (if separate from spec) |

**Zero-padded numbers** (`e01` not `e1`) for proper sorting in file explorers.

---

## Benefits

| Benefit | How |
|---------|-----|
| **Clear containment** | Features visually nested under epics |
| **Easy navigation** | Expand epic folder → see all artifacts |
| **Consistent naming** | Convention enforced by structure |
| **Better git history** | Epic changes grouped in one directory |
| **Simpler cleanup** | Delete epic = delete directory |
| **Discoverable** | New contributor can browse structure |

---

## Migration Approach

### Option A: Migrate Now (Before F&F)
- Disruptive but clean slate for F&F users
- Skills reference paths need updating
- CLAUDE.local.md references need updating

### Option B: Migrate Post-F&F
- Less disruption during crunch
- New epics (E14+) use new structure
- Old epics remain flat (technical debt)

### Option C: New Structure for New Epics Only
- E14+ uses tree structure
- Old epics stay where they are
- Gradual transition

**Recommendation:** Option C — start E14 in new structure, migrate old epics later.

---

## Impact on Skills

Skills that reference epic/feature paths:

| Skill | Current Reference | Needs Update |
|-------|-------------------|--------------|
| `/epic-start` | Creates branch only | No |
| `/epic-design` | `dev/epic-{id}-scope.md` | Yes |
| `/epic-plan` | Appends to scope.md | Yes |
| `/epic-close` | `dev/epic-{id}-retrospective.md` | Yes |
| `/feature-start` | `work/features/` | Yes |
| `/feature-design` | `work/features/{id}/` | Yes |
| CLAUDE.local.md | Manual references | Yes |

---

## Questions

1. **Zero-pad epic numbers?** `e01` vs `e1`
   - Pro: Sorts correctly (e01, e02... e10, e11)
   - Con: More typing

2. **Where do completed epics go?**
   - Option A: Stay in `work/epics/` (simpler)
   - Option B: Move to `docs/epics/` after close (cleaner work/)
   - Recommendation: Stay in place, status is in scope.md

3. **What about research, proposals?**
   - Keep `work/research/` separate (not tied to epics)
   - Or nest under epic? `e14/research/`
   - Recommendation: Keep separate — research often spans epics

4. **Should closed features have all artifacts?**
   - spec.md, plan.md — keep for history
   - Working files — clean up at feature-close
   - Recommendation: Keep spec/plan, clean temp files

---

## Related

- ISSUE-003: Directory Structure Ontology
- E14: Would be first epic in new structure

---

*Created: 2026-02-05*
*Author: Rai + Emilio*
