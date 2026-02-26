# Research Report: Rovo AI Capabilities for RaiSE Forge Integration

> **Question:** ¿Qué puede hacer Rovo AI hoy con custom Forge tools para ejecutar workflows tipo skill de RaiSE?
> **Depth:** Quick scan (10 sources)
> **Date:** 2026-02-26
> **Decision informs:** S275.5 endpoint design

## Key Findings

### 1. Rovo Agent Architecture

Un Rovo Agent se define con:
- **Prompt** (markdown/text): instrucciones de comportamiento, personalidad, cuándo usar qué action
- **Actions** (Forge functions): operaciones que el agente puede invocar
- **Conversation starters**: sugerencias para el usuario

El **prompt es el skill**. Rovo sigue las instrucciones del prompt y decide cuándo invocar cada action.

**Confidence: HIGH** (5 primary sources confirm)

### 2. Actions = Tools para Rovo

Cada action es una función Forge (JS/TS) que:
- Recibe inputs tipados (string, integer, number, boolean)
- Puede llamar **APIs externas** via Forge fetch (← nuestro servidor)
- Devuelve string o JSON que Rovo transforma en respuesta natural
- Límite: **5MB** de data por invocación
- El agente decide cuándo invocar basándose en el **description** del action

**Confidence: HIGH** (sources 2, 3, 10)

### 3. Multi-step: Limitado pero Funcional

- **Sí puede:** Llamar múltiples actions en secuencia (Q&A agent: fetch → generate → register × N → insert)
- **No puede:** "A long string of tasks" — actualizar varios campos + comentar + notificar de golpe
- **Patrón que funciona:** fetch data → agent razona → action para persistir → confirmar con usuario → siguiente paso
- **Patrón que NO funciona:** cadenas largas autónomas sin checkpoints humanos

**Confidence: MEDIUM** (2 primary + 2 secondary sources, limitación reportada por terceros)

### 4. Contexto Disponible para el Agent

Rovo recibe contexto de:
- Página/issue actual (si invocado desde editor)
- Texto seleccionado (si hay)
- accountId del usuario
- **NO** recibe automáticamente el contenido de la página — necesita una action fetch-content

**Confidence: HIGH** (source 5 explicit: "The AI does not automatically operate with the current page")

### 5. Forge Actions Pueden Llamar APIs Externas

Confirmado: actions usan Forge fetch para llamar APIs externas. Esto significa que nuestros endpoints del rai-server son accesibles como backend de las actions.

**Confidence: HIGH** (sources 2, 6, 10)

## Triangulated Claims

### Claim 1: "Rovo puede ejecutar un skill de RaiSE si el prompt es el skill y las actions son las operaciones"

| Source | Supports? | Detail |
|--------|-----------|--------|
| Hello World tutorial (#3) | ✅ | Prompt define comportamiento, actions ejecutan |
| Q&A Agent tutorial (#5) | ✅ | Multi-step: fetch → process → persist |
| Jira Analyst (#4) | ✅ | Fetch → analyze → report |
| Rovo limitations (#8) | ⚠️ | "Smart reusable prompts", no autonomous multi-step |

**Verdict:** Sí, pero con patrón simple: pocos pasos, cada paso = 1 action call, checkpoints humanos entre pasos complejos.

### Claim 2: "Nuestro servidor puede ser el backend de las Forge actions"

| Source | Supports? | Detail |
|--------|-----------|--------|
| Action docs (#2) | ✅ | External API via Forge fetch |
| No-code article (#6) | ✅ | Personio/Moco como external systems |
| Rovo modules index (#10) | ✅ | `endpoint` option for remote |

**Verdict:** Confirmado. El patrón es: Forge action → fetch a nuestro API → devuelve resultado → Rovo lo presenta.

### Claim 3: "No necesitamos doble inferencia para el POC"

| Source | Supports? | Detail |
|--------|-----------|--------|
| All tutorials (#3,4,5) | ✅ | Agent razona, actions solo ejecutan lógica |
| Q&A Agent (#5) | ✅ | Rovo genera Q&A, actions solo persisten |
| Limitations (#8) | ⚠️ | Si el skill es muy complejo, Rovo puede no seguirlo |

**Verdict:** Para skills simples (1-3 pasos), la inferencia de Rovo basta. Si falla con skills complejos, escalamos a server-side inference.

## Contrary Evidence

- Source #8 reporta que Rovo "can't do a long string of tasks". Nuestros skills de governance (problem-shape, epic-design) son multi-paso complejos. **Riesgo:** Rovo podría no completar el flujo completo sin intervención.
- Prompt engineering es trial-and-error según usuarios. Los skills tal cual pueden necesitar adaptación significativa para funcionar como prompts de Rovo.

## Recommendation

**Confidence: HIGH**

Para el POC, el servidor necesita servir:

1. **Skills como prompts** — El prompt del Rovo Agent ES el skill adaptado
2. **Templates** — Actions que devuelven el template para que Rovo lo llene
3. **Contexto del proyecto** — Action que devuelve el grafo/contexto relevante

### Endpoints mínimos para el POC

```
GET  /api/v1/skills                → Lista skills disponibles
GET  /api/v1/skills/{name}         → Contenido del skill (prompt para Rovo)
GET  /api/v1/templates             → Lista templates disponibles
GET  /api/v1/templates/{name}      → Contenido del template
GET  /api/v1/graph/query           → Ya existe (contexto del proyecto)
POST /api/v1/graph/sync            → Ya existe (CLI sube grafo)
```

### Forge Actions que Fernando construiría

```yaml
actions:
  - key: get-skill
    function: fetchSkill
    actionVerb: GET
    description: "Retrieves a RaiSE governance skill with instructions"
    inputs:
      skill_name:
        title: Skill name
        type: string
        required: true

  - key: get-template
    function: fetchTemplate
    actionVerb: GET
    description: "Retrieves a governance template to fill"
    inputs:
      template_name:
        title: Template name
        type: string
        required: true

  - key: get-project-context
    function: fetchContext
    actionVerb: GET
    description: "Retrieves project knowledge graph context"
    inputs:
      query:
        title: Search query
        type: string
        required: true
```

### Rovo Agent definition

```yaml
rovo:agent:
  - key: raise-governance-agent
    name: RaiSE Governance
    prompt: >
      You are a RaiSE governance assistant. You help teams create
      governance documents following RaiSE methodology.

      When asked to create a document:
      1. Use get-skill to retrieve the methodology steps
      2. Use get-template to retrieve the document template
      3. Use get-project-context if you need project information
      4. Follow the skill instructions to fill the template
      5. Create the document in Confluence
    actions:
      - get-skill
      - get-template
      - get-project-context
```

## Implications for S275.5

- **Trace/impact/constraints → parking lot.** No son necesarios para el POC.
- **S275.5 se redefine:** Skills & Templates endpoints (sync + serve).
- **DB schema:** Necesitamos tablas para skills y templates (o reusar JSONB en nodes).
- **Sync pattern:** Igual que graph sync — CLI sube, server sirve.

## Sources

See `sources/evidence-catalog.md` for full catalog.
