# DEPRECATED - Use framework/ Instead

> **This directory is deprecated as of v2.5 (ADR-011)**

## New Location

The contents of this directory have moved to `framework/`:

| Old Path | New Path |
|----------|----------|
| `specs/raise/vision.md` | `framework/vision.md` |
| `specs/raise/adrs/` | `framework/decisions/` |
| `specs/raise/schemas/` | `framework/schemas/` |
| `specs/raise/README.md` | `framework/README.md` |

## Why

The Three-Directory Model (ADR-011) separates concerns:

- `framework/` - Governance OF the framework (what RaiSE IS)
- `governance/` - Governance FOR projects (what governs your solution)
- `work/` - Active work in progress

## Migration

See `docs/migration/v2.4-to-v2.5-migration.md` for full migration guide.

## Timeline

This directory will be removed in v3.0. Please update your references.

---

*Deprecated: 2026-01-30*
