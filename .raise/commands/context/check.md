---
description: Verifies code compliance against applicable rules and reports violations.
handoffs:
  - label: Edit a rule
    agent: setup/edit-rule
    prompt: I want to modify a rule based on this check
  - label: Get context for fix
    agent: context/get
    prompt: Get MVC to fix the violations
---

## User Input

```text
$ARGUMENTS
```

Specify file path(s) or pattern to check (e.g., `src/auth/*.ts`). If empty, checks staged files or current directory.

## Outline

Goal: Validate code files against applicable rules and report compliance status with actionable feedback.

1. **Initialize Environment**:
   - Run `.specify/scripts/bash/check-prerequisites.sh --json --paths-only` to get REPO_ROOT and paths.
   - Verify `.cursor/rules/` directory exists.

2. **Paso 1: Determinar Scope de Verificación**:
   - **Acción**: Parsear input del usuario para identificar archivos a verificar.
   - **Estrategia**:
     - Si hay path explícito → usar ese path/pattern
     - Si vacío + hay staged files → usar staged files
     - Si vacío + sin staged → usar directorio actual
   - **Análisis**: Expandir globs y listar archivos concretos.
   - **Verificación**: Al menos 1 archivo identificado para verificar.
   - > **Si no puedes continuar**: Sin archivos → **JIDOKA**: Pedir al usuario que especifique archivos o use `git add` para stage.

3. **Paso 2: Cargar Reglas Aplicables**:
   - **Acción**: Para cada archivo, buscar reglas cuyo glob matchee.
   - **Análisis**: Construir mapa `{archivo: [reglas_aplicables]}`.
   - **Indexación**: Agrupar archivos por set de reglas para eficiencia.
   - **Verificación**: Mapa de reglas construido.
   - > **Si no puedes continuar**: Sin reglas para ningún archivo → Informar que no hay convenciones definidas para estos archivos; sugerir `/setup/generate-rules`.

4. **Paso 3: Ejecutar Verificación**:
   - **Acción**: Para cada par (archivo, regla):
     - Leer contenido del archivo
     - Parsear instrucciones de la regla
     - Verificar cumplimiento de cada instrucción verificable
   - **Clasificar resultados**:
     - `PASS`: Cumple con la regla
     - `WARN`: Cumplimiento parcial o caso ambiguo
     - `FAIL`: Violación clara de la regla
     - `SKIP`: Regla no aplicable a este archivo específico
   - **Verificación**: Verificación ejecutada para todos los pares.
   - > **Si no puedes continuar**: Error de lectura de archivo → **JIDOKA**: Verificar permisos y existencia del archivo.

5. **Paso 4: Generar Reporte de Compliance**:
   - **Acción**: Compilar resultados en reporte estructurado:
     ```markdown
     ## Compliance Report

     **Scope**: [archivos verificados]
     **Rules Applied**: [N reglas]
     **Overall Status**: [PASS/WARN/FAIL]

     ### Summary
     - PASS: N checks
     - WARN: M checks
     - FAIL: K checks

     ### Violations

     #### [archivo.ts]
     | Rule | Status | Line | Issue | Suggestion |
     |------|--------|------|-------|------------|
     | 200-clean-arch | FAIL | 45 | Import from wrong layer | Move to infrastructure/ |
     ```
   - **Priorización**: Mostrar FAILs primero, luego WARNs.
   - **Verificación**: Reporte generado con todos los resultados.
   - > **Si no puedes continuar**: Demasiadas violaciones (>50) → Mostrar resumen y top 10; ofrecer exportar reporte completo.

6. **Paso 5: Sugerir Acciones**:
   - **Acción**: Para cada violación, proponer acción concreta:
     - Código de ejemplo para fix
     - Referencia a sección de la regla
     - Handoff a `/context/get` para obtener contexto completo
   - **Análisis**: Agrupar violaciones similares para fixes en batch.
   - **Verificación**: Sugerencias generadas para violaciones.
   - > **Si no puedes continuar**: Violación sin fix claro → Marcar como "Requiere revisión manual" y sugerir `/context/explain [rule]`.

7. **Finalize**:
   - Mostrar status general (PASS/WARN/FAIL).
   - Si FAIL: Mostrar handoff "→ Obtener contexto para fix: `/context/get`"
   - Si PASS: Mostrar "Compliance verified. Ready for commit."
   - Opcionalmente, ofrecer guardar reporte en `specs/main/compliance-reports/`.

## High-Signaling Guidelines

- **Output**: Reporte de compliance con status claro y acciones.
- **Focus**: Actionability — cada violación con sugerencia concreta.
- **Language**: Instructions English; Content **SPANISH**.
- **Jidoka**: Si hay violaciones críticas (seguridad, arquitectura), escalar antes de continuar.

## AI Guidance

When executing this workflow:
1. **Precision**: Solo reportar violaciones claras. Ante ambigüedad, usar WARN no FAIL.
2. **Context**: Incluir línea de código y contexto suficiente para entender el issue.
3. **Actionable**: Cada FAIL debe tener sugerencia de fix o referencia a documentación.
4. **Batch Fixes**: Si detectas el mismo issue en múltiples archivos, sugerir fix en batch.
5. **Learning**: Si una regla genera muchos false positives, sugerir revisar con `/setup/edit-rule`.
