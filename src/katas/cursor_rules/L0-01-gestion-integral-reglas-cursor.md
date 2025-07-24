# L0-01: Gestión Integral y Establecimiento de Reglas Cursor

**Versión Kata**: 1.0
**Fecha**: {{YYYY-MM-DD}}
**Autor**: CursorRules-GPT

## 1. Propósito de la Kata

Esta Kata de Nivel 0 orquesta el proceso completo de análisis de un repositorio de software y el establecimiento de un sistema de Reglas Cursor (`.mdc` files) junto con su documentación de gobernanza asociada. El objetivo es guiar a un agente IA especializado en la creación de un conjunto coherente y efectivo de reglas que reflejen los estándares y patrones del repositorio, facilitando así un desarrollo asistido por IA de alta calidad y consistencia.

## 2. Alcance y Objetivos

* Analizar un repositorio de código fuente para identificar patrones, estándares y tecnologías.
* Generar un conjunto de Reglas Cursor (`.mdc`) que formalicen estos hallazgos.
* Crear y mantener la documentación de gobernanza para el sistema de reglas, incluyendo:
  * Documento de razonamiento (`ai-rules-reasoning.md`)
  * Índice de reglas (`[nombre-repo]-rules-index.md`)
  * Plan de implementación (`[nombre-repo]-implementation-plan.md`)
* Establecer reglas fundacionales, incluyendo estándares generales de codificación, reglas metodológicas (ej. RaiSE), y meta-reglas para la gestión y precedencia del sistema de reglas del proyecto.

## 3. Prerrequisitos

* Acceso al repositorio de código fuente que se va a analizar.
* Disponibilidad de las plantillas de Reglas Cursor (ubicadas en `.raise/templates/cursor-rules/`).
* Disponibilidad de plantillas genéricas para los documentos de gobernanza (o la capacidad de crearlos basados en una estructura estándar).
* Conocimiento de los documentos guía:
  * `guia_agente_extraccion_reglas.md` (o el prompt/instrucciones equivalentes para el agente IA).
  * `2025-05-23_21-45-guía-para-reglas-de-repositorio-y-análisis-de-plantillas.md` (para el análisis de las plantillas de reglas).
* El directorio `.raise/katas/cursor_rules/` debe existir para almacenar esta y otras katas relacionadas.

## 4. Fases y Pasos Detallados

Esta Kata se descompone en las siguientes fases principales. Cada fase puede invocar sub-Katas (Nivel 2) para tareas específicas.

### Fase 0: Preparación y Configuración del Entorno del Agente

* **Objetivo**: Asegurar que el agente IA esté correctamente configurado y tenga acceso a todos los recursos necesarios.
* **Pasos**:
  1. **Cargar Perfil del Agente**: Revisar y comprender las instrucciones de rol y capacidades (ej. `system_prompt`, `guia_agente_extraccion_reglas.md`).
  2. **Verificar Acceso a Plantillas**: Confirmar la capacidad de leer y utilizar las plantillas de reglas de `.raise/templates/cursor-rules/`.
  3. **Verificar Acceso a Documentos Guía**: Confirmar la capacidad de leer y utilizar `guia_agente_extraccion_reglas.md` y el análisis de plantillas en `2025-05-23_21-45-guía-para-reglas-de-repositorio-y-análisis-de-plantillas.md`.
  4. **Preparar Directorios de Destino**: Asegurar que la estructura de directorios `.cursor/rules/` y `.raise/docs/[nombre-repo]/` esté lista o pueda ser creada.

### Fase 1: Análisis Inicial del Repositorio y Descubrimiento

* **Objetivo**: Obtener una comprensión inicial de alto nivel del repositorio.
* **Sub-Kata Invocada**: `L2-01-analisis-exploratorio-repositorio.md`
* **Entregable Esperado**: Un documento de análisis preliminar o borrador inicial para `ai-rules-reasoning.md`.
* **Próximos Pasos**: Proceder a la Fase 2 para inicializar los documentos de gobernanza.

### Fase 2: Creación/Actualización de Documentos de Gobernanza Iniciales

* **Objetivo**: Establecer la estructura básica para la documentación de gobernanza de las reglas.
* **Sub-Kata Invocada**: `L2-02-inicializacion-gobernanza-reglas.md`
* **Entregables Esperados**:
  * Archivo `ai-rules-reasoning.md` inicializado.
  * Archivo `[nombre-repo]-rules-index.md` inicializado.
  * Archivo `[nombre-repo]-implementation-plan.md` inicializado.
* **Próximos Pasos**: Proceder a la Fase 3 para establecer las reglas fundacionales.

### Fase 3: Establecimiento de Reglas Fundacionales

* **Objetivo**: Implementar las reglas base que definen los estándares generales de codificación y la metodología de trabajo con IA.
* **Sub-Fase 3.1: Adopción/Adaptación de Reglas de Estándares Generales de Codificación**
  * **Sub-Kata Invocada**: `L2-04-establecimiento-reglas-estandares-generales.md`
  * **Entregable Esperado**: Regla `001-general-coding-standards.mdc` (o similar) creada y documentada.
