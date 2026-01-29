# RaiSE Archive

Archived artifacts from the RaiSE framework that have been superseded by the ADR-008 ontological simplification.

## Archived: 2025-01-29

### Why Archived

Per **ADR-008: Kata/Skill/Context Ontology Simplification**, the framework moved from:

- **7 command categories** → **4 Work Cycle katas**
- **4 kata levels** → **Flat kata structure by Work Cycle**

### Contents

| Directory | Description | Replaced By |
|-----------|-------------|-------------|
| `commands/` | spec-kit style commands | `.raise/katas/` (by Work Cycle) |
| `templates-legacy/` | Old templates (SAR, rules) | `.raise/templates/` (current) |

### Migration Reference

| Old Command | New Kata |
|-------------|----------|
| `commands/project/create-prd.md` | `katas/project/discovery.md` |
| `commands/project/create-vision.md` | `katas/project/vision.md` |
| `commands/project/create-architecture.md` | `katas/project/design.md` |
| `commands/project/create-backlog.md` | `katas/project/backlog.md` |
| `commands/feature/plan.md` | `katas/feature/plan.md` |
| `commands/feature/implement.md` | `katas/feature/implement.md` |
| `commands/context/*` | `.raise/skills/` (YAML contracts) |
| `commands/validate/*` | `.raise/skills/run-gate.yaml` |

### Note

These artifacts are preserved for reference only. Do not use them in new development.

---

See: `specs/raise/adrs/adr-008-kata-skill-context-simplification.md`
