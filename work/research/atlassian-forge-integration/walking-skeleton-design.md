# Walking Skeleton Design: RaiSE Governance Copilot on Atlassian Forge

**RAISE-274** | **Updated:** 2026-02-26 (post-E275) | **Type:** Architecture + Implementation Guide
**Constraint:** Must support scale from day 1 — no throwaway demo

---

## Vision

Un sistema de governance organizacional con tres capas:

- **Confluence** = Content Store (documentos, skills, standards)
- **RaiSE Backend** = Knowledge Layer (grafo neuro-simbólico, determinista) — **EXISTS (E275)**
- **Forge App** = UI Layer (Rovo Agent como copiloto contextual) — **THIS EPIC**

Jira orquesta el proceso. Confluence almacena el contenido. RaiSE garantiza
determinismo, trazabilidad y consistencia. Rai asiste a cada humano según
su rol y fase — tanto governance como desarrollo.

```
                    ┌──────────────────────────┐
                    │      Confluence           │
                    │   (Content Store)         │
                    │                           │
                    │  Skills   Standards       │
                    │  ADRs     Documents       │
                    │  Templates                │
                    └─────────┬────────────────┘
                              │
                    indexa contenido,
                    construye relaciones
                              │
                              ▼
                    ┌──────────────────────────┐
                    │    RaiSE Backend          │
                    │  (Knowledge Layer)        │
                    │  ✅ DONE (E275)           │
                    │                           │
                    │  Knowledge Graph          │
                    │  (neuro-simbólico,        │
                    │   determinista)           │
                    │                           │
                    │  POST /graph/sync         │
                    │  GET  /graph/query        │
                    │  POST/GET /agent/events   │
                    │  POST/GET /memory/patterns│
                    └─────────┬────────────────┘
                              │
                    queries deterministas,
                    telemetría, patrones
                              │
                    ┌─────────┴────────────────┐
                    │                           │
                    ▼                           ▼
          ┌─────────────────┐       ┌─────────────────┐
          │  Rai Governance  │       │    Rai Dev       │
          │  (Rovo Agent)    │       │  (Rovo Agent /   │
          │                  │       │   rai-cli)       │
          │  Confluence +    │       │                  │
          │  Jira context    │       │  IDE + Jira      │
          │                  │       │  context         │
          │  Users:          │       │                  │
          │  PO, Architect,  │       │  Users:          │
          │  Portfolio Mgr   │       │  Developers      │
          └─────────────────┘       └─────────────────┘
```

### The Knowledge Loop

```
Governance team                     Dev team
creates/updates                     consumes/implements
      │                                   │
      ▼                                   ▼
  Confluence                          Rai Dev
  (content)                           queries
      │                                   │
      ▼                                   │
  RaiSE Backend                           │
  indexes into ──────────────────────────►│
  knowledge graph                         │
      │                                   │
      │◄──── validates against ───────────┘
      │      (code, PRs, stories)
      ▼
  Deterministic:
  "ADR-003 governs mod-auth"
  "LBC-X traces to Epic-Y"
  "Changing X impacts [A, B, C]"
```

What governance produces, development consumes. What development produces,
governance validates. The RaiSE knowledge graph closes the loop deterministically.

---

## User Journeys & Sequence Diagrams

### Personas

| Persona | Rol | Herramienta | Qué necesita |
|---------|-----|------------|--------------|
| **Ana** | Product Owner | Confluence + Rovo Chat | Crear documentos de governance (LBC, Problem Scope) con guía paso a paso |
| **Rodo** | Architect / Reviewer | Confluence + Rovo Chat | Revisar documentos contra estándares, ADRs y el knowledge graph |
| **Carlos** | Developer | IDE + Jira (+ Rovo Chat opcional) | Saber qué ADRs, standards y constraints aplican antes de codear |

### Test Case 1: Ana crea un Lean Business Case

**Precondiciones:**
- Jira Automation ya creó: Epic "Iniciativa Piloto" + Story "LBC" + Confluence page vacía (from template)
- Story "LBC" está In Progress, assigned to Ana
- La página de Confluence está linkeada a la Story via remote link

**Flujo (lo que Ana experimenta):**

1. Ana abre Confluence, navega a la página "LBC: Iniciativa Piloto"
2. La página tiene el template vacío
3. Ana abre el chat de Rovo (ícono en la barra lateral o `/ai` en el editor)
4. Ana dice: *"Necesito trabajar en este Lean Business Case. Tengo notas de la reunión con el cliente."* y pega el transcript
5. Rai responde:
   - *"Estoy en la story PROJ-45, LBC, In Progress. La página existe pero está vacía."*
   - *"Cargué el skill 'Lean Business Case'. Necesito: ✅ Transcript (lo tengo), ❓ Costo del status quo, ❓ Sponsor ejecutivo"*
6. Ana responde con los datos faltantes
7. Rai actualiza la página de Confluence — Ana VE el contenido aparecer en la página
8. Rai confirma: *"Draft creado. Secciones completas: ✅✅✅. Pendientes: ⚠️❌. Indexé en el knowledge graph."*
9. Ana revisa el documento, pide ajustes conversacionales
10. Cuando está lista, Ana mueve la Story a "In Review" (manual o le pide a Rai)

**Lo que Ana NO ve:** graph-sync, report-event, API calls al backend. Solo ve la página actualizarse y confirmaciones de Rai.

```
┌─────┐          ┌──────────┐       ┌──────────┐        ┌──────────┐
│ Ana │          │Rai (Rovo)│       │Confluence│        │  Backend │
└──┬──┘          └────┬─────┘       └────┬─────┘        └────┬─────┘
   │                  │                  │                    │
   │  "Trabajar en    │                  │                    │
   │   el LBC..."     │                  │                    │
   │─────────────────►│                  │                    │
   │                  │                  │                    │
   │                  │  read-jira-ctx   │                    │
   │                  │─────────────────►│ (via Jira API)     │
   │                  │  ◄── story ctx ──│                    │
   │                  │                  │                    │
   │                  │  read-page       │                    │
   │                  │─────────────────►│                    │
   │                  │  ◄── vacío ──────│                    │
   │                  │                  │                    │
   │                  │  find-skill-page │                    │
   │                  │─────────────────►│                    │
   │                  │  ◄── skill def ──│                    │
   │                  │                  │                    │
   │  "Te faltan      │                  │                    │
   │   estos datos"   │                  │                    │
   │◄─────────────────│                  │                    │
   │                  │                  │                    │
   │  "Status quo     │                  │                    │
   │   $150K/mes..."  │                  │                    │
   │─────────────────►│                  │                    │
   │                  │                  │                    │
   │                  │  update-page     │                    │
   │                  │─────────────────►│                    │
   │                  │                  │                    │
   │                  │  graph-sync      │                    │
   │                  │──────────────────┼───────────────────►│
   │                  │                  │    ◄── ok ─────────│
   │                  │                  │                    │
   │                  │  report-event    │                    │
   │                  │──────────────────┼───────────────────►│
   │                  │                  │                    │
   │  "Draft creado.  │                  │                    │
   │   ✅✅✅ ⚠️❌"  │                  │                    │
   │◄─────────────────│                  │                    │
   │                  │                  │                    │
```

### Test Case 2: Rodo revisa el LBC

**Precondiciones:**
- Ana completó el draft y movió la Story a "In Review"
- Rodo es reviewer (puede ser assignee o simplemente abre la página)

**Flujo (lo que Rodo experimenta):**

1. Rodo recibe notificación de Jira: "LBC movido a In Review"
2. Abre la página de Confluence "LBC: Iniciativa Piloto"
3. Lee el documento — el contenido ya está ahí
4. Abre Rovo Chat: *"Quiero revisar este LBC"*
5. Rai responde:
   - *"LBC en Review. Mi análisis combinando el grafo y el documento:"*
   - *"✅ Problem Statement: hypothesis format correcto"*
   - *"✅ Financial Impact: cuantificado ($1.8M/año)"*
   - *"⚠️ Risks: mencionados pero sin cuantificar"*
   - *"❌ Auth approach: no hay ADR que respalde la decisión de autenticación"*
6. Rodo dice: *"Agrega comentarios de revisión y crea un ADR para auth"*
7. Rai agrega 2 comentarios EN LA PÁGINA (visibles para Ana)
8. Rai crea nueva página "ADR-003: OAuth2" y la indexa en el grafo
9. Rai devuelve la Story a "In Progress"
10. Rodo confirma y cierra

**Lo que Rodo VE:** análisis con ✅⚠️❌, comentarios en la página, nuevo ADR creado. Todo trazable.

