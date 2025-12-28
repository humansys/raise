# RaiSE Golden Data Framework
## Arquitectura Documental para Diseño Asistido por Agentes

**Versión:** 1.0.0  
**Fecha:** 26 de Diciembre, 2025  
**Propósito:** Definir la estructura documental óptima para que agentes de IA asistan consistentemente en el diseño y desarrollo de RaiSE.

---

## 1. Principios de Diseño del Corpus

### 1.1 Filosofía: "Context is King"

Los agentes de IA operan como **"mentes sin memoria persistente"**. Cada sesión comienza desde cero. Por tanto, el corpus debe:

1. **Ser auto-contenido**: Cada documento debe tener suficiente contexto para ser útil de forma aislada
2. **Ser interconectado**: Referencias cruzadas claras entre documentos
3. **Evitar redundancia**: Un concepto vive en UN lugar (DRY para documentación)
4. **Optimizar para tokens**: Densidad de información alta, palabrería baja
5. **Ser versionado**: Cambios rastreables, estado actual claro

### 1.2 Estructura de Capas

```
┌─────────────────────────────────────────────────────────────┐
│                    CAPA 0: CONSTITUTION                      │
│  (Principios inmutables - raramente cambia)                 │
├─────────────────────────────────────────────────────────────┤
│                    CAPA 1: VISION                           │
│  (Qué construimos y por qué - cambia con pivotes)           │
├─────────────────────────────────────────────────────────────┤
│                    CAPA 2: ARCHITECTURE                     │
│  (Cómo lo construimos - evoluciona con decisiones)          │
├─────────────────────────────────────────────────────────────┤
│                    CAPA 3: DOMAIN                           │
│  (Conocimiento del problema - crece continuamente)          │
├─────────────────────────────────────────────────────────────┤
│                    CAPA 4: EXECUTION                        │
│  (Estado actual, tareas, progreso - cambia constantemente)  │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Catálogo de Documentos Golden Data

### CAPA 0: CONSTITUTION (1 documento)

#### 📜 `00-CONSTITUTION.md`
**Propósito:** Principios inmutables que gobiernan todas las decisiones.  
**Audiencia:** Todos los agentes, todos los humanos.  
**Frecuencia de cambio:** Casi nunca (requiere proceso formal).  
**Tamaño objetivo:** 500-1000 palabras.

**Contenido requerido:**
```markdown
# RaiSE Constitution

## Identidad
- Qué es RaiSE (una oración)
- Qué NO es RaiSE (anti-patrones explícitos)

## Principios Innegociables
1. [Principio] - [Por qué es inmutable]
2. ...

## Valores de Diseño
- Simplicidad > Completitud
- Composabilidad > Monolitos
- Transparencia > Magia

## Restricciones Absolutas
- Nunca [X]
- Siempre [Y]

## Proceso de Enmienda
- Cómo se modifica este documento
```

---

### CAPA 1: VISION (3-4 documentos)

#### 📄 `01-PRODUCT-VISION.md`
**Propósito:** El "North Star" del producto.  
**Audiencia:** Product decisions, roadmap planning.  
**Frecuencia de cambio:** Trimestral o con pivotes.  
**Tamaño objetivo:** 1500-2500 palabras.

**Contenido requerido:**
```markdown
# RaiSE Product Vision

## Problema Central
[Descripción del dolor que resolvemos, con evidencia]

## Solución Propuesta
[Cómo RaiSE resuelve el problema, diferenciadores clave]

## Propuesta de Valor Única (UVP)
[Una oración que captura por qué elegirnos]

## User Personas
### Persona A: [Nombre]
- Rol, contexto, goals, pain points
- Jobs-to-be-done

### Persona B: [Nombre]
- ...

## Casos de Uso Primarios
1. [Caso de uso] → [Outcome esperado]
2. ...

## Anti-Casos de Uso
- Lo que explícitamente NO hacemos

