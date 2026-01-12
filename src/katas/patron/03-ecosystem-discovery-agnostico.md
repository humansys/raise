---
id: L2-03-ecosystem-discovery-agnostico
nivel: 2
tags: [arquitectura, diseño, ecosistema, agnostico, reutilizacion]
---
# L2-03: Descubrimiento de Ecosistema y Diseño de Features Agnóstico a la Pila Tecnológica

## Metadatos
- **Id**: L2-03-ecosystem-discovery-agnostico
- **Nivel**: 2
- **Título**: Descubrimiento de Ecosistema y Diseño de Features Agnóstico a la Pila Tecnológica
- **Propósito**: Formalizar un proceso de análisis a nivel de ecosistema, tecnológicamente agnóstico, para diseñar nuevos features maximizando la reutilización de componentes existentes y previniendo la duplicación funcional, antes de escribir una sola línea de código de implementación.
- **Contexto**: Se ejecuta después de haber analizado los módulos relevantes con la Kata `L2-02` y antes de diseñar la solución técnica para un nuevo requerimiento o feature que involucra la interacción de múltiples módulos o servicios.
- **Audiencia**: Arquitecto de Software, Líder Técnico, Analista de Sistemas.

## Pre-condiciones
- **Artefactos de `L2-02` generados**: La Kata `L2-02-Analisis-Agnostico-Codigo-Fuente` ha sido ejecutada para todos los módulos o servicios relevantes dentro del ecosistema. Esto implica tener disponibles los siguientes documentos por cada módulo:
  - `service-overview.md`
  - `contracts.yaml` o `contracts.md`
  - `dependencies.yaml`
  - `use-cases.md`
- **Requerimientos del Feature definidos**: Se cuenta con una descripción clara de la nueva funcionalidad a construir, incluyendo historias de usuario y criterios de aceptación.

## Principio Fundamental: "ECOSYSTEM-FIRST DESIGN"
Antes de diseñar cualquier feature nuevo, se debe demostrar una comprensión completa del ecosistema existente y justificar por qué la nueva funcionalidad no puede ser implementada mediante la extensión o reutilización de los componentes ya existentes. El diseño no parte de una hoja en blanco, sino del estado actual del ecosistema.

## Pasos de la Kata

### Fase 1: Consolidación y Mapeo de Capacidades del Ecosistema

#### Paso 1.1: Centralizar Artefactos del Ecosistema
- **Acción**: Recopilar los artefactos clave (`service-overview.md`, `contracts.yaml`, `use-cases.md`) de cada módulo analizado en un directorio de trabajo centralizado para esta Kata.
- **Criterios de Aceptación**:
  - Se crea una estructura de directorios (`.raise/analysis/[feature-name]/ecosystem-artifacts/`) que contiene una copia o enlace a los documentos esenciales de cada módulo.

#### Paso 1.2: Generar la Matriz de Capacidades del Ecosistema
- **Acción**: Analizar la colección de documentos `use-cases.md` y `contracts.yaml` para construir un mapa consolidado de todas las capacidades de negocio que el ecosistema ofrece. Posteriormente, mapear cada requerimiento del nuevo feature contra esta matriz de capacidades.
- **Criterios de Aceptación**:
  - Se genera un artefacto `capability-matrix.yaml`.
  - Para cada requerimiento, la matriz identifica los módulos existentes que ofrecen la funcionalidad, el porcentaje de cobertura (`coverage: 100%` si es completo, `coverage: 70%` si es parcial), y el `gap` (lo que falta).
  - Se incluye una `recommendation` inicial (`REUSE`, `EXTEND`).

### Fase 2: Análisis de Duplicación y Definición de la Estrategia

#### Paso 2.1: Análisis de Solapamiento Funcional (Overlap Analysis)
- **Acción**: Utilizando la `capability-matrix.yaml` como entrada, realizar un análisis semántico para identificar solapamientos funcionales. El objetivo es detectar dónde la creación de nuevo código duplicaría lógica ya existente en otro lugar del ecosistema.
- **Criterios de Aceptación**:
  - Se genera un artefacto `overlap-analysis.yaml`.
  - El análisis clasifica los solapamientos por nivel de riesgo (`CRITICAL`: >90% de duplicación, `HIGH`: >70%).
  - Se emiten recomendaciones anti-duplicación explícitas para cada requerimiento: `REUSE - NO CHANGES`, `EXTEND - MINIMAL CHANGES`, o `EVALUATE - JUSTIFY NEW`.

#### Paso 2.2: Validación de Continuidad Arquitectónica
- **Acción**: Evaluar cómo las potenciales modificaciones o adiciones se alinearían con los patrones arquitectónicos predominantes en el ecosistema. Se deben analizar los patrones de comunicación (ej. REST vs. Mensajería), modelos de datos y estrategias de resiliencia documentados en los artefactos de `L2-02`.
- **Criterios de Aceptación**:
  - Se genera un documento `architecture-validation.md` que confirma que la estrategia de reutilización/extensión es coherente con la arquitectura existente.
  - Se identifica cualquier posible desviación de los patrones establecidos y se justifica.

