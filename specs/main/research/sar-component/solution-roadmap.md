# SAR Component - Solution Roadmap

**Document ID**: ROAD-SAR-001
**Version**: 1.0.0
**Date**: 2026-01-28
**Author**: Emilio + Claude Opus 4.5
**Status**: Activo
**Related Docs**:
  - [Solution Vision](./solution-vision.md) - Vision estrategica
  - [Semantic Density Research](./semantic-density/) - Research de formatos

---

## Estado Actual

**Track Activo**: Track A (Open Core)
**Fase Actual**: A1 - Foundation & Schemas
**Ultima Actualizacion**: 2026-01-28

### Progreso General

```
Track A: Open Core
├── A1: Foundation & Schemas     [ ] En progreso
├── A2: Comando SAR              [ ] Pendiente
├── A3: CLI raise get rules      [ ] Pendiente
└── A4: Documentacion & Launch   [ ] Pendiente

Track B: Licensed
└── (Pendiente validacion Open Core)
```

---

## Alcance por Tier

### Tier 1: Open Core MVP

El Open Core es el primer entregable, usando el patron "Deterministic Rails, Non-Deterministic Engine".

**Entregables:**

| # | Entregable | Descripcion |
|---|------------|-------------|
| 1 | Comando `raise.sar.analyze` | Pipeline completo via LLM synthesis |
| 2 | JSON Schemas | Schemas para rule.yaml, graph.yaml |
| 3 | CLI `raise get rules` | Query de reglas con MVC |
| 4 | Documentacion | Guia de uso, ejemplos por stack |

**Caracteristicas del comando SAR:**
- Pipeline LLM: DETECT → SCAN → DESCRIBE → GOVERN
- Prompts estructurados con secciones esperadas
- Schemas JSON/YAML para validar outputs
- Gates de validacion (estructura, no contenido)
- Context management (chunking, purging)
- Stack-agnostico (React, PydanticAI, PHP, Vite, Next.js)

**Formato de outputs:**
- `specs/main/sar/project-profile.yaml`
- `specs/main/sar/conventions.md`
- `specs/main/sar/rules/*.yaml`
- `specs/main/sar/graph.yaml`

### Tier 2: Licensed

El producto Licensed agrega capacidades enterprise sobre Open Core.

**Entregables adicionales:**

| # | Entregable | Descripcion |
|---|------------|-------------|
| 1 | Pipeline determinista | Phases 0-1 con ast-grep, ripgrep |
| 2 | Observabilidad | Logs, metricas, dashboard |
| 3 | CI/CD integrations | GitHub Actions, GitLab CI gates |
| 4 | Multi-repo governance | Reglas compartidas entre proyectos |
| 5 | Tooling por stack | Parsers optimizados (TS, Python, React) |

### Fuera del Alcance (Ambos Tiers)

1. ~~Extraccion automatica sin supervision~~ (siempre human-in-the-loop)
2. ~~Machine learning para inferir reglas~~ (no ML, solo LLM synthesis)
3. ~~Evaluacion contra Clean Code/Architecture~~ (excluido por "Facts Not Gaps")

### Considerado para Futuro

1. Integracion con IDEs (VS Code extension, JetBrains plugin)
2. RAG avanzado (embeddings, retrieval semantico, re-ranking)
3. Autofix suggestions basadas en reglas

---

## Track A: Open Core

### Fase A1: Foundation & Schemas

**Duracion estimada**: 1 semana
**Objetivo**: Establecer los schemas y templates que definen el formato de outputs

**Tareas:**

- [ ] **A1.1** Finalizar JSON Schema para regla unitaria (`rule-schema.json`)
  - Campos: id, version, status, category, confidence, pattern, examples, provenance
  - Validar con ejemplos reales

- [ ] **A1.2** Finalizar JSON Schema para grafo (`graph-schema.json`)
  - Campos: nodes, edges, version
  - Tipos de edges: requires, conflicts_with, supersedes, related_to

- [ ] **A1.3** Crear templates de output SAR
  - `project-profile.yaml` template
  - `conventions.md` template
  - Estructura de `rules/` directory

- [ ] **A1.4** Documentar formato de prompts estructurados
  - Prompt template por fase (DETECT, SCAN, DESCRIBE, GOVERN)
  - Ejemplos de outputs esperados

