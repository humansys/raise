# RaiSE Product Vision
## Reliable AI Software Engineering Framework

**VersiÃ³n:** 2.0.0  
**Fecha:** 28 de Diciembre, 2025  
**Estado:** Ratificado

> **Nota de versiÃ³n 2.0:** VisiÃ³n actualizada con diferenciadores MCP-native, Observable Workflow, y terminologÃ­a v2.1 (Validation Gates, Guardrails, Orquestador).

---

## Problema Central

### El Dolor
Los equipos de desarrollo adoptan herramientas de AI coding (Copilot, Cursor, Claude Code) sin governance. El resultado:

- **Inconsistencia**: Cada desarrollador usa AI de forma diferente, produciendo cÃ³digo heterogÃ©neo
- **Alucinaciones no detectadas**: Sin validaciÃ³n estructurada, errores de AI llegan a producciÃ³n
- **PÃ©rdida de contexto**: Cada sesiÃ³n con AI empieza de cero; no hay "memoria" organizacional
- **Atrofia cognitiva**: Desarrolladores aceptan cÃ³digo AI sin entenderlo
- **Compliance gaps**: Regulaciones como EU AI Act exigen trazabilidad que no existe
- **Opacidad de decisiones**: No hay forma de auditar *por quÃ©* el agente tomÃ³ una decisiÃ³n [NUEVO v2.1]

### Evidencia
- El mercado de AI Governance crece 35-50% CAGR, de $200M (2024) a $7B+ (2030)
- 84% de desarrolladores usan AI tools, pero satisfacciÃ³n cayÃ³ a 60% por calidad inconsistente
- 77% de empresas iniciaron frameworks de AI governance; 90% de las que tienen deployments activos
- EU AI Act entra en vigor 2025, mandando trazabilidad y governance
- **11,000+ MCP servers registrados** â€” MCP es el estÃ¡ndar de facto para Context Engineering [NUEVO v2.1]

---

## SoluciÃ³n Propuesta

**RaiSE** es un framework de Context Engineering que estructura el uso de AI en desarrollo de software mediante governance-as-code y observabilidad nativa.

### CÃ³mo Funciona [ACTUALIZADO v2.1]

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”    â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”    â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚   raise-config      â”‚    â”‚     raise-mcp       â”‚    â”‚   AI Agent          â”‚
â”‚   (Central Repo)    â”‚â”€â”€â”€â”€â–¶â”‚   (MCP Server)      â”‚â”€â”€â”€â”€â–¶â”‚   (Copilot,        â”‚
â”‚                     â”‚    â”‚     LOCAL           â”‚    â”‚    Cursor, Claude)  â”‚
â”‚  â€¢ Guardrails (.mdc)â”‚    â”‚                     â”‚    â”‚                     â”‚
â”‚  â€¢ Katas            â”‚    â”‚  â€¢ Context Server   â”‚    â”‚  â€¢ Contexto via     â”‚
â”‚  â€¢ Templates        â”‚    â”‚  â€¢ Validation Gates â”‚    â”‚    MCP Protocol     â”‚
â”‚  â€¢ Constitution     â”‚    â”‚  â€¢ Observable Tracesâ”‚    â”‚  â€¢ Tools MCP        â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜    â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜    â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
       Git                        MCP                      IDE/CLI
                                  â”‚
                                  â–¼
                     â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                     â”‚  .raise/traces/     â”‚
                     â”‚  Observable Workflowâ”‚
                     â”‚  (JSONL local)      â”‚
                     â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

### Diferenciadores Clave [ACTUALIZADO v2.1]

| Diferenciador | DescripciÃ³n | Competidores sin esto |
|---------------|-------------|----------------------|
| **MCP-Native** | Context Engineering via estÃ¡ndar de facto (11k+ servers) | Spec Kit, OpenSpec, Kiro |
| **Validation Gates** | Quality gates por fase, no solo al final | Spec Kit, OpenSpec, Kiro |
| **Observable Workflow** | Trazabilidad completa de decisiones AI | **TODOS** |
| **Escalation Gates** | HITL explÃ­cito con criterios definidos | **TODOS** |
| **Katas Ejecutables** | Validaciones automÃ¡ticas de specs y cÃ³digo | Todos |
| **HeutagogÃ­a** | Entrenamiento activo del Orquestador | Todos (focus en reemplazo) |
| **Git-Native** | Sin APIs propietarias; Git como transporte | Kiro (AWS), Tessl (SaaS) |
| **Platform Agnostic** | GitHub, GitLab, Bitbucket indistintamente | Copilot (GitHub), Kiro (AWS) |

