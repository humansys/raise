# RaiSE PRO — MVP Product Definition

> Version: 0.1 (draft)
> Date: 2026-03-20
> Author: Emilio + Rai
> Target: April 16, 2026
> Status: Draft — pending HITL review

---

## 1. Vision

Rai PRO es el copiloto omnisciente del equipo de desarrollo. Conoce todo sobre sus entornos, gobierno, backlog y documentacion. Conecta fuentes via adaptadores universales y usa una memoria en grafo neurosimbolico para respuestas deterministas y verificables.

**Thesis**: La guerra no es contra la alucinacion. Es contra el derroche del token. RaiSE PRO resuelve esto con contexto minimo viable — deterministico, curado, preciso.

**Triada**: Metodo (RaiSE) + Agente (Rai) + Humano — trabajando juntos hacia software confiable. Cada developer lidera su triada.

---

## 2. Product Suite (Vision Completa)

| Componente | Tipo | Descripcion | Estado |
|---|---|---|---|
| **raise-cli** | OSS package (pip) | Framework base: graph, session, patterns, gates, skills, discover | Estable |
| **raise-pro** | Commercial plugin (pip) | Adaptadores (Jira, Confluence, GitLab, Odoo), doctor checks, license gating | Parcial |
| **raise-server** | SaaS API | Graph hosting, tenant management, governance centralizada, metricas | No existe |
| **raise-forge** | Atlassian Forge app | Rovo Agent + actions, Jira/Confluence integration nativa | No existe |
| **raise-agent** | AI agent product | Agente autonomo por developer (daemon, Telegram, cron, knowledge pipeline) | En desarrollo |

---

## 3. MVP Scope (April 16)

### Que es MVP

El minimo necesario para que:
1. Un attendee del webinar pueda iniciar un trial
2. El trial demuestre valor tangible en su Jira/Confluence
3. Kurigage (20 personas, stack legacy PHP/Symfony/.NET) lo use en produccion

### Que NO es MVP

- Cross-repo graph merge/deduplication automatica (V2)
- Cross-repo relationship discovery automatica (V2)
- raise-agent como producto licenciado (V2)
- License server con phone-home (V2)
- Neo4j / graph database avanzado (V2)
- Governance centralizada en server (V2)
- Rovo Dev MCP integration (V2 — buen path pero no critico para webinar)

---

## 4. MVP Components

### 4.1 raise-server (Minimal)

**Owner**: Emilio
**Esfuerzo**: 1-2 semanas

API read-only para servir graph data a todos los clientes (Forge, CLI, Rovo Dev).

**Endpoints**:

```
POST   /api/v1/graphs/{tenant}/{repo}              # Push graph data per repo
GET    /api/v1/graphs/{tenant}/query                # Cross-repo: busca en TODOS los repos del tenant
GET    /api/v1/graphs/{tenant}/{repo}/query          # Single-repo: busca en un repo especifico
GET    /api/v1/graphs/{tenant}/{repo}/nodes/{id}     # Nodo individual
GET    /api/v1/graphs/{tenant}/{repo}/context/{id}   # Contexto de modulo (nodo + relaciones)
GET    /api/v1/graphs/{tenant}/repos                 # Lista repos del tenant
GET    /api/v1/health                                # Health check
```

**Cross-repo query (MVP)**: El endpoint `/{tenant}/query` busca en todos los graphs del tenant y retorna resultados con su `repo` de origen. No hace merge ni deduplication — es busqueda federada simple. Cada repo mantiene su graph independiente.

**Stack**: FastAPI + PostgreSQL (o SQLite para v0) + API key auth per tenant.

**Deploy**: Fly.io o Railway (simplicidad, bajo costo, deploy rapido).

**Reutiliza**: GraphNode/GraphEdge Pydantic models, logica de query de `rai graph query`.

**CLI integration**: Nuevo comando `rai graph push` que sube el graph local al server. Detecta repo name automaticamente (git remote o manifest).

### 4.2 raise-forge (Atlassian Forge App)

**Owner**: Fernando + Aquiles
**Esfuerzo**: 2-3 semanas

