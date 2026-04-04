# RaiSE Happy Path — Guía del Desarrollador

> Referencia completa del flujo de trabajo con RaiSE.
> Generado a partir de sesión de onboarding, 2026-02-12.

---

## Prerrequisitos

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) o pip
- [Claude Code](https://claude.ai/claude-code) CLI instalado y configurado

```bash
# Instalar raise-cli (alpha — requiere flag --pre)
pip install --pre raise-cli
# o: uv pip install --prerelease=allow raise-cli

# Verificar
rai --help
```

---

## Fase 0: Configuración del Proyecto

### Greenfield (proyecto nuevo)

```bash
mkdir mi-proyecto && cd mi-proyecto
git init
rai init                              # Crea .raise/, manifest.yaml, estructura base
```

```
# En Claude Code:
/rai-welcome                          # Onboarding del desarrollador (perfil, grafo, context bundle)
/rai-project-create                   # Conversación guiada para llenar governance:
                                      #   -> vision.md, prd.md, guardrails.md, constitution
                                      #   -> ejecuta: rai memory build
```

### Brownfield (proyecto existente)

```bash
git clone <repo> && cd <repo>
rai init --detect                     # Detecta convenciones existentes
```

```
# En Claude Code:
/rai-welcome                          # Onboarding del desarrollador
/rai-project-onboard                  # Conversación guiada:
                                      #   -> Analiza lo que ya existe
                                      #   -> Llena governance con contexto descubierto
                                      #   -> ejecuta: rai memory build
```

### Descubrimiento de Codebase (opcional, recomendado para brownfield)

```
/rai-discover-start                   # Detecta tipo de proyecto, lenguajes, directorios
/rai-discover-scan                    # Extrae símbolos (clases, funciones, constantes)
/rai-discover-validate                # HITL: humano valida descripciones por nivel de confianza
/rai-discover-document                # Genera docs de arquitectura (C4 Context + Container)
                                      #   -> governance/architecture/modules/*.md
                                      #   -> ejecuta: rai memory build
```

---

## Fase 1: Ciclo de Sesión (cada bloque de trabajo)

```
/rai-session-start                    # Carga: perfil + estado previo + grafo + patrones
                                      # Rai interpreta contexto y propone foco
                                      # CLI: rai session start --context

    [TRABAJO — ver Fases 2-4]

/rai-session-close                    # Reflexión estructurada:
                                      #   -> Patrones descubiertos -> patterns.jsonl
                                      #   -> Correcciones de coaching -> developer.yaml
                                      #   -> Estado de trabajo -> session-state.yaml
                                      #   -> Registro de sesión -> personal/sessions/
                                      #   -> Telemetría -> personal/telemetry/
```

### Cuándo cerrar una sesión

- Después de terminar tu bloque de trabajo (1-3 horas típico)
- Al cambiar de contexto (diferente epic/story)
- Cuando Rai empiece a "olvidar" cosas (ventana de contexto llenándose)
- Siempre antes de cerrar Claude Code

---

## Fase 2: Ciclo de Epic (cuerpo de trabajo grande, 3-10 features)

```
/rai-epic-start                       # Inicializa directorio y scope del epic
                                      #   -> Scope commit
                                      #   -> Telemetría: rai memory emit-work epic --phase init

/rai-epic-design                      # Diseña el epic:
                                      #   -> Objetivo estratégico -> features
                                      #   -> ADRs para decisiones arquitectónicas
                                      #   -> Puede llamar /rai-research
                                      #   -> Escribe: work/stories/E-{N}/epic-design.md

/rai-epic-plan                        # Secuencia features:
                                      #   -> Milestones con dependencias
                                      #   -> Orden de ejecución de stories
                                      #   -> Escribe: work/stories/E-{N}/epic-plan.md

    [CICLOS DE STORY — Fase 3, repetir por story]

/rai-epic-close                       # Cierra el epic:
                                      #   -> Retrospectiva + métricas (planeado vs real)
                                      #   -> Actualiza backlog/tracker
                                      #   -> No hay merge de branch (epics son contenedores lógicos)
```

---

## Fase 3: Ciclo de Story (unidad entregable)

```
/rai-story-start                      # Crea branch: story/sN.M/nombre
                                      #   -> Siempre desde dev
                                      #   -> Scope commit: work/stories/S-NOMBRE/scope.md

/rai-story-design                     # Especificación lean (PAT-186: el diseño NO es opcional):
                                      #   -> Decisiones de integración
                                      #   -> Spec optimizada para humano + IA
                                      #   -> Puede llamar /rai-research para stories con UX
                                      #   -> Escribe: work/stories/S-NOMBRE/design.md

/rai-story-plan                       # Descompone en tareas atómicas:
                                      #   -> Dependencias entre tareas
                                      #   -> Criterios de verificación por tarea
                                      #   -> Escribe: work/stories/S-NOMBRE/plan.md

/rai-story-implement                  # Ejecuta tarea por tarea:
                                      #   -> Ciclos TDD (red -> green -> refactor)
                                      #   -> Gates de validación por tarea
                                      #   -> Commits atómicos por tarea completada

/rai-story-review                     # Retrospectiva post-implementación:
                                      #   -> Patrones descubiertos -> patterns.jsonl
                                      #   -> Calibración (estimado vs real) -> calibration.jsonl
                                      #   -> Escribe: work/stories/S-NOMBRE/retro.md

/rai-story-close                      # Cierra la story:
                                      #   -> Verificación final (tests, lint, types)
                                      #   -> Ejecuta /rai-docs-update (coherencia código<->docs)
                                      #   -> git merge --no-ff a dev
                                      #   -> git branch -D story/sN.M/nombre
                                      #   -> Actualiza scope del epic
```

### Artefactos de Story

```
work/stories/S-NOMBRE/
├── scope.md          <- /rai-story-start
├── design.md         <- /rai-story-design
├── plan.md           <- /rai-story-plan
└── retro.md          <- /rai-story-review
```

---

## Fase 4: Skills de Soporte (según se necesite)

| Skill | Cuándo | Qué hace |
|-------|--------|----------|
| `/rai-research` | Antes de ADRs, decisiones tecnológicas, stories con UX | Investigación epistemológicamente rigurosa con catálogo de evidencia |
| `/rai-debug` | Cuando se detecta un defecto (Jidoka: parar y corregir) | Análisis de causa raíz: 5 Porqués, Ishikawa, Gemba |
| `/rai-docs-update` | Se llama automáticamente en `/rai-story-close` | Sincroniza código con governance/architecture/modules/ docs |
| `/rai-framework-sync` | Después de crear/actualizar ADRs | Sincroniza backlog, glosario, ontología, visión |
| `/rai-skill-create` | Al agregar nueva automatización de flujo | Scaffoldea, valida e integra nuevos skills |

---

## Mantenimiento del Sistema

```bash
# Reconstruir grafo de conocimiento (después de cambios en governance/architecture)
rai memory build

# Validar integridad del grafo
rai memory validate

# Visualizar lo que Rai sabe
rai memory viz                        # Genera HTML interactivo

# Consultar memoria
rai memory query "patrones de velocidad"
rai memory context mod-session        # Contexto completo de un módulo

# Ver perfil del desarrollador
rai profile show

# Detectar drift arquitectónico
rai discover drift
```

---

## Modelo de Branches

```
main (releases estables)
  └── dev (desarrollo)
        ├── story/s18.1/nombre
        ├── story/s18.2/nombre
        ├── story/s18.3/nombre
        └── story/sBF-1/bugfix
```

Las stories siempre se crean desde y mergean a dev. Los epics son contenedores lógicos (directorio + Jira tracker), no branches.

---

## Mapa de Archivos

### Global (por máquina, viaja contigo)

```
~/.rai/
└── developer.yaml                    # Nombre, coaching, preferencias, nivel de confianza
```

### Por Proyecto

```
.raise/
├── manifest.yaml                     # Identidad del proyecto
├── rai/
│   ├── memory/
│   │   ├── patterns.jsonl            # Patrones compartidos (committed)
│   │   ├── MEMORY.md                 # Documentación de patrones (committed)
│   │   └── index.json                # Grafo derivado (gitignored, reconstruir con rai memory build)
│   └── personal/                     # Por desarrollador (gitignored, se crea al primer session close)
│       ├── sessions/index.jsonl      # Historial de sesiones
│       ├── session-state.yaml        # Estado de trabajo entre sesiones
│       ├── calibration.jsonl         # Calibración de estimaciones
│       ├── telemetry/signals.jsonl   # Métricas de flujo lean
│       └── last-diff.json            # Último diff de reconstrucción de grafo
├── katas/                            # Definiciones de proceso
├── gates/                            # Criterios de validación
├── templates/                        # Scaffolds de artefactos
└── skills/                           # Legacy (ahora en .claude/skills/)

.claude/skills/                       # 24 skills activos
governance/                           # Governance del proyecto (alimenta el grafo)
  └── architecture/modules/           # Un doc por módulo
framework/                            # Textbook público (constitución, glosario, conceptos)
work/stories/                         # Artefactos de trabajo (scope, design, plan, retro)
dev/                                  # Mantenimiento (parking-lot, decisiones)
# CLAUDE.local.md eliminado — contexto de sesión derivado de git (ADR-038)
```

---

## Referencia de Comandos CLI

| Comando | Escribe en | Lee de |
|---------|-----------|--------|
| `rai init` | estructura `.raise/` | — |
| `rai session start` | `~/.rai/developer.yaml` | perfil + grafo + session-state |
| `rai session close` | `personal/sessions/`, `personal/session-state.yaml` | sesión activa |
| `rai memory build` | `memory/index.json` | JSONL + governance/ + architecture/ + work/ |
| `rai memory add-pattern` | `memory/patterns.jsonl` | — |
| `rai memory emit-work` | `personal/telemetry/signals.jsonl` | — |
| `rai memory emit-calibration` | `personal/telemetry/signals.jsonl` | — |
| `rai memory query` | — (solo lectura) | `memory/index.json` |
| `rai memory context` | — (solo lectura) | `memory/index.json` |
| `rai memory validate` | — (solo lectura) | `memory/index.json` |
| `rai memory viz` | archivo HTML | `memory/index.json` |
| `rai discover scan` | stdout (JSON) | código fuente (AST) |
| `rai discover drift` | stdout | componentes + docs de arquitectura |
| `rai profile show` | — (solo lectura) | `~/.rai/developer.yaml` |
| `rai skill list` | — (solo lectura) | `.claude/skills/` |
| `rai skill validate` | — (solo lectura) | skill SKILL.md |

---

## Qué Manejan los Skills vs Qué Decides Tú

### Los skills manejan (90%):

- Proponer en qué trabajar (`/rai-session-start`)
- Llamar `/rai-docs-update` durante story close
- Pedir patrones y calibración durante review
- Ejecutar `rai memory build` después de discovery
- Emitir telemetría en transiciones de lifecycle

### Tú decides (10%):

- **Cuándo cerrar una sesión** — juicio basado en uso de contexto
- **Cuándo ejecutar `rai memory build`** — si editas docs de governance/ manualmente
- **Cuándo usar `/rai-research`** — story-design lo sugiere para UX pero no lo fuerza
- **Cuándo parar y debuggear** — Jidoka: tú notas el defecto, tú llamas `/rai-debug`

---

## Flujo Visual

```
[SETUP — una vez por proyecto]
rai init -> /rai-welcome -> /rai-project-create|onboard -> /rai-discover-*

[CADA BLOQUE DE TRABAJO]
/rai-session-start
|
|-- /rai-epic-start -> design -> plan
|   |
|   |-- /rai-story-start -> design -> plan -> implement -> review -> close
|   |-- /rai-story-start -> design -> plan -> implement -> review -> close
|   |-- /rai-story-start -> design -> plan -> implement -> review -> close
|   |
|   +-- /rai-epic-close
|
|-- /rai-research (cuando se necesite)
|-- /rai-debug (cuando se detecte defecto)
|
/rai-session-close
```

---

*Generado: 2026-02-12*
*Fuente: sesión de onboarding de raise-commons con Fer*
