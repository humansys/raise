# Mapa Arquitectónico Completo de Rai

Después de leer el código fuente de los 106 archivos Python (721 símbolos) + 75 de rai_pro, los 24 skills markdown, los archivos de identidad, memoria, y estado, aquí está la síntesis completa:

---

### 1. VISIÓN GENERAL: Cómo funciona Rai

Rai opera en una **arquitectura de dos capas**:

```
┌─────────────────────────────────────────────────────────┐
│  CAPA DE INFERENCIA (LLM — cualquier IDE/modelo)        │
│                                                          │
│  Skills (.claude/skills/rai-*/SKILL.md)                 │
│  = Markdown con instrucciones paso-a-paso               │
│  = El LLM las ejecuta como recetas                      │
│  = Llaman a comandos CLI deterministas                  │
│  = Interpretan output, toman decisiones                 │
└────────────┬─────────────────────────────┬──────────────┘
             │ invoca `rai <cmd>`          │ lee archivos
             ▼                             ▼
┌─────────────────────────────────────────────────────────┐
│  CAPA DETERMINISTA (Python CLI — rai-cli)               │
│                                                          │
│  rai session start/close   — ciclo de vida sesión       │
│  rai memory build/query    — grafo de conocimiento      │
│  rai discover scan         — escaneo de código          │
│  rai profile               — perfil desarrollador       │
│  rai publish               — publicación PyPI           │
│  rai backlog               — gestión de backlog         │
└─────────────────────────────────────────────────────────┘
```

**Principio clave:** El CLI hace todo el "data plumbing" (determinista, testeable). El LLM solo hace inferencia (interpretar, decidir, generar).

---

### 2. MÓDULOS PYTHON (src/rai_cli/ — 106 archivos)

