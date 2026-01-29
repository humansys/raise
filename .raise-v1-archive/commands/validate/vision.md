---
description: Validates a Solution Vision document against Gate-Vision criteria.
handoffs:
  - label: Fix Vision issues
    agent: project/define-vision
    prompt: Update the Vision to address the failing criteria
  - label: Continue to Architecture
    agent: project/design-architecture
    prompt: Create Technical Design from this validated Vision
---

## User Input

```text
$ARGUMENTS
```

Specify path to Solution Vision document (default: `specs/main/solution_vision.md`).

## Outline

Goal: Validate Solution Vision completeness, alignment with PRD, and quality before proceeding to Architecture phase.

1. **Initialize Environment**:
   - Run `.specify/scripts/bash/check-prerequisites.sh --json --paths-only` to get REPO_ROOT.
   - Load gate from `.raise/gates/gate-vision.md`.
   - Load PRD from `specs/main/project_requirements.md` for traceability checks.

2. **Paso 1: Cargar Solution Vision**:
   - **Acción**: Leer documento Vision del path especificado o default.
   - **Verificación**: Archivo existe y tiene estructura de Vision.
   - > **Si no puedes continuar**: Vision no encontrada → **JIDOKA**: Ejecutar `/project/define-vision` primero.

3. **Paso 2: Evaluar Criterios Obligatorios (Must Pass)**:
   - **GV001**: Problem Statement conecta problema de negocio con capacidad técnica faltante.
   - **GV002**: Vision articula propuesta de valor, diferenciadores, y outcomes claros.
   - **GV003**: Alineación explícita: cada goal del PRD tiene mecanismo técnico mapeado.
   - **GV004**: MVP Scope acotado; lista "Must Have" tiene 3-5 items máximo.
   - **GV005**: Métricas técnicas: cada métrica de negocio tiene contraparte técnica medible.
   - **GV006**: Constraints técnicos son cuantificados y específicos.
   - **GV007**: Evidencia de aprobación dual (Business + Technical Lead).
   - **Verificación**: Todos los Must Pass evaluados.
   - > **Si no puedes continuar**: Vision incompleta → Reportar qué secciones faltan.

4. **Paso 3: Evaluar Criterios Recomendados (Should Pass)**:
   - **GV008**: Overview de componentes de alto nivel (3-7 componentes).
   - **GV009**: Mapeo de impacto para todos los stakeholders del PRD.
   - **GV010**: Al menos 3 assumptions explícitas documentadas.
   - **Verificación**: Criterios recomendados evaluados.
   - > **Si no puedes continuar**: N/A (estos son opcionales).

5. **Paso 4: Verificar Trazabilidad con PRD**:
   - **GV011**: Todos los goals del PRD están contabilizados.
   - **GV012**: No hay scope creep (Vision scope es subconjunto o igual a PRD scope).
   - **Verificación**: Trazabilidad verificada.
   - > **Si no puedes continuar**: Inconsistencia detectada → Listar gaps entre PRD y Vision.

6. **Paso 5: Generar Reporte de Validación**:
   - **Acción**: Compilar resultado para cada criterio con status y evidencia.
   - **Verificación**: Reporte generado completo.
   - > **Si no puedes continuar**: N/A.

7. **Finalize**:
   - Mostrar status final (PASS/FAIL).
   - Si PASS: "Ready for Technical Design → `/project/design-architecture`"
   - Si FAIL: "Address issues above → `/project/define-vision`"

## High-Signaling Guidelines

- **Output**: Reporte de validación con checklist y trazabilidad.
- **Focus**: Alineación PRD↔Vision y completitud.
- **Language**: Instructions English; Content **SPANISH**.
- **Jidoka**: FAIL en Must Pass o Traceability bloquea avance.

## AI Guidance

When executing this workflow:
1. **Traceability First**: Siempre verificar alineación con PRD.
2. **Evidence-Based**: Citar secciones específicas al evaluar.
3. **Scope Creep Detection**: Alertar si Vision añade scope no presente en PRD.
4. **Dual Approval**: Verificar ambas aprobaciones antes de PASS final.