---

## Propuesta de Valor Ãšnica (UVP)

> **"RaiSE convierte el caos del AI-assisted development en un proceso gobernable, trazable y que mejora continuamenteâ€”sin sacrificar la velocidad. Es el Ãºnico framework MCP-native con Observable Workflow."**

### Value Props por Stakeholder [ACTUALIZADO v2.1]

| Stakeholder | Value Prop |
|-------------|------------|
| **Developer (Orquestador)** | "Mis herramientas AI producen cÃ³digo consistente porque tienen contexto estructurado via MCP" |
| **Tech Lead** | "Puedo gobernar cÃ³mo mi equipo usa AI con Validation Gates automÃ¡ticos" |
| **VP Engineering** | "Tengo Observable Workflow: trazabilidad completa para mÃ©tricas y compliance" |
| **CISO** | "Los guardrails de seguridad se aplican automÃ¡ticamente y tengo audit trail" |
| **Compliance Officer** | "EU AI Act cubierto: cada decisiÃ³n AI es auditable" |

---

## User Personas

### Persona A: "Elena, la MetodÃ³loga"
**Rol:** Staff Engineer / Platform Architect  
**Contexto:** Empresa de 100+ developers, mÃºltiples equipos  
**Goals:**
- Estandarizar prÃ¡cticas de AI-assisted development
- Reducir inconsistencias entre equipos
- Preparar para auditorÃ­as de compliance

**Pain Points:**
- Cada equipo usa AI de forma diferente
- No hay forma de medir calidad del cÃ³digo AI-generated
- Regulaciones (EU AI Act) se acercan sin preparaciÃ³n
- **No puede auditar decisiones de agentes** [NUEVO v2.1]

**Jobs-to-be-Done:**
- Definir guardrails que todos los equipos sigan
- Distribuir actualizaciones sin fricciÃ³n
- Validar cumplimiento automÃ¡ticamente
- **Generar reportes de Observable Workflow** [NUEVO v2.1]

### Persona B: "Devon, el Orquestador"
**Rol:** Senior Developer â†’ **Orquestador** [ACTUALIZADO]  
**Contexto:** Trabaja en features con AI daily  
**Goals:**
- Entregar features rÃ¡pido y con calidad
- No perder tiempo en setup y configuraciÃ³n
- Entender y poder mantener cÃ³digo AI-generated
- **Crecer como profesional, no atrofiarse** [NUEVO v2.1]

**Pain Points:**
- AI genera cÃ³digo inconsistente con patrones del proyecto
- Tiene que "adivinar" quÃ© contexto darle al AI
- A veces acepta cÃ³digo sin entenderlo completamente
- **No sabe cuÃ¡ndo el agente tiene baja confianza** [NUEVO v2.1]

**Jobs-to-be-Done:**
- Obtener contexto estructurado automÃ¡ticamente via MCP
- Validar que su cÃ³digo pasa Validation Gates
- Aprender de las decisiones que AI tomÃ³
- **Responder a Escalation Gates de forma informada** [NUEVO v2.1]

### Persona C: "Carlos, el Compliance Officer"
**Rol:** Security/Compliance Manager  
**Contexto:** Enterprise regulada (Fintech, Healthcare)  
**Goals:**
- Demostrar governance de AI a auditores
- Trazabilidad de quÃ© cÃ³digo fue AI-generated
- PolÃ­ticas aplicadas consistentemente

**Pain Points:**
- No sabe quÃ© cÃ³digo es AI-generated
- No hay audit trail de decisiones AI
- Cada auditorÃ­a es un scramble

**Jobs-to-be-Done:**
- Generar reportes de compliance automÃ¡ticos via `raise audit`
- Tener Observable Workflow logs para auditorÃ­a
- Demostrar guardrails como cÃ³digo versionado

---

## Casos de Uso Primarios

### CU-1: Onboarding de Proyecto Existente
**Trigger:** Equipo quiere adoptar RaiSE en proyecto brownfield  
**Flow:**
1. `raise init` escanea el proyecto
2. `raise mcp start` inicia servidor MCP
3. Genera constitution basada en patrones detectados
4. Crea guardrails iniciales respetando el legado
5. Developer usa `/raise.specify` para nueva feature
6. **Observable Workflow comienza a registrar traces** [NUEVO v2.1]

