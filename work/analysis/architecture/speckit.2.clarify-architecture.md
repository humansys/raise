# Análisis Arquitectónico: speckit.2.clarify

## 1. Resumen Ejecutivo

El comando `speckit.2.clarify` es un workflow interactivo de reducción de ambigüedad diseñado para detectar y resolver puntos de decisión faltantes o subespecificados en la especificación de features. Opera bajo el principio de "shift-left quality" - resolviendo ambigüedades ANTES del diseño técnico para minimizar el riesgo de retrabajo downstream.

**Patrón arquitectónico clave**: Interactive Question-Answer Loop con integración incremental en cada paso, evitando pérdida de contexto y maximizando atomicidad.

**Innovación principal**: Sistema de taxonomía multi-dimensional para detección de ambigüedad que cubre 11 categorías de calidad de especificaciones.

## 2. Estructura del Comando

### 2.1 Frontmatter Analysis

```yaml
description: Identify underspecified areas in the current story spec by asking up to 5 highly targeted clarification questions and encoding answers back into the spec.
handoffs:
  - label: Build Technical Plan
    agent: speckit.3.plan
    prompt: Create a plan for the spec. I am building with...
```

**Patrón**: Single sequential handoff. La clarificación es un paso bloqueante antes de planning.

**Diseño**: El handoff usa un prompt abierto ("I am building with...") permitiendo al usuario especificar tech stack directamente al pasar a plan.

### 2.2 Input Processing

**Patrón**: Dual-input context
- `$ARGUMENTS`: Usado para priorización de preguntas (contexto del usuario)
- Spec file content: Fuente principal de análisis

**Estrategia**: Los argumentos se usan en el paso 8 (prioritization) para ajustar la relevancia de las categorías.

### 2.3 Outline Structure

**Flujo principal**: 8 pasos secuenciales con punto de decisión temprana (early termination)

1. **Initialize** (prerequisite check via JSON)
2. **Scan** (ambiguity detection usando taxonomía)
3. **Generate queue** (priorización de preguntas, max 5)
4. **Interactive loop** (preguntar UNA a la vez)
5. **Incremental integration** (escribir después de CADA respuesta)
6. **Validation** (después de cada escritura + final)
7. **Write spec** (save final)
8. **Report** (coverage summary)

**Punto crítico**: El paso 5 (integration) se ejecuta DESPUÉS DE CADA respuesta aceptada, no al final del loop - esto es fundamental para la robustez.

## 3. Patrones de Diseño Identificados

| Patrón | Manifestación | Propósito |
|--------|---------------|-----------|
| **Interactive Question Loop** | Un pregunta a la vez, validación antes de continuar | Reducir carga cognitiva, mejorar precisión de respuestas |
| **Incremental Integration** | Escribir spec después de cada respuesta aceptada | Prevenir pérdida de contexto en conversaciones largas |
| **Taxonomy-Based Detection** | 11 categorías de análisis de calidad | Cobertura sistemática vs. ad-hoc |
| **Progressive Disclosure** | No revelar futuras preguntas en la cola | Evitar anchoring bias del usuario |
| **Multiple-Choice with Recommendation** | Analizar opciones y recomendar la mejor | Reducir decisión fatigue mientras preserva autonomía |
| **Early Termination** | Permitir "done"/"good" en cualquier momento | Respetar señales de completitud del usuario |
| **Coverage Mapping** | Rastrear estado Clear/Partial/Missing por categoría | Validar completitud y guiar reporte |
| **Atomic Section Updates** | Actualizar secciones apropiadas + clarifications log | Trazabilidad dual: cambios inline + audit trail |

## 4. Script Integration

| Script Called | Input | Output | Purpose |
|---------------|-------|--------|---------|
| `check-prerequisites.sh` | `--json --paths-only` | JSON con FEATURE_DIR, FEATURE_SPEC | Obtener rutas absolutas sin validación pesada |

**Patrón de integración**: Single-script, minimal mode (`--paths-only`) para reducir overhead.

**Decisión de diseño**: NO usa `--require-*` flags porque clarify puede ejecutarse antes de que existan plan/tasks.

## 5. Validation Strategy

**Multi-level validation**:

### Nivel 1: Per-Answer Validation (Paso 4)
- Validar respuesta mapea a opción o cumple restricción ≤5 palabras
- Pedir desambiguación si necesario (no cuenta como nueva pregunta)

### Nivel 2: Per-Write Validation (Paso 6)
Ejecutado DESPUÉS DE CADA integración:
- Exactamente un bullet por respuesta aceptada (no duplicados)
- Total preguntas ≤ 5
- No placeholders vagos que la respuesta debía resolver
- No declaraciones contradictorias previas
- Estructura markdown válida
- Consistencia terminológica

