---
description: Validates a Product Backlog against Gate-Backlog criteria.
handoffs:
  - label: Fix Backlog issues
    agent: project/create-backlog
    prompt: Update the backlog to address the failing criteria
  - label: Continue to Estimation
    agent: project/estimate-effort
    prompt: Estimate effort for this validated backlog
---

## User Input

```text
$ARGUMENTS
```

Specify path to Backlog document (default: `specs/main/project_backlog.md`).

## Outline

Goal: Validate that backlog is complete, properly prioritized, and has sufficient quality for Implementation Planning.

1. **Initialize Environment**:
   - Run `.specify/scripts/bash/check-prerequisites.sh --json --paths-only` to get REPO_ROOT.
   - Load gate from `.raise/gates/gate-backlog.md`.

2. **Paso 1: Cargar Backlog**:
   - **Acción**: Leer documento del path especificado o default.
   - **Verificación**: Archivo existe con estructura de backlog.
   - > **Si no puedes continuar**: Backlog no encontrado → **JIDOKA**: Ejecutar `/project/create-backlog` primero.

3. **Paso 2: Evaluar Criterios Obligatorios**:
   - **1**: Features identificadas (3-7 con valor claro).
   - **2**: Features priorizadas con justificación.
   - **3**: MVP identificado (subset mínimo para valor).
   - **4**: User Stories con formato correcto ("Como [rol], quiero [acción], para [beneficio]").
   - **5**: Criterios BDD (cada US tiene ≥2 escenarios Given/When/Then).
   - **6**: Estimaciones completas (todas las US tienen story points).
   - **7**: Product Owner approval documentado.
   - **Verificación**: Todos los obligatorios evaluados.
   - > **Si no puedes continuar**: Criterios fallando → Detalle de cada fallo.

4. **Paso 3: Evaluar Criterios Recomendados**:
   - INVEST compliance (Independent, Valuable, Small, Testable).
   - Detalles técnicos (US enlazadas a Tech Design).
   - Dependencias claras (orden considera dependencias técnicas).
   - **Verificación**: Evaluados como warnings si faltan.
   - > **Si no puedes continuar**: N/A.

5. **Paso 4: Calcular Métricas**:
   - Story Points MVP.
   - Story Points Total.
   - Ratio MVP/Total (target: 30-50%).
   - Conteo de Features y User Stories.
   - **Verificación**: Métricas calculadas.
   - > **Si no puedes continuar**: No hay estimaciones → Reportar como fallo de C6.

6. **Paso 5: Generar Reporte**:
   ```markdown
   ## Gate-Backlog Report

   **Proyecto**: [nombre]
   **Total Features**: N
   **Total User Stories**: M
   **Status**: [PASS / FAIL]

   ### Métricas
   - Story Points MVP: X
   - Story Points Total: Y
   - Ratio MVP/Total: Z% (target: 30-50%)

   ### Obligatorios
   - [x] 1. Features 3-7 con valor claro
   - [ ] 2. Features priorizadas con justificación
   ...

   ### Issues to Address
   1. [Issue específico y cómo resolverlo]
   ```
   - **Verificación**: Reporte generado.
   - > **Si no puedes continuar**: N/A.

7. **Finalize**:
   - Si PASS: "Ready for Estimation → `/project/estimate-effort`"
   - Si FAIL: "Address issues → `/project/create-backlog`"

## High-Signaling Guidelines

- **Output**: Reporte con métricas y checklist.
- **Focus**: Calidad de User Stories y priorización.
- **Language**: Instructions English; Content **SPANISH**.
- **Jidoka**: FAIL en obligatorios bloquea estimación.

## AI Guidance

When executing this workflow:
1. **Format Strict**: Verificar formato exacto de User Stories.
2. **BDD Coverage**: Cada US DEBE tener ≥2 criterios Given/When/Then.
3. **MVP Ratio**: Alertar si MVP >50% del backlog (scope creep risk).
4. **Estimation Consistency**: Story points deben ser consistentes (similar complexity = similar SP).