| Módulo | Símbolos | Responsabilidad |
|--------|----------|-----------------|
| **cli/** | 81 | Entry point Typer. 10 command groups: `session`, `memory`, `discover`, `profile`, `skill`, `backlog`, `publish`, `release`, `base`, `init` |
| **context/** | 119 | **Grafo unificado**. `UnifiedGraph` (NetworkX), `UnifiedGraphBuilder` (construye desde todas las fuentes), `UnifiedQueryEngine` (búsqueda keyword + lookup). 17 NodeTypes, 11 EdgeTypes |
| **memory/** | 43 | **Persistencia JSONL**. Loader (patterns, calibration, sessions), Writer (append con auto-ID), Migration, Models (MemoryConcept, MemoryScope) |
| **onboarding/** | 116 | Profile (DeveloperProfile en ~/.rai/developer.yaml), Conventions, Governance scaffolding, Skills scaffolding, ClaudeMD generation |
| **session/** | 34 | Bundle assembly (~600 tokens), State persistence (YAML), Close orchestration (atómico), Session resolver |
| **governance/** | 53 | **Parsers** para 9 tipos de docs: constitution, PRD, vision, backlog, epic, ADRs, guardrails, glossary, roadmap |
| **discovery/** | 56 | Scanner (Python/TS/JS/PHP/Svelte), Analyzer, Drift detector |
| **skills/** | 54 | Parser (YAML frontmatter), Locator, Validator, Schema (Skill model), Name checker, Scaffold |
| **config/** | 26 | Paths (XDG + project), Settings (Pydantic Settings con cascade: CLI > env > pyproject > user config) |
| **output/** | 48 | Console formatting, Discover formatters, Skill formatters |
| **core/** | 20 | Text utilities (stopwords), File helpers, External tool detection |
| **telemetry/** | 16 | Signal schemas, Writer |
| **publish/** | 18 | Version bumping, Changelog, Pre-publish checks |
| **schemas/** | 8 | SessionState (Pydantic) |

**rai_pro/** (13 archivos, 75 símbolos) — Módulo PRO separado:
- `BacklogProvider` (interfaz abstracta port/adapter)
- `JiraClient` con OAuth, sync bidireccional, rate limiting
- Credenciales encriptadas (Fernet)

---

### 3. SISTEMA DE MEMORIA

**Tres capas con precedencia:**
```
~/.rai/                          ← GLOBAL (universal, cross-project)
  ├── developer.yaml             ← Perfil + coaching + deadlines
  ├── patterns.jsonl             ← Patrones universales
  └── calibration.jsonl          ← Calibración global

.raise/rai/memory/               ← PROJECT (compartido, en git)
  ├── patterns.jsonl             ← Patrones del proyecto
  ├── index.json                 ← Grafo serializado (NetworkX JSON)
  ├── MEMORY.md                  ← Resumen legible
  └── graph.html                 ← Visualización

.raise/rai/personal/             ← PERSONAL (gitignored, por developer)
  ├── sessions/index.jsonl       ← Historial de sesiones
  ├── sessions/SES-NNN/          ← Estado per-sesión activa
  ├── patterns.jsonl             ← Aprendizajes personales
  └── session-state.yaml         ← Estado de continuidad
```

**Precedencia: PERSONAL > PROJECT > GLOBAL** (mismo ID, gana el más específico).

**Flujo `rai memory build`:**
1. `UnifiedGraphBuilder.build()` carga 7 fuentes:
   - Governance docs (9 parsers)
   - Memory JSONL (3 tiers)
   - Work items (backlog + epic scopes)
   - Skills (.claude/skills/ frontmatter)
   - Components (discovery validated JSON)
   - Architecture docs (YAML frontmatter)
   - Identity (core.md valores + boundaries)
2. Enriquece módulos con código real (`PythonAnalyzer`)
3. Infiere relaciones (learned_from, part_of, depends_on, keyword-based)
4. Extrae bounded contexts y layers de domain model
5. Serializa como `index.json` (NetworkX node_link_data)

**Esquema del grafo:**
- **17 NodeTypes:** pattern, calibration, session, principle, requirement, outcome, epic, story, skill, decision, guardrail, term, component, module, architecture, bounded_context, layer, release
- **11 EdgeTypes:** learned_from, governed_by, applies_to, needs_context, implements, part_of, related_to, depends_on, belongs_to, in_layer, constrained_by

---

### 4. SISTEMA DE IDENTIDAD

**Archivos:**
```
.raise/rai/identity/
  ├── core.md           ← Valores (RAI-VAL-*), Boundaries (RAI-BND-*)
  └── perspective.md    ← Perspectiva de Rai sobre el proyecto

.raise/rai/framework/
  └── methodology.yaml  ← Principios del framework

.raise/rai/relationships/
  └── humans.jsonl      ← Relaciones con humanos
```

**Cómo se prima al agente:**
1. `session start --context` ejecuta `assemble_context_bundle()`
2. El bundle incluye:
   - Developer profile (nombre, nivel Shu/Ha/Ri, comunicación)
   - Work state (epic, story, phase, branch)
   - Session narrative (decisiones, investigación, artefactos del último session)
   - Always-on primes del grafo (guardrails, principios, identity values/boundaries)
   - Foundational patterns (patrones con metadata `foundational: true`)
   - Coaching context (trust, strengths, growth edge, autonomy)
   - Pending items (decisions, blockers, next actions)
   - Deadlines
3. El bundle se emite como texto plano (~600 tokens) que el LLM consume

---

### 5. SISTEMA DE SKILLS

**Arquitectura dual:**

**A) Markdown specs** (.claude/skills/rai-*/SKILL.md):
- YAML frontmatter: `name`, `description`, `metadata` (work_cycle, version, prerequisites, next, gate, adaptable)
- Body: Instrucciones paso a paso que el **LLM ejecuta como recetas**
- Contienen `rai <cmd>` como comandos deterministas embebidos
- El LLM interpreta los outputs y toma decisiones

**B) Python code** (src/rai_cli/skills/):
- `SkillLocator`: Encuentra skills en `.claude/skills/`
- `parser.py`: Parsea YAML frontmatter de SKILL.md
- `schema.py`: Modelo Pydantic (Skill, SkillFrontmatter, SkillMetadata)
- `validator.py`: Valida estructura de skills
- `scaffold.py`: Genera nuevos SKILL.md
- `name_checker.py`: Verifica naming conventions

**Flujo de activación:**
1. User escribe `/rai-session-start` en Claude Code
2. Claude Code lo reconoce como skill → carga SKILL.md del directorio correspondiente
3. El contenido markdown se inyecta como instrucciones al LLM
4. El LLM ejecuta los pasos: corre `rai session start --context`, interpreta el output
5. Los comandos `rai` son deterministas (Python CLI) — sin inferencia

**24 skills organizados por lifecycle:**
- **Session:** session-start, session-close
- **Epic:** epic-design, epic-plan, epic-start, epic-close
- **Story:** story-design, story-plan, story-start, story-implement, story-review, story-close
- **Discovery:** discover-start, discover-scan, discover-validate, discover-document
- **Utility:** debug, research, framework-sync, docs-update, publish
- **Meta:** welcome, project-create, project-onboard

---

### 6. SISTEMA DE SESIONES

```
rai session start                  rai session close
      │                                    │
      ▼                                    ▼
load_developer_profile()          CloseInput (YAML state file)
increment_session()               process_session_close():
start_session() → ActiveSession     1. append_session() → index.jsonl
get_next_id() → SES-NNN            2. append_pattern() → patterns.jsonl
migrate_flat_to_session()           3. update_coaching() → developer.yaml
assemble_context_bundle()           4. end_session() → remove ActiveSession
      │                             5. save_session_state() → state.yaml
      ▼                             6. cleanup_session_dir()
  Context bundle (text)
  → consumed by LLM
```