## Métricas de Éxito
| Métrica | Baseline | Target Y1 | Target Y3 |
|---------|----------|-----------|-----------|

## Competitive Positioning
[Matriz de posicionamiento vs competidores clave]
```

---

#### 📄 `02-BUSINESS-MODEL.md`
**Propósito:** Cómo genera valor y revenue.  
**Audiencia:** Business decisions, pricing, partnerships.  
**Frecuencia de cambio:** Semestral.  
**Tamaño objetivo:** 1000-1500 palabras.

**Contenido requerido:**
```markdown
# RaiSE Business Model

## Modelo: Open Core
[Descripción del modelo elegido y rationale]

## Tiers y Pricing
| Tier | Precio | Features | Target Segment |
|------|--------|----------|----------------|

## Revenue Streams
1. [Stream] - [% esperado]
2. ...

## Cost Structure
- Fixed: [categorías]
- Variable: [categorías]

## Unit Economics (Target)
- CAC: $X
- LTV: $Y
- LTV/CAC: Z

## Go-to-Market Strategy
[Canales, partnerships, community strategy]
```

---

#### 📄 `03-MARKET-CONTEXT.md`
**Propósito:** Landscape competitivo y oportunidades.  
**Audiencia:** Strategy decisions, differentiation.  
**Frecuencia de cambio:** Mensual (mercado dinámico).  
**Tamaño objetivo:** 2000-3000 palabras.

**Contenido requerido:**
```markdown
# RaiSE Market Context

## Tamaño de Mercado
| Segmento | TAM | SAM | SOM |
|----------|-----|-----|-----|

## Tendencias Clave
1. [Tendencia] - [Implicación para RaiSE]
2. ...

## Competitive Landscape
### Categoría: SDD Tools
| Competidor | Fortalezas | Debilidades | Estrategia vs |

### Categoría: AI Coding Assistants
...

### Categoría: AI Governance Platforms
...

## Regulatory Environment
- EU AI Act: [implicaciones]
- [Otras regulaciones]

## Oportunidades Identificadas
1. [Oportunidad] - [Tamaño] - [Timing]

## Amenazas Activas
1. [Amenaza] - [Probabilidad] - [Mitigación]

## Última Actualización
[Fecha] - [Cambios desde versión anterior]
```

---

#### 📄 `04-STAKEHOLDER-MAP.md`
**Propósito:** Quiénes son los actores y sus intereses.  
**Audiencia:** Communication, prioritization.  
**Frecuencia de cambio:** Según cambios organizacionales.  
**Tamaño objetivo:** 500-1000 palabras.

**Contenido requerido:**
```markdown
# RaiSE Stakeholder Map

## Equipo Core
| Rol | Persona | Responsabilidades | Expertise |
|-----|---------|-------------------|-----------|

## Advisors / Mentors
...

## Early Adopters Comprometidos
...

## Partners Potenciales
...

## Comunidad
- Discord/Slack: [URL]
- GitHub Discussions: [URL]
```

---

### CAPA 2: ARCHITECTURE (5-6 documentos)

#### 🏗️ `10-SYSTEM-ARCHITECTURE.md`
**Propósito:** Vista de alto nivel del sistema.  
**Audiencia:** Technical decisions, onboarding.  
**Frecuencia de cambio:** Con cambios arquitectónicos mayores.  
**Tamaño objetivo:** 2000-3000 palabras.

**Contenido requerido:**
```markdown
# RaiSE System Architecture

## Diagrama de Contexto (C4 Level 1)
[Mermaid diagram: sistema + actores externos]

## Diagrama de Contenedores (C4 Level 2)
[Mermaid diagram: componentes principales]

## Componentes Core
### raise-kit (CLI)
- Propósito, responsabilidades, límites
- Stack tecnológico
- Dependencias externas

### raise-config (Central Repo)
- ...

### raise-mcp (Context Server)
- ...

## Flujos de Datos Principales
1. [Flujo A]: [diagrama secuencia o descripción]
2. ...

