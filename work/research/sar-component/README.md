# RaiSE Governance Components

Este directorio contiene la documentacion de los componentes de gobernanza de RaiSE.

## Arquitectura

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    RAISE GOVERNANCE ARCHITECTURE                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌─────────────────────┐         ┌─────────────────────────────────┐   │
│  │        SAR          │         │          raise.ctx              │   │
│  │   (Extracción)      │         │      (Entrega de MVC)           │   │
│  ├─────────────────────┤         ├─────────────────────────────────┤   │
│  │ • Analiza codebase  │ ──────▶ │ • Lee rules + graph             │   │
│  │ • Extrae patrones   │ genera  │ • Traversal determinista        │   │
│  │ • Genera reglas     │  data   │ • Filtra por task/scope         │   │
│  │ • Construye grafo   │         │ • Entrega MVC al agente         │   │
│  ├─────────────────────┤         ├─────────────────────────────────┤   │
│  │ CLI: raise sar      │         │ CLI: raise ctx                  │   │
│  │ Frecuencia: Batch   │         │ Frecuencia: On-demand           │   │
│  └─────────────────────┘         └─────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

| Componente | Responsabilidad | Frecuencia |
|------------|-----------------|------------|
| **SAR** | Extraer patrones, generar reglas y grafo | Batch (cuando codebase cambia) |
| **raise.ctx** | Entregar MVC a agentes | On-demand (cada task) |

## Documentos

### Solution Visions

| Documento | Componente | Status |
|-----------|------------|--------|
| [solution-vision.md](./solution-vision.md) | SAR (Extracción) | Aprobado v1.1.0 |
| [solution-vision-context.md](./solution-vision-context.md) | raise.ctx (Entrega) | Borrador v1.0.0 |

### Roadmap

| Documento | Proposito | Status |
|-----------|-----------|--------|
| [solution-roadmap.md](./solution-roadmap.md) | Roadmap de implementacion | Activo |

### Research

| Documento | Proposito | Status |
|-----------|-----------|--------|
| [semantic-density/](./semantic-density/) | Formatos de representacion de reglas | Completado |

### Archivo

| Documento | Nota |
|-----------|------|
| [solution-vision-sar.md](./solution-vision-sar.md) | Version anterior combinada |

## Conceptos Clave

### SAR (Software Architecture Reconstruction)

- **Que hace**: Analiza codebase brownfield, extrae patrones, genera reglas
- **Output**: `.raise/rules/*.yaml`, `.raise/graph.yaml`
- **CLI**: `rai sar analyze [path]`
- **Tiers**: Open Core (LLM) / Licensed (determinista)

### raise.ctx (RaiSE Context)

- **Que hace**: Entrega Minimum-Viable Context a agentes
- **Input**: Query (task + scope) + datos de SAR
- **Output**: MVC (reglas + contexto + warnings)
- **CLI**: `rai ctx get --task "..." --scope "..."`
- **Caracteristica**: Siempre determinista

### Minimum-Viable Context (MVC)

Conjunto minimo de reglas + contexto relacional para una tarea:
- `primary_rules`: Reglas directamente aplicables
- `context_rules`: Reglas relacionadas (summaries)
- `warnings`: Conflictos, deprecaciones, low-confidence
- `graph_context`: Subgrafo relevante

### Data Store (`.raise/`)

Output de SAR, input de raise.ctx:
```
.raise/
├── rules/
│   └── *.yaml           # Reglas unitarias
├── graph.yaml           # Grafo de relaciones
├── conventions.md       # Documentacion human-readable
└── project-profile.yaml # Metadata del proyecto
```

## Roadmap

### Track A: Open Core (Prioridad)

| Fase | SAR | raise.ctx |
|------|-----|-----------|
| A1 | Schemas y templates | - |
| A2 | Comando `raise.sar.analyze` | - |
| A3 | - | CLI `rai ctx get` basico |
| A4 | Documentacion | Integracion con agentes |

### Track B: Licensed

| Fase | SAR | raise.ctx |
|------|-----|-----------|
| B1 | Pipeline determinista | - |
| B2 | LLM synthesis mejorada | Graph traversal completo |
| B3 | Observabilidad | Cache y optimizacion |

Ver [solution-roadmap.md](./solution-roadmap.md) para detalles.

## Quick Start (Futuro)

```bash
# 1. Ejecutar SAR para extraer reglas
raise sar analyze ./my-project

# 2. Obtener contexto para una tarea
raise ctx get --task "implement user service" --scope "src/services/"

# 3. O usar slash command en Claude Code
/raise.ctx
```

## Research Relacionado

| Directorio | Proposito |
|------------|-----------|
| [../bmad-brownfield-analysis/](../bmad-brownfield-analysis/) | Analisis de BMAD (benchmark) |
| [../speckit-critiques/](../speckit-critiques/) | Analisis de spec-kit (harness pattern) |
| [../deterministic-rule-extraction/](../deterministic-rule-extraction/) | Patrones de extraccion determinista |
