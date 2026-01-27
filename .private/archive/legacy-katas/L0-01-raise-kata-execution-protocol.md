---
id: principios-01-kata-execution-protocol
nivel: principios
tags: [meta-kata, raise, protocol, collaboration, execution, agent-autonomy]
---
# Meta-Kata del Protocolo de Ejecución y Colaboración

## Metadatos
- **Id**: principios-01-kata-execution-protocol
- **Nivel**: Principios (Meta-Kata)
- **Título**: Protocolo de Ejecución de Katas y Colaboración Humano-IA
- **Propósito**: Definir un protocolo de operación estándar, claro y auditable para la ejecución de cualquier Kata RaiSE, estableciendo un modelo de colaboración que equilibra la autonomía del Agente IA con la supervisión estratégica del Orquestador.
- **Contexto**: Esta Meta-Kata es la "fuente de verdad" sobre CÓMO se ejecutan otras Katas (de niveles flujo, patrón, técnica). Se aplica al inicio de cualquier sesión de trabajo que involucre la implementación de una Kata.
- **Audiencia**: Orquestador y Agente IA.

## Pre-condiciones
- Se ha seleccionado una Kata específica (la "Kata Objetivo") para ser ejecutada.
- El Orquestador Humano y el Agente IA han iniciado una sesión de trabajo.
- Se ha creado un documento de tracking de sesión, según lo estipulado en el "Paso 0" de la Kata Objetivo.

## Fases del Protocolo de Ejecución

Este protocolo consta de tres fases secuenciales que rigen el ciclo de vida de la ejecución de una Kata.

### Fase 1: Planificación y Aprobación (Punto de Partida Colaborativo)

- **Roles**:
  - **Agente IA**: Lidera la generación del plan detallado.
  - **Orquestador Humano**: Revisa, ajusta y aprueba el plan.
- **Acción**:
  1. El Agente IA analiza la "Kata Objetivo" seleccionada.
  2. A partir de los pasos de la Kata, el Agente genera un **"Plan de Implementación y Tracking"**. Este es un documento o una sección en el log de tracking que desglosa cada paso de la Kata en una checklist de tareas atómicas y ejecutables (ej: "Leer archivo X", "Analizar dependencias", "Proponer cambio Y", "Ejecutar prueba Z").
  3. El Agente presenta este plan detallado al Orquestador Humano para su revisión.
- **Entregable(s)**:
  - Un "Plan de Implementación y Tracking" detallado en formato de checklist.
- **Criterios de Aceptación**:
  - El Orquestador ha revisado el plan y confirma que representa fielmente las intenciones de la Kata Objetivo.
  - El Orquestador da su **aprobación explícita** al plan, lo que autoriza al Agente IA a proceder con la siguiente fase. Esta aprobación debe quedar registrada en el log de tracking.

**Verificación:** Existe un Plan de Implementación aprobado explícitamente por el Orquestador y registrado en el tracking.

> **Si no puedes continuar:** Plan no aprobado → Revisar feedback del Orquestador y ajustar el plan antes de solicitar nueva aprobación.

### Fase 2: Ejecución (Autonomía Supervisada del Agente)

- **Roles**:
  - **Agente IA**: Lidera la ejecución de las tareas.
  - **Orquestador Humano**: Supervisa pasivamente y está disponible para intervenir si se activa una condición de pausa.
- **Acción**:
  1. Una vez aprobado el plan, el Agente IA comienza a ejecutar las tareas de la checklist de forma **secuencial y autónoma**.
  2. Por cada tarea completada, el Agente actualiza la checklist en el documento de tracking, marcándola como "completada" y añadiendo un breve resumen del resultado o un enlace a la evidencia (ej: un commit hash, un log de prueba exitoso).
  3. El Agente continúa ejecutando el plan sin interrupción **a menos que** se encuentre con una de las "Condiciones de Pausa" definidas en la siguiente sección.
