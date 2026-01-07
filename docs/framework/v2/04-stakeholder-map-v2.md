# RaiSE Stakeholder Map
## Mapa de Actores e Intereses

**Versión:** 2.0.0  
**Fecha:** 28 de Diciembre, 2025  
**Propósito:** Identificar stakeholders clave y sus intereses.

> **Nota de versión 2.0:** Actualizado con rol de Orquestador, stakeholders del ecosistema MCP, y nuevos intereses relacionados con Observable Workflow y compliance.

---

## Concepto: El Orquestador [NUEVO v2.0]

Antes de mapear stakeholders, es esencial entender el concepto central de RaiSE:

> **Orquestador** = Desarrollador que evoluciona de "escribir código" a "diseñar contexto y validar outputs".

**Evolución del rol:**
```
Developer (tradicional)
    ↓ adopta AI tools
AI-Assisted Developer (caos)
    ↓ adopta RaiSE
Orquestador (governance + growth)
```

**Características del Orquestador:**
- Define el "qué" (specs), valida el "cómo" (código)
- Diseña contexto para agentes (Context Engineering)
- Responde a Escalation Gates con criterio
- Crece profesionalmente (Heutagogía)
- Mantiene ownership del sistema

---

## Equipo Core

| Rol | Persona | Responsabilidades | Expertise |
|-----|---------|-------------------|-----------|
| Founder / Product | Emilio | Visión, estrategia, decisiones de producto | Product management, AI/ML, Lean |
| (futuro) Tech Lead | TBD | Arquitectura, code quality, raise-mcp | Python, MCP, distributed systems |
| (futuro) Community | TBD | Developer relations, docs, ecosystem | DevRel, content |
| (futuro) Compliance | TBD | EU AI Act, SOC2, enterprise reqs | Governance, auditoría |

---

## Advisors / Mentors

| Área | Perfil Buscado | Estado | Prioridad v2.0 |
|------|---------------|--------|----------------|
| MCP Ecosystem | Contributor MCP, conoce Anthropic | 📋 Por identificar | **P0** |
| Enterprise Sales | Experiencia vendiendo a enterprises | 📋 Por identificar | P1 |
| Open Source | Mantenedor de proyecto exitoso | 📋 Por identificar | P1 |
| AI Governance | Expertise en compliance/regulación | 📋 Por identificar | **P0** |
| VC/Funding | Conocimiento del landscape de inversión | 📋 Por identificar | P2 |

---

## Early Adopters Comprometidos

### Perfil Ideal de Early Adopter [ACTUALIZADO v2.0]

| Característica | Descripción |
|----------------|-------------|
| Tamaño | 10-50 developers |
| Pain | Inconsistencia en uso de AI tools |
| Motivación | Preparación para compliance + MCP adoption |
| Stack | Ya usa Cursor, Claude Code, o similar |
| Disponibilidad | Dispuesto a dar feedback + probar MCP |

### Perfil de "Orquestador Champion"

| Característica | Descripción |
|----------------|-------------|
| Rol | Staff/Senior Engineer con influencia |
| Mindset | Cree en governance, no solo velocidad |
| Interés | Quiere crecer, no solo producir |
| Capacidad | Puede evangelizar en su organización |

### Early Adopters Actuales

| Organización | Tipo | Estado | Notas |
|--------------|------|--------|-------|
| HumanSys | Interna | ✅ Usando | Desarrollo interno, primer Orquestador |
| (otros) | TBD | 📋 Por identificar | Outreach Q1 2025 |

---

## Partners Potenciales [ACTUALIZADO v2.0]

### Technology Partners

| Partner | Tipo | Value Prop | Prioridad | Estado |
|---------|------|------------|-----------|--------|
| **Anthropic** | AI Provider | MCP native integration, raise-mcp listing | **P0** | 📋 Explorar |
| **Cursor** | IDE | Native MCP support, rules integration | **P0** | 📋 Explorar |
| Windsurf | IDE | MCP support, alternative a Cursor | P1 | 📋 Explorar |
| Claude Code | CLI | MCP native, complemento natural | P1 | 📋 Explorar |
| GitHub | VCS | Spec Kit compatibility, fallback | P2 | 📋 Explorar |
| VS Code | IDE | Extension marketplace | P2 | 📋 Explorar |

### Compliance Partners [NUEVO v2.0]

| Partner Type | Role | Target |
|--------------|------|--------|
| EU AI Act Consultants | Validation de approach | Enterprises EU |
| SOC2 Auditors | Certificación | Enterprise tier |
| GRC Vendors | Integración | Observable Workflow export |

### Channel Partners

| Partner Type | Role | Target |
|--------------|------|--------|
| Consulting Firms | Implementation | Enterprises |
| Training Companies | Education, Orquestador certification | Teams |
| SI (System Integrators) | Solutions | Large orgs |

---

## User Personas (Actualizado)

