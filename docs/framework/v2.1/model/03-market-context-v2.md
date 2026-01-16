# RaiSE Market Context
## Contexto de Mercado y Competencia

**Versión:** 2.0.0  
**Fecha:** 28 de Diciembre, 2025  
**Propósito:** Documentar el landscape competitivo y oportunidades de mercado.

> **Nota de versión 2.0:** Actualizado con tendencia MCP como estándar de facto, Observable Workflow como diferenciador, y Context Engineering como paradigma emergente.

---

## Tamaño de Mercado

| Segmento | TAM | SAM | SOM |
|----------|-----|-----|-----|
| AI Governance Software | $7B (2030) | $2B | $50M |
| Developer Tools | $40B (2027) | $5B | $100M |
| SDD/Spec Tools | $500M (2027) | $100M | $20M |
| **MCP Ecosystem** [NUEVO] | $1B (2028) | $200M | $10M |

**Fuentes:** Gartner, IDC, análisis interno, MCP Registry stats

---

## Tendencias Clave [ACTUALIZADO v2.0]

### 1. MCP como Estándar de Facto
**Tendencia:** Model Context Protocol (Anthropic) alcanza 11,000+ servers registrados.  
**Implicación:** Integración nativa MCP es requisito, no diferenciador.  
**Oportunidad RaiSE:** Ser el **único framework de governance MCP-native** antes de que otros reaccionen.

> *"MCP se convirtió en el USB de los agentes AI—si no eres compatible, no existes."* — Análisis interno, Dic 2025

### 2. De Prompt Engineering a Context Engineering
**Tendencia:** El paradigma evoluciona de "tweaking prompts" a "arquitectar contexto".  
**Implicación:** Los desarrolladores necesitan frameworks para diseñar ambientes informacionales.  
**Oportunidad RaiSE:** Posicionarse como el framework de **Context Engineering** para desarrollo.

> *"No es prompt engineering, es context engineering—arquitectar todo el ambiente de información en el que opera el LLM."* — Andrej Karpathy, 2025

### 3. AI Governance Mandatorio
**Tendencia:** EU AI Act en vigor, más regulaciones globales en camino.  
**Implicación:** Demanda creciente de herramientas que demuestren compliance.  
**Oportunidad RaiSE:** **Observable Workflow** como solución nativa de trazabilidad.

### 4. Saturación de AI Coding Tools
**Tendencia:** Mercado crowded (Copilot, Cursor, Claude Code, Windsurf, etc.).  
**Implicación:** Diferenciación difícil en "más código generado".  
**Oportunidad RaiSE:** Layer de governance sobre cualquier tool, no competidor.

### 5. Human-in-the-Loop (HITL) como Requisito
**Tendencia:** Sistemas agentic requieren puntos de control humano explícitos.  
**Implicación:** No basta con generar—hay que saber cuándo escalar.  
**Oportunidad RaiSE:** **Escalation Gates** como implementación sistemática de HITL.

### 6. Shift a Spec-Driven Development
**Tendencia:** Specs primero, código después está ganando tracción.  
**Implicación:** Tools como Spec Kit creciendo rápido.  
**Oportunidad RaiSE:** Agregar governance, calidad y observabilidad al paradigma SDD.

### 7. Enterprise AI Concerns
**Tendencia:** Enterprises preocupadas por calidad y trazabilidad de código AI.  
**Implicación:** Dispuestas a pagar por governance + audit trails.  
**Oportunidad RaiSE:** Enterprise tier con Observable Workflow + EU AI Act compliance.

---

## Competitive Landscape [ACTUALIZADO v2.0]

### Matriz de Posicionamiento

```
                    GOVERNANCE ENTERPRISE
                           ↑
                           |
    IBM Watson    ◦        |        ◉ RaiSE
    Collibra      ◦        |          (MCP-native +
    OneTrust      ◦        |           Observable)
                           |
    ←─────────────────────────────────────────────→
    DATA/MODEL             |            CODE/DEV
    FOCUSED                |            FOCUSED
                           |
    OpenSpec      ◦        |        ◦ Cursor
    Spec Kit      ◦        |        ◦ Copilot
    Kiro          ◦        |        ◦ Claude Code
    LangGraph     ◦        |        ◦ Windsurf
                           |
                           ↓
                    DEVELOPER TOOLS
```