**Outcome:** Proyecto existente tiene governance + observabilidad sin rewrite

### CU-2: Governance Centralizada Multi-Proyecto
**Trigger:** Platform team quiere gobernar 50+ repos  
**Flow:**
1. Platform team mantiene `raise-config` central
2. Cada repo configura `raise.yaml` con URL del config
3. `raise pull` sincroniza guardrails en cada repo
4. CI ejecuta `raise check` + `raise gate status` bloqueando non-compliance
5. **`raise audit --format json` genera reportes agregados** [NUEVO v2.1]

**Outcome:** Una sola fuente de verdad + mÃ©tricas aggregadas de Observable Workflow

### CU-3: Desarrollo con Validation Gates [ACTUALIZADO]
**Trigger:** Orquestador comienza feature nueva  
**Flow:**
1. `/raise.specify` â†’ Genera spec, valida **Gate-Discovery**
2. `/raise.plan` â†’ Genera plan tÃ©cnico, valida **Gate-Design**
3. `/raise.tasks` â†’ Genera tareas, valida **Gate-Backlog**
4. `/raise.implement` â†’ Ejecuta tareas con validaciÃ³n continua
5. **Escalation Gate si agente tiene baja confianza** [NUEVO v2.1]
6. Kata final valida **Gate-Code**
7. **`raise audit` para revisar sesiÃ³n** [NUEVO v2.1]

**Outcome:** Cada fase tiene Validation Gate; Orquestador mantiene ownership

### CU-4: Audit Trail para Compliance [ACTUALIZADO]
**Trigger:** Auditor pregunta "Â¿cÃ³mo gobiernan AI?"  
**Flow:**
1. Mostrar `raise-config` con guardrails versionados en Git
2. Mostrar Observable Workflow: `.raise/traces/*.jsonl`
3. Ejecutar `raise audit --period month --format md`
4. Demostrar trazabilidad spec â†’ plan â†’ cÃ³digo â†’ decisiones

**Outcome:** EU AI Act compliance con evidencia concreta

### CU-5: Escalation Gate en AcciÃ³n [NUEVO v2.1]
**Trigger:** Agente encuentra ambigÃ¼edad durante implementaciÃ³n  
**Flow:**
1. Agente ejecuta `validate_gate` via MCP
2. Gate falla por criterio ambiguo
3. Agente ejecuta `escalate` tool con opciones
4. Orquestador recibe notificaciÃ³n con contexto
5. Orquestador decide y responde
6. DecisiÃ³n registrada en Observable Workflow

**Outcome:** Human-in-the-Loop estructurado, decisiones documentadas

---

## Anti-Casos de Uso

Lo que RaiSE **explÃ­citamente NO hace**:

| Anti-Caso | Por quÃ© no |
|-----------|------------|
| Reemplazar al developer | HeutagogÃ­a: evolucionamos al Orquestador |
| Ser otro AI coding assistant | Somos governance + context layer, no generator |
| Funcionar solo con un IDE | Platform agnostic por principio |
| Requerir cloud/SaaS | Git-native + MCP local, funciona 100% on-premise |
| Garantizar cÃ³digo sin bugs | Reducimos errores, no los eliminamos |
| Vigilar sin valor | Observable Workflow es para mejora, no surveillance |

---

## MÃ©tricas de Ã‰xito

### MÃ©tricas de AdopciÃ³n

| MÃ©trica | Baseline | Target Y1 | Target Y3 |
|---------|----------|-----------|-----------|
| Community users | 0 | 5,000 | 100,000 |
| Pro subscribers | 0 | 50 | 2,000 |
| Enterprise deals | 0 | 0 | 10 |
| GitHub stars | 0 | 5,000 | 25,000 |
| **MCP Registry listings** | 0 | 1 | N/A |

### MÃ©tricas de Valor

| MÃ©trica | Baseline | Target |
|---------|----------|--------|
| Tiempo promedio spec â†’ cÃ³digo | Variable | -40% |
| Defectos post-release AI code | Variable | -50% |
| AuditorÃ­as sin hallazgos crÃ­ticos | N/A | 100% |
| Adherencia a patrones definidos | N/A | >90% |
| **Escalation rate** | N/A | 10-15% |
| **Re-prompting rate** | N/A | <3 |

### MÃ©tricas de Engagement

| MÃ©trica | Target |
|---------|--------|
| NPS (Pro/Enterprise) | >50 |
| Monthly active CLI users | >60% of installs |
| Community contributions | >50/quarter |
| **Observable Workflow adoption** | >80% of projects |

