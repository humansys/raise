# RaiSE Data Architecture
## Estructuras de Datos y OntologÃ­a

**VersiÃ³n:** 2.1.0  
**Fecha:** 29 de Diciembre, 2025  
**PropÃ³sito:** Documentar las estructuras de datos, schemas y ontologÃ­a canÃ³nica de RaiSE.

> **Nota v2.1:** Campo `audience` aÃ±adido a Kata (ADR-009). Diagrama ER actualizado. Encoding UTF-8 corregido.

---

## OntologÃ­a de Conceptos

```mermaid
erDiagram
    CONSTITUTION ||--o{ GUARDRAIL : "define"
    CONSTITUTION ||--o{ PROJECT : "aplica_a"
    
    PROJECT ||--o{ SPEC : "contiene"
    PROJECT ||--o{ PLAN : "genera"
    PROJECT ||--|{ GUARDRAIL : "hereda"
    
    SPEC ||--o{ USER_STORY : "descompone_en"
    USER_STORY ||--o{ TASK : "implementa_via"
    
    KATA ||--o{ VALIDATION_GATE : "define_criterios"
    KATA }|--|| KATA_LEVEL : "pertenece_a"
    KATA }|--|| KATA_AUDIENCE : "dirigida_a"
    
    KATA_AUDIENCE {
        string id PK "beginner, intermediate, advanced"
        string shuhari_mapping "shu, ha, ri (interno)"
    }
    
    VALIDATION_GATE ||--o{ ESCALATION_GATE : "puede_triggerar"
    
    AGENT ||--o{ TASK : "ejecuta"
    AGENT }|--|| GUARDRAIL : "sigue"
    AGENT ||--o{ OBSERVABLE_TRACE : "genera"
    
    TEMPLATE ||--o{ SPEC : "genera"
    TEMPLATE ||--o{ PLAN : "genera"
    
    MCP_SERVER ||--o{ AGENT : "sirve_contexto_a"
    MCP_SERVER ||--|| PROJECT : "lee_golden_data_de"
```

---

## Entidades Core

### Constitution

**DefiniciÃ³n:** Principios inmutables que gobiernan el proyecto. Documento de mÃ¡xima jerarquÃ­a.

**Atributos:**

| Campo | Tipo | Requerido | DescripciÃ³n |
|-------|------|-----------|-------------|
| version | semver | âœ… | VersiÃ³n del documento |
| identity | object | âœ… | QuÃ© es y quÃ© no es |
| principles | array | âœ… | Principios innegociables (Â§1-Â§9) |
| values | array | âœ… | Valores de diseÃ±o |
| restrictions | object | âœ… | Nunca/Siempre |

**UbicaciÃ³n:** `.raise/memory/constitution.md`

**Referencia MCP:** `raise://constitution`

---

### Guardrail [v2.0: antes "Rule"]

**DefiniciÃ³n:** Control que gobierna comportamiento de agentes o calidad de cÃ³digo. Los Guardrails son protecciones activas, no reglas pasivas.

**Atributos:**

| Campo | Tipo | Requerido | DescripciÃ³n |
|-------|------|-----------|-------------|
| id | string | âœ… | Identificador Ãºnico (ej. `guard-001-naming`) |
| title | string | âœ… | Nombre descriptivo |
| scope | enum | âœ… | `agent`, `code`, `process`, `security` |
| severity | enum | âœ… | `error`, `warning`, `info` |
| priority | int | âœ… | 1-999, menor = mayor prioridad |
| content | markdown | âœ… | Contenido del guardrail |
| globs | array | âŒ | Patrones de archivo donde aplica |
| enforcement | enum | âœ… | `block`, `warn`, `log` |

**Formato humano:** `.mdc` (Markdown con frontmatter)  
**Formato mÃ¡quina:** `.json` (compilado)

**UbicaciÃ³n:**
- Origen: `raise-config/guardrails/*.mdc`
- Compilado: `.raise/memory/guardrails.json`

