# L2-03: Extracción y Generación Iterativa de Reglas Cursor Específicas

**Versión Kata**: 1.0
**Fecha**: {{YYYY-MM-DD}}
**Autor**: CursorRules-GPT
**Kata Principal Relacionada**: `L0-01-gestion-integral-reglas-cursor.md`

## 1. Propósito de la Sub-Kata

Esta Sub-Kata de Nivel 2 describe el proceso iterativo para identificar, definir, generar y documentar Reglas Cursor específicas para un repositorio, basándose en el análisis exploratorio y los documentos de gobernanza.

## 2. Alcance y Objetivos

*   Identificar un área o patrón específico del código que se beneficiaría de una Regla Cursor (basado en el análisis de `L2-01` y el plan de `L2-02`).
*   Definir el propósito, alcance, y contenido de la nueva regla.
*   Generar el archivo `.mdc` de la regla con el formato adecuado (front matter YAML y contenido Markdown).
*   Actualizar los documentos de gobernanza (`ai-rules-reasoning.md`, `[nombre-repo]-rules-index.md`, `[nombre-repo]-implementation-plan.md`) para reflejar la nueva regla.
*   Repetir este proceso para múltiples reglas según sea necesario.

## 3. Prerrequisitos

*   Haber completado la Sub-Kata `L2-01-analisis-exploratorio-repositorio.md` y `L2-02-inicializacion-gobernanza-reglas.md`.
*   Tener acceso a los documentos de gobernanza (`ai-rules-reasoning.md`, `[nombre-repo]-rules-index.md`, `[nombre-repo]-implementation-plan.md`).
*   Agente IA configurado con herramientas: `edit_file`, `read_file`, `grep_search`, `list_dir`.
*   Conocimiento del formato de las Reglas Cursor (`.mdc` con front matter YAML).
*   Acceso a plantillas de reglas si existen (ej. `template-specific-rule.md`).
*   El nombre del repositorio (`[nombre-repo]`) debe ser conocido.

## 4. Ciclo Iterativo de Creación de Reglas

Este proceso se repite para cada regla que se decida implementar.

### Paso 4.1: Identificación y Priorización de la Siguiente Regla

*   **Acción**: Consultar el `[nombre-repo]-implementation-plan.md` y el `ai-rules-reasoning.md` (sección de áreas potenciales) para seleccionar la próxima regla a desarrollar.
    *   Considerar la criticidad, impacto y facilidad de implementación.
    *   Si el plan aún no detalla reglas específicas, analizar las "Áreas Potenciales para Reglas Cursor" del informe de `L2-01` y seleccionar una.
*   **Observaciones a Registrar**: Nombre propuesto para la regla (ej. `200-clean-architecture.mdc`), breve justificación de su necesidad.

### Paso 4.2: Análisis Detallado para la Regla Específica

*   **Acción**: Realizar un análisis más profundo del código fuente enfocado en el área que cubrirá la regla.
    *   Utilizar `grep_search` para encontrar ejemplos y anti-ejemplos del patrón.
    *   Utilizar `read_file` para entender el contexto de esos ejemplos.
    *   Utilizar `list_dir` si es necesario para entender la ubicación de los archivos relevantes.
*   **Observaciones a Registrar**: Ejemplos de código, convenciones observadas, anti-patrones, puntos clave a incluir en la regla.
*   **Resultado Esperado**: Un documento de análisis específico para la regla (similar a `analysis-for-XXX-rule.md` que hemos generado anteriormente).
*   **Herramientas**: `grep_search`, `read_file`, `list_dir`, `edit_file` (para crear el documento de análisis).

### Paso 4.3: Definición y Diseño de la Regla

*   **Acción**: Basado en el análisis, definir:
    *   `name`: Nombre descriptivo de la regla.
    *   `description`: Breve descripción.
    *   `globs`: Patrones de archivo a los que aplicará la regla.
    *   Contenido en Markdown: Explicaciones claras, ejemplos de código (`Do's` y `Don'ts`).
    *   `tags`: Palabras clave relevantes.
    *   (Opcional) `related_rules`: Enlaces a otras reglas relacionadas.
*   **Consideraciones**: Utilizar plantillas de reglas si están disponibles y son adecuadas.

### Paso 4.4: Generación del Archivo de Regla (`.mdc`)

*   **Acción**: Crear el archivo `.cursor/rules/[nombre-regla].mdc` con el front matter YAML y el contenido Markdown definidos en el paso anterior.
    *   Asegurar la numeración correcta (ej. `110-`, `205-`) según la categoría y el orden deseado.
*   **Herramienta**: `edit_file`

### Paso 4.5: Actualización de Documentos de Gobernanza

*   **Acción**: Actualizar los siguientes documentos para reflejar la nueva regla:
    1.  **`ai-rules-reasoning.md`**: Añadir una subsección bajo "Catálogo de Reglas Generadas y su Razonamiento" que detalle:
        *   El nombre de la regla.
        *   El razonamiento detrás de su creación (resumen del análisis del Paso 4.2).
        *   El impacto esperado de la regla.
    2.  **`[nombre-repo]-rules-index.md`**: Añadir la regla a la tabla correspondiente de su categoría, con su nombre, un enlace al archivo `.mdc` y una breve descripción.
    3.  **`[nombre-repo]-implementation-plan.md`**: Marcar la regla como "Implementada" o "En Progreso" en la Fase 2. Añadir una entrada si no estaba explícitamente listada.
*   **Herramienta**: `edit_file`

### Paso 4.6: Verificación y Pruebas (Conceptual)

*   **Acción**: (Este paso es más conceptual para el agente en este contexto, pero importante en la práctica humana) Verificar que la regla se activa en los archivos correctos y que la guía proporcionada es la esperada.
    *   En un entorno real, esto implicaría probar la regla con el asistente de IA en Cursor.
*   **Observaciones a Registrar**: Cualquier ajuste necesario a la regla después de la verificación.

### Paso 4.7: Iteración

*   **Acción**: Volver al Paso 4.1 para la siguiente regla, hasta que se cubran las reglas planificadas o se decida detener el proceso.

## 5. Entregables de esta Sub-Kata (por cada iteración)

*   Un nuevo archivo de regla `.cursor/rules/[nombre-regla].mdc`.
*   Un documento de análisis para la regla específica (ej. `.raise/docs/[nombre-repo]/analysis-for-[nombre-regla].md`).
*   Actualizaciones en `ai-rules-reasoning.md`, `[nombre-repo]-rules-index.md`, y `[nombre-repo]-implementation-plan.md`.

## 6. Consideraciones Adicionales

*   La granularidad de las reglas es clave: ni demasiado genéricas ni demasiado específicas.
*   Priorizar reglas que aborden los patrones más comunes o los problemas más críticos primero.
*   Es importante mantener la consistencia en el formato y estilo de todas las reglas.

## 7. Próximos Pasos (según Kata Principal)

*   Continuar iterando esta Sub-Kata (`L2-03`) para definir todas las reglas específicas del repositorio necesarias.
*   Una vez completada la generación de reglas específicas, proceder con la Fase 6 de `L0-01-gestion-integral-reglas-cursor.md`: Revisión, Pruebas y Despliegue Inicial. 