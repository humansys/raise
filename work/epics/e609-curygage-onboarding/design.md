---
epic_id: "RAISE-609"
grounded_in: "Transcript daily 2026-03-20, brief.md, RAISE-594 (ACLI adapter)"
corrected: "2026-03-20 — Kurigage ya sabe RaiSE, scope reducido a integración"
---

# Epic Design: Kurigage RaiSE Integration

## Contexto que cambia todo

Kurigage lleva ~1 mes usando RaiSE. Ya corren historias. Ya conocen los skills.
El diseño original asumía un onboarding desde cero — eso era incorrecto.

**El problema real no es enseñar RaiSE. Es conectar sus herramientas.**

Hoy trabajan con workarounds: sus issues de Jira los manejan fuera del flujo de RaiSE,
su documentación va a Confluence manualmente. El epic resuelve esa fricción.

---

## Gemba — Lo que existe

| Componente | Estado | Rol en este epic |
|------------|--------|-----------------|
| ACLI backlog adapter (RAISE-594) | ✓ En dev/2.2.4 | Conecta `rai backlog` con Jira de Kurigage |
| Confluence adapter | 🔄 Emilio en progreso | Conecta `rai docs publish` con su Confluence |
| Skillset ecosystem (`rai skill set`) | ✓ En 2.2.4 | Mecanismo para crear y distribuir skillsets |
| Skills base en `.claude/skills/` | ✓ Existentes | Punto de partida para el fork de Kurigage |
| `rai init --detect` | ✓ En 2.2.4 | Detecta convenciones existentes del repo |

**Lo que NO necesitamos construir:** lógica nueva en el CLI. Todo existe.
Este epic es configuración + scaffold + validación.

---

## S609.1 — Adapter Setup: ¿qué implica realmente?

El ACLI Jira adapter requiere que el entorno de Kurigage tenga:
- `atlassian-plugin-sdk` o ACLI instalado y autenticado con su instancia
- Variables de entorno o `.raise/jira.yaml` apuntando a su Jira

El flujo de validación es secuencial:

```
1. rai adapter list              → confirmar que jira aparece
2. rai adapter check             → validar que el adapter pasa protocol checks
3. rai backlog search "type = Story" -a jira   → retorna issues reales
4. rai backlog get <KEY>         → detalle de un issue
5. rai backlog transition <KEY> in-progress    → write test
```

Si Confluence está listo: mismo patrón con `rai docs publish`.
Si no: documentar el estado, no bloquear S609.2.

---

## S609.2 — Skillset Scaffold: ¿qué es lo mínimo útil?

El objetivo no es darles un skillset completo — es darles la **estructura correcta**
para que ellos lo evolucionen. Un skillset sobreingenierado que no entienden es peor
que uno mínimo que pueden mantener.

**Scaffold mínimo útil:**

```
.claude/skills/
  curygage-story-start/
    SKILL.md          ← override con su convención de nombres de branch
  curygage-story-close/
    SKILL.md          ← override con su política de merge (PR a Bitbucket)
  rai-session-start/  ← override opcional si tienen contexto propio
    SKILL.md
```

**Por qué solo story-start y story-close:**
Son los dos puntos donde sus convenciones divergen más de los genéricos:
- `story-start`: naming de branches, convención de Jira keys
- `story-close`: merge policy, PR a Bitbucket en lugar de GitLab

El resto de los skills (design, plan, implement, review) es suficientemente genérico
para usarlos sin cambios. Si necesitan overrides adicionales, ellos mismos los agregarán.

**La guía de "cómo modificar un skill" debe responder:**
1. ¿Dónde va el archivo?
2. ¿Qué estructura tiene un SKILL.md?
3. ¿Cómo sabe RaiSE cuál skill usar (lookup order)?
4. ¿Cómo valido que mi skill funciona? (`rai skill validate`)

---

## S609.3 — Integration Validation: la prueba real

No es una demo preparada — es correr una historia real de su backlog con:
- `rai backlog get <KEY>` para leer el issue
- `/rai-story-run` completo con sus skills
- `rai docs publish` al final hacia Confluence

Si algo falla aquí, es un bug real que hay que resolver antes de considerar el epic cerrado.

---

## Decisión: 5 sesiones — ¿por qué no menos?

Las integraciones siempre tardan más de lo esperado. 3 sesiones son suficientes si
todo sale a la primera; 5 sesiones son lo correcto porque permiten que *algo* falle
sin que eso rompa el programa.

```
S1 — Repo + Jira básico (½ día)
  rai init en su repo. Jira adapter configurado. rai backlog search funciona.
  Quién: Fer + dev de Kurigage con acceso admin a Jira

S2 — Jira profundo (½ día)
  Flujo completo de backlog: get, transition, comment.
  El equipo corre un ciclo sin que Fer les diga cada paso.
  Por qué una sesión entera: Jira tiene edge cases (permisos, workflows customizados,
  campos obligatorios en transitions) que no se ven hasta que se usan.

S3 — Confluence (½ día)
  Adapter de docs + rai docs publish. Flujo de documentación.
  Puede moverse al final de la semana si el adapter de Emilio no está listo.

S4 — Skillset workshop (½ día)
  Revisión conjunta del scaffold. Ellos hacen el primer override solos.
  Por qué tarda: no es que sea difícil — es que tienen que decidir qué customizar.
  Esa conversación ("¿cambiamos esto o dejamos el genérico?") lleva tiempo.

S5 — Historia end-to-end (½ día)
  Historia real de su backlog. Fer observa, no facilita.
  Por qué existe aunque todo haya salido bien: la autonomía se prueba, no se asume.
  Si algo falló en S1-S4, S5 lo absorbe.
```

**La sesión 5 no es relleno** — es el momento donde el equipo demuestra (y siente)
que pueden hacerlo solos. Sin ese cierre, el programa queda como "nos ayudaron a configurar",
no como "ahora somos autónomos".

---

## Sin ADRs

No hay decisiones de arquitectura de software en este epic.
Las decisiones de diseño arriba son de alcance y de entrega — no requieren ADR formal.