**Referencia MCP:** `raise://guardrails`

---

### Validation Gate [v2.0: antes "DoD"]

**DefiniciÃ³n:** Punto de inspecciÃ³n que debe pasarse antes de avanzar a la siguiente fase. Implementa el principio Jidoka.

**Atributos:**

| Campo | Tipo | Requerido | DescripciÃ³n |
|-------|------|-----------|-------------|
| id | string | âœ… | Identificador (ej. `gate-design`) |
| phase | enum | âœ… | `context`, `discovery`, `vision`, `design`, `backlog`, `plan`, `code`, `deploy` |
| criteria | array | âœ… | Lista de criterios a validar |
| escalation_threshold | float | âŒ | Confidence bajo el cual escalar (0.0-1.0) |
| blocking | boolean | âœ… | Si bloquea avance o solo advierte |

**Fases estÃ¡ndar:**

| Gate | Fase | Pregunta clave |
|------|------|----------------|
| `gate-context` | 0 | Â¿Stakeholders y restricciones claros? |
| `gate-discovery` | 1 | Â¿PRD completo y validado? |
| `gate-vision` | 2 | Â¿AlineaciÃ³n negocio-tÃ©cnica? |
| `gate-design` | 3 | Â¿Arquitectura consistente? |
| `gate-backlog` | 4 | Â¿HUs siguen formato estÃ¡ndar? |
| `gate-plan` | 5 | Â¿Pasos atÃ³micos y verificables? |
| `gate-code` | 6 | Â¿CÃ³digo validado multinivel? |
| `gate-deploy` | 7 | Â¿Feature en producciÃ³n estable? |

**UbicaciÃ³n:** Definidos en katas correspondientes

**Referencia MCP:** Tool `validate_gate`

---

### Escalation Gate [v2.0: NUEVO]

**DefiniciÃ³n:** Trigger para intervenciÃ³n humana (HITL). Se activa cuando un Validation Gate falla o la confianza es baja.

**Atributos:**

| Campo | Tipo | Requerido | DescripciÃ³n |
|-------|------|-----------|-------------|
| trigger_source | string | âœ… | Gate o condiciÃ³n que lo activÃ³ |
| reason | string | âœ… | Por quÃ© se requiere intervenciÃ³n |
| context | object | âœ… | InformaciÃ³n para el Orquestador |
| options | array | âœ… | Acciones posibles |
| timeout | duration | âŒ | Tiempo mÃ¡ximo de espera |

**Referencia MCP:** Tool `escalate`

---

### Observable Trace [v2.0: NUEVO]

**DefiniciÃ³n:** Registro de una interacciÃ³n agente-MCP para auditorÃ­a y Observable Workflow.

**Atributos:**

| Campo | Tipo | Requerido | DescripciÃ³n |
|-------|------|-----------|-------------|
| trace_id | uuid | âœ… | Identificador Ãºnico |
| session_id | uuid | âœ… | SesiÃ³n de trabajo |
| timestamp | datetime | âœ… | Momento de la acciÃ³n |
| action | string | âœ… | Tipo de acciÃ³n (resource_read, tool_call, etc.) |
| actor | enum | âœ… | `agent`, `orchestrator`, `system` |
| input | object | âœ… | Datos de entrada |
| output | object | âœ… | Resultado |
| duration_ms | int | âœ… | Tiempo de ejecuciÃ³n |
| gate_status | enum | âŒ | `passed`, `failed`, `escalated` |

**UbicaciÃ³n:** `.raise/traces/{date}/{session_id}.jsonl`

**Formato:** JSON Lines (un trace por lÃ­nea)

---

### Kata

**DefiniciÃ³n:** Proceso estructurado que codifica un estÃ¡ndar o patrÃ³n. Ejercicio deliberado de mejora.

**Atributos:**