Forge app con Rovo Agent que consulta raise-server para dar contexto de governance y codebase.

**Modules**:

```yaml
modules:
  rovo:agent:
    - key: raise-governance-agent
      name: "RaiSE Governance"
      prompt: |
        You are RaiSE, an AI governance partner for software teams.
        You have access to the team's knowledge graph which contains
        their codebase structure, architectural decisions, patterns,
        and governance rules. Use the queryGraph action to find
        relevant context before answering questions.
      conversationStarters:
        - "What's the architecture of this project?"
        - "Show me recent patterns and decisions"
        - "What are the governance gates for this story?"
        - "Explain the dependency structure"
      actions:
        - actionVerb: queryGraph
          function: query-graph
        - actionVerb: getModuleContext
          function: get-module-context
        - actionVerb: getProjectStatus
          function: get-project-status

  action:
    - key: query-graph
      function: queryGraphHandler
      description: "Search the project knowledge graph for architecture, patterns, decisions"
      inputParameters:
        query:
          type: string
          description: "Search query"
        strategy:
          type: string
          description: "keyword_search or concept_lookup"

    - key: get-module-context
      function: getModuleContextHandler
      description: "Get full context for a specific module including relationships"
      inputParameters:
        moduleId:
          type: string
          description: "Module identifier (e.g., mod-memory, mod-cli)"

    - key: get-project-status
      function: getProjectStatusHandler
      description: "Get current project status from Jira"
```

**Forge Remote**: Llama a raise-server API con API key del tenant.

**Storage**: Forge KVS para cache de configuracion (tenant API key, server URL).

**Distribucion**: Private listing via distribution links para beta. Trial de 30 dias built-in de Marketplace cuando sea publico.

**Constraint critico**: Forge LLM API esta en EAP — no se puede usar para Marketplace listing. El Rovo Agent usa AI de Atlassian internamente (no afecta), pero si necesitamos LLM custom, debe ser via raise-server.

### 4.3 raise-pro CLI (License + Distribution)

**Owner**: Emilio
**Esfuerzo**: 3-5 dias

Distribucion del package Python con activacion de licencia.

**Modelo** (inspirado en Nx Powerpack):

```bash
# Instalacion (GitLab Package Registry con deploy token)
uv pip install raise-pro --extra-index-url https://__token__:${RAISE_PRO_TOKEN}@gitlab.com/api/v4/projects/<id>/packages/pypi/simple

# Activacion
rai activate LICENSE_KEY

# Verificacion
rai doctor --check license
```

**License file**: JWT firmado (EdDSA) en `~/.raise/license.key`

```json
{
  "sub": "org-kurigage",
  "plan": "pro-trial",
  "features": ["jira", "confluence", "governance-agent"],
  "exp": 1747612800,
  "iat": 1713052800,
  "iss": "raise.humansys.ai"
}
```

**Validacion**: At command invocation time (no at import). Zero overhead para comandos free. Public key embebida en el package.

**Graceful degradation**:

| Estado | Comportamiento |
|---|---|
| Valido | Todas las features pro activas |
| Expira en <30 dias | Warning en stderr, features activas |
| Expirado <7 dias | Warning prominente, features activas |
| Expirado >7 dias | Pro commands muestran "license expired, renew at..." |
| Sin licencia | Pro commands muestran "upgrade to PRO at..." |

**Licencia legal**: FSL 1.1-ALv2 (Functional Source License → Apache 2.0 en 2 anos). Developer-friendly, source-available, usada por Sentry/Codecov.

### 4.4 Trial + Waitlist Flow

**Owner**: Emilio (backend) + rai-gtm (landing page)
**Esfuerzo**: 3-5 dias

**Funnel**:

```
Videos de calentamiento (lunes)
  → Webinar (Apr 16)
    → Attendees reciben invite code exclusivo
      → Landing page raiseframework.ai/pro
        → Sign up (email + org)
          → Trial key generado (JWT, 30 dias)
            → Email con key + instrucciones de instalacion
              → rai activate KEY
                → Trial activo
```

