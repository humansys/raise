# Legacy Templates

Templates originales de RaiSE antes de la migración a **Lean Specification**.

Estos templates siguen el estilo verbose original (spec-kit style, ratio 3.7:1).

## Por qué están aquí

- Referencia histórica
- Algunos proyectos pueden aún usarlos
- Migración gradual a templates lean

## Migración

| Legacy Template | Replacement |
|-----------------|-------------|
| `solution-vision_es.md` | `../solution/solution-vision.md` |
| `project_requirements.md` | (PRD separado, fuera de hierarchy) |
| `plan-template.md` | (integrado en backlog workflow) |
| `spec-template.md` | (reemplazado por hierarchy) |
| `tasks-template.md` | (tasks viven en issue tracker) |
| `rules/*` | (cursor rules, sin cambio) |
| `sar/*` | (SAR output templates, sin cambio) |

## Recomendación

Para nuevos proyectos, usar templates en carpetas padre:

```
../solution/solution-vision.md
../architecture/architecture-overview.md
../architecture/adr.md
../tech/tech-design.md
../tech/tech-design-feature.md
../backlog/backlog.md
```

Ver `../README.md` para guía completa de la jerarquía.

---

*Archivado: 2026-01-28*
