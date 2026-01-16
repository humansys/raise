---
description: Transform raw discovery notes or meeting transcripts into a structured Product Requirements Document (PRD).
handoffs: 
  - label: Define Solution Vision
    agent: speckit.raise.vision
    prompt: Create the solution vision for this PRD
    send: true
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

Goal: Transform initial discovery notes into a validated PRD in `specs/main/project_requirements.md` following the 9 steps of Kata `flujo-01-discovery`.

1. **Initialize Environment**:
   - Run `.specify/scripts/bash/check-prerequisites.sh --json --paths-only` to get REPO_ROOT and paths.
   - Load template from `.specify/templates/raise/solution/project_requirements.md`.

2. **Paso 1: Cargar Contexto Inicial**:
   - Recopilar todas las notas de reuniones y documentos previos en $ARGUMENTS.
   - **Verificación**: Existe contexto suficiente para iniciar.
   - > **Si no puedes continuar**: Contexto disperso o incompleto → Solicitar al usuario que consolide las notas de reuniones antes de continuar.

3. **Paso 2: Instanciar Template PRD**:
   - Preparar el archivo `specs/main/project_requirements.md` basado en el template.
   - **Verificación**: El archivo está listo para ser llenado.
   - > **Si no puedes continuar**: Template no encontrado → Verificar que `.specify/templates/raise/solution/project_requirements.md` existe.

4. **Paso 3: Articular el Problema de Negocio**:
   - Completar sección "Problem Statement": usuarios afectados, impacto (costo/tiempo), urgencia.
   - **Verificación**: Un stakeholder no técnico puede entenderlo sin explicación.
   - > **Si no puedes continuar**: Problema no claro → Usar técnica de los "5 Por Qués" para clarificar el problema central con el usuario.

5. **Paso 4: Definir Metas y Métricas de Éxito**:
   - Completar "Goals & Success Metrics": metas cuantificables, métricas y targets numéricos.
   - **Verificación**: Cada meta tiene al menos una métrica asociada con target numérico.
   - > **Si no puedes continuar**: Métricas vagas → Preguntar "¿Cómo sabremos que tuvimos éxito?" hasta obtener números concretos. Si no hay, proponer rangos.

6. **Paso 5: Documentar Alcance (In/Out)**:
   - Completar sección "Scope": In-Scope vs Out-of-Scope explícito.
   - **Verificación**: Las listas son mutuamente excluyentes y cubren ambigüedades.
   - > **Si no puedes continuar**: Alcance ambiguo → Listar 3-5 áreas grises (ej: "¿incluye móvil?") y pedir decisión explícita.

7. **Paso 6: Listar Requisitos Funcionales**:
   - Completar "Functional Requirements" usando formato: "El sistema DEBE [acción] cuando [condición]" y MoSCoW.
   - **Verificación**: Cada requisito es testeable (Gherkin-ready).
   - > **Si no puedes continuar**: Requisitos vagos → Reformular como comportamiento observable. Preguntar por la acción específica y el resultado esperado.

8. **Paso 7: Listar Requisitos No-Funcionales**:
   - Completar "Non-Functional Requirements": Rendimiento, Seguridad, Disponibilidad, Escalabilidad.
   - **Verificación**: Cada requisito tiene un número o rango específico.
   - > **Si no puedes continuar**: NFRs sin cuantificar → Proponer un número basado en estándares de la industria y pedir validación.

9. **Paso 8: Documentar Supuestos y Riesgos**:
   - Completar secciones "Assumptions" y "Risks": al menos 3 de cada uno con mitigación para riesgos.
   - **Verificación**: Cada riesgo tiene una estrategia de mitigación asociada.
   - > **Si no puedes continuar**: No se identifican riesgos → Usar técnica de pre-mortem: "Imagina que el proyecto fracasó, ¿qué salió mal?".

10. **Paso 9: Validar PRD**:
    - Generar el contenido final en `specs/main/project_requirements.md`.
    - **LIMIT: Maximum 3 [NEEDS CLARIFICATION] markers total**.
    - **Verificación**: El PRD está completo y listo para validación formal.
    - > **Si no puedes continuar**: Información crítica faltante → Documentar como "pendiente aprobación formal" y establecer deadline.

11. **Finalize & Validate**:
    - Ejecutar validación usando `.specify/gates/raise/gate-discovery.md`.
    - Run `.specify/scripts/bash/update-agent-context.sh gemini`.
    - Confirm file existence with `check_file "specs/main/project_requirements.md" "PRD Generation"`.

## High-Signaling Guidelines

- **Focus**: Business value and "WHAT", not "HOW".
- **Language**: Instructions English; Content **SPANISH**.
- **Jidoka**: Stop and ask if critical goals/metrics are missing after 3 clarification attempts.

## AI Guidance

When executing this workflow:
1. **Be proactive**: Propose standard industry metrics if notes are vague.
2. **Follow Katas**: Ensure every step and Jidoka block from `flujo-01-discovery` is respected.
3. **Traceability**: Every requirement should link back to a goal or a problem.
4. **Gates**: Always run the reference gate at the end.

