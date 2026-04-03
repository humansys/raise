---
title: Referencia CLI
description: Referencia completa de todos los comandos del CLI de RaiSE — flags, opciones y ejemplos.
---

Referencia completa de la interfaz de línea de comandos `rai`.

## Opciones Globales

Estas opciones están disponibles en todos los comandos:

| Flag | Corto | Descripción |
|------|-------|-------------|
| `--version` | `-V` | Mostrar versión y salir |
| `--format` | `-f` | Formato de salida: `human`, `json` o `table` |
| `--verbose` | `-v` | Aumentar verbosidad (`-v`, `-vv`, `-vvv`) |
| `--quiet` | `-q` | Suprimir salida no-error |
| `--help` | | Mostrar ayuda y salir |

---

## Proyecto

### `rai init`

Inicializa un proyecto RaiSE en el directorio actual. Detecta el tipo de proyecto (greenfield o brownfield), crea `.raise/manifest.yaml` y configura la estructura del proyecto.

Con `--detect`, también analiza las convenciones de código y genera guardrails.

| Flag | Corto | Descripción |
|------|-------|-------------|
| `--name` | `-n` | Nombre del proyecto (por defecto: nombre del directorio) |
| `--path` | `-p` | Ruta del proyecto (por defecto: directorio actual) |
| `--detect` | `-d` | Detectar convenciones y generar `guardrails.md` |
| `--ide` | | Tipo de IDE: `claude` (por defecto), `antigravity`, `cursor` |

```bash
# Proyecto nuevo
rai init

# Proyecto con nombre
rai init --name mi-api

# Proyecto existente con detección de convenciones
rai init --detect

# Inicializar para Antigravity IDE
rai init --ide antigravity
```

---

## Sesión

### `rai session start`

Inicia una nueva sesión de trabajo. Incrementa el contador de sesiones y establece el estado de sesión activa. Verifica sesiones huérfanas (iniciadas pero no cerradas) y avisa si las encuentra.

Con `--context`, genera un bundle de contexto optimizado en tokens (~150 tokens) ensamblado desde tu perfil de desarrollador, estado de sesión y grafo de memoria.

| Flag | Corto | Descripción |
|------|-------|-------------|
| `--name` | `-n` | Tu nombre (requerido en la primera configuración) |
| `--project` | `-p` | Ruta del proyecto a asociar con esta sesión |
| `--agent` | | Tipo de agente (ej., `claude-code`, `cursor`). Por defecto: `unknown` |
| `--context` | | Generar bundle de contexto para consumo de IA |

```bash
# Primera configuración
rai session start --name "Alice" --project .

# Iniciar sesión con bundle de contexto
rai session start --project . --context

# Inicio simple
rai session start
```

### `rai session close`

Finaliza la sesión de trabajo actual. Con `--summary` o `--state-file`, realiza un cierre estructurado completo — registra sesión, patrones, correcciones y actualiza el estado.

| Flag | Corto | Descripción |
|------|-------|-------------|
| `--summary` | `-s` | Resumen de la sesión |
| `--type` | `-t` | Tipo de sesión (feature, research, maintenance, etc.) |
| `--pattern` | | Descripción del patrón a registrar |
| `--correction` | | Corrección de coaching observada |
| `--correction-lesson` | | Lección de la corrección |
| `--state-file` | | Archivo YAML con salida estructurada completa |
| `--session` | | ID de sesión a cerrar (ej., `SES-177`). Usa `RAI_SESSION_ID` como fallback |
| `--project` | `-p` | Ruta del proyecto |

```bash
# Cierre simple
rai session close

# Cierre con resumen
rai session close --summary "Implementé módulo de auth" --type feature

# Cierre con patrón aprendido
rai session close --summary "Refactoricé tests" --type maintenance \
  --pattern "Usar fixtures para setup de base de datos"
```

### `rai session context`

Carga secciones de contexto relevantes para la tarea. Se llama después de `rai session start --context` para cargar priming detallado para un tipo de trabajo específico. Secciones disponibles: `governance`, `behavioral`, `coaching`, `deadlines`, `progress`.

| Flag | Corto | Descripción |
|------|-------|-------------|
| `--sections` | | Nombres de secciones separados por coma |
| `--project` | `-p` | Ruta del proyecto |

```bash
# Trabajo en feature: principios de gobernanza + patrones de comportamiento
rai session context --sections governance,behavioral --project .

# Cerca de una fecha límite: verificar urgencia
rai session context --sections deadlines,progress --project .

# Primera sesión: cargar todo
rai session context --sections governance,behavioral,coaching --project .
```

