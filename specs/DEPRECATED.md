# DEPRECATED - Use governance/ and work/ Instead

> **This directory structure is deprecated as of v2.5 (ADR-011)**

## New Locations

The Three-Directory Model reorganizes `specs/` into two directories:

| Old Path | New Path | Purpose |
|----------|----------|---------|
| `specs/main/*.md` | `governance/solution/` | Solution-level approved artifacts |
| `specs/main/*.md` | `governance/projects/{name}/` | Project-level approved artifacts |
| `specs/NNN-feature/` | `work/features/NNN-feature/` | Feature work in progress |
| `specs/raise/` | `framework/` | Framework specification |

## Specific Moves

### Solution-Level Artifacts
```
specs/main/business_case.md    → governance/solution/business_case.md
specs/main/solution_vision.md  → governance/solution/vision.md
```

### Project-Level Artifacts
```
specs/main/project_vision.md   → governance/projects/{name}/vision.md
specs/main/tech_design.md      → governance/projects/{name}/design.md
specs/main/project_backlog.md  → governance/projects/{name}/backlog.md
```

### Feature Work
```
specs/006-katas-normalization/ → work/features/006-katas-normalization/
specs/007-*/                   → work/features/007-*/
...
```

### Framework Specification
```
specs/raise/vision.md          → framework/vision.md
specs/raise/adrs/              → framework/decisions/
specs/raise/schemas/           → framework/schemas/
```

## Why

The Three-Directory Model separates concerns:

- `governance/` - Approved, authoritative artifacts (what governs)
- `work/` - Work in progress (what we're doing)
- `framework/` - Framework specification (what RaiSE IS)

## Migration

See `docs/migration/v2.4-to-v2.5-migration.md` for full migration guide.

## Timeline

This directory structure will be reorganized in v3.0. Please update your references and workflows.

---

*Deprecated: 2026-01-30*