```
┌──────┐         ┌──────────┐       ┌──────────┐        ┌──────────┐
│ Rodo │         │Rai (Rovo)│       │Confluence│        │  Backend │
└──┬───┘         └────┬─────┘       └────┬─────┘        └────┬─────┘
   │                  │                  │                    │
   │  "Revisar el     │                  │                    │
   │   LBC"           │                  │                    │
   │─────────────────►│                  │                    │
   │                  │                  │                    │
   │                  │  read-jira-ctx   │                    │
   │                  │─────────────────►│                    │
   │                  │  read-page       │                    │
   │                  │─────────────────►│                    │
   │                  │                  │                    │
   │                  │  graph-query     │                    │
   │                  │  "auth piloto"   │                    │
   │                  │──────────────────┼───────────────────►│
   │                  │                  │  ◄── nodos ────────│
   │                  │                  │                    │
   │  "✅✅ ⚠️ ❌    │                  │                    │
   │   Auth sin ADR"  │                  │                    │
   │◄─────────────────│                  │                    │
   │                  │                  │                    │
   │  "Agrega         │                  │                    │
   │   comentarios    │                  │                    │
   │   y crea ADR"    │                  │                    │
   │─────────────────►│                  │                    │
   │                  │                  │                    │
   │                  │  add-comment x2  │                    │
   │                  │─────────────────►│                    │
   │                  │                  │                    │
   │                  │  find-skill-page │                    │
   │                  │  ("ADR")         │                    │
   │                  │─────────────────►│                    │
   │                  │                  │                    │
   │                  │  create-page     │                    │
   │                  │  (ADR-003)       │                    │
   │                  │─────────────────►│                    │
   │                  │                  │                    │
   │                  │  graph-sync      │                    │
   │                  │  (ADR + rels)    │                    │
   │                  │──────────────────┼───────────────────►│
   │                  │                  │                    │
   │                  │  transition-jira │                    │
   │                  │  → In Progress   │                    │
   │                  │─────────────────►│ (Jira)             │
   │                  │                  │                    │
   │  "2 comentarios  │                  │                    │
   │   + ADR-003      │                  │                    │
   │   creado"        │                  │                    │
   │◄─────────────────│                  │                    │
   │                  │                  │                    │
```

### Test Case 3: Carlos (Dev) consulta constraints antes de codear

**Precondiciones:**
- LBC aprobado, ADR-003 creado e indexado en el grafo
- Story "Implement Auth" asignada a Carlos, In Progress

**Flujo (lo que Carlos experimenta):**

1. Carlos abre Rovo Chat (desde Confluence, Jira, o el IDE si tiene el plugin)
2. Carlos dice: *"Voy a implementar el módulo de auth para Iniciativa Piloto"*
3. Rai Dev responde:
   - *"Antes de empezar, estos constraints de governance aplican:"*
   - *"📋 ADR-003 (mandatory): OAuth2 con JWT"*
   - *"📋 STD-SEC-01: OWASP Top 10 compliance"*
   - *"📋 From LBC: capacity 50K concurrent users"*
   - *"Estos son verificables — si tu código no cumple ADR-003, lo voy a flag."*
4. Carlos procede a implementar
5. Si Carlos intenta usar session-based auth, Rai Dev:
   - *"⛔ Esto usa session auth, pero ADR-003 requiere OAuth2 con JWT. ¿Refactorizo o quieres desafiar el ADR?"*

**Lo que Carlos VE:** constraints claros ANTES de codear, con fuente citada. Si viola uno, flag inmediato con referencia al documento de governance.

```
┌────────┐       ┌──────────┐                            ┌──────────┐
│ Carlos │       │Rai Dev   │                            │  Backend │
│  (Dev) │       │  (Rovo)  │                            │          │
└───┬────┘       └────┬─────┘                            └────┬─────┘
    │                 │                                       │
    │  "Implementar   │                                       │
    │   auth para     │                                       │
    │   Piloto"       │                                       │
    │────────────────►│                                       │
    │                 │                                       │
    │                 │  read-jira-ctx                        │
    │                 │──────────────────────────────────────►│(Jira)
    │                 │  ◄── story + epic ctx ────────────────│
    │                 │                                       │
    │                 │  graph-query                          │
    │                 │  "auth piloto"                        │
    │                 │──────────────────────────────────────►│
    │                 │  ◄── ADR-003, STD-SEC-01, LBC data ──│
    │                 │                                       │
    │  "📋 ADR-003:   │                                       │
    │   OAuth2+JWT    │                                       │
    │   📋 STD-SEC-01 │                                       │
    │   📋 LBC: 50K"  │                                       │
    │◄────────────────│                                       │
    │                 │                                       │
    │  [implementa    │                                       │
    │   con session   │                                       │
    │   auth]         │                                       │
    │────────────────►│                                       │
    │                 │                                       │
    │  "⛔ ADR-003    │                                       │
    │   requiere      │                                       │
    │   OAuth2+JWT"   │                                       │
    │◄────────────────│                                       │
    │                 │                                       │
```

### Test Case 4: Extensibilidad — Nuevo tipo de documento sin código

**Precondiciones:**
- Fase 5 del plan. El agente ya funciona con Problem Scope.

**Flujo:**

1. Emilio crea una página en Confluence: "Skill: Lean Business Case"
   - Usa el formato de skill page (Description, Inputs, Process, Outputs, Template, Validation Rules, Graph Relations)
2. Ana abre Rovo Chat: *"Necesito crear un Lean Business Case para Iniciativa Beta"*
3. Rai:
   - Busca `find-skill-page("Lean Business Case")` → **lo encuentra** (es una página nueva)
   - Lee el skill, extrae inputs/process/outputs
   - Ejecuta el skill igual que antes — mismas acciones, mismo flujo
4. **ZERO código cambiado. ZERO deploy. Solo una página de Confluence.**

```
┌────────┐       ┌──────────┐       ┌──────────┐
│ Emilio │       │Confluence│       │Rai (Rovo)│
└───┬────┘       └────┬─────┘       └────┬─────┘
    │                 │                   │
    │  Crea página    │                   │
    │  "Skill: LBC"   │                   │
    │────────────────►│                   │
    │                 │                   │
    │                 │    (tiempo pasa)  │
    │                 │                   │
    │                 │   Ana: "Crear     │
    │                 │    LBC para Beta" │
    │                 │◄──────────────────│(user message)
    │                 │                   │
    │                 │  find-skill-page  │
    │                 │  ("LBC")         │
    │                 │◄──────────────────│
    │                 │──── found! ──────►│
    │                 │                   │
    │                 │  (mismo flujo     │
    │                 │   que Test Case 1)│
    │                 │                   │
    │                 │  ZERO code change │
    │                 │  ZERO deploy      │
    │                 │                   │
```

**Este ES el killer demo para Coppel:** "¿Quieren agregar un nuevo proceso de governance? Creen una página en Confluence. Listo."

---

## 1. Decisiones Arquitectónicas

### DA-1: Tres Capas, Tres Responsabilidades

| Capa | Responsabilidad | Tecnología | Determinismo |
|------|----------------|------------|--------------|
| **UI** | Interacción con humanos | Forge App (Rovo Agents) | No (LLM) |
| **Content** | Almacén de documentos | Confluence + Jira | N/A (storage) |
| **Knowledge** | Relaciones, validación, trazabilidad | RaiSE Backend ✅ | **Sí** |

**Por qué tres capas:**
- Confluence es buen content store pero mal knowledge graph (no tiene relaciones tipadas)
- Teamwork Graph de Atlassian es RAG probabilístico, no garantiza resultados
- RaiSE knowledge graph es neuro-simbólico: nodos tipados, relaciones explícitas, traversal determinista
- La UI (Rovo) es donde vive el LLM — la parte no-determinista está contenida aquí
- El backend es donde vive el determinismo — validación, trazabilidad, consistencia

### DA-2: Un Agente Contextual que Ejecuta Skills de Confluence

**Decisión:** Un solo Rovo Agent ("Rai") que detecta contexto, lee skills desde
Confluence, y los ejecuta. El agente no tiene conocimiento de governance hardcoded —
toda la inteligencia de proceso vive en skill pages.

