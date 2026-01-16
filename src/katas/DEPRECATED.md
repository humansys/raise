# ⚠️ DEPRECATED - Katas Legacy

> **Este directorio contiene katas de versiones anteriores del framework RaiSE.**
>
> **Para la versión actual, usar:** [`src/katas-v2.1/`](../katas-v2.1/README.md)

---

## Estado de Deprecación

Las katas en este directorio están en proceso de deprecación como parte del feature `005-katas-ontology-audit`. Las razones incluyen:

1. **Modelo Híbrido (ADR-011)**: Se adoptó un nuevo modelo que separa Templates, Katas y Validation Gates
2. **Terminología Deprecated**: Usan términos como "DoD" (ahora: Validation Gate), "Developer" (ahora: Orquestador)
3. **Estructura Inconsistente**: No siguen el patrón Jidoka Inline estandarizado
4. **Niveles L0-L3**: Usan nomenclatura antigua en vez de principios/flujo/patrón/técnica

## Migración

| Kata Legacy | Nueva Ubicación |
|-------------|-----------------|
| `principios/00-raise-katas-documentation.md` | [`katas-v2.1/principios/00-meta-kata.md`](../katas-v2.1/principios/00-meta-kata.md) |
| `principios/01-raise-kata-execution-protocol.md` | [`katas-v2.1/principios/01-execution-protocol.md`](../katas-v2.1/principios/01-execution-protocol.md) |
| `flujo/04-generacion-plan-implementacion-hu.md` | [`katas-v2.1/flujo/04-implementation-plan.md`](../katas-v2.1/flujo/04-implementation-plan.md) |
| `flujo/06-implementacion-hu-asistida-por-ia.md` | [`katas-v2.1/flujo/06-development.md`](../katas-v2.1/flujo/06-development.md) |
| `patron/02-analisis-agnostico-codigo-fuente.md` | [`katas-v2.1/patron/01-code-analysis.md`](../katas-v2.1/patron/01-code-analysis.md) |
| `patron/03-ecosystem-discovery-agnostico.md` | [`katas-v2.1/patron/02-ecosystem-discovery.md`](../katas-v2.1/patron/02-ecosystem-discovery.md) |
| `patron/07-validacion-tecnica-dependencias.md` | [`katas-v2.1/patron/04-dependency-validation.md`](../katas-v2.1/patron/04-dependency-validation.md) |
| `flujo/01-tech-design-stack-aware.md` | [`katas-v2.1/patron/03-tech-design-stack-aware.md`](../katas-v2.1/patron/03-tech-design-stack-aware.md) |

## Katas No Migradas

Algunas katas legacy no tienen equivalente directo en v2.1 porque:
- Eran específicas de cursor rules (subdirectorio `cursor_rules/`)
- Se consolidaron en otras katas
- Se determinó que no eran necesarias en el modelo híbrido

## Timeline

- **Fase 1** (Completada): Crear estructura katas v2.1
- **Fase 2** (Completada): Documentar modelo híbrido (ADR-011)
- **Fase 3** (Actual): Deprecar katas legacy
- **Fase 4** (Pendiente): Eliminar directorio legacy (después de validación)

---

## Referencias

- **Nuevas Katas**: [`src/katas-v2.1/README.md`](../katas-v2.1/README.md)
- **ADR-011**: [`adr-011-hybrid-kata-template-gate.md`](../../docs/framework/v2.1/adrs/adr-011-hybrid-kata-template-gate.md)
- **Kata Schema v2.1**: [`12-kata-schema-v2.1.md`](../../docs/framework/v2.1/model/12-kata-schema-v2.1.md)
