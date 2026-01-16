# RaiSE Dependencies & Blockers
## Dependencias Externas y Blockers

**Última Actualización:** 28 de Diciembre, 2025

---

## Dependencias Externas

### DEP-001: Trademark Clearance

**Status:** 🟡 En Progreso  
**Blocker para:** Lanzamiento público, marketing  
**Owner:** Emilio  
**ETA:** 2025-01-30

**Notas:**
- Iniciar búsqueda en USPTO, EUIPO
- Considerar alternativas si hay conflicto

---

### DEP-002: MCP Protocol [ACTUALIZADO v2.0]

**Status:** ✅ Resuelto (Adoptado como CORE)  
**Blocker para:** — (ya no es blocker)  
**Owner:** —  
**ETA:** —

**Notas:**
- MCP adoptado como componente CORE de RaiSE (ADR-003)
- 11,000+ servers registrados = estándar de facto
- Tracking de cambios en spec continúa
- Version pinning implementado para estabilidad
- Abstracción layer mantiene flexibilidad

**Decisión v2.0:** En lugar de esperar estabilidad, adoptamos MCP activamente y contribuimos al ecosistema.

---

### DEP-003: Python Packaging (uv)

**Status:** ✅ Resuelto  
**Blocker para:** —  
**Owner:** —

**Notas:**
- uv es estable y adoptado
- Alternativa a poetry/pip

---

### DEP-004: JSONL Tooling [NUEVO v2.0]

**Status:** ✅ Resuelto  
**Blocker para:** Observable Workflow  
**Owner:** —

**Notas:**
- JSONL parsing nativo en Python (json + líneas)
- jq disponible para análisis CLI
- No hay dependencia externa significativa

---

## Blockers Actuales

### BLOCK-002: Migración Terminología v2.0 [NUEVO]

**Status:** 🟡 En Progreso  
**Impacto:** Documentación legacy con terminología v1.0  
**Causa raíz:** Actualización ontológica  
**Plan de resolución:**
1. ✅ Crear documentos v2.0 paralelos
2. 🔄 Completar Layer 4 v2.0
3. 📋 Merge a repositorio principal
4. 📋 Actualizar katas y templates
5. 📋 Deprecation notice en docs v1.0

**Fecha resolución esperada:** 2025-12-29

---

## Blockers Resueltos

### BLOCK-001: Definición de Corpus Structure

**Impacto:** No se podía iniciar generación de documentos  
**Causa raíz:** Framework no definido  
**Resolución:** Creación de `raise-golden-data-framework.md`  
**Fecha resolución:** 2025-12-26

---

## Riesgos Identificados

### RISK-001: Dependencia de MCP [ACTUALIZADO v2.0]

**Probabilidad:** Media → Baja  
**Impacto:** Alto → Medio  
**Descripción:** MCP es estándar de Anthropic. Podría evolucionar con breaking changes.

**Actualización v2.0:** Riesgo reducido por:
- Adopción masiva (11k+ servers)
- Soporte de múltiples IDEs (Cursor, Windsurf, Zed)
- Microsoft involvement
- Anthropic commitment público

**Mitigación:**
- ✅ Abstracción en código (interface layer)
- ✅ Version pinning
- 🔄 Engagement con Anthropic community
- 📋 Fallback a .cursorrules/.claude.md para agentes legacy

**Trigger de escalación:** MCP 2.0 con breaking changes incompatibles

---

### RISK-002: Spec Kit Competition

**Probabilidad:** Media  
**Impacto:** Medio  
**Descripción:** GitHub/Microsoft podrían agregar governance features a Spec Kit.

**Mitigación:**
- ✅ Diferenciación profunda (Validation Gates, Heutagogía, Observable Workflow)
- ✅ MCP-native (spec-kit no tiene esto)
- 📋 Community building
- 📋 Enterprise focus

**Actualización v2.0:** RaiSE se diferencia ahora por ser MCP-native. Spec Kit no integra MCP.