## Decisiones Arquitectónicas Clave
| Decisión | Opciones Consideradas | Elegida | Rationale |
|----------|----------------------|---------|-----------|

## Principios Técnicos
1. Platform Agnosticism: [qué significa en práctica]
2. Git as API: [implementación]
3. ...

## Constraints y Trade-offs
- [Constraint] → [Implicación]
```

---

#### 🏗️ `11-DATA-ARCHITECTURE.md`
**Propósito:** Estructuras de datos, schemas, ontología.  
**Audiencia:** Implementation, integrations.  
**Frecuencia de cambio:** Con cambios de schema.  
**Tamaño objetivo:** 1500-2500 palabras.

**Contenido requerido:**
```markdown
# RaiSE Data Architecture

## Ontología de Conceptos
[Diagrama ER o grafo de conceptos]

### Entidades Core
#### Rule
- Definición, atributos, relaciones
- JSON Schema

#### Kata
- ...

#### DoD (Definition of Done)
- ...

## Formatos de Archivo
### Markdown (Humanos)
- Estructura esperada
- Frontmatter schema

### JSON (Máquinas)
- raise-rules.json schema
- Ejemplos

## Flujo de Transformación
Markdown → [Librarian Kata] → JSON → [MCP Server] → Agent Context

## Versionado de Schemas
- Estrategia de migración
- Backward compatibility policy
```

---

#### 🏗️ `12-INTEGRATION-PATTERNS.md`
**Propósito:** Cómo RaiSE se conecta con el ecosistema.  
**Audiencia:** Integration development, partnerships.  
**Frecuencia de cambio:** Con nuevas integraciones.  
**Tamaño objetivo:** 2000-3000 palabras.

**Contenido requerido:**
```markdown
# RaiSE Integration Patterns

## Matriz de Integraciones
| Sistema | Tipo | Estado | Prioridad |
|---------|------|--------|-----------|
| GitHub | VCS | MVP | P0 |
| GitLab | VCS | Planned | P1 |
| Cursor | IDE | MVP | P0 |
| ...

## Patrones de Integración

### Patrón: VCS Provider
- Interface abstracta
- Implementación GitHub
- Implementación GitLab
- Testing strategy

### Patrón: IDE/Agent
- Slash commands
- MCP protocol
- Context injection

### Patrón: Project Management
- Jira sync
- Linear sync
- Bidirectional updates

## APIs Externas Consumidas
| API | Propósito | Auth | Rate Limits |
|-----|-----------|------|-------------|

## APIs Expuestas
| Endpoint | Propósito | Auth | Consumers |
|----------|-----------|------|-----------|
```

---

#### 🏗️ `13-SECURITY-COMPLIANCE.md`
**Propósito:** Postura de seguridad y compliance.  
**Audiencia:** Enterprise sales, audits.  
**Frecuencia de cambio:** Con nuevos requerimientos.  
**Tamaño objetivo:** 1500-2000 palabras.

**Contenido requerido:**
```markdown
# RaiSE Security & Compliance

## Modelo de Amenazas
[Threat model diagram]

### Activos Críticos
1. [Activo] - [Clasificación] - [Controles]

### Vectores de Ataque
1. [Vector] - [Mitigación]

## Políticas de Datos
- Data residency
- Encryption at rest/transit
- Retention policy

## Compliance Roadmap
| Framework | Estado | Target Date |
|-----------|--------|-------------|
| SOC2 Type I | Planned | Q3 2026 |
| ISO 27001 | Future | 2027 |
| EU AI Act | In Progress | Q2 2025 |

## Audit Trail
- Qué se loguea
- Retención
- Acceso

## Incident Response
[Proceso de respuesta a incidentes]
```

---

#### 🏗️ `14-ADR-INDEX.md`
**Propósito:** Índice de Architecture Decision Records.  
**Audiencia:** Understanding historical decisions.  
**Frecuencia de cambio:** Con cada ADR nuevo.  
**Tamaño objetivo:** Variable (índice + ADRs individuales).

**Contenido requerido:**
```markdown
# Architecture Decision Records

