# RaiSE Business Model

## Modelo de Negocio

**Versión:** 2.0.0**Fecha:** 28 de Diciembre, 2025**Propósito:** Documentar cómo RaiSE genera y captura valor.

> **Nota de versión 2.0:** Modelo actualizado con Observable Workflow como feature diferenciador, terminología v2.0 (guardrails), y MCP como componente comercial.

---

## Modelo: Open Core

RaiSE sigue el modelo **Open Core**:

- **Core open source (MIT):** CLI, guardrails base, templates, katas, raise-mcp
- **Valor añadido comercial:** Features enterprise, soporte, SLAs, analytics avanzado

### Rationale

- Construir comunidad y confianza
- Reducir fricción de adopción
- Diferenciación via features enterprise
- Contribuciones community mejoran el core
- **MCP open garantiza interoperabilidad** [NUEVO v2.0]

---

## Tiers y Pricing 

| Tier                 | Precio       | Target                            | Features                                                             |
| -------------------- | ------------ | --------------------------------- | -------------------------------------------------------------------- |
| **Community**  | Gratis       | Developers individuales, startups | CLI completo, raise-mcp, guardrails base, Observable Workflow local  |
| **Pro**        | $29/user/mes | Equipos pequeños (5-20 devs)     | + Analytics dashboard, + Katas L3, + Priority issues                 |
| **Enterprise** | Custom       | Empresas (50+ devs)               | + SSO/SAML, + Audit export, + SLA, + On-premise, + Custom guardrails |

### Detalles por Tier

#### Community (Free)

**Core value:** Todo para empezar a gobernar AI-assisted development

- raise-kit CLI completo
- **raise-mcp server (CORE)** [NUEVO v2.0]
- Guardrails y katas base
- Templates core
- **Observable Workflow local (JSONL)** [NUEVO v2.0]
- **8 Validation Gates estándar** [NUEVO v2.0]
- **Escalation Gates básicos** [NUEVO v2.0]
- Documentación pública
- GitHub Discussions support
- Self-hosted raise-config

**Limitaciones:**

- Analytics local only (via `raise audit`)
- Sin export OpenTelemetry
- Community support (best-effort)

#### Pro ($29/user/mes)

**Core value:** Métricas y visibilidad para equipos

Todo de Community +:

- **Analytics dashboard** (web-based)
- **Observable Workflow cloud sync** (opcional)
- **Export a OpenTelemetry, DataDog, etc.** [NUEVO v2.0]
- Katas L3 avanzadas
- **Métricas de equipo agregadas** [NUEVO v2.0]
- Priority en issues
- Actualizaciones early access
- Email support (48h response)

#### Enterprise (Custom)

**Core value:** Compliance, escala y soporte dedicado

Todo de Pro +:

- SSO/SAML integration
- **Audit logging compliance-grade** [NUEVO v2.0]
- **EU AI Act reporting templates** [NUEVO v2.0]
- SLA 99.9% (para componentes hosted)
- On-premise deployment guide
- Custom guardrail development
- **Custom Validation Gates** [NUEVO v2.0]
- Dedicated support (24h response)
- Training y onboarding
- **Integración con sistemas GRC existentes** [NUEVO v2.0]

---

## Productos Core 

| Producto                    | Tier       | Descripción             |
| --------------------------- | ---------- | ------------------------ |
| **raise-kit**         | Community  | CLI principal            |
| **raise-mcp**         | Community  | MCP server (CORE)        |
| **raise-config**      | Community  | Repo de guardrails/katas |
| **raise-analytics**   | Pro        | Dashboard de métricas   |
| **raise-audit-cloud** | Pro        | Observable Workflow sync |
| **raise-enterprise**  | Enterprise | Suite compliance         |

---

## Revenue Streams

| Stream               | % Esperado Y3 | Descripción                            |
| -------------------- | ------------- | --------------------------------------- |
| Subscriptions Pro    | 40%           | Teams pequeños/medianos                |
| Contracts Enterprise | 45%           | Grandes organizaciones                  |
| Services             | 10%           | Consulting, training, custom guardrails |
| Sponsorships         | 5%            | Patrocinios community                   |

### Revenue por Feature 

| Feature                   | Monetización         |
| ------------------------- | --------------------- |
| Validation Gates          | Community (free)      |
| Observable Workflow Local | Community (free)      |
| Observable Workflow Cloud | Pro                   |
| Analytics Dashboard       | Pro                   |
| EU AI Act Reports         | Enterprise            |
| Custom Guardrails         | Enterprise + Services |

---

## Cost Structure

### Fixed Costs