**Waitlist** (para no-attendees):

```
raiseframework.ai/pro
  → Sign up to waitlist (email + org + stack info)
    → Queue con referral queue-jumping
      → Invites por cohort (modelo Linear)
```

**Backend**: CF Worker + D1 (reutiliza ADR-004 existente). Genera JWT trial keys.

**Marketplace**: Forge app tiene trial de 30 dias built-in. No necesita implementacion custom.

---

## 5. Architecture

### 5.1 Core Concept: Pluggable Ontology Registry

El knowledge graph de cada repo no es un solo graph plano — es una **composicion de ontologias plugables**. Cada ontologia es un schema versionado + instances por repo.

**Grounding**: Este modelo esta validado por LinkedIn Knowledge Graph (domain-specific ontologies linked por cross-references), Apollo Federation (subgraphs → supergraph con validacion), Confluent Schema Registry (compatibility checking), OBO Foundry (350+ ontologias interoperables via core minimo), y Palantir Foundry (semantic layer sobre data stores estandar).

```
┌─────────────────────────────────────────────────────────────┐
│                    ONTOLOGY REGISTRY                         │
│                                                              │
│  Built-in schemas:                Custom schemas:            │
│  ┌─────────────────┐             ┌─────────────────┐        │
│  │ code v1.0       │             │ pharmacy v1.0   │        │
│  │ (rai discover)  │             │ (knowledge      │        │
│  ├─────────────────┤             │  extractor)     │        │
│  │ governance v2.1 │             ├─────────────────┤        │
│  │ (RaiSE method)  │             │ php-symfony v1.0│        │
│  └─────────────────┘             │ (curated)       │        │
│                                   └─────────────────┘        │
│  Each schema defines: node types, edge types,                │
│  property constraints, competency questions,                 │
│  compatibility mode (backward/forward/full)                  │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                    SUBSCRIPTIONS                              │
│                                                              │
│  Tenant: org-kurigage                                        │
│  ┌─────────────┬──────────────────────────────────────┐     │
│  │ repo-erp    │ code + governance + pharmacy + php   │     │
│  ├─────────────┼──────────────────────────────────────┤     │
│  │ repo-api    │ code + governance + pharmacy         │     │
│  ├─────────────┼──────────────────────────────────────┤     │
│  │ repo-mobile │ code + governance                    │     │
│  └─────────────┴──────────────────────────────────────┘     │
│                                                              │
│  On subscribe: Apollo-style composition validation           │
│  (no type collisions, cross-refs resolve, compatible)        │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                    INSTANCE DATA                             │
│                                                              │
│  repo-erp/code:       {ModuleAuth, ModuleInventory, ...}    │
│  repo-erp/governance: {ADR-001, Pattern-012, Gate-tests}    │
│  repo-erp/pharmacy:   {DrugCatalog, Prescription, ...}      │
│  repo-erp/php:        {SymfonyBundle, DoctrineEntity, ...}  │
│                                                              │
│  Cross-repo query: busca en todas las instances del tenant   │
│  Cross-ontology: type_mappings resuelven conceptos comunes   │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 Layered Architecture

```
┌───────────────────────────────────────────────────────────┐
│  LAYER 6: CONSUMERS                                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │Forge App │  │CLI (rai) │  │Rovo Dev  │  │Future:   │  │
│  │(Rovo     │  │graph push│  │(MCP      │  │IDE, CI,  │  │
│  │ Agent)   │  │query     │  │ server)  │  │webhooks  │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  │
├───────┼──────────────┼──────────────┼──────────────┼───────┤
│  LAYER 5: QUERY + AI GROUNDING                             │
│  - Keyword search, concept lookup across ontologies         │
│  - Cross-repo federated query                               │
│  - LLM context assembly (graph → minimum viable context)    │
│  - Rule-based inference (application-layer, V2)             │
├────────────────────────────────────────────────────────────┤
│  LAYER 4: COMPOSITION ENGINE                                │
│  - Apollo-style: merge subscribed schemas → composed view   │
│  - Confluent-style: compatibility check on version upgrade  │
│  - Buf-style: breaking changes require explicit approval    │
│  - Reserved identifiers (deleted types can't be reused)     │
├────────────────────────────────────────────────────────────┤
│  LAYER 3: ONTOLOGY MODULES                                  │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐  │
│  │  code    │ │governance│ │ domain   │ │  technology  │  │
│  │ (built-  │ │ (built-  │ │ (custom, │ │  (custom,    │  │
│  │  in)     │ │  in)     │ │extracted)│ │  curated)    │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────┘  │
├────────────────────────────────────────────────────────────┤
│  LAYER 2: META-SCHEMA (Core Ontology)                       │
│  - Root types: Entity, Relation, Attribute (PERA-inspired)  │
│  - Module descriptor: id, version, deps, compatibility      │
│  - Annotation vocabulary: confidence, provenance, source    │
│  - Dumb-Down principle: any data readable with only core    │
├────────────────────────────────────────────────────────────┤
│  LAYER 1: STORAGE                                           │
│  - PostgreSQL (JSONB + indexes)                             │
│  - Schema: ontology registry + subscriptions + instances    │
│  - Future: + vector index for semantic search               │
│  - Future: + graph DB read replica if traversals bottleneck │
└────────────────────────────────────────────────────────────┘
```

### 5.3 System Diagram

```
  Developer workstation              raise-server (SaaS)              Atlassian Cloud
  ──────────────────────             ──────────────────               ─────────────────
                                     FastAPI + PostgreSQL
  repo-a/                                    │
    rai discover ──→ code graph              │
    rai graph build ──→ local graph          │
    rai graph push ─────────────────→ POST /graphs/{tenant}/{repo}
                                             │
  repo-b/                                    │
    rai graph push ─────────────────→ POST /graphs/{tenant}/{repo}
                                             │
  repo-c/                                    │
    rai graph push ─────────────────→ POST /graphs/{tenant}/{repo}
                                             │
                                     ┌───────┴────────┐
                                     │ Ontology        │
                                     │ Registry        │
                                     │ ┌────────────┐  │
                                     │ │code v1.0   │  │
                                     │ │govern v2.1 │  │
                                     │ │pharmacy v1 │  │
                                     │ └────────────┘  │
                                     │                  │
                                     │ Composed views   │
                                     │ per repo         │
                                     └───────┬──────────┘
                                             │
                              ┌──────────────┼──────────────┐
                              │              │              │
                    GET /query?q=...   GET /query?q=...    │
                              │              │              │
                         raise-pro      Rovo Agent     Rovo Dev
                         (CLI)          (Forge app)    (MCP)
                              │              │              │
                              └──────┬───────┘              │
                                     │                      │
                               Developer (triada)           │
                               Jira / Confluence ───────────┘
```

### 5.4 Moat Strategy

**Leccion de Palantir**: El moat NO es el storage engine. Es el modelo semantico + el SDK + el flywheel.

| Capa de moat | Que es | Por que es dificil de replicar |
|---|---|---|
| **Ontology modules pre-built** | code, governance, technology patterns | Curados, validados, con competency questions. Como MODL pero para software |
| **Knowledge extractor** | Pipeline LLM que extrae ontologias de corpus | Domain-agnostic, HITL curation, mejora con cada extraccion |
| **AI grounding** | Graph como contexto para LLM features | Determinista, verificable, 97% token savings vs context dump |
| **Cross-tenant insights** | Patterns anonimizados del aggregate de graphs | Network effect: mas tenants → mejores patterns → mas valor |
| **Integration ecosystem** | Forge, CLI, MCP, IDE, CI | Cada integracion es un switching cost |

**Formato abierto**: Schemas exportables (JSON). El moat no esta en atrapar los datos — esta en lo que se puede HACER con ellos.

### 5.5 Design Principles (from research)

1. **Thin Core Ontology** (BFO pattern) — minimal root types que todas las ontologias extienden
2. **Orthogonality** (OBO Foundry) — cada concepto tiene UNA definicion canonica, namespace-qualified
3. **Compatibility Checking** (Confluent) — BACKWARD_TRANSITIVE por default al actualizar schemas
4. **Build-time Composition** (Apollo Federation) — validar al suscribirse, no al queryar
5. **Dumb-Down Principle** (Dublin Core) — cualquier dato legible con solo el core schema
6. **Ontology is Application-Layer** (Palantir) — PostgreSQL para storage, Pydantic para schemas, Python para composicion

---

## 6. Team + Timeline

### People

| Persona | Workstream | Disponibilidad |
|---|---|---|
| **Emilio + Rai** | raise-server + raise-pro CLI + trial backend + architecture | Full-time |
| **Fernando** | raise-forge (Forge app + Rovo Agent) | Disponible, necesita epicas prescriptivas |
| **Aquiles** | raise-forge (Forge app + Rovo Agent) | Disponible, necesita epicas prescriptivas |

### Timeline (27 dias)

```
Semana 1 (Mar 21-27): Foundation
  Emilio: raise-server scaffold + graph push + deploy
  Fernando+Aquiles: Forge app scaffold + Rovo Agent hello world
  GTM: Videos de calentamiento (empieza lunes)

Semana 2 (Mar 28 - Apr 3): Core
  Emilio: raise-server query API + trial/license endpoints
  Fernando+Aquiles: Forge actions (query graph, module context)
  GTM: Mas videos, landing page pro

Semana 3 (Apr 4-10): Integration
  Emilio: rai activate + rai graph push + license validation
  Fernando+Aquiles: Forge → raise-server integration, Jira panels
  GTM: Waitlist backend, webinar prep

Semana 4 (Apr 11-16): Polish + Launch
  Todos: Integration testing, bug fixes, demo rehearsal
  GTM: Webinar final prep
  Apr 16: WEBINAR + LAUNCH
```

---

## 7. Pricing Model (Draft)

Inspirado en GitLab + Nx + Sidekiq.

| Tier | Target | Precio | Incluye |
|---|---|---|---|
| **Community** | OSS, individual devs | Gratis | raise-cli completo, graph local, skills, discover |
| **Pro** | Equipos (5-50 devs) | $X/user/mes (TBD) | Adaptadores (Jira, Confluence, etc.), raise-forge agent, raise-server graph hosting, trial 30 dias |
| **Enterprise** | Organizaciones (50+ devs) | Custom | Multi-repo graph, RBAC, SSO, managed inference, SLA, evals — H2 2026 |

**Marketplace**: Forge app con App Editions (Standard = Pro, Advanced = Enterprise). Trial de 30 dias built-in.

**CLI**: Per-seat annual subscription. Trial key de 30 dias (JWT).

**Incentivo Atlassian**: 0% revenue share en primer $1M lifetime para pure Forge apps.

---

## 8. Licensing

| Componente | Licencia |
|---|---|
| raise-cli | MIT (open source) |
| raise-pro | FSL 1.1-ALv2 (source-available, → Apache 2.0 en 2 anos) |
| raise-server | FSL 1.1-ALv2 o propietaria |
| raise-forge | Propietaria (Marketplace app) |

**Por que FSL 1.1**: Usada por Sentry, Codecov, Liquibase. Developer-friendly (source visible), protege contra competencia directa, convierte a Apache 2.0 en 2 anos. Disenada por Armin Ronacher (creador de Flask).

---

## 9. Risks + Mitigations

| Riesgo | Impacto | Mitigacion |
|---|---|---|
| raise-server no listo a tiempo | Alto — Forge app sin backend | Scope minimo: read-only graph API, SQLite, deploy en Railway |
| Forge LLM API en EAP | Medio — no podemos usar inference custom en Forge | Rovo Agent usa AI de Atlassian (no afecta MVP). Custom inference via raise-server si se necesita |
| Fernando/Aquiles sin experiencia en diseño | Medio — dependencia en Emilio para decisions | Epicas ultra-prescriptivas con mocks, contracts, tests definidos |
| 27 dias para 4 workstreams | Alto — scope creep | Triage agresivo: lo que no esta aqui es V2 |
| Forge app review toma 5-10 dias | Medio — puede no estar lista para Apr 16 | Distribuir via distribution links (beta privado), Marketplace listing en paralelo |
| Trial key management manual | Bajo — no escala | Aceptable para beta. Automatizar en V2 |

---

## 10. Success Criteria (Apr 16)

- [ ] Webinar ejecutado con asistentes reales
- [ ] Al menos 1 attendee activa trial de raise-pro CLI
- [ ] Al menos 1 attendee instala Forge app (beta)
- [ ] Kurigage usando raise-pro en al menos 1 repo
- [ ] raise-server desplegado y sirviendo graph queries
- [ ] Landing page raiseframework.ai/pro live con waitlist
- [ ] FSL 1.1-ALv2 license headers en raise-pro

---

## 11. Open Questions

1. **Pricing**: Que precio por usuario/mes para Pro? Benchmarks: Nx Powerpack (~$15-20/dev/mo), GitLab Premium ($29/user/mo), Sidekiq Pro ($995/org/yr)
2. **Forge + raise-server auth**: Como conecta un admin de Jira su org con su tenant en raise-server? Onboarding flow pendiente
3. **Graph push frequency**: Manual via `rai graph push`? Post-commit hook? CI pipeline?
4. **Kurigage stack support**: Graph discover funciona con PHP/Symfony? Necesita validacion
5. **Atlassian funding**: Confirmar alcance del fondeo — es solo pauta o hay co-investment?
6. **Video content**: Quien los produce? Que formato? (demo, talking head, animated?)
7. **Webinar format**: Duracion, agenda, speakers, demo live vs grabado?

---

## 12. Evidence Base

Este document se basa en research de 10 agentes (2026-03-20):

### Round 1: Licensing + Distribution
1. **Licensing models del mercado**: GitLab, JetBrains, HashiCorp, Elastic, Sidekiq, PostHog, Temporal, Redis, Nx
2. **Implementacion tecnica**: Keygen.sh, LicenseSpring, Cryptolens, JWT custom, GitLab Package Registry, entry point gating

### Round 2: Atlassian + GTM
3. **Atlassian Forge platform**: Runtime (Node.js serverless), modules, constraints (25s sync, 512MB), pricing
4. **Rovo AI agents + SDK**: Agent builder, knowledge connectors, no persistent memory, MCP extensibility
5. **Trial/waitlist/beta patterns**: Linear, Cursor, Nx Powerpack, GitHub Copilot, Marketplace built-in 30-day trial
6. **Atlassian partner programs**: $1M at 0% revenue share (pure Forge), Ventures ($1-5M Seed-B), review 5-10 days
7. **raise-gtm exploration**: E8 PRO scope (draft), positioning doc, Kurigage data, waitlist ADR-004, no webinar plan exists

### Round 3: Knowledge Graph Architecture (structural decision)
8. **SOTA Knowledge Graphs**: Google KG, LinkedIn KG, Sourcegraph SCIP, Backstage catalog, Cursor indexing. Gap: nadie combina CODE + DOMAIN + GOVERNANCE
9. **TypeDB + Palantir deep dive**: TypeDB (schema-first pero sin multi-ontology), Palantir (ontology = application layer, no DB feature). Moat = semantic model + SDK + flywheel
10. **Ontology modularization patterns**: OWL imports, OBO Foundry orthogonality, FIBO modular hierarchy, Schema.org extensions, Confluent compatibility, Apollo Federation composition, concrete PostgreSQL schema proposal

Full research outputs archived in session transcripts.

---

## 13. Next Steps

1. **HITL review** de este document — Emilio valida scope y prioridades
2. **Crear epicas** para cada workstream:
   - E-server: raise-server minimal
   - E-forge: raise-forge Atlassian app
   - E-license: raise-pro licensing + distribution
   - E-trial: trial flow + waitlist
3. **Disenar epicas para Fernando/Aquiles** — prescriptivas, con contracts y mocks
4. **Kickoff lunes** — videos de calentamiento + arranque de development
