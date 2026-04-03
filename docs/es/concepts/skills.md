---
title: Skills
description: Proceso-como-código — workflows repetibles que guían tanto al humano como a la IA a través de tareas de ingeniería complejas.
---

Los skills son el proceso-como-código de RaiSE. Cada skill es un workflow estructurado — un archivo `SKILL.md` — que guía tanto a ti como a tu partner de IA a través de una actividad de ingeniería específica. Piensa en ellos como runbooks que tu IA puede seguir, no solo leer.

## Cómo Luce un Skill

Un skill es un archivo markdown en `.claude/skills/<nombre>/SKILL.md` con:

- **Propósito** — qué hace este skill y cuándo usarlo
- **Pasos** — secuencia ordenada con gates de verificación en cada paso
- **Niveles de maestría** — Shu (seguir exactamente), Ha (adaptar), Ri (crear el tuyo)
- **Entradas y salidas** — qué necesita, qué produce

Cuando invocas un skill (ej. `/rai-story-plan`), tu IA carga el SKILL.md y sigue sus pasos — verificando prerequisitos, ejecutando cada paso, verificando resultados y produciendo salida documentada.

## El Ciclo de Vida de una Story

La cadena de skills más importante es el ciclo de vida de una story — la secuencia que lleva una feature desde la idea hasta código mergeado:

```
/rai-story-start    → Crear branch y scope commit
      ↓
/rai-story-design   → Diseñar la especificación
      ↓
/rai-story-plan     → Descomponer en tareas atómicas
      ↓
/rai-story-implement → Ejecutar tareas con TDD
      ↓
/rai-story-review   → Retrospectiva y aprendizajes
      ↓
/rai-story-close    → Verificar, mergear, limpiar
```

Cada paso produce un artefacto (scope.md, design.md, plan.md, progress.md, retrospective.md) y tiene gates de verificación que deben pasar antes de continuar. Esto no es burocracia — es cómo aseguras consistencia y trazabilidad entre sesiones.

## Ciclos de Vida de Skills

Los skills se organizan por el ciclo de vida de trabajo al que pertenecen:

| Ciclo de Vida | Skills | Cuándo |
|---------------|--------|--------|
| **Session** | `/rai-session-start`, `/rai-session-close` | Cada sesión de trabajo |
| **Story** | `/rai-story-start` hasta `/rai-story-close` | Para cada feature |
| **Epic** | `/rai-epic-start` hasta `/rai-epic-close` | Para cuerpos de trabajo multi-story |
| **Discovery** | `/rai-discover-start` hasta `/rai-discover-document` | Al analizar un codebase |

## Skills vs. CLI

Esta distinción importa:

- **Skills** guían el *proceso* — le dicen a ti y a tu IA qué hacer, en qué orden, con qué verificación
- **CLI** maneja los *datos* — lee, escribe, construye y consulta determinísticamente

Un skill como `/rai-story-plan` le dice a la IA que descomponga una story en tareas. El comando CLI `rai signal emit-work` registra el evento. El skill orquesta; el CLI ejecuta.

## Niveles de Maestría (ShuHaRi)

Cada skill soporta tres niveles de maestría, tomados de las artes marciales:

- **Shu (守)** — Seguir la forma exactamente. Para practicantes nuevos o tipos de skill nuevos.
- **Ha (破)** — Adaptar la forma. Saltar pasos opcionales, ajustar al contexto. Para practicantes experimentados.
- **Ri (離)** — Trascender la forma. Crear patrones propios. Para expertos que entienden los principios lo suficientemente profundo como para improvisar.

Tu nivel de experiencia se registra en tu perfil de desarrollador y se incluye en el bundle de contexto. En nivel Shu, los skills dan explicaciones detalladas. En nivel Ri, muestran solo lo esencial.

## Gates de Verificación

Cada paso de un skill tiene un criterio de verificación — un chequeo concreto de que el paso se completó correctamente. Si la verificación falla, el skill se detiene (principio Jidoka: detenerse ante defectos, no acumular errores).

Ejemplos de gates de verificación:
- "Existe el branch del epic" antes de crear un branch de story
- "Existe el plan" antes de iniciar implementación
- "Los tests pasan" antes de hacer commit
- "Retrospectiva completa" antes de mergear

## Gestionar Skills

```bash
# Listar todos los skills
rai skill list

# Validar estructura de skills
rai skill validate

# Crear nuevo skill desde plantilla
rai skill scaffold mi-nuevo-skill --lifecycle story

# Verificar convenciones de naming
rai skill check-name mi-nuevo-skill
```

Ver la [Referencia CLI](../cli/index.md/ para detalles completos.