| Campo | Tipo | Requerido | DescripciÃ³n |
|-------|------|-----------|-------------|
| id | string | âœ… | Ej. `L1-04` |
| level | enum | âœ… | `L0`, `L1`, `L2`, `L3` (quÃ© enseÃ±a) |
| audience | enum | âœ… | `beginner`, `intermediate`, `advanced` (a quiÃ©n) [v2.1] |
| title | string | âœ… | Nombre descriptivo |
| purpose | string | âœ… | Para quÃ© sirve |
| inputs | array | âœ… | QuÃ© consume |
| outputs | array | âœ… | QuÃ© produce |
| steps | array | âœ… | Pasos a seguir |
| validation_gate | string | âŒ | Gate que este kata valida |
| prerequisites | array | âŒ | Katas que deben completarse antes [v2.1] |

**Niveles (Level) â€” QuÃ© enseÃ±a:**

| Nivel | PropÃ³sito | Ejemplo |
|-------|-----------|---------|
| L0 | Meta-katas: filosofÃ­a | Principios RaiSE |
| L1 | Proceso: metodologÃ­a | GeneraciÃ³n de planes |
| L2 | Componentes: patrones | AnÃ¡lisis de cÃ³digo |
| L3 | TÃ©cnico: especializaciÃ³n | Modelado de datos |

**Audiencia (Audience) â€” A quiÃ©n estÃ¡ dirigida:** [v2.1 - ADR-009]

| Audience | CaracterÃ­sticas | Mapeo Interno |
|----------|-----------------|---------------|
| `beginner` | Pasos exactos, copiar la forma, sin variaciÃ³n | Shu (å®ˆ) |
| `intermediate` | AdaptaciÃ³n al contexto, entender el "por quÃ©" | Ha (ç ´) |
| `advanced` | Crear variaciones propias, fluir sin forma | Ri (é›¢) |

> **Nota de diseÃ±o (ADR-009):** El mapeo ShuHaRi es interno para mantenedores. Los usuarios ven solo tÃ©rminos universales (`beginner/intermediate/advanced`). Esta decisiÃ³n balancea diferenciaciÃ³n filosÃ³fica con simplicidad de onboarding.

**UbicaciÃ³n:** `raise-config/katas/L{n}-*.md`

---

### Spec (Specification)

**DefiniciÃ³n:** Documento que describe QUÃ‰ construir. Artefacto central del Context Engineering.

**Tipos:**
- PRD (Product Requirements Document)
- Solution Vision
- Technical Design
- Feature Specification

**Atributos comunes:**

| Campo | Tipo | Requerido | DescripciÃ³n |
|-------|------|-----------|-------------|
| id | string | âœ… | Identificador (ej. JIRA ID) |
| title | string | âœ… | Nombre descriptivo |
| status | enum | âœ… | `draft`, `review`, `approved` |
| version | semver | âœ… | VersiÃ³n del documento |
| stakeholders | array | âŒ | Interesados |
| content | markdown | âœ… | Contenido principal |

**UbicaciÃ³n:** `.raise/specs/{id}-{type}.md`

**Referencia MCP:** `raise://specs/{id}`

---

### User Story

**DefiniciÃ³n:** Requisito desde perspectiva del usuario.

**Atributos:**

| Campo | Tipo | Requerido | DescripciÃ³n |
|-------|------|-----------|-------------|
| id | string | âœ… | Identificador |
| title | string | âœ… | Como [rol], quiero [acciÃ³n] |
| description | string | âœ… | Contexto y detalles |
| acceptance_criteria | array | âœ… | Criterios BDD (Dado/Cuando/Entonces) |
| priority | enum | âœ… | `P0`, `P1`, `P2`, `P3` |
| story_points | int | âŒ | EstimaciÃ³n |

**Formato BDD para AC:**
```gherkin
Dado [contexto inicial]
Cuando [acciÃ³n del usuario]
Entonces [resultado esperado]
```

**UbicaciÃ³n:** `.raise/specs/{feature-id}/{id}-US-*.md`

---

### Agent

**DefiniciÃ³n:** ConfiguraciÃ³n de un agente de IA especializado.

