# Proceso de Reconstrucción de Arquitectura de Software (SAR) con Katas Guiados

Este directorio contiene un conjunto de templates y Katas diseñados para guiar el proceso de Reconstrucción de Arquitectura de Software (SAR) de un repositorio .NET C# existente, con un enfoque en los principios de Clean Code y Clean Architecture. El objetivo es generar una documentación exhaustiva y coherente que sirva como base de conocimiento tanto para desarrolladores humanos como para asistentes de IA (como el "DotNet Clean Architect Analyzer").

## 1. Documentos SAR (Templates)

Los siguientes templates Markdown se utilizan para capturar los hallazgos del análisis:

1.  **`resumen_repositorio.md`**: Punto de entrada y resumen general del repositorio y el análisis.
2.  **`descripcion_general_arquitectura.md`**: Visión de alto nivel de la arquitectura del sistema.
3.  **`informe_analisis_codigo_limpio.md`**: Evaluación detallada de la adherencia a los principios de Clean Code.
4.  **`informe_analisis_arquitectura_limpia.md`**: Evaluación de la adherencia a los principios de Clean Architecture.
5.  **`informe_desglose_componentes.md`**: Documentación detallada de los principales proyectos y módulos.
6.  **`informe_mapa_dependencias.md`**: Visualización y descripción de las dependencias del sistema.
7.  **`recomendaciones_refactorizacion.md`**: Lista consolidada de sugerencias para mejorar el código base.

## 2. Katas SAR por Capa Arquitectónica

Para guiar el llenado de estos documentos de manera sistemática, se proporcionan los siguientes Katas (ubicados en `raise-ai/.raise/katas/`):

*   `raise-kata-sar-capa-dominio.md`
*   `raise-kata-sar-capa-aplicacion.md`
*   `raise-kata-sar-capa-infraestructura.md`
*   `raise-kata-sar-capa-presentacion.md`

Estos Katas se enfocan en el análisis detallado de cada capa arquitectónica identificada comúnmente en aplicaciones que siguen principios de diseño limpio.

## 3. Proceso Recomendado para el Uso de los Katas y Templates SAR

Se recomienda seguir un proceso iterativo y estructurado para la reconstrucción y documentación arquitectónica:

### Fase 0: Preparación y Planificación Inicial

1.  **Definir Alcance:** Identificar el repositorio a analizar y el objetivo del análisis (documentación completa, análisis de un área crítica, etc.).
2.  **(Opcional pero Recomendado) Crear Plan de Análisis General:**
    *   Se sugiere crear un documento `PLAN_ANALISIS_ARQUITECTONICO_[NombreRepo].md` en una ubicación designada (ej., `[RutaAlRepositorio]/.raise/analysis/`).
    *   Este plan debe listar los 7 documentos SAR como hitos principales y desglosar sub-tareas o áreas de enfoque para cada uno. Servirá como un checklist maestro para rastrear el progreso.
3.  **Familiarización Inicial:** El practicante y el Asistente IA (DotNetCleanArchitectAnalyzer) deben tener acceso al repositorio y a estos templates/Katas.

### Fase 1: Documentación Fundamental Inicial

1.  **Generar `resumen_repositorio.md`:**
    *   Utilizar las herramientas del Asistente IA para escanear la estructura básica del repositorio (`.sln`, `.csproj`), identificar el stack tecnológico y listar los proyectos.
    *   Poblar las secciones correspondientes del template `resumen_repositorio.md`.
    *   Marcar como completado en el `PLAN_ANALISIS_ARQUITECTONICO`.
2.  **Generar Borrador Inicial de `descripcion_general_arquitectura.md`:**
    *   Con base en el análisis inicial de la estructura de proyectos y sus nombres, el Asistente IA debe proponer una identificación preliminar del estilo arquitectónico y las principales capas.
    *   Poblar las secciones iniciales de `descripcion_general_arquitectura.md`.
    *   Este documento se refinará a medida que se completen los Katas por capa.
    *   Marcar como completado (borrador inicial) en el `PLAN_ANALISIS_ARQUITECTONICO`.

### Fase 2: Ejecución de Katas por Capa Arquitectónica

Se recomienda abordar las capas en el siguiente orden, ya que el análisis de una capa a menudo informa al siguiente:

