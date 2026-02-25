# Research Report: Atlassian Forge Integration for Governance Sidebar

**RAISE-273** | **Date:** 2026-02-24 | **Researcher:** Rai (AI) | **Depth:** Standard
**Decision informs:** Architecture for Coppel governance copilot in Confluence

---

## Executive Summary

**La pregunta original era equivocada — y eso es buena noticia.**

Fernando investigaba si se puede crear un "sidebar panel" custom en Confluence con Forge. La respuesta corta: **no, ese módulo no existe**. Pero hay algo mejor: **Rovo Agents**, la plataforma de agentes AI nativos de Atlassian, ya proporciona exactamente lo que necesitamos — un chat contextual integrado en Confluence que puede leer/escribir páginas, ejecutar acciones custom, y está incluido sin costo adicional en todas las suscripciones pagas de Atlassian desde abril 2025.

**Recommendation: GO** — Construir un Rovo Agent custom con acciones Forge como la arquitectura principal.

**Confidence: HIGH** (16/18 fuentes primarias, documentación oficial, tutorial funcional existente)

---

## Arquitectura Recomendada

```
+---------------------------+
|   Confluence Cloud        |
|                           |
|  +---------------------+ |     +-------------------+
|  | Rovo Agent           | |     | RaiSE Backend     |
|  | "Governance Copilot" | |     | (API externa)     |
|  |                      | |     |                   |
|  | Prompt: LPM/SAFe     | |     | - Knowledge Graph |
|  | governance rules,    | |     | - Template engine |
|  | templates, workflow  | |     | - Validation      |
|  |                      | |     |                   |
|  | Actions:             | |     +-------------------+
|  | - read-page          |---------->  |
|  | - validate-document  |---------->  |
|  | - generate-section   |---------->  |
|  | - submit-for-review  | |          |
|  | - check-consistency  |---------->  |
|  +---------------------+ |
|                           |
|  Entry points:            |
|  - Chat button (top nav)  |
|  - /ai command (editor)   |
|  - Conversation starters  |
+---------------------------+
```

### Componentes

1. **Rovo Agent (Forge)** — El agente AI que vive en Confluence
   - Prompt engineered para governance LPM/SAFe
   - Conversation starters predefinidos ("Create Lean Business Case", "Validate Portfolio Canvas")
   - Acciones custom que conectan con el backend

2. **Rovo Actions (Forge Functions)** — Las capacidades del agente
   - `read-governance-doc`: Lee la página activa, extrae secciones
   - `validate-against-template`: Envía contenido al backend para validación
   - `generate-section`: Pide al backend que genere una sección basada en contexto
   - `submit-for-review`: Cambia el status de la página + notifica aprobadores
   - `check-cross-doc-consistency`: Valida coherencia entre documentos vía knowledge graph

3. **RaiSE Backend (API externa)** — Donde vive la inteligencia
   - Knowledge graph con contexto organizacional
   - Templates de documentos de gobierno
   - Motor de validación de consistencia
   - Expuesto como API HTTPS (requerido por Forge)

### Flujo de Uso (Demo Coppel)

1. Un Portfolio Manager abre una página de Confluence
2. Invoca al agente via `/ai` o el botón de Chat
3. Dice: "Ayúdame a crear un Lean Business Case para [iniciativa]"
4. El agente lee el Portfolio Canvas existente (action: read-page)
5. Genera secciones del LBC basándose en el template y contexto (action: generate-section via backend)
6. El usuario revisa, edita, refina en conversación
7. El agente valida consistencia con otros documentos (action: check-consistency)
8. El usuario dice "Submit for review"
9. El agente cambia el status de la página y notifica (action: submit-for-review)

---

## Viabilidad por Capacidad

| Capacidad | Viabilidad | Confianza | Notas |
|-----------|-----------|-----------|-------|
| Chat en Confluence | **GO** | HIGH | Rovo Agent nativo, ya existe |
| Leer contenido de página | **GO** | HIGH | Confluence REST API v2, tutorial existente |
| Escribir/editar página | **GO** | HIGH | Rovo tiene "edit page" built-in + API |
| Conectar a API externa | **GO** | HIGH | fetch() con dominios declarados en manifest |
| Streaming LLM responses | **GO** | HIGH | Forge Realtime + async functions |
| Approval workflow | **GO con caveats** | MEDIUM | Status nativos + automation, no hay módulo Forge dedicado |
| Sidebar persistente junto a la página | **NO-GO** | HIGH | No existe el módulo, pero Rovo chat es alternativa suficiente |
| Memoria entre interacciones | **WORKAROUND** | MEDIUM | Guardar estado en content properties o Forge storage |

---

## Constraints Técnicos

| Constraint | Valor | Impacto | Mitigación |
|-----------|-------|---------|------------|
| Timeout sync | 25 segundos | Medio | Async functions (hasta 900s) + Realtime |
| Timeout async | 900 segundos (15 min) | Bajo | Suficiente para LLM calls |
| Memoria | 512MB - 1GB | Bajo | Suficiente para documentos governance |
| Payload response | 5MB | Bajo | Docs governance son texto, bien bajo ese límite |
| Egress | HTTPS only, dominios pre-declarados | Bajo | Declarar dominio de RaiSE backend en manifest |
| Rovo: sin memoria entre conversaciones | - | Alto | Forge Storage / Content Properties para estado |
| Forge LLMs API | EAP (experimental) | Medio | Usar backend propio para LLM, Forge solo como bridge |
| Distribución | Sin private Marketplace listing | Bajo | Distribution links para clientes directos |

