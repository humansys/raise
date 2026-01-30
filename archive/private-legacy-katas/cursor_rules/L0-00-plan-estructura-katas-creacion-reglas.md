# Plan de Estructura para Katas de Creación de Reglas Cursor

Propondría la siguiente estructura, utilizando un enfoque jerárquico similar al que parece existir en tus Katas actuales:

**Kata Principal (Nivel 0 o 1):**

* **Nombre Propuesto**: `L0-XX-gestion-integral-reglas-cursor.md` o `L1-XX-proceso-establecimiento-reglas-cursor.md`
* **Propósito**: Orquestar el proceso completo de análisis de un repositorio y establecimiento del sistema de Reglas Cursor y su gobernanza.
* **Fases/Pasos Principales**:
  1. **Fase 0: Preparación y Configuración del Entorno del Agente**
     * Instrucciones para el agente sobre su rol (similar al `system_prompt` que hemos estado usando o la `guia_agente_extraccion_reglas.md`).
     * Acceso y comprensión de plantillas de reglas (`.raise/templates/cursor-rules/`).
     * Acceso y comprensión de plantillas de documentos de gobernanza (si creamos versiones genéricas como se discutió).
     * Referencia a la `guia_agente_extraccion_reglas.md` y al `2025-05-23_21-45-guía-para-reglas-de-repositorio-y-análisis-de-plantillas.md` (para el análisis de plantillas).
  2. **Fase 1: Análisis Inicial del Repositorio y Descubrimiento**
     * Sub-Kata: `L2-XX-analisis-exploratorio-repositorio.md`
     * Objetivo: Identificar tecnologías, estructura general, patrones arquitectónicos de alto nivel.
     * Resultado: Un documento de análisis preliminar o borrador inicial para `ai-rules-reasoning.md`.
  3. **Fase 2: Creación/Actualización de Documentos de Gobernanza Iniciales**
     * Sub-Kata: `L2-XX-inicializacion-gobernanza-reglas.md`
     * Objetivo: Crear (si no existen) o preparar los archivos:
       * `ai-rules-reasoning.md` (con la introducción y observaciones preliminares).
       * `[nombre-repo]-rules-index.md` (con la estructura de categorías inicial).
       * `[nombre-repo]-implementation-plan.md` (con las fases iniciales).
  4. **Fase 3: Extracción y Generación Iterativa de Reglas Específicas**
     * Este sería un bucle o una serie de llamadas a una Sub-Kata más granular.
     * Sub-Kata: `L2-XX-extraccion-generacion-regla-cursor.md` (esta se llamaría múltiples veces, una por cada regla o grupo de reglas identificadas).
     * *Nota: La ejecución de esta fase se beneficiará si las reglas de estándares generales y metodología RaiSE ya están conceptualmente presentes o son referenciadas.*
  5. **Fase 4: Establecimiento de Reglas Fundacionales y Meta-Reglas** (Nombre de la fase actualizado)
     * **Sub-Fase 4.1: Adopción/Adaptación de Reglas de Estándares Generales de Codificación**
        *   Sub-Kata: `L2-XX-establecimiento-estandares-codificacion-general.md`
        *   Objetivo: Revisar, adaptar (si es necesario) e instanciar la regla de estándares generales de codificación (ej. `001-general-coding-standards.mdc`).
     * **Sub-Fase 4.2: Adopción/Adaptación de Reglas de Metodología (RaiSE)**
        *   Sub-Kata: `L2-XX-establecimiento-reglas-metodologia-raise.md`
        *   Objetivo: Revisar, adaptar (si es necesario) e instanciar reglas clave de la metodología RaiSE (ej. `010-raise-methodology-overview.mdc`).
     * **Sub-Fase 4.3: Creación de Meta-Reglas Específicas del Proyecto**
        *   Sub-Kata: `L2-XX-creacion-meta-reglas-esenciales-proyecto.md`
        *   Objetivo: Crear `901-ia-rule-management.mdc` y `902-rule-precedence.mdc` específicas para el proyecto actual.
  6. **Fase 5: Revisión y Consolidación Final**
     * Verificación de la consistencia entre todas las reglas y documentos de gobernanza.
     * Generación de un resumen del estado del sistema de reglas.

**Sub-Katas (Nivel 2):**

1. **`L2-XX-analisis-exploratorio-repositorio.md`**
   * Pasos detallados para que el agente explore el código: `list_dir`, `read_file` de archivos clave (manifests, entrypoints, etc.), `grep_search` para tecnologías o patrones comunes.
   * Cómo documentar los hallazgos iniciales.
