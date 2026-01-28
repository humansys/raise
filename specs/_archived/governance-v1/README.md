# ARCHIVED - Governance v1.x

> **⚠️ Este directorio está archivado.**
>
> La documentación de RaiSE ha sido migrada a **RaiSE Framework v2.0**.

## Nueva Ubicación

```
/specs/raise/          ← NUEVA UBICACIÓN
```

**Ver**: [`/specs/raise/README.md`](../../raise/README.md)

## Cambios en v2.0

| Aspecto | v1.x (este directorio) | v2.0 (nueva ubicación) |
|---------|------------------------|------------------------|
| Scope | Solo SAR + CTX | Framework completo (3 capas) |
| Estructura | Archivos flat | Organizado por componentes |
| Commands | No documentados | 5 categorías estandarizadas |
| Specification | Templates verbosos | Lean Spec (MVS) |
| Nombre | "Governance" | "RaiSE Framework" |

## Mapeo de Archivos

| Archivo v1.x | Nueva ubicación v2.0 |
|--------------|---------------------|
| solution-vision.md | `/specs/raise/vision.md` |
| solution-vision-sar.md | `/specs/raise/sar/vision.md` |
| solution-vision-context.md | `/specs/raise/ctx/vision.md` |
| architecture-overview.md | `/specs/raise/architecture.md` |
| tech-design.md | `/specs/raise/design.md` |
| solution-roadmap.md | `/specs/raise/roadmap.md` |
| adrs/* | `/specs/raise/adrs/*` |

## Por Qué v2.0

RaiSE v2.0 representa un major refactor que incluye:

1. **Arquitectura de 3 Capas**: Data Store → Components → Commands
2. **Lean Specification**: MVS, MVC, Progressive Discovery
3. **5 Categorías de Comandos**: setup, context, project, feature, tools
4. **Spec-Kit Harness**: Katas + Gates + Templates con Jidoka inline

---

*Archivado: 2026-01-28*
*Superseded by: RaiSE Framework v2.0*
