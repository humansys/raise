# Kurigage — Plan de Integración RaiSE
**Interno HumanSys** · RAISE-609 · 2026-03-20

---

## Contexto

Kurigage lleva ~1 mes usando RaiSE con skills genéricos. Ya conocen el flujo y han
desarrollado con él. Esta semana los integramos con sus herramientas corporativas (Jira,
Confluence) y les entregamos un skillset propio que puedan mantener sin depender de nosotros.

**Equipo facilitador:** Fer (principal), Emilio (disponible para cobertura)
**Semana objetivo:** 2026-03-24

---

## Flujo de Artefactos por Sesión

Cada sesión tiene entradas que deben existir antes de empezar, y produce salidas que
la siguiente sesión necesita. Si una entrada no está lista, la sesión no puede correr.

```
ANTES de la semana
     ↓
[ S1: Jira ] ──salidas──► [ S2: Confluence ] ──salidas──► [ S3: Skillset I ]
                                                                   ↓
                                                          [ S4: Skillset II ]
                                                                   ↓
                                                          [ S5: Historia ]
```

---

## Las 5 Sesiones

### S1 — Lunes: Jira

**Objetivo:** `rai backlog` operativo con su Jira en Windows

#### Necesitamos antes de entrar
| Artefacto | Quién lo prepara | Estado |
|-----------|-----------------|--------|
| raise-cli 2.2.4 instalado en Windows | HumanSys (Fer) | Por hacer |
| ACLI instalado y autenticado en su máquina | Kurigage (dev con acceso admin) | Por confirmar |
| URL de su instancia de Jira + project key | Kurigage | Por confirmar |
| Acceso al repo donde haremos `rai init` | Kurigage | Por confirmar |

#### Lo que hacemos
- `rai init --detect` en su repo
- Configurar `.raise/jira.yaml` apuntando a su instancia
- Validar: `rai backlog search`, `get`, `transition`, `comment`

#### Salidas de esta sesión
| Artefacto | Descripción |
|-----------|-------------|
| `.raise/jira.yaml` | Adapter configurado y commiteado en su repo |
| `.raise/` inicializado | Governance scaffold en su repo |
| Validación documentada | Captura de `rai backlog search` retornando sus issues reales |

---

### S2 — Martes: Confluence

**Objetivo:** `rai docs publish` operativo con su Confluence

#### Necesitamos antes de entrar
| Artefacto | Quién lo prepara | Estado |
|-----------|-----------------|--------|
| Confluence adapter de Emilio disponible en 2.2.4 | HumanSys (Emilio) | En progreso |
| URL de su Confluence + space key | Kurigage | Por confirmar |
| Acceso admin a Confluence | Kurigage | Por confirmar |

> ⚠ Si el adapter no está listo: swap S2↔S3. Skillset adelanta, Confluence cierra la semana.

#### Lo que hacemos
- Instalar y configurar Confluence adapter
- Crear `.raise/confluence.yaml` en su repo
- Publicar un documento de prueba y verificar que aparece en Confluence

#### Salidas de esta sesión
| Artefacto | Descripción |
|-----------|-------------|
| `.raise/confluence.yaml` | Adapter configurado y commiteado |
| Página de prueba en Confluence | Evidencia de que el flujo funciona end-to-end |

---

### S3 — Miércoles: Skillset (guiado)

**Objetivo:** Equipo entiende cómo funciona un skillset y hace su primer override con acompañamiento

#### Necesitamos antes de entrar
| Artefacto | Quién lo prepara | Estado |
|-----------|-----------------|--------|
| Skillset scaffold base de Kurigage | HumanSys (Fer) | Por hacer antes de la semana |
| Lista de sus procesos actuales de desarrollo | Kurigage | **Ver nota abajo** |

> **Nota importante — procesos no documentados:**
> Es probable que Kurigage no tenga documentados formalmente sus pasos de desarrollo.
> Sus "skills" hoy existen como práctica informal — convenciones que el equipo conoce
> pero que nunca nadie escribió. Necesitamos hacerlas explícitas antes de S3 para que
> los overrides reflejen su realidad, no la nuestra.
>
> Enviar el cuestionario abajo antes del miércoles. Con esas respuestas construimos
> los overrides correctos. Sin ellas, el skillset será genérico y tendrá que rehacerse.

---

## Cuestionario de Procesos — Kurigage

> Enviar a Kurigage antes de S3 (miércoles). Pedir respuestas para el martes al final del día.
> El objetivo es capturar cómo trabajan HOY, no cómo creen que deberían trabajar.

### 1. Origen del requerimiento

*Queremos entender cómo nace una historia antes de llegar al equipo técnico.*

