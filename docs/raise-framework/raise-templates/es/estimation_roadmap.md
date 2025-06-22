---
document_id: "[EST]-[PROJECTCODE]-[SEQ]" # ej: EST-XYZ-001
title: "Estimación de Proyecto y Roadmap: [Nombre del Proyecto]"
project_name: "[Nombre del Proyecto]"
client: "[Nombre del Cliente]"
version: "[Número de Versión, ej., 1.0]"
date: "[YYYY-MM-DD]"
author: "[Nombres o Roles]"
related_docs:
  - "[ID del PRD, ej., PRD-XYZ-001]" # From old PRD ref
  - "[ID del SoW, ej., SOW-XYZ-001]" # From old SoW ref
  - "[ID_DOC_RELACIONADO_1]"
status: "[Draft|In Review|Approved|Final]"
---

# Estimación de Proyecto y Roadmap: [Nombre del Proyecto]

**Documentos Relacionados:**
    *   **PRD:** [ID del PRD, ej., PRD-XYZ-001]
    *   **SoW:** [ID del SoW, ej., SOW-XYZ-001]
    *   **Otros:** [Lista de IDs adicionales]
**Fecha:** [YYYY-MM-DD]
**Versión:** [Número de Versión, ej., 1.0]

## 1. Guía de Estimación en Puntos de Historia (Story Points)

*[Esta sección describe cómo abordar la estimación para este proyecto.]*

*   **Propósito:** Estimar el *tamaño relativo* del trabajo necesario para completar cada elemento del backlog (Funcionalidades, Epics, Historias de Usuario), no el tiempo exacto en horas/días.
*   **Unidad:** Puntos de Historia (Story Points - SP).
*   **Escala:** Usaremos una secuencia basada en Fibonacci modificada: `1, 2, 3, 5, 8, 13, 20, 40, 100`. Números más altos indican mayor tamaño/complejidad/incertidumbre.
*   **Referencia Base:** Acordar una historia de usuario pequeña y bien entendida como punto de referencia (ej., asignarle 2 o 3 SP). Todas las demás estimaciones se harán *en relación* a esta referencia.
*   **Factores a Considerar:**
    *   **Complejidad:** ¿Cuán difícil es técnicamente?
    *   **Esfuerzo:** ¿Cuánto trabajo implica (desarrollo, pruebas, etc.)?
    *   **Incertidumbre/Riesgo:** ¿Cuán bien entendemos el requisito? ¿Existen dependencias desconocidas o riesgos técnicos?
*   **Proceso (Idealmente Planning Poker):**
    1.  El Product Owner/Analista explica el elemento del backlog.
    2.  El equipo discute y hace preguntas para aclarar dudas (Ref: RaiSE Clarity-Seeking).
    3.  Cada miembro del equipo de desarrollo estima *privadamente* el tamaño relativo.
    4.  Todos revelan sus estimaciones simultáneamente.
    5.  Si hay grandes diferencias, los estimadores con los valores más altos y bajos explican su razonamiento.
    6.  El equipo discute hasta alcanzar un *consenso* en la estimación.
*   **Documentación:** Registrar la estimación acordada y cualquier supuesto clave o riesgo identificado durante la discusión.

## 2. Estimación del Backlog

*[Listar los elementos principales del backlog (derivados del PRD/SoW) y su estimación consensuada en Puntos de Historia.]*

| ID (Jira/Otro) | Elemento del Backlog (Funcionalidad/Epic/Historia) | Estimación (SP) | Notas / Supuestos Clave / Riesgos | Referencia (PRD/SoW Sec.) |
|----------------|----------------------------------------------------|-----------------|-----------------------------------|---------------------------|
| [ID-001]       | [Descripción Funcionalidad/Epic 1]                 | [ej., 13]       | [Supuesto sobre API externa X]    | [PRD 4.1]                 |
| [ID-002]       | [Descripción Funcionalidad/Epic 2]                 | [ej., 8]        | [Requiere diseño UX detallado]    | [PRD 4.1]                 |
|  ↳ [ID-002a]   |   *Historia de Usuario 2.1*                        | [ej., 3]        | [Parte de Epic ID-002]            |                           |
|  ↳ [ID-002b]   |   *Historia de Usuario 2.2*                        | [ej., 5]        | [Complejidad en validación]       |                           |
| [ID-003]       | [Descripción Funcionalidad/Epic 3]                 | [ej., 20]       | [Incertidumbre en integración Y]  | [PRD 7]                   |
| ...            | ...                                                | ...             | ...                               | ...                       |
| **TOTAL ESTIMADO** |                                                    | **[Suma SP]**   |                                   |                           |

