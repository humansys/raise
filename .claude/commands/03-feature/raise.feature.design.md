---
description: Generate a Feature Tech Design from a prioritized feature in the backlog, using the lean tech-design-feature template.
handoffs:
  - label: Generate User Stories
    agent: raise.feature.stories
    prompt: Generate user stories for this feature design
    send: true
  - label: Plan Implementation
    agent: raise.feature.plan
    prompt: Create implementation plan for this feature
    send: false
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty). The input should be:
- A feature ID (e.g., "F1.1", "FID-001")
- A feature name from the backlog
- Or a feature description if no backlog exists yet

## Outline

Goal: Create a lean Feature Tech Design (`specs/features/{feature-id}/tech-design.md`) that documents the technical approach for implementing a specific feature.

1. **Initialize Environment**:
   - Run `.raise/scripts/bash/raise/check-prerequisites.sh --json --paths-only` to get REPO_ROOT and paths.
   - Load the template from `.raise/templates/tech/tech-design-feature.md`.
   - Identify the feature from user input or prompt for selection.

2. **Paso 1: Identificar Feature y Contexto**:
   - Si se proporcionó Feature ID: buscar en `specs/main/project_backlog.md` o `specs/main/feature_prioritization.md`.
   - Si se proporcionó descripción: crear nuevo feature ID con formato `F{epic}.{seq}`.
   - Cargar contexto del proyecto:
     - `specs/main/tech_design.md` (arquitectura del proyecto)
     - `specs/main/solution_vision.md` (visión general)
   - **Verificación**: El feature está identificado y existe contexto de proyecto.
   - > **Si no puedes continuar**: Feature no encontrado en backlog → Verificar que `/raise.5.backlog` se ejecutó. Sin contexto de proyecto → Ejecutar `/raise.4.tech-design` primero para proyectos nuevos.

3. **Paso 2: Crear Estructura de Feature**:
   - Crear directorio `specs/features/{feature-id}/` si no existe.
   - Copiar template a `specs/features/{feature-id}/tech-design.md`.
   - Completar frontmatter YAML:
     - `id`: Código único (e.g., "TEC-RAISE-F1.1")
     - `title`: "Tech Design: {Feature Name}"
     - `feature_ref`: ID del feature en backlog
     - `backlog_ref`: Referencia al backlog item
     - `date`: Fecha actual
     - `status`: "Draft"
   - **Verificación**: El archivo existe con frontmatter completo.
   - > **Si no puedes continuar**: Template no encontrado → Verificar ruta `.raise/templates/tech/tech-design-feature.md`.

4. **Paso 3: Definir Approach**:
   - Completar sección "1. Approach":
     - **Qué hace este feature**: 1-2 oraciones describiendo el valor entregado.
     - **Cómo lo implementamos**: 1-2 oraciones con approach técnico de alto nivel.
     - **Componentes afectados**: Lista de componentes que se crean o modifican.
   - Alinear con la arquitectura del proyecto (`specs/main/tech_design.md`).
   - **Verificación**: El approach es comprensible en 30 segundos de lectura. Está alineado con arquitectura existente.
   - > **Si no puedes continuar**: Approach no encaja en arquitectura → Revisar si el feature requiere cambio arquitectónico. Si es así, documentar en "Consideraciones" y escalar a Arquitecto.

5. **Paso 4: Especificar Interfaz/Contrato**:
   - Completar sección "2. Interfaz / Contrato":
     - Definir API endpoints, CLI args, o schema principal en YAML/JSON.
     - Incluir ejemplo de uso concreto.
   - Para features que no exponen API: documentar interfaz interna (función signatures, eventos, etc.).
   - **Verificación**: Existe al menos un ejemplo de uso que un desarrollador puede ejecutar.
   - > **Si no puedes continuar**: Interfaz no clara → Preguntar: "¿Cómo invoca un usuario/sistema esta funcionalidad?" Documentar esa respuesta.