---

## Memoria

### `rai graph query`

Busca en la memoria unificada conceptos relevantes. La memoria contiene todas las fuentes de contexto: gobernanza (principios, requisitos, términos), memoria (patrones, calibración, sesiones), skills (metadatos de workflow) y trabajo (epics, stories, decisiones).

| Flag | Corto | Descripción |
|------|-------|-------------|
| `--format` | `-f` | Formato de salida: `human`, `json` o `compact` |
| `--output` | `-o` | Archivo de salida (por defecto: stdout) |
| `--strategy` | `-s` | Estrategia de búsqueda: `keyword_search` o `concept_lookup` |
| `--types` | `-t` | Filtrar por tipos (separados por coma: `pattern`, `calibration`, `principle`, etc.) |
| `--edge-types` | | Filtrar por tipos de relación (separados por coma: `constrained_by`, `depends_on`, etc.) |
| `--limit` | `-l` | Número máximo de resultados (por defecto: 10) |
| `--index` | `-i` | Ruta del índice de memoria |

```bash
# Buscar por palabras clave
rai graph query "planning estimation"

# Filtrar solo patrones
rai graph query "testing" --types pattern,calibration

# Buscar concepto específico por ID
rai graph query "PAT-001" --strategy concept_lookup

# Salida en JSON
rai graph query "velocity" --format json
```

### `rai graph context`

Muestra el contexto arquitectónico completo de un módulo. Retorna el bounded context (dominio), capa arquitectónica, guardrails aplicables (restricciones) y dependencias del módulo.

| Flag | Corto | Descripción |
|------|-------|-------------|
| `--format` | `-f` | Formato de salida: `human` o `json` |
| `--index` | `-i` | Ruta del índice de memoria |

```bash
# Mostrar contexto del módulo de memoria
rai graph context mod-memory

# Salida en JSON
rai graph context mod-memory --format json
```

### `rai graph build`

Construye el índice de memoria unificado desde todas las fuentes: documentos de gobernanza, memoria (patrones, calibración, sesiones), seguimiento de trabajo (epics, stories), skills y componentes de discovery.

| Flag | Corto | Descripción |
|------|-------|-------------|
| `--output` | `-o` | Ruta para guardar el JSON del índice |

```bash
# Construir índice en ubicación por defecto
rai graph build

# Guardar en ubicación personalizada
rai graph build --output custom_index.json
```

### `rai graph validate`

Valida la estructura y relaciones del índice de memoria. Verifica ciclos en relaciones `depends_on`, tipos de relación válidos y que todos los targets de edges existan como nodos.

| Flag | Corto | Descripción |
|------|-------|-------------|
| `--index` | `-i` | Ruta al archivo JSON del índice |

```bash
# Validar índice por defecto
rai graph validate

# Validar archivo específico
rai graph validate --index custom_index.json
```

### `rai graph list`

Lista los conceptos en el índice de memoria. Muestra conceptos para inspección y debugging.

| Flag | Corto | Descripción |
|------|-------|-------------|
| `--format` | `-f` | Formato de salida: `human`, `json` o `table` |
| `--output` | `-o` | Archivo de salida (por defecto: stdout) |
| `--index` | `-i` | Ruta del índice de memoria |
| `--memory-only` / `--all` | | Mostrar solo tipos de memoria (pattern, calibration, session) o todos |

```bash
# Mostrar tabla resumen
rai graph list

# Mostrar solo patrones/calibraciones/sesiones
rai graph list --memory-only

# Exportar como JSON
rai graph list --format json --output memory.json
```

### `rai graph extract`

Extrae conceptos de archivos markdown de gobernanza. Si no se provee ruta, extrae de todas las ubicaciones estándar de gobernanza (`governance/prd.md`, `governance/vision.md`, `framework/reference/constitution.md`).

| Flag | Corto | Descripción |
|------|-------|-------------|
| `--format` | `-f` | Formato de salida: `human` o `json` |

```bash
# Extraer de todos los archivos de gobernanza
rai graph extract

# Extraer de archivo específico
rai graph extract governance/prd.md
```

### `rai pattern add`

Agrega un nuevo patrón a la memoria. Los patrones capturan aprendizajes del desarrollo — mejoras de proceso, descubrimientos técnicos, decisiones arquitectónicas.

