# Guía del Proceso RaiSE: Definición Inicial de Requisitos y Alcance

Este documento describe los primeros pasos del proceso RaiSE para la definición de requisitos y el alcance de un proyecto, basándose en la metodología observada y las herramientas utilizadas en las fases iniciales.

## Paso 0: Exploración Inicial de Alcances y Definición de Enfoque

**Propósito:** Establecer una comprensión preliminar del problema de negocio, los objetivos del proyecto, y las posibles soluciones técnicas, así como los métodos de trabajo.

**Actividades Clave:**

* **Reuniones de Descubrimiento:** Realizar sesiones de diálogo con los stakeholders clave para capturar el contexto del proyecto, los requisitos de alto nivel, y las restricciones iniciales.
  * **Referencia de Ejemplo:** `Reunión iniciada a las 2025_07_23 12_01 CST - Notas de Gemini.md` (como fuente de requisitos y aclaraciones iniciales).
* **Exploración de Enfoque Técnico:** Identificar las tecnologías principales (ej. Python, Jira API v3) y las consideraciones operacionales (ej. ejecución local, manejo de rate limits).
* **Definición de Métodos de Trabajo:** Acordar el enfoque para la coincidencia de datos (ej. matching por título) y el manejo de excepciones (ej. marcado de tareas no procesables).
* **Generación de Borradores con IA:** Utilizar herramientas de IA para generar un borrador inicial de los pasos de la tarea, sirviendo como punto de partida para la discusión.

## Paso 1: Creación del Documento de Requisitos del Proyecto (PRD)

**Propósito:** Formalizar los requisitos del proyecto, el alcance y las metas, utilizando la información recopilada en la fase de exploración.

**Actividades Clave:**

* **Consolidación de Información:** Extraer y estructurar los requisitos detallados y las explicaciones del proceso directamente de las transcripciones de las reuniones.
* **Uso de Plantilla Estándar:** Emplear una plantilla predefinida para asegurar la coherencia y exhaustividad del documento.
  * **Plantilla Utilizada:** `.raise/templates/solution/project_requirements.md`
* **Redacción del PRD:** Rellenar las secciones de la plantilla con la información pertinente, incluyendo:
  * Resumen del proyecto, problema de negocio, metas y métricas de éxito.
  * Identificación de stakeholders y usuarios objetivo.
  * Definición clara del alcance (dentro y fuera de él).
  * Detalle de requisitos funcionales y no funcionales.
  * Consideraciones sobre datos e integraciones.
  * Documentación de supuestos, restricciones, preguntas abiertas y riesgos.
* **Iteración y Refinamiento:** El PRD debe ser un documento vivo, sujeto a revisión y actualización a medida que se obtiene más claridad o los requisitos evolucionan.

## Paso 2: Creación del Agente Arquitecto

**Propósito:** Instanciar un agente con perfil de arquitecto para guiar la creación de la visión de la solución.

**Actividades Clave:**

* **Acción:** Utilizar un "agente de agentes" preexistente (ej., `Race Gemini prompt Engineer` en `race common/agents/Curent`) para instanciar el Agente Arquitecto.
* **Input:** Proporcionar el Documento de Requisitos del Proyecto (PRD) para enfocar su rol en la arquitectura de la solución.

## Paso 3: Creación de la Visión de Solución

**Propósito:** Desarrollar una visión de alto nivel de la solución que alinee los objetivos de negocio con el diseño técnico propuesto.

**Actividades Clave:**

* **Input:** Utilizar el Agente Arquitecto creado en el paso anterior.
* **Consolidación con PRD y Plantilla:** Proporcionar al Agente Arquitecto el PRD y una plantilla de Visión de Solución (ej., `.raise/templates/solution/solution-vision-template.md`) para generar el documento de Visión de Solución.

## Paso 4: Creación del Agente Tech Lead

**Propósito:** Generar un agente con perfil de Tech Lead para la creación del diseño técnico general.

**Actividades Clave:**

