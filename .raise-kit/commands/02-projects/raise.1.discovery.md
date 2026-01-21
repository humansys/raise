---
description: Transform raw discovery notes or meeting transcripts into a structured Product Requirements Document (PRD).
handoffs: 
  - label: Define Solution Vision
    agent: raise.2.vision
    prompt: Create the solution vision for this PRD
    send: true
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

Goal: Populate the PRD template (`.specify/templates/raise/solution/project_requirements.md`) with content extracted from discovery notes, producing `specs/main/project_requirements.md`.

1. **Initialize Environment**:
   - Run `.specify/scripts/bash/check-prerequisites.sh --json --paths-only` to get REPO_ROOT and paths.
   - Load and copy the template from `.specify/templates/raise/solution/project_requirements.md` to `specs/main/project_requirements.md`.

2. **Paso 1: Cargar Contexto Inicial**:
   - Recopilar todas las notas de reuniones y documentos previos en $ARGUMENTS.
   - **Verificación**: Existe contexto suficiente para iniciar.
   - > **Si no puedes continuar**: Contexto disperso o incompleto → Solicitar al usuario que consolide las notas de reuniones antes de continuar.

3. **Paso 2: Instanciar Template PRD**:
   - Preparar el archivo `specs/main/project_requirements.md` basado en el template.
   - **Verificación**: El archivo está listo para ser llenado.
   - > **Si no puedes continuar**: Template no encontrado → Verificar que `.specify/templates/raise/solution/project_requirements.md` existe.

4. **Paso 3: Articular el Problema de Negocio**:
   - Redactar sección "1.2 Problema de Negocio": usuarios afectados, impacto (costo/tiempo), urgencia.
   - **Verificación**: Un stakeholder no técnico puede entenderlo sin explicación.
   - > **Si no puedes continuar**: Problema no claro → Usar técnica de los "5 Por Qués" para clarificar el problema central con el usuario.

5. **Paso 4: Definir Metas y Métricas de Éxito**:
   - Redactar secciones "1.3 Metas" y "1.4 Métricas de Éxito": metas cuantificables, métricas y targets numéricos.
   - **Verificación**: Cada meta tiene al menos una métrica asociada con target numérico.
   - > **Si no puedes continuar**: Métricas vagas → Preguntar "¿Cómo sabremos que tuvimos éxito?" hasta obtener números concretos. Si no hay, proponer rangos.

6. **Paso 5: Documentar Alcance (In/Out)**:
   - Redactar sección "3. Alcance del Proyecto": In-Scope vs Out-of-Scope explícito.
   - **Verificación**: Las listas son mutuamente excluyentes y cubren ambigüedades.
   - > **Si no puedes continuar**: Alcance ambiguo → Listar 3-5 áreas grises (ej: "¿incluye móvil?") y pedir decisión explícita.

7. **Paso 6: Listar Requisitos Funcionales**:
   - Redactar sección "4. Requisitos Funcionales" usando formato: "El sistema DEBE [acción] cuando [condición]" y MoSCoW.
   - **Verificación**: Cada requisito es testeable (Gherkin-ready).
   - > **Si no puedes continuar**: Requisitos vagos → Reformular como comportamiento observable. Preguntar por la acción específica y el resultado esperado.

8. **Paso 7: Listar Requisitos No-Funcionales**:
   - Redactar sección "5. Requisitos No Funcionales": Rendimiento, Seguridad, Disponibilidad, Escalabilidad.
   - **Verificación**: Cada requisito tiene un número o rango específico.
   - > **Si no puedes continuar**: NFRs sin cuantificar → Proponer un número basado en estándares de la industria y pedir validación.

9. **Paso 8: Documentar Supuestos y Riesgos**:
   - Redactar secciones "8. Supuestos" y "10. Riesgos Identificados": al menos 3 de cada uno con mitigación para riesgos.
   - **Verificación**: Cada riesgo tiene una estrategia de mitigación asociada.
   - > **Si no puedes continuar**: No se identifican riesgos → Usar técnica de pre-mortem: "Imagina que el proyecto fracasó, ¿qué salió mal?".

10. **Paso 9: Validar PRD con Stakeholders**:
    - **IMPORTANTE**: Primero guarda el documento `specs/main/project_requirements.md` con todas las secciones de la template completadas.
    - **LIMIT: Maximum 3 [NEEDS CLARIFICATION] markers total**.
    - Luego, presenta el PRD para revisión y aprobación:
      1. Indicar que el PRD debe enviarse con 24-48 horas de anticipación
      2. Recomendar agendar sesión de revisión (30-60 min)
      3. Capturar feedback y ajustar
      4. Obtener aprobación explícita
    - **Verificación**: El PRD tiene aprobación explícita (email, comentario en documento, o acta de reunión) de al menos un stakeholder clave.
    - > **Si no puedes continuar**: Stakeholder no disponible → Documentar intento de validación (fecha, canal) y proceder con nota de "pendiente aprobación formal". Establecer deadline para aprobación antes de iniciar Fase 2.

11. **Finalize & Validate**:
    - Confirm file existence with `check_file "specs/main/project_requirements.md" "PRD Generation"`.
    - Ejecutar validación usando `.specify/gates/raise/gate-discovery.md`.
    - Run `.specify/scripts/bash/update-agent-context.sh` (sin parámetro actualiza todos los agentes existentes, o especificar: `claude|gemini|copilot|cursor-agent|qwen|opencode|codex|windsurf|kilocode|auggie|roo|amp|shai|q|bob|qoder`).
    - Verificar que el PRD cumple los criterios del gate:
      - [ ] Problema de negocio articulado claramente
      - [ ] Metas y métricas de éxito definidas con números
      - [ ] Alcance (in/out) explícito
      - [ ] Requisitos funcionales testeables
      - [ ] Requisitos no funcionales cuantificados
      - [ ] Supuestos y riesgos documentados
      - [ ] Aprobación de al menos un stakeholder

## Notas

### Para Proyectos Brownfield
Antes de ejecutar este flujo, considerar ejecutar:
- Análisis de código existente para entender la base actual
- Mapeo de dependencias del ecosistema

## High-Signaling Guidelines

- **Output**: A single Markdown document (`specs/main/project_requirements.md`) populated from the template.
- **Focus**: Business value and "WHAT", not "HOW" (no implementation, no code).
- **Language**: Instructions English; Content **SPANISH**.
- **Jidoka**: Stop and ask if critical goals/metrics are missing after 3 clarification attempts.

## AI Guidance

When executing this workflow:
1. **Role**: You are a Technical Writer populating a template—your output is the PRD document, not code or implementation.
2. **Be proactive**: Propose standard industry metrics if notes are vague.
3. **Follow Katas**: Ensure every step and Jidoka block from `flujo-01-discovery` is respected.
4. **Traceability**: Every requirement should link back to a goal or a problem.
5. **Gates**: Always run the reference gate at the end.

