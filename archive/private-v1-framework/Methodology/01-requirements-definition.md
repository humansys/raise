# 01: Definición de Requisitos

## Artefactos Clave

*   **Capacidades (Capabilities):** Comportamientos de alto nivel de la solución.
*   **Características (Features):** Entregables de valor que realizan una capacidad.
*   **Historias de Usuario (User Stories):** Requisitos detallados para implementar una característica.

## Proceso y Convenciones Estrictas

1.  **Plantillas Obligatorias:** Utilizar **exclusivamente** las plantillas definidas en `.raise/templates/` (`capability.md`, `feature.md`, `user_story.md`) para cada tipo de artefacto.
2.  **Identificador JIRA Mandatorio:** Todos los nombres de archivo **deben** comenzar con el ID de JIRA asociado (ej. `PROJ-123-Feature-nombre.md`). Obtener el ID del usuario si no se proporciona.
3.  **Ubicación Estricta:** Almacenar los artefactos **únicamente** en las ubicaciones designadas:
    *   Capacidades: `docs/capabilities/`
    *   Features y sus Historias/Diseños: `docs/features/<jira-id-feature>-<nombre-feature>/`
4.  **Hipótesis de Beneficio Clara:** Definir explícitamente el valor esperado (Benefit Hypothesis) en Capacidades y Features.
5.  **Criterios de Aceptación (AC):**
    *   Para Historias de Usuario: Escribir AC usando el formato **BDD (Gherkin: Dado/Cuando/Entonces)**.
    *   Para Features/Capacidades: Definir AC medibles y de alto nivel.
6.  **Enfoque:** Centrarse en definir claramente el "Qué" se necesita y el "Por qué" (valor de negocio), preparando el contexto para el diseño técnico.
7.  **Verificación:** Antes de crear un archivo, verificar que no exista uno con el mismo nombre exacto en la ubicación destino. 