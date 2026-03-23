# Dev Environment Setup — raise-commons

> Internal guide for HumanSys maintainers. Not for external contributors.

---

## Prerequisites

| Tool | Version | Install |
|------|---------|---------|
| Miniconda / Miniforge | any | https://docs.conda.io/en/latest/miniconda.html |
| uv | 0.10+ | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Git | any | system package manager |
| Python | 3.12+ | via conda (managed per env) |
| acli | 1.3+ | ver sección **Instalar acli** abajo |

---

## Workspace Structure

```
raise-commons/                  ← workspace root (raise-cli package)
├── pyproject.toml              ← uv workspace root + hatchling build
├── src/raise_cli/              ← CLI source
├── src/raise_core/             ← core library (bundled in raise-cli wheel)
└── packages/
    ├── raise-core/             ← workspace member, editable en rai-dev
    ├── raise-pro/              ← enterprise adapters: Jira, Confluence
    └── raise-server/           ← MCP server, dev-only dependency
```

---

## Environments

| | `base` (conda) | `rai-dev` (conda) | `.venv` (uv) |
|--|--|--|--|
| Python | 3.13 | 3.12 | 3.12 |
| Purpose | sistema `rai` PyPI estable | desarrollo + enterprise features | tests, linting, CI |
| raise-cli | PyPI wheel | editable ✓ (raise-commons source) | editable ✓ |
| raise-pro | ✗ | editable ✓ | via extras |
| raise-server | ✗ | editable ✓ | via extras |

**Rol de cada env:** `base` replica lo que tiene un usuario final de PyPI. `rai-dev` apunta siempre al source de raise-commons — cualquier cambio en el código es visible inmediatamente, sin reinstalar.

---

## Setup desde cero

### 1. Clonar

```bash
git clone <repo-url> ~/Documents/raise-commons
cd ~/Documents/raise-commons
```

### 2. Crear `rai-dev` — env de desarrollo completo

```bash
conda create -n rai-dev python=3.12 -y
conda run -n rai-dev pip install -e . -e packages/raise-pro -e packages/raise-server
```

**Por qué el orden importa:** instalar `.` primero (raise-cli editable desde source), luego los workspace members. `raise-pro` y `raise-server` no están en PyPI — deben instalarse como editable locales.

> **Nota (Miniconda fresh install):** Si `conda create` falla con error de TOS:
> ```bash
> conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main
> conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r
> ```

### 3. Instalar en `base` (produce el comando `rai` del sistema)

```bash
pip install raise-cli
```

Base usa la versión estable de PyPI, **sin** raise-pro. Replica la experiencia del usuario final.

### 4. Crear `.venv` con uv (para CI y lockfile)

```bash
uv sync
```

### 5. Exponer `rai` en el sistema

```bash
ln -sf ~/miniconda3/bin/rai ~/.local/bin/rai
# confirmar que ~/.local/bin está en PATH
```

### 6. Instalar acli (Atlassian CLI — requerido para `rai backlog -a jira`)

**Linux x86-64:**
```bash
curl -LO "https://acli.atlassian.com/linux/latest/acli_linux_amd64/acli"
chmod +x ./acli
sudo install -o root -g root -m 0755 acli /usr/local/bin/acli
rm ./acli
```

**Linux ARM64:**
```bash
curl -LO "https://acli.atlassian.com/linux/latest/acli_linux_arm64/acli"
chmod +x ./acli
sudo install -o root -g root -m 0755 acli /usr/local/bin/acli
rm ./acli
```

**macOS:**
```bash
brew install atlassian/tap/acli
```

**Windows:** ver https://developer.atlassian.com/cloud/acli/guides/install-windows/

### 7. Autenticar acli

```bash
acli jira auth login
# Sigue el flujo — abre browser, selecciona humansys.atlassian.net
```

Verifica:
```bash
acli jira auth status
# → ✓ Authenticated · Site: humansys.atlassian.net
```