### Fase 3: Diseño de Opciones y Evaluación de Impacto

#### Paso 3.1: Generar Opciones de Diseño Orientadas a la Reutilización
- **Acción**: Basado en los análisis anteriores, generar un mínimo de dos opciones de diseño.
    - **Opción A (Máxima Reutilización - Mandatoria)**: Propone una solución que se basa en extender los módulos existentes. Debe detallar qué módulos se modifican y cómo. El porcentaje de reutilización debe ser el máximo posible.
    - **Opción B (Nuevo Componente - Desaconsejada)**: Propone la creación de un nuevo módulo o servicio. Debe incluir una justificación robusta de por qué la reutilización no es viable, evaluando el impacto a largo plazo en mantenimiento, coherencia y coste operativo.
- **Criterios de Aceptación**:
  - Se presenta un documento `design-options.md` que compara ambas opciones, evaluando pros, contras, porcentaje de reutilización, tiempo de desarrollo estimado e impacto arquitectónico.
  - La recomendación por defecto debe ser la Opción A, a menos que existan razones técnicas o de negocio contundentes.

#### Paso 3.2: Crear la Matriz de Impacto Multi-Módulo
- **Acción**: Para la opción de diseño seleccionada, generar una matriz de impacto detallada. Esta matriz debe listar cada módulo afectado y describir granularmente los cambios requeridos.
- **Criterios de Aceptación**:
  - Se genera un artefacto `impact-matrix.yaml`.
  - Para cada módulo, se especifica: `impact_level` (ALTO, MEDIO, BAJO, NULO), `specific_changes` (lista de cambios en contratos, lógica, etc.), `effort_estimate` (en unidades de tiempo) y `risk_level`.
  - Se incluye un resumen ejecutivo con el número total de módulos impactados y el esfuerzo total estimado.

### Fase 4: Formalización del Diseño Técnico y Plan de Implementación

#### Paso 4.1: Diseñar las Extensiones de Contratos y Flujos de Interacción
- **Acción**: Detallar las modificaciones o adiciones a los `contracts.yaml` de los módulos afectados. Diseñar y visualizar los flujos de comunicación entre módulos para la nueva funcionalidad (ej. con un diagrama de secuencia en Mermaid).
- **Criterios de Aceptación**:
  - Se producen definiciones de contrato actualizadas. Cualquier cambio en un contrato existente debe ser aditivo y 100% compatible con versiones anteriores (backward compatible).
  - Se genera un `interaction-flow.md` con el diagrama de secuencia.

#### Paso 4.2: Generar Evidencia de Cero Duplicación
- **Acción**: Sintetizar la información de los análisis previos en un documento final que sirva como evidencia auditable de que el diseño previene la duplicación.
- **Criterios de Aceptación**:
  - Se crea un documento `zero-duplication-evidence.md`.
  - El documento lista cada pieza de funcionalidad requerida y la mapea a un componente existente que la provee (`REUSES module.capability`), o la clasifica como `NEW - NO OVERLAP`.
  - Se incluyen métricas de reutilización: `% de funcionalidad reutilizada`, `% de funcionalidad nueva`, `N de módulos modificados / Total de módulos`.

#### Paso 4.3: Crear el Roadmap de Implementación
- **Acción**: Desarrollar un plan de implementación por fases que ordene lógicamente el trabajo a través de los diferentes módulos. El plan debe incluir "gates" de validación para asegurar que los principios de diseño se mantengan durante el desarrollo.
- **Criterios de Aceptación**:
  - Se genera un `implementation-roadmap.md` con fases, entregables por fase y criterios de validación claros para cada "gate".

## Post-condiciones
- Un diseño técnico validado que está explícitamente alineado con la arquitectura y capacidades del ecosistema existente.
- Evidencia documentada que demuestra que el diseño previene la duplicación funcional y maximiza la reutilización.
- Un plan de implementación claro y por fases que reduce el riesgo de integración y coordina el trabajo entre diferentes módulos o equipos.
- Una base sólida para la posterior generación de historias de usuario técnicas y la asignación de tareas de desarrollo.

## Notas Adicionales
- **Herramientas**: Fomentar el uso de scripts para automatizar la consolidación de artefactos y la generación de borradores de las matrices.
- **Cultura**: Esta Kata refuerza una cultura de colaboración y visión sistémica, obligando a los equipos a mirar más allá de los límites de su propio módulo y a considerar el impacto global de sus decisiones.
- **Escalabilidad**: El proceso es escalable. Para ecosistemas muy grandes, el "alcance relevante" de los módulos a analizar en la Pre-condición puede ser acotado por el arquitecto.