### Nueva Dimensión: MCP Compatibility

```
                    MCP-NATIVE
                         ↑
                         |
         RaiSE ◉         |
                         |
    ←────────────────────────────────────→
    GOVERNANCE           |         GENERATION
    FOCUSED              |         FOCUSED
                         |
         Cursor ◦        |         ◦ Copilot
         Claude Code ◦   |         ◦ CodeWhisperer
                         |
                         ↓
                    NO MCP / PROPIETARIO
```

---

## Competidores Directos [ACTUALIZADO v2.0]

### Categoría: SDD/Context Engineering Tools

| Competidor | Fortalezas | Debilidades | Estrategia vs |
|------------|-----------|-----------|---------------|
| **GitHub Spec Kit** | 58k⭐, backing Microsoft | Sin governance, sin MCP, sin HITL | MCP-native + Observable + Escalation Gates |
| **AWS Kiro** | Integración AWS, recursos Amazon | Vendor lock-in, no MCP | Platform agnostic + MCP estándar |
| **OpenSpec** | Lightweight, TypeScript | Sin governance, sin observabilidad | Observable Workflow como upgrade |
| **BMAD Method** | Multi-agente robusto | Complejo, no MCP nativo | Simplicidad + MCP + governance |
| **LangGraph** | Framework agentic sólido | No es governance, es orquestación | Complementario, no competidor |

### Categoría: AI Coding Assistants

| Competidor | MCP Support | Relación con RaiSE |
|------------|-------------|-------------------|
| Claude Code | ✅ Nativo | Integración prioritaria via raise-mcp |
| Cursor | ✅ Nativo | Integración prioritaria via raise-mcp |
| Windsurf | ✅ Nativo | Integración via raise-mcp |
| GitHub Copilot | ❌ | Fallback via .github/copilot-instructions.md |
| Amazon CodeWhisperer | ❌ | Complemento potencial |

### Categoría: AI Governance Platforms

| Competidor | Fortalezas | Debilidades | Diferenciador RaiSE |
|------------|-----------|-----------|-------------------|
| IBM Watson Governance | Enterprise-grade | Caro, no code-focused, no MCP | Dev-first, MCP-native, affordable |
| Collibra | Data governance leader | No para código | Code-native + Observable Workflow |
| OneTrust | Privacy/compliance | General purpose | Especializado en dev AI |

### Análisis: ¿Quién tiene Observable Workflow?

| Competidor | Trazabilidad | Audit Trail | Métricas |
|------------|--------------|-------------|----------|
| RaiSE | ✅ JSONL local + export | ✅ Nativo | ✅ Integrado |
| Spec Kit | ❌ | ❌ | ❌ |
| Kiro | Parcial (AWS CloudTrail) | Parcial | ❌ |
| OpenSpec | ❌ | ❌ | ❌ |
| BMAD | ❌ | ❌ | ❌ |

**Conclusión:** Observable Workflow es diferenciador único en el segmento SDD.

---

## Regulatory Environment [ACTUALIZADO v2.0]

### EU AI Act
- **Entrada en vigor:** 2025 (fases)
- **Requisitos clave:** Trazabilidad, documentación, supervisión humana
- **Artículos relevantes:**
  - Art. 13: Transparencia y trazabilidad
  - Art. 14: Supervisión humana
  - Art. 17: Sistema de gestión de calidad
- **Implicación RaiSE:** Observable Workflow + Escalation Gates = compliance nativo

### Otros Frameworks
| Framework | Estado | Relevancia | Soporte RaiSE |
|-----------|--------|------------|---------------|
| NIST AI RMF | Publicado | Guía para governance | Templates de mapping |
| ISO/IEC 42001 | Publicado 2023 | Estándar AI MS | Audit export compatible |
| SOC2 | Establecido | Enterprise requirement | Observable Workflow evidencia |

---

## Oportunidades Identificadas [ACTUALIZADO v2.0]

| Oportunidad | Tamaño | Timing | Acción |
|-------------|--------|--------|--------|
| **MCP ecosystem leadership** | Grande | Q1 2025 | Listing en registry, docs ejemplares |
| EU AI Act compliance | Grande | 2025 | Observable Workflow + audit templates |
| Enterprise pilot programs | Medio | Q2 2025 | Outreach a early adopters |
| Spec Kit community migration | Medio | Ongoing | Migration guide + MCP como upgrade path |
| Partner integrations | Medio | Q3 2025 | IDE vendors, AI providers |
| **Context Engineering education** | Medio | Ongoing | Content marketing, thought leadership |