## Índice
| ID | Título | Estado | Fecha |
|----|--------|--------|-------|
| ADR-001 | Usar Python para CLI | Accepted | 2025-12 |
| ADR-002 | Git como API de distribución | Accepted | 2025-12 |
| ...

## Template ADR
[Template para nuevos ADRs]

---

## ADR-001: Usar Python para CLI

### Contexto
[Situación que requirió la decisión]

### Decisión
[Lo que decidimos]

### Consecuencias
- Positivas: [...]
- Negativas: [...]
- Neutras: [...]

### Alternativas Consideradas
1. [Alternativa] - [Por qué no]
```

---

#### 🏗️ `15-TECH-STACK.md`
**Propósito:** Stack tecnológico detallado.  
**Audiencia:** Development, hiring, onboarding.  
**Frecuencia de cambio:** Con cambios de dependencias.  
**Tamaño objetivo:** 1000-1500 palabras.

**Contenido requerido:**
```markdown
# RaiSE Tech Stack

## Core Stack
| Layer | Technology | Version | Rationale |
|-------|------------|---------|-----------|
| Language | Python | 3.11+ | Ecosystem, tooling |
| CLI Framework | Click + Rich | latest | UX, maintainability |
| HTTP | httpx | latest | Async support |
| ...

## Development Tools
| Tool | Purpose |
|------|---------|
| uv | Package management |
| pytest | Testing |
| ruff | Linting |
| ...

## Infrastructure
| Component | Technology |
|-----------|------------|
| CI/CD | GitHub Actions |
| Registry | PyPI |
| Docs | Docusaurus |

## Dependency Policy
- Criteria para agregar dependencias
- Update strategy
- Security scanning
```

---

### CAPA 3: DOMAIN (4-5 documentos)

#### 📚 `20-GLOSSARY.md`
**Propósito:** Definiciones canónicas de términos.  
**Audiencia:** Todos (humanos y agentes).  
**Frecuencia de cambio:** Con nuevos conceptos.  
**Tamaño objetivo:** Variable (crece orgánicamente).

**Contenido requerido:**
```markdown
# RaiSE Glossary

## Términos Core

### Agent
Un sistema de IA que ejecuta tareas de desarrollo. Ejemplos: GitHub Copilot, Claude Code, Cursor.

### Constitution
Conjunto de principios inmutables que gobiernan un proyecto. Vive en `memory/constitution.md`.

### Definition of Done (DoD)
Criterios que deben cumplirse para considerar una fase completada. En RaiSE, son "fractales" (cada fase tiene su propio DoD).

### Kata
Script o proceso de validación que verifica el cumplimiento de reglas. Inspirado en las katas de artes marciales (práctica deliberada).

### Rule
Una directiva que gobierna el comportamiento del agente o la calidad del código. Definida en Markdown, distribuida en JSON.

### Spec (Specification)
Documento que describe QUÉ construir, no CÓMO. Es la fuente de verdad para el agente.

...

## Términos Relacionados (Ecosistema)

### MCP (Model Context Protocol)
Protocolo de Anthropic para orquestar contexto entre herramientas y agentes.

### SDD (Spec-Driven Development)
Paradigma donde las especificaciones, no el código, son el artefacto primario.

...

## Anti-Términos (Qué NO usamos)
- "Vibe coding" → Usamos "development sin spec"
- ...
```

---

#### 📚 `21-METHODOLOGY.md`
**Propósito:** La metodología RaiSE en detalle.  
**Audiencia:** Users, implementers, trainers.  
**Frecuencia de cambio:** Con refinamientos metodológicos.  
**Tamaño objetivo:** 3000-4000 palabras.

**Contenido requerido:**
```markdown
# RaiSE Methodology

