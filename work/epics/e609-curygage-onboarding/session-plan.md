# CuryGage — Plan de Integración RaiSE
**Interno HumanSys** · RAISE-609 · 2026-03-20

---

## Contexto

CuryGage lleva ~1 mes usando RaiSE con skills genéricos. Ya conocen el flujo y han
desarrollado con él. Esta semana los integramos con sus herramientas corporativas (Jira,
Confluence) y les entregamos un skillset propio que puedan mantener sin depender de nosotros.

**Equipo facilitador:** Fer (principal), Emilio (disponible para cobertura)
**Semana objetivo:** 2026-03-24

---

## Las 5 Sesiones

### S1 — Lunes: Jira
**Objetivo:** `rai backlog` operativo con su Jira en Windows

Lo que hacemos:
- `rai init --detect` en su repo
- Configurar ACLI adapter apuntando a su instancia de Jira
- Validar: search, get, transition, comment

**Output concreto:** El equipo puede buscar y actualizar sus issues de Jira desde el CLI.

---

### S2 — Martes: Confluence
**Objetivo:** `rai docs publish` operativo con su Confluence

Lo que hacemos:
- Configurar Confluence adapter
- Validar flujo completo: generar doc → publicar → ver en Confluence

**Output concreto:** La documentación que genera RaiSE llega a Confluence sin pasos manuales.

> ⚠ Depende del adapter que está terminando Emilio. Si no está listo, swap con S3 — el skillset no requiere acceso a su entorno.

---

### S3 — Miércoles: Skillset (guiado)
**Objetivo:** Equipo entiende cómo funciona un skillset y hace su primer override

Lo que hacemos:
- Fer presenta el scaffold base de CuryGage (ya preparado)
- Revisamos juntos: ¿qué skill cambian primero y por qué?
- Ellos hacen el override — Fer acompaña pero no escribe el código

**Output concreto:** Un skill customizado commiteado en su repo, hecho por ellos.

---

### S4 — Jueves: Skillset (autónomo)
**Objetivo:** El equipo agrega skills adicionales sin que Fer intervenga

Lo que hacemos:
- Ellos identifican qué más customizar
- Fer está disponible para preguntas, no da instrucciones
- Al final: revisión de lo que quedó vs. lo que podría agregarse después

**Output concreto:** 2+ skills propios en su repo. Equipo sabe cómo agregar más.

---

### S5 — Viernes: Historia completa
**Objetivo:** Una historia real de su backlog, de principio a fin, con sus herramientas

Lo que hacemos:
- El equipo elige una historia pequeña de su Jira
- Corren el flujo completo: backlog → scope → plan → implement → docs → close
- Fer observa, no facilita

**Output concreto:** Historia cerrada. Evidencia de autonomía.

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
| Confluence adapter no listo para S2 | Swap S2↔S3 — skillset adelanta, Confluence al final de la semana |
| Problemas de acceso/permisos en S1 | Sandbox environment como fallback para validar el flujo técnico |
| S3-S4 van rápido | S5 se convierte en historia más ambiciosa o segunda historia |

---

## Prep antes del lunes

- [ ] Instalar raise-cli 2.2.4 en el entorno Windows de CuryGage
- [ ] Configurar ACLI con su instancia de Jira
- [ ] Preparar skillset scaffold base (puede hacerse antes sin acceso a su entorno)
- [ ] Confirmar con CuryGage: quién tiene acceso admin a Jira y Confluence