**Atributos:**

| Campo | Tipo | Requerido | DescripciÃ³n |
|-------|------|-----------|-------------|
| name | string | âœ… | Nombre del agente |
| version | semver | âœ… | VersiÃ³n de la spec |
| identity | object | âœ… | Rol, misiÃ³n, dominios |
| behavior | object | âœ… | Principios, persistencia |
| capabilities | object | âœ… | Tareas primarias/secundarias |
| mcp_tools | array | âŒ | Tools MCP que puede invocar |
| guardrails | array | âœ… | Guardrails que debe seguir |
| safety | object | âœ… | Condiciones de rechazo |

**Formato:** YAML

**UbicaciÃ³n:** `raise-config/agents/{agent-name}/spec.yaml`

---

## Formatos de Archivo

### Markdown (Humanos)

Usado para: Constitution, Specs, Katas, Plans

**Estructura esperada:**
```markdown
# TÃ­tulo del Documento

**VersiÃ³n:** X.Y.Z  
**Fecha:** YYYY-MM-DD  
**Estado:** draft|review|approved

---

## SecciÃ³n Principal

Contenido...

---

*Footer con notas*
```

**Frontmatter (opcional):**
```yaml
---
id: PROJ-123
type: user_story
priority: P1
audience: intermediate
---
```

---

### MDC (Guardrails)

Markdown con configuraciÃ³n embedded para Cursor y otros IDEs.

**Estructura:**
```markdown
---
description: DescripciÃ³n breve del guardrail
globs:
  - "**/*.py"
  - "src/**/*.ts"
priority: 100
severity: error
enforcement: block
---

# TÃ­tulo del Guardrail

Contenido del guardrail en Markdown...
```

---

### JSON (MÃ¡quinas)

Usado para: Guardrails compilados, configuraciÃ³n

**Schema guardrails.json:** [v2.0: renombrado de raise-rules.json]
```json
{
  "$schema": "https://raise.dev/schemas/guardrails.v2.json",
  "version": "2.0.0",
  "compiled_at": "2025-12-28T00:00:00Z",
  "guardrails": [
    {
      "id": "guard-001-naming",
      "title": "Naming Conventions",
      "priority": 100,
      "scope": "code",
      "severity": "error",
      "enforcement": "block",
      "globs": ["**/*.py"],
      "content_hash": "sha256:abc123..."
    }
  ]
}
```

---

### JSONL (Traces)

Usado para: Observable Workflow traces

**Estructura:**
```jsonl
{"trace_id":"uuid1","session_id":"sess1","timestamp":"2025-12-28T10:00:00Z","action":"resource_read","actor":"agent","input":{"uri":"raise://constitution"},"output":{"status":"ok"},"duration_ms":45}
{"trace_id":"uuid2","session_id":"sess1","timestamp":"2025-12-28T10:00:01Z","action":"tool_call","actor":"agent","input":{"tool":"validate_gate","args":{"gate":"gate-design"}},"output":{"status":"passed"},"duration_ms":120}
```

---

### YAML (Agents)

Usado para: Definiciones de agentes

**Schema reducido:**
```yaml
agent_specification:
  version: "2.0.0"
  metadata:
    name: "agent-name"
    description: "..."
  identity:
    short_role: "Role Label"
    mission: "..."
  behavior:
    core_principles: [...]
  capabilities:
    primary_tasks: [...]
    mcp_tools: [validate_gate, escalate]
    non_goals: [...]
  guardrails:
    - guard-001-naming
    - guard-002-security
```

---

## Flujo de TransformaciÃ³n

```mermaid
flowchart LR
    A[Guardrails .mdc] -->|raise pull| B[guardrails.json]
    C[Templates .md] -->|kata execution| D[Specs .md]
    D -->|agent processing| E[Plans .md]
    E -->|implementation| F[Code]
    B --> G[raise-mcp]
    D --> G
    G -->|MCP Resources| H[AI Agent]
    H -->|MCP Tools| G
    G -->|traces| I[.raise/traces/]
    I -->|raise audit| J[Observable Workflow Report]
```