**Trigger de escalación:** Spec Kit anuncia MCP integration

---

### RISK-003: Solo Founder

**Probabilidad:** Alta  
**Impacto:** Alto  
**Descripción:** Proyecto depende de un solo contributor.

**Mitigación:**
- ✅ Documentación exhaustiva (corpus v2.0)
- ✅ Session logs para continuidad
- 📋 Community contributors
- 📋 Buscar co-founder técnico

**Trigger de escalación:** Burnout, proyecto se detiene >2 semanas

---

### RISK-004: EU AI Act Compliance [NUEVO v2.0]

**Probabilidad:** Baja  
**Impacto:** Alto (para enterprise)  
**Descripción:** EU AI Act requiere trazabilidad de decisiones AI.

**Mitigación:**
- ✅ Observable Workflow implementado (ADR-008)
- ✅ Traces locales (privacy-first)
- 📋 Documentación de compliance
- 📋 Templates de audit report

**Trigger de escalación:** Nuevo requisito regulatorio no cubierto

---

### RISK-005: Ontology Drift [NUEVO v2.0]

**Probabilidad:** Media  
**Impacto:** Medio  
**Descripción:** Terminología Agentic AI evoluciona rápido. RaiSE podría quedar desactualizado.

**Mitigación:**
- ✅ Investigación periódica (Perplexity Deep Research)
- ✅ ADRs documentan decisiones terminológicas
- 📋 Revisión semestral de ontología
- 📋 Engagement con comunidad AI

**Trigger de escalación:** Nuevo framework dominante con terminología incompatible

---

## Dependencias Técnicas

### Stack Principal

| Dependencia | Versión | Status | Notas |
|-------------|---------|--------|-------|
| Python | 3.11+ | ✅ Estable | Target: 3.12 |
| Click | latest | ✅ Estable | CLI framework |
| Rich | latest | ✅ Estable | Terminal UI |
| GitPython | latest | ✅ Estable | Git operations |
| mcp-server-python | latest | 🔄 Tracking | MCP server |
| httpx | latest | ✅ Estable | HTTP client |
| PyYAML | latest | ✅ Estable | Config parsing |
| jsonschema | latest | ✅ Estable | Guardrail validation |

### Dependencias de Desarrollo

| Dependencia | Versión | Status | Notas |
|-------------|---------|--------|-------|
| uv | latest | ✅ Estable | Package manager |
| pytest | latest | ✅ Estable | Testing |
| ruff | latest | ✅ Estable | Linting |
| mypy | latest | ✅ Estable | Type checking |

---

## Proceso de Tracking

### Para Dependencias
1. Identificar cuando surge necesidad externa
2. Documentar impacto en roadmap
3. Asignar owner y ETA
4. Revisar semanalmente
5. **Crear ADR si es decisión arquitectónica** [NUEVO v2.0]

### Para Blockers
1. Identificar cuando trabajo no puede avanzar
2. Documentar causa raíz
3. Definir plan de resolución
4. Escalar si no resuelve en 48h

### Para Riesgos
1. Identificar en planning o retrospectiva
2. Evaluar probabilidad e impacto
3. Definir mitigación y trigger
4. Revisar mensualmente
5. **Actualizar si contexto cambia** [NUEVO v2.0]

---

## Changelog

### 2025-12-28
- DEP-002: MCP marcado como RESUELTO (adoptado como CORE)
- NUEVO: DEP-004 (JSONL Tooling)
- NUEVO: BLOCK-002 (Migración Terminología v2.0)
- ACTUALIZADO: RISK-001 (MCP risk reducido)
- ACTUALIZADO: RISK-002 (diferenciación MCP-native)
- NUEVO: RISK-004 (EU AI Act)
- NUEVO: RISK-005 (Ontology Drift)
- NUEVO: Sección Dependencias Técnicas

### 2025-12-27
- Documento inicial

---

*Este documento se revisa semanalmente. Ver [30-roadmap-v2.md](./30-roadmap-v2.md) para impacto en timeline.*