## Filosofía
### Los Tres Pilares
1. **Heutagogía**: [Explicación profunda]
2. **DoD Fractales**: [Explicación profunda]
3. **Kaizen**: [Explicación profunda]

## El Flujo de Valor

### Fase 0: Contexto
- Brownfield vs Greenfield
- Escaneo de legado
- Generación de reglas iniciales

### Fase 1: Discovery
- Protocolo de elicitación
- Artefacto: PRD
- DoD de fase

### Fase 2: Solution Vision
- Investigación contextual
- Artefacto: Vision Document
- DoD de fase

### Fase 3: Tech Design
- Traducción a diseño técnico
- Artefacto: Tech Design
- DoD de fase

### Fase 4: Backlog
- Atomización inteligente
- Artefacto: HUs priorizadas
- DoD de fase

### Fase 5: Implementation Plan
- Guionización determinista
- Artefacto: Plan paso a paso
- DoD de fase

### Fase 6: Development
- Debugging científico (Ishikawa)
- Ejecución guiada
- DoD de fase

### Fase 7: UAT & Deploy
- Despliegue adaptativo
- Validación final

## Katas de Validación
[Lista de katas disponibles y su propósito]

## Adaptación por Contexto
### Para Features Pequeñas
[Workflow abreviado]

### Para Proyectos Greenfield
[Workflow completo]

### Para Brownfield/Legacy
[Workflow con escaneo previo]
```

---

#### 📚 `22-TEMPLATES-CATALOG.md`
**Propósito:** Catálogo de templates disponibles.  
**Audiencia:** Users, template developers.  
**Frecuencia de cambio:** Con nuevos templates.  
**Tamaño objetivo:** Variable.

**Contenido requerido:**
```markdown
# RaiSE Templates Catalog

## Templates Core

### constitution.md
- Propósito: Principios inmutables del proyecto
- Variables: [lista]
- Ejemplo de uso

### spec.md
- Propósito: Especificación de feature
- Variables: [lista]
- Ejemplo de uso

### plan.md
- Propósito: Plan técnico
- Variables: [lista]
- Ejemplo de uso

### tasks.md
- Propósito: Lista de tareas implementables
- Variables: [lista]
- Ejemplo de uso

## Templates de DoD

### dod-strategy.md
...

### dod-design.md
...

### dod-code.md
...

## Templates de Katas

### kata-librarian.md
...

## Creación de Templates Personalizados
[Guía para crear nuevos templates]
```

---

#### 📚 `23-COMMANDS-REFERENCE.md`
**Propósito:** Referencia de comandos CLI y slash commands.  
**Audiencia:** Users, developers.  
**Frecuencia de cambio:** Con nuevos comandos.  
**Tamaño objetivo:** 1500-2500 palabras.

**Contenido requerido:**
```markdown
# RaiSE Commands Reference

## CLI Commands

### raise init
Inicializa un proyecto con estructura RaiSE.

**Sintaxis:**
```bash
raise init [--agent <agent>] [--template <template>]
```

**Opciones:**
| Flag | Descripción | Default |
|------|-------------|---------|
| --agent | Agente target | auto-detect |
| --template | Template base | standard |

**Ejemplos:**
```bash
raise init --agent cursor
raise init --agent copilot --template enterprise
```

### raise hydrate
Sincroniza reglas desde el repositorio central.
...

### raise check
Valida el proyecto contra las reglas.
...

## Slash Commands (Para Agentes)

### /raise.constitution
Genera o actualiza la constitución del proyecto.
...

### /raise.specify
Crea una especificación para una feature.
...

### /raise.plan
Genera un plan técnico desde una spec.
...

### /raise.tasks
Desglosa un plan en tareas implementables.
...

### /raise.implement
Ejecuta la implementación de tareas.
...