| Categoría             | Descripción                       |
| ---------------------- | ---------------------------------- |
| Desarrollo             | Equipo core (1-3 personas inicial) |
| Infra                  | GitHub, dominio, hosting docs      |
| Legal                  | Trademark, términos de servicio   |
| **MCP Registry** | Listing en registry oficial        |

### Variable Costs

| Categoría           | Descripción                                 |
| -------------------- | -------------------------------------------- |
| Support              | Escala con customers                         |
| Infrastructure       | Analytics cloud, Observable Workflow storage |
| Marketing            | Content, eventos                             |
| **Compliance** | Certificaciones (SOC2, etc.)                 |

---

## Unit Economics (Targets)

| Métrica       | Target Y1       | Target Y3 |
| -------------- | --------------- | --------- |
| CAC (Pro)      | $200 | $150     |           |
| LTV (Pro)      | $1,000 | $1,500 |           |
| LTV/CAC        | 5x              | 10x       |
| Churn mensual  | <5%             | <3%       |
| Payback period | 7 meses         | 5 meses   |

---

## Go-to-Market Strategy

### Canales

| Canal                   | Prioridad | Descripción                                            |
| ----------------------- | --------- | ------------------------------------------------------- |
| Community/PLG           | P0        | Product-led growth via GitHub + MCP Registry            |
| Content                 | P0        | Blog, tutorials, casos de estudio                       |
| **MCP Ecosystem** | P0        | Integración con ecosystem de 11k+ servers [NUEVO v2.0] |
| Social                  | P1        | Twitter/X, LinkedIn, YouTube                            |
| Partnerships            | P2        | Integraciones con vendors AI                            |
| Events                  | P2        | Conferencias, meetups                                   |
| Outbound                | P3        | Solo para Enterprise                                    |

### Community Strategy

1. **Open Development:** Roadmap público, RFCs abiertos
2. **Recognition:** Contributors destacados
3. **Engagement:** Discord/Slack activo
4. **Content:** Tutoriales generados por community
5. **Feedback Loop:** Issues → features rápido
6. **MCP Interop:** Contribuir al ecosistema MCP [NUEVO v2.0]

### Partner Strategy

| Partner Type                 | Value Prop                              |
| ---------------------------- | --------------------------------------- |
| IDE Vendors                  | raise-mcp integration                   |
| AI Agent Providers           | MCP compatibility certificada           |
| Consulting Firms             | Implementation partners + training      |
| Training Providers           | Certified trainers                      |
| **Compliance Vendors** | Integración con GRC tools [NUEVO v2.0] |

---

## Competitive Moat [ACTUALIZADO v2.0]

| Moat                          | Descripción                                   |
| ----------------------------- | ---------------------------------------------- |
| **MCP-Native**          | Único framework governance con MCP nativo     |
| **Observable Workflow** | Trazabilidad que otros no tienen               |
| **Validation Gates**    | Quality gates sistemáticos por fase           |
| **Heutagogía**         | Philosophy differentiator (Orquestador growth) |
| **Community**           | Network effects                                |
| **Katas Library**       | Content moat creciente                         |
| **Enterprise Trust**    | Compliance + security                          |

---

## Milestones Financieros

| Milestone            | Target  | Métrica       |
| -------------------- | ------- | -------------- |
| First 1000 users     | Q2 2025 | Adoption       |
| MCP Registry listing | Q2 2025 | Ecosystem      |
| First Pro customer   | Q2 2025 | Revenue        |
| $10K MRR             | Q4 2025 | Scale          |
| First Enterprise     | Q1 2026 | Validation     |
| Break-even           | Q4 2026 | Sustainability |

---

## Risks

| Riesgo                                 | Mitigación                                    |
| -------------------------------------- | ---------------------------------------------- |
| Pricing too high                       | Feedback loops, adjust early                   |
| Pricing too low                        | Start low, increase with value                 |
| Community not monetizing               | Observable Workflow cloud como upgrade natural |
| Enterprise sales cycle long            | PLG para pipeline                              |
| **MCP protocol changes**         | Version pinning, abstraction layer             |
| **Competitor copies Observable** | First-mover + community lock-in                |

---

## Changelog

### v2.0.0 (2025-12-28)

- Productos actualizados con raise-mcp, raise-analytics
- Features por tier actualizados con Observable Workflow
- Terminología: rules → guardrails
- MCP Ecosystem como canal GTM
- Competitive moat actualizado
- Risks actualizados

### v1.0.0 (2025-12-27)

- Modelo inicial

---

*Este modelo se revisa trimestralmente basado en datos reales. Ver [01-product-vision-v2.md](./01-product-vision-v2.md) para contexto estratégico.*