---

## Competitive Positioning [ACTUALIZADO v2.1]

```
                    GOVERNANCE ENTERPRISE
                           â†‘
                           |
    IBM Watson    â—¦        |        â—‰ RaiSE
    Collibra      â—¦        |          (MCP-native +
    OneTrust      â—¦        |           Observable)
                           |
    â†â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â†’
    DATA/MODEL             |            CODE/DEV
    FOCUSED                |            FOCUSED
                           |
    OpenSpec      â—¦        |        â—¦ Cursor
    Spec Kit      â—¦        |        â—¦ Copilot
    Kiro          â—¦        |        â—¦ Claude Code
                           |
                           â†“
                    DEVELOPER TOOLS
```

### Competidores Directos [ACTUALIZADO v2.1]

| Competidor | Fortaleza | Debilidad | Estrategia vs |
|------------|-----------|-----------|---------------|
| GitHub Spec Kit | 58kâ­, backing Microsoft | Sin governance, sin MCP | MCP-native + Observable Workflow |
| AWS Kiro | IntegraciÃ³n AWS | Vendor lock-in, overkill | Platform agnostic, local-first |
| OpenSpec | Lightweight, TypeScript | Menos features, sin HITL | Escalation Gates, HeutagogÃ­a |
| BMAD Method | Multi-agente robusto | Complejo, curva alta | Simplicidad + MCP estÃ¡ndar |
| **LangGraph** | Framework agentic sÃ³lido | No es para governance | Complementario, no competidor |

### Diferenciador Ãšnico [NUEVO v2.1]

**NingÃºn framework combina:**
1. MCP-native (estÃ¡ndar de facto)
2. Observable Workflow (trazabilidad EU AI Act)
3. Escalation Gates (HITL estructurado)
4. HeutagogÃ­a (crecimiento del Orquestador)

---

## Roadmap de Alto Nivel [ACTUALIZADO v2.1]

### v0.1 - Foundation (Q1 2025)
- CLI bÃ¡sico (init, check, pull)
- Soporte 5 agentes principales
- Templates core
- DocumentaciÃ³n

### v0.2 - MCP-Native & Validation Gates (Q2 2025)
- **raise-mcp server (CORE)**
- Validation Gates completos (8 gates)
- Guardrails system
- `raise gate`, `raise guardrail` commands

### v0.3 - Observable Workflow (Q3 2025)
- Observable Workflow completo
- `raise audit` command
- JSONL trace storage
- Escalation Gates (HITL)

### v0.4 - Enterprise Preview (Q4 2025)
- SSO/SAML integration
- Team analytics dashboard
- On-premise deployment guide

### v1.0 - Production (Q1 2026)
- Estabilidad API
- SOC2 Type I
- Integraciones Jira/Linear
- Marketplace de katas community

---

## Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | MitigaciÃ³n |
|--------|--------------|---------|------------|
| GitHub agrega governance a Spec Kit | Media | Alto | MCP-native + Observable son diferenciadores profundos |
| MCP evoluciona con breaking changes | Media | Medio | Version pinning, abstraction layer |
| Paradigma SDD no gana tracciÃ³n | Baja | Alto | Pivote a governance + observability puro |
| Competidor bien-fondeado entra | Media | Medio | First-mover en MCP + Observability |
| EU AI Act se diluye | Baja | Medio | Value prop existe sin regulaciÃ³n |

---

## Preguntas Abiertas

1. **Naming final**: Â¿RaiSE es el nombre definitivo? (Trademark clearance pendiente)
2. **Pricing validation**: Â¿$29/$49/custom es el punto correcto?
3. **First enterprise target**: Â¿QuÃ© vertical atacar primero?
4. **MCP transport default**: Â¿stdio vs SSE para raise-mcp?

---

## Changelog

### v2.1.0 (2025-12-28)
- Diferenciadores actualizados: MCP-native, Observable Workflow
- TerminologÃ­a: DoD â†’ Validation Gates, rules â†’ guardrails
- Nuevo CU-5: Escalation Gate en AcciÃ³n
- Roadmap alineado con ontologÃ­a v2.1
- MÃ©tricas aÃ±adidas: escalation rate, re-prompting rate
- Posicionamiento competitivo actualizado

### v1.0.0 (2025-12-26)
- VisiÃ³n inicial

---

*Este documento es la fuente de verdad para decisiones de producto. Actualizar con cada pivote o aprendizaje significativo.*
