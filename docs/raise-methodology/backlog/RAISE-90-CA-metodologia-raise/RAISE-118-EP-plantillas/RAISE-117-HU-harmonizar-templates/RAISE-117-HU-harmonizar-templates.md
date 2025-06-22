# Historia de Usuario: RAISE-117 - Armonizar Templates de Preventa RaiSE

**ID Jira:** [RAISE-117](<Link a Jira si está disponible>)
**Funcionalidad/Epic Superior:** [RAISE-118 Plantillas](../RAISE-118-EP-plantillas.md)
**Capacidad Superior:** [RAISE-90 Metodología RaiSE](../../RAISE-90-CA-metodologia-raise.md)
**Estado:** Pendiente <!-- O el estado actual -->

---

## Descripción

**Como** miembro del equipo RaiSE (preventa, desarrollador, agente AI),
**Quiero** que los templates de documentos de preventa (`project_requirements.md`, `solution-vision-template.md`, `feature-prioritization-template.md`, `tech_design.md`, `statement_of_work.md`, `estimation_roadmap.md`, y el nuevo `RaiSE-terminology.md`) estén armonizados en terminología, estructura y trazabilidad,
**Para** mejorar la coherencia, facilitar su uso manual y automático (por agentes AI), optimizar los workflows agénticos y manuales, y asegurar la alineación con los principios RaiSE.

## Criterios de Aceptación

Los siguientes criterios deben cumplirse para considerar esta historia completada, basados en las fases del plan de implementación:

**CA1: Armonización Fundacional Completa (Fase 1)**
*   [ ] **Glosario Creado:** Existe un archivo `RaiSE-terminology.md` (ubicación a definir, posiblemente en `.raise/templates/docs/` o similar) que define términos estándar, mapeo ES/EN, jerarquías y formato de referencias a principios RaiSE.
*   [ ] **Terminología Coherente:** Todos los templates de preventa mencionados en la descripción han sido revisados y actualizados para usar consistentemente los términos definidos en el Glosario.
*   [ ] **Referencias Básicas:** Se ha definido e implementado una convención clara para los IDs de documento (ej., `PRD-XYZ`). Cada template incluye un campo (`Documentos Relacionados` o similar) al inicio para listar los IDs de documentos vinculados usando la convención definida.

**CA2: Trazabilidad y Mapeo Fortalecidos (Fase 2)**
*   [ ] **Mapeo PRD → Otros:** `project_requirements.md` incluye secciones explícitas para mapear requisitos a artefactos posteriores y criterios preliminares de priorización.
*   [ ] **Mapeo Vision ← PRD:** `solution-vision-template.md` incluye referencias explícitas a las secciones fuente del PRD en sus partes clave.
*   [ ] **Mapeo Prioritization ← Otros:** `feature-prioritization-template.md` incluye referencias a dependencias técnicas (Tech Design) e impacto estimado (Estimation) en su matriz.
*   [ ] **Mapeo Tech Design ← → Otros:** `tech_design.md` incluye referencias a actividades del SoW asociadas y consideraciones para la estimación.
*   [ ] **Mapeo SoW ← → Otros:** `statement_of_work.md` incluye referencias explícitas al detalle técnico (Tech Design), estimación detallada (Estimation Roadmap) y opcionalmente una matriz de trazabilidad de requisitos (vs PRD).
*   [ ] **Mapeo Estimation ← Otros:** `estimation_roadmap.md` incluye referencias a la prioridad (Feature Prioritization) y vinculación con el modelo de costos (SoW).

**CA3: Preparación para Workflow Agéntico (Fase 3)**
*   [ ] **Metadatos YAML:** Todos los templates incluyen una cabecera YAML estándar al inicio con metadatos clave definidos (título, proyecto, versión, fecha, cliente, autor, documentos relacionados, etc.).
*   [ ] **Sintaxis Estructurada:** Se ha definido e implementado una sintaxis clara (ej., `@metric:[ID]{Valor}`, `@requirement:[ID]{Tipo}`) para marcar datos específicos inline en los templates, facilitando la extracción automatizada.
*   [ ] **Instrucciones Agente (Opcional):** Se han añadido comentarios específicos (`<!-- Agent Instructions: ... -->`) si se consideran necesarios para guiar a los agentes AI.

**CA4: Revisión y Validación (Fase 4)**
*   [ ] **Revisión Cruzada:** Se ha realizado una revisión completa de todos los templates modificados para asegurar la consistencia terminológica y de referencias.
*   [ ] **Simulación de Flujo:** Se ha simulado manualmente el flujo de generación de documentos (PRD → SoW) usando los templates actualizados, validando que la información fluye correctamente.
*   [ ] **Feedback e Iteración:** Se ha recopilado feedback del equipo y se han realizado las iteraciones necesarias sobre los templates.

---

## Notas Adicionales

*   La ubicación exacta de `RaiSE-terminology.md` debe definirse.
*   Los enlaces a los archivos de Capacidad y Funcionalidad deben verificarse/ajustarse una vez que dichos archivos existan.
*   Considerar añadir enlaces directos a los templates específicos una vez estén en su ubicación final dentro del repositorio (ej., en `.raise/templates/docs/`). 