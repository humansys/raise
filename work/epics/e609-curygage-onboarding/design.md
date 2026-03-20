---
epic_id: "RAISE-609"
grounded_in: "Transcript daily 2026-03-20, brief.md, RAISE-594 (ACLI adapter)"
---

# Epic Design: CuryGage RaiSE Onboarding

## ¿Por qué este diseño existe?

Este no es un epic de desarrollo de software — es un epic de **habilitación metodológica**.
El output principal no es código nuevo en raise-commons, sino un equipo de CuryGage que puede
correr RaiSE de forma autónoma con su propio toolstack.

La pregunta central de diseño no es "¿cómo construimos X?" sino
**"¿cómo enseñamos RaiSE de forma que quede?"**

---

## Gemba — Lo que existe para construir encima

| Componente | Estado actual | Rol en este epic |
|------------|---------------|-----------------|
| `rai init --detect` | ✓ En 2.2.4 | Detecta convenciones del repo de CuryGage automáticamente |
| ACLI backlog adapter (RAISE-594) | ✓ Mergeado en dev | Conecta `rai backlog` con el Jira de ellos |
| Confluence adapter | 🔄 Emilio lo está haciendo | Permite `rai docs publish` a su Confluence |
| Skillset ecosystem (RAISE-242/476) | ✓ En 2.2.4 | Base para crear el skillset personalizado de CuryGage |
| `/rai-story-run` skill chain | ✓ Existente | El flujo que correremos en sesión 5 |
| `.raise/templates/` | ✓ En 2.2.4 | Governance templates que se populan en el init |

**Conclusión:** No necesitamos construir nada nuevo. El epic es conectar las piezas existentes
al contexto de CuryGage y enseñar a usarlas.

---

## Decisión de Diseño #1: Secuencia de las sesiones

**El principio de aprendizaje que aplica aquí se llama "desafío con soporte".**
Si empezamos con customización, el equipo no tiene contexto para decidir qué customizar.
Si empezamos solo con teoría, se aburren antes de ver valor.

La secuencia correcta es: **experiencia primero, abstracción después**.

```
Sesión 1 — Orientación: ¿Qué es RaiSE y por qué?
    ↓
    Aquí entendemos el "por qué" — la metodología lean, el flujo completo.
    Sin herramientas aún. Solo conversación y tour.

Sesión 2 — Primera historia: correr el flujo con skills genéricos
    ↓
    Aquí sienten el ciclo. /rai-story-run con una historia pequeña.
    Ven el output: scope, plan, commits, retrospectiva.

Sesión 3 — Integración: conectar su Jira y Confluence
    ↓
    Ahora que saben qué hace el flujo, conectamos sus herramientas.
    rai backlog muestra sus issues reales. rai docs publica a su Confluence.

Sesión 4 — Customización: crear su propio skillset
    ↓
    Solo hasta aquí customizamos. Ya saben qué cambiar y por qué.
    Workshop: revisar skills genéricos, identificar gaps, crear CuryGage skillset.

Sesión 5 — Prueba autónoma: historia real de su backlog
    ↓
    Con sus skills, sus adapters, su repo. Fer observa, no facilita.
    Jorge (stakeholder) puede estar presente para ver el output.
```

**Por qué este orden y no otro:**
- Customizar antes de experimentar → decisiones sin contexto
- Integrar antes de entender el flujo → confusión sobre qué integra con qué
- Sesión 5 autónoma → la prueba real de que aprendieron, no solo siguieron instrucciones

---

## Decisión de Diseño #2: Un equipo piloto, no todos

**Tentación:** onboardear varios equipos simultáneamente para ir más rápido.

**Por qué no:** El skillset y las convenciones de governance se definen durante el onboarding.
Si múltiples equipos lo hacen en paralelo, convergen en convenciones distintas y después
hay que hacer un trabajo de normalización costoso.

**Regla:** Piloto con un equipo → validar → escalar. El segundo equipo llega con un
skillset ya probado y una facilitation guide ya escrita.

---

## Decisión de Diseño #3: Skills genéricos primero, customización al final

**Rabbit hole a evitar:** crear el skillset perfecto de CuryGage antes de que hayan
usado los skills genéricos.

**Por qué importa:** Los skills genéricos representan años de iteración sobre qué funciona.
CuryGage solo necesita customizar lo que *genuinamente* choca con su contexto — no todo.
Si customizamos primero, terminamos manteniendo una divergencia innecesaria.

**Criterio de customización en sesión 4:**
> "¿Esto choca con algo específico de CuryGage, o solo se siente diferente?"
> Solo customizar lo que choca.

---

## Artifacts del epic — ¿qué producimos?

| Artifact | Quién lo usa | Cuándo |
|----------|-------------|--------|
| Plan de sesiones (`S609.1`) | Emilio para aprobar, Fer para facilitar | Antes de la semana de onboarding |
| Repo bootstrappeado (`S609.2`) | Equipo CuryGage | Desde sesión 1 |
| Adapters validados (`S609.3`) | Equipo CuryGage en sesión 3+ | Sesión 3 en adelante |
| Skillset CuryGage (`S609.4`) | Equipo CuryGage en sesión 4+ | Sesión 4 en adelante |
| Demo story + facilitation guide (`S609.5`) | Fer (guía), equipo CuryGage (la corre) | Sesión 5 |

---

## Estructura del skillset CuryGage (S609.4)

El skillset no se crea desde cero — se crea como **fork del skillset base** de RaiSE
con overrides específicos para CuryGage. La estructura esperada:

```
.claude/skills/
  rai-story-start/     ← override: título en formato CuryGage
  rai-story-run/       ← override: incluye paso de Jira/Confluence automático
  curygage-story-start/  ← skill nuevo si tienen proceso específico de inicio
```

**Criterio de inclusión:** un skill entra al skillset de CuryGage solo si tiene
una diferencia observable con el genérico. Si la única diferencia es el nombre de la empresa
en algún template, no merece un override.

---

## Facilitación (para Fer)

Este epic tiene un actor clave que no es el usuario típico: **Fer como facilitador**.
El facilitation guide (S609.5) debe responder:

1. **¿Qué hace Fer si el ambiente falla en sesión 2?** → fallback: correr en repo sandbox
2. **¿Qué hace Fer si el equipo se dispersa?** → redirigir al parking lot, igual que Rai hace con Fer
3. **¿Cómo maneja Fer preguntas sobre features que no existen?** → parking lot para post-piloto
4. **¿Cómo sabe Fer que sesión 5 fue exitosa?** → equipo corrió la historia sin intervención de Fer

---

## Sin ADRs formales

Este epic no requiere ADRs. Las tres decisiones de diseño arriba (secuencia, piloto único,
customización al final) son decisiones de metodología pedagógica, no de arquitectura de software.
Son reversibles con bajo costo y no tienen dependencias con otros epics técnicos.

Si en S609.4 descubrimos que el skillset de CuryGage requiere cambios en el CLI,
**ese hallazgo se convierte en un ticket nuevo**, no en scope de este epic.
