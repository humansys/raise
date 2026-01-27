# Feature 012: Research para Estructuración de Comandos RaiSE

**Branch**: `012-raise-commands-research`
**Tipo**: Research & Architecture
**Fecha Inicio**: 2026-01-23
**Estado**: 🔬 In Progress

---

## Objetivo

Investigar y documentar la correcta estructuración de los comandos de RaiSE, integrando los hallazgos de:

1. **Análisis arquitectónico de spec-kit** (8 comandos analizados)
2. **Análisis de comandos RaiSE onboarding** (analyze.code, rules.generate)
3. **Investigación de prácticas de la industria** (brownfield documentation for AI agents)

---

## Contexto

Actualmente tenemos:

- **18 comandos RaiSE** distribuidos en 01-onboarding/, 02-projects/, 03-feature/
- **Roadmap de estandarización** con 3 waves de migración
- **12 patrones arquitectónicos** extraídos de spec-kit
- **10 anti-patrones** a evitar
- **40K+ palabras** de research sobre prácticas de la industria

Este feature de research busca consolidar todo ese conocimiento en recomendaciones accionables para la reestructuración de comandos RaiSE.

---

## Alcance de Research

### 1. Análisis Arquitectónico Completado

✅ **Comandos spec-kit analizados** (8):
- `speckit.1.specify` (create-spec)
- `speckit.2.clarify` (refinement)
- `speckit.3.plan` (implementation planning)
- `speckit.4.tasks` (task generation)
- `speckit.5.analyze` (quality gate)
- `speckit.6.implement` (execution)
- `speckit.util.checklist` (validation)
- `speckit.util.issues` (GitHub integration)
- **Sistema general** (specify-system-architecture)

✅ **Comandos RaiSE onboarding analizados** (2):
- `raise.1.analyze.code` (SAR brownfield analysis)
- `raise.rules.generate` (pattern mining & rule formalization)

✅ **Investigación de industria**:
- 7 case studies con métricas
- 15+ herramientas catalogadas
- 13 recomendaciones priorizadas
- 5 patrones noveles identificados

**Total documentación**: ~86K palabras

### 2. Deliverables Esperados

**D1: Análisis Comparativo de Comandos**
- Matriz de comparación entre comandos RaiSE y spec-kit
- Identificación de gaps y oportunidades
- Mapeo de arquetipos (Generator/Refiner/Analyzer/Tool)

**D2: Propuesta de Reestructuración**
- Aplicación de patrones spec-kit a comandos RaiSE
- Integración de hallazgos de research (YAML frontmatter, RAG, etc.)
- Priorización de refactoring (quick wins vs strategic)

**D3: Guía de Implementación**
- Checklist de estandarización por comando
- Templates actualizados
- Scripts de validación

**D4: Plan de Migración Refinado**
- Actualización del roadmap con insights de research
- Timeline ajustado
- Métricas de éxito

---

## Artefactos Existentes

### Análisis Arquitectónico
- `specs/main/analysis/architecture/` (10 reports, ~180K)
  - speckit.{1-6} + util.{checklist,issues} + specify-system
  - raise.1.analyze-code
  - raise.rules.generate
  - Design patterns synthesis
  - README (índice maestro)

### Research de Industria
- `specs/main/research/brownfield-agent-docs/`
  - landscape-report.md (8.2K)
  - recommendations.md (22K)
  - research-summary.md (10K)
  - sources/ (catalog)

### Roadmap Existente
- `specs/main/migration/command-standardization-roadmap.md`
  - 3 waves de migración
  - 18 comandos → 14 comandos (reducción 22%)
  - Checklist de estandarización

---

## Próximos Pasos

1. **Crear análisis comparativo** entre comandos RaiSE y spec-kit
2. **Identificar quick wins** de la investigación aplicables a comandos RaiSE
3. **Proponer reestructuración** integrando:
   - Patrones spec-kit (IEF, incremental persistence, etc.)
   - Recomendaciones de research (YAML frontmatter, AST-RAG, etc.)
   - Gaps identificados (Katas faltantes, validación, handoffs)
4. **Actualizar roadmap** con nueva información
5. **Generar guía de implementación** para Wave 1

---

## Referencias

- **ADR-012**: `/.private/decisions/adr-012-speckit-command-consolidation.md`
- **Roadmap**: `/specs/main/migration/command-standardization-roadmap.md`
- **Análisis arquitectónico**: `/specs/main/analysis/architecture/`
- **Research industria**: `/specs/main/research/brownfield-agent-docs/`
- **Constitution RaiSE**: `/docs/framework/v2.1/model/00-constitution-v2.md`
- **Glosario**: `/docs/framework/v2.1/model/20-glossary-v2.1.md`

---

**Maintained by**: RaiSE Ontology Architect + Emilio
**Status**: Research en progreso
**Target Completion**: 2 semanas
