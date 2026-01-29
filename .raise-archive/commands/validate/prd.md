---
description: Validates a PRD document against Gate-Discovery criteria.
handoffs:
  - label: Fix PRD issues
    agent: project/create-prd
    prompt: Update the PRD to address the failing criteria
  - label: Continue to Vision
    agent: project/define-vision
    prompt: Create Solution Vision from this validated PRD
---

## User Input

```text
$ARGUMENTS
```

Specify path to PRD document (default: `specs/main/project_requirements.md`).

## Outline

Goal: Validate PRD completeness and quality against Gate-Discovery checklist before proceeding to Vision phase.

1. **Initialize Environment**:
   - Run `.specify/scripts/bash/check-prerequisites.sh --json --paths-only` to get REPO_ROOT.
   - Load gate from `.raise/gates/gate-discovery.md`.

2. **Paso 1: Cargar PRD**:
   - **Acción**: Leer documento PRD del path especificado o default.
   - **Verificación**: Archivo existe y tiene estructura de PRD.
   - > **Si no puedes continuar**: PRD no encontrado → **JIDOKA**: Ejecutar `/project/create-prd` primero.

3. **Paso 2: Evaluar Criterios Obligatorios (Must Pass)**:
   - **GD001**: Problem Statement describe quién tiene el problema, impacto, y por qué ahora.
   - **GD002**: Goals tienen al menos una métrica de éxito con target numérico.
   - **GD003**: In-Scope y Out-of-Scope son explícitos y no vacíos.
   - **GD004**: Requisitos funcionales son testeables (expresables como Given/When/Then).
   - **GD005**: NFRs están cuantificados (tiempo, %, concurrencia).
   - **GD006**: Al menos 3 riesgos documentados con estrategias de mitigación.
   - **GD007**: Evidencia de aprobación de stakeholders.
   - **Verificación**: Todos los Must Pass evaluados.
   - > **Si no puedes continuar**: PRD incompleto → Reportar qué secciones faltan.

4. **Paso 3: Evaluar Criterios Recomendados (Should Pass)**:
   - **GD008**: Al menos 3 assumptions explícitas documentadas.
   - **GD009**: Requisitos usan priorización MoSCoW.
   - **GD010**: No hay "TBD", placeholders, o marcadores "pending".
   - **Verificación**: Criterios recomendados evaluados.
   - > **Si no puedes continuar**: N/A (estos son opcionales).

5. **Paso 4: Generar Reporte de Validación**:
   - **Acción**: Compilar resultado para cada criterio:
     ```markdown
     ## Gate-Discovery Report

     **Document**: [path al PRD]
     **Status**: [PASS / PASS con observaciones / FAIL]

     ### Must Pass Criteria
     - [x] GD001: Problem Statement completo
     - [ ] GD002: Falta métrica numérica en goals
     ...

     ### Should Pass Criteria
     - [x] GD008: Assumptions documentadas
     ...

     ### Issues to Address
     1. [Descripción del issue y cómo resolverlo]
     ```
   - **Verificación**: Reporte generado con todos los criterios.
   - > **Si no puedes continuar**: N/A.

6. **Finalize**:
   - Mostrar status final (PASS/FAIL).
   - Si PASS: "Ready for Solution Vision → `/project/define-vision`"
   - Si FAIL: "Address issues above → `/project/create-prd`"

## High-Signaling Guidelines

- **Output**: Reporte de validación con checklist y status.
- **Focus**: Completitud antes de avanzar de fase.
- **Language**: Instructions English; Content **SPANISH**.
- **Jidoka**: FAIL en Must Pass bloquea avance a siguiente fase.

## AI Guidance

When executing this workflow:
1. **Strict on Must Pass**: No hay excepciones para criterios obligatorios.
2. **Actionable Feedback**: Cada fallo debe tener sugerencia de corrección.
3. **Evidence-Based**: Citar secciones específicas del PRD al evaluar.
4. **Traceability**: El reporte es auditable y reproducible.