- ¿Quién define los requerimientos? ¿El cliente, producto, el líder técnico?
- ¿Los requerimientos llegan como tickets de Jira ya creados, o alguien del equipo técnico los crea?
- ¿Qué información mínima debe tener un ticket para que el equipo lo considere "listo para trabajar"?
  - ¿Tiene criterios de aceptación? ¿En qué formato?
  - ¿Tiene estimación? ¿Quién estima?
  - ¿Tiene diseño o mockup adjunto?
- ¿Tienen definición de "Ready"? ¿Está escrita en algún lado o es de palabra?

---

### 2. Planeación y priorización

*Queremos entender cómo deciden qué construir primero.*

- ¿Trabajan en sprints, kanban, o algo diferente?
- ¿Quién decide qué entra al sprint/iteración actual?
- ¿Cómo se asignan los tickets? ¿El líder asigna, cada quien toma, otro sistema?
- Cuando alguien va a tomar un ticket, ¿qué hace primero? ¿Lo lee, habla con alguien, algo más?

---

### 3. Diseño técnico

*Queremos entender qué pasa entre "ticket asignado" y "primera línea de código".*

- ¿El equipo hace diseño técnico antes de implementar? ¿Siempre, a veces, nunca?
- Si lo hacen, ¿dónde queda ese diseño? (comentario en Jira, página de Confluence, doc en el repo, de palabra)
- ¿Hay revisión del diseño con alguien antes de arrancar? ¿Con quién?
- ¿Qué tan grande tiene que ser una tarea para que merezca diseño técnico?

---

### 4. Implementación

*Queremos entender el flujo de código del equipo.*

- ¿Cómo nombran sus branches? Poner un ejemplo real: `_______________`
- ¿Branch desde dónde? (`main`, `dev`, otra rama?)
- ¿Hay convenciones de commit messages? Ejemplo: `_______________`
- ¿Corren tests localmente antes de hacer push? ¿Qué tipo de tests?
- ¿Hay linting o formateo automático? ¿Con qué herramienta?

---

### 5. Revisión de código (PR / Code Review)

*Queremos entender cómo validan el trabajo antes de integrarlo.*

- ¿Todo el código pasa por PR o hay excepciones?
- ¿Cuántos reviewers se requieren para aprobar?
- ¿Quién puede aprobar? ¿Solo el líder técnico, cualquier dev senior, cualquiera?
- ¿Hay un checklist de PR? ¿Está escrito o es de memoria? Si existe, ¿dónde está?
- ¿Qué cosas típicamente se rechaza en un PR? (para entender sus estándares reales)
- ¿Cuánto tiempo típicamente tarda un PR en ser revisado?

---

### 6. Pruebas

*Queremos entender qué tan automatizado está su proceso de QA.*

- ¿Tienen pruebas unitarias? ¿Son obligatorias o voluntarias?
- ¿Tienen pruebas de integración o end-to-end?
- ¿Hay un ambiente de QA / staging donde se prueba antes de producción?
- ¿Quién hace QA? ¿El mismo dev, un QA dedicado, el product owner?
- ¿Qué tiene que pasar para que algo se considere "probado"?

---

### 7. Documentación

*Queremos entender dónde vive el conocimiento del equipo.*

- ¿El equipo documenta lo que construye? ¿Siempre, a veces, cuando da tiempo?
- ¿Dónde va esa documentación? (Confluence, README en el repo, Notion, otra herramienta)
- ¿Qué tipo de documentación producen? (diseño, decisiones técnicas, guías de uso, API docs)
- ¿Hay alguien responsable de que la documentación exista, o es responsabilidad de cada dev?

---

### 8. Deploy a producción

*Queremos entender el último paso del ciclo.*

- ¿Tienen CI/CD? ¿Automatizado o manual?
- ¿Quién puede hacer deploy a producción? ¿Cualquier dev, solo el líder, un DevOps?
- ¿Hay un proceso de aprobación antes del deploy? ¿Quién aprueba?
- ¿Qué pasa después del deploy? ¿Alguien monitorea? ¿Por cuánto tiempo?
- ¿Cómo saben que el deploy fue exitoso?

---

### 9. Cierre de la historia

*Queremos entender cómo se cierra el ciclo en Jira y con el cliente.*

- ¿Cuándo transicionan un ticket a "Done"? ¿Después del merge, después del deploy, cuando el cliente lo valida?
- ¿Quién transiciona el ticket? ¿El dev, el PM, automático?
- ¿Le avisan al cliente/stakeholder cuando algo está listo? ¿Cómo?
- ¿Tienen retrospectivas? ¿Con qué frecuencia? ¿Qué formato usan?

---

### 10. Excepciones y casos especiales

*Las reglas reales se ven en los bordes.*

- ¿Qué pasa cuando hay un bug crítico en producción? ¿Cómo cambia el proceso?
- ¿Qué se saltean cuando hay presión de tiempo? (esto nos dice qué es opcional y qué es obligatorio)
- ¿Hay algo del proceso actual que el equipo considera que no funciona bien?

