# L2-04: Establecimiento de Reglas de Estándares Generales de Codificación

**Versión Kata**: 1.0
**Fecha**: {{YYYY-MM-DD}}
**Autor**: CursorRules-GPT
**Kata Principal Relacionada**: `L0-01-gestion-integral-reglas-cursor.md`

## 1. Propósito de la Sub-Kata

Esta Sub-Kata de Nivel 2 detalla los pasos para crear e implementar la Regla Cursor fundamental que establece los estándares generales de codificación para un proyecto. Esta regla sirve como base para todas las demás y asegura una calidad y consistencia mínimas en el código generado por la IA.

## 2. Alcance y Objetivos

*   Adaptar el contenido de un documento de estándares de codificación general (como `001-general-coding-standards` proporcionado por el usuario) al formato de una Regla Cursor.
*   Generar el archivo `.mdc` para esta regla (ej. `001-general-coding-standards.mdc`).
*   Asegurar que la regla tenga un `glob` global para aplicar a todos los archivos relevantes.
*   Actualizar los documentos de gobernanza para reflejar la creación de esta regla fundacional.

## 3. Prerrequisitos

*   Haber completado la Sub-Kata `L2-02-inicializacion-gobernanza-reglas.md`.
*   Tener acceso al contenido del documento de estándares generales de codificación (ej. el contenido de `001-general-coding-standards` que el usuario ya ha proporcionado en las `required_instructions`).
*   Agente IA configurado con la herramienta `edit_file`.
*   Conocimiento del formato de las Reglas Cursor (`.mdc` con front matter YAML).
*   El nombre del repositorio (`[nombre-repo]`) debe ser conocido.

## 4. Pasos Detallados para la Creación de la Regla

### Paso 4.1: Obtención y Adaptación del Contenido de Estándares

*   **Acción**: Localizar y revisar el documento de estándares generales de codificación proporcionado por el usuario (se asume que está disponible como parte de las `required_instructions` del agente o es proporcionado explícitamente).
*   **Adaptación**: Formatear el contenido para que sea adecuado para una Regla Cursor. Esto puede implicar:
    *   Asegurar que el lenguaje sea directivo y claro para la IA.
    *   Resumir puntos si es necesario para concisión, manteniendo la esencia.
    *   Organizarlo con encabezados Markdown.
*   **Observaciones a Registrar**: Contenido final adaptado para la regla.

### Paso 4.2: Definición del Front Matter de la Regla

*   **Acción**: Definir los campos del front matter para la regla `001-general-coding-standards.mdc` (o un nombre similar).
    *   `name`: "Estándares Generales de Codificación"
    *   `description`: "Regla fundamental que establece los principios y convenciones básicas de codificación para el proyecto."
    *   `globs`: `["**/*"]` (o un glob más específico si se desea, aunque generalmente estas reglas son globales).
    *   `tags`: `["general", "standards", "core", "best-practices"]`
    *   `order`: `001` (para asegurar que se cargue primero o muy temprano).
*   **Consideraciones**: El `order` es crucial para las reglas base.

### Paso 4.3: Generación del Archivo de Regla (`001-general-coding-standards.mdc`)

*   **Acción**: Crear el archivo `.cursor/rules/001-general-coding-standards.mdc` (o el nombre definido) con el front matter YAML y el contenido Markdown adaptado.
*   **Herramienta**: `edit_file`

### Paso 4.4: Actualización de Documentos de Gobernanza

*   **Acción**: Actualizar los siguientes documentos para reflejar la nueva regla fundacional:
    1.  **`ai-rules-reasoning.md`**: Añadir una entrada bajo "Catálogo de Reglas Generadas y su Razonamiento":
        *   Nombre de la regla: `001-general-coding-standards.mdc`.
        *   Razonamiento: Explicar que esta regla codifica las directrices básicas de codificación del equipo/proyecto para asegurar consistencia y calidad desde el nivel más fundamental.
        *   Impacto: Establece la línea base para toda la generación y modificación de código.
    2.  **`[nombre-repo]-rules-index.md`**: Añadir la regla a la categoría "Principios Fundamentales y Metodología (000-099)", con su nombre, enlace y descripción.
    3.  **`[nombre-repo]-implementation-plan.md`**: Marcar la creación de esta regla como un paso clave en la "Fase 3: Establecimiento de Reglas Fundacionales y Meta-Reglas".
*   **Herramienta**: `edit_file`

## 5. Entregables de esta Sub-Kata

*   Archivo `.cursor/rules/001-general-coding-standards.mdc` creado.
*   Actualizaciones en `ai-rules-reasoning.md`, `[nombre-repo]-rules-index.md`, y `[nombre-repo]-implementation-plan.md`.

## 6. Consideraciones Adicionales

*   Esta regla es crítica y debe ser una de las primeras en establecerse en un nuevo proyecto.
*   El contenido debe ser revisado cuidadosamente para asegurar que refleja fielmente las intenciones del equipo.

## 7. Próximos Pasos (según Kata Principal)

*   Proceder con la Sub-Kata `L2-05-establecimiento-reglas-metodologia-raise.md` para establecer las reglas sobre la metodología RaiSE.
*   Luego, continuar con la creación de Meta-Reglas (`L2-06` y `L2-07`) o volver al ciclo iterativo de `L2-03` si aún quedan reglas específicas por definir. 