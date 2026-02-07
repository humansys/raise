# Project Vision: [Nombre del Proyecto]

> **Estado**: Draft | En Revisión | Aprobado
> **Fecha**: [YYYY-MM-DD]
> **Autor**: [Nombre]
> **Versión**: 1.0.0
> **PRD Referencia**: `governance/prd.md`

---

## 1. Problem Statement

### 1.1 Problema de Negocio (del PRD)

[Resumir el problema de negocio del PRD en 2-3 oraciones]

### 1.2 Perspectiva Técnica

[Conectar el problema de negocio con la capacidad técnica faltante]

**Dolor técnico subyacente:**
- [Qué limita actualmente la solución técnica]
- [Por qué no se ha resuelto antes]

---

## 2. Visión de Alto Nivel

### 2.1 Value Proposition

[1-2 párrafos describiendo el valor principal que entrega esta solución]

### 2.2 Diferenciadores Clave

- [Diferenciador 1]
- [Diferenciador 2]
- [Diferenciador 3]

### 2.3 Resultados Esperados

- [Resultado medible 1]
- [Resultado medible 2]
- [Resultado medible 3]

---

## 3. Alineamiento Estratégico

### 3.1 Mapeo Goals → Mecanismos

| Business Goal (PRD) | Mecanismo Técnico | Métrica de Éxito |
|---------------------|-------------------|------------------|
| [Goal 1] | [Cómo se logra técnicamente] | [Cómo se mide] |
| [Goal 2] | [Cómo se logra técnicamente] | [Cómo se mide] |
| [Goal 3] | [Cómo se logra técnicamente] | [Cómo se mide] |

### 3.2 Impacto por Stakeholder

| Stakeholder | Beneficio Esperado | Métrica |
|-------------|-------------------|---------|
| [Stakeholder 1] | [Beneficio concreto] | [Cómo se mide] |
| [Stakeholder 2] | [Beneficio concreto] | [Cómo se mide] |

---

## 4. Scope

### 4.1 Must Have (MVP)

> Máximo 3-5 items. Sin estos, el proyecto no tiene sentido.

- [ ] [Item 1 - capacidad esencial]
- [ ] [Item 2 - capacidad esencial]
- [ ] [Item 3 - capacidad esencial]

### 4.2 Should Have

> Importante pero el MVP funciona sin ellos.

- [ ] [Item 1]
- [ ] [Item 2]

### 4.3 Could Have (Nice-to-Have)

> Mejoras post-MVP.

- [ ] [Item 1]
- [ ] [Item 2]

### 4.4 Out of Scope

> Explícitamente excluido de este proyecto.

- ❌ [Exclusión 1]
- ❌ [Exclusión 2]

---

## 5. Métricas de Éxito

### 5.1 Métricas de Negocio (Lagging)

| Métrica | Baseline | Target | Timeframe |
|---------|----------|--------|-----------|
| [Ej: Revenue impact] | [Actual] | [Meta] | [Cuándo] |
| [Ej: Cost reduction] | [Actual] | [Meta] | [Cuándo] |

### 5.2 Métricas Técnicas (Leading)

| Métrica | Target | Cómo se Mide |
|---------|--------|--------------|
| Response time P95 | < [X]ms | APM/Monitoring |
| Error rate | < [X]% | Logs/Alerting |
| Throughput | > [X] req/s | Load testing |
| Availability | [X]% | Uptime monitoring |

---

## 6. Constraints y Assumptions

### 6.1 Constraints Técnicas

| Constraint | Fuente | Negociable |
|------------|--------|------------|
| [Ej: Debe usar stack existente] | [IT Policy] | No |
| [Ej: Budget de infra $X/mes] | [Sponsor] | Parcial |
| [Ej: Timeline Q3 launch] | [Negocio] | Parcial |

### 6.2 Constraints de Negocio

| Constraint | Fuente | Negociable |
|------------|--------|------------|
| [Ej: Compliance SOC2] | [Legal] | No |
| [Ej: Integración con ERP] | [Operaciones] | No |

### 6.3 Assumptions

> Supuestos que deben validarse durante la implementación.

1. [Assumption 1]
2. [Assumption 2]
3. [Assumption 3]

---

## 7. Componentes de Alto Nivel

### 7.1 Diagrama de Contexto

```
[Dibujar diagrama simple de 3-7 componentes]

┌─────────────────────────────────────────────────────┐
│                    Sistema                          │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐       │
│  │Component 1│──│Component 2│──│Component 3│       │
│  └───────────┘  └───────────┘  └───────────┘       │
└─────────────────────────────────────────────────────┘
        │                               │
        ▼                               ▼
   [Sistema A]                     [Sistema B]
```

### 7.2 Componentes Principales

| Componente | Responsabilidad | Tecnología Sugerida |
|------------|-----------------|---------------------|
| [Nombre] | [Qué hace] | [Tech] |
| [Nombre] | [Qué hace] | [Tech] |
| [Nombre] | [Qué hace] | [Tech] |

### 7.3 Integraciones Externas

| Sistema | Tipo | Datos | Criticidad |
|---------|------|-------|------------|
| [Nombre] | API/DB/Event | [Qué datos] | Core/Supporting |

---

## 8. Trade-offs Documentados

| Decisión | Alternativas | Elección | Razón |
|----------|--------------|----------|-------|
| [Qué decidir] | [A, B, C] | [B] | [Por qué B] |

---

## 9. Trazabilidad

| Fuente | Artefacto | Relación |
|--------|-----------|----------|
| PRD | `governance/prd.md` | Input principal |
| Solution Vision | `governance/vision.md` | Contexto de sistema |
| Tech Design | `governance/design.md` | Output (siguiente) |

---

## 10. Aprobaciones

| Rol | Nombre | Fecha | Status |
|-----|--------|-------|--------|
| Product Owner | [Nombre] | [Fecha] | Aprobado/Pendiente |
| Technical Lead | [Nombre] | [Fecha] | Aprobado/Pendiente |
| Architect | [Nombre] | [Fecha] | Aprobado/Pendiente |

---

## Historial de Cambios

| Versión | Fecha | Autor | Cambio |
|---------|-------|-------|--------|
| 1.0.0 | [Fecha] | [Autor] | Versión inicial |

---

*Generado por: `project/vision` kata*
*Template version: 1.0.0 (ADR-010)*
