# Katas RaiSE v2.1

Sistema de katas del framework RaiSE siguiendo el **Modelo Híbrido** (ADR-011).

## Modelo Híbrido

```
┌─────────────────────────────────────────────────────────────┐
│   TEMPLATE              KATA                VALIDATION GATE │
│   ─────────            ─────               ──────────────── │
│   ¿QUÉ produce?        ¿CÓMO hacerlo?      ¿ESTÁ BIEN?      │
└─────────────────────────────────────────────────────────────┘
```

- **Template**: Estructura del artefacto (en `src/templates/`)
- **Kata**: Proceso para crear el artefacto (aquí)
- **Validation Gate**: Checklist de verificación (en `src/gates/`)

## Estructura de Niveles

| Nivel | Pregunta Guía | Propósito |
|-------|---------------|-----------|
| **principios/** | ¿Por qué? ¿Cuándo? | Filosofía y meta-proceso |
| **flujo/** | ¿Cómo fluye? | Secuencias de valor por fase metodológica |
| **patron/** | ¿Qué forma? | Estructuras reutilizables |
| **tecnica/** | ¿Cómo hacer? | Instrucciones específicas (futuro) |

---

## Índice de Katas

### Principios (Meta-nivel)

| ID | Título | Propósito |
|----|--------|-----------|
| [principios-00](./principios/00-meta-kata.md) | Meta-Kata | Qué es una kata y cómo usarla |
| [principios-01](./principios/01-execution-protocol.md) | Protocolo de Ejecución | Los 7 pasos para ejecutar cualquier kata |

### Flujo (Por Fase Metodológica)

| ID | Fase | Título | Template | Gate |
|----|------|--------|----------|------|
| [flujo-01](./flujo/01-discovery.md) | 1 | Discovery | prd.md | gate-discovery |
| [flujo-02](./flujo/02-solution-vision.md) | 2 | Solution Vision | solution_vision.md | gate-vision |
| [flujo-03](./flujo/03-tech-design.md) | 3 | Tech Design | tech_design.md | gate-design |
| [flujo-04](./flujo/04-implementation-plan.md) | 5 | Implementation Plan | - | gate-plan |
| [flujo-05](./flujo/05-backlog-creation.md) | 4 | Backlog Creation | user_story.md | gate-backlog |
| [flujo-06](./flujo/06-development.md) | 6 | Development | - | gate-code |

### Patrón (Estructuras Reutilizables)

| ID | Título | Contexto |
|----|--------|----------|
| [patron-01](./patron/01-code-analysis.md) | Análisis de Código | Brownfield |
| [patron-02](./patron/02-ecosystem-discovery.md) | Descubrimiento de Ecosistema | Integraciones |
| [patron-03](./patron/03-tech-design-stack-aware.md) | Tech Design Stack-Aware | Brownfield |
| [patron-04](./patron/04-dependency-validation.md) | Validación de Dependencias | Nuevas libs |

### Técnica (Futuro)

*Pendiente: Katas de nivel técnico se crearán según demanda.*

---

## Cómo Empezar

1. **Leer** [`principios-00-meta-kata`](./principios/00-meta-kata.md) para entender qué son las katas
2. **Estudiar** [`principios-01-execution-protocol`](./principios/01-execution-protocol.md) para el protocolo de ejecución
3. **Identificar** la fase metodológica en la que te encuentras
4. **Seleccionar** la kata de flujo correspondiente
5. **Ejecutar** siguiendo el protocolo de 7 pasos

## Validation Gates

Los gates están en `src/gates/`:

| Gate | Fase | Verifica |
|------|------|----------|
| [gate-discovery](../gates/gate-discovery.md) | 1 | PRD completo y válido |
| [gate-vision](../gates/gate-vision.md) | 2 | Solution Vision alineada |
| [gate-design](../gates/gate-design.md) | 3 | Tech Design verificable |
| [gate-backlog](../gates/gate-backlog.md) | 4 | Backlog priorizado |
| [gate-plan](../gates/gate-plan.md) | 5 | Plan atómico y verificable |
| [gate-code](../gates/gate-code.md) | 6 | Código listo para merge |

---

## Referencias

- **ADR-011**: [`adr-011-hybrid-kata-template-gate.md`](../../../docs/framework/v2.1/adrs/adr-011-hybrid-kata-template-gate.md)
- **Kata Schema**: [`12-kata-schema-v2.1.md`](../../../docs/framework/v2.1/model/12-kata-schema-v2.1.md)
- **Metodología**: [`21-methodology-v2.md`](../../../docs/framework/v2.1/model/21-methodology-v2.md)
- **Glosario**: [`20-glossary-v2.1.md`](../../../docs/framework/v2.1/model/20-glossary-v2.1.md)