| Flag | Corto | Descripción |
|------|-------|-------------|
| `--context` | `-c` | Palabras clave de contexto (separadas por coma) |
| `--type` | `-t` | Tipo de patrón: `codebase`, `process`, `architecture`, `technical` (por defecto: `process`) |
| `--from` | `-f` | Story/sesión donde se aprendió |
| `--scope` | `-s` | Alcance de memoria: `global`, `project`, `personal` (por defecto: `project`) |
| `--memory-dir` | `-m` | Ruta del directorio de memoria (sobreescribe scope) |

```bash
# Agregar patrón de proceso
rai pattern add "HITL before commits" -c "git,workflow"

# Agregar patrón técnico
rai pattern add "Use capsys for stdout tests" -t technical -c "pytest,testing"

# Agregar con referencia de origen
rai pattern add "BFS reuse across modules" -t architecture --from S2.3

# Agregar a scope personal
rai pattern add "My workflow preference" --scope personal
```

### `rai pattern reinforce`

Registra una señal de refuerzo para un patrón. Se llama al revisar una story para indicar si el patrón fue aplicado (`1`), no fue relevante (`0`), o fue contradicho (`-1`). El voto `0` (N/A) no cuenta hacia el total de evaluaciones — úsalo libremente para patrones irrelevantes.

| Flag | Corto | Descripción |
|------|-------|-------------|
| `--vote` | `-v` | Voto: `1` (aplicado), `0` (N/A — no contado), `-1` (contradicho) |
| `--from` | `-f` | ID de story para trazabilidad (ej., `RAISE-170`) |
| `--scope` | `-s` | Scope de memoria: `global`, `project`, `personal` (por defecto: `project`) |
| `--memory-dir` | `-m` | Ruta del directorio de memoria (reemplaza scope) |

```bash
# El patrón fue seguido durante la implementación
rai pattern reinforce PAT-001 --vote 1 --from S101

# El patrón no fue relevante para esta story
rai pattern reinforce PAT-002 --vote 0 --from S101

# El patrón fue contradicho
rai pattern reinforce PAT-003 --vote -1 --from S101
```

### `rai signal emit-calibration`

Agrega datos de calibración para una story completada. Registra estimación vs. duración real para análisis de velocidad.

| Flag | Corto | Descripción |
|------|-------|-------------|
| `--name` | | Nombre de la story (requerido) |
| `--size` | `-s` | Talla: `XS`, `S`, `M`, `L`, `XL` (requerido) |
| `--actual` | `-a` | Minutos reales (requerido) |
| `--estimated` | `-e` | Minutos estimados |
| `--sp` | | Story points |
| `--kata` / `--no-kata` | | Si se siguió el ciclo kata (por defecto: sí) |
| `--notes` | `-n` | Notas adicionales |
| `--scope` | `-s` | Alcance de memoria: `global`, `project`, `personal` |
| `--memory-dir` | `-m` | Ruta del directorio de memoria |

```bash
# Calibración básica
rai signal emit-calibration S3.5 --name "Skills Integration" -s XS -a 20

# Con estimación para cálculo de velocidad
rai signal emit-calibration S3.5 --name "Skills Integration" -s XS -a 20 -e 60

# Detalles completos
rai signal emit-calibration S3.5 --name "Skills Integration" -s XS -a 20 -e 60 --sp 2 -n "Hook-assisted"
```

### `rai signal emit-session`

Agrega un registro de sesión a la memoria. Las sesiones son específicas del desarrollador y siempre se escriben en el directorio personal.

| Flag | Corto | Descripción |
|------|-------|-------------|
| `--outcomes` | `-o` | Resultados de la sesión (separados por coma) |
| `--type` | `-t` | Tipo de sesión (por defecto: `story`) |
| `--log` | `-l` | Ruta al archivo de log de sesión |
| `--memory-dir` | `-m` | Ruta del directorio de memoria |

```bash
# Sesión básica
rai signal emit-session "S3.5 Skills Integration"

# Con resultados
rai signal emit-session "S3.5 Skills Integration" -o "Writer API,Hooks setup,CLI commands"

# Detalles completos
rai signal emit-session "S3.5 Skills Integration" -t story -o "Writer API,Hooks" \
  -l "dev/sessions/2026-02-02-s3.5.md"
```

### `rai signal emit-work`

Emite un evento de ciclo de vida de trabajo para análisis de flujo Lean. Registra ítems de trabajo (epics, stories) a través de fases normalizadas para habilitar análisis de lead time, wait time, WIP y cuellos de botella.

Fases: `design`, `plan`, `implement`, `review`.

| Flag | Corto | Descripción |
|------|-------|-------------|
| `--event` | `-e` | Tipo de evento: `start`, `complete`, `blocked`, `unblocked`, `abandoned` (por defecto: `start`) |
| `--phase` | `-p` | Fase: `design`, `plan`, `implement`, `review` (por defecto: `design`) |
| `--blocker` | `-b` | Descripción del bloqueante (para eventos `blocked`) |

