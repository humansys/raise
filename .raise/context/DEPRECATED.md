# DEPRECATED - Use framework/reference/ Instead

> **This directory is deprecated as of v2.5 (ADR-011)**

## New Location

The contents of this directory have moved to `framework/reference/`:

| Old Path | New Path |
|----------|----------|
| `.raise/context/glossary.md` | `framework/reference/glossary.md` |
| `.raise/context/constitution.md` | `framework/reference/constitution.md` |
| `.raise/context/philosophy.md` | `framework/reference/philosophy.md` |
| `.raise/context/work-cycles.md` | `framework/reference/work-cycles.md` |
| `.raise/context/compliance.md` | `framework/reference/compliance.md` |

## Why

The Three-Directory Model (ADR-011) separates:

- `.raise/` - Framework engine (katas, gates, templates, skills)
- `framework/` - Framework textbook (PUBLIC - concepts, getting-started, reference)

Reference files are canonical documentation, not engine components, so they belong in `framework/reference/`.

## Migration

See `docs/migration/v2.4-to-v2.5-migration.md` for full migration guide.

## Timeline

This directory will be removed in v3.0. Please update your references.

---

*Deprecated: 2026-01-30*
