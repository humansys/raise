---
description: Explains a specific rule, its rationale, and how to apply it correctly.
handoffs:
  - label: Edit this rule
    agent: setup/edit-rule
    prompt: I want to modify this rule
  - label: Check compliance
    agent: context/check
    prompt: Check if my code follows this rule
---

## User Input

```text
$ARGUMENTS
```

Specify the rule ID or name to explain (e.g., `200-clean-architecture` or `naming conventions`). If empty, lists available rules.

## Outline

Goal: Provide deep understanding of a rule including its rationale, examples, anti-examples, and practical application guidance.

1. **Initialize Environment**:
   - Run `.specify/scripts/bash/check-prerequisites.sh --json --paths-only` to get REPO_ROOT and paths.
   - Verify `.cursor/rules/` directory exists.

2. **Paso 1: Identificar Regla**:
   - **Acción**: Parsear input para identificar la regla solicitada.
   - **Estrategia de búsqueda**:
     - Match exacto por ID (ej: `200-clean-architecture`)
     - Match parcial por nombre (ej: `clean arch` → `200-clean-architecture.mdc`)
     - Match por tag (ej: `architecture` → listar reglas con ese tag)
   - **Si vacío**: Listar todas las reglas disponibles con descripción breve.
   - **Verificación**: Regla identificada o lista generada.
   - > **Si no puedes continuar**: Regla no encontrada → Mostrar reglas disponibles más similares; sugerir búsqueda alternativa.

3. **Paso 2: Cargar Regla y Contexto**:
   - **Acción**: Leer contenido completo de la regla `.mdc`.
   - **Extraer**:
     - YAML frontmatter (name, description, globs, tags, alwaysApply)
     - Instrucciones principales
     - Ejemplos y anti-ejemplos (si existen)
   - **Contexto adicional**: Buscar en `specs/main/analysis/rules/analysis-for-[rule].md` si existe.
   - **Verificación**: Contenido de regla cargado.
   - > **Si no puedes continuar**: Archivo corrupto → **JIDOKA**: Reportar error de formato; sugerir recrear con `/setup/generate-rules`.

4. **Paso 3: Generar Explicación Estructurada**:
   - **Acción**: Construir explicación comprensiva:
     ```markdown
     ## Regla: [nombre]

     **ID**: [id]
     **Aplica a**: [globs]
     **Tags**: [tags]

     ### Propósito
     [Explicación del "por qué" de esta regla]

     ### Instrucciones Clave
     [Resumen de las instrucciones principales]

     ### Ejemplos Correctos
     [Código que sigue la regla]

     ### Anti-Ejemplos (Qué Evitar)
     [Código que viola la regla]

     ### Aplicación Práctica
     [Cuándo y cómo aplicar esta regla]

     ### Relación con Otras Reglas
     [Dependencias o conflictos con otras reglas]
     ```
   - **Verificación**: Explicación tiene al menos propósito e instrucciones.
   - > **Si no puedes continuar**: Regla muy corta sin contexto → Generar propósito inferido desde nombre/descripción; marcar como "Explicación inferida".

5. **Paso 4: Buscar Evidencia en Código**:
   - **Acción**: Buscar en el repositorio ejemplos reales de aplicación de la regla.
   - **Análisis**:
     - Archivos que matchean los globs
     - Patrones del código que siguen la regla
     - Posibles violaciones existentes
   - **Output**: Ejemplos concretos del repositorio actual.
   - **Verificación**: Búsqueda ejecutada (puede no haber resultados).
   - > **Si no puedes continuar**: Búsqueda muy lenta → Limitar a 10 archivos más recientes.

6. **Paso 5: Presentar Explicación Interactiva**:
   - **Acción**: Mostrar explicación formateada.
   - **Interactividad**: Ofrecer opciones:
     - "¿Ver más ejemplos del repositorio?"
     - "¿Editar esta regla?" → handoff a `/setup/edit-rule`
     - "¿Verificar compliance?" → handoff a `/context/check`
   - **Verificación**: Explicación presentada.
   - > **Si no puedes continuar**: N/A (paso final de presentación).

7. **Finalize**:
   - Mostrar resumen de la regla con aplicabilidad.
   - Mostrar handoffs disponibles.
   - Si hay notas de personalización, destacarlas.

## High-Signaling Guidelines

- **Output**: Explicación comprensiva pero concisa de la regla.
- **Focus**: Enseñar el "por qué", no solo el "qué".
- **Language**: Instructions English; Content **SPANISH**.
- **Jidoka**: Si la regla tiene conflictos conocidos, mencionarlos proactivamente.

## AI Guidance

When executing this workflow:
1. **Educational**: El objetivo es que el usuario ENTIENDA la regla, no solo la conozca.
2. **Practical**: Siempre incluir al menos un ejemplo concreto del repositorio cuando sea posible.
3. **Connected**: Explicar cómo esta regla se relaciona con la Constitution y otras reglas.
4. **Honest**: Si la regla es ambigua o tiene edge cases, mencionarlos.
5. **Heutagógico**: Facilitar que el usuario decida si la regla aplica a su caso específico.
