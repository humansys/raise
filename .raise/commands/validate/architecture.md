---
description: Validates a Technical Design/Architecture document against Gate-Architecture criteria.
handoffs:
  - label: Fix Architecture issues
    agent: project/design-architecture
    prompt: Update the architecture to address the failing criteria
  - label: Continue to Backlog
    agent: project/create-backlog
    prompt: Create backlog from this validated architecture
---

## User Input

```text
$ARGUMENTS
```

Specify path to Technical Design document (default: `specs/main/tech_design.md`).

## Outline

Goal: Validate Technical Design structure, content quality, and consistency with Solution Vision.

1. **Initialize Environment**:
   - Run `.specify/scripts/bash/check-prerequisites.sh --json --paths-only` to get REPO_ROOT.
   - Load gate from `.raise/gates/gate-architecture.md`.
   - Load Solution Vision from `specs/main/solution_vision.md` for consistency checks.

2. **Paso 1: Cargar Technical Design**:
   - **Acción**: Leer documento del path especificado o default.
   - **Verificación**: Archivo existe y tiene estructura de diseño técnico.
   - > **Si no puedes continuar**: Tech Design no encontrado → **JIDOKA**: Ejecutar `/project/design-architecture` primero.

3. **Paso 2: Evaluar Estructura (Requerido)**:
   - Tiene sección "System Context".
   - Tiene sección "Container Diagram".
   - Tiene sección "Decisiones Clave".
   - Tiene sección "Quality Attributes".
   - **Verificación**: Todas las secciones requeridas presentes.
   - > **Si no puedes continuar**: Secciones faltantes → Listar qué secciones añadir.

4. **Paso 3: Evaluar Contenido (Requerido)**:
   - System Context tiene ≥1 actor externo.
   - System Context tiene ≥1 sistema externo O justificación de standalone.
   - Container diagram tiene ≥2 containers.
   - Cada container tiene: nombre, responsabilidad, tecnología.
   - Cada decisión tiene rationale (no solo "qué", también "por qué").
   - NFRs son medibles (tienen números o criterios objetivos).
   - **Verificación**: Contenido cumple criterios de calidad.
   - > **Si no puedes continuar**: Contenido incompleto → Detallar qué falta en cada sección.

5. **Paso 4: Evaluar Consistencia (Requerido)**:
   - Componentes mencionados existen en Solution Vision.
   - No hay contradicciones con Solution Vision.
   - Tecnologías son consistentes con restricciones técnicas.
   - **Verificación**: Consistencia verificada.
   - > **Si no puedes continuar**: Inconsistencia detectada → Listar contradicciones específicas.

6. **Paso 5: Evaluar Calidad (Recomendado)**:
   - Diagramas son legibles (no sobrecargados).
   - No hay secciones con placeholders `[TODO]`.
   - Decisiones referencian ADRs si existen.
   - **Verificación**: Criterios de calidad evaluados.
   - > **Si no puedes continuar**: N/A (estos son opcionales).

7. **Paso 6: Generar Reporte de Validación**:
   - **Status**: PASS / PASS con observaciones / FAIL
   - Incluir checklist completo con evidencia.
   - **Verificación**: Reporte generado.
   - > **Si no puedes continuar**: N/A.

8. **Finalize**:
   - Mostrar status final.
   - Si PASS: "Ready for Backlog → `/project/create-backlog`"
   - Si FAIL: "Address issues above → `/project/design-architecture`"

## High-Signaling Guidelines

- **Output**: Reporte de validación con checklist C4-style.
- **Focus**: Estructura, contenido, y consistencia.
- **Language**: Instructions English; Content **SPANISH**.
- **Jidoka**: FAIL en cualquier criterio Requerido bloquea avance.

## AI Guidance

When executing this workflow:
1. **C4 Model Awareness**: Verificar que System Context y Container siguen C4.
2. **Decision Records**: Cada decisión debe tener "por qué", no solo "qué".
3. **Measurable NFRs**: Rechazar NFRs vagos como "debe ser rápido".
4. **Vision Alignment**: Cada componente debe tener origen en Vision.
