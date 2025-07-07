---
document_id: "EST-DL3221-001"
title: "Estimación de Proyecto y Roadmap: Agente IA de Cotizaciones"
project_name: "Agente IA de Cotizaciones para Totalplay/Grupo Salinas"
client: "Totalplay / Grupo Salinas"
version: "1.0"
date: "2025-05-30"
author: "Emilio Osorio, Karina Aranda"
related_docs:
  - "PRD-DL3221-001"
  - "SOW-DL3221-001" # Asumido
  - "PRI-DL3221-001"
  - "BCK-DL3221-001"
status: "Draft"
---

# Estimación de Proyecto y Roadmap: Agente IA de Cotizaciones

**Documentos Relacionados:**
    *   **PRD:** PRD-DL3221-001
    *   **SoW:** SOW-DL3221-001 (Asumido)
    *   **Priorización:** PRI-DL3221-001
    *   **Backlog:** BCK-DL3221-001
**Fecha:** 2025-05-30
**Versión:** 1.0

## 1. Guía de Estimación en Puntos de Historia (Story Points)

*   **Propósito:** Estimar el *tamaño relativo* del trabajo necesario para completar cada elemento del backlog (Funcionalidades, Epics, Historias de Usuario), no el tiempo exacto en horas/días.
*   **Unidad:** Puntos de Historia (Story Points - SP).
*   **Escala:** Usaremos una secuencia basada en Fibonacci modificada: `1, 2, 3, 5, 8, 13, 20, 40, 100`. Números más altos indican mayor tamaño/complejidad/incertidumbre.
*   **Referencia Base:** [**Pendiente**] Acordar una historia de usuario pequeña y bien entendida (ej., US-001 o US-002 del backlog) como punto de referencia (asignarle 2 o 3 SP). Todas las demás estimaciones se harán *en relación* a esta referencia.
*   **Factores a Considerar:**
    *   **Complejidad:** ¿Cuán difícil es técnicamente?
    *   **Esfuerzo:** ¿Cuánto trabajo implica (desarrollo, pruebas, etc.)?
    *   **Incertidumbre/Riesgo:** ¿Cuán bien entendemos el requisito? ¿Existen dependencias desconocidas o riesgos técnicos?
*   **Proceso (Recomendado: Planning Poker):**
    1.  El Product Owner/Analista explica el elemento del backlog.
    2.  El equipo (AI Architect, AI Engineer, AI QA) discute y hace preguntas para aclarar dudas.
    3.  Cada miembro del equipo estima *privadamente* el tamaño relativo.
    4.  Todos revelan sus estimaciones simultáneamente.
    5.  Si hay grandes diferencias, los estimadores con los valores más altos y bajos explican su razonamiento.
    6.  El equipo discute hasta alcanzar un *consenso* en la estimación.
*   **Documentación:** Registrar la estimación acordada en `project_backlog.md` y cualquier supuesto clave o riesgo identificado durante la discusión.

## 2. Estimación del Backlog

*[**Pendiente** - Requiere sesión de estimación con el equipo de desarrollo (AI Architect, AI Engineer, AI QA). Los resultados se registrarán en `project_backlog.md`.]*

| ID (Backlog) | Elemento del Backlog (Feature/Historia MVP) | Estimación (SP) | Notas / Supuestos Clave / Riesgos | Referencia (PRD/SoW Sec.) |
|--------------|---------------------------------------------|-----------------|-----------------------------------|---------------------------|
| F001         | Correo centralizado                         | [Pendiente]     |                                   | PRD 1.1                   |
| F004         | Búsqueda en catálogo                        | [Pendiente]     | Dependencia: Acceso Catálogo      | PRD 2.1                   |
| F012         | Búsqueda externa                            | [Pendiente]     | Dependencia: APIs Búsqueda        | PRD 2.2                   |
| F005         | Generación correos proveedores              | [Pendiente]     |                                   | PRD 2.4, 2.5              |
| F007         | Enlace recepción estandarizada              | [Pendiente]     |                                   | PRD 3.1                   |
| F008         | Generación cuadros comparativos             | [Pendiente]     |                                   | PRD 3.3                   |
| F009         | Generación correos respuesta solicitantes   | [Pendiente]     |                                   | PRD 5.1, 5.2              |
| F013         | Notificaciones automáticas                  | [Pendiente]     |                                   | PRD 4.3                   |
| F017         | Formatos diferenciados                      | [Pendiente]     |                                   | PRD 1.4, 5.4              |
| F016         | Evaluación preliminar externa (parte MVP) | [Pendiente]     |                                   | PRD 2.3                   |
| TASK-001     | Config Infraestructura                      | [Pendiente]     |                                   | Tech Sec 3                |
| TASK-002     | Conexión Catálogo                         | [Pendiente]     |                                   | Tech Sec 3                |
| TASK-003     | Config N8N                                  | [Pendiente]     |                                   | Tech Sec 3                |
| TASK-004     | Fine-tuning LLM                           | [Pendiente]     |                                   | Tech Sec 7                |
| ...          | ...                                         | ...             | ...                               | ...                       |
| **TOTAL ESTIMADO MVP** |                                             | **[Suma SP Pendiente]** |                                   |                           |