---

## Amenazas Activas [ACTUALIZADO v2.0]

| Amenaza | Probabilidad | Impacto | Mitigación |
|---------|--------------|---------|------------|
| GitHub agrega governance a Spec Kit | Media | Alto | MCP-native + Observable son defensivos |
| **Anthropic lanza governance layer** | Baja-Media | Alto | First-mover, community, platform-agnostic |
| Nuevo competidor bien-fondeado | Media | Medio | First-mover, community lock-in |
| **MCP protocol breaking changes** | Media | Medio | Version pinning, abstraction layer |
| Paradigma SDD no gana tracción | Baja | Alto | Pivote a governance + observability puro |
| EU AI Act se diluye | Baja | Medio | Value prop existe sin regulación |
| Open source fork competitivo | Baja | Bajo | Community engagement, moat en katas |

---

## Market Timing [ACTUALIZADO v2.0]

### Why Now?

1. **MCP es estándar:** 11,000+ servers, adopción masiva en 2025
2. **AI tools mainstream:** 84% de devs usando AI coding
3. **Quality concerns rising:** Satisfacción cayó a 60%
4. **Regulation imminent:** EU AI Act 2025
5. **Open spot in market:** No hay governance MCP-native líder
6. **Context Engineering emergente:** Paradigma buscando herramientas

### Window of Opportunity

```
2025 Q1-Q2: Establecer posición MCP-native + Observable
     ↓
2025 Q3-Q4: Enterprise traction via EU AI Act
     ↓
2026: Consolidación como estándar de governance
     ↓
2027+: Posible consolidación o adquisición
```

### Riesgo de Timing

| Escenario | Probabilidad | Respuesta |
|-----------|--------------|-----------|
| Llegamos primero | Alta | Capturar mercado, community |
| Llegamos junto con otros | Media | Diferenciación en Observable + Heutagogía |
| Llegamos tarde | Baja | Pivote a nicho (compliance puro) |

---

## Ecosystem Map [NUEVO v2.0]

```
┌─────────────────────────────────────────────────────────────────┐
│                        MCP ECOSYSTEM                            │
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │   Claude    │    │   Cursor    │    │  Windsurf   │         │
│  │   Code      │    │             │    │             │         │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘         │
│         │                  │                  │                 │
│         └──────────────────┼──────────────────┘                 │
│                            │                                    │
│                     ┌──────▼──────┐                             │
│                     │  raise-mcp  │ ◀── RaiSE's position        │
│                     │  (Context   │                             │
│                     │   Server)   │                             │
│                     └──────┬──────┘                             │
│                            │                                    │
│              ┌─────────────┼─────────────┐                      │
│              │             │             │                      │
│       ┌──────▼──────┐ ┌────▼────┐ ┌─────▼─────┐                │
│       │ Guardrails  │ │  Specs  │ │  Traces   │                │
│       │  (Rules)    │ │ (Plans) │ │ (Observ.) │                │
│       └─────────────┘ └─────────┘ └───────────┘                │
│                                                                 │
│                    11,000+ MCP Servers                          │
└─────────────────────────────────────────────────────────────────┘
```

---

## Última Actualización
**Fecha:** 28 de Diciembre, 2025  
**Cambios desde versión anterior:** 
- MCP como tendencia #1
- Context Engineering como paradigma
- Observable Workflow como diferenciador único
- Ecosystem map añadido
- Análisis de trazabilidad competitiva

---

## Changelog

### v2.0.0 (2025-12-28)
- Tendencias actualizadas: MCP, Context Engineering, HITL
- Matriz de posicionamiento con dimensión MCP
- Análisis de Observable Workflow vs competencia
- EU AI Act artículos específicos
- Ecosystem map
- Timing window actualizado

### v1.0.0 (2025-12-27)
- Documento inicial

---

*Este documento se actualiza mensualmente o con cambios significativos del mercado. Ver [01-product-vision-v2.md](./01-product-vision-v2.md) para estrategia de producto.*