#### Lo que hacemos
- Fer presenta el scaffold: qué archivos hay, para qué sirve cada uno
- Revisamos juntos sus respuestas del cuestionario de procesos
- Identificamos el primer skill a customizar (generalmente `story-start`)
- Ellos escriben el override — Fer acompaña, no escribe

#### Salidas de esta sesión
| Artefacto | Descripción |
|-----------|-------------|
| `curygage-story-start/SKILL.md` | Primer skill customizado, commiteado por ellos |
| Cuestionario de procesos respondido | Base para S4 |

---

### S4 — Jueves: Skillset (autónomo)

**Objetivo:** El equipo agrega skills adicionales sin que Fer intervenga

#### Necesitamos antes de entrar
| Artefacto | Quién lo prepara | Estado |
|-----------|-----------------|--------|
| Skill de S3 funcionando | Kurigage (de S3) | Depende de S3 |
| Lista de otros procesos que quieren encodificar | Kurigage | De su cuestionario + S3 |

#### Lo que hacemos
- El equipo decide qué skill customizar a continuación
- Fer está presente pero no da instrucciones — solo responde preguntas directas
- Al cierre: revisión de qué quedó y qué podrían agregar solos después

#### Salidas de esta sesión
| Artefacto | Descripción |
|-----------|-------------|
| 2+ skills customizados en su repo | Mínimo: `story-start` + `story-close` |
| Guía "cómo agregar un skill" | Doc corto para que continúen solos post-programa |

---

### S5 — Viernes: Historia completa

**Objetivo:** Historia real de su backlog, de principio a fin, con sus herramientas y sus skills

#### Necesitamos antes de entrar
| Artefacto | Quién lo prepara | Estado |
|-----------|-----------------|--------|
| Jira + Confluence operativos (de S1-S2) | — | Depende de S1-S2 |
| Skillset con al menos 2 skills (de S3-S4) | Kurigage | Depende de S3-S4 |
| Historia pequeña seleccionada de su Jira | Kurigage | Seleccionar antes del viernes |

#### Lo que hacemos
- El equipo corre el flujo completo: backlog → scope → plan → implement → docs → close
- Fer observa, no facilita
- Si algo falla: se resuelve en sesión — eso es parte del aprendizaje

#### Salidas de esta sesión
| Artefacto | Descripción |
|-----------|-------------|
| Historia cerrada en Jira | Con traceabilidad completa |
| Documento publicado en Confluence | Generado por RaiSE, no manualmente |
| Retrospectiva del programa | Qué funcionó, qué ajustar, qué sigue |

---

## Por qué 5 sesiones y no menos

Las integraciones tienen edge cases que no se ven hasta que se tocan: permisos de Jira,
workflows customizados, campos obligatorios en transitions, diferencias de entorno en Windows.
Dedicar S1-S2 solo a adapters nos da margen para resolver esos problemas sin presión.

Las dos sesiones de skillset (S3 guiada, S4 autónoma) son intencionales: la primera
para que entiendan cómo funciona, la segunda para demostrar que pueden hacerlo solos.
Si fueran una sola sesión, quedaría como "nos enseñaron" en lugar de "aprendimos".

S5 no es buffer disfrazado. Es la diferencia entre "nos configuraron las herramientas"
y "somos autónomos con RaiSE". Sin esa sesión el programa cierra en setup, no en autonomía.

---

## Contingencias

| Situación | Acción |
|-----------|--------|
| Confluence adapter no listo para S2 | Swap S2↔S3 — skillset adelanta, Confluence cierra la semana |
| Problemas de acceso/permisos en S1 | Sandbox como fallback para validar el flujo técnico |
| Kurigage no respondió el cuestionario antes de S3 | Dedicar primera hora de S3 a levantarlo — acorta el tiempo de override |
| S3-S4 van rápido | S5 se convierte en historia más ambiciosa o segunda historia |

---

## Checklist de Preparación

### HumanSys debe tener listo antes del lunes
- [ ] raise-cli 2.2.4 instalado en Windows (entorno de Kurigage)
- [ ] Skillset scaffold base de Kurigage preparado localmente
- [ ] Cuestionario de procesos enviado a Kurigage para que respondan antes de S3

### Kurigage debe tener listo antes del lunes
- [ ] Acceso admin a Jira + project key de su proyecto
- [ ] Acceso admin a Confluence + space key
- [ ] ACLI instalado en la máquina donde correrán las sesiones
- [ ] Repo disponible para hacer `rai init`
- [ ] Cuestionario de procesos respondido antes del miércoles (para S3)
- [ ] Historia pequeña seleccionada para el viernes (S5)