**Estructura de spaces en Confluence:**
```
Governance Hub (Space)
├── 📁 Skills/
│   ├── 📄 Skill: Problem Scope
│   ├── 📄 Skill: Lean Business Case
│   ├── 📄 Skill: Architecture Review
│   └── 📄 Skill: Portfolio Canvas
│
├── 📁 Standards/
│   ├── 📄 Python Coding Standards
│   ├── 📄 API Design Guidelines
│   └── 📄 Security Requirements
│
├── 📁 Architecture Decisions/
│   ├── 📄 ADR-001: PostgreSQL
│   ├── 📄 ADR-002: Event-driven
│   └── 📄 ADR-003: OAuth2
│
└── 📁 Templates/
    ├── 📄 Template: Problem Scope
    ├── 📄 Template: LBC
    └── 📄 Template: ADR
```

**Agregar un nuevo proceso de governance = crear una página en Confluence.**
No code, no deploy.

### DA-3: Skills como Páginas de Confluence

Cada skill es una página con estructura parseable que el agente lee y ejecuta.

**Skill Page Format:**

```
# Skill: {Name}

## Description
{What this skill produces and why}

## Inputs
| Input | Source | Required |
|-------|--------|----------|
| {name} | {user/jira/confluence/graph} | {yes/no} |

## Process

### Step 1: {name}
{instructions for the agent}

### Step 2: {name}
{instructions}

## Outputs
| Artifact | Type | Destination |
|----------|------|-------------|
| {name} | {confluence-page/jira-issue/comment/...} | {where} |

## Template
{The document template — Confluence storage format}

## Validation Rules
- [ ] {rule 1 — deterministic check}
- [ ] {rule 2}

## Graph Relations
| From | Relation | To |
|------|----------|----|
| this document | traces-to | {parent epic/LBC/...} |
| this document | governed-by | {applicable ADRs/standards} |

## Review Checklist
- [ ] {review criterion 1}
- [ ] {review criterion 2}
```

**La sección "Graph Relations" es clave:** le dice al backend qué nodos y relaciones
crear cuando se indexa el documento. Esto es lo que Teamwork Graph NO hace.

### DA-4: Acciones como Primitivas de Tres Dominios

Las acciones cubren tres dominios (Confluence, Jira, RaiSE Backend).
El agente las compone según las instrucciones del skill.

#### Confluence Actions

| Acción | Verbo | Qué hace |
|--------|-------|----------|
| `read-confluence-page` | GET | Lee contenido + properties + labels + status |
| `create-confluence-page` | CREATE | Crea página con metadata, labels, governance property |
| `update-confluence-page` | UPDATE | Actualiza contenido + version message + metadata |
| `read-page-comments` | GET | Lee comentarios (feedback de revisores) |
| `add-page-comment` | CREATE | Agrega comentario de revisión |
| `find-skill-page` | GET | Busca skill pages en el space de Governance Skills |

#### Jira Actions

| Acción | Verbo | Qué hace |
|--------|-------|----------|
| `read-jira-context` | GET | Lee issue, epic, status, assignee, linked pages |
| `transition-jira-issue` | UPDATE | Mueve issue de status |

#### RaiSE Backend Actions

| Acción | Verbo | Backend Endpoint | Qué hace |
|--------|-------|-----------------|----------|
| `graph-sync` | CREATE | `POST /api/v1/graph/sync` | Envía nodos/edges parseados del documento al grafo |
| `graph-query` | GET | `GET /api/v1/graph/query` | Búsqueda keyword en el grafo (determinista) |
| `report-event` | CREATE | `POST /api/v1/agent/events` | Rovo reporta acciones ejecutadas |
| `share-pattern` | CREATE | `POST /api/v1/memory/patterns` | Rovo comparte patrones aprendidos |

**Nota:** Los endpoints `governance/validate`, `dev/constraints`, `graph/trace` y
`graph/impact` están deferred para post-POC. Para el POC, la validación se hace
combinando LLM + `graph/query`, y los constraints se consultan via `graph/query`
con filtro por tipo de nodo.

#### Ephemeral State

| Acción | Verbo | Qué hace |
|--------|-------|----------|
| `save-draft-state` | CREATE | Estado efímero pre-documento en Forge Storage |
| `load-draft-state` | GET | Recupera borrador en progreso |

### DA-5: Estado del Documento en Confluence, Estado del Conocimiento en el Grafo

| Dato | Dónde vive | Mecanismo |
|------|-----------|-----------|
| Contenido del documento | Confluence page body | Storage format |
| Metadata de governance | Content property `rai-governance` | JSON en la página |
| Log de cambios | Version history | Version messages ("Rai: ...") |
| Status del workflow | Page status | Draft / In Review / Approved |
| Clasificación | Page labels | `rai-generated`, `problem-scope` |
| Feedback de revisión | Page comments | Comentarios nativos |
| **Relaciones entre documentos** | **RaiSE knowledge graph** | **Nodos tipados + edges** |
| **Trazabilidad** | **RaiSE knowledge graph** | **Graph traversal** |
| **Validación de consistencia** | **RaiSE knowledge graph** | **Queries deterministas** |
| **Constraints para devs** | **RaiSE knowledge graph** | **graph/query con filtros** |
| Borrador pre-publicación | Forge Storage | Efímero, se borra al publicar |

**Principio:** Confluence almacena **contenido**. RaiSE almacena **conocimiento**.
Confluence responde "¿qué dice el documento?". RaiSE responde "¿qué significa?
¿es consistente? ¿qué impacta?".

### DA-6: Detección de Contexto y Modos de Operación

| Señal | Modo | Comportamiento |
|-------|------|---------------|
| No hay documento vinculado | **CREATE** | Lee skill page, guía creación |
| Documento draft + user es assignee | **ELABORATE** | Ayuda a llenar/mejorar |
| Documento in review + user es reviewer | **REVIEW** | Evalúa contra grafo + standards |
| Hay comentarios sin resolver | **REFINE** | Muestra feedback, ayuda a resolver |
| User pide validación explícita | **VALIDATE** | Invoca graph/query: busca gaps y conflictos |
| User es dev + pide guidance | **GUIDE** | Query al grafo por ADRs, standards, patterns del módulo |

### DA-7: Jira como Orquestador

**Jira Automation crea la estructura. Rai opera dentro de ella.**

```
JSM Request ("New Initiative")
  → Jira Automation:
      1. Create Epic "Iniciativa: {nombre}"
      2. Create Story "Problem Scope" → Create Confluence page from template
      3. Create Story "Lean Business Case" → Create Confluence page from template
      4. Create Story "Architecture Review" → Create Confluence page from template
      5. Link pages to stories
```

Rai NO crea la estructura de trabajo. Solo trabaja dentro de ella.
Si Rai se cae, el proceso sigue — los humanos pueden trabajar sin él.

### DA-8: Dos Agentes, Un App

```yaml
rovo:agent:
  - key: rai-governance       # Para governance en Confluence
    name: "Rai"
    prompt: resource:static-resources;prompts/rai-governance.txt

  - key: rai-dev               # Para devs en IDE/Jira
    name: "Rai Dev"
    prompt: resource:static-resources;prompts/rai-dev.txt
```

Comparten las mismas acciones. Diferentes prompts, diferentes modos.

- **Rai Governance:** CREATE, ELABORATE, REVIEW, REFINE, VALIDATE
- **Rai Dev:** GUIDE (consulta constraints del grafo antes de generar código)

### DA-9: Backend RaiSE — Disponible (E275)

El backend **ya existe** (Epic RAISE-275, merged to dev 2026-02-26).

**Endpoints disponibles:**

```
# === Graph Operations ===

POST /api/v1/graph/sync
  Input:  { project_id: str, nodes: [{node_id, node_type, scope, content,
            source_file?, properties?}], edges: [{source_node_id,
            target_node_id, edge_type, weight?, properties?}] }
  Output: { status, project_id, nodes_upserted, edges_created,
            edges_skipped, nodes_pruned }
  Notes:  Idempotent upsert. Replaces all nodes/edges for a project.
          Forge action pre-parses Confluence doc into nodes/edges.

GET  /api/v1/graph/query
  Input:  ?q=...&limit=N
  Output: { results: [{node_id, node_type, scope, content, source_file,
            properties, rank}], total, query, limit }
  Notes:  GIN full-text search. Deterministic. Same input → same output.

# === Agent Telemetry ===

POST /api/v1/agent/events
  Input:  { agent_id, event_type, payload }
  Output: { id, agent_id, event_type, created_at }
  Notes:  Rovo reports actions executed (create, update, review, validate).

GET  /api/v1/agent/events
  Input:  ?agent_id=...&limit=N
  Output: { events: [...], total }

# === Memory / Patterns ===

POST /api/v1/memory/patterns
  Input:  { content, context, pattern_type, source }
  Output: { id, content, created_at }
  Notes:  Rovo shares patterns learned during governance workflows.

GET  /api/v1/memory/patterns
  Input:  ?limit=N
  Output: { patterns: [...], total }
```

