---
document_id: "[BCK]-[PROJECTCODE]-[SEQ]" # ej: BCK-XYZ-001
title: "Backlog de Proyecto: [Nombre del Proyecto]"
project_name: "[Nombre del Proyecto]"
client: "[Nombre del Cliente]"
version: "[Número de Versión, ej., 1.0]"
date: "[YYYY-MM-DD]"
author: "[Nombres o Roles]"
related_docs:
  - "[ID del PRD, ej., PRD-XYZ-001]" 
  - "[ID del SoW, ej., SOW-XYZ-001]"
  - "[ID de Priorización, ej., PRI-XYZ-001]"
  - "[ID de Estimación, ej., EST-XYZ-001]"
status: "[Draft|In Review|Approved|Final]"
---

# Backlog de Proyecto: [Nombre del Proyecto]

**Documentos Relacionados:**
- **PRD:** [ID del PRD, ej., PRD-XYZ-001]
- **SoW:** [ID del SoW, ej., SOW-XYZ-001]
- **Priorización:** [ID de Priorización, ej., PRI-XYZ-001]
- **Estimación:** [ID de Estimación, ej., EST-XYZ-001]
**Fecha:** [YYYY-MM-DD]
**Versión:** [Número de Versión, ej., 1.0]

## 1. Descripción General

*[Breve introducción al documento de backlog, su propósito y cómo se relaciona con otros documentos del proyecto.]*

Este documento representa el backlog consolidado del proyecto a alto nivel. Sirve como fuente centralizada para la definición de Epics, Features e Historias de Usuario que forman parte del alcance del proyecto. Este backlog es la base para los procesos de priorización (Ref: `feature-prioritization-template.md`) y estimación (Ref: `estimation_roadmap.md`).

## 2. Estructura del Backlog

El backlog está organizado jerárquicamente, siguiendo esta estructura:

- **Epics**: Grandes bloques de trabajo que generalmente abarcan múltiples sprints y se alinean con capacidades o módulos completos del sistema.
- **Features**: Funcionalidades específicas dentro de un Epic que entregan valor por sí mismas.
- **Historias de Usuario**: Unidades de trabajo específicas que describen una funcionalidad desde la perspectiva del usuario.

## 3. Epics

*[Listado de todos los Epics que conforman el alcance del proyecto, derivados del PRD Sec 3.1 y Sec 4.]*

| ID Epic | Título | Descripción | PRD Ref | Prioridad | Estimación (SP) | Estado |
|---------|--------|-------------|---------|-----------|-----------------|--------|
| EPIC-001 | [Título del Epic] | [Descripción breve] | [PRD Sec.] | [Alta/Media/Baja] | [Total SP] | [Por Iniciar/En Progreso/Completado] |
| EPIC-002 | [Título del Epic] | [Descripción breve] | [PRD Sec.] | [Alta/Media/Baja] | [Total SP] | [Por Iniciar/En Progreso/Completado] |
| ... | ... | ... | ... | ... | ... | ... |

## 4. Features

*[Desglose de Features por Epic, derivados del PRD Sec 4.1 y complementados con diseño técnico (Tech Design).]*

### Epic: EPIC-001 - [Título del Epic]

| ID Feature | Título | Descripción | Criterios de Aceptación | PRD Ref | Tech Ref | Prioridad | Estimación (SP) | Estado |
|------------|--------|-------------|-------------------------|---------|----------|-----------|-----------------|--------|
| FEAT-001 | [Título del Feature] | [Descripción] | [Criterios clave] | [PRD Sec.] | [Tech Sec.] | [Alta/Media/Baja] | [SP] | [Por Iniciar/En Progreso/Completado] |
| FEAT-002 | [Título del Feature] | [Descripción] | [Criterios clave] | [PRD Sec.] | [Tech Sec.] | [Alta/Media/Baja] | [SP] | [Por Iniciar/En Progreso/Completado] |
| ... | ... | ... | ... | ... | ... | ... | ... | ... |

### Epic: EPIC-002 - [Título del Epic]

| ID Feature | Título | Descripción | Criterios de Aceptación | PRD Ref | Tech Ref | Prioridad | Estimación (SP) | Estado |
|------------|--------|-------------|-------------------------|---------|----------|-----------|-----------------|--------|
| FEAT-003 | [Título del Feature] | [Descripción] | [Criterios clave] | [PRD Sec.] | [Tech Sec.] | [Alta/Media/Baja] | [SP] | [Por Iniciar/En Progreso/Completado] |
| FEAT-004 | [Título del Feature] | [Descripción] | [Criterios clave] | [PRD Sec.] | [Tech Sec.] | [Alta/Media/Baja] | [SP] | [Por Iniciar/En Progreso/Completado] |
| ... | ... | ... | ... | ... | ... | ... | ... | ... |

## 5. Historias de Usuario

*[Desglose de Historias de Usuario por Feature. Cada historia sigue el formato "Como [rol], quiero [funcionalidad] para [beneficio]".]*

### Feature: FEAT-001 - [Título del Feature]

| ID Historia | Historia de Usuario | Criterios de Aceptación | Estimación (SP) | Dependencias | Estado |
|-------------|---------------------|-------------------------|-----------------|--------------|--------|
| US-001 | Como [rol], quiero [funcionalidad] para [beneficio]. | <ul><li>Criterio 1</li><li>Criterio 2</li><li>...</li></ul> | [1/2/3/5/8/13...] | [US-002, US-003] | [Por Iniciar/En Progreso/Completado] |
| US-002 | Como [rol], quiero [funcionalidad] para [beneficio]. | <ul><li>Criterio 1</li><li>Criterio 2</li><li>...</li></ul> | [1/2/3/5/8/13...] | [ninguna] | [Por Iniciar/En Progreso/Completado] |
| ... | ... | ... | ... | ... | ... |

