# DEPRECATED - Use framework/context/ Instead

> **This directory is deprecated as of v2.5 (ADR-011)**

## New Location

The contents of this directory have moved to `framework/context/`:

| Old Path | New Path |
|----------|----------|
| `.raise/context/glossary.md` | `framework/context/glossary.md` |
| `.raise/context/constitution.md` | `framework/context/constitution.md` |
| `.raise/context/philosophy.md` | `framework/context/philosophy.md` |
| `.raise/context/work-cycles.md` | `framework/context/work-cycles.md` |
| `.raise/context/compliance.md` | `framework/context/compliance.md` |

## Why

The Three-Directory Model (ADR-011) separates:

- `.raise/` - Framework engine (katas, gates, templates, skills)
- `framework/` - Framework governance (vision, context, decisions)

Context files are governance artifacts, not engine components, so they belong in `framework/`.

## Migration

See `docs/migration/v2.4-to-v2.5-migration.md` for full migration guide.

## Timeline

This directory will be removed in v3.0. Please update your references.

---

*Deprecated: 2026-01-30*