- **Criterios de Aceptación**:
  - El Agente completa todas las tareas del plan sin violar los guardrails de escalado.

**Verificación:** Todas las tareas de la checklist están marcadas como completadas con evidencia registrada.

> **Si no puedes continuar:** Tarea fallida después de dos intentos → Escalar al Orquestador siguiendo el protocolo de Condición 2.

### Fase 3: Post-Ejecución y Cierre

- **Roles**:
  - **Ambos**: Participan en la revisión final.
- **Acción**:
  1. Una vez que todas las tareas del plan han sido completadas, el Agente IA notifica al Orquestador Humano.
  2. Se realiza una revisión final para asegurar que se han cumplido todas las "Post-condiciones" de la Kata Objetivo.
  3. Se archiva el log de tracking como el registro auditable y final de la ejecución.
- **Post-condiciones**:
  - El "Plan de Implementación y Tracking" está completamente marcado como ejecutado.
  - Se han cumplido todos los objetivos y post-condiciones de la "Kata Objetivo".
  - Existe un registro completo y auditable de la sesión de trabajo.

**Verificación:** El log de tracking archivado contiene: plan aprobado, todas las tareas completadas con evidencia, y confirmación de post-condiciones cumplidas.

> **Si no puedes continuar:** Post-condiciones no cumplidas → Identificar tareas pendientes y regresar a Fase 2 para completarlas.

## Guardrails de Colaboración y Escalado (Condiciones de Pausa)

El Agente IA DEBE detener su ejecución autónoma y escalar al Orquestador Humano únicamente si se cumple una de las siguientes condiciones:

### Condición 1: Punto de Decisión Estratégica

- **Gatillo**: El Agente se encuentra ante múltiples caminos viables donde la elección impacta el diseño, la arquitectura o la estrategia, y la Kata Objetivo no prescribe una única opción.
- **Protocolo de Pausa y Escalado**:
  1. **Pausar la ejecución** y notificar al Orquestador.
  2. **Presentar el contexto**: Explicar claramente la encrucijada.
  3. **Exponer las opciones**: Listar las alternativas viables de forma estructurada.
  4. **Analizar y Recomendar**: Para cada opción, presentar un análisis conciso de pros y contras. Basado en este análisis y en el contexto del proyecto, el Agente debe **sustentar una recomendación**.
  5. **Esperar Instrucción**: El Agente permanecerá en pausa hasta recibir una directiva clara del Orquestador Humano.

### Condición 2: Error No Resuelto

- **Gatillo**: Una tarea del plan de implementación falla.
- **Protocolo de Pausa y Escalado**:
  1. **Primer Intento**: El Agente registra el error y el resultado.
  2. **Segundo Intento Autónomo**: El Agente debe intentar resolver el problema con una **estrategia diferente** y registrar su nuevo enfoque y el resultado.
  3. **Escalado (si el segundo intento falla)**:
      a. **Pausar la ejecución** y notificar al Orquestador.
      b. **Resumir la situación**: Presentar un informe claro que incluya:
          - La tarea que se intentaba ejecutar.
          - El enfoque y el resultado del primer intento fallido.
          - El enfoque y el resultado del segundo intento fallido.
          - Logs de error relevantes y concisos.
      c. **Solicitar Ayuda Específica**: Formular una pregunta concreta que guíe al Orquestador hacia una solución (ej: "¿La dependencia X es incorrecta? Sugiero las alternativas Y o Z. ¿Cuál prefieres?").
      d. **Esperar Instrucción**: El Agente permanecerá en pausa hasta recibir una solución o una nueva estrategia por parte del Orquestador.

## Notas Adicionales
- Este protocolo es la base de la confianza y eficiencia en la colaboración Humano-IA. Su seguimiento riguroso es mandatorio.
- El objetivo no es eliminar la intervención humana, sino asegurar que ocurra en los momentos de mayor valor estratégico. 