### Feature: FEAT-002 - [Título del Feature]

| ID Historia | Historia de Usuario | Criterios de Aceptación | Estimación (SP) | Dependencias | Estado |
|-------------|---------------------|-------------------------|-----------------|--------------|--------|
| US-003 | Como [rol], quiero [funcionalidad] para [beneficio]. | <ul><li>Criterio 1</li><li>Criterio 2</li><li>...</li></ul> | [1/2/3/5/8/13...] | [US-004] | [Por Iniciar/En Progreso/Completado] |
| US-004 | Como [rol], quiero [funcionalidad] para [beneficio]. | <ul><li>Criterio 1</li><li>Criterio 2</li><li>...</li></ul> | [1/2/3/5/8/13...] | [ninguna] | [Por Iniciar/En Progreso/Completado] |
| ... | ... | ... | ... | ... | ... |

## 6. Tareas Técnicas

*[Listado de tareas técnicas que no están directamente vinculadas a una historia de usuario pero son necesarias para el proyecto.]*

| ID Tarea | Título | Descripción | Estimación (SP) | Dependencias | Estado |
|----------|--------|-------------|-----------------|--------------|--------|
| TASK-001 | [Título de la Tarea] | [Descripción] | [1/2/3/5/8/13...] | [US-001, TASK-002] | [Por Iniciar/En Progreso/Completado] |
| TASK-002 | [Título de la Tarea] | [Descripción] | [1/2/3/5/8/13...] | [ninguna] | [Por Iniciar/En Progreso/Completado] |
| ... | ... | ... | ... | ... | ... |

## 7. Resumen de Estimaciones

*[Esta sección proporciona un resumen consolidado de las estimaciones realizadas utilizando la escala de Story Points definida en el documento de Estimación y Roadmap.]*

*   **Escala de Estimación:** Secuencia Fibonacci modificada: `1, 2, 3, 5, 8, 13, 20, 40, 100` (Ref: `estimation_roadmap.md` Sec 1)
*   **Historia de Referencia:** [Breve descripción de la historia usada como referencia] - **Valor:** [ej., 3 SP]

### Totales por Epic

| ID Epic | Título | Total SP | % del Proyecto |
|---------|--------|----------|----------------|
| EPIC-001 | [Título del Epic] | [Suma SP] | [%] |
| EPIC-002 | [Título del Epic] | [Suma SP] | [%] |
| ... | ... | ... | ... |
| **TOTAL PROYECTO** | | **[SUMA TOTAL SP]** | **100%** |

### Distribución por Complejidad

*[Muestra la distribución de historias según su complejidad para ayudar a entender la composición del backlog.]*

| Valor SP | Cantidad de Historias | % del Total de Historias | Total SP | % del Total SP |
|----------|------------------------|--------------------------|----------|----------------|
| 1 | [N] | [%] | [N×1] | [%] |
| 2 | [N] | [%] | [N×2] | [%] |
| 3 | [N] | [%] | [N×3] | [%] |
| 5 | [N] | [%] | [N×5] | [%] |
| 8 | [N] | [%] | [N×8] | [%] |
| 13 | [N] | [%] | [N×13] | [%] |
| 20 | [N] | [%] | [N×20] | [%] |
| 40 | [N] | [%] | [N×40] | [%] |
| 100 | [N] | [%] | [N×100] | [%] |

## 8. Listado de Dependencias Clave

*[Esta sección identifica las dependencias críticas entre elementos del backlog que podrían afectar la planificación y ejecución del proyecto.]*

| ID Dependencia | Elemento Dependiente | Depende de | Tipo | Descripción | Impacto |
|----------------|----------------------|------------|------|-------------|---------|
| DEP-001 | [US-001] | [US-002] | [Bloqueante/Facilitadora] | [Descripción] | [Alto/Medio/Bajo] |
| DEP-002 | [FEAT-001] | [Sistema Externo X] | [Técnica/Negocio] | [Descripción] | [Alto/Medio/Bajo] |
| ... | ... | ... | ... | ... | ... |

## 9. Vinculación con Roadmap

*[Esta sección conecta el backlog con la planificación temporal establecida en el documento de Estimación y Roadmap.]*

*   **Velocidad Estimada del Equipo:** [N] SP/Sprint (Ref: `estimation_roadmap.md` Sec 3)
*   **Cantidad Estimada de Sprints:** [Total SP / Velocidad] = [N] Sprints

| Sprint | Elementos Planificados (IDs) | Total SP | % Acumulado |
|--------|------------------------------|----------|-------------|
| 1 | [US-001, US-002, TASK-001] | [Suma SP] | [%] |
| 2 | [US-003, US-004] | [Suma SP] | [%] |
| ... | ... | ... | ... |

## 10. Notas Adicionales

*[Cualquier información relevante que no encaje en las secciones anteriores.]*

- [Supuestos clave para la implementación del backlog]
- [Aclaraciones sobre la estructura o mantenimiento del backlog]
- [Otros comentarios importantes]

## 11. Historial del Documento

| Versión | Fecha | Autor(es) | Cambios Realizados |
|---------|-------|-----------|-------------------|
| 0.1 | YYYY-MM-DD | [Nombre(s)] | Versión inicial del backlog |
| ... | ... | ... | ... |