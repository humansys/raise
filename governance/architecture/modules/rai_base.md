---
type: module
name: rai_base
purpose: "Base identity, patterns, and framework content that ships with raise-cli and gets copied on 'raise init'"
status: current
depends_on: []
depended_by: [onboarding]
entry_points: []
public_api:
  - "__version__"
components: 16
constraints:
  - "No internal dependencies — distribution package"
  - "Content is copied, not imported at runtime"
  - "Changes here affect all new projects on next raise init"
---

## Purpose

The rai_base module is a **distribution package** — it contains the base Rai identity files, starter patterns, and framework reference content that gets copied into a project's `.raise/` directory when you run `raise init`. It's not imported at runtime by other modules; it's read as data files by the onboarding module during initialization.

This is how new projects get Rai's core identity (`identity/core.md`, `identity/perspective.md`), base patterns (`memory/patterns.jsonl`), and framework reference material — without those files living in the project repo until initialization.

## Key Files

- **`identity/`** — `core.md` and `perspective.md` — Rai's identity and voice definition
- **`memory/`** — `patterns.jsonl` — Base patterns that every project starts with (TDD discipline, commit practices, etc.)
- **`framework/`** — Reference material copied to `.raise/`

## Dependencies

None — this is a data-only package. Content is accessed via `importlib.resources`.

## Conventions

- Content files use `importlib.resources.abc.Traversable` for access (not `importlib.abc.Traversable` — PAT-155)
- Version tracked in `__init__.py` as `__version__`
- Base patterns have `"base": true, "version": 1` fields to distinguish from user patterns
