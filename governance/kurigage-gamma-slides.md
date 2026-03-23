# Kurigage × RaiSE
## Plan de Integración — Semana del 24 de marzo

---

# Contexto

- Kurigage lleva ~1 mes usando RaiSE con skills genéricos
- Ya conocen el flujo y han desarrollado con él
- Esta semana: integrar sus herramientas + entregarles un skillset propio

**Meta al viernes:** autónomos — no dependientes de HumanSys

---

# La semana en 5 sesiones

```
Lunes        Martes        Miércoles      Jueves        Viernes
  S1            S2              S3            S4            S5
 Jira      Confluence     Skillset I    Skillset II    Historia
  ↓              ↓              ↓             ↓             ↓
adapter       adapter       guiado        autónomo      completa
operativo    operativo      primer        sin Fer       su Jira,
                            override      interviniendo  de cabo
                                                        a rabo
```

Cada sesión depende de la anterior. Si una entrada no está, la sesión no corre.

---

# S1 — Lunes · Jira

**Objetivo:** `rai backlog` operativo con su Jira en Windows

### Necesitamos antes de entrar

- raise-cli 2.2.4 instalado en Windows _(HumanSys)_
- ACLI instalado y autenticado _(Kurigage)_
- URL de Jira + project key _(Kurigage)_
- Repo disponible para `rai init` _(Kurigage)_

### Lo que hacemos

- `rai init --detect` en su repo
- Configurar `.raise/jira.yaml`
- Validar: `search`, `get`, `transition`, `comment`

### Sale de esta sesión

- `.raise/jira.yaml` commiteado
- Captura de `rai backlog search` con sus issues reales

---

# S2 — Martes · Confluence

**Objetivo:** `rai docs publish` operativo con su Confluence

### Necesitamos antes de entrar

- Confluence adapter (Emilio) disponible en 2.2.4
- URL de Confluence + space key _(Kurigage)_
- Acceso admin _(Kurigage)_

> ⚠ Si el adapter no está: **swap S2↔S3** — skillset adelanta, Confluence cierra la semana

### Lo que hacemos

- Instalar y configurar Confluence adapter
- Crear `.raise/confluence.yaml`
- Publicar documento de prueba end-to-end

### Sale de esta sesión

- `.raise/confluence.yaml` commiteado
- Página de prueba visible en su Confluence

---

# S3 — Miércoles · Skillset (guiado)

**Objetivo:** Entienden cómo funciona un skillset y escriben su primer override

### Necesitamos antes de entrar

- Scaffold base de Kurigage _(HumanSys, preparado antes del lunes)_
- Sus procesos actuales documentados _(cuestionario — ver slide siguiente)_

### Lo que hacemos

- Fer presenta el scaffold: archivos, estructura, propósito
- Revisamos juntos sus respuestas del cuestionario
- Identifican el primer skill a customizar (generalmente `story-start`)
- **Ellos escriben el override — Fer acompaña, no escribe**

### Sale de esta sesión

- `kurigage-story-start/SKILL.md` primer skill propio, commiteado por ellos

---

# El cuestionario de procesos

Necesitamos capturar cómo trabajan **hoy**, no cómo creen que deberían trabajar.

Sus "skills" existen como práctica informal — convenciones que el equipo conoce pero nunca nadie escribió. El cuestionario las hace explícitas.

**10 secciones:**

1. Origen del requerimiento
2. Planeación y priorización
3. Diseño técnico
4. Implementación (branches, commits, tests)
5. Revisión de código (PR / code review)
6. Pruebas
7. Documentación
8. Deploy a producción
9. Cierre de la historia
10. Excepciones y casos especiales

> **Enviar antes del martes al final del día.**
> Sin respuestas, los overrides serán genéricos y tendrán que rehacerse.

---

# S4 — Jueves · Skillset (autónomo)

**Objetivo:** El equipo agrega skills sin que Fer intervenga

### Necesitamos antes de entrar

- Skill de S3 funcionando
- Lista de otros procesos a encodificar (de su cuestionario + S3)

### Lo que hacemos

- El equipo decide qué skill customizar a continuación
- Fer está presente pero **solo responde preguntas directas**
- Al cierre: revisión de qué quedó y qué podrían agregar solos

### Sale de esta sesión

- 2+ skills customizados (`story-start` + `story-close` mínimo)
- Guía corta: "cómo agregar un skill" — para que continúen solos

---

# S5 — Viernes · Historia completa

**Objetivo:** Historia real de su backlog, de principio a fin, con sus herramientas y sus skills

### Necesitamos antes de entrar

- Jira + Confluence operativos (de S1-S2)
- Skillset con al menos 2 skills (de S3-S4)
- Historia pequeña seleccionada de su Jira _(Kurigage)_

### Lo que hacemos

- Flujo completo: backlog → scope → plan → implement → docs → close
- **Fer observa, no facilita**
- Si algo falla: se resuelve en sesión — eso es parte del aprendizaje

### Sale de esta sesión

- Historia cerrada en Jira con traceabilidad completa
- Documento publicado en Confluence (generado por RaiSE, no manualmente)
- Retrospectiva del programa: qué funcionó, qué ajustar, qué sigue

---

# ¿Por qué 5 sesiones y no menos?

**S1-S2 solo adapters** → los adapters tienen edge cases que no se ven hasta que se tocan: permisos, workflows customizados, campos obligatorios, diferencias en Windows. Necesitamos ese margen.

**S3 guiada, S4 autónoma — intencional** → si fueran una sola sesión, el resultado sería "nos enseñaron". Con dos, el resultado es "aprendimos".

**S5 no es buffer disfrazado** → es la diferencia entre "nos configuraron las herramientas" y "somos autónomos con RaiSE". Sin S5 el programa cierra en setup, no en autonomía.

---

# Contingencias

| Situación | Acción |
|-----------|--------|
| Confluence adapter no listo | Swap S2↔S3 — skillset adelanta |
| Problemas de acceso en S1 | Sandbox como fallback técnico |
| Kurigage no respondió cuestionario | Primera hora de S3 se usa para levantarlo |
| S3-S4 van rápido | S5 se convierte en historia más ambiciosa |

---

# Checklist de preparación

### HumanSys — antes del lunes
- [ ] raise-cli 2.2.4 instalado en Windows (entorno Kurigage)
- [ ] Skillset scaffold base de Kurigage preparado
- [ ] Cuestionario de procesos enviado a Kurigage

### Kurigage — antes del lunes
- [ ] Acceso admin a Jira + project key
- [ ] Acceso admin a Confluence + space key
- [ ] ACLI instalado en la máquina de las sesiones
- [ ] Repo disponible para `rai init`
- [ ] Cuestionario respondido antes del **miércoles**
- [ ] Historia pequeña seleccionada para el **viernes**