### Nivel 3: Final Pass Validation (Paso 6)
Mismo checklist pero ejecutado al finalizar todo el loop.

**Diseño**: Validación después de cada write (atomic) + final pass (comprehensive) - doble red de seguridad.

## 6. Error Handling Patterns

### Pattern 1: Prerequisite Failure
```
If JSON parsing fails → abort and instruct user to re-run /speckit.1.specify
```
**Filosofía**: Fail fast con acción correctiva clara.

### Pattern 2: Missing Spec File
```
If spec file missing → instruct user to run /speckit.1.specify first
```
**Principio**: No crear artefactos aquí - preservar single responsibility.

### Pattern 3: Early Exit on Full Coverage
```
If no meaningful ambiguities → report "No critical ambiguities" + suggest proceeding
```
**Diseño**: Reportar éxito explícitamente, evitar trabajo innecesario.

### Pattern 4: Answer Disambiguation
```
If answer ambiguous → ask quick disambiguation (counts as same question)
```
**Estrategia**: Resolver en el momento, no avanzar con incertidumbre.

### Pattern 5: Quota Management
```
If quota reached with high-impact unresolved → flag as Deferred with rationale
```
**Transparencia**: Reportar qué quedó pendiente y por qué.

## 7. State Management

### In-Memory State
- **Coverage map**: Categoría → Status (Clear/Partial/Missing)
- **Question queue**: Max 5 preguntas priorizadas
- **Working memory**: Respuestas aceptadas pendientes de integración
- **Spec representation**: Contenido actual + raw file contents

### Persistent State
- **Spec file**: Actualizado incrementalmente después de cada respuesta
- **Clarifications section**: Audit trail con `## Clarifications` / `### Session YYYY-MM-DD`

### State Transitions
```
Load spec → Build coverage map → Generate queue → Ask Q1 → User answers → Integrate → Write spec → Ask Q2 → ...
```

**Patrón crítico**: Write después de CADA integración, no batch al final.

**Razón**: Conversaciones largas pueden exceder límites de contexto o interrumpirse - guardar progreso incrementalmente.

## 8. Key Design Decisions

| Decision | Rationale | Trade-offs |
|----------|-----------|------------|
| **Max 5 questions per session** | Límite cognitivo razonable; evitar clarification fatigue | Puede requerir múltiples runs para specs complejos |
| **Un pregunta a la vez** | Reduce carga cognitiva; mejora precisión de respuestas | Más turns de conversación (más tokens) |
| **Incremental writes** | Previene pérdida de contexto; atomicidad | Más I/O operations; spec puede tener estados intermedios |
| **Recommendation-first en multiple choice** | Reduce decision fatigue; aplica best practices | Usuario puede sentir pérdida de control si no se explica bien |
| **Taxonomía de 11 categorías** | Cobertura sistemática vs. ad-hoc | Overhead de análisis inicial; puede generar preguntas menos relevantes |
| **No revelar cola de preguntas** | Evita anchoring bias; permite reordenamiento dinámico | Usuario no sabe cuántas quedan (puede generar ansiedad) |
| **Multiple-choice con ≤5 opciones** | Balance entre estructura y flexibilidad | Requiere diseño cuidadoso de opciones mutuamente excluyentes |
| **Short answer ≤5 words** | Fuerza precisión; reduce ambiguedad | Puede limitar expresividad para conceptos complejos |
| **Clarifications section separada** | Trazabilidad; audit trail limpio | Duplicación de info (también inline en otras secciones) |
| **Actualizar secciones inline** | Spec es single source of truth | Riesgo de inconsistencia entre clarifications log y secciones |

## 9. Comparison with Other Commands

### vs. speckit.1.specify
- **Specify**: Creación inicial de spec desde descripción natural
- **Clarify**: Refinamiento iterativo de spec existente
- **Relación**: Sequential dependency (clarify requiere spec existente)

### vs. speckit.3.plan
- **Clarify**: Resuelve ambigüedades funcionales/de dominio
- **Plan**: Resuelve decisiones técnicas/arquitectónicas
- **Handoff**: Clarify → Plan (clarify es prerequisito recomendado)

### vs. speckit.util.checklist
- **Clarify**: Interactive workflow que MODIFICA spec
- **Checklist**: Non-interactive generation que NO modifica nada
- **Propósito**: Clarify reduce ambiguedad; Checklist valida calidad

### vs. speckit.5.analyze
- **Clarify**: Interactive, domain-focused, modifica spec
- **Analyze**: Read-only, cross-artifact consistency, NO modifica
- **Timing**: Clarify ANTES de plan; Analyze DESPUÉS de tasks