## 3. Parámetros para el Roadmap

*[Definir los factores clave para proyectar el roadmap.]*

*   **Duración del Sprint/Iteración:** [ej., 2 semanas]
*   **Estructura del Equipo (Asumida):** [Describir brevemente la composición del equipo, ej., 1 PM, 1 Tech Lead, 3 Desarrolladores (Backend/Frontend), 1 QA]
*   **Velocidad Estimada del Equipo (Puntos de Historia por Sprint):** [Número] SP
    *   *Nota sobre la Velocidad:* Este es un valor *estimado* inicial. Se basa en [ej., experiencia pasada con equipos similares, estimación inicial de capacidad]. La velocidad real se determinará midiendo el trabajo completado en los primeros sprints y se usará para ajustar el roadmap futuro. **La velocidad NO es una métrica de rendimiento individual ni una herramienta de comparación entre equipos.**

## 4. Roadmap Proyectado

*[Basado en el Total Estimado de SP y la Velocidad Estimada del Equipo, proyectar qué elementos del backlog podrían abordarse en cada sprint. Este es un plan *indicativo* y está sujeto a cambios.]*

**Total SP Estimados:** [Suma SP de la tabla anterior]
**Velocidad Estimada:** [Velocidad] SP/Sprint
**Número Estimado de Sprints:** [Total SP / Velocidad] = [Número] Sprints (redondear hacia arriba)

| Sprint | Fechas Estimadas      | Objetivo del Sprint (Opcional)                 | Elementos del Backlog Planeados (IDs) | Prioridad (Ref: Feat. Prio.) | SP Estimados por Sprint | SP Acumulados | Notas / Dependencias Clave |
|--------|-----------------------|------------------------------------------------|---------------------------------------|------------------------------|-------------------------|---------------|----------------------------|
| 1      | [Fecha Inicio - Fin]  | [ej., Establecer base proyecto, Auth básica] | [ID-001a, ID-002a]                    | [ej., Alta]                  | [ej., <= Velocidad]     | [SP Sprint 1] |                            |
| 2      | [Fecha Inicio - Fin]  | [ej., Implementar CRUD para Recurso X]       | [ID-001b, ID-002b]                    | [ej., Alta]                  | [ej., <= Velocidad]     | [SP Acum S2]  |                            |
| 3      | [Fecha Inicio - Fin]  | [ej., Integración inicial con Sistema Y]       | [ID-003a, ...]                        | [ej., Media]                 | [ej., <= Velocidad]     | [SP Acum S3]  | [Depende de API Y]         |
| ...    | ...                   | ...                                            | ...                                   | ...                          | ...                     | ...           | ...                        |
| N      | [Fecha Inicio - Fin]  | [ej., Refinamiento final, Preparación UAT]     | [...]                                 | [...]                        | [ej., <= Velocidad]     | [Total SP]    |                            |

**Descargo de Responsabilidad:** Este roadmap es una proyección basada en estimaciones iniciales y una velocidad asumida. El alcance real completado por sprint puede variar. El roadmap se revisará y ajustará regularmente (ej., al final de cada sprint) basándose en el progreso real, la velocidad medida y cualquier cambio en las prioridades o el alcance (gestionado a través del proceso de Gestión de Cambios).

## 5. Vinculación con Modelo de Costos

*[Esta sección conecta la estimación de esfuerzo (SP) y el roadmap proyectado con la estructura de precios definida en el SoW.]*
*(**Referencia:** `statement_of_work.md` Sec 9)*

*   **Relación Esfuerzo-Costo:** [Explicar cómo se relaciona la estimación total en SP con el precio final, especialmente en modelos T&M o híbridos. ej., El costo total estimado en el SoW asume el completado de X SP con una velocidad de Y SP/Sprint.]
*   **Impacto de Cambios en Roadmap:** [Mencionar cómo cambios en el roadmap (ej., re-priorización, cambios de alcance) pueden impactar el costo total o el calendario de pagos definido en el SoW, requiriendo potencialmente un Change Request.]
*   **Supuestos de Costo Clave:** [Reiterar supuestos del SoW que afectan directamente la estimación y el costo, ej., composición del equipo, tarifas por rol.] 