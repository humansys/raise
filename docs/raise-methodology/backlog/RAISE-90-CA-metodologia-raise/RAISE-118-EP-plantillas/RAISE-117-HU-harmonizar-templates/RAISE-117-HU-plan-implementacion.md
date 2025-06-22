# Plan de Implementación: Armonización de Templates RaiSE (RAISE-117)

**Historia de Usuario:** [RAISE-117 Harmonizar Templates](./RAISE-117-HU-harmonizar-templates.md)

**Objetivo General:** Mejorar la coherencia, claridad y trazabilidad de los templates de preventa para optimizar su uso en workflows agénticos y manuales, asegurando la alineación con los principios RaiSE.

---

### **Fase 1: Armonización Fundacional (Terminología y Trazabilidad Básica)**

**Meta:** Establecer un lenguaje común y referencias cruzadas básicas entre todos los documentos.

*   **1.1. Crear Glosario Compartido (`RaiSE-terminology.md`)**
    *   [x] Definir términos estándar (Funcionalidad, Requisito, Stakeholder, Objetivo, Métrica, etc.).
    *   [x] Incluir mapeo Español-Inglés para términos técnicos clave (Feature, Epic, Story Point, Velocity, etc.).
    *   [x] Establecer jerarquías claras (ej., Stakeholder > Usuario > Persona; Capacidad > Funcionalidad > Historia).
    *   [x] Definir formato estándar para referencias a principios RaiSE (ej., `[RaiSE: Human-Centric]`).
*   **1.2. Refactorizar Templates para Coherencia Terminológica**
    *   [x] Revisar y actualizar `project_requirements.md` usando términos del Glosario.
    *   [x] Revisar y actualizar `solution-vision-template.md` usando términos del Glosario.
    *   [x] Revisar y actualizar `feature-prioritization-template.md` usando términos del Glosario.
    *   [x] Revisar y actualizar `tech_design.md` usando términos del Glosario.
    *   [x] Revisar y actualizar `statement_of_work.md` usando términos del Glosario.
    *   [x] Revisar y actualizar `estimation_roadmap.md` usando términos del Glosario.
*   **1.3. Implementar Sistema Básico de Referencias Cruzadas**
    *   [x] Definir convención de ID para documentos (ej., PRD-XYZ, SOW-XYZ).
    *   [x] Añadir campo `Documentos Relacionados` al inicio de cada template para listar IDs vinculados.
    *   [x] Asegurar que las referencias existentes (ej., `Referencia PRD:` en SoW) usan la convención de ID.

---

### **Fase 2: Fortalecer Trazabilidad y Mapeo entre Documentos**

**Meta:** Crear vínculos explícitos y claros entre secciones específicas de documentos relacionados.

*   **2.1. Mejorar Mapeo PRD → Otros Documentos**
    *   [x] En `project_requirements.md`: Añadir sección "Mapeo a Artefactos Posteriores" (ej., tabla que vincula Requisitos Funcionales a potenciales elementos del SoW/Roadmap).
    *   [x] En `project_requirements.md`: Añadir sección "Criterios Preliminares de Priorización" (Inputs para `feature-prioritization-template.md`).
*   **2.2. Mejorar Mapeo Solution Vision ← PRD**
    *   [x] En `solution-vision-template.md`: Añadir referencias explícitas `(Fuente: PRD Sec X.Y)` en secciones clave (Problem Statement, Business Goals, User Impact, MVP Scope).
*   **2.3. Mejorar Mapeo Feature Prioritization ← Otros**
    *   [x] En `feature-prioritization-template.md`: Añadir columna "Dependencia Técnica Clave (Ref: Tech Design)" en la matriz.
    *   [x] En `feature-prioritization-template.md`: Añadir columna "Impacto Estimado Preliminar (Ref: Estimation)" en la matriz.
*   **2.4. Mejorar Mapeo Tech Design ← → Otros**
    *   [x] En `tech_design.md`: Añadir campo "Actividades SoW Asociadas (Ref: SoW Sec 3.2)" por componente/API.
    *   [x] En `tech_design.md`: Añadir sección "Consideraciones para Estimación (Input para `estimation_roadmap.md`)".
*   **2.5. Mejorar Mapeo SoW ← → Otros**
    *   [x] En `statement_of_work.md`: Añadir referencias `(Detalle Técnico: Tech Design Sec X)` en Actividades Principales (Sec 3.2).
    *   [x] En `statement_of_work.md`: Añadir referencia `(Estimación Detallada: Estimation Roadmap)` en Precio/Cronograma (Sec 9 / Sec 5).
    *   [x] En `statement_of_work.md`: Añadir matriz o sección "Trazabilidad de Requisitos (Entregable vs PRD Req.)" (opcional, para mayor rigor).
*   **2.6. Mejorar Mapeo Estimation Roadmap ← Otros**
    *   [x] En `estimation_roadmap.md`: Añadir columna/nota "Prioridad (Ref: Feature Prioritization)" en la tabla del Roadmap Proyectado (Sec 4).
    *   [x] En `estimation_roadmap.md`: Añadir sección "Vinculación con Modelo de Costos (Ref: SoW Sec 9)".

---

### **Fase 3: Preparación para Workflow Agéntico y Mejoras Estructurales**

**Meta:** Adaptar los templates para facilitar la extracción y generación automatizada de información.

*   **3.1. Introducir Metadatos Estructurados (YAML Headers)**
    *   [x] Definir conjunto estándar de metadatos (ej., `title`, `project_name`, `version`, `date`, `client`, `author`, `related_docs: [ID1, ID2]`).
    *   [x] Implementar cabecera YAML al inicio de todos los templates.
*   **3.2. Definir Sintaxis para Campos Clave Estructurados (Inline)**
    *   [x] Establecer una sintaxis clara para marcar datos específicos dentro del texto (ej., `@metric:[ID_Metrica]{Valor Objetivo}`, `@requirement:[ID_Req]{Tipo: Funcional}`). Investigar si Markdown extendido o comentarios HTML son viables.
    *   [x] Aplicar esta sintaxis a elementos críticos en `project_requirements.md` (Métricas, Requisitos, Stakeholders).
    *   [ ] Aplicar sintaxis similar en otros documentos para IDs, estimaciones, fechas clave, etc. *(Deferred/Optional for now)*
*   **3.3. Añadir Instrucciones Específicas para Agentes (Opcional)**
    *   [ ] Considerar añadir secciones `<!-- Agent Instructions: ... -->` en los templates para guiar la extracción/generación automática de secciones específicas. *(Skipped for now)*

---

### **Fase 4: Revisión y Validación**

**Meta:** Asegurar que los cambios son coherentes y efectivos.

*   [ ] Realizar una revisión cruzada de todos los templates modificados para verificar consistencia terminológica y de referencias.
*   [ ] Simular manually el flujo de generación de documentos (PRD → Vision → Prioritization → Tech Design → Estimation/Roadmap → SoW) usando los templates actualizados.
*   [ ] Validar que la información necesaria para cada paso fluye correctamente desde los documentos anteriores.
*   [ ] Recopilar feedback del equipo de preventa sobre la usabilidad y claridad de los nuevos templates.
*   [ ] Iterar sobre los templates basándose en la revisión y el feedback.

---

Este plan proporciona un enfoque estructurado para mejorar la suite de templates. Cada ítem del checklist representa una tarea concreta que puede ser asignada y cuyo progreso puede ser monitoreado. 