## 10. Learnings for Standardization

### Patrón 1: Incremental Persistence
**Adoptar**: Escribir estado después de cada paso significativo, no batch al final.
**Aplicar a**: Cualquier comando con loops largos o procesos multi-paso.
**Razón**: Robustez ante interrupciones, pérdida de contexto, límites de memoria.

### Patrón 2: Taxonomy-Based Analysis
**Adoptar**: Usar frameworks estructurados de análisis vs. preguntas ad-hoc.
**Aplicar a**: Commands que detectan gaps/issues (analyze, checklist generation).
**Razón**: Cobertura predecible, documentación de proceso, resultados comparables.

### Patrón 3: Progressive Disclosure
**Adoptar**: No revelar toda la información/planes de una vez.
**Aplicar a**: Workflows interactivos con múltiples decisiones.
**Razón**: Reduce carga cognitiva, evita anchoring bias, permite adaptación dinámica.

### Patrón 4: Recommendation-First Choices
**Adoptar**: Para decisiones múltiples, analizar y recomendar opción óptima.
**Aplicar a**: Cualquier comando que presente opciones al usuario.
**Razón**: Reduce decision fatigue, aplica best practices, preserva autonomía.

### Patrón 5: Early Termination Signals
**Adoptar**: Respetar señales de completitud del usuario ("done", "good").
**Aplicar a**: Todos los workflows interactivos.
**Razón**: Respeta autonomía, evita preguntas innecesarias, mejora UX.

### Patrón 6: Dual Traceability
**Adoptar**: Audit trail separado + cambios inline en artefactos.
**Aplicar a**: Commands que modifican artefactos críticos.
**Razón**: Trazabilidad histórica + spec como single source of truth.

### Patrón 7: Quota-Based Constraints
**Adoptar**: Límites explícitos en procesos abiertos (max N preguntas/items).
**Aplicar a**: Procesos potencialmente ilimitados (preguntas, generación de items).
**Razón**: Predecibilidad, evita runaway processes, gestión de expectativas.

### Anti-Patrón 1: Batch Updates
**Evitar**: Acumular múltiples cambios para escribir al final.
**Problema**: Pérdida de progreso ante interrupciones, exceed context limits.
**Solución**: Incremental writes como en clarify.

### Anti-Patrón 2: Revealing Future Questions
**Evitar**: Mostrar toda la cola de preguntas pendientes.
**Problema**: Anchoring bias, usuario responde basado en preguntas futuras.
**Solución**: Progressive disclosure - una a la vez.

### Anti-Patrón 3: Vague Constraints
**Evitar**: "Answer briefly" sin límite específico.
**Problema**: Interpretación variable, respuestas inconsistentes.
**Solución**: Restricciones medibles ("≤5 words").

### Patrón de Arquitectura: Question-Driven State Refinement
**Concepto**: Usar ciclos interactivos de pregunta-respuesta para refinar estado gradualmente.
**Componentes**:
1. Initial state analysis (taxonomía)
2. Priority queue generation (máximo N items)
3. Interactive loop (un item a la vez)
4. Incremental state update (write después de cada item)
5. Validation (después de cada update + final)
6. Coverage report (estado final vs. inicial)

**Aplicabilidad**: Cualquier proceso de refinamiento iterativo (clarification, configuration, optimization).

### Patrón de Diseño: Coverage-Based Reporting
**Concepto**: Reportar estado usando matriz de cobertura (categoría → status).
**Beneficios**:
- Visualización clara de progreso
- Identificación de gaps restantes
- Decisión informada de continuar o iterar
- Documentación de completitud

**Formato estándar**:
```markdown
| Category | Status | Notes |
|----------|--------|-------|
| Functional Scope | Resolved | Was Partial, addressed in Q1-Q2 |
| Data Model | Clear | Already sufficient |
| Non-Functional | Deferred | Low impact, can address in plan |
| Edge Cases | Outstanding | Exceeds quota, run /clarify again |
```

### Consideración de Tokens: Minimal JSON Mode
**Patrón**: Usar `--json --paths-only` para obtener solo lo necesario.
**Razón**: Reduce payload, acelera ejecución, minimiza parsing.
**Aplicar**: Cuando solo se necesitan rutas, no validación completa.

### Consideración de UX: Escape Handling
**Patrón**: Documentar manejo de edge cases (comillas simples en args).
**Ejemplo**: `'I'\''m Groot'` o `"I'm Groot"`
**Aplicar**: Todos los comandos que reciben user input.
**Razón**: Prevenir errores de shell escaping.