---

## Riesgos y Mitigaciones

### R1: Sin memoria entre interacciones Rovo (ALTO)
**Impacto:** Workflows multi-paso pueden perder contexto entre mensajes.
**Mitigación:** Almacenar estado del workflow en Confluence content properties. Cada acción lee estado previo antes de ejecutar. El prompt del agente instruye a reconstruir contexto.

### R2: Forge LLMs API es EAP (MEDIO)
**Impacto:** API podría cambiar, no tiene SLA.
**Mitigación:** No depender de ella. Usar nuestro propio backend LLM via fetch(). Forge solo como bridge, no como cerebro.

### R3: Rovo chat no es sidebar persistente (MEDIO)
**Impacto:** UX diferente al mockup original de "sidebar junto a la página".
**Mitigación:** El chat Rovo es contextual cuando se invoca desde el editor (/ai). Para el use case de governance, es suficiente. Reframe la demo.

### R4: Iteración significativa para prompt engineering (MEDIO)
**Impacto:** No es plug-and-play, requiere refinamiento.
**Mitigación:** Usar approach híbrido: no-code agent para iterar prompts rápido, luego portar a Forge para producción.

### R5: Dependencia en Atlassian Cloud (BAJO)
**Impacto:** Solo funciona en Confluence Cloud, no Server/DC.
**Mitigación:** Coppel ya usa Cloud. Para clientes on-premise, se necesitaría arquitectura diferente.

---

## Dos Opciones de Arquitectura

### Opción A: Rovo Agent + Backend Propio (RECOMENDADA)

```
Rovo Agent (prompt + actions) → Forge Functions → fetch() → RaiSE API
```

**Pros:**
- Chat nativo en Confluence, zero UI development
- Control total del LLM y lógica en nuestro backend
- Knowledge graph centralizado
- Independiente del EAP de Forge LLMs

**Contras:**
- Requiere backend desplegado y accesible vía HTTPS
- Sin memoria entre interacciones (workaround vía storage)
- Latencia adicional por hop extra (Forge → Backend)

### Opción B: Rovo Agent + Forge LLMs API (Solo Atlassian)

```
Rovo Agent (prompt + actions) → Forge Functions → Forge LLMs API (Claude)
```

**Pros:**
- Todo dentro de Atlassian, "Runs on Atlassian" badge
- Sin backend externo que mantener
- Streaming nativo

**Contras:**
- EAP, sin SLA
- Sin knowledge graph propio (solo Teamwork Graph de Atlassian)
- Menos control sobre la lógica
- Templates y validación tendrían que vivir en Forge storage

### Veredicto: Opción A

Opción A nos da control sobre la inteligencia (knowledge graph, templates, validación) mientras aprovecha la UI nativa de Rovo. El backend puede ser el mismo raise-cli o un API wrapper. La Opción B nos ata completamente a Atlassian y pierde el diferenciador de RaiSE.

---

## Implicaciones para RaiSE PRO

1. **El producto es el agente + el backend, no la UI** — Rovo provee la UI gratis
2. **Diferenciador: knowledge graph + governance templates + validation engine** — Lo que Rovo no tiene
3. **Modelo de distribución:** Forge app con distribution link (no Marketplace inicialmente)
4. **Prerequisito para Coppel:** Tener un API backend de RaiSE desplegado en HTTPS
5. **Licensing:** Rovo viene gratis con su suscripción Confluence Cloud (desde April 2025)

---

## Next Steps

1. **Fernando:** Configurar entorno Forge y crear hello-world Rovo Agent en Confluence de prueba
2. **Diseño:** Definir las 5-6 acciones core del governance copilot
3. **Backend:** Diseñar API endpoints que las acciones Forge consumirían
4. **Prompt:** Iterar el prompt del agente con governance rules y templates
5. **Demo jueves:** Mostrar el concepto arquitectónico + hello-world funcional (si hay tiempo)

---

## Sources

Full evidence catalog: [sources/evidence-catalog.md](sources/evidence-catalog.md)

Key references:
- [Forge Confluence Modules](https://developer.atlassian.com/platform/forge/manifest-reference/modules/index-confluence/)
- [Rovo Agent Module](https://developer.atlassian.com/platform/forge/manifest-reference/modules/rovo-agent/)
- [Rovo Action Module](https://developer.atlassian.com/platform/forge/manifest-reference/modules/rovo-action/)
- [Forge LLMs API](https://developer.atlassian.com/platform/forge/runtime-reference/forge-llms-api/)
- [Forge Realtime + LLM Streaming](https://developer.atlassian.com/platform/forge/llm-long-running-process-with-forge-realtime/)
- [Q&A Rovo Agent Tutorial](https://developer.atlassian.com/platform/forge/build-a-q-and-a-rovo-agent-for-confluence/)
- [External APIs + Rovo: What Actually Works](https://community.atlassian.com/forums/Atlassian-AI-Rovo-articles/External-APIs-Rovo-Agents-What-Actually-Works/ba-p/3096718)
- [Rovo Pricing](https://support.atlassian.com/rovo/kb/understand-rovo-billing-and-managing-costs-in-atlassian-cloud/)
- [Forge Invocation Limits](https://developer.atlassian.com/platform/forge/limits-invocation/)
