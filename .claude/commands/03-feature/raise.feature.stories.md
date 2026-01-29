---
description: Generate User Stories from a Feature Tech Design, decomposing technical approach into implementable work units with clear acceptance criteria.
handoffs:
  - label: Plan Implementation
    agent: raise.feature.plan
    prompt: Create implementation plan from these user stories
    send: true
  - label: Validate Stories
    agent: raise.validate.stories
    prompt: Validate the generated user stories
    send: false
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty). The input should be:
- A feature ID (e.g., "F1.2", "raise-feature-stories")
- Or a path to the tech-design.md file

## Outline

Goal: Generate User Stories from a Feature Tech Design (`specs/features/{feature-id}/tech-design.md`), creating individual story files in `specs/features/{feature-id}/stories/`.

1. **Initialize Environment**:
   - Identify feature from user input.
   - Locate tech-design at `specs/features/{feature-id}/tech-design.md`.
   - Create stories directory: `specs/features/{feature-id}/stories/`.

2. **Paso 1: Cargar y Parsear Tech Design**:
   - Leer `specs/features/{feature-id}/tech-design.md`.
   - Extraer frontmatter YAML (id, title, feature_ref).
   - Identificar secciones clave:
     - "Componentes afectados" → lista de componentes
     - "Interfaz / Contrato" → definición de contrato
     - "Consideraciones" → decisiones y riesgos
   - **Verificación**: Tech Design existe y tiene las 3 secciones obligatorias.
   - > **Si no puedes continuar**: Tech Design no encontrado → **JIDOKA**: Ejecutar `/raise.feature.design {feature-id}` primero. Secciones faltantes → Completar tech-design antes de generar stories.

3. **Paso 2: Generar Stories por Componente**:
   - Para cada componente en "Componentes afectados":
     - Si es **nuevo**: Crear story "Implementar {componente}"
     - Si es **modificación**: Crear story "Modificar {componente} para {cambio}"
   - Asignar prioridad:
     - P1: Componentes sin dependencias o bloqueantes
     - P2: Componentes con dependencias
     - P3: Componentes opcionales o mejoras
   - **Verificación**: Al menos 1 story generada por componente nuevo.
   - > **Si no puedes continuar**: Sin componentes identificados → Revisar sección "Componentes afectados" del tech-design.

4. **Paso 3: Generar Story de Contrato**:
   - Leer sección "Interfaz / Contrato".
   - Crear story: "Implementar contrato de {interface}".
   - Extraer acceptance criteria del contrato:
     - Cada endpoint/método → 1 criterion
     - Cada validación → 1 criterion
     - Ejemplo de uso → criterion de smoke test
   - **Verificación**: Story de contrato tiene >= 3 acceptance criteria.
   - > **Si no puedes continuar**: Contrato no definido → Marcar como [NEEDS CLARIFICATION] y continuar con stories de componentes.

5. **Paso 4: Enriquecer Stories con Consideraciones**:
   - Leer sección "Consideraciones".
   - Para cada riesgo con mitigación:
     - Agregar "Technical Note" a la story más relacionada.
   - Para cada decisión:
     - Verificar que alguna story la implementa.
   - **Verificación**: Decisiones técnicas están reflejadas en al menos una story.
   - > **Si no puedes continuar**: Decisiones huérfanas → Crear story adicional o agregar a story existente.

6. **Paso 5: Escribir Archivos de Stories**:
   - Para cada story generada, crear archivo:
     - Path: `specs/features/{feature-id}/stories/US-{NNN}-{slug}.md`
     - Formato:
       ```markdown
       ---
       id: US-{NNN}
       title: "{título}"
       feature_ref: {feature-id}
       status: draft
       priority: {P1|P2|P3}
       estimate: {S|M|L}
       ---

       # US-{NNN}: {título}

       **Como** {rol},
       **Quiero** {acción},
       **Para** {beneficio}.

       ## Acceptance Criteria

       - [ ] {criterion 1}
       - [ ] {criterion 2}
       - [ ] {criterion 3}

       ## Technical Notes

       {notas del tech-design si aplican}
       ```
   - **Verificación**: Cada archivo existe y tiene formato válido.
   - > **Si no puedes continuar**: Error de escritura → Verificar permisos del directorio.

