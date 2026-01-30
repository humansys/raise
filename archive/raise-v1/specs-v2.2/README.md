# RaiSE Specs v2.2 Archive

**Archived:** 2026-01-29
**Reason:** Superseded by v2.3 ontological simplification (ADR-008)

## What Was Archived

| File | Version | Replaced By |
|------|---------|-------------|
| `vision.md` | v2.2.0 | `specs/raise/vision.md` (v2.3) |
| `architecture.md` | v2.1.0 | Consolidated into v2.3 vision |
| `design.md` | v2.0.0 | Consolidated into v2.3 vision |
| `roadmap.md` | v2.1.0 | To be created as v2.3 roadmap |
| `README.md` | v2.0 | `specs/raise/README.md` (v2.3) |
| `sar/vision.md` | v2.0.0 | setup/ katas in `.raise/katas/setup/` |
| `ctx/vision.md` | v2.1.0 | context/ skills in `.raise/skills/` |
| `commands/architecture.md` | v2.1 | Kata/Skill architecture in ADR-008 |
| `commands/standardization.md` | v2.1 | Migration complete via ADR-008 |
| `prompts/next-session-a1-schemas.md` | - | Session notes (historical) |

## Why Archived

Per **ADR-008: Kata/Skill/Context Ontology Simplification**, the framework moved from:

- **SAR/CTX Components** → setup/ katas + context/ skills
- **7 command categories** → Context/Kata/Skill ontology with Work Cycles
- **spec-kit harness** → Kata Harness (platform capability)
- **Regla** → Guardrail

## Deprecated Terminology in These Files

| Deprecated | v2.3 Replacement |
|------------|------------------|
| SAR (Software Architecture Reconstruction) | setup/ katas |
| CTX | context/ skills |
| Command | Kata or Skill |
| Regla | Guardrail |
| spec-kit harness | Kata Harness |
| 7 command categories | Work Cycles (project/feature/setup/improve) |

## What Was Preserved

- **ADRs** (`specs/raise/adrs/`) - Kept in place (immutable historical records)
- **JSON Schemas** (`specs/raise/schemas/`) - Still valid for rule/graph/MVC formats

## References

- **ADR-008**: `specs/raise/adrs/adr-008-kata-skill-context-simplification.md`
- **v2.3 Vision**: `specs/raise/vision.md`
- **Glossary v2.3**: `.raise/context/glossary.md`
