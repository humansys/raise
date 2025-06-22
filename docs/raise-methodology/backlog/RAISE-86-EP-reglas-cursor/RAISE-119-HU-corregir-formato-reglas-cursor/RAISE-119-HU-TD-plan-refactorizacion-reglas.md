# Plan de Implementación: Refactorización de Reglas de Cursor (RAISE-119)

**Historia de Usuario:** [RAISE-119 Corregir Formato y Cabeceras Faltantes en Reglas de Cursor](./RAISE-119-HU-corregir-formato-reglas.md)

**Objetivo General:** Refactorizar todas las reglas de cursor existentes para que utilicen el formato estándar de cabecera YAML front matter y contengan los campos requeridos (`name`, `description`, `globs`), asegurando así su correcta carga y aplicación por parte de Cursor IDE.

---

### **Fase 1: Refactorización Individual de Reglas**

**Meta:** Convertir cada regla existente al formato YAML estándar y definir los metadatos necesarios.

*   **Para cada archivo `.mdc` listado abajo:**
    *   [ ] Convertir el encabezado no estándar (`Rule Name: ...`, `Description: ...`) a una cabecera YAML (`---
      ...
      ---`).
    *   [ ] Añadir el campo `name` con el valor del `Rule Name` original.
    *   [ ] Añadir el campo `description` con el valor de la `Description` original.
    *   [ ] **Definir `globs` apropiados:** Analizar el contenido de la regla y determinar los patrones de archivo (`*.py`, `**/tests/*.py`, `*.md`, etc.) a los que debe aplicarse. Ser lo más específico posible.
    *   [ ] (Opcional) Añadir `tags` relevantes.
    *   [ ] (Opcional) Añadir `related` si aplica.

*   **Reglas a Refactorizar:**
    *   [x] `010-monorepo-python-tests.mdc`
    *   [x] `010-python-version.mdc`
    *   [x] `020-external-config.mdc`
    *   [x] `020-python-naming-conventions.mdc`
    *   [x] `021-yaml-parsing.mdc`
    *   [x] `022-validate-config.mdc`
    *   [x] `030-cli-parsers.mdc`
    *   [x] `030-python-mocking-guidelines.mdc`
    *   [x] `040-security-credentials.mdc`
    *   [x] `050-dependency-updates.mdc`
    *   [x] `060-commit-guidelines.mdc`
    *   [x] `061-jira-issue-types.mdc`
    *   [x] `100-pydantic-models.mdc`
    *   [x] `101-pydantic-validators.mdc`
    *   [x] `110-dataclasses-for-results.mdc`
    *   [x] `200-api-client-libs.mdc`
    *   [x] `201-api-client-wrappers.mdc`
    *   [x] `210-api-batch-operations.mdc`
    *   [x] `211-api-explicit-data-request.mdc`
    *   [x] `220-api-retries.mdc`
    *   [x] `221-api-specific-error-codes.mdc`
    *   [x] `300-complex-data-structures.mdc`
    *   [x] `310-modularity.mdc`
    *   [x] `400-type-hints.mdc`
    *   [x] `401-pep8-style.mdc`
    *   [x] `405-monorepo-structure.mdc`
    *   [x] `406-monorepo-poetry-config.mdc`
    *   [x] `407-monorepo-execution.mdc`
    *   [x] `410-structured-logging.mdc`
    *   [x] `411-logging-sensitive-data.mdc`
    *   [x] `420-broad-exception-handling.mdc`
    *   [x] `500-unit-testing.mdc`
    *   [x] `510-integration-testing-mocks.mdc`
    *   [x] `600-python-project-documentation.mdc`
    *   [x] `610-standard-output-formats.mdc`
    *   [x] `900-rule-authoring-guidelines.mdc`
    *   [ ] `920-memory-tool-usage-guide.mdc`

---

### **Fase 2: Verificación y Validación**

**Meta:** Asegurar que todas las reglas refactorizadas se cargan y aplican correctamente en el entorno de desarrollo.

*   [x] **Verificar Regla `061-jira-issue-types.mdc`:** Se ha verificado que su cabecera YAML está completa y los `globs` son adecuados.
*   [ ] **Validación en Cursor IDE:**
    *   Abrir archivos de ejemplo que coincidan con los `globs` definidos para un subconjunto de reglas refactorizadas.
    *   Verificar que la regla esperada se carga automáticamente (aparece en la lista de reglas adjuntas).
    *   Verificar que el contenido de la regla está disponible en el contexto del asistente IA.
    *   Confirmar que no aparecen advertencias del IDE relacionadas con el formato de las reglas.
*   [x] **Revisión Cruzada:** Se ha completado la revisión de todas las cabeceras YAML para asegurar la consistencia y la presencia de los campos requeridos (`name`, `description`, `globs`).
*   [ ] **Commit y Merge:** Integrar los cambios en el control de versiones una vez validados.

**Notas adicionales:**
* Se ha detectado que el archivo `411-logging-sensitive-data.mdc` existe pero está vacío. Se ha añadido la cabecera YAML pero no se ha generado contenido.
* El archivo `920-memory-tool-usage-guide.mdc` mencionado en la lista no existe en el workspace.

---

Este plan divide la refactorización en tareas manejables por regla, culminando en una fase de validación para asegurar el cumplimiento del objetivo. 