**Criterio de completitud:**
- Schemas validados con al menos 3 ejemplos cada uno
- Templates documentados con instrucciones de uso

**Dependencias:**
- Semantic Density Research (completado)

---

### Fase A2: Comando SAR No-Determinista

**Duracion estimada**: 2 semanas
**Objetivo**: Implementar el comando principal de analisis SAR

**Tareas:**

- [ ] **A2.1** Crear estructura de comando
  - `.raise-kit/commands/03-sar/raise.sar.analyze.md`
  - Frontmatter con handoffs
  - Outline con pasos Jidoka

- [ ] **A2.2** Implementar pipeline LLM por fases
  - Phase 0: DETECT - clasificar proyecto
  - Phase 1: SCAN - analizar estructura y patrones
  - Phase 2: DESCRIBE - generar documentacion
  - Phase 3: GOVERN - extraer reglas y grafo

- [ ] **A2.3** Crear prompts estructurados por fase
  - Secciones esperadas en cada prompt
  - Schemas de output inline
  - Ejemplos few-shot

- [ ] **A2.4** Implementar gates de validacion
  - Schema validation post-cada fase
  - Verificacion de campos requeridos
  - Confidence scores presentes

- [ ] **A2.5** Implementar context management
  - Chunking de archivos grandes
  - Purging de contexto entre fases
  - Seleccion de archivos relevantes

- [ ] **A2.6** Testear con stacks reales
  - TypeScript/Node project
  - Python/FastAPI project
  - PHP project (si disponible)

**Criterio de completitud:**
- Comando ejecuta exitosamente en 3+ stacks diferentes
- Outputs pasan validacion de schema
- Confidence scores presentes en todas las reglas

**Dependencias:**
- A1 completado
- Acceso a codebases de prueba

---

### Fase A3: CLI `raise get rules`

**Duracion estimada**: 1 semana
**Objetivo**: Implementar la interfaz de query de reglas

**Tareas:**

- [ ] **A3.1** Implementar query por tarea
  - `--task "implement user service"`
  - Matching semantico de reglas relevantes

- [ ] **A3.2** Implementar query por scope
  - `--scope "src/services/"`
  - `--file "src/services/UserService.ts"`
  - Filtering por path patterns

- [ ] **A3.3** Implementar filter por confidence
  - `--min-confidence 0.80`
  - `--include-all` para todo

- [ ] **A3.4** Implementar output MVC
  - Formato YAML por default
  - `--format json` option
  - primary_rules, context_rules, warnings, graph_context

- [ ] **A3.5** Integracion con Claude Code
  - Skill invocable desde agente
  - Context injection automatico

**Criterio de completitud:**
- CLI funciona con todos los flags documentados
- Output MVC contiene todas las secciones esperadas
- Integracion con Claude Code verificada

**Dependencias:**
- A2 completado (necesita reglas extraidas para probar)

---

### Fase A4: Documentacion & Launch

**Duracion estimada**: 1 semana
**Objetivo**: Preparar para publicacion open source

**Tareas:**

- [ ] **A4.1** Guia de uso SAR Open Core
  - Getting started (5 min)
  - Workflow completo
  - Troubleshooting comun

- [ ] **A4.2** Ejemplos por stack
  - TypeScript/React example
  - Python/FastAPI example
  - Generic example

- [ ] **A4.3** Best practices para validacion humana
  - Como revisar reglas extraidas
  - Cuando ajustar confidence
  - Como agregar excepciones

- [ ] **A4.4** README y getting started
  - Instalacion
  - Primer uso
  - Links a documentacion completa

- [ ] **A4.5** Publicacion
  - Preparar repo para open source
  - Licencia (determinar cual)
  - Anuncio/blog post

**Criterio de completitud:**
- Un usuario nuevo puede ejecutar SAR en 15 minutos
- Documentacion cubre los casos de uso principales
- Repo listo para publicacion

**Dependencias:**
- A3 completado

---

## Track B: Licensed (Post-Validacion)

> **Nota**: Track B inicia despues de validar Open Core con usuarios reales.

### Fase B1: Pipeline Determinista

**Duracion estimada**: 3 semanas