### /raise.validate
Ejecuta katas de validación.
...
```

---

#### 📚 `24-EXAMPLES-LIBRARY.md`
**Propósito:** Ejemplos concretos de uso.  
**Audiencia:** Users, training.  
**Frecuencia de cambio:** Con nuevos ejemplos.  
**Tamaño objetivo:** Variable (biblioteca creciente).

**Contenido requerido:**
```markdown
# RaiSE Examples Library

## Ejemplo 1: Feature Nueva en Proyecto Existente
### Contexto
[Descripción del escenario]

### Proceso Paso a Paso
1. [Comando/acción] → [Resultado]
2. ...

### Artefactos Generados
[Links o contenido de artefactos]

### Lecciones Aprendidas
...

## Ejemplo 2: Proyecto Greenfield Completo
...

## Ejemplo 3: Migración de Proyecto Legacy
...

## Ejemplo 4: Integración con Jira
...

## Anti-Ejemplos: Qué NO Hacer
### Anti-Ejemplo 1: Spec Demasiado Vaga
[Ejemplo de spec mala y por qué falla]
...
```

---

### CAPA 4: EXECUTION (4-5 documentos)

#### 🚀 `30-ROADMAP.md`
**Propósito:** Plan de desarrollo con hitos.  
**Audiencia:** Team, stakeholders, community.  
**Frecuencia de cambio:** Mensual.  
**Tamaño objetivo:** 1000-1500 palabras.

**Contenido requerido:**
```markdown
# RaiSE Roadmap

## Última Actualización
[Fecha]

## Visión de Releases

### v0.1.0 - MVP (Target: Q1 2025)
**Tema:** "Foundation"
- [ ] CLI básico (init, check)
- [ ] Soporte 5 agentes principales
- [ ] Templates core
- [ ] Documentación inicial

### v0.2.0 - DoD & Katas (Target: Q2 2025)
**Tema:** "Quality Gates"
- [ ] DoD fractales
- [ ] Katas de validación
- [ ] raise-config central

### v0.3.0 - Enterprise (Target: Q3 2025)
**Tema:** "Scale"
- [ ] MCP Server
- [ ] SSO integration
- [ ] Audit logging

## Milestones Actuales
| Milestone | Status | Target | Progress |
|-----------|--------|--------|----------|
| Fork completo | In Progress | 2025-01-05 | 60% |
| ...

## Backlog Priorizado
### P0 (Must Have)
1. [Item] - [Owner] - [ETA]

### P1 (Should Have)
...

### P2 (Nice to Have)
...

## Changelog
### [Fecha]
- [Cambio en roadmap y razón]
```

---

#### 🚀 `31-CURRENT-STATE.md`
**Propósito:** Estado actual del proyecto.  
**Audiencia:** Anyone joining mid-stream.  
**Frecuencia de cambio:** Semanal o más.  
**Tamaño objetivo:** 500-1000 palabras.

**Contenido requerido:**
```markdown
# RaiSE Current State

## Última Actualización
[Fecha y hora]

## Estado General
🟡 En Desarrollo Activo

## Lo Que Existe Hoy
- ✅ Fork de spec-kit completado
- ✅ Due diligence legal/técnico
- 🔄 Renaming en progreso
- ❌ DoD fractales (pendiente)
- ❌ Katas (pendiente)

## Trabajo en Progreso
### [Nombre del trabajo]
- Owner: [Persona]
- Status: [Estado]
- Blocker: [Si existe]
- ETA: [Fecha]

## Decisiones Pendientes
1. [Decisión] - [Contexto] - [Deadline]

## Métricas Actuales
| Métrica | Valor | Trend |
|---------|-------|-------|
| Lines of code | X | ↑ |
| Test coverage | Y% | → |
| Open issues | Z | ↓ |

## Siguiente Sesión de Trabajo
- Focus: [Qué se trabajará]
- Prerequisitos: [Qué debe estar listo]
```

---

#### 🚀 `32-SESSION-LOG.md`
**Propósito:** Log de sesiones de trabajo con agentes.  
**Audiencia:** Continuity entre sesiones.  
**Frecuencia de cambio:** Cada sesión.  
**Tamaño objetivo:** Variable (append-only).

**Contenido requerido:**
```markdown
# RaiSE Session Log