### 8. Configurar integraciones

Estos archivos viven en `.raise/` y **no están en el repo** — cada dev los crea localmente.

**Jira — `.raise/jira.yaml`:**

```yaml
default_instance: humansys

instances:
  humansys:
    site: humansys.atlassian.net
    email: tu@humansys.ai
    projects: [RAISE, RTEST]

projects:
  RAISE:
    instance: humansys
    name: RAISE
    category: Development
    board_type: kanban

workflow:
  status_mapping:
    backlog: 11
    selected: 21
    in-progress: 31
    done: 41
```

> Copia de otro dev o pide el template. Cambia solo `email` y los proyectos que uses.

**Confluence — `.raise/confluence.yaml`:**

```yaml
space_key: RAIDOC
```

Solo necesita el space key. El adapter conecta a través de los MCP tools de Claude Code — no requiere config de servidor adicional.

**Page tracking — `.raise/confluence-pages.yaml`:**

Se crea automáticamente al publicar por primera vez (`rai docs publish`). Mapea artifact types a page IDs para upsert automático. No requiere config manual.

### 9. Verificar todo

```bash
rai --version                                                         # raise-cli PyPI en base
~/miniconda3/envs/rai-dev/bin/rai --version                          # raise-cli editable desde source
~/miniconda3/envs/rai-dev/bin/rai adapter list                       # debe mostrar jira + confluence
~/miniconda3/envs/rai-dev/bin/rai backlog get RAISE-608 -a jira      # smoke test Jira
~/miniconda3/envs/rai-dev/bin/rai docs search "setup" -t confluence  # smoke test Confluence
uv run pytest --tb=short                                              # tests
```

---

## Migración desde config anterior (MCP Jira)

Si ya tenías el setup anterior (antes de S494), el adapter de Jira cambió de MCP a ACLI.

### Qué cambió

| | Antes (≤ S494) | Ahora (S494+) |
|--|----------------|----------------|
| Adapter Jira | `mcp_jira` (MCP server) | `acli_jira` (ACLI subprocess) |
| Requisito | mcp-atlassian server corriendo | binario `acli` en PATH |
| Config Jira | `.raise/mcp/atlassian.yaml` | `.raise/jira.yaml` (sin cambios) |
| Confluence | `mcp_confluence` (MCP) | `mcp_confluence` (MCP) — **sin cambios** |

### Pasos

**1. Actualizar el código:**
```bash
git pull --rebase
```

**2. Reinstalar raise-pro en rai-dev** (los entry points stale requieren force-reinstall):
```bash
~/miniconda3/envs/rai-dev/bin/pip install --force-reinstall -e packages/raise-pro
```

**3. Instalar acli** — ver paso 6 del setup.

**4. Autenticar acli** — ver paso 7. El api_token que tenías para MCP **no se reutiliza** — acli maneja su propia auth.

**5. Verificar:**
```bash
acli jira auth status
~/miniconda3/envs/rai-dev/bin/rai backlog get RAISE-1 -a jira
```

**6. El MCP de Atlassian (si lo tenías configurado):**
- Sigue siendo necesario para Confluence (`rai docs`).
- Ya no es necesario para Jira (`rai backlog`).
- No hay nada que borrar — el adapter `mcp_jira` simplemente ya no existe en el código.

---

## Cómo resuelve `rai`

```
rai
  → ~/.local/bin/rai           (symlink)
    → ~/miniconda3/bin/rai     (script, shebang: ~/miniconda3/bin/python3.13)
    → raise-cli PyPI en base
```

**Quirk importante:** `conda run -n rai-dev rai` resuelve a `~/.local/bin/rai` (base) porque
`~/.local/bin` tiene precedencia en PATH sobre los bins del env. Para usar el binario de rai-dev:

```bash
~/miniconda3/envs/rai-dev/bin/rai --version
```

---

## Qué comando usar