**Auth:** `Authorization: Bearer rsk_...` (API key per org, hash in DB).
**Infrastructure:** Docker Compose (PG 16 + FastAPI). `docker compose up` in raise-commons.
**OpenAPI spec:** Auto-generated at `http://localhost:8000/docs`.
**Validated:** E2E with 1589 nodes + 33k edges from real raise-commons graph.

**Endpoints deferred (post-POC):**
- `POST /governance/validate` — POC uses LLM + graph/query combo
- `GET /dev/constraints` — POC uses graph/query with type filtering
- `GET /graph/trace` — trazabilidad upstream/downstream
- `GET /graph/impact` — análisis de impacto

### DA-10: Entornos y Testing

**Forge:** dev/staging/production desde el día 1.
**Backend:** Docker Compose for dev. Future: staging/prod with separate DBs.
**Testing:** Jest for actions, Rovo Studio for prompts, E2E manual with tunnel.

---

## 2. Walking Skeleton — Ciclo End-to-End de 3 Capas

### Lo que prueba el skeleton

| # | Paso | Capa | Prueba que... |
|---|------|------|---------------|
| 1 | Skill page existe en Confluence | Content | Skills como páginas funciona |
| 2 | Rai lee el skill page | UI | `find-skill-page` + `read-confluence-page` |
| 3 | Rai guía creación de documento | UI | Ejecución de skill conversacional |
| 4 | Documento se crea en Confluence | Content | `create-confluence-page` + properties + labels |
| 5 | **Backend indexa el documento en el grafo** | **Knowledge** | **`graph-sync` funciona** |
| 6 | PO elabora con Rai, página se actualiza | UI+Content | `update-confluence-page` + version messages |
| 7 | PO manda a review, Jira transiciona | Content | `transition-jira-issue` |
| 8 | Architect revisa con Rai | UI | Modo REVIEW, agrega comentarios |
| 9 | **Rai valida contra el grafo** | **Knowledge** | **`graph-query` + LLM analysis** |
| 10 | PO refina basado en feedback | UI+Content | Modo REFINE, actualiza doc |
| 11 | **Dev pide constraints, grafo responde** | **Knowledge** | **`graph-query` con filtro por tipo** |
| 12 | Documento se aprueba, ciclo cierra | All | Loop completo funciona |

### Flujo Visual

```
FASE 1: SETUP (Jira Automation, no Rai)
══════════════════════════════════════════

JSM Request: "Iniciativa Piloto"
    │
    ▼
Jira Automation:
    Epic: "Iniciativa Piloto"
    ├── Story: "Lean Business Case"  →  📄 LBC page (from template)
    ├── Story: "Problem Scope"       →  📄 PS page (from template)
    └── Story: "Arch Review"         →  📄 AR page (from template)


FASE 2: ELABORACIÓN (Ana, PO — Rai Governance)
══════════════════════════════════════════════════

Ana abre Story "LBC" en Jira, habla con Rai:
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ Rai Governance Agent                                         │
│                                                              │
│ 1. read-jira-context("PROJ-45")                              │
│    → Story "LBC", In Progress, assignee: Ana, epic: Piloto   │
│    → linked page: "LBC: Iniciativa Piloto"                   │
│                                                              │
│ 2. read-confluence-page(linked page)                         │
│    → Template vacío, no governance property                  │
│    → MODE: CREATE                                            │
│                                                              │
│ 3. find-skill-page("Lean Business Case")                     │
│    → Lee skill page del space Governance Skills               │
│    → Extrae: inputs, process, outputs, template, validation  │
│                                                              │
│ 4. Ejecuta el skill:                                         │
│    a. Pide inputs según skill definition                     │
│    b. Guía conversación paso a paso                          │
│    c. update-confluence-page(content + version message)      │
│    d. Set content property: rai-governance                   │
│    e. Add labels: rai-generated, lean-business-case          │
│                                                              │
│ 5. graph-sync(project_id, nodes, edges)              ◄── KG  │
│    → Backend indexa LBC como nodo tipado                     │
│    → Crea: LBC --traces-to--> Epic "Piloto"                 │
│    → Crea: LBC --requires--> concept:auth                   │
│                                                              │
│ 6. report-event(agent_id, "document-created", {...}) ◄── Tel │
│                                                              │
│ 7. Reporta a Ana: "Documento creado, v2. Link: ..."         │
└─────────────────────────────────────────────────────────────┘
                         │
                    Confluence
                         │
    📄 "LBC: Iniciativa Piloto"
    ├── Body: [contenido generado]
    ├── Property: rai-governance = {documentType: "lbc", step: "draft"}
    ├── Labels: [rai-generated, lean-business-case]
    ├── Version History:
    │   v1: Created from template (Automation)
    │   v2: Rai: Initial LBC draft — problem + stakeholders + financials
    └── Status: Draft


FASE 3: REVIEW (Rodo, Architect — Rai Governance)
═══════════════════════════════════════════════════

Rodo abre la misma Story, habla con Rai:
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ Rai Governance Agent                                         │
│                                                              │
│ 1. read-jira-context → In Review, Rodo is reviewer           │
│ 2. read-confluence-page → LBC content + property             │
│ 3. MODE: REVIEW                                              │
│                                                              │
│ 4. graph-query(q="auth piloto", limit=20)            ◄── KG  │
│    → LLM analiza resultados del grafo:                       │
│      ✅ Problem statement: hypothesis format                 │
│      ✅ Stakeholders: identified                             │
│      ⚠️ Risks: mentioned but not quantified                 │
│      ❌ No ADR for auth approach mentioned in solution       │
│      Coverage: ADRs 0/1, Standards 2/3                       │
│                                                              │
│ 5. Rai presents findings to Rodo (graph facts + LLM analysis)│
│                                                              │
│ 6. add-page-comment(review feedback)                         │
│    → "Review (Rodo via Rai): Risks need quantification..."   │
│    → "Review (Rodo via Rai): Auth approach needs ADR..."     │
│                                                              │
│ 7. transition-jira-issue → back to In Progress               │
│ 8. report-event(agent_id, "document-reviewed", {...})        │
└─────────────────────────────────────────────────────────────┘


FASE 4: REFINAMIENTO (Ana, PO — Rai Governance)
═════════════════════════════════════════════════

Ana vuelve, habla con Rai:
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ Rai Governance Agent                                         │
│                                                              │
│ 1. read-confluence-page → property {step: "revision-1"}      │
│ 2. read-page-comments → 2 unresolved comments               │
│ 3. MODE: REFINE                                              │
│                                                              │
│ 4. Shows pending feedback, works through each:               │
│    a. Quantifies risks → update-confluence-page              │
│       version msg: "Rai: Quantified risks per Rodo's review" │
│    b. Notes ADR gap → suggests creating ADR for auth         │
│                                                              │
│ 5. graph-sync(updated nodes + new relations)         ◄── KG  │
│    → Updates LBC node, adds: LBC --needs-adr--> concept:auth │
│                                                              │
│ 6. Ana moves to Review again                                 │
│    → Rodo approves → Story: Done → Page status: Approved     │
│    → graph-sync updates: LBC step = "approved"               │
└─────────────────────────────────────────────────────────────┘


FASE 5: DEV CONSUMES (Developer — Rai Dev)
═══════════════════════════════════════════

Dev implementing auth for Iniciativa Piloto:
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ Rai Dev Agent (or rai-cli)                                   │
│                                                              │
│ 1. read-jira-context → Story "Implement auth", epic: Piloto  │
│                                                              │
│ 2. graph-query(q="auth piloto", limit=20)            ◄── KG  │
│    → DETERMINISTIC results:                                  │
│      ADRs: [ADR-003: "Must use OAuth2 with JWT"]             │
│      Standards: [STD-SEC-01: "OWASP Top 10 compliance"]      │
│      Patterns: [PAT-001: "JWT validation middleware"]        │
│      From LBC: "Auth for 50K concurrent users"               │
│                                                              │
│ 3. Rai Dev generates code that complies with ALL constraints │
│    "Based on ADR-003 (mandatory), implementing OAuth2..."    │
│                                                              │
│ 4. If code would violate a constraint → STOP and flag        │
└─────────────────────────────────────────────────────────────┘
```

### Conversaciones del Skeleton

**Conversación 1: Ana (PO) crea el LBC**