```bash
# Ciclo de vida de epic
rai signal emit-work epic E9 --event start --phase design
rai signal emit-work epic E9 -e complete -p design

# Ciclo de vida de story
rai signal emit-work story S9.4 --event start --phase implement
rai signal emit-work story S9.4 -e complete -p implement

# Trabajo bloqueado
rai signal emit-work story S9.4 -e blocked -p plan -b "requisitos poco claros"
```

### `rai signal emit-session`

Emite un evento de sesión a telemetría. Registra la completitud de una sesión para aprendizaje local e insights.

| Flag | Corto | Descripción |
|------|-------|-------------|
| `--type` | `-t` | Tipo de sesión: `story`, `research`, `maintenance`, etc. (por defecto: `story`) |
| `--outcome` | `-o` | Resultado: `success`, `partial`, `abandoned` (por defecto: `success`) |
| `--duration` | `-d` | Duración de la sesión en minutos |
| `--stories` | `-f` | Stories trabajadas (separadas por coma) |

```bash
# Sesión completada básica
rai signal emit-session --type story --outcome success

# Con duración y stories
rai signal emit-session -t story -o success -d 45 -f S9.1,S9.2,S9.3
```

### `rai signal emit-calibration`

Emite un evento de calibración a telemetría. Registra estimación vs. real para seguimiento de velocidad. La velocidad se calcula automáticamente: `estimated / actual` (>1.0 = más rápido de lo estimado).

| Flag | Corto | Descripción |
|------|-------|-------------|
| `--size` | `-s` | Talla: `XS`, `S`, `M`, `L` (por defecto: `S`) |
| `--estimated` | `-e` | Duración estimada en minutos |
| `--actual` | `-a` | Duración real en minutos |

```bash
# Story completada más rápido de lo estimado
rai signal emit-calibration S9.4 --size S --estimated 30 --actual 15

# Story tomó más tiempo
rai signal emit-calibration S9.4 -s M -e 60 -a 90
```

### `rai graph viz`

Genera una visualización HTML interactiva del grafo de memoria. Crea un archivo HTML autocontenido con un grafo de fuerza dirigida D3.js. Los nodos están coloreados por tipo, son filtrables, tienen zoom y búsqueda.

| Flag | Corto | Descripción |
|------|-------|-------------|
| `--output` | `-o` | Ruta del archivo HTML de salida |
| `--index` | `-i` | Ruta del índice de memoria |
| `--open` / `--no-open` | | Abrir en navegador después de generar (por defecto: open) |

```bash
# Generar y abrir en navegador
rai graph viz

# Generar en ruta específica
rai graph viz --output graph.html

# Generar sin abrir
rai graph viz --no-open
```

### `rai memory generate`