2. **`L2-XX-inicializacion-gobernanza-reglas.md`**
   * Pasos para crear la estructura de directorios (`.cursor/rules`, `.raise/docs/[nombre-repo]`).
   * Instrucciones para generar el contenido inicial de `ai-rules-reasoning.md`, `[nombre-repo]-rules-index.md` y `[nombre-repo]-implementation-plan.md` usando plantillas genéricas (si las creamos) o basándose en la estructura que ya definimos.
3. **`L2-XX-extraccion-generacion-regla-cursor.md`**
   * Esta es la kata "de trabajo" principal que se repetirá.
   * **Entrada**: Un área específica a analizar (ej. "Estándares de C#", "Patrón Repositorio", "Logging").
   * Pasos:
     1. **Análisis Detallado del Código Específico**: Enfocado en el área de entrada.
     2. **Creación del Documento de Análisis Específico**: (ej. `analysis-for-[nombre-regla].md`) dentro de `.raise/docs/[nombre-repo]/`.
     3. **Selección de Plantilla de Regla**: De `.raise/templates/cursor-rules/`.
     4. **Redacción de la Regla (`.mdc`)**: Incluyendo frontmatter y contenido.
     5. **Actualización de `ai-rules-reasoning.md`**: Añadir la sección para la nueva regla.
     6. **Actualización de `[nombre-repo]-rules-index.md`**: Añadir la entrada de la nueva regla.
     7. **Actualización de `[nombre-repo]-implementation-plan.md`**: Marcar la regla como completada.
4. **`L2-XX-establecimiento-estandares-codificacion-general.md`** (Nueva Sub-Kata)
    *   **Entrada**: Referencia a una regla de estándares de codificación general base (ej. la `001-general-coding-standards` original).
    *   Pasos:
        1.  Leer la regla base.
        2.  Evaluar su aplicabilidad directa al repositorio actual.
        3.  Realizar adaptaciones menores si son evidentes y necesarias.
        4.  Crear el archivo `.cursor/rules/001-general-coding-standards.mdc` (o el número que corresponda) en el repositorio destino.
        5.  Actualizar los documentos de gobernanza para esta regla.
5. **`L2-XX-establecimiento-reglas-metodologia-raise.md`** (Nueva Sub-Kata)
    *   **Entrada**: Referencia a reglas base de la metodología RaiSE (ej. `010-raise-methodology-overview` original).
    *   Pasos:
        1.  Leer las reglas base de RaiSE.
        2.  Evaluar su aplicabilidad.
        3.  Instanciar los archivos `.mdc` correspondientes en el repositorio destino.
        4.  Actualizar los documentos de gobernanza para estas reglas.
6. **`L2-XX-creacion-meta-reglas-esenciales-proyecto.md`** (Anteriormente L2-XX-creacion-meta-reglas-esenciales.md, renumerada)
   * Pasos específicos para adaptar y crear `901-ia-rule-management.mdc` y `902-rule-precedence.mdc` para el repositorio actual, usando las versiones que ya hemos creado como base/plantilla.
   * Incluye la actualización de los documentos de gobernanza para estas meta-reglas.

**Puntos Clave a Incluir en las Katas:**

* **Referencias Explícitas**:
  * A la `guia_agente_extraccion_reglas.md` (o el contenido equivalente que se generó).
  * Al análisis de plantillas de `2025-05-23_21-45-guía-para-reglas-de-repositorio-y-análisis-de-plantillas.md`.
  * A las plantillas en `.raise/templates/cursor-rules/`.
  * A las plantillas genéricas para los documentos de gobernanza (si decidimos crearlas).
* **Instrucciones para el Agente**: Claridad sobre qué herramientas usar (`list_dir`, `read_file`, `edit_file`, `grep_search`), qué buscar, y cómo estructurar la salida.
* **Criterios de "Hecho" (Definition of Done)** para cada Kata y sub-Kata.
* **Manejo de Casos donde Algo no Existe**: Por ejemplo, si un repositorio es muy pequeño y no tiene un patrón claro para "Servicios", la Kata debe guiar sobre cómo documentar esa ausencia o decidir no crear una regla.

**Consideraciones de los Archivos de Katas Existentes:**

* Los nombres `L0-XX`, `L1-XX`, `L2-XX`, `L3-XX` sugieren una jerarquía. Intentaré alinearme con eso.
* La granularidad de algunas Katas existentes (ej. `L2-01-interfaces-dominio-kata.md`, `L2-07-viewmodel-kata.md`) es similar a la que propongo para `L2-XX-extraccion-generacion-regla-cursor.md` (aplicada a un tema específico).
* Revisaré el formato interno de algunas de estas Katas para ver si hay una estructura común (ej. "Objetivo", "Pasos", "Entregables", "Herramientas") que podamos adoptar.