1.  **Capa de Dominio (`raise-kata-sar-capa-dominio.md`):**
    *   Seguir los pasos del Kata para identificar entidades, servicios de dominio, interfaces y evaluar la adherencia a principios como la Regla de Dependencia (sin dependencias hacia afuera) y la independencia de frameworks.
    *   Poblar las secciones relevantes de TODOS los documentos SAR (`informe_analisis_codigo_limpio.md` para el código de dominio, `informe_analisis_arquitectura_limpia.md` para principios específicos del dominio, `informe_desglose_componentes.md` para proyectos de dominio, etc.).
2.  **Capa de Aplicación (`raise-kata-sar-capa-aplicacion.md`):**
    *   Analizar casos de uso, servicios de aplicación, DTOs, y cómo esta capa orquesta la lógica de negocio interactuando con el Dominio y definiendo interfaces para la Infraestructura.
    *   Actualizar todos los documentos SAR con los hallazgos específicos de esta capa.
3.  **Capa de Infraestructura (`raise-kata-sar-capa-infraestructura.md`):**
    *   Examinar implementaciones de repositorios, clientes de servicios externos, y otros componentes que interactúan con elementos fuera del núcleo de la aplicación.
    *   Verificar cómo se implementan las interfaces de Aplicación/Dominio y se encapsulan los detalles del framework.
    *   Actualizar todos los documentos SAR.
4.  **Capa de Presentación (`raise-kata-sar-capa-presentacion.md`):**
    *   Analizar controladores API/MVC, puntos de entrada (Worker Services), manejo de solicitudes/respuestas, validación, y cómo interactúa con la Capa de Aplicación.
    *   Actualizar todos los documentos SAR.

**Durante la ejecución de cada Kata por capa:**
*   Utilizar activamente el `PLAN_ANALISIS_ARQUITECTONICO` para marcar tareas específicas como completadas.
*   El practicante guía al Asistente IA, solicitando análisis específicos, validando hallazgos y dirigiendo la creación de contenido para los documentos SAR.
*   Es un proceso iterativo. Los hallazgos en una capa pueden requerir revisar o refinar secciones de documentos relacionados con capas analizadas previamente.

### Fase 3: Consolidación y Finalización

1.  **Generar `recomendaciones_refactorizacion.md`:**
    *   Una vez analizadas todas las capas, consolidar todos los problemas identificados y las sugerencias de mejora en este documento.
    *   Priorizar las recomendaciones según su impacto y complejidad estimada.
2.  **Revisión Integral de Documentos SAR:**
    *   El practicante debe realizar una lectura completa de todos los documentos generados para asegurar la coherencia, corrección y completitud de la información.
    *   Verificar que todos los enlaces entre documentos sean correctos.
3.  **Verificación Final del Plan de Análisis:**
    *   Asegurar que todas las tareas en `PLAN_ANALISIS_ARQUITECTONICO` estén marcadas como completadas.

## 4. Rol del Asistente IA (DotNetCleanArchitectAnalyzer)

*   **Análisis de Código:** Utiliza sus capacidades conceptuales para escanear, parsear y analizar el código C#.
*   **Inferencia de Patrones y Principios:** Ayuda a identificar estilos arquitectónicos, capas, patrones de diseño, `code smells` y violaciones de principios.
*   **Generación de Contenido:** Propone texto, ejemplos de código y diagramas (ej., Mermaid) para poblar los templates SAR, siguiendo las instrucciones del practicante.
*   **Navegación y Búsqueda:** Utiliza herramientas como `read_file`, `list_dir`, `grep_search` para obtener información del repositorio.

## 5. Resultados Esperados

Al finalizar este proceso, se dispondrá de un conjunto completo y coherente de documentos de Reconstrucción Arquitectónica de Software que:
*   Describen la arquitectura actual del sistema.
*   Evalúan su calidad en términos de Clean Code y Clean Architecture.
*   Identifican áreas de mejora y recomendaciones concretas.
*   Sirven como una valiosa base de conocimiento para el mantenimiento, evolución y onboarding de nuevos miembros al equipo (humanos o IA).

Este proceso busca ser una guía flexible. Adáptelo según las necesidades específicas de su proyecto y la complejidad del repositorio a analizar. 