7. **Paso 6: Generar Índice de Stories**:
   - Crear `specs/features/{feature-id}/stories/index.md`:
     ```markdown
     # User Stories: {feature-name}

     | ID | Title | Priority | Status | Estimate |
     |----|-------|----------|--------|----------|
     | US-001 | {title} | P1 | draft | M |
     | US-002 | {title} | P2 | draft | S |

     ## Dependency Graph

     ```mermaid
     graph LR
       US-001 --> US-002
       US-001 --> US-003
     ```

     ## Summary

     - Total stories: {N}
     - P1 (Critical): {n1}
     - P2 (Important): {n2}
     - P3 (Nice-to-have): {n3}
     ```
   - **Verificación**: Índice refleja todas las stories generadas.
   - > **Si no puedes continuar**: Inconsistencia → Regenerar índice desde archivos existentes.

8. **Paso 7: Validar Resultado**:
   - Contar stories generadas:
     - Si < 3: Warning "Pocas stories, verificar granularidad"
     - Si > 7: Warning "Muchas stories, considerar dividir feature"
     - Si 3-7: OK
   - Verificar cada story tiene:
     - [ ] >= 2 acceptance criteria
     - [ ] Priority asignada
     - [ ] Estimate asignada (S/M/L)
   - **Verificación**: Todas las stories pasan validación básica.
   - > **Si no puedes continuar**: Stories inválidas → Corregir antes de continuar.

9. **Finalize & Validate**:
   - Confirmar archivos creados:
     - `specs/features/{feature-id}/stories/index.md`
     - `specs/features/{feature-id}/stories/US-*.md` (N archivos)
   - Mostrar resumen:
     ```
     ✓ User Stories generadas para {feature-name}

     📁 specs/features/{feature-id}/stories/
        ├── index.md
        ├── US-001-{slug}.md (P1, M)
        ├── US-002-{slug}.md (P2, S)
        └── US-003-{slug}.md (P2, S)

     📊 Resumen:
        - Total: {N} stories
        - Estimación: {total} (S=1, M=2, L=3 puntos)
        - Prioridad: {n1} P1, {n2} P2, {n3} P3
     ```
   - Mostrar warnings si aplican:
     - "⚠ Pocas stories (< 3): verificar si el feature está sub-descompuesto"
     - "⚠ Muchas stories (> 7): considerar dividir en sub-features"
   - Mostrar handoff: "→ Siguiente paso: `/raise.feature.plan` para crear plan de implementación"

## Notas

### Granularidad de Stories
- **Ideal**: 1 story = 1-3 días de trabajo
- **Mínimo**: 2 acceptance criteria por story
- **Máximo sugerido**: 7 stories por feature

### Sizing (Estimación)
| Size | Descripción | Referencia |
|------|-------------|------------|
| S | < 4 horas | Cambio simple, path conocido |
| M | 4-16 horas | Complejidad media, alguna incertidumbre |
| L | 16-40 horas | Complejo, requiere investigación |

### Priorización
| Priority | Criterio |
|----------|----------|
| P1 | Bloqueante para otras stories, core del feature |
| P2 | Importante pero no bloqueante |
| P3 | Nice-to-have, puede diferirse |

## High-Signaling Guidelines

- **Output**: `specs/features/{feature-id}/stories/` con archivos US-*.md e index.md
- **Focus**: Descomponer tech-design en unidades de trabajo implementables
- **Language**: Instructions English; Content **SPANISH**
- **Jidoka**: Stop si tech-design no existe o está incompleto
- **Lean**: 3-7 stories por feature. Menos es sub-descompuesto, más es over-engineering.

## AI Guidance

When executing this workflow:
1. **Role**: You are a Technical Lead breaking down a feature into implementable units.
2. **Be practical**: Each story should be completable in 1-3 days by one developer.
3. **Traceability**: Every story links back to a component or contract in the tech-design.
4. **Acceptance Criteria**: Write criteria that are testable and unambiguous.
5. **Dependencies**: Identify which stories block others and reflect in priority.
6. **Consistency**: Follow the story template exactly. Don't add extra sections.