## Sesión [Fecha/Hora]

### Contexto de Entrada
- Estado previo: [referencia a estado]
- Objetivo de sesión: [qué queríamos lograr]

### Trabajo Realizado
1. [Acción] → [Resultado]
2. ...

### Decisiones Tomadas
- [Decisión]: [Rationale]

### Artefactos Creados/Modificados
- [Archivo]: [Cambio]

### Pendientes para Próxima Sesión
1. [Pendiente]

### Aprendizajes
- [Qué aprendimos que debe reflejarse en docs]

---

## Sesión [Fecha Anterior]
...
```

---

#### 🚀 `33-ISSUES-DECISIONS.md`
**Propósito:** Tracking de issues abiertos y decisiones pendientes.  
**Audiencia:** Decision makers.  
**Frecuencia de cambio:** Con resolución de issues.  
**Tamaño objetivo:** Variable.

**Contenido requerido:**
```markdown
# RaiSE Open Issues & Pending Decisions

## Issues Abiertos

### ISSUE-001: Nombre del Producto
**Status:** Open  
**Urgencia:** Media  
**Contexto:** ¿Usar "RaiSE" o considerar alternativas por trademark?  
**Opciones:**
1. RaiSE - [pros/cons]
2. SpecRise - [pros/cons]
3. ...
**Deadline:** 2025-01-15  
**Owner:** [Persona]

### ISSUE-002: ...

## Decisiones Recientes

### DEC-001: Fork de github/spec-kit directo
**Fecha:** 2025-12-26  
**Decisión:** Hacer fork del upstream principal, no del intermedio  
**Rationale:** Mayor actividad, menor bus factor  
**Consecuencias:** [Lista]

### DEC-002: ...
```

---

#### 🚀 `34-DEPENDENCIES-BLOCKERS.md`
**Propósito:** Tracking de dependencias externas y blockers.  
**Audiencia:** Project management.  
**Frecuencia de cambio:** Según cambios de estado.  
**Tamaño objetivo:** 500-1000 palabras.

**Contenido requerido:**
```markdown
# RaiSE Dependencies & Blockers

## Dependencias Externas

### DEP-001: Trademark Clearance
**Status:** 🟡 En Progreso  
**Blocker para:** Lanzamiento público  
**Owner:** [Persona]  
**ETA:** 2025-01-30  
**Notas:** [Actualizaciones]

### DEP-002: ...

## Blockers Actuales

### BLOCK-001: [Descripción]
**Impacto:** [Qué no puede avanzar]  
**Causa raíz:** [Por qué está bloqueado]  
**Plan de resolución:** [Pasos]  
**ETA de resolución:** [Fecha]

## Riesgos Identificados

### RISK-001: [Descripción]
**Probabilidad:** [Alta/Media/Baja]  
**Impacto:** [Alto/Medio/Bajo]  
**Mitigación:** [Plan]  
**Trigger de activación:** [Cuándo escala]
```

---

## 3. Organización del Repositorio de Docs

```
.raise/
├── docs/
│   ├── 00-constitution.md
│   ├── 01-product-vision.md
│   ├── 02-business-model.md
│   ├── 03-market-context.md
│   ├── 04-stakeholder-map.md
│   ├── 10-system-architecture.md
│   ├── 11-data-architecture.md
│   ├── 12-integration-patterns.md
│   ├── 13-security-compliance.md
│   ├── 14-adr-index.md
│   ├── 15-tech-stack.md
│   ├── 20-glossary.md
│   ├── 21-methodology.md
│   ├── 22-templates-catalog.md
│   ├── 23-commands-reference.md
│   ├── 24-examples-library.md
│   ├── 30-roadmap.md
│   ├── 31-current-state.md
│   ├── 32-session-log.md
│   ├── 33-issues-decisions.md
│   └── 34-dependencies-blockers.md
├── memory/
│   ├── constitution.md      # Constitution del proyecto RaiSE
│   └── raise-rules.json     # Reglas compiladas
└── DOCS-INDEX.md            # Índice navegable
```

---

## 4. Protocolo de Uso con Agentes

### 4.1 Inicio de Sesión

Cada sesión con un agente debe comenzar con:

```markdown
# Contexto de Sesión