```
Ana:  Necesito trabajar en el Lean Business Case de Iniciativa
      Piloto. Tengo las notas de la sesión con el cliente.
      [pega transcript]

Rai:  [read-jira-context → PROJ-45, "LBC", In Progress, Ana]
      [read-confluence-page → template vacío]
      [find-skill-page → lee "Skill: Lean Business Case"]

      Estoy en la story PROJ-45 (Lean Business Case) que está
      In Progress. La página existe pero está vacía.

      Cargué el skill "Lean Business Case". Necesito estos
      inputs:
      ✅ Transcript — lo tengo
      ❓ Costo del status quo — no lo veo en las notas
      ❓ Sponsor ejecutivo — ¿quién firma?

Ana:  El status quo cuesta $150K/mes en retrabajo. El sponsor
      es Carlos, VP de Finanzas.

Rai:  [update-confluence-page → draft con version message
       "Rai: Initial LBC from session transcript + clarifications"]
      [graph-sync → indexa LBC, crea relaciones al epic]
      [report-event → "document-created"]

      Creé el draft. Secciones:
      ✅ Problem Statement (hypothesis format)
      ✅ Stakeholders (Carlos sponsor, 3 más del transcript)
      ✅ Financial Impact ($150K/mes, $1.8M/año)
      ⚠️ Success Metrics — necesitan targets específicos
      ❌ Implementation Strategy — pendiente

      Indexé el documento en el knowledge graph con trazabilidad
      al Epic "Iniciativa Piloto".

      ¿Seguimos con las métricas?
```

**Conversación 2: Rodo (Architect) revisa**

```
Rodo: Quiero revisar el LBC de Iniciativa Piloto.

Rai:  [read-jira-context → In Review, Rodo]
      [read-confluence-page → LBC content + property]
      [graph-query → busca nodos relacionados a "auth piloto"]

      El LBC está en Review. Mi análisis combinando el grafo
      y el contenido del documento:

      ✅ Problem Statement: hypothesis format correcto
      ✅ Financial Impact: cuantificado ($1.8M/año)
      ⚠️ Risks: mencionados pero sin cuantificar
         (probabilidad × impacto ausentes)
      ❌ Auth approach: el documento menciona "autenticación
         para 50K usuarios" pero el grafo no tiene ADR que
         la respalde. Se necesita ADR para la decisión de auth.

      ¿Agrego comentarios de revisión?

Rodo: Sí, agrega los comentarios. Y crea un ADR para auth
      basado en lo que dice el LBC.

Rai:  [add-page-comment → 2 comentarios de revisión]
      [find-skill-page → lee "Skill: ADR"]
      [create-confluence-page → nuevo ADR con datos del LBC]
      [graph-sync → indexa ADR, crea relaciones]
      [report-event → "document-reviewed", "document-created"]

      Hecho:
      - 2 comentarios de revisión en el LBC
      - Nuevo ADR: "ADR-003: OAuth2 for Iniciativa Piloto"
        → Indexado en el grafo con relación al LBC
      - Story PROJ-45 devuelta a In Progress

      Cuando el dev implemente auth, Rai Dev le dirá que
      ADR-003 aplica.
```

**Conversación 3: Dev consume governance**

```
Dev:  Voy a implementar el módulo de auth para Iniciativa
      Piloto.

Rai Dev:
      [read-jira-context → Story "Implement Auth", epic: Piloto]
      [graph-query → busca "auth" + "piloto" en el grafo]

      Antes de empezar, estos son los constraints de governance
      para auth en Iniciativa Piloto:

      📋 ADR-003 (mandatory): OAuth2 con JWT
         "All API authentication must use OAuth2 with JWT tokens.
          Session-based auth is not permitted."
         → Traces to: LBC Iniciativa Piloto (approved)

      📋 STD-SEC-01: OWASP Top 10 compliance
         "JWT tokens must expire in ≤1 hour.
          Refresh tokens must be rotatable."

      📋 From LBC: capacity requirement = 50K concurrent users

      Estos son verificables — si tu código no cumple ADR-003,
      lo voy a flag antes del commit.

      ¿Procedemos con la implementación?
```

---

## 3. Manifest Completo