**Tareas:**
- [ ] Implementar `phase0-detect.sh` (determinista)
- [ ] Implementar `phase1-scan.sh` (ast-grep, ripgrep)
- [ ] JSON Schema para `project-profile.yaml`
- [ ] JSON Schema para `scan-report.json`
- [ ] Evidencia con file:line references

### Fase B2: LLM Synthesis Mejorada

**Duracion estimada**: 2 semanas

**Tareas:**
- [ ] LLM recibe datos estructurados de Phase 0-1
- [ ] architecture-as-found.md generation
- [ ] conventions-discovered.md generation
- [ ] .cursorrules automatico

### Fase B3: Observabilidad & Enterprise

**Duracion estimada**: 2 semanas

**Tareas:**
- [ ] Dashboard de gobernanza
- [ ] CI/CD integrations (GitHub Actions, GitLab CI)
- [ ] Multi-repo governance
- [ ] Audit logs

### Fase B4: Graph Intelligence

**Duracion estimada**: 2 semanas

**Tareas:**
- [ ] Algoritmo de MVC traversal optimizado
- [ ] Deteccion de conflictos automatica
- [ ] Confidence propagation en edges
- [ ] Drift detection

---

## Criterio de Transicion A → B

Track B inicia cuando Open Core demuestra:

| Criterio | Target | Medicion |
|----------|--------|----------|
| Proyectos activos | 10+ | Repos con SAR ejecutado |
| Precision validada | >70% | Feedback de usuarios |
| Interes enterprise | 3+ empresas | Expresiones de interes |
| Feedback consolidado | Documento | Limitaciones identificadas |

---

## Open Questions

### Decisiones Pendientes

1. **Donde vive el rule store?**
   - Opcion A: `.raise/rules/` en el repo del proyecto
   - Opcion B: Repo separado de gobernanza
   - Opcion C: Hibrido (base + overrides)
   - **Recomendacion preliminar**: Opcion A para Open Core, Opcion C para Licensed

2. **Como se versionan las reglas?**
   - Opcion A: Semver por regla individual
   - Opcion B: Version del rule set completo
   - Opcion C: Git tags
   - **Recomendacion preliminar**: Opcion A con version en YAML

3. **Como se resuelven conflictos entre reglas?**
   - Opcion A: Prioridad explicita
   - Opcion B: Scope mas especifico gana
   - Opcion C: Requiere resolucion humana
   - **Recomendacion preliminar**: Opcion B con fallback a C

4. **Como se integra con CI/CD?** (Licensed)
   - Opcion A: Gate que bloquea
   - Opcion B: Warning que reporta
   - Opcion C: Autofix que corrige
   - **Recomendacion preliminar**: Opcion B por default, A configurable

5. **Como evoluciona el grafo?**
   - Opcion A: Edges manuales solamente
   - Opcion B: Inferencia automatica de relaciones
   - Opcion C: Validacion de consistencia
   - **Recomendacion preliminar**: Opcion A para MVP, B para futuro

### Para Resolver en A1

- [ ] Estructura exacta de `rule-schema.json`
- [ ] Campos opcionales vs requeridos
- [ ] Formato de ejemplos (inline code vs file reference)

### Para Resolver en A2

- [ ] Estrategia de chunking para codebases grandes
- [ ] Limite de archivos a analizar
- [ ] Handling de binarios y assets

---

## Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigacion |
|--------|--------------|---------|------------|
| LLM inconsistencia | Alta | Medio | Schemas estrictos, validation gates |
| Costo de tokens alto | Media | Medio | Context purging, chunking |
| Baja adopcion Open Core | Media | Alto | Marketing, ejemplos, facilidad de uso |
| Competencia (BMAD) | Baja | Medio | Diferenciacion por gobernanza |

---

## Changelog

| Version | Fecha | Cambios |
|---------|-------|---------|
| 1.0.0 | 2026-01-28 | Documento inicial separado de Solution Vision |

---

## Siguiente Accion

**Iniciar Fase A1**: Finalizar JSON Schemas para regla unitaria y grafo.

Primer entregable: `rule-schema.json` con ejemplos de validacion.

---

*Este documento define el "cuando" y los detalles tacticos. Para el "que" y "por que", ver [Solution Vision](./solution-vision.md).*