## 3. Parámetros para el Roadmap

*   **Duración del Sprint/Iteración:** **2 semanas**
*   **Estructura del Equipo:**
    *   1 Engagement Manager (Facilitador, no cuenta en capacidad SP)
    *   1 AI Architect (Part-Time, ~50%)
    *   1 AI Engineer (Full-Time, ~100%)
    *   1 AI QA (Part-Time, ~50%)
*   **Capacidad Estimada Inicial del Equipo (Puntos de Historia por Iteración):** **16 SP**
    *   *Cálculo:* (0.5 Arq * 8) + (1 Ing * 8) + (0.5 QA * 8) = 4 + 8 + 4 = 16 SP.
    *   *Nota sobre la Capacidad/Velocidad:* Este es un valor *estimado inicial* basado en la composición del equipo y la normalización sugerida por SAFe para equipos nuevos. **No es una velocidad garantizada.** La capacidad real se determinará midiendo el trabajo completado en la primera Iteración y se usará para ajustar el roadmap futuro. El equipo planificará la primera iteración basándose en esta capacidad como guía y su propio juicio sobre lo que pueden comprometerse a entregar.

## 4. Roadmap Proyectado

*[**Pendiente** - Se completará después de la estimación del backlog en SP.]*

**Total SP Estimados MVP:** [Suma SP Pendiente de la tabla anterior]
**Capacidad Estimada:** 16 SP/Iteración
**Número Estimado de Iteraciones MVP:** [Total SP MVP / 16] = [Número Pendiente] Iteraciones (redondear hacia arriba)

| Iteración | Fechas Estimadas      | Objetivo de la Iteración (Sugerido)             | Elementos del Backlog Planeados (IDs)       | Prioridad (Ref: PRI) | SP Estimados por Iteración | SP Acumulados   | Notas / Dependencias Clave                   |
|-----------|-----------------------|-------------------------------------------------|---------------------------------------------|----------------------|----------------------------|-----------------|----------------------------------------------|
| 1         | [Fecha Inicio - Fin]  | Establecer bases, recepción y búsqueda interna  | F001, F004 (inicio), TASK-001, TASK-002     | Alta                 | [<= 16 SP Pendiente]       | [SP Iter 1 Pend.] | Depende: Acceso correo, Acceso catálogo    |
| 2         | [Fecha Inicio - Fin]  | Búsqueda externa y generación correos           | F004 (fin), F012, F005, F013, TASK-003       | Alta                 | [<= 16 SP Pendiente]       | [SP Acum 2 Pend.] | Depende: APIs Búsqueda, Modelo LLM básico |
| 3         | [Fecha Inicio - Fin]  | Recepción, comparación y respuesta              | F007, F008, F017, F009, F016(básico), TASK-004 | Alta                 | [<= 16 SP Pendiente]       | [Total SP MVP Pend.] |                                              |
| ...       | ...                   | ...                                             | ...                                         | ...                  | ...                        | ...             | ...                                          |

**Descargo de Responsabilidad:** Este roadmap es una proyección basada en estimaciones pendientes y una capacidad inicial asumida. El alcance real completado por iteración puede variar. El roadmap se revisará y ajustará regularmente (ej., al final de cada iteración) basándose en el progreso real, la velocidad medida y cualquier cambio en las prioridades o el alcance.

## 5. Vinculación con Modelo de Costos

*[**Pendiente** - Requiere definición del modelo de costos en el SoW y estimación completa en SP.]*

*   **Relación Esfuerzo-Costo:** [Explicar cómo se relaciona la estimación total en SP con el precio final. ej., El costo total estimado en el SoW asume el completado de X SP con una capacidad de 16 SP/Iteración y tarifas definidas.]
*   **Impacto de Cambios en Roadmap:** [Mencionar cómo cambios pueden impactar costo/calendario.]
*   **Supuestos de Costo Clave:** [Reiterar supuestos del SoW: composición del equipo, tarifas.] 