Ver [01-product-vision-v2.md](./01-product-vision-v2.md#user-personas) para detalle completo.

| Persona | Rol v2.0 | Interés Principal |
|---------|----------|-------------------|
| **Elena** | Staff Engineer / Platform Architect | Estandarizar prácticas AI, Observable Workflow |
| **Devon** | Senior Developer → **Orquestador** | Productividad + crecimiento + ownership |
| **Carlos** | Compliance Officer | Audit trail, Observable Workflow, EU AI Act |

### Nueva Persona: "Alex, el Escéptico" [NUEVO v2.0]

**Rol:** Tech Lead experimentado  
**Contexto:** Ha visto muchos frameworks ir y venir  
**Concern:** "¿Por qué otro framework? ¿No es overhead innecesario?"

**Cómo convencer:**
- Demostrar ROI tangible (menos re-prompting, menos bugs)
- Mostrar Observable Workflow metrics
- Enfatizar que no reemplaza herramientas, las gobierna
- Heutagogía: sus devs crecen, no se atrofian

---

## Comunidad

### Canales Actuales

| Canal | URL | Propósito |
|-------|-----|-----------|
| GitLab Repo | gitlab.com/humansys-demos/raise1 | Código fuente (interno) |
| (futuro) GitHub | github.com/raise-dev | Mirror público |
| (futuro) Discord | TBD | Community chat |
| (futuro) Discussions | GitHub Discussions | Q&A, RFCs |
| **MCP Registry** | mcp.io (TBD) | raise-mcp listing |

### Métricas de Community (Targets) [ACTUALIZADO v2.0]

| Métrica | Q1 2025 | Q2 2025 | Q4 2025 |
|---------|---------|---------|---------|
| GitHub stars | 500 | 2,000 | 5,000 |
| Contributors | 5 | 15 | 50 |
| Discord members | 100 | 500 | 2,000 |
| **MCP Registry installs** | 100 | 500 | 2,000 |
| **Orquestadores activos** | 50 | 200 | 1,000 |

---

## Stakeholder Communication

### Matriz de Comunicación

| Stakeholder | Frecuencia | Canal | Owner |
|-------------|------------|-------|-------|
| Core Team | Daily | Sync, chat | All |
| Early Adopters | Weekly | Email, calls | Founder |
| Community | Ongoing | Discord, GitHub | (future) Community |
| Advisors | Monthly | Calls | Founder |
| Partners | As needed | Email, meetings | Founder |
| **MCP Ecosystem** | Ongoing | GitHub, MCP channels | Founder |

---

## Intereses por Stakeholder [ACTUALIZADO v2.0]

| Stakeholder | Interés Principal | Cómo Satisfacer |
|-------------|-------------------|-----------------|
| **Orquestadores** | Productividad + crecimiento + ownership | UX excelente, Heutagogía, Observable Workflow |
| Tech Leads | Governance sin micromanagement | Guardrails centralizados, métricas de equipo |
| Enterprises | Compliance, seguridad, EU AI Act | Observable Workflow, audit export, SLAs |
| Community | Participación, recognition, MCP ecosystem | Open development, credits, MCP compatibility |
| Compliance Officers | Trazabilidad, evidencia | Observable Workflow, templates EU AI Act |
| Investors (futuro) | Growth, monetization | Métricas claras, MRR |
| **Reguladores** | Transparencia, supervisión humana | Observable Workflow, Escalation Gates docs |

---

## Matriz de Poder/Interés [NUEVO v2.0]

```
                    ALTO INTERÉS
                         ↑
                         |
    ┌────────────────────┼────────────────────┐
    │                    │                    │
    │   MANTENER         │   GESTIONAR        │
    │   SATISFECHOS      │   DE CERCA         │
    │                    │                    │
    │   • Advisors       │   • Early Adopters │
    │   • Partners       │   • Orquestadores  │
BAJO│                    │   • Core Team      │ALTO
PODER├────────────────────┼────────────────────┤PODER
    │                    │                    │
    │   MONITOREAR       │   MANTENER         │
    │   (mínimo esfuerzo)│   INFORMADOS       │
    │                    │                    │
    │   • Community      │   • Enterprises    │
    │     general        │   • Reguladores    │
    │                    │                    │
    └────────────────────┼────────────────────┘
                         |
                         ↓
                    BAJO INTERÉS
```

**Implicación estratégica:**
- **Gestionar de cerca:** Orquestadores y Early Adopters son co-creadores
- **Mantener informados:** Enterprises y Reguladores necesitan Observable Workflow
- **Mantener satisfechos:** Partners MCP son multiplicadores
- **Monitorear:** Community general se autogestiona

---

## Ecosistema MCP: Stakeholders Externos [NUEVO v2.0]

| Actor | Rol en Ecosistema | Relación con RaiSE |
|-------|-------------------|-------------------|
| Anthropic | Creador MCP, Claude | Enabler, potencial partner |
| MCP Server Authors | 11k+ servers | Peers, potencial integración |
| IDE Vendors | Implementan MCP clients | Distribution channels |
| AI Agent Builders | Usan MCP para tools | Usuarios de raise-mcp |

---

## Compromisos de RaiSE con Stakeholders

> Estos compromisos se derivan de la [Constitution v2.0](./00-constitution-v2.md#compromisos-con-stakeholders).

### Con Orquestadores (Developers)
- Nunca aumentar fricción sin valor demostrable
- Respetar sus herramientas existentes
- Proveer feedback inmediato y accionable
- **Enseñar, no solo ejecutar** (Heutagogía)

### Con Organizaciones
- Path claro Community → Enterprise
- Datos dentro de infraestructura del cliente
- Soporte compliance frameworks
- **Observable Workflow como evidencia**

### Con Comunidad Open Source
- Core siempre open source (MIT)
- Contribuciones upstream
- Documentación pública y completa

### Con Reguladores
- Trazabilidad completa de decisiones AI
- Audit trails exportables
- Documentación de guardrails como controles

---

## Changelog

### v2.0.0 (2025-12-28)
- Concepto de Orquestador introducido
- Partners MCP añadidos (P0)
- Nueva persona: Alex el Escéptico
- Matriz de Poder/Interés
- Ecosistema MCP como stakeholders externos
- Métricas MCP Registry
- Compromisos alineados con Constitution v2.0

### v1.0.0 (2025-12-27)
- Documento inicial

---

*Este mapa se actualiza con cambios en el equipo o stakeholders clave. Ver [00-constitution-v2.md](./00-constitution-v2.md) para compromisos formales.*