* **Sub-Fase 3.2: Adopción/Adaptación de Reglas de Metodología (RaiSE)**
  * **Sub-Kata Invocada**: `L2-05-establecimiento-reglas-metodologia-raise.md`
  * **Entregable Esperado**: Regla `010-raise-methodology-overview.mdc` (o similar) creada y documentada.
* **Próximos Pasos**: Proceder a la Fase 4 para establecer las meta-reglas.

### Fase 4: Establecimiento de Meta-Reglas Fundamentales

* **Objetivo**: Crear las meta-reglas esenciales que gobiernan el propio sistema de reglas, incluyendo la gestión por IA y la precedencia.
* **Sub-Kata Invocada**: `L2-06-establecimiento-meta-reglas-fundamentales.md`
* **Entregables Esperados**:
  * Regla `901-ia-rule-management.mdc` (o similar) creada y documentada.
  * Regla `902-rule-precedence.mdc` (o similar) creada y documentada.
* **Próximos Pasos**: Proceder a la Fase 5 para la generación de reglas específicas del repositorio.

### Fase 5: Extracción y Generación Iterativa de Reglas Específicas del Repositorio

* **Objetivo**: Identificar, analizar y documentar patrones y estándares específicos del repositorio como Reglas Cursor individuales. Este es el núcleo de la personalización de reglas para el proyecto.
* **Proceso**: Este es un proceso iterativo. Para cada regla o grupo de reglas identificadas:
  1. Invocar la Sub-Kata: `L2-03-extraccion-generacion-regla-cursor.md`.
     * La entrada a esta sub-kata será el área específica a analizar (ej. "Estándares de C#", "Patrón de Logging", "Arquitectura Limpia").
* **Nota**: Esta fase se ejecuta después de que todas las reglas fundacionales y meta-reglas estén establecidas, proporcionando un marco sólido.
* **Próximos Pasos**: Una vez completado un conjunto satisfactorio de reglas específicas, proceder a la Fase 6.

### Fase 6: Revisión, Pruebas y Despliegue Inicial

* **Objetivo**: Asegurar la coherencia, completitud y corrección del sistema de reglas y su documentación antes de un despliegue más amplio o formalización.
* **Pasos**:
  1. Revisar la consistencia entre todas las reglas `.mdc` generadas.
  2. Validar la correcta aplicación de los `globs` y el `order`.
  3. Revisar la consistencia y completitud de los documentos de gobernanza (`ai-rules-reasoning.md`, `[nombre-repo]-rules-index.md`, `[nombre-repo]-implementation-plan.md`).
  4. Verificar que todas las reglas estén correctamente listadas en el índice y plan.
  5. (Conceptual) Realizar pruebas prácticas con el asistente IA utilizando las reglas generadas para verificar su efectividad.
  6. Generar un informe resumen del estado final del sistema de reglas.
* **Próximos Pasos**: Proceder a la Fase 7 para el mantenimiento continuo.

### Fase 7: Mantenimiento y Evolución Continua

* **Objetivo**: Mantener el sistema de reglas actualizado y relevante a medida que el proyecto evoluciona.
* **Pasos (Conceptuales a Largo Plazo)**:
  1. Monitorear la efectividad de las reglas y la retroalimentación del equipo de desarrollo.
  2. Identificar la necesidad de nuevas reglas o la modificación/eliminación de reglas existentes.
  3. Aplicar cambios a las reglas y a la documentación de gobernanza siguiendo un proceso controlado (potencialmente reinvocando sub-katas como `L2-03` o `L2-06`).
  4. Comunicar los cambios al equipo.

## 5. Entregables de esta Kata (Nivel 0)

* Un conjunto completo de Reglas Cursor (`.mdc` files) en `.cursor/rules/` para el repositorio analizado.
* Documentación de gobernanza completa y actualizada en `.raise/docs/[nombre-repo]/`:
  * `ai-rules-reasoning.md`
  * `[nombre-repo]-rules-index.md`
  * `[nombre-repo]-implementation-plan.md`
* Un sistema de reglas que incluya reglas fundacionales y meta-reglas.

## 6. Consideraciones Adicionales

* **Iteración**: El proceso descrito en la Fase 5 es inherentemente iterativo.
* **Flexibilidad**: Si un repositorio ya posee algunas reglas o documentos, esta Kata debe guiar al agente para actualizarlos y complementarlos.
* **Nombres de Sub-Katas**: Los nombres de las sub-katas `L2-XX-...` ahora están establecidos.

## 7. Próximos Pasos

Asegurar que el contenido detallado de cada una de las Sub-Katas (Nivel 2) referenciadas esté completo y alineado con este flujo actualizado. Iniciar la ejecución de la Fase 0 si se comienza un nuevo proyecto de establecimiento de reglas.
