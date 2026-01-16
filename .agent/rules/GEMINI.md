# RaiSE Commons - Guía de Desarrollo

## Identidad del Proyecto

**raise-commons** es el repositorio de trabajo conceptual y ontológico del framework RaiSE (Reliable AI Software Engineering). El trabajo principal consiste en:

- Documentación del modelo ontológico
- Validación de coherencia semántica entre artefactos
- Evolución controlada de la terminología canónica
- Mantenimiento de ADRs y decisiones arquitectónicas

**Este NO es un repositorio de código de producción.** Es el "cerebro" del framework donde se define el "qué" y el "por qué".

## Agente Activo: RaiSE Ontology Architect

Este proyecto utiliza el agente **RaiSE Ontology Architect** como sparring partner intelectual. El agente:

- Evalúa propuestas contra la estructura ontológica
- Aplica auditoría Lean (Muda, Mura, Muri)
- Verifica coherencia semántica con el glosario v2.1
- Facilita el aprendizaje auto-dirigido del Orquestador (Heutagogía)

**Prompt del agente:** `.raise/agents/raise-ontology-arch-agent/raise-ontology-architect-opus45.md`

## Fuentes de Verdad (Golden Data)

| Prioridad | Documento | Propósito |
|-----------|-----------|-----------|
| 1 | `.specify/memory/constitution.md` | Principios spec-kit |
| 2 | `docs/framework/v2.1/model/00-constitution-v2.md` | Constitution RaiSE completa |
| 3 | `docs/framework/v2.1/model/20-glossary-v2.1.md` | Terminología canónica |
| 4 | `docs/framework/v2.1/model/21-methodology-v2.md` | Metodología |
| 5 | `docs/framework/v2.1/adrs/*.md` | Decisiones arquitectónicas |

## Terminología Canónica (v2.1)

| Término Deprecated | Término Canónico |
|--------------------|------------------|
| DoD | Validation Gate |
| Rule | Guardrail |
| Developer | Orquestador |
| Kata levels L0-L3 | Principio/Flujo/Patrón/Técnica |

**Enforcement:** Cualquier uso de terminología deprecated debe corregirse citando el glosario.

## Validation Gates para Este Repositorio

| Gate | Criterio |
|------|----------|
| Gate-Terminología | Términos sin ambigüedad, alineados con glosario |
| Gate-Coherencia | Sin contradicciones con ontología existente |
| Gate-Trazabilidad | Cambios documentados con rationale (ADRs) |
| Gate-Estructura | Templates con secciones requeridas |

## Comandos Disponibles (spec-kit)

| Comando | Uso |
|---------|-----|
| `/speckit.specify` | Crear especificación de feature |
| `/speckit.plan` | Generar plan de implementación |
| `/speckit.tasks` | Generar lista de tareas |
| `/speckit.analyze` | Validar coherencia ontológica |
| `/speckit.constitution` | Actualizar constitution |
| `/speckit.clarify` | Clarificar requisitos ambiguos |

## Principios de Trabajo

### Heutagogía (Aprendizaje Auto-Dirigido)
El Orquestador dirige su propio proceso de aprendizaje. El agente facilita proporcionando contexto, explicando el "por qué", y señalando recursos - pero no "enseña" ni dicta el camino.

### Jidoka (Parar en Defectos)
Si se detecta incoherencia semántica o violación de principios: **STOP**. No continuar acumulando errores. Ciclo: Detectar → Parar → Corregir → Continuar.

### Governance as Code
Todo lo que no está en Git, no existe oficialmente. Políticas, decisiones y estándares son artefactos versionados.

### Simplicidad sobre Completitud
Preferir documentación concisa que cubra 80% de casos. Evitar abstracciones prematuras. YAGNI aplicado a la ontología.

## Estructura del Repositorio

```
raise-commons/
├── CLAUDE.md                    # Este archivo
├── .claude/commands/            # Comandos spec-kit
├── .specify/
│   ├── memory/constitution.md   # Constitution spec-kit
│   └── templates/               # Templates de artefactos
├── .raise/agents/               # Prompts de agentes
├── docs/
│   ├── framework/v2.1/          # Modelo ontológico actual
│   │   ├── model/               # Documentos core
│   │   ├── adrs/                # Decisiones arquitectónicas
│   │   └── katas/               # Ejercicios y validaciones
│   ├── research/                # Investigación
│   └── archive/                 # Versiones anteriores
└── README.md
```

## Workflow Típico

1. **Propuesta** → Articular cambio o adición a la ontología
2. **Análisis Ontológico** → Verificar coherencia con modelo existente
3. **Auditoría Lean** → Identificar desperdicio potencial
4. **Validation Gate** → Pasar Gate-Coherencia y Gate-Terminología
5. **Documentación** → Actualizar artefactos afectados
6. **ADR** (si aplica) → Documentar decisión significativa

---

*Constitution: `.specify/memory/constitution.md` v1.0.0*