6. **Paso 5: Documentar Consideraciones**:
   - Completar sección "3. Consideraciones":
     - Tabla de decisiones: Aspecto | Decisión | Rationale
     - Lista de riesgos identificados con checkboxes.
   - Incluir al menos 2 aspectos considerados (seguridad, performance, compatibilidad, etc.).
   - **Verificación**: Cada decisión tiene rationale documentado. Riesgos tienen mitigación implícita o explícita.
   - > **Si no puedes continuar**: Sin decisiones que documentar → Todo feature tiene al menos: "Approach general" y "Prioridad de implementación". Documentar esas.

7. **Paso 6: Algoritmo/Lógica (Opcional)**:
   - Si el feature tiene lógica compleja, expandir sección "Algoritmo / Lógica".
   - Documentar en pseudocódigo o descripción paso a paso.
   - **Verificación**: Si aplica, la lógica es comprensible sin leer código.
   - > **Si no puedes continuar**: Lógica muy compleja → Dividir en sub-pasos. Cada paso debe ser verificable independientemente.

8. **Paso 7: Testing Approach (Opcional)**:
   - Si el feature requiere estrategia de testing específica, expandir sección "Testing Approach".
   - Documentar tipos de pruebas y qué cubren.
   - **Verificación**: Si aplica, la estrategia cubre el happy path y casos de error principales.
   - > **Si no puedes continuar**: Sin claridad en testing → Mínimo: unit tests para lógica, integration test para contrato.

9. **Finalize & Validate**:
   - Verificar que el archivo existe: `specs/features/{feature-id}/tech-design.md`.
   - Ejecutar validación usando `.raise/gates/gate-design.md` (criterios aplicables a features).
   - Verificar criterios lean:
     - [ ] Approach claro y alineado con arquitectura
     - [ ] Contrato/interfaz definido con ejemplo
     - [ ] Decisiones con rationale
     - [ ] Riesgos identificados
   - Run `.raise/scripts/bash/raise/update-agent-context.sh` si existe.
   - Mostrar resumen:
     - "✓ Feature Tech Design generado en specs/features/{feature-id}/tech-design.md"
     - Para secciones opcionales vacías: "ℹ Sección '[nombre]' omitida (no aplica)"
   - Mostrar handoff: "→ Siguiente paso: `/raise.feature.stories` para generar User Stories"

## Notas

### Diferencia con Tech Design de Proyecto
- **Proyecto** (`/raise.4.tech-design`): Arquitectura completa, 15+ secciones, decisiones fundamentales.
- **Feature** (`/raise.feature.design`): Diseño lean, 3-4 secciones, enfocado en implementación específica.

### Cuándo Usar Este Comando
- Feature ya priorizado en backlog
- Arquitectura de proyecto ya definida
- Necesidad de documentar approach antes de implementar

### Cuándo NO Usar Este Comando
- Feature requiere cambios arquitectónicos mayores → Usar `/raise.4.tech-design` para actualizar arquitectura primero
- Feature es trivial (< 2 horas de trabajo) → Ir directo a `/raise.feature.plan`

## High-Signaling Guidelines

- **Output**: `specs/features/{feature-id}/tech-design.md` - documento lean de diseño técnico.
- **Focus**: HOW para un feature específico, no arquitectura general.
- **Language**: Instructions English; Content **SPANISH**.
- **Jidoka**: Stop si no hay contexto de proyecto. Para features complejos, escalar a Arquitecto.
- **Lean**: Máximo 4 secciones obligatorias. Secciones opcionales solo si agregan valor.

## AI Guidance

When executing this workflow:
1. **Role**: You are a Technical Lead designing a specific feature—focus on actionable decisions, not comprehensive documentation.
2. **Be lean**: Prefer 1 page over 5 pages. If a section doesn't add value for this specific feature, omit it.
3. **Align with architecture**: Every decision should fit within the project's existing architecture (`specs/main/tech_design.md`).
4. **Traceability**: Link back to the feature in the backlog and the project architecture.
5. **Gates**: Apply gate-design criteria but scoped to feature level.
6. **Consistency**: Follow the lean template structure. Don't add sections not in the template.