| Situación | Comando |
|-----------|---------|
| Uso diario, cualquier proyecto | `rai ...` |
| Desarrollo raise-commons | `~/miniconda3/envs/rai-dev/bin/rai ...` |
| Jira / Confluence | `~/miniconda3/envs/rai-dev/bin/rai backlog -a jira` |
| Tests / linting | `uv run pytest` / `uv run ruff check .` |
| Simular experiencia usuario PyPI | `rai ...` (base, sin raise-pro) |

---

## Recomendación: CLAUDE.md global para Claude Code

Si usas Claude Code (claude-code CLI), agrega esto a `~/.claude/CLAUDE.md` para que Claude sepa
qué binario usar sin que tengas que indicarlo en cada sesión:

```markdown
## Tool Preferences

### raise-cli (`rai`)
- Para **raise-commons** (desarrollo): `/home/<tu-usuario>/miniconda3/envs/rai-dev/bin/rai`
  — env rai-dev tiene editable install del source + raise-pro.
  `conda run -n rai-dev rai` NO funciona (resuelve a `~/.local/bin/rai` base por precedencia de PATH).
- Para **producción / otros proyectos**: `~/.local/bin/rai`
  — base python3.13 con versión PyPI estable. raise-pro NO instalado en base.
```

> Ajusta `<tu-usuario>` a tu path real.

---

## Workflow diario

```bash
uv run pytest                   # tests
uv run ruff check .             # lint
uv run ruff format .            # format  ← correr ANTES de pyright
uv run pyright src/             # type check  ← siempre después de format
```

> `ruff format` puede desplazar comentarios `# type: ignore` al partir líneas largas,
> introduciendo nuevos errores de pyright. Siempre correr pyright después de format (PAT-F-044).

---

## Actualizar después de `git pull`

Los editable installs de rai-dev reflejan cambios de código inmediatamente. Algunos cambios sí requieren reinstalar:

- Nuevo entry point en `pyproject.toml` (adapters, gates, hooks)
- Cambio en `packages/raise-pro/pyproject.toml` o `packages/raise-server/pyproject.toml`

```bash
# Si cambiaron deps en pyproject.toml raíz:
uv sync
~/miniconda3/envs/rai-dev/bin/pip install -e . -e packages/raise-pro -e packages/raise-server

# Si solo cambió raise-pro (entry points stale):
~/miniconda3/envs/rai-dev/bin/pip install --force-reinstall -e packages/raise-pro
```

---

## Troubleshooting

**`rai backlog -a jira` → "ACLI binary not found"**
Instalar `acli` — ver sección **Instalar acli** arriba.

**`rai backlog -a jira` → "PM adapter 'jira' not found"**
raise-pro no instalado en rai-dev, o entry points stale:
```bash
~/miniconda3/envs/rai-dev/bin/pip install --force-reinstall -e packages/raise-pro
```

**`rai backlog -a jira` → "unauthorized"**
```bash
acli jira auth login
```

**`acli jira auth status` muestra autenticado, pero `rai backlog` falla de todas formas**
Estás usando el binario de base (`~/.local/bin/rai`) en lugar de rai-dev:
```bash
~/miniconda3/envs/rai-dev/bin/rai backlog -a jira ...
```

**`rai docs -t confluence` → error de conexión**
El MCP server de Atlassian para Confluence no está corriendo. Verificar config en `.raise/mcp/`.

**`rai` returns wrong version after code change**
Not possible with editable installs — source is read directly. If version string is wrong,
it's defined in `pyproject.toml` and requires a manual bump.

**`uv sync` fails with workspace member errors**
Some packages may lack a `pyproject.toml`. Check `packages/` for incomplete members.

**`snyk monitor` falla (PAT-F-043)**
uv venvs no incluyen pip por diseño:
```bash
uv pip install pip
pip freeze | grep -v '^-e' > req.txt
snyk monitor --file=req.txt --command=.venv/bin/python --package-manager=pip \
  --org=aquileslazaroh --project-name=raise-commons
```
