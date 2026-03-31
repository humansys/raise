---
title: Tu Primera Historia
description: Recorre el ciclo de vida completo de una story — desde el scope hasta código mergeado — usando skills de RaiSE.
---

Esta guía te lleva a través del ciclo de vida completo de una story usando skills de RaiSE. Al final, habrás experimentado el ritmo que hace la ingeniería asistida por IA confiable y repetible.

## Antes de Empezar

Asegúrate de tener:
- Un [proyecto RaiSE inicializado](../getting-started.md/
- Un asistente de IA funcionando (se recomienda Claude Code)
- Una feature pequeña para construir (algo que puedas terminar en una sesión)

Inicia una sesión:

```bash
rai session start --project . --context
```

Pasa el bundle de contexto a tu asistente de IA.

## Paso 1: Iniciar la Story

Toda story comienza con `/rai-story-start`. Esto crea un branch y documenta qué estás construyendo.

```
/rai-story-start S1.1 Agregar saludo de usuario
```

Tu IA va a:
1. Crear un branch de story (`story/s1.1/agregar-saludo-usuario`)
2. Escribir un documento de scope con criterios de inclusión/exclusión
3. Crear el scope commit

El documento de scope captura qué está **en scope**, qué está **fuera de scope** y cómo luce el **done**. Esto previene el scope creep — una feature que era "solo un saludo" no se convierte en un sistema de autenticación.

## Paso 2: Diseñar la Especificación

Después, `/rai-story-design` crea una especificación lean.

```
/rai-story-design S1.1 Agregar saludo de usuario
```

Tu IA va a:
1. Evaluar la complejidad (simple, moderada, compleja)
2. Enmarcar el problema y el valor
3. Describir el approach
4. Escribir ejemplos concretos
5. Definir criterios de aceptación

El documento de diseño está optimizado tanto para revisión humana como para implementación por IA. Los ejemplos son la parte más importante — ejemplos concretos y ejecutables le dicen a la IA exactamente qué construir.

Para features simples, puedes saltar el diseño e ir directamente a la planificación.

## Paso 3: Planificar la Implementación

`/rai-story-plan` descompone la story en tareas atómicas.

```
/rai-story-plan S1.1 Agregar saludo de usuario
```

Tu IA va a:
1. Dividir la feature en tareas pequeñas e independientes
2. Definir criterios de verificación para cada tarea
3. Mapear dependencias entre tareas
4. Establecer el orden de ejecución

Cada tarea debe ser individualmente committeable y verificable. El plan incluye un ciclo TDD: escribir un test que falle (RED), hacer que pase (GREEN), limpiar (REFACTOR).

## Paso 4: Implementar

`/rai-story-implement` ejecuta el plan tarea por tarea.

```
/rai-story-implement S1.1 Agregar saludo de usuario
```

Tu IA va a:
1. Tomar la siguiente tarea del plan
2. Escribir el test que falla
3. Implementar el código mínimo para pasar
4. Verificar (tests, linting, type checks)
5. Hacer commit
6. Pausar para tu revisión (checkpoint HITL)
7. Repetir hasta completar todas las tareas

El ritmo clave aquí: **implementar → verificar → commit → pausar**. Después de cada tarea, tu IA se detiene y te muestra qué se hizo. Tú revisas, apruebas y pasa a la siguiente tarea.

## Paso 5: Revisar

Después de la implementación, `/rai-story-review` captura aprendizajes.

```
/rai-story-review S1.1 Agregar saludo de usuario
```

Tu IA va a:
1. Recopilar datos: tiempo real vs. estimado, desviaciones del plan
2. Responder cuatro preguntas heutagógicas:
   - ¿Qué aprendiste?
   - ¿Qué cambiarías del proceso?
   - ¿Hay mejoras para el framework?
   - ¿De qué eres más capaz ahora?
3. Identificar mejoras de proceso
4. Persistir patrones valiosos a memoria

Aquí es donde la memoria se acumula. Un patrón aprendido aquí aparece en sesiones futuras.

## Paso 6: Cerrar

Finalmente, `/rai-story-close` mergea y limpia.

```
/rai-story-close S1.1 Agregar saludo de usuario
```

Tu IA va a:
1. Verificar que todos los criterios de done se cumplan
2. Mergear el branch de story al branch del epic (o desarrollo)
3. Eliminar el branch de story
4. Actualizar el tracking

## El Ritmo

Después de unas pocas stories, el ritmo se vuelve natural:

```
scope → diseño → plan → construir → reflexionar → cerrar
```

Cada paso produce un artefacto. Cada artefacto alimenta el siguiente paso. La retrospectiva alimenta la memoria, que alimenta sesiones futuras. Así es como RaiSE acumula aprendizaje — no por magia, sino por repetición disciplinada.

## Tips

- **Empieza pequeño.** Tu primera story debería ser XS o S. Primero domina el ritmo, luego escala.
- **No te saltes la review.** La retrospectiva es donde sucede el aprendizaje. Es tentador saltarla cuando estás emocionado por empezar la siguiente feature — resiste ese impulso.
- **Confía en los gates.** Los gates de verificación existen por una razón. Cuando un gate falla, arregla el problema antes de continuar.
- **Commit después de cada tarea.** No al final de la story. Cada tarea tiene su propio commit. Esto crea un historial limpio y facilita el debugging.
