# RaiSE v1/v2.1 Archive

Archived artifacts from the RaiSE framework that have been superseded by the v2.3 ontological simplification (ADR-008).

## Archived: 2026-01-29

### Why Archived

Per **ADR-008: Kata/Skill/Context Ontology Simplification**, the framework moved from:

- **7 command categories** → **4 Work Cycle katas**
- **4 kata levels** (principios/flujo/patrón/técnica) → **Work Cycle directories** (project/feature/setup/improve)
- **SAR/CTX components** → **setup/ and context/ concepts integrated into ontology**
- **docs/ sprawl** → **Consolidated .raise/context/**

### Contents

| Directory | Description | Replaced By |
|-----------|-------------|-------------|
| `commands/` | spec-kit style commands (23 files) | `.raise/katas/` (by Work Cycle) |
| `templates-legacy/` | Old templates (SAR, rules) | `.raise/templates/` |
| `katas-architecture/` | Old kata organization | `.raise/katas/project/design.md` |
| `docs/` | v2.1 documentation (89 files) | `.raise/context/` |

### docs/ Archive Detail

| docs/ Subdirectory | Status | Migrated To |
|--------------------|--------|-------------|
| `docs/core/glossary.md` | Migrated | `.raise/context/glossary.md` (v2.3) |
| `docs/core/constitution.md` | Migrated | `.raise/context/constitution.md` |
| `docs/reference/learning-philosophy.md` | Migrated | `.raise/context/philosophy.md` |
| `docs/reference/work-cycles.md` | Migrated | `.raise/context/work-cycles.md` |
| `docs/reference/security-compliance.md` | Migrated | `.raise/context/compliance.md` |
| `docs/gates/gate-discovery.md` | Merged | `.raise/gates/gate-discovery.md` (v2.0) |
| `docs/gates/gate-vision.md` | Merged | `.raise/gates/gate-vision.md` (v2.0) |
| `docs/gates/gate-code.md` | Copied | `.raise/gates/gate-code.md` |
| `docs/gates/gate-plan.md` | Copied | `.raise/gates/gate-plan.md` |
| `docs/corpus/` | Archived | Historical only |
| `docs/templates/sar/` | Deprecated | SAR terminology eliminated |
| `docs/katas/` | Deprecated | Old kata level organization |

### Command Migration Reference

| Old Command | New Kata |
|-------------|----------|
| `commands/project/create-prd.md` | `katas/project/discovery.md` |
| `commands/project/define-vision.md` | `katas/project/vision.md` |
| `commands/project/design-architecture.md` | `katas/project/design.md` |
| `commands/project/create-backlog.md` | `katas/project/backlog.md` |
| `commands/feature/plan-implementation.md` | `katas/feature/plan.md` |
| `commands/feature/implement.md` | `katas/feature/implement.md` |
| `commands/context/*` | `.raise/skills/*.yaml` |
| `commands/validate/*` | `.raise/skills/run-gate.yaml` |

### Deprecated Terminology

| Deprecated | v2.3 Replacement |
|------------|------------------|
| SAR, CTX | Eliminated (setup/, context/) |
| L0/L1/L2/L3 | Eliminated |
| principios/flujo/patrón/técnica | Work Cycles (project/feature/setup/improve) |
| Command | Kata or Skill |
| Kata Executor Harness | Kata Harness |

### Note

These artifacts are preserved for historical reference only. Do not use them in new development.

---

**See:** `specs/raise/adrs/adr-008-kata-skill-context-simplification.md`
**Audit:** `specs/main/research/outputs/corpus-audit-v2.3.md`