```yaml
# manifest.yml
modules:
  rovo:agent:
    - key: rai-governance
      name: "Rai"
      description: >
        Governance copilot for Lean Portfolio Management.
        Reads skill definitions from Confluence, executes them
        conversationally, and queries the RaiSE knowledge graph
        for deterministic governance validation.
      prompt: resource:static-resources;prompts/rai-governance.txt
      conversationStarters:
        - Help me work on a governance document
        - Review this document against standards
        - Show me pending review comments
        - What governance gaps exist in this initiative?
      actions:
        - find-skill-page
        - read-confluence-page
        - create-confluence-page
        - update-confluence-page
        - read-page-comments
        - add-page-comment
        - read-jira-context
        - transition-jira-issue
        - graph-sync
        - graph-query
        - report-event
        - share-pattern
        - save-draft-state
        - load-draft-state

    - key: rai-dev
      name: "Rai Dev"
      description: >
        Development copilot that ensures code complies with
        governance decisions, architecture standards, and
        organizational patterns from the RaiSE knowledge graph.
      prompt: resource:static-resources;prompts/rai-dev.txt
      conversationStarters:
        - What constraints apply to this module?
        - Check if my implementation follows the ADRs
        - What standards govern this project?
      actions:
        - read-confluence-page
        - read-jira-context
        - graph-query
        - report-event

  action:
    # === Confluence: Skills ===
    - key: find-skill-page
      name: Find Governance Skill
      function: findSkill
      actionVerb: GET
      description: >
        Searches for a governance skill definition page in the
        Governance Skills space. Returns the skill page content
        including inputs, process, outputs, and validation rules.
      inputs:
        skillName:
          title: Skill Name
          type: string
          required: true
          description: "Name or keyword to find the skill (e.g. 'Problem Scope', 'LBC')"
        spaceKey:
          title: Skills Space
          type: string
          required: false
          description: "Space key where skills live (default: GOV)"

    # === Confluence: Page CRUD ===
    - key: read-confluence-page
      name: Read Confluence Page
      function: readPage
      actionVerb: GET
      description: >
        Reads a Confluence page: content, governance properties,
        labels, status, and version info.
      inputs:
        pageId:
          title: Page ID
          type: string
          required: false
          description: "Confluence page ID"
        spaceKey:
          title: Space Key
          type: string
          required: false
          description: "Space key (use with pageTitle)"
        pageTitle:
          title: Page Title
          type: string
          required: false
          description: "Exact page title (use with spaceKey)"

    - key: create-confluence-page
      name: Create Confluence Page
      function: createPage
      actionVerb: CREATE
      description: >
        Creates a new Confluence page with content, governance
        metadata, and labels.
      inputs:
        spaceKey:
          title: Space Key
          type: string
          required: true
          description: "Target Confluence space"
        title:
          title: Page Title
          type: string
          required: true
          description: "Document title"
        content:
          title: Content
          type: string
          required: true
          description: "Page content in Confluence storage format"
        parentPageId:
          title: Parent Page ID
          type: string
          required: false
          description: "Parent page for hierarchy"
        labels:
          title: Labels
          type: string
          required: false
          description: "Comma-separated labels"
        governanceMetadata:
          title: Governance Metadata
          type: string
          required: false
          description: "JSON for rai-governance content property"

    - key: update-confluence-page
      name: Update Confluence Page
      function: updatePage
      actionVerb: UPDATE
      description: >
        Updates page content with a descriptive version message.
        Always explain what changed and why in the version message.
      inputs:
        pageId:
          title: Page ID
          type: string
          required: true
          description: "The page ID to update"
        content:
          title: New Content
          type: string
          required: true
          description: "Updated page content in storage format"
        versionMessage:
          title: Version Message
          type: string
          required: true
          description: "Change description (e.g. 'Rai: Added risk quantification')"
        governanceMetadata:
          title: Updated Metadata
          type: string
          required: false
          description: "JSON to update rai-governance property"

    # === Confluence: Comments ===
    - key: read-page-comments
      name: Read Page Comments
      function: readComments
      actionVerb: GET
      description: >
        Reads all comments on a page. Use to find pending
        review feedback.
      inputs:
        pageId:
          title: Page ID
          type: string
          required: true
          description: "Page to read comments from"

    - key: add-page-comment
      name: Add Page Comment
      function: addComment
      actionVerb: CREATE
      description: >
        Adds a review comment to a page. Format:
        "Review ({name} via Rai): {feedback}"
      inputs:
        pageId:
          title: Page ID
          type: string
          required: true
          description: "Page to comment on"
        comment:
          title: Comment
          type: string
          required: true
          description: "Review comment in storage format"

    # === Jira ===
    - key: read-jira-context
      name: Read Jira Context
      function: readJiraContext
      actionVerb: GET
      description: >
        Reads issue context: summary, status, type, assignee,
        parent epic, linked Confluence pages.
      inputs:
        issueKey:
          title: Issue Key
          type: string
          required: true
          description: "Jira issue key (e.g. PROJ-123)"

    - key: transition-jira-issue
      name: Transition Jira Issue
      function: transitionIssue
      actionVerb: UPDATE
      description: >
        Moves a Jira issue to a new status. Always confirm
        with the user before transitioning.
      inputs:
        issueKey:
          title: Issue Key
          type: string
          required: true
          description: "Issue to transition"
        transitionName:
          title: Target Status
          type: string
          required: true
          description: "Target status name (e.g. 'In Review')"

    # === RaiSE Backend ===
    - key: graph-sync
      name: Sync to Knowledge Graph
      function: graphSync
      actionVerb: CREATE
      description: >
        Sends parsed document nodes and edges to the RaiSE
        knowledge graph. Call after creating or significantly
        updating a governance document. The Forge action
        pre-parses Confluence content into typed nodes and
        relation edges before calling the backend.
      inputs:
        projectId:
          title: Project ID
          type: string
          required: true
          description: "Project identifier for graph scoping"
        nodes:
          title: Graph Nodes
          type: string
          required: true
          description: "JSON array of {node_id, node_type, scope, content, source_file?, properties?}"
        edges:
          title: Graph Edges
          type: string
          required: false
          description: "JSON array of {source_node_id, target_node_id, edge_type, weight?, properties?}"

    - key: graph-query
      name: Query Knowledge Graph
      function: graphQuery
      actionVerb: GET
      description: >
        Keyword search on the RaiSE knowledge graph.
        Returns typed nodes ranked by relevance.
        Same input always produces same output.
      inputs:
        query:
          title: Query
          type: string
          required: true
          description: "Search keywords (e.g. 'auth piloto')"
        limit:
          title: Max Results
          type: number
          required: false
          description: "Maximum results to return (default: 20)"

    - key: report-event
      name: Report Agent Event
      function: reportEvent
      actionVerb: CREATE
      description: >
        Reports an agent action to RaiSE telemetry.
        Call after significant actions (document created,
        reviewed, validated).
      inputs:
        agentId:
          title: Agent ID
          type: string
          required: true
          description: "Agent identifier (e.g. 'rai-governance')"
        eventType:
          title: Event Type
          type: string
          required: true
          description: "Action type (e.g. 'document-created', 'document-reviewed')"
        payload:
          title: Event Payload
          type: string
          required: false
          description: "JSON with event details"

    - key: share-pattern
      name: Share Pattern
      function: sharePattern
      actionVerb: CREATE
      description: >
        Shares a learned pattern with the team via the
        RaiSE memory system.
      inputs:
        content:
          title: Pattern
          type: string
          required: true
          description: "Pattern description"
        context:
          title: Context
          type: string
          required: false
          description: "Keywords for when this pattern applies"
        patternType:
          title: Type
          type: string
          required: false
          description: "Pattern type (e.g. 'governance', 'process')"

    # === Ephemeral State ===
    - key: save-draft-state
      name: Save Draft State
      function: saveDraft
      actionVerb: CREATE
      description: >
        Saves ephemeral pre-document state. Use ONLY before
        a Confluence page exists. Once published, use content
        properties instead.
      inputs:
        draftId:
          title: Draft ID
          type: string
          required: true
          description: "Unique draft identifier"
        state:
          title: State
          type: string
          required: true
          description: "JSON draft data"

    - key: load-draft-state
      name: Load Draft State
      function: loadDraft
      actionVerb: GET
      description: >
        Loads ephemeral draft state.
      inputs:
        draftId:
          title: Draft ID
          type: string
          required: true
          description: "Draft ID to load"

  function:
    # Confluence
    - key: findSkill
      handler: src/actions/confluence.findSkill
    - key: readPage
      handler: src/actions/confluence.readPage
    - key: createPage
      handler: src/actions/confluence.createPage
    - key: updatePage
      handler: src/actions/confluence.updatePage
    - key: readComments
      handler: src/actions/confluence.readComments
    - key: addComment
      handler: src/actions/confluence.addComment
    # Jira
    - key: readJiraContext
      handler: src/actions/jira.readJiraContext
    - key: transitionIssue
      handler: src/actions/jira.transitionIssue
    # RaiSE Backend
    - key: graphSync
      handler: src/actions/raise.graphSync
    - key: graphQuery
      handler: src/actions/raise.graphQuery
    - key: reportEvent
      handler: src/actions/raise.reportEvent
    - key: sharePattern
      handler: src/actions/raise.sharePattern
    # State
    - key: saveDraft
      handler: src/actions/state.saveDraft
    - key: loadDraft
      handler: src/actions/state.loadDraft

resources:
  - key: static-resources
    path: static

app:
  runtime:
    name: nodejs22.x
  id: <app-id>

permissions:
  scopes:
    - read:confluence-content.all
    - write:confluence-content
    - write:confluence-props
    - read:confluence-space.summary
    - read:jira-work
    - write:jira-work
    - read:chat:rovo
  external:
    fetch:
      backend:
        - 'raise-api.humansys.ai'
        - '*.ngrok-free.app'
```

---

## 4. Implementación de Acciones

### src/actions/confluence.js

```javascript
import api, { route } from '@forge/api';

// === FIND SKILL ===

export async function findSkill(payload) {
  const { skillName, spaceKey = 'GOV' } = payload;

  const cql = `space = "${spaceKey}" AND title ~ "Skill: ${skillName}" AND type = page`;
  const res = await api.asUser().requestConfluence(
    route`/wiki/rest/api/content/search?cql=${encodeURIComponent(cql)}&expand=body.storage`
  );
  const data = await res.json();
  const page = data.results?.[0];

  if (!page) {
    return { found: false, query: skillName, space: spaceKey };
  }

  return {
    found: true,
    id: page.id,
    title: page.title,
    content: page.body?.storage?.value || '',
  };
}

// === READ PAGE ===

export async function readPage(payload) {
  const { pageId, spaceKey, pageTitle } = payload;

  let page;
  if (pageId) {
    const res = await api.asUser().requestConfluence(
      route`/wiki/api/v2/pages/${pageId}?body-format=storage`
    );
    page = await res.json();
  } else if (spaceKey && pageTitle) {
    const res = await api.asUser().requestConfluence(
      route`/wiki/api/v2/spaces/${spaceKey}/pages?title=${pageTitle}&body-format=storage`
    );
    const data = await res.json();
    page = data.results?.[0];
  } else {
    return { error: 'Provide pageId or both spaceKey and pageTitle' };
  }

  if (!page) return { error: 'Page not found' };

  // Content property
  let governance = null;
  try {
    const propRes = await api.asUser().requestConfluence(
      route`/wiki/api/v2/pages/${page.id}/properties?key=rai-governance`
    );
    const propData = await propRes.json();
    governance = propData.results?.[0]?.value || null;
  } catch (e) { /* no property */ }

  // Labels
  let labels = [];
  try {
    const labelRes = await api.asUser().requestConfluence(
      route`/wiki/api/v2/pages/${page.id}/labels`
    );
    const labelData = await labelRes.json();
    labels = labelData.results?.map(l => l.name) || [];
  } catch (e) { /* no labels */ }

  return {
    id: page.id,
    title: page.title,
    content: page.body?.storage?.value || '',
    status: page.status,
    version: page.version?.number,
    governance,
    labels,
  };
}

// === CREATE PAGE ===

export async function createPage(payload) {
  const { spaceKey, title, content, parentPageId, labels, governanceMetadata } = payload;

  const spaceRes = await api.asUser().requestConfluence(
    route`/wiki/api/v2/spaces?keys=${spaceKey}`
  );
  const spaceData = await spaceRes.json();
  const spaceId = spaceData.results?.[0]?.id;
  if (!spaceId) return { error: `Space ${spaceKey} not found` };

  const body = {
    spaceId, title, status: 'current',
    body: { representation: 'storage', value: content },
  };
  if (parentPageId) body.parentId = parentPageId;

  const res = await api.asUser().requestConfluence(route`/wiki/api/v2/pages`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  const page = await res.json();

  if (governanceMetadata) {
    await setGovernanceProperty(page.id, JSON.parse(governanceMetadata));
  }

  if (labels) {
    for (const label of labels.split(',').map(l => l.trim())) {
      await api.asUser().requestConfluence(
        route`/wiki/api/v2/pages/${page.id}/labels`,
        { method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name: label }) }
      );
    }
  }

  return {
    id: page.id, title: page.title,
    url: `${page._links?.base || ''}${page._links?.webui || ''}`,
  };
}

// === UPDATE PAGE ===

export async function updatePage(payload) {
  const { pageId, content, versionMessage, governanceMetadata } = payload;

  const currentRes = await api.asUser().requestConfluence(
    route`/wiki/api/v2/pages/${pageId}`
  );
  const current = await currentRes.json();

  const res = await api.asUser().requestConfluence(
    route`/wiki/api/v2/pages/${pageId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        id: pageId, status: 'current', title: current.title,
        body: { representation: 'storage', value: content },
        version: { number: current.version.number + 1, message: versionMessage },
      }),
    }
  );
  const updated = await res.json();

  if (governanceMetadata) {
    await setGovernanceProperty(pageId, JSON.parse(governanceMetadata));
  }

  return { id: updated.id, version: updated.version?.number, message: versionMessage };
}

// === COMMENTS ===

export async function readComments(payload) {
  const { pageId } = payload;
  const res = await api.asUser().requestConfluence(
    route`/wiki/api/v2/pages/${pageId}/footer-comments?body-format=storage`
  );
  const data = await res.json();
  return {
    comments: (data.results || []).map(c => ({
      id: c.id, author: c.version?.authorId,
      body: c.body?.storage?.value || '', created: c.version?.createdAt,
    })),
    count: data.results?.length || 0,
  };
}

export async function addComment(payload) {
  const { pageId, comment } = payload;
  const res = await api.asUser().requestConfluence(
    route`/wiki/api/v2/pages/${pageId}/footer-comments`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ body: { representation: 'storage', value: comment } }),
    }
  );
  const created = await res.json();
  return { id: created.id, created: true };
}

// === HELPERS ===

async function setGovernanceProperty(pageId, value) {
  const existing = await api.asUser().requestConfluence(
    route`/wiki/api/v2/pages/${pageId}/properties?key=rai-governance`
  );
  const existingData = await existing.json();
  const prop = existingData.results?.[0];

  const payload = { key: 'rai-governance', value };
  if (prop) {
    await api.asUser().requestConfluence(
      route`/wiki/api/v2/pages/${pageId}/properties/${prop.id}`,
      { method: 'PUT', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload) }
    );
  } else {
    await api.asUser().requestConfluence(
      route`/wiki/api/v2/pages/${pageId}/properties`,
      { method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload) }
    );
  }
}
```

### src/actions/jira.js

```javascript
import api, { route } from '@forge/api';

export async function readJiraContext(payload) {
  const { issueKey } = payload;

  const res = await api.asUser().requestJira(
    route`/rest/api/3/issue/${issueKey}?fields=summary,status,issuetype,assignee,reporter,parent,priority,labels,description&expand=names`
  );
  const issue = await res.json();

  // Remote links (Confluence pages)
  let linkedPages = [];
  try {
    const linksRes = await api.asUser().requestJira(
      route`/rest/api/3/issue/${issueKey}/remotelink`
    );
    const links = await linksRes.json();
    linkedPages = links
      .filter(l => l.object?.url?.includes('/wiki/'))
      .map(l => ({ title: l.object?.title, url: l.object?.url }));
  } catch (e) { /* no links */ }

  // Parent epic
  let epicContext = null;
  const parentKey = issue.fields?.parent?.key;
  if (parentKey) {
    try {
      const epicRes = await api.asUser().requestJira(
        route`/rest/api/3/issue/${parentKey}?fields=summary,status,description`
      );
      const epic = await epicRes.json();
      epicContext = {
        key: parentKey,
        summary: epic.fields?.summary,
        status: epic.fields?.status?.name,
      };
    } catch (e) { /* no parent */ }
  }

  return {
    key: issueKey,
    summary: issue.fields?.summary,
    status: issue.fields?.status?.name,
    statusCategory: issue.fields?.status?.statusCategory?.key,
    type: issue.fields?.issuetype?.name,
    assignee: issue.fields?.assignee?.displayName,
    reporter: issue.fields?.reporter?.displayName,
    labels: issue.fields?.labels || [],
    description: issue.fields?.description,
    epic: epicContext,
    linkedPages,
  };
}

export async function transitionIssue(payload) {
  const { issueKey, transitionName } = payload;

  const transRes = await api.asUser().requestJira(
    route`/rest/api/3/issue/${issueKey}/transitions`
  );
  const transData = await transRes.json();
  const transition = transData.transitions?.find(
    t => t.name.toLowerCase() === transitionName.toLowerCase()
  );

  if (!transition) {
    const available = transData.transitions?.map(t => t.name).join(', ');
    return { error: `"${transitionName}" not found. Available: ${available}` };
  }

  await api.asUser().requestJira(
    route`/rest/api/3/issue/${issueKey}/transitions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ transition: { id: transition.id } }),
    }
  );

  return { transitioned: true, to: transitionName, issueKey };
}
```

### src/actions/raise.js

```javascript
import api from '@forge/api';

const BACKEND_URL = process.env.RAISE_BACKEND_URL || 'https://raise-api.humansys.ai';
const API_KEY = process.env.RAISE_API_KEY || '';

async function callBackend(method, path, body = null) {
  const options = {
    method,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${API_KEY}`,
    },
  };
  if (body) options.body = JSON.stringify(body);

  const res = await api.fetch(`${BACKEND_URL}${path}`, options);
  if (!res.ok) {
    return { error: `Backend ${res.status}`, details: await res.text() };
  }
  return await res.json();
}

// === Graph Sync ===
// POST /api/v1/graph/sync — idempotent upsert of nodes + edges

export async function graphSync(payload) {
  const { projectId, nodes, edges } = payload;

  return await callBackend('POST', '/api/v1/graph/sync', {
    project_id: projectId,
    nodes: JSON.parse(nodes),
    edges: edges ? JSON.parse(edges) : [],
  });
}

// === Graph Query ===
// GET /api/v1/graph/query — GIN full-text keyword search

export async function graphQuery(payload) {
  const { query, limit } = payload;

  const params = new URLSearchParams({ q: query });
  if (limit) params.set('limit', String(limit));

  return await callBackend('GET', `/api/v1/graph/query?${params}`);
}

// === Agent Telemetry ===
// POST /api/v1/agent/events — report agent action

export async function reportEvent(payload) {
  const { agentId, eventType, payload: eventPayload } = payload;

  return await callBackend('POST', '/api/v1/agent/events', {
    agent_id: agentId,
    event_type: eventType,
    payload: eventPayload ? JSON.parse(eventPayload) : {},
  });
}

// === Memory Patterns ===
// POST /api/v1/memory/patterns — share learned pattern

export async function sharePattern(payload) {
  const { content, context, patternType } = payload;

  return await callBackend('POST', '/api/v1/memory/patterns', {
    content,
    context: context || '',
    pattern_type: patternType || 'governance',
    source: 'rovo-agent',
  });
}
```

### src/actions/state.js

```javascript
import { storage } from '@forge/api';

export async function saveDraft(payload) {
  const { draftId, state } = payload;
  await storage.set(`draft:${draftId}`, {
    data: JSON.parse(state),
    updatedAt: new Date().toISOString(),
  });
  return { saved: true, draftId };
}

export async function loadDraft(payload) {
  const { draftId } = payload;
  const data = await storage.get(`draft:${draftId}`);
  if (!data) return { found: false, draftId };
  return { found: true, ...data };
}
```

---

## 5. Prompts

### static/prompts/rai-governance.txt

```text
You are Rai, a governance skill execution engine for Lean Portfolio
Management (SAFe). You operate inside Confluence and Jira.

## How You Work

You do NOT have governance knowledge built-in. All governance rules,
templates, and processes come from SKILL PAGES in Confluence. You are
an execution engine — you read skills and follow them.

Your deterministic backbone is the RaiSE Knowledge Graph. When you
need to check what exists, search for related documents, or find
constraints, you query the graph via graph-query. Graph results are
FACTS, not opinions. Present them as such.

## Identity
- Direct, honest, no praise
- Distinguish between your interpretation (LLM, fallible) and
  graph results (deterministic, verifiable)
- Say "The knowledge graph shows..." for graph query results
- Say "I think..." or "Based on the text..." for interpretation
- Say "I don't know" when you don't

## Context Detection (EVERY conversation start)

1. If user mentions a Jira issue key:
   → read-jira-context to load full context
   → Note: type, status, assignee, epic, linked pages

2. If you have a page context:
   → read-confluence-page to load content + governance metadata
   → read-page-comments for pending feedback

3. Determine MODE:

   CREATE — No document exists or page is empty/template
   → Find the matching skill page (find-skill-page)
   → Follow skill's Process section step by step
   → Create document, sync to graph (graph-sync)

   ELABORATE — Document draft, user is working on it
   → Read current document + skill for reference
   → Help fill sections, improve content
   → Update page with version messages
   → Re-sync after significant changes (graph-sync)

   REVIEW — Document in review, or user asks to review
   → Read document
   → graph-query to find related docs, ADRs, standards
   → Analyze coverage using graph results + document content
   → Present findings: ✅ ⚠️ ❌
   → Add comments if reviewer agrees

   REFINE — Unresolved comments exist
   → read-page-comments, show grouped by section
   → Work through each, update page
   → Re-sync after changes

   VALIDATE — User asks for explicit validation
   → graph-query for related governance docs
   → Report: gaps, conflicts, coverage, traceability

4. Tell user your mode and why.

## Executing a Skill

When you need to execute a governance skill:

1. find-skill-page("{skill name}")
2. Parse the skill page:
   - Inputs: what data to gather and from where
   - Process: steps to follow (in order)
   - Outputs: what artifacts to create
   - Validation Rules: what must be true when done
   - Graph Relations: what to index
3. Follow the Process section step by step
4. For each Output:
   - Create or update the Confluence page
   - Set governance metadata (content property)
   - Add labels
   - Use version message: "Rai: {what was done}"
5. Sync to knowledge graph:
   - graph-sync with nodes and edges from skill's Graph Relations
6. Report action:
   - report-event with what was done
7. Validate:
   - Check each Validation Rule
   - Report status to user

## Graph Operations

### After creating/updating a document:
→ graph-sync: send parsed nodes and edges to backend
   Include relations from the skill's "Graph Relations" section

### When reviewing:
→ graph-query: search for related ADRs, standards, patterns
   Combine graph results with document analysis to find gaps

### When user asks about dependencies:
→ graph-query: "what documents relate to this topic?"

## Version Messages
ALWAYS descriptive:
- "Rai: Initial {docType} from {source}"
- "Rai: Added {section} per {user}"
- "Rai: Addressed review comments from {reviewer}"

## Content Properties (rai-governance)
Maintain on every governance document:
{
  "documentType": "problem-scope|lbc|adr|standard",
  "workflowStep": "draft|review|revision-N|approved",
  "createdBy": "rai",
  "lastAgentAction": "created|updated|reviewed",
  "jiraIssueKey": "PROJ-123",
  "graphProjectId": "{project-id}"
}

## Boundaries
- You don't remember previous conversations
  → Always read page + metadata first
- Graph results are deterministic
  → Present as facts, not opinions
- You don't create Jira structure
  → Jira Automation does that
- You operate AS the user
  → Respect their permissions
- Confirm before destructive actions
  → "Move PROJ-45 to In Review?"
```

### static/prompts/rai-dev.txt

```text
You are Rai Dev, a development copilot that ensures code complies
with organizational governance.

## How You Work

Before generating or reviewing code, you query the RaiSE Knowledge
Graph for constraints that MUST be followed. These constraints come
from governance documents (ADRs, standards, patterns) created and
approved by the governance team.

Graph results are MANDATORY — they are organizational decisions,
not suggestions.

## At Conversation Start

1. read-jira-context for the current story/issue
2. Identify the module/concept being worked on
3. graph-query for related ADRs, standards, patterns

4. Present constraints before any code:
   "Before we start, these governance constraints apply:
    📋 ADR-003 (mandatory): OAuth2 with JWT
    📋 STD-SEC-01: OWASP Top 10 compliance
    📋 From LBC: 50K concurrent users capacity"

## While Working

- If code would violate a constraint → STOP
  "⛔ This implementation uses session-based auth, but ADR-003
   requires OAuth2 with JWT. Should I refactor, or do you want
   to challenge the ADR?"

- If no constraint exists for a decision → flag it
  "No ADR exists for the caching strategy. Consider creating
   one before implementing."

## Constraints Are Not Optional

These come from approved governance documents. If a developer
disagrees, the right path is to challenge the ADR through the
governance process, not to ignore it in code.

## Identity
- Direct, factual
- "ADR-003 requires..." not "I suggest..."
- Always cite the source document
- Distinguish: graph facts vs. your suggestions
```

---

## 6. Plan de Implementación

### Fase 0: Content Setup (Emilio, 1-2 días)
- [ ] Create Confluence space "Governance Hub" with folder structure
- [ ] Create skill page "Skill: Problem Scope"
- [ ] Create skill page "Skill: Lean Business Case"
- [ ] Create Jira project with workflow (To Do → In Progress → In Review → Done)
- [ ] Setup Jira Automation (intake → epic + stories + pages)
- [ ] Deploy backend via Docker Compose + ngrok for dev access

### Fase 1: Forge Actions — Confluence + Jira (Fernando, 2-3 días)
- [ ] `forge create` + dev environment + install on test site
- [ ] Implement Confluence actions (read, create, update, comments, findSkill)
- [ ] Implement Jira actions (readContext, transition)
- [ ] Implement Forge Storage actions (save/load draft)
- [ ] Implement `rai-governance` prompt
- [ ] **Gate: Rai reads skill page, creates document, updates with version messages**

### Fase 2: Backend Integration (Fernando, 1-2 días)
- [ ] Implement `raise.js` actions (graphSync, graphQuery, reportEvent, sharePattern)
- [ ] Configure `RAISE_BACKEND_URL` + `RAISE_API_KEY` env vars
- [ ] **Gate: Create document → graph-sync → graph-query returns indexed result**

### Fase 3: E2E Governance Cycle (Fernando + Emilio, 2-3 días)
- [ ] Full cycle: CREATE → ELABORATE → REVIEW → REFINE → APPROVE
- [ ] Graph sync on every create/update
- [ ] Content properties + version messages + labels working
- [ ] **Gate: Full skeleton conversation (Ana → Rodo → Ana → Dev)**

### Fase 4: Rai Dev Agent (Fernando, 1-2 días)
- [ ] Add `rai-dev` agent to manifest
- [ ] Implement `rai-dev` prompt
- [ ] **Gate: Dev asks for constraints → graph-query returns ADRs + standards**

### Fase 5: Second Document Type (Emilio, 1 día)
- [ ] Verify "Skill: Lean Business Case" page works with existing agent
- [ ] **Gate: Same agent, same actions, new doc type — ZERO code change**
- [ ] THIS is the killer demo: "New governance process = new Confluence page"

### Timeline

| Phase | Owner | Est. | Target |
|-------|-------|------|--------|
| 0 | Emilio | 1-2d | Feb 27 |
| 1 | Fernando | 2-3d | Mar 1 |
| 2 | Fernando | 1-2d | Mar 2 |
| 3 | Fernando + Emilio | 2-3d | Mar 4 (Coppel demo) |
| 4 | Fernando | 1-2d | Mar 7 |
| 5 | Emilio | 1d | Mar 8 |

**Coppel demo (Mar 4):** Phases 0-3 = Rovo Agent creating governance docs + graph integration.
**Atlassian webinar (Mar 14):** + Phase 4-5 = Rai Dev + zero-code extensibility.

---

## 7. FREE vs PRO

```
RaiSE FREE (rai-cli):
├── Knowledge graph LOCAL (rai graph build, per-repo)
├── Skills in SKILL.md (local, per-repo)
├── Patterns in patterns.jsonl (local)
├── One dev, one repo, one machine
├── No Atlassian integration
└── Value: AI copilot with local memory

RaiSE PRO (rai-cli + Forge + Backend):
├── Knowledge graph CENTRALIZED (RaiSE backend, deterministic)
├── Skills in Confluence (governance team edits, no code)
├── Governance → Dev loop (ADRs → code constraints)
├── Multi-team, multi-repo, multi-role
├── Trazabilidad end-to-end (strategy → code)
├── Deterministic validation (not RAG, not probabilistic)
├── Atlassian native (Jira + Confluence + Rovo)
└── Value: organizational governance with deterministic AI

Differentiator vs Teamwork Graph:
  Teamwork Graph: "here are some pages that might be relevant"
  RaiSE Graph:    "ADR-003 governs mod-auth, which traces to
                   LBC-X, which implements Strategic Theme Y.
                   Changing ADR-003 impacts 3 modules."
```
