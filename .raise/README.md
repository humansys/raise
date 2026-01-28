# .raise/

> **RaiSE Methodology Artifacts** — Todo lo necesario para aplicar Lean Specification

---

## Estructura

```
.raise/
├── templates/        # Formatos de output (qué estructura tiene el entregable)
├── katas/            # Workflows (cómo crear el entregable)
├── gates/            # Validación (cómo saber si está bien)
├── commands/         # Comandos slash (automatización)
├── scripts/          # Scripts de soporte
└── README.md         ← estás aquí
```

## Filosofía

| Principio | Aplicación |
|-----------|------------|
| **MVS** (Minimum Viable Specification) | 4 secciones requeridas, resto opcional |
| **Lean Spec** | Ratio markdown:code < 1.5:1 |
| **Progressive Discovery** | Documentar cuando se necesita, no antes |
| **MVC** (Minimum Viable Context) | Solo contexto relevante para la tarea |

---

## Directorios

### `/templates/` — Formatos de Output

Estructuras lean para documentos. Ver [templates/README.md](./templates/README.md).

```
templates/
├── solution/solution-vision.md
├── architecture/architecture-overview.md
├── architecture/adr.md
├── tech/tech-design.md
├── tech/tech-design-feature.md
├── backlog/backlog.md
└── _legacy/                      # Templates anteriores (verbose)
```

### `/katas/` — Workflows

Procesos paso a paso para crear entregables. Cada kata define:
- Cuándo aplicar
- Pasos con verificación Jidoka
- Output esperado

```
katas/
├── README.md                     # Guía de katas lean
└── [categoria]/[kata].md
```

### `/gates/` — Validación

Criterios para validar entregables. Cada gate define:
- Checklist de validación
- Criterios pass/fail

```
gates/
├── gate-discovery.md
├── gate-vision.md
├── gate-design.md
├── gate-backlog.md
└── gate-estimation.md
```

### `/commands/` — Comandos Slash

Comandos ejecutables para Claude/Cursor. Organizados por flujo:

```
commands/
├── 01-onboarding/               # Setup inicial
│   ├── raise.1.analyze.code.md
│   ├── raise.rules.generate.md
│   └── raise.rules.edit.md
├── 02-projects/                 # Flujo de proyecto
│   ├── raise.1.discovery.md
│   ├── raise.2.vision.md
│   ├── raise.3.ecosystem.md
│   ├── raise.4.tech-design.md
│   ├── raise.5.backlog.md
│   ├── raise.6.estimation.md
│   └── raise.7.sow.md
└── 03-governance/               # SAR + raise.ctx (futuro)
```

### `/scripts/` — Scripts de Soporte

```
scripts/
├── bash/raise/                  # Scripts Bash
└── powershell/raise/            # Scripts PowerShell
```

---

## Jerarquía de Documentos

```
LEVEL 0: STRATEGY
├── Solution Vision        → templates/solution/solution-vision.md
└── Architecture Overview  → templates/architecture/architecture-overview.md
    └── ADRs              → templates/architecture/adr.md

LEVEL 1: DESIGN
└── Tech Design (System)   → templates/tech/tech-design.md

LEVEL 2: PLANNING
├── Backlog               → templates/backlog/backlog.md
└── Tech Design (Feature) → templates/tech/tech-design-feature.md
```

---

## Uso

### Para Nuevos Proyectos

Inyectar `.raise/` en un proyecto:

```bash
# Bash
bash .raise/scripts/bash/raise/transform-commands.sh <proyecto>

# PowerShell
powershell -File .raise/scripts/powershell/raise/transform-commands.ps1 -ProjectName <proyecto>
```

### Flujo Típico

```
/raise.1.discovery  → PRD
/raise.2.vision     → Solution Vision
/raise.4.tech-design → Tech Design
/raise.5.backlog    → Backlog
```

---

## Contribuir

1. **Templates**: Seguir formato MVS (4 secciones + opcionales colapsadas)
2. **Katas**: Seguir formato lean (Cuándo/Pasos/Output)
3. **Gates**: Checklist verificable, criterios objetivos
4. **Commands**: Referencias a `.specify/` (no `.raise/`)

---

*RaiSE Framework — Lean Specification v1.0*
