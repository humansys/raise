# 02: Diseño Técnico

## Artefactos Clave

*   **Diseño Técnico (Technical Design):** Detalla el "Cómo" implementar una Feature o Historia de Usuario compleja.
*   **Especificación de API (API Specification):** Define el contrato preciso de los endpoints de API.
*   **Especificación de Componente (Component Specification):** Define el contrato y comportamiento de componentes reutilizables (UI o backend).

## Proceso y Convenciones Estrictas

1.  **Creación de Diseño Técnico:** Para Features o Historias no triviales, crear un documento `TechDesign.md` usando la plantilla (`.raise/templates/tech_design.md`) y almacenarlo en la carpeta de la Feature correspondiente (`docs/features/<jira-id>-<feature-name>/`).
2.  **Especificaciones Detalladas:**
    *   Definir **APIs** nuevas o modificadas usando la plantilla `api_spec.md` y almacenarlas centralizadamente en `docs/api/`. Incluir el ID de JIRA relevante en el nombre de archivo (`<jira-id>-API-<method>-<path>.md`).
    *   Definir **Componentes** reutilizables usando la plantilla `component_spec.md` y almacenarlos centralizadamente en `docs/components/`. Incluir el ID de JIRA relevante en el nombre de archivo (`<jira-id>-Component-<NombreComponente>.md`).
3.  **Vinculación (Linking):**
    *   El Diseño Técnico **debe** enlazar a la Feature/Historia padre.
    *   El Diseño Técnico **debe** enlazar a las Especificaciones de API y Componente relevantes que detalla.
4.  **Contenido del Diseño Técnico:** Asegurar que el documento cubra aspectos clave como Arquitectura, Flujo de Datos, Contratos API (o enlaces a specs), Modelo de Datos, Algoritmos Clave, Seguridad y **Alternativas Consideradas**.
5.  **Claridad para la IA:** El objetivo es proporcionar suficiente detalle técnico estructurado para que los agentes de IA puedan entender el diseño y asistir en la implementación de forma fiable. 