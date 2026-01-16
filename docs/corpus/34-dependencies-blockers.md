# RaiSE Dependencies & Blockers
## Dependencias Externas y Blockers

**Última Actualización:** 27 de Diciembre, 2025

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

### DEP-002: MCP Protocol Stability

**Status:** 🟡 Monitoring  
**Blocker para:** raise-mcp v1.0  
**Owner:** —  
**ETA:** Dependiente de Anthropic

**Notas:**
- MCP aún en evolución activa
- Tracking de cambios en spec
- Plan de migración si hay breaking changes

---

### DEP-003: Python Packaging (uv)

**Status:** ✅ Resuelto  
**Blocker para:** —  
**Owner:** —  

**Notas:**
- uv es estable y adoptado
- Alternativa a poetry/pip

---

## Blockers Actuales

*No hay blockers críticos actualmente.*

---

## Blockers Resueltos

### BLOCK-001: Definición de Corpus Structure

**Impacto:** No se podía iniciar generación de documentos  
**Causa raíz:** Framework no definido  
**Resolución:** Creación de `raise-golden-data-framework.md`  
**Fecha resolución:** 2025-12-26

---

## Riesgos Identificados

### RISK-001: Dependencia de MCP

**Probabilidad:** Media  
**Impacto:** Alto  
**Descripción:** MCP es estándar joven de Anthropic. Podría cambiar o ser abandonado.

**Mitigación:**
- Abstracción en código (interface layer)
- Monitorear alternatives (LSP, custom)
- Engagement con Anthropic community

**Trigger de escalación:** Anthropic anuncia deprecation o breaking changes mayores

---

### RISK-002: Spec Kit Competition

**Probabilidad:** Media  
**Impacto:** Medio  
**Descripción:** GitHub/Microsoft podrían agregar governance features a Spec Kit.

**Mitigación:**
- Diferenciación profunda (DoD, Heutagogía)
- Community building
- Enterprise focus

**Trigger de escalación:** Spec Kit anuncia features similares

---

### RISK-003: Solo Founder

**Probabilidad:** Alta  
**Impacto:** Alto  
**Descripción:** Proyecto depende de un solo contributor.

**Mitigación:**
- Documentación exhaustiva (este corpus)
- Community contributors
- Buscar co-founder técnico

**Trigger de escalación:** Burnout, proyecto se detiene >2 semanas

---

## Proceso de Tracking

### Para Dependencias
1. Identificar cuando surge necesidad externa
2. Documentar impacto en roadmap
3. Asignar owner y ETA
4. Revisar semanalmente

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

---

*Este documento se revisa semanalmente.*
