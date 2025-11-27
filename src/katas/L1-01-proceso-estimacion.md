---
id: L1-10-proceso-estimacion-prosa-pmo
nivel: 1
tags: [raise, estimacion, presales, prosa-pmo, documentacion]
---
# L1-10: Proceso de Estimación PROSA PMO de Requerimientos a Propuesta

## Metadatos
- **Id**: L1-10-proceso-estimacion-prosa-pmo
- **Nivel**: 1
- **Título**: Proceso de Estimación PROSA PMO de Requerimientos a Propuesta Económica
- **Propósito**: Formalizar el flujo que convierte un requerimiento documentado en una estimación de esfuerzo y costo lista para el cliente, articulando Solution Vision, Tech Design, Backlog, Estimación y Statement of Work.
- **Contexto**: Se aplica en preventa o planeación inicial para proyectos PROSA PMO, siguiendo los acuerdos descritos en la reunión del 08/sep/2025 y el documento `docs/estimacion/proceso_estimacion_prosa.md`.
- **Audiencia**: Arquitecto de Preventa, Líder Técnico, Analista de Estimaciones.

## Pre-condiciones
- Existe un PRD validado para el módulo o proyecto a estimar.
- Se tiene acceso a los templates en `.raise/templates/solution/`, `.raise/templates/tech/` y `.raise/templates/backlog/`.
- El equipo conoce las reglas de estimación base (1 punto = 4 horas) y el flujo descrito en `docs/estimacion/proceso_estimacion_prosa.md`.
- El espacio colaborativo (Confluence/Drive) para la oportunidad de venta está habilitado y con permisos vigentes.
- Se cuenta con la grabación o notas de referencia (`docs/estimacion/Reunión iniciada a las 2025_09_08 11_17 CST - Notas de Gemini.md`) para aclarar expectativas y lineamientos.

## Pasos de la Kata

### Paso 1: Consolidar insumos clave
- **Acción**: Reunir PRD, anexos regulatorios (ej. Capítulo 6 mencionado en la reunión) y acuerdos de alcance; registrar supuestos iniciales y dependencias técnicas.
- **Criterios de Aceptación**:
  - Los insumos se listan en un log de trabajo con su ubicación.
  - Se documentan supuestos, exclusiones y restricciones conocidas.

### Paso 2: Configurar el espacio de trabajo colaborativo
- **Acción**: Crear o actualizar la carpeta de la oportunidad con las versiones “live doc” de PRD, Solution Vision, Tech Design, Backlog, Estimation Roadmap y Statement of Work.
- **Criterios de Aceptación**:
  - El folder contiene los documentos base con nomenclatura consistente.
  - Los participantes tienen permisos de edición confirmados.

### Paso 3: Generar la Solution Vision
- **Acción**: Usar `.raise/templates/solution/solution-vision-template.md` para transformar el PRD en una visión estructurada (objetivos, alcance MVP, métricas, dependencias críticas).
- **Criterios de Aceptación**:
  - El documento queda completo, trazando cada requerimiento del PRD.
  - Se registran decisiones clave de negocio discutidas en la reunión.

### Paso 4: Elaborar el Tech Design inicial
- **Acción**: Instanciar `.raise/templates/tech/tech_design.md` describiendo arquitectura, componentes, flujos y consideraciones técnicas (incluyendo integraciones como PingOne y requisitos de auditoría mencionados).
- **Criterios de Aceptación**:
  - Se cubren arquitectura, componentes, datos, seguridad y riesgos.
  - Las dependencias y exclusiones heredadas del PRD están etiquetadas.

### Paso 5: Construir el backlog estimable
- **Acción**: Con la Solution Vision y el Tech Design, poblar `project_backlog.md` desde `.raise/templates/backlog/`, definiendo épicas, features e historias con criterios de aceptación.
- **Criterios de Aceptación**:
  - Cada requerimiento del PRD se asigna a al menos una historia.
  - Las historias incluyen criterios de aceptación claros y observan dependencias técnicas.

### Paso 6: Realizar la estimación detallada
- **Acción**: Aplicar `estimation_roadmap.md` para estimar puntos/horas por historia (1 punto = 4 horas, incorporando QA, documentación y buffers) y sintetizar cargas por epic/feature.
- **Criterios de Aceptación**:
  - El roadmap resume esfuerzo por historia, epic y total (horas y semanas).
  - Se documentan supuestos, riesgos y buffers explícitos.

### Paso 7: Preparar el Statement of Work (SoW)
- **Acción**: Completar `statement_of_work.md` con entregables, cronograma en días desde el arranque, hitos de validación y términos comerciales alineados a la estimación.
- **Criterios de Aceptación**:
  - El SoW detalla fases, responsables y fechas relativas.
  - Se alinea con el esfuerzo estimado y señala supuestos comerciales.

### Paso 8: Consolidar y publicar el paquete de estimación
- **Acción**: Revisar coherencia entre Solution Vision, Tech Design, Backlog, Estimación y SoW; cargar versiones finales a la carpeta compartida y notificar a los interesados.
- **Criterios de Aceptación**:
  - Todos los documentos están vinculados entre sí y sin inconsistencias.
  - Existe un registro de aprobación o envío a stakeholders (ej. Marilú/Braulio).

## Post-condiciones
- Solution Vision, Tech Design, Backlog, Estimation Roadmap y Statement of Work completos y versionados.
- Estimación total en horas y costo derivado listos para presentar al cliente.
- Supuestos, riesgos y dependencias documentados y comunicados.
- Paquete de propuesta accesible en el repositorio colaborativo acordado.

## Notas Adicionales
- Mantener los documentos en español cuando el cliente lo requiera; ajustar terminología para evitar anglicismos.
- Documentar si alguna pieza (ej. gestión de sesiones) se delega a servicios externos como PingOne.
- Reutilizar esta Kata para futuros proyectos, adaptando plantillas y supuestos según el dominio del cliente.