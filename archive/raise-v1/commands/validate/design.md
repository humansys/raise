---
description: Validates a detailed Technical Design against Gate-Design criteria.
handoffs:
  - label: Fix Design issues
    agent: feature/design-feature
    prompt: Update the feature design to address the failing criteria
  - label: Continue to Stories
    agent: feature/generate-stories
    prompt: Generate user stories from this validated design
---

## User Input

```text
$ARGUMENTS
```

Specify path to Technical Design document (default: `specs/main/tech_design.md`).

## Outline

Goal: Validate that Technical Design is complete, technically sound, and provides sufficient guidance for implementation.

1. **Initialize Environment**:
   - Run `.specify/scripts/bash/check-prerequisites.sh --json --paths-only` to get REPO_ROOT.
   - Load gate from `.raise/gates/gate-design.md`.
   - Load Solution Vision for traceability.

2. **Paso 1: Cargar Technical Design**:
   - **Acción**: Leer documento del path especificado o default.
   - **Verificación**: Archivo existe con estructura esperada.
   - > **Si no puedes continuar**: Design no encontrado → **JIDOKA**: Ejecutar `/project/design-architecture` primero.

3. **Paso 2: Verificar Completitud de Secciones**:
   - Visión General presente.
   - Solución Propuesta presente.
   - Arquitectura de Componentes con diagrama.
   - Flujo de Datos documentado.
   - Contratos de API especificados.
   - Modelo de Datos con entidades.
   - Seguridad (AuthN/AuthZ) documentada.
   - Manejo de Errores estandarizado.
   - **Verificación**: Todas las secciones tienen contenido sustancial.
   - > **Si no puedes continuar**: Secciones incompletas → Listar qué completar.

4. **Paso 3: Evaluar Criterios Obligatorios**:
   - **1**: Diagrama de arquitectura presente y claro.
   - **2**: Flujos de datos trazables end-to-end.
   - **3**: Contratos de API con request/response.
   - **4**: Modelo de datos con entidades y relaciones.
   - **5**: Seguridad por endpoint definida.
   - **6**: Catálogo de errores estandarizado.
   - **7**: Aprobación de Arquitecto/Tech Lead.
   - **Verificación**: Todos los obligatorios evaluados.
   - > **Si no puedes continuar**: Criterios fallando → Detalle específico de cada fallo.

5. **Paso 4: Validar Coherencia Arquitectónica**:
   - Componentes del diagrama = componentes descritos.
   - Flujos usan componentes definidos.
   - APIs soportan los flujos.
   - Modelo de datos soporta las APIs.
   - **Verificación**: Sin elementos "huérfanos".
   - > **Si no puedes continuar**: Incoherencia → Trazar cada flujo end-to-end.

6. **Paso 5: Validar Trazabilidad con Vision**:
   - MVP scope cubierto.
   - Mecanismos técnicos prometidos implementados.
   - Sin scope creep.
   - **Verificación**: No hay gaps Vision↔Design.
   - > **Si no puedes continuar**: Gaps detectados → Listar discrepancias.

7. **Paso 6: Evaluar Criterios Recomendados**:
   - ≥2 alternativas por decisión arquitectónica principal.
   - Estrategia de testing definida.
   - Riesgos con owner y mitigación.
   - Sin preguntas abiertas bloqueantes.
   - **Verificación**: Criterios evaluados (pueden ser warnings).
   - > **Si no puedes continuar**: N/A.

8. **Paso 7: Generar Reporte**:
   - Status: PASS / PASS con observaciones / FAIL.
   - Checklist completo con evidencia.
   - **Verificación**: Reporte generado.
   - > **Si no puedes continuar**: N/A.

9. **Finalize**:
   - Si PASS: "Ready for Implementation → `/feature/generate-stories`"
   - Si FAIL: "Address issues → `/feature/design-feature`"

## High-Signaling Guidelines

- **Output**: Reporte de validación exhaustivo.
- **Focus**: Completitud arquitectónica y coherencia.
- **Language**: Instructions English; Content **SPANISH**.
- **Jidoka**: FAIL en obligatorios bloquea implementación.

## AI Guidance

When executing this workflow:
1. **Technical Depth**: Verificar que cada API tiene contrato completo.
2. **Security First**: AuthN/AuthZ debe estar explícito para cada endpoint.
3. **Error Standards**: Catálogo de errores debe ser reusable.
4. **Peer Review Evidence**: Buscar evidencia de revisión técnica.