---

## Versionado de Schemas

### PolÃ­tica de Compatibilidad

| Cambio | AcciÃ³n |
|--------|--------|
| Nuevo campo opcional | VersiÃ³n minor (1.x) |
| Campo requerido nuevo | VersiÃ³n major (x.0) |
| DeprecaciÃ³n de campo | Aviso + 2 versiones |
| EliminaciÃ³n de campo | VersiÃ³n major (x.0) |
| Renombre de entidad | VersiÃ³n major + migration script |

### MigraciÃ³n v1.0 â†’ v2.0

| Cambio | Script |
|--------|--------|
| `raise-rules.json` â†’ `guardrails.json` | `raise migrate --to v2` |
| `rules/` â†’ `guardrails/` | AutomÃ¡tico en hydrate |
| `dod` field â†’ `validation_gate` | AutomÃ¡tico en hydrate |

### MigraciÃ³n v2.0 â†’ v2.1 [NUEVO]

| Cambio | Script |
|--------|--------|
| AÃ±adir `audience` a Katas | Manual o `raise kata migrate` |

---

## Relaciones entre Entidades

| Origen | RelaciÃ³n | Destino |
|--------|----------|---------|
| Constitution | define | Guardrail |
| Guardrail | aplica a | Project |
| Kata | define_criterios | Validation Gate |
| Kata | dirigida_a | Kata Audience [v2.1] |
| Validation Gate | puede_triggerar | Escalation Gate |
| Spec | descompone en | User Story |
| User Story | implementa via | Task |
| Agent | ejecuta | Task |
| Agent | sigue | Guardrail |
| Agent | genera | Observable Trace |
| Template | genera | Spec, Plan |
| MCP Server | sirve_contexto_a | Agent |
| MCP Server | lee_golden_data_de | Project |

---

## JerarquÃ­a de Entidades

```
Constitution (Inmutable)
    â”‚
    â”œâ”€â”€ Guardrails (Controles)
    â”‚       â”‚
    â”‚       â””â”€â”€ enforcement: block|warn|log
    â”‚
    â”œâ”€â”€ Validation Gates (Checkpoints)
    â”‚       â”‚
    â”‚       â””â”€â”€ Escalation Gates (HITL)
    â”‚
    â””â”€â”€ Specs (IntenciÃ³n)
            â”‚
            â”œâ”€â”€ User Stories
            â”‚       â”‚
            â”‚       â””â”€â”€ Tasks
            â”‚
            â””â”€â”€ Plans
```

---

## Changelog

### v2.1.0 (2025-12-29)
- NUEVO: Campo `audience` en Kata (ADR-009)
- NUEVO: Campo `prerequisites` en Kata
- NUEVO: Entidad KATA_AUDIENCE en diagrama ER
- NUEVO: Tabla de mapeo ShuHaRi (interno)
- FIX: Encoding UTF-8 corregido en todo el documento

### v2.0.0 (2025-12-28)
- **BREAKING:** Rule â†’ Guardrail (schema y ubicaciÃ³n)
- **BREAKING:** DoD â†’ Validation Gate
- **BREAKING:** raise-rules.json â†’ guardrails.json
- NUEVO: Entidad Escalation Gate
- NUEVO: Entidad Observable Trace
- NUEVO: Formato JSONL para traces
- NUEVO: Atributos severity y enforcement en Guardrail
- NUEVO: Atributo mcp_tools en Agent
- Diagrama ER actualizado con nuevas entidades
- Flujo de transformaciÃ³n incluye Observable Workflow

---

*Este documento define la ontologÃ­a canÃ³nica de RaiSE. Actualizar con cada nueva entidad. Referencias cruzadas: [10-system-architecture-v2.md](./10-system-architecture-v2.md), [20-glossary-v2.md](./20-glossary-v2.md), [ADR-009](./adr/adr-009-shuhari-hybrid.md).*