* **Acción:** Utilizar el "agente de agentes" para generar el Agente Tech Lead.
* **Input:** Proporcionar el PRD y la Visión de Solución como contexto principal.

## Paso 5: Generación del Diseño Técnico General (Tech Design)

**Propósito:** Crear un documento de diseño técnico de alto nivel que detalle la arquitectura, los componentes principales y las interacciones de la solución.

**Actividades Clave:**

* **Input:** Utilizar el Agente Tech Lead.
* **Contexto Completo:** Alimentar al agente con el PRD y la Visión de Solución.
* **Uso de Plantilla Estándar:** Emplear una plantilla predefinida para el diseño técnico (ej., `.raise/templates/tech/tech_design.md`).
* **Provisión de Contexto Técnico Específico:** Es crucial proporcionar documentación técnica adicional, como la de la API de Jira Cloud (v3) o plantillas de especificación de API, para asegurar que el diseño técnico sea preciso y no "invente" detalles de implementación.
* **Validación de Endpoints:** Revisar y validar los endpoints de la API sugeridos en el diseño técnico (ej. asegurarse de que se utilice JQL para obtener información del proyecto y que los métodos de actualización sean correctos).

## Paso 6: Definición de Reglas Específicas para la Generación de Código (con Agente de Reglas)

**Propósito:** Establecer directrices y estándares de codificación explícitos para el futuro agente de generación de código, asegurando la adherencia a las mejores prácticas del proyecto y el uso correcto de las tecnologías.

**Actividades Clave:**

* **Acción:** Desarrollar archivos `.mdc` que capturen las convenciones de Python y el uso de la API de Jira (ej. ejemplos de cómo interactuar con la API).
* **Uso de Plantillas de Reglas:** Emplear las plantillas de reglas disponibles (ej., las ubicadas en `.raise/templates/cursor-rules/`) para estructurar la creación de reglas de forma coherente.
* **Uso de Agente:** Emplear un agente de IA especializado en la creación de reglas (ubicado en la misma carpeta que el "agente de agentes", ej., `race common/agents/Curent`) para asistir en la formalización de estas directrices.
* **Consideración de la Experiencia Actual:** Reconocer que la creación de reglas detalladas para el código "campo verde" puede ser un desafío inicial sin código existente, enfocándose en lo fundamental.

## Paso 7: Generación del Agente Coder

**Propósito:** Crear el agente de IA encargado de la generación del código base del proyecto, capacitándolo con el contexto de diseño y las reglas de codificación.

**Actividades Clave:**

* **Acción:** Utilizar el "agente de agentes" para instanciar un agente con el rol de "Coder".
* **Input:** Proporcionar al agente Coder el Diseño Técnico General (Paso 5) y las Reglas de Codificación (Paso 6) para guiar su proceso de generación de código.
* **Preparación para la Implementación:** Este paso prepara al agente para la fase de implementación de código, la cual no fue parte de la conversación actual.

## Paso 8: Creación y Priorización de Features

**Propósito:** Definir y priorizar las funcionalidades (features) de la solución para establecer el alcance del Producto Mínimo Viable (MVP) y guiar el desarrollo.

**Actividades Clave:**

*   **Agente Involucrado:** Utilizar el Agente Tech Lead.
*   **Inputs:** Proporcionar al agente el Diseño Técnico General, el PRD y la Visión de Solución. El Diseño Técnico es el input principal para identificar las features.
*   **Uso de Plantilla Estándar:** Emplear la plantilla de priorización de features (`.raise/templates/solution/feature-prioritization-template.md`) para estructurar la evaluación.
*   **Proceso de Priorización:** El agente rellena la matriz de priorización, evaluando cada feature en función del valor de negocio, la necesidad del usuario y la complejidad técnica.
*   **Definición del MVP:** Con base en las puntuaciones, se selecciona el conjunto de features para la Fase 1 (MVP) y se establece una secuencia de implementación.

## Paso 8.5: Generación del Diseño Técnico por Feature

