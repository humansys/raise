---
document_id: "[PRI]-[PROJECTCODE]-[SEQ]" # ej: PRI-XYZ-001
title: "{SOLUTION_NAME} - Matriz de Priorización de Funcionalidades"
project_name: "{SOLUTION_NAME}" # Asumiendo que SOLUTION_NAME es el nombre del proyecto
client: "[Nombre del Cliente]"
version: "[Número de Versión]"
date: "[YYYY-MM-DD]"
author: "[Nombres o Roles]"
related_docs:
  - "{RELATED_DOC_ID_1}" # ej: PRD-XYZ-001, VIS-XYZ-001
  - "{RELATED_DOC_ID_2}"
status: "[Borrador|En Revisión|Aprobado|Final]"
---

# {SOLUTION_NAME} - Matriz de Priorización de Funcionalidades

## Marco de Puntuación de Prioridad

### Métricas de Impacto (Escala 1-5)
- **Valor de Negocio**: Ingresos, ahorro de costos, alineación estratégica
- **Valor para el Usuario**: Satisfacción del usuario, ganancias de eficiencia, resolución de puntos de dolor
- **Base Técnica**: Capacidad de la plataforma, habilitación de escalabilidad
- **Reducción de Riesgo**: Seguridad, cumplimiento, reducción de deuda técnica

### Métricas de Esfuerzo (Escala 1-5)
- **Complejidad de Desarrollo**: Dificultad técnica, dependencias
- **Puntos de Integración**: Interacciones del sistema, flujos de datos
- **Requisitos de Pruebas**: Cobertura de pruebas, complejidad de validación
- **Impacto Operativo**: Despliegue, monitoreo, mantenimiento

## Matriz de Evaluación de Funcionalidades

| ID de Funcionalidad | Descripción | Valor de Negocio | Valor de Usuario | Base Técnica | Reducción de Riesgo | Impacto Total | Esfuerzo de Desarrollo | Dependencia Técnica (Ref: Tech Design) | Impacto Estimado (Ref: Estimation) | Puntuación de Prioridad |
| ------------------- | ----------- | ---------------- | ---------------- | ------------ | ------------------- | ------------- | ---------------------- | -------------------------------------- | ---------------------------------- | ----------------------- |
| {FID-001}           | {DESC}      | {1-5}            | {1-5}            | {1-5}        | {1-5}               | {SUM/4}       | {1-5}                  | {REF_TEC?}                             | {REF_EST?}                         | {Impacto/Esfuerzo}      |

## Conjunto de Funcionalidades MVP

### Fase 1 (Imprescindible / Must Have)
| ID de Funcionalidad | Descripción | Puntuación de Prioridad | Orden de Implementación | Dependencias |
| ------------------- | ----------- | ----------------------- | ----------------------- | ------------ |
| {FID-001}           | {DESC}      | {PUNTUACIÓN}            | {ORDEN}                 | {DEPS}       |

### Fase 2 (Deseable / Should Have)
| ID de Funcionalidad | Descripción | Puntuación de Prioridad | Justificación para Aplazamiento |
| ------------------- | ----------- | ----------------------- | ------------------------------- |
| {FID-002}           | {DESC}      | {PUNTUACIÓN}            | {RAZÓN}                         |

## Secuencia de Implementación

### Sprint 1
- {FEATURE_1}
  - Capacidades clave: {CAPACITIES}
  - Dependencias: {DEPENDENCIES}
  - Definición de Hecho (DoD): {DOD}

### Sprint 2
- {FEATURE_2}
  - Capacidades clave: {CAPACITIES}
  - Dependencias: {DEPENDENCIES}
  - Definición de Hecho (DoD): {DOD}

## Evaluación de Riesgos

### Riesgos Técnicos
| Riesgo   | Impacto  | Estrategia de Mitigación |
| -------- | -------- | ------------------------ |
| {RISK_1} | {IMPACT} | {STRATEGY}               |

### Riesgos de Negocio
| Riesgo   | Impacto  | Estrategia de Mitigación |
| -------- | -------- | ------------------------ |
| {RISK_1} | {IMPACT} | {STRATEGY}               |

## Dependencias

### Dependencias Externas
- {DEPENDENCY_1}
  - Propietario: {OWNER}
  - Cronograma: {TIMELINE}
  - Estado: {STATUS}

### Dependencias Internas
- {DEPENDENCY_1}
  - Equipo: {TEAM}
  - Cronograma: {TIMELINE}
  - Estado: {STATUS}

## Métricas de Éxito

### KPIs a Nivel de Funcionalidad
| Funcionalidad | Métrica  | Objetivo | Método de Medición |
| ------------- | -------- | -------- | ------------------ |
| {FID-001}     | {METRIC} | {TARGET} | {METHOD}           |

<!-- Instrucciones de Uso de la Plantilla:
1. Puntuar las funcionalidades objetivamente usando las métricas definidas
2. Centrarse en el impacto y esfuerzo medibles
3. Considerar las dependencias en la secuencia de implementación
4. Documentar criterios de éxito claros por funcionalidad
5. Mantener la evaluación de riesgos enfocada en el alcance del MVP
6. Actualizar regularmente basado en nueva información
-->
