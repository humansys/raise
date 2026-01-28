# SAR Component - Research & Specifications

**SAR = Software Architecture Reconstruction**

Este directorio contiene toda la documentacion de research y especificaciones para el componente SAR de RaiSE.

## Vision General

SAR es el componente que:
1. **Extrae** patrones y convenciones de codebases brownfield
2. **Representa** esas convenciones como reglas en un grafo de conocimiento
3. **Entrega** el Minimum-Viable Context (MVC) a agentes LLM

## Estrategia de Producto

SAR sigue un modelo **Open Core**:

| Tier | Caracteristicas | Target |
|------|-----------------|--------|
| **Open Core** (Free) | SAR no-determinista, stack-agnostico, metodologia completa | Developers, equipos pequenos |
| **Licensed** (Paid) | SAR determinista, pipeline observable, integraciones enterprise | Empresas, equipos grandes |

El Open Core usa el patron **"Deterministic Rails, Non-Deterministic Engine"**: workflow estructurado (spec-kit harness) + LLM synthesis (BMAD patterns).

## Documentos

### Core (Solution)

| Documento | Proposito | Status |
|-----------|-----------|--------|
| [solution-vision.md](./solution-vision.md) | Vision estrategica del componente (v1.0.0) | Aprobado |
| [solution-roadmap.md](./solution-roadmap.md) | Roadmap tactico y fases de implementacion | Activo |

### Research

| Documento | Proposito | Status |
|-----------|-----------|--------|
| [semantic-density/](./semantic-density/) | Formatos de representacion de reglas | Completado |

### Research Relacionado (otros directorios)

| Documento | Proposito |
|-----------|-----------|
| [../deterministic-rule-extraction/](../deterministic-rule-extraction/) | Patrones de extraccion determinista |
| [../rule-extraction-alignment/](../rule-extraction-alignment/) | Alineacion de extraccion de reglas |
| [../bmad-brownfield-analysis/](../bmad-brownfield-analysis/) | Analisis de codebase brownfield (BMAD patterns) |
| [../speckit-critiques/](../speckit-critiques/) | Analisis de spec-kit (harness determinista) |

## Conceptos Clave

### Regla Unitaria
Documento YAML+Markdown auto-contenido que representa una convencion o patron.

### Grafo de Conocimiento
Estructura que conecta reglas con relaciones semanticas:
- `requires` - dependencia
- `conflicts_with` - exclusion mutua
- `supersedes` - deprecacion
- `related_to` - informacional

### Minimum-Viable Context (MVC)
Conjunto minimo de reglas + contexto relacional necesario para que un agente complete una tarea.

## Roadmap

### Track A: Open Core (Prioridad)
- [ ] A1: Foundation - Schemas y templates de output
- [ ] A2: Comando `raise.sar.analyze` (no-determinista)
- [ ] A3: CLI `raise get rules`
- [ ] A4: Documentacion y launch open source

### Track B: Licensed (Post-validacion Open Core)
- [ ] B1: Pipeline determinista (ast-grep, ripgrep)
- [ ] B2: LLM synthesis mejorada
- [ ] B3: Observabilidad y enterprise features
- [ ] B4: Graph intelligence avanzado

Ver [solution-roadmap.md](./solution-roadmap.md) para detalles completos.

## Open Questions

Ver seccion "Open Questions" en [solution-roadmap.md](./solution-roadmap.md).

## Archivo

| Documento | Nota |
|-----------|------|
| [solution-vision-sar.md](./solution-vision-sar.md) | Version anterior (v0.3.0) - ahora separado en vision + roadmap |