## Proyecto
RaiSE - Reliable AI Software Engineering Framework

## Documentos a Cargar
Por favor lee los siguientes documentos en orden:
1. .raise/docs/00-constitution.md (principios)
2. .raise/docs/31-current-state.md (estado actual)
3. .raise/docs/[documento relevante para la tarea]

## Objetivo de Sesión
[Descripción clara del objetivo]

## Constraints
- [Limitaciones específicas]
```

### 4.2 Cierre de Sesión

Cada sesión debe terminar con:

```markdown
## Actualizar Documentos
1. Actualiza 31-current-state.md con el nuevo estado
2. Agrega entrada a 32-session-log.md
3. Si hubo decisiones, actualiza 33-issues-decisions.md
4. Si hay nuevos términos, actualiza 20-glossary.md
```

### 4.3 Selección de Documentos por Tarea

| Tipo de Tarea | Documentos a Cargar |
|---------------|---------------------|
| Diseño de feature | 00, 01, 10, 11, 21, 31 |
| Implementación | 00, 10, 15, 23, 31, 32 |
| Decisión técnica | 00, 10, 14, 33 |
| Integración nueva | 00, 10, 12, 15 |
| Preparar pitch | 01, 02, 03, 04 |
| Onboarding | 00, 01, 10, 20, 21 |

---

## 5. Mantenimiento del Corpus

### 5.1 Ownership

| Documento | Owner | Reviewer |
|-----------|-------|----------|
| 00-Constitution | Founder | All |
| 01-05 (Vision) | Product | Tech Lead |
| 10-15 (Architecture) | Tech Lead | Founder |
| 20-24 (Domain) | Tech Lead | Community |
| 30-34 (Execution) | Any | Self |

### 5.2 Cadencia de Revisión

| Capa | Frecuencia | Trigger |
|------|------------|---------|
| Constitution | Trimestral | Pivote mayor |
| Vision | Mensual | Cambio de estrategia |
| Architecture | Bi-semanal | Decisión técnica |
| Domain | Semanal | Nuevo concepto |
| Execution | Cada sesión | Siempre |

### 5.3 Señales de Decaimiento

- Documento no actualizado > 2x su cadencia esperada
- Contradicciones entre documentos
- Agentes produciendo output inconsistente
- Preguntas repetidas que deberían estar documentadas

---

## 6. Anti-Patrones a Evitar

1. **Documentación Aspiracional**: Escribir lo que queremos que sea, no lo que es
2. **Redundancia**: Mismo concepto definido en múltiples lugares
3. **Documentos Huérfanos**: Sin owner ni cadencia de revisión
4. **Over-documentation**: Docs que nadie lee porque son muy largos
5. **Under-documentation**: Gaps que causan decisiones inconsistentes
6. **Documentación Estática**: Tratarla como "terminada" en lugar de viva

---

## 7. Métricas de Salud del Corpus

| Métrica | Fórmula | Target |
|---------|---------|--------|
| Freshness Score | % docs actualizados en su cadencia | >90% |
| Coverage Score | % conceptos con definición en glossary | >95% |
| Consistency Score | # contradicciones detectadas | 0 |
| Utility Score | # veces que agentes referenciaron docs | ↑ |
| Onboarding Time | Tiempo para nuevo contributor productivo | <1 día |

---

*Este framework es en sí mismo un documento vivo. Debe evolucionar con RaiSE.*