:::caution[Deprecado]
`memory generate` está deprecado. Usa [`rai graph build`](#rai-graph-build) en su lugar. El grafo de memoria es ahora la fuente única de verdad — el contexto se entrega vía `rai session start --context`.
:::

---

## Discovery

Comandos para escanear, analizar y rastrear la arquitectura de tu codebase.

### `rai discover scan`

Escanea un directorio y extrae símbolos de código (clases, funciones, métodos, interfaces, docstrings de módulos). Soporta Python, TypeScript y JavaScript.

| Flag | Corto | Descripción |
|------|-------|-------------|
| `--language` | `-l` | Lenguaje: `python`, `typescript`, `javascript` (auto-detección si no se especifica) |
| `--output` | `-o` | Formato de salida: `human`, `json` o `summary` |
| `--pattern` | `-p` | Patrón glob para archivos |
| `--exclude` | `-e` | Patrones a excluir (se puede repetir) |

```bash
# Escanear directorio actual
rai discover scan

# Escanear solo archivos Python
rai discover scan src/ --language python

# Salida JSON para pipe a analyze
rai discover scan src/ -l python -o json

# Excluir tests
rai discover scan . --exclude "**/test_*" --exclude "**/__tests__/**"
```

### `rai discover analyze`

Analiza resultados de escaneo con scoring de confianza y agrupación por módulos. Toma la salida de scan y produce un análisis con auto-categorización, folding jerárquico y agrupación por módulos. Todo el análisis es determinístico — no requiere inferencia de IA.

| Flag | Corto | Descripción |
|------|-------|-------------|
| `--input` | `-i` | Ruta al JSON de resultado de scan (lee stdin si no se provee) |
| `--output` | `-o` | Formato de salida: `human`, `json` o `summary` |
| `--category-map` | `-c` | Archivo YAML con mapeos personalizados de ruta a categoría |

```bash
# Analizar desde archivo
rai discover analyze --input scan-result.json

# Pipe desde scan
rai discover scan src/ -l python -o json | rai discover analyze

# Solo resumen
rai discover analyze --input scan-result.json --output summary
```

### `rai discover build`

Construye el grafo unificado con componentes descubiertos. Lee componentes validados desde JSON y los integra en el grafo de contexto unificado, haciéndolos consultables vía `rai graph context`.

| Flag | Corto | Descripción |
|------|-------|-------------|
| `--input` | `-i` | Ruta al JSON de componentes validados |
| `--project-root` | `-r` | Directorio raíz del proyecto (por defecto: `.`) |
| `--output` | `-o` | Formato de salida: `human`, `json` o `summary` |

```bash
# Construir con archivo de entrada por defecto
rai discover build

# Construir con entrada personalizada
rai discover build --input my-components.json
```

### `rai discover drift`

Verifica drift arquitectónico contra el baseline de componentes. Compara código escaneado contra el baseline de componentes validados para identificar drift potencial (archivos en ubicaciones incorrectas, violaciones de convenciones de naming, documentación faltante).

Códigos de salida: `0` = sin drift, `1` = advertencias de drift encontradas.

| Flag | Corto | Descripción |
|------|-------|-------------|
| `--project-root` | `-r` | Directorio raíz del proyecto (por defecto: `.`) |
| `--output` | `-o` | Formato de salida: `human`, `json` o `summary` |

```bash
# Verificar proyecto completo
rai discover drift

# Verificar directorio específico
rai discover drift src/new_module/

# Salida en JSON
rai discover drift --output json
```

---

## Skills

### `rai skill list`

Lista todos los skills en el directorio de skills. Muestra skills agrupados por ciclo de vida con versión y descripción.

| Flag | Corto | Descripción |
|------|-------|-------------|
| `--format` | `-f` | Formato de salida: `human` o `json` |

```bash
rai skill list
```

### `rai skill validate`

Valida la estructura de un skill contra el schema de RaiSE. Verifica frontmatter, campos requeridos, secciones y convenciones de naming.

| Flag | Corto | Descripción |
|------|-------|-------------|
| `--format` | `-f` | Formato de salida: `human` o `json` |

```bash
# Validar todos los skills
rai skill validate

# Validar skill específico
rai skill validate .claude/skills/story-start/SKILL.md
```

### `rai skill scaffold`

Crea un nuevo skill desde plantilla. Genera un archivo `SKILL.md` con la estructura apropiada en `.claude/skills/<nombre>/`.

| Flag | Corto | Descripción |
|------|-------|-------------|
| `--lifecycle` | `-l` | Ciclo de vida: `session`, `epic`, `story`, `discovery`, `utility`, `meta` |
| `--after` | | Skill que debe ir antes (prerequisito) |
| `--before` | | Skill que debe ir después (siguiente) |
| `--format` | `-f` | Formato de salida: `human` o `json` |

```bash
# Crear nuevo skill de story
rai skill scaffold story-validate

# Con ciclo de vida y ordenamiento
rai skill scaffold story-validate --lifecycle story --after story-implement --before story-close
```

### `rai skill check-name`

Verifica un nombre propuesto de skill contra convenciones de naming. Valida el patrón `{dominio}-{acción}`, verifica conflictos con skills existentes o comandos CLI, y confirma el dominio de ciclo de vida.

| Flag | Corto | Descripción |
|------|-------|-------------|
| `--format` | `-f` | Formato de salida: `human` o `json` |

```bash
rai skill check-name story-validate
```

---

## Profile

### `rai profile show`

Muestra el perfil de desarrollador en formato YAML. Muestra el contenido de `~/.rai/developer.yaml`. Si no existe perfil, muestra un mensaje guía para crear uno.

```bash
rai profile show
```

---

## Base

### `rai base show`

Muestra información del paquete base de Rai. Muestra la versión del base incluido, contenidos (identidad, patrones, metodología) y si ha sido instalado en el proyecto actual.

```bash
rai base show
```

---

## Release

### `rai release list`

Listar releases del grafo de memoria. Muestra todos los nodos de release con su estado, fecha objetivo y epics asociados.

| Flag | Corto | Descripción |
|------|-------|-------------|
| `--project` | `-p` | Ruta raíz del proyecto (por defecto: `.`) |

```bash
rai release list
```
