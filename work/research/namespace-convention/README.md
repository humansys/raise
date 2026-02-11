# RES-NAMESPACE-001: Skill Namespace Convention

**Research ID:** RES-NAMESPACE-001
**Date:** 2026-02-11
**Decision Informs:** S-NAMESPACE story (pre-publish skill rename)
**Depth:** Standard (4h)
**Status:** Complete

## Navigation

- [Full Report](./namespace-report.md)
- [Evidence Catalog](./sources/evidence-catalog.md)

## 5-Minute Summary

### Question

What naming convention should RaiSE use to namespace distributed skills so they don't collide with user-created or third-party skills?

### Answer

**Use dash-prefix: `rai-session-start`, `rai-story-implement`, etc.**

The only valid separator in the Agent Skills specification is the hyphen. Dots, colons, underscores, and double underscores are all prohibited in skill names. Since the spec requires `name` to match the directory name, and names only allow `[a-z0-9-]`, the dash-prefix is the only compliant namespace pattern.

### Key Constraint

The Agent Skills specification (agentskills.io) — the emerging standard backed by 25+ tools — restricts skill names to:
- `a-z`, `0-9`, `-` only
- Max 64 characters
- No leading/trailing/consecutive hyphens
- Name must match directory name

This single constraint eliminates all alternatives.

### Trade-offs

| Factor | Assessment |
|--------|-----------|
| **DX friction** | `/session-start` → `/rai-session-start` (4 chars longer to type) |
| **Namespace clarity** | Dash does double duty (word separator + namespace separator) — visually ambiguous |
| **Spec compliance** | Full compliance with Agent Skills spec |
| **Future-proofing** | If native namespacing arrives, prefix convention adapts easily |
| **Collision prevention** | Effective — `rai-` prefix is distinctive enough |

### Blast Radius

~60 files, ~300-400 lines changed. Mechanical rename across:
- 20 skill directories × 2 locations (skills_base + .claude/skills)
- DISTRIBUTABLE_SKILLS list
- 2 methodology.yaml files
- 14 skills with cross-references
- 5 test files
