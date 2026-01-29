---
description: Delivers Minimum Viable Context (MVC) for a specific task to an LLM agent.
handoffs:
  - label: Check compliance
    agent: context/check
    prompt: Verify code against the loaded rules
  - label: Explain a rule
    agent: context/explain
    prompt: I need clarification on one of these rules
---

## User Input

```text
$ARGUMENTS
```

Specify the task description and optional scope (e.g., `implement login feature in src/auth/`). If empty, uses current context.

## Outline

Goal: Retrieve the minimum viable context (rules, conventions, constraints) needed for a specific development task, avoiding context overflow.

1. **Initialize Environment**:
   - Run `.specify/scripts/bash/check-prerequisites.sh --json --paths-only` to get REPO_ROOT and paths.
   - Verify `.cursor/rules/` directory exists with rule files.

2. **Paso 1: Parsear Query del Usuario**:
   - **Acción**: Extraer `task`, `scope`, y `min_confidence` del input del usuario.
   - **Defaults**: Si no hay scope → usar directorio actual; si no hay confidence → 0.80.
   - **Análisis**: Determinar el tipo de tarea (implement, fix, refactor, test, docs).
   - **Verificación**: Task description tiene suficiente información para buscar reglas.
   - > **Si no puedes continuar**: Task vaga → **JIDOKA**: Pedir al usuario que especifique qué va a implementar (feature, fix, etc.).

3. **Paso 2: Escanear Reglas Disponibles**:
   - **Acción**: Leer todos los archivos `.mdc` en `.cursor/rules/`.
   - **Análisis**: Extraer YAML frontmatter de cada regla (name, description, globs, tags).
   - **Indexación**: Construir índice de reglas con: ID, nombre, globs aplicables, tags.
   - **Verificación**: Al menos 1 regla indexada.
   - > **Si no puedes continuar**: Sin reglas → **JIDOKA**: Ejecutar `/setup/generate-rules` primero para crear reglas base.

4. **Paso 3: Matching de Reglas (Determinista)**:
   - **Acción**: Para cada regla, evaluar si aplica al scope del task.
   - **Criterios de matching**:
     - Globs match con archivos del scope
     - Tags relacionados con tipo de tarea
     - Descripción semánticamente relevante
   - **Clasificar**:
     - `primary_rules`: Match directo con scope (incluir contenido completo)
     - `context_rules`: Match por tags/tipo (solo incluir resumen)
   - **Verificación**: Matching ejecutado sin errores.
   - > **Si no puedes continuar**: Error de glob → **JIDOKA**: Verificar sintaxis de globs en reglas; reportar regla malformada.

5. **Paso 4: Detectar Conflictos y Warnings**:
   - **Acción**: Analizar reglas seleccionadas buscando:
     - Conflictos entre reglas (instrucciones contradictorias)
     - Reglas deprecadas o con notas de migración
     - Confianza baja (regla marcada como provisional)
   - **Output**: Lista de `warnings` para el MVC.
   - **Verificación**: Análisis de conflictos completado.
   - > **Si no puedes continuar**: Conflicto crítico detectado → **JIDOKA**: Escalar al Orquestador para resolver antes de continuar.

6. **Paso 5: Construir y Entregar MVC**:
   - **Acción**: Ensamblar el MVC siguiendo la estructura canónica:
     ```yaml
     query:
       task: "[descripción de la tarea]"
       scope: "[path/pattern]"
       min_confidence: 0.80

     primary_rules:
       - id: "[ID]"
         name: "[nombre]"
         content: "[contenido completo de la regla]"

     context_rules:
       - id: "[ID]"
         name: "[nombre]"
         summary: "[resumen de 1-2 líneas]"

     warnings:
       - type: "[conflict|deprecated|low_confidence]"
         message: "[descripción]"
         affected_rules: ["[IDs]"]
     ```
   - **Presentación**: Mostrar MVC formateado al usuario.
   - **Verificación**: MVC contiene al menos 1 primary_rule o explicación de por qué no hay reglas aplicables.
   - > **Si no puedes continuar**: Sin reglas aplicables → Informar al usuario que no hay convenciones específicas para este scope; sugerir usar constitution como guía general.

7. **Finalize**:
   - Mostrar resumen: N primary rules, M context rules, K warnings.
   - Si hay warnings críticos, mostrar con prioridad.
   - Mostrar handoff: "→ Verificar compliance: `/context/check`"

## High-Signaling Guidelines

- **Output**: MVC estructurado (YAML o Markdown formateado).
- **Focus**: Precisión sobre completitud — menos reglas pero más relevantes.
- **Language**: Instructions English; Content **SPANISH**.
- **Jidoka**: Escalar si hay conflictos entre reglas que requieren decisión humana.

## AI Guidance

When executing this workflow:
1. **Determinism**: El matching de reglas DEBE ser reproducible. Mismo input = mismo output.
2. **Token Efficiency**: Solo incluir contenido completo de `primary_rules`. Context rules solo resumen.
3. **Transparency**: Explicar por qué cada regla fue incluida (match de glob, tag, o descripción).
4. **Graph Awareness**: Si existe un grafo de dependencias entre reglas, incluir subgrafo relevante.
5. **Fallback**: Si no hay reglas específicas, referenciar Constitution como fuente de principios.
