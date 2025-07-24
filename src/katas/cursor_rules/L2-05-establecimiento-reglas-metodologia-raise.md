# L2-05: Establecimiento de Reglas de Metodología RaiSE

**Versión Kata**: 1.0
**Fecha**: {{YYYY-MM-DD}}
**Autor**: CursorRules-GPT
**Kata Principal Relacionada**: `L0-01-gestion-integral-reglas-cursor.md`

## 1. Propósito de la Sub-Kata

Esta Sub-Kata de Nivel 2 detalla los pasos para crear e implementar la Regla Cursor que introduce y refuerza los principios de la Metodología RaiSE (Reliable AI Software Engineering) dentro del proyecto. Esta regla guía al asistente de IA para operar de acuerdo con los principios de RaiSE.

## 2. Alcance y Objetivos

*   Adaptar el contenido de un documento de visión general de la metodología RaiSE (como `010-raise-methodology-overview` proporcionado por el usuario) al formato de una Regla Cursor.
*   Generar el archivo `.mdc` para esta regla (ej. `010-raise-methodology-overview.mdc`).
*   Asegurar que la regla tenga un `glob` global o apropiado para su aplicación.
*   Actualizar los documentos de gobernanza para reflejar la creación de esta regla metodológica.

## 3. Prerrequisitos

*   Haber completado la Sub-Kata `L2-02-inicializacion-gobernanza-reglas.md`.
*   Tener acceso al contenido del documento de la metodología RaiSE (ej. el contenido de `010-raise-methodology-overview` que el usuario ya ha proporcionado en las `required_instructions`).
*   Agente IA configurado con la herramienta `edit_file`.
*   Conocimiento del formato de las Reglas Cursor (`.mdc` con front matter YAML).
*   El nombre del repositorio (`[nombre-repo]`) debe ser conocido.

## 4. Pasos Detallados para la Creación de la Regla

### Paso 4.1: Obtención y Adaptación del Contenido de la Metodología

*   **Acción**: Localizar y revisar el documento de la metodología RaiSE proporcionado por el usuario.
*   **Adaptación**: Formatear el contenido para que sea una guía clara y accionable para el asistente de IA. Esto podría incluir:
    *   Enfocarse en la sección "Guía para la IA" o extraer los puntos más relevantes para la interacción con la IA.
    *   Asegurar que los principios clave sean fácilmente comprensibles por la IA.
    *   Resumir o refrasear para concisión y claridad en el contexto de una regla.
*   **Observaciones a Registrar**: Contenido final adaptado para la regla.

### Paso 4.2: Definición del Front Matter de la Regla

*   **Acción**: Definir los campos del front matter para la regla `010-raise-methodology-overview.mdc` (o un nombre similar).
    *   `name`: "Visión General de la Metodología RaiSE"
    *   `description`: "Introduce los conceptos y principios clave del framework RaiSE para guiar al asistente de IA."
    *   `globs`: `["**/*"]` (Generalmente, esta es una guía aplicable a toda interacción).
    *   `tags`: `["metodologia", "raise", "principios", "core"]`
    *   `order`: `010` (Para asegurar que se cargue después de los estándares generales pero antes de reglas más específicas).
*   **Consideraciones**: El `order` es importante para que las reglas base se establezcan correctamente.

### Paso 4.3: Generación del Archivo de Regla (`010-raise-methodology-overview.mdc`)

*   **Acción**: Crear el archivo `.cursor/rules/010-raise-methodology-overview.mdc` (o el nombre definido) con el front matter YAML y el contenido Markdown adaptado.
*   **Herramienta**: `edit_file`

### Paso 4.4: Actualización de Documentos de Gobernanza

*   **Acción**: Actualizar los siguientes documentos para reflejar la nueva regla metodológica:
    1.  **`ai-rules-reasoning.md`**: Añadir una entrada bajo "Catálogo de Reglas Generadas y su Razonamiento":
        *   Nombre de la regla: `010-raise-methodology-overview.mdc`.
        *   Razonamiento: Explicar que esta regla formaliza la metodología de trabajo con la IA (RaiSE) para asegurar que el asistente colabore de manera efectiva y alineada con los principios del proyecto.
        *   Impacto: Guía el comportamiento general del asistente de IA en todas sus interacciones.
    2.  **`[nombre-repo]-rules-index.md`**: Añadir la regla a la categoría "Principios Fundamentales y Metodología (000-099)", con su nombre, enlace y descripción.
    3.  **`[nombre-repo]-implementation-plan.md`**: Marcar la creación de esta regla como un paso clave en la "Fase 3: Establecimiento de Reglas Fundacionales y Meta-Reglas".
*   **Herramienta**: `edit_file`

## 5. Entregables de esta Sub-Kata

*   Archivo `.cursor/rules/010-raise-methodology-overview.mdc` creado.
*   Actualizaciones en `ai-rules-reasoning.md`, `[nombre-repo]-rules-index.md`, y `[nombre-repo]-implementation-plan.md`.

## 6. Consideraciones Adicionales

*   Esta regla, junto con los estándares generales de codificación, forma la base del comportamiento esperado del asistente de IA.
*   El contenido debe ser claro y conciso para ser interpretado correctamente por la IA.

## 7. Próximos Pasos (según Kata Principal)

*   Proceder con la Fase 4 de `L0-01-gestion-integral-reglas-cursor.md`, invocando la Sub-Kata `L2-06-establecimiento-meta-reglas-fundamentales.md` para crear las meta-reglas. 