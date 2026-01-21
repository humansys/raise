---
id: L1-04-estimacion-requerimientos
nivel: 1
tags: [raise, estimacion, presales, documentacion, estandar]
---
# L1-04: Proceso de Estimación de Requerimientos a Propuesta

## Metadatos
- **Id**: L1-04-estimacion-requerimientos
- **Nivel**: 1
- **Título**: Proceso de Estimación de Requerimientos a Propuesta Económica
- **Propósito**: Formalizar el flujo que convierte un requerimiento documentado en una estimación de esfuerzo y costo lista para el cliente, articulando Solution Vision, Tech Design, Backlog, Estimación y Statement of Work.
- **Contexto**: Se aplica en preventa o planeación inicial para nuevos proyectos o features, asegurando que la propuesta esté respaldada por un análisis técnico preliminar y un backlog estructurado.
- **Audiencia**: Arquitecto de Preventa, Líder Técnico, Analista de Estimaciones.

## Pre-condiciones
- Existe un PRD (Product Requirements Document) o documento de requisitos validado para el módulo o proyecto a estimar.
- Se tiene acceso a los templates estándar del proyecto en `.raise/templates/solution/`, `.raise/templates/tech/` y `.raise/templates/backlog/`.
- El equipo conoce las reglas de estimación base del proyecto (ej. equivalencia puntos/horas) y el flujo de trabajo de preventa.
- El espacio colaborativo (Confluence/Drive/Repo) para la oportunidad está habilitado y con permisos vigentes.

## Pasos de la Kata

### Paso 1: Consolidar insumos clave
- **Acción**: Reunir PRD, anexos regulatorios y acuerdos de alcance preliminares; registrar supuestos iniciales y dependencias técnicas.
- **Criterios de Aceptación**:
  - Los insumos se listan en un log de trabajo con su ubicación.
  - Se documentan supuestos, exclusiones y restricciones conocidas explícitamente.

### Paso 2: Configurar el espacio de trabajo colaborativo
- **Acción**: Crear o actualizar la carpeta/espacio de la oportunidad con las versiones “live doc” de PRD, Solution Vision, Tech Design, Backlog, Estimation Roadmap y Statement of Work (SoW).
- **Criterios de Aceptación**:
  - El espacio contiene los documentos base instanciados desde los templates con nomenclatura consistente.
  - Los participantes tienen permisos de edición confirmados.

### Paso 3: Generar la Solution Vision
- **Acción**: Usar `.raise/templates/solution/solution-vision-template.md` para transformar el PRD en una visión estructurada (objetivos, alcance MVP, métricas, dependencias críticas).
- **Criterios de Aceptación**:
  - El documento queda completo, trazando cada requerimiento del PRD a la visión de solución.
  - Se registran decisiones clave de negocio y alcance del MVP.

### Paso 4: Elaborar el Tech Design inicial
- **Acción**: Instanciar `.raise/templates/tech/tech_design.md` describiendo arquitectura de alto nivel, componentes, flujos principales y consideraciones técnicas (incluyendo integraciones con terceros y requisitos de seguridad/auditoría).
- **Criterios de Aceptación**:
  - Se cubren arquitectura, componentes principales, modelo de datos preliminar, seguridad y riesgos.
  - Las dependencias técnicas y exclusiones heredadas del PRD están etiquetadas.

### Paso 5: Construir el backlog estimable
- **Acción**: Con la Solution Vision y el Tech Design, poblar `project_backlog.md` desde `.raise/templates/backlog/`, definiendo épicas, features e historias de usuario preliminares con criterios de aceptación.
- **Criterios de Aceptación**:
  - Cada requerimiento del PRD se asigna a al menos una historia o épica.
  - Las historias incluyen criterios de aceptación claros y observan dependencias técnicas identificadas en el Tech Design.

### Paso 6: Realizar la estimación detallada
- **Acción**: Aplicar el template de estimación (ej. `estimation_roadmap.md`) para estimar puntos/horas por historia (considerando factores de conversión estándar, QA, documentación y buffers) y sintetizar cargas por epic/feature.
- **Criterios de Aceptación**:
  - El roadmap resume esfuerzo por historia, epic y total (en horas y semanas/sprints).
  - Se documentan supuestos de estimación, riesgos y buffers explícitos.

### Paso 7: Preparar el Statement of Work (SoW)
- **Acción**: Completar `statement_of_work.md` con entregables, cronograma propuesto (fases y duración), hitos de validación y términos alineados a la estimación técnica.
- **Criterios de Aceptación**:
  - El SoW detalla fases, responsables y fechas relativas o duración.
  - El alcance y costo en el SoW se alinean perfectamente con el esfuerzo estimado en el paso anterior.

### Paso 8: Consolidar y publicar el paquete de estimación
- **Acción**: Revisar coherencia transversal entre Solution Vision, Tech Design, Backlog, Estimación y SoW; cargar versiones finales al espacio compartido y notificar a los stakeholders comerciales y técnicos.
- **Criterios de Aceptación**:
  - Todos los documentos están vinculados entre sí y sin inconsistencias de alcance.
  - Existe un registro de entrega o notificación a los interesados para su revisión y aprobación.

## Post-condiciones
- Solution Vision, Tech Design, Backlog, Estimation Roadmap y Statement of Work completos y versionados.
- Estimación total en horas/puntos lista para cálculo de costos.
- Supuestos, riesgos y dependencias documentados y comunicados claramente.
- Paquete de propuesta accesible en el repositorio colaborativo.

## Notas Adicionales
- Mantener los documentos en el idioma acordado con el cliente (español/inglés).
- Documentar explícitamente cualquier delegación de funcionalidad a servicios externos (SaaS, PaaS) en el Tech Design.
- Reutilizar esta Kata para futuros proyectos, adaptando los factores de estimación según la madurez del equipo y la tecnología.
