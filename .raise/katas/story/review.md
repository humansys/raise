---
id: review
titulo: "Review: Retrospective & Learning"
work_cycle: story
frequency: per-story
fase_metodologia: 7

prerequisites:
  - story/implement
template: null
gate: null
next_kata: null

adaptable: true
shuhari:
  shu: "Seguir las preguntas de retrospectiva estándar"
  ha: "Adaptar preguntas al contexto del equipo"
  ri: "Crear kata de Review para contextos específicos"

version: 1.0.0
---

# Review: Retrospective & Learning

## Propósito

Reflexionar sobre el feature completado para extraer aprendizajes, identificar mejoras al proceso, y actualizar el framework con insights ganados.

## Contexto

**Cuándo usar:**
- Después de completar un feature
- Antes de comenzar el siguiente feature
- Como cierre del ciclo de desarrollo

**Inputs requeridos:**
- Feature completado
- Registro de progreso
- Feedback del equipo

**Output:**
- Retrospectiva documentada
- Mejoras identificadas

## Pasos

### Paso 1: Recopilar Datos

Revisar el desarrollo del feature:
- Tiempo real vs estimado
- Blockers encontrados
- Desviaciones del plan

**Verificación:** Datos del feature recopilados.

> **Si no puedes continuar:** Sin datos → Reconstruir timeline de commits/PRs.

### Paso 2: Checkpoint Heutagógico

Responder las cuatro preguntas:
1. ¿Qué aprendiste?
2. ¿Qué cambiarías del proceso?
3. ¿Hay mejoras para el framework?
4. ¿En qué eres más capaz ahora?

**Verificación:** Las cuatro preguntas respondidas.

> **Si no puedes continuar:** Respuestas vagas → Ser más específico con ejemplos concretos.

### Paso 3: Identificar Mejoras de Proceso

Listar mejoras concretas:
- A las katas
- A las reglas
- A los templates

**Verificación:** Mejoras identificadas con owner.

> **Si no puedes continuar:** Sin mejoras → Celebrar el proceso y continuar.

### Paso 4: Actualizar Framework

Si hay mejoras identificadas:
- Actualizar katas relevantes
- Crear o modificar reglas
- Documentar decisiones

**Verificación:** Mejoras aplicadas al framework.

> **Si no puedes continuar:** Mejora compleja → Crear issue para futuro.

### Paso 5: Documentar Retrospectiva

Crear documento de retrospectiva:
- Resumen del feature
- Aprendizajes clave
- Mejoras aplicadas

**Verificación:** Retrospectiva documentada.

> **Si no puedes continuar:** N/A.

## Output

- **Artefacto:** Retrospectiva
- **Ubicación:** `work/stories/{feature}/retrospective.md`
- **Gate:** N/A
- **Siguiente kata:** Próximo feature o mejora continua

## Notas

### Kaizen

Esta kata implementa el principio Kaizen de mejora continua. Cada retrospectiva debe producir al menos una mejora concreta.

## Referencias

- Checkpoint Heutagógico: Glossary v2.1
- Kaizen: Toyota Production System
