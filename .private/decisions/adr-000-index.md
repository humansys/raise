# Architecture Decision Records
## Índice de Decisiones Arquitectónicas

**Versión:** 2.1.0  
**Fecha:** 29 de Diciembre, 2025  
**Propósito:** Índice y template para ADRs del proyecto RaiSE.

> **Nota v2.1:** Estructura refactorizada a un archivo por ADR siguiendo el patrón estándar de Michael Nygard. ADR-009 añadido para ShuHaRi Hybrid.

---

## Índice de ADRs

| ID | Título | Estado | Fecha | Archivo |
|----|--------|--------|-------|---------|
| ADR-001 | Usar Python para CLI | ✅ Accepted | 2025-12-26 | [adr-001](./adr-001-python-cli.md) |
| ADR-002 | Git como API de distribución | ✅ Accepted | 2025-12-26 | [adr-002](./adr-002-git-distribution.md) |
| ADR-003 | MCP como protocolo de contexto | ✅ Accepted | 2025-12-26 | [adr-003](./adr-003-mcp-protocol.md) |
| ADR-004 | Markdown para humanos, JSON para máquinas | ✅ Accepted | 2025-12-26 | [adr-004](./adr-004-markdown-json.md) |
| ADR-005 | Local-first architecture | ✅ Accepted | 2025-12-26 | [adr-005](./adr-005-local-first.md) |
| ADR-006 | ~~DoD fractales por fase~~ | ⚠️ Superseded | 2025-12-26 | [adr-006](./adr-006-dod-fractales.md) |
| ADR-006a | Validation Gates por fase | ✅ Accepted | 2025-12-28 | [adr-006a](./adr-006a-validation-gates.md) |
| ADR-007 | Guardrails over Rules | ✅ Accepted | 2025-12-28 | [adr-007](./adr-007-guardrails.md) |
| ADR-008 | Observable Workflow local | ✅ Accepted | 2025-12-28 | [adr-008](./adr-008-observable-workflow.md) |
| ADR-009 | ShuHaRi Hybrid Implementation | ✅ Accepted | 2025-12-29 | [adr-009](./adr-009-shuhari-hybrid.md) |
| ADR-010 | Ontología de Comandos CLI | ✅ Accepted | 2025-12-29 | [adr-010](./adr-010-cli-ontology.md) |
| ADR-011 | Modelo Híbrido: Katas, Templates y Gates | ✅ Accepted | 2026-01-12 | [adr-011](./adr-011-hybrid-kata-template-gate.md) |

---

## Estados de ADR

| Estado | Significado |
|--------|-------------|
| 📝 Proposed | En discusión, no implementado |
| ✅ Accepted | Aprobado e implementado |
| ⚠️ Deprecated | Válido pero desaconsejado |
| ⚠️ Superseded | Reemplazado por otro ADR |

---

## Template ADR

Usar este template para nuevos ADRs. Guardar como `adr-XXX-titulo-kebab-case.md`.

```markdown
# ADR-XXX: [Título]

**Estado:** [Proposed | Accepted | Deprecated | Superseded by ADR-XXX]  
**Fecha:** YYYY-MM-DD  
**Autores:** [Nombres]

---

## Contexto

[Situación que requirió la decisión. ¿Qué problema resolvemos?]

## Decisión

[Lo que decidimos hacer. Ser específico y concreto.]

## Consecuencias

### Positivas
- [Beneficio 1]

### Negativas
- [Trade-off 1]

### Neutras
- [Implicación neutral]

## Alternativas Consideradas

1. **[Alternativa A]** - [Por qué no se eligió]
2. **[Alternativa B]** - [Por qué no se eligió]

## Referencias

- [Link a documento relacionado]
```

---

## Convenciones

1. **Naming:** `adr-XXX-titulo-en-kebab-case.md`
2. **Immutabilidad:** Los ADRs aceptados no se modifican; se crean nuevos que los superseden
3. **Superseding:** Usar sufijo `a`, `b`, etc. para versiones (ej: ADR-006a)
4. **Referencias:** Siempre linkear documentos afectados

---

## Changelog

### v2.1.0 (2025-12-29)
- **REFACTOR**: Un archivo por ADR (antes: monolito)
- **NUEVO**: ADR-009 ShuHaRi Hybrid Implementation

### v2.0.0 (2025-12-28)
- ADR-006a, ADR-007, ADR-008 añadidos
- Terminología v2.0 adoptada

### v1.0.0 (2025-12-27)
- Release inicial con ADR-001 a ADR-006

---

*Cada ADR es un archivo separado para facilitar versionado y referencias. Ver template arriba para crear nuevos ADRs.*