**Propósito:** Detallar la implementación técnica de una feature específica que ha sido priorizada, sirviendo como el puente entre el diseño de alto nivel y las historias de usuario.

**Actividades Clave:**

*   **Agente Involucrado:** Utilizar el Agente Tech Lead.
*   **Inputs:** Proporcionar al agente el Diseño Técnico General y el documento de Priorización de Features. Es crucial indicar qué feature específica se va a detallar.
*   **Uso de Plantilla Estándar:** Emplear la misma plantilla que el diseño técnico general (`.raise/templates/tech/tech_design.md`), pero enfocando el contenido exclusivamente en la feature seleccionada.
*   **Detalle Técnico:** El agente debe profundizar en los componentes, flujos de datos, contratos de API y lógica de negocio que son relevantes únicamente para esa feature.

## Paso 9: Sugerencia, Refinamiento y Creación de Historias de Usuario (HU)

**Propósito:** Desglosar el diseño técnico de una feature en historias de usuario más pequeñas y accionables, que servirán como base para el desarrollo, y formalizarlas en documentos individuales.

**Actividades Clave:**

* **Agente Involucrado:** Utilizar el Agente Coder.
* **Inputs:** Proporcionar al agente el Diseño Técnico de la Feature, el Diseño Técnico General de la Solución y el documento de Priorización de Features.
* **Generación de Sugerencias:** El agente genera un documento con sugerencias de historias de usuario.
* **Revisión y Refinamiento:** Revisar las sugerencias de historias de usuario generadas por el agente, detallando los elementos a mantener o quitar. Fusionar aquellas que sean muy pequeñas o poco concisas para optimizar el proceso.
* **Consideraciones de Configuración:** Decidir si ciertos detalles (ej., IDs de campos personalizados de Jira, variables de entorno) deben documentarse en las HU o ser manejados directamente en el código del script. Se prefiere definir en el script para elementos técnicos de bajo nivel que no requieran documentación de alto nivel.
* **Creación de Documentos de HU:** Para cada historia de usuario refinada, generar un documento individual de HU utilizando una plantilla específica (ej., `.raise/templates/backlog/user_story.md`).

## Paso 10: Generación del Plan de Implementación por Historia de Usuario

**Propósito:** Crear un plan detallado paso a paso para la implementación de cada historia de usuario, facilitando la ejecución del desarrollo.

**Actividades Clave:**

* **Agente Involucrado:** Se infiere el uso de un agente especializado en planificación o el Agente Coder con la instrucción adecuada.
* **Kata Utilizada:** Emplear una Kata específica para la generación de planes de implementación (ej., `L14` para planes de implementación).
* **Inputs:** Proporcionar los documentos de Historias de Usuario definidas.
* **Generación Individual:** El plan de implementación se genera por cada Historia de Usuario por separado.
* **Revisión:** Revisar el plan de implementación generado para asegurar que sea lógico, completo y que no incluya pasos irrelevantes (ej. pruebas unitarias si no aplican a la tarea).

## Paso 11: Desarrollo e Implementación

**Propósito:** Ejecutar el desarrollo del código basándose en el plan de implementación detallado.

**Actividades Clave:**

* **Acción:** Utilizar el plan de implementación generado para proceder con el desarrollo y codificación de la historia de usuario.
* **Agente Involucrado:** El Agente Coder puede asistir en esta fase, utilizando las reglas de código y el contexto de diseño.

### Refinamiento Continuo y Aclaraciones:

* Durante todo el proceso, se identificarán y aclararán detalles específicos de los requisitos, como los nombres exactos de los campos de Jira (ej. `roles que participan en el proyecto`, `tipo de plan vigente`) y los estados de las tareas a procesar (`vigente`).
* Se buscará la definición de acrónimos o nombres de roles específicos del negocio (ej. PM, nuevo requerimiento, ACPN).
* Se reconoce la importancia de documentar explícitamente las tecnologías utilizadas en el PRD para mejorar la claridad para los agentes y el equipo.
