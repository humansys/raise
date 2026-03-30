---
title: Configurar un Proyecto
description: Configura un proyecto RaiSE desde cero o integra un codebase existente — gobernanza, memoria y skills.
---

Esta guía cubre cómo configurar un proyecto RaiSE — ya sea que estés empezando desde cero (greenfield) o agregando RaiSE a un codebase existente (brownfield).

## Greenfield: Proyecto Nuevo

### Inicializar

```bash
mkdir mi-proyecto && cd mi-proyecto
git init
rai init --name mi-proyecto
```

Esto crea el directorio `.raise/`:

```
.raise/
├── manifest.yaml          # Metadatos del proyecto
└── rai/
    ├── memory/
    │   ├── patterns.jsonl  # Patrones aprendidos
    │   └── index.json      # Índice de memoria unificado
    ├── session-state.yaml  # Estado de sesión actual
    ├── identity/
    │   ├── core.md         # Identidad de Rai
    │   └── perspective.md  # Perspectiva de Rai
    └── personal/           # Tus datos privados (gitignored)
        ├── sessions/
        └── telemetry/
```

### Configurar Gobernanza

RaiSE crea un directorio `governance/` con plantillas:

```
governance/
├── constitution.md     # Tus principios
├── prd.md              # Tus requisitos
├── guardrails.md       # Tus reglas
├── backlog.md          # Tus ítems de trabajo
└── architecture/
    ├── system-context.md
    └── system-design.md
```

Llénalos con las especificidades de tu proyecto:

1. **Constitución** — ¿Cuáles son tus principios no negociables? "Type annotations en todo el código." "Tests antes de la implementación." Escribe 5-10 de estos.

2. **PRD** — ¿Qué estás construyendo? Define 3-5 requisitos a nivel de feature.

3. **Guardrails** — ¿Qué reglas debe seguir tu código? Usa MUST para lo no negociable, SHOULD para lo recomendado. Enlaza cada guardrail a un requisito.

No necesitas llenar todo de una vez. Empieza con unos pocos principios y guardrails. Agrega más a medida que aprendas qué importa para tu proyecto.

### Configurar Skills

Los skills viven en `.claude/skills/`. RaiSE viene con un conjunto estándar de skills de ciclo de vida. Para ver qué hay disponible:

```bash
rai skill list
```

Puedes crear skills específicos del proyecto:

```bash
rai skill scaffold mi-skill-custom --lifecycle utility
```

### Construir Memoria

Después de llenar los archivos de gobernanza, construye el índice de memoria:

```bash
rai graph build
```

Esto crea el knowledge graph unificado desde todos tus documentos de gobernanza, haciéndolos consultables y cargables en el contexto de tu IA.

### Primera Sesión

```bash
rai session start --project . --context
```

Tu partner de IA ahora tiene la gobernanza, memoria y skills de tu proyecto cargados. Estás listo para trabajar.

## Brownfield: Proyecto Existente

### Inicializar con Detección

Para codebases existentes, usa `--detect` para analizar convenciones:

```bash
cd proyecto-existente
rai init --detect
```

Esto hace todo lo que `rai init` hace, más:
- Escanea tu código fuente buscando patrones
- Identifica convenciones de código (naming, formato, imports)
- Detecta patrones de testing y frameworks
- Genera guardrails desde las convenciones detectadas

Revisa el `governance/guardrails.md` generado — es un punto de partida, no un evangelio. Ajústalo para que coincida con los estándares reales de tu equipo.

### Discovery Scan

Para un análisis más profundo, ejecuta el pipeline de discovery:

```bash
# Escanear código fuente
rai discover scan src/ --language python

# Analizar con scoring de confianza
rai discover scan src/ -l python -o json | rai discover analyze

# Verificar drift arquitectónico después
rai discover drift
```

Discovery extrae la estructura de tu codebase — clases, funciones, módulos — y construye un mapa de componentes. Esto alimenta el knowledge graph, dándole a tu partner de IA conciencia arquitectónica.

### Integrar con Workflow Existente

RaiSE agrega estructura junto a tus herramientas existentes:

- **Git**: RaiSE usa branching estándar de Git. Los branches de story se anidan bajo branches de epic, que se anidan bajo tu branch de desarrollo.
- **CI/CD**: RaiSE no toca tu pipeline. Los guardrails se ejecutan a nivel de IA, no a nivel de CI.
- **Editor**: Los skills se invocan a través de tu asistente de IA (ej. `/rai-story-start` en Claude Code). No se necesita plugin de editor.

## Referencia de Estructura del Proyecto

Un proyecto RaiSE completamente configurado luce así:

```
mi-proyecto/
├── .raise/                    # Runtime de RaiSE
│   ├── manifest.yaml
│   └── rai/
│       ├── memory/            # Memoria compartida (committed)
│       ├── personal/          # Datos privados (gitignored)
│       ├── session-state.yaml
│       └── identity/
├── .claude/
│   └── skills/                # Definiciones de skills
│       ├── session-start/
│       ├── story-start/
│       └── ...
├── governance/                # Gobernanza del proyecto
│   ├── constitution.md
│   ├── prd.md
│   ├── guardrails.md
│   └── architecture/
├── work/                      # Seguimiento de trabajo
│   └── epics/
│       └── e01-mi-epic/
│           ├── SCOPE.md
│           └── stories/
├── src/                       # Tu código
└── tests/                     # Tus tests
```

## Qué Commitear

| Directorio | ¿Commitear? | Por qué |
|-----------|-------------|---------|
| `.raise/rai/memory/` | Sí | Patrones y calibración compartidos |
| `.raise/rai/personal/` | No | Específico del desarrollador, gitignored |
| `.raise/manifest.yaml` | Sí | Metadatos del proyecto |
| `governance/` | Sí | Documentos de gobernanza compartidos |
| `.claude/skills/` | Sí | Definiciones de skills compartidas |
| `work/epics/` | Sí | Seguimiento de trabajo y retrospectivas |