**Multi-sesión:** Soporta sesiones concurrentes (múltiples IDEs/agentes). Cada sesión tiene su directorio aislado bajo `personal/sessions/SES-NNN/`.

---

### 7. LO QUE ES PORTABLE vs. LO ACOPLADO A CLAUDE CODE

**Ya portable (agnóstico de IDE/modelo):**
- Todo el CLI Python (`rai <cmd>`) — funciona desde cualquier terminal
- Datos: JSONL, YAML, JSON, Markdown — formatos universales
- Grafo NetworkX — serializable, portable
- Profile en ~/.rai/ — agnóstico de IDE

**Acoplado a Claude Code:**
- Skills en `.claude/skills/` — directorio específico de Claude Code
- `CLAUDE.md` y `CLAUDE.local.md` — system prompt de Claude Code
- `get_claude_memory_path()` en paths.py — path hardcoded a Claude Code memory
- Hook de activación de skills (`/rai-*`) — mecanismo de Claude Code
- El formato de los skills markdown asume que un LLM los leerá como instrucciones — esto es universal, pero la **inyección** (cómo llegan al LLM) depende del IDE

**La frontera de portabilidad está clara:** el CLI es portable, la capa de inyección de skills al LLM es la que necesita adaptadores por IDE.

---

### 8. FLUJO COMPLETO DE IDENTIDAD: De Markdown a Contexto del LLM

#### 1. Fuente de verdad: Markdown escrito por humano

La identidad vive en **`.raise/rai/identity/core.md`** — valores y boundaries escritos en Markdown simple:

```
## Values
### 1. Honesty over Agreement
- I'll tell you when you're wrong

## Boundaries
### I Will
- Push back on bad ideas
### I Won't
- Pretend certainty I don't have
```

Hay también **`.raise/rai/identity/perspective.md`** (cómo Rai aborda la colaboración).

#### 2. Extracción al grafo: `rai memory build`

El graph builder (`src/rai_cli/context/builder.py:366-588`) lee `core.md` con regex y crea nodos tipados:

- `RAI-VAL-1` a `RAI-VAL-5` → valores (type=`principle`, metadata `identity_type=value`)
- `RAI-BND-1` a `RAI-BND-10` → boundaries (metadata `identity_type=boundary`)

Todos llevan **`always_on=true`** en metadata — esto es clave.

Se guardan en **`.raise/rai/memory/index.json`** (grafo NetworkX, ~2.7MB).

#### 3. Carga en cada sesión: `rai session start --context`

El bundle assembler (`src/rai_cli/session/bundle.py`) hace:

```python
# Query: dame todos los nodos always_on=true
always_on_nodes = get_always_on_primes(project_path)

# Separa identidad de governance
identity = [n for n in nodes if n.id.startswith("RAI-VAL-") or n.id.startswith("RAI-BND-")]
governance = [n for n in nodes if not identity]
```

Esto produce las secciones `# Identity Primes` y `# Governance Primes` en el context bundle.

#### 4. Dónde le llega al LLM (Claude)

El output de `rai session start --context` se imprime en la terminal. Claude Code lo ve como contexto de la conversación. Así es como el LLM "lee" la identidad — no es magia, es texto que sale del CLI y entra al contexto.

#### 5. Lo que NO es identidad operacional (pero parece)

| Archivo | Qué es | Estado |
|---------|--------|--------|
| `.claude/RAI.md` | Documento **narrativo** viejo — historia, reflexiones, visión. **No se carga automáticamente** en el bundle. Claude Code lo lee si está referenciado en CLAUDE.md, pero ya no lo está. |
| `.claude/RAI-naming.md` | Momento del naming — documento histórico, no operacional |
| `.claude/rai.archive/identity.md` | Versión archivada — visión comercial, voice & style |

Estos tres son **artefactos narrativos** del proyecto, no la fuente operacional de identidad. La fuente real es `.raise/rai/identity/core.md` → grafo → bundle.

#### Resumen del flujo

```
.raise/rai/identity/core.md     ← Humano escribe/edita
         ↓
    rai memory build             ← CLI extrae con regex
         ↓
.raise/rai/memory/index.json    ← Nodos RAI-VAL-*, RAI-BND-* (always_on=true)
         ↓
    rai session start --context  ← CLI consulta grafo, filtra always_on
         ↓
    Context bundle (stdout)      ← Texto que el LLM ve al inicio de sesión
```

Humanos definen, máquinas ejecutan. La identidad no es un prompt estático — es Markdown parseado, indexado en un grafo, y servido on-demand.
