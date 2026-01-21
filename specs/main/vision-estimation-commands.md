---
document_id: "VIS-RAISE-002"
title: "Comandos para Proceso de Estimación - Documento RaiSEVision"
project_name: "estimation-commands"
client: "RaiSE Framework"
version: "1.0"
date: "2026-01-20"
author: "Orquestador"
related_docs:
  - "PRD-RAISE-002"
  - "L1-04-Estimar-Requerimiento.md"
status: "Draft"
---

# Comandos para Proceso de Estimación - Documento RaiSEVision

## Contexto de Negocio

### Declaración del Problema
*(Fuente: PRD Sec 1.2)*

El framework RaiSE define un proceso de estimación completo en el kata L1-04 con 8 pasos, pero la infraestructura de comandos solo cubre 2 de ellos. Esto significa que:

- **¿Quién se ve afectado?** Arquitectos de Preventa, Líderes Técnicos y Analistas de Estimaciones
- **¿Cuál es el impacto?** Proceso manual, inconsistente y sin guía para los pasos 4-7 del flujo
- **¿Cuándo ocurre?** En cada ciclo de preventa o estimación de proyectos nuevos
- **¿Por qué es importante?** Sin comandos estandarizados, cada estimación es diferente y propensa a omisiones

**Capacidad técnica faltante:** 4 archivos de comandos (`.md`) que implementen la lógica de orquestación para Tech Design, Backlog, Estimation Roadmap y SoW.

### Visión de la Solución
*(Fuente: PRD Sec 1.1, 3.1)*

Completar el flujo de estimación con 4 comandos que siguen el patrón establecido por `raise.1.discovery` y `raise.2.vision`, permitiendo ejecutar el proceso completo de estimación de manera guiada y consistente.

- **Propuesta de valor central:** Flujo de estimación completo y automatizado desde PRD hasta SoW
- **Diferenciadores clave:** Cada comando sigue el kata correspondiente, usa templates existentes, e incluye handoffs para continuidad
- **Resultados objetivo:** Un paquete de estimación completo (6 artefactos) generado de manera consistente

## Alineación Estratégica

### Metas de Negocio → Mecanismos Técnicos
*(Fuente: PRD Sec 1.3)*

| Meta de Negocio | Mecanismo Técnico |
|-----------------|-------------------|
| **Meta 1:** Completar flujo kata L1-04 | 4 archivos `.md` en `.claude/commands/02-projects/` con estructura de comando |
| **Meta 2:** Estandarizar generación de artefactos | Cada comando usa un template específico de `src/templates/` y produce output en `specs/main/` |
| **Meta 3:** Mantener trazabilidad | Frontmatter YAML con `handoffs` que conecta al siguiente comando |

### Impacto en el Usuario
*(Fuente: PRD Sec 2.2)*

| Stakeholder | Puntos de Dolor Actuales | Beneficios Esperados |
|-------------|--------------------------|----------------------|
| Arquitecto de Preventa | Proceso manual sin guía estructurada | Ejecutar `/raise.4.tech-design` y obtener Tech Design completo en minutos |
| Líder Técnico | Crear backlog desde cero cada vez | Ejecutar `/raise.5.backlog` con Tech Design como input y obtener backlog estructurado |
| Analista de Estimaciones | Estimar sin plantilla consistente | Ejecutar `/raise.6.estimation` y `/raise.7.sow` para cerrar el ciclo de estimación |

## Alcance del MVP

### Imprescindible (Must Have)
*(Fuente: PRD Sec 3.1)*

1. **`raise.4.tech-design`** - Comando que genera Tech Design desde Solution Vision
2. **`raise.5.backlog`** - Comando que genera Backlog desde Tech Design
3. **`raise.6.estimation`** - Comando que genera Estimation Roadmap desde Backlog
4. **`raise.7.sow`** - Comando que genera Statement of Work desde Estimation Roadmap

### Deseable (Futuro / Nice to Have)
- Comando de consolidación (`raise.estimate-all`) que ejecute todo el flujo
- Validación automática de consistencia entre artefactos
- Exportación a PDF/DOCX

### Fuera del Alcance
- Modificación de templates existentes
- Modificación de comandos existentes
- Creación de gates de validación
- Integración con herramientas externas

## Métricas de Éxito

### Métricas Técnicas
| Métrica de Negocio | Métrica Técnica | Target |
|--------------------|-----------------|--------|
| Cobertura del kata | Comandos existentes / Pasos del kata | 6/6 (100%) |
| Uso de templates | Templates usados / Comandos creados | 4/4 (100%) |
| Consistencia de estructura | Comandos que siguen patrón / Total comandos | 4/4 (100%) |

### Método de Verificación
- Ejecutar cada comando y verificar que produce el artefacto esperado
- Validar que el frontmatter incluye handoff correcto
- Revisar que sigue la estructura de `raise.1.discovery`

## Restricciones y Supuestos

### Restricciones de Negocio
- Los comandos deben completarse para habilitar el flujo de estimación completo
- No se pueden modificar los templates existentes (están validados)

### Restricciones Técnicas
- Ubicación fija: `.claude/commands/02-projects/`
- Estructura: Debe seguir patrón de comandos existentes
- Templates: Solo usar los de `src/templates/`

### Supuestos
1. Los templates en `src/templates/` están completos y correctos
2. Los flujos en `src/katas-v2.1/flujo/` definen correctamente los pasos
3. La estructura de `raise.1.discovery` es el patrón canónico a seguir
4. El frontmatter YAML con `handoffs` es el mecanismo de conexión entre comandos

## Componentes de Alto Nivel

```
┌─────────────────────────────────────────────────────────────────┐
│                    FLUJO DE ESTIMACIÓN                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  [PRD] ──► [Vision] ──► [Tech Design] ──► [Backlog]            │
│    │          │              │               │                  │
│    ▼          ▼              ▼               ▼                  │
│  raise.1   raise.2       raise.4         raise.5               │
│  (existe)  (existe)      (CREAR)         (CREAR)               │
│                                                                 │
│                    [Estimation] ──► [SoW]                      │
│                         │            │                          │
│                         ▼            ▼                          │
│                     raise.6      raise.7                       │
│                     (CREAR)      (CREAR)                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Componentes a Crear (4)

| Componente | Tipo | Input | Output | Kata de Referencia |
|------------|------|-------|--------|-------------------|
| `raise.4.tech-design.md` | Comando | solution_vision.md | tech_design.md | flujo-03-tech-design |
| `raise.5.backlog.md` | Comando | tech_design.md | project_backlog.md | flujo-05-backlog-creation |
| `raise.6.estimation.md` | Comando | project_backlog.md | estimation_roadmap.md | (nuevo - basado en kata L1-04 paso 6) |
| `raise.7.sow.md` | Comando | estimation_roadmap.md | statement_of_work.md | (nuevo - basado en kata L1-04 paso 7) |

## Stakeholders

### Tomadores de Decisiones Clave
- **Mantenedor RaiSE:** Aprobación de la estructura y ubicación de comandos
- **Orquestador:** Validación de que los comandos cumplen el flujo del kata

### Equipo de Implementación
- **Agente Claude:** Creación de los 4 archivos de comando siguiendo el patrón establecido
