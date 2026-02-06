# Feature Scope: F14.12 Memory Ontology Simplification

> Rename "graph" to "memory" in CLI and file naming. Graph is implementation detail, memory is the user concept.

**Epic:** E14 Rai Distribution
**Size:** XS (renames only)
**Branch:** Working on `epic/e14/rai-distribution` (XS skip condition)

---

## In Scope

- CLI: `raise context query` → `raise memory query`
- CLI: `raise graph build` → `raise memory build`
- File: `.raise/graph/unified.json` → `.raise/rai/memory/index.json`
- Update all skill references to new commands
- Update tests

## Out of Scope

- Internal class names (UnifiedGraph stays — implementation detail)
- Schema changes (just file/command renames)
- New functionality

## Done Criteria

- [ ] `raise memory query "..."` works
- [ ] `raise memory build` works
- [ ] Old commands removed or aliased
- [ ] Skills reference new command names
- [ ] Tests pass
- [ ] Graph file moved to memory directory

---

*Created: 2026-02-05*
