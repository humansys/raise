---
description: Validates an Estimation Roadmap against Gate-Estimation criteria.
handoffs:
  - label: Fix Estimation issues
    agent: project/estimate-effort
    prompt: Update the estimation to address the failing criteria
  - label: Generate SOW
    agent: tools/generate-contract
    prompt: Generate Statement of Work from this validated estimation
---

## User Input

```text
$ARGUMENTS
```

Specify path to Estimation Roadmap (default: `specs/main/estimation_roadmap.md`).

## Outline

Goal: Validate that Estimation Roadmap is complete, accurate, and ready for Statement of Work generation.

1. **Initialize Environment**:
   - Run `.specify/scripts/bash/check-prerequisites.sh --json --paths-only` to get REPO_ROOT.
   - Load gate from `.raise/gates/gate-estimation.md`.
   - Load backlog for coverage verification.

2. **Paso 1: Cargar Estimation Roadmap**:
   - **Acción**: Leer documento del path especificado o default.
   - **Verificación**: Archivo existe con estructura de estimación.
   - > **Si no puedes continuar**: Roadmap no encontrado → **JIDOKA**: Ejecutar `/project/estimate-effort` primero.

3. **Paso 2: C1 - Guía de Estimación Completa**:
   - Sección "1. Guía de Estimación en Puntos de Historia" existe.
   - Escala Fibonacci documentada (1, 2, 3, 5, 8, 13).
   - Al menos 3 factores explicados (complejidad, esfuerzo, incertidumbre).
   - Proceso de planning poker descrito.
   - **Verificación**: Guía completa.
   - > **Si no puedes continuar**: Sección faltante → Añadir elementos faltantes.

4. **Paso 3: C2 - Tabla de Estimación Completa**:
   - Sección "2. Estimación del Backlog" existe.
   - Tabla tiene columnas: ID, Elemento, Estimación (SP), Notas, Referencia.
   - 100% cobertura del backlog (verificar contra `project_backlog.md`).
   - Fila TOTAL con suma correcta.
   - **Verificación**: Cobertura completa y matemáticas correctas.
   - > **Si no puedes continuar**: Items faltantes → Listar y añadir al tabla.

5. **Paso 4: C3 - Parámetros de Equipo**:
   - Sección "3. Parámetros para el Roadmap" existe.
   - Duración del sprint documentada.
   - Estructura del equipo (roles con % dedicación).
   - Capacidad con cálculo mostrado.
   - Nota sobre velocidad inicial vs real.
   - **Verificación**: Parámetros completos.
   - > **Si no puedes continuar**: Parámetros faltantes → Añadir cálculos.

6. **Paso 5: C4 - Tabla de Roadmap Proyectado**:
   - Sección "4. Roadmap Proyectado" existe.
   - Tabla: Iteración, Fechas, Objetivo, Elementos, SP Estimados, SP Acumulados.
   - Al menos 1 iteración.
   - SP Acumulados final ≈ Total SP (±5 SP tolerancia).
   - Disclaimer sobre naturaleza de proyección.
   - **Verificación**: Roadmap coherente.
   - > **Si no puedes continuar**: Tabla incompleta → Completar columnas.

7. **Paso 6: C5 - MVP Identificado Claramente**:
   - Iteraciones MVP marcadas en roadmap.
   - SP total del MVP calculado.
   - Ratio MVP documentado (MVP SP / Total SP %).
   - **Verificación**: MVP claro.
   - > **Si no puedes continuar**: MVP no marcado → Marcar iteraciones MVP.

8. **Paso 7: C6 - Modelo de Costos**:
   - Sección "5. Vinculación con Modelo de Costos" existe.
   - Relación SP-a-esfuerzo explicada.
   - Impacto de cambios discutido.
   - Assumptions de costo listadas.
   - **Verificación**: Sección completa.
   - > **Si no puedes continuar**: Sección faltante → Añadir con 3 subsecciones.

9. **Paso 8: C7 - Metadata y Referencias**:
   - YAML frontmatter existe.
   - Campos requeridos: document_id, title, project_name, version, date, author, related_docs, status.
   - related_docs incluye ≥4 items (PRD, Vision, Tech Design, Backlog).
   - Status es "Draft" o "In Review".
   - **Verificación**: Metadata completa.
   - > **Si no puedes continuar**: Campos faltantes → Añadir al YAML.

10. **Paso 9: Generar Reporte**:
    ```
    ## Gate-Estimation Report

    **Status**: [PASS / FAIL]

    ### Summary
    - Total Story Points: X SP
    - MVP Story Points: Y SP (Z% of total)
    - Iterations Needed: N sprints (W weeks)
    - Team Capacity: C SP/sprint
    - Backlog Coverage: 100% (count/count items)

    ### Criteria Results
    - [x] C1: Guía de Estimación
    - [x] C2: Tabla de Estimación
    ...

    ### Issues (if any)
    C#: [Criterion]
      - Issue: [Specific problem]
      - Fix: [Concrete action]
    ```
    - **Verificación**: Reporte generado.
    - > **Si no puedes continuar**: N/A.

11. **Finalize**:
    - Si PASS (7/7): "Ready for SOW → `/tools/generate-contract`"
    - Si FAIL: Ejecutar Jidoka - NO ofrecer handoff hasta que todos pasen.

## High-Signaling Guidelines

- **Output**: Reporte con 7 criterios y métricas.
- **Focus**: Completitud matemática y trazabilidad.
- **Language**: Instructions English; Content **SPANISH**.
- **Jidoka**: ANY criterion failing blocks gate. All 7 must pass.

## AI Guidance

When executing this workflow:
1. **Math Verification**: Verificar todas las sumas de SP.
2. **Backlog Coverage**: Comparar itemlist exacto con backlog.
3. **MVP Ratio Check**: Alertar si MVP >50% (scope creep risk).
4. **Date Consistency**: Verificar que fechas del roadmap son coherentes con duración de sprint.
