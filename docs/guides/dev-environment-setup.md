# Dev Environment Setup

Guía para instalar lo mínimo indispensable para trabajar con raise-cli.

**Si ya tienes instalaciones viejas** (conda, pipx, symlinks rotos), limpia primero con la [Guía de Limpieza](dev-environment-cleanup.md).

## Lo que necesitas (y SOLO esto)

| Herramienta  | Para qué                             | Cómo se instala   |
| ------------ | ------------------------------------- | ------------------ |
| Python 3.12+ | El lenguaje. Ya viene en Ubuntu/macOS | Sistema operativo  |
| uv           | Gestor de paquetes y entornos Python  | `curl` one-liner |
| git          | Control de versiones                  | Sistema operativo  |

Eso es todo. No necesitas conda, pyenv, asdf, ni nada más.

## Paso 1: Instalar uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Cierra y abre tu terminal. Verifica:

```bash
uv --version
```

**¿Qué es uv?** Un gestor de paquetes Python ultra-rápido (escrito en Rust). Reemplaza a pip, pipx, conda, pyenv y virtualenv — todo en uno. Es lo único que necesitas.

## Paso 2: Instalar raise-cli global (estable)

```bash
uv tool install raise-cli
```

Verifica:

```bash
rai --version        # → raise-cli version X.Y.Z (la última estable de PyPI)
which rai            # → ~/.local/bin/rai
```

**¿Qué hace `uv tool install`?**

1. Crea un entorno virtual aislado en `~/.local/share/uv/tools/raise-cli/`
2. Instala raise-cli y sus dependencias ahí dentro (no contamina nada)
3. Pone un ejecutable `rai` en `~/.local/bin/` que apunta a ese entorno

Resultado: tienes `rai` disponible en cualquier directorio, con la versión estable de PyPI.

## Paso 3: Setup de desarrollo (solo para contribuidores de raise-commons)

```bash
cd ~/Documents/raise-commons    # o donde tengas el repo clonado
uv sync                          # crea .venv y instala todo en modo editable
```

Verifica:

```bash
uv run rai --version    # → raise-cli version X.Y.Z-alpha (la versión de desarrollo)
```

**¿Qué hace `uv run`?** Ejecuta un comando usando el `.venv` del proyecto actual, no el `rai` global. Así puedes tener:

- `rai` → versión estable (para proyectos normales)
- `uv run rai` (dentro de raise-commons) → versión en desarrollo (tus cambios locales)

**¿Qué es `uv sync`?** Lee el `pyproject.toml` del proyecto, crea un `.venv`, e instala todo en modo "editable". Editable significa que cuando cambias el código fuente, los cambios se reflejan inmediatamente sin reinstalar nada.

### raise-pro (adapters de Jira, Confluence, etc.)

raise-pro es un paquete privado que no está en PyPI. Se instala **solo en el entorno de desarrollo** (raise-commons), no en el global.

`uv sync` ya lo instala automáticamente si está configurado como workspace member en `pyproject.toml`. Verifica que funciona:

```bash
uv run rai adapter list    # Debe mostrar: jira, confluence (además de filesystem)
uv run rai backlog search "test" -a jira -n 1    # Debe conectar a Jira
```

Si `rai adapter list` solo muestra `filesystem`, raise-pro no se instaló. Verifica que el workspace esté configurado:

```bash
uv sync --reinstall    # fuerza reinstalación de todos los paquetes
uv run rai adapter list    # verificar de nuevo
```

**Importante:** los comandos `rai docs` (Confluence) y `rai backlog` (Jira) solo funcionan con `uv run rai` dentro de raise-commons, no con el `rai` global. El global solo tiene el adapter `filesystem`.

## Resultado final

```
En cualquier directorio:
  $ rai --version
  raise-cli version 2.3.0          ← estable, de PyPI

En raise-commons:
  $ uv run rai --version
  raise-cli version 2.4.0a2        ← desarrollo, editable desde código fuente
```

## Troubleshooting

| Problema | Causa | Solución |
| --- | --- | --- |
| `rai: command not found` | `~/.local/bin` no está en tu PATH | Agrega `export PATH="$HOME/.local/bin:$PATH"` a tu `~/.bashrc` |
| `rai: cannot execute: required file not found` | uv tool linkó a un Python que ya no existe (conda borrado después de instalar) | `uv tool uninstall raise-cli && uv tool install raise-cli` |
| `uv run rai` da la misma versión que `rai` | No estás dentro del directorio de raise-commons, o falta el `.venv` | `cd raise-commons && uv sync` |
| `uv: command not found` | uv no instalado o terminal no recargada | Reinstala uv, o abre terminal nueva |
| `rai docs` o `rai backlog` da "adapter not found" | Estás usando el `rai` global (no tiene raise-pro) | Usa `uv run rai` dentro de raise-commons |

### Tests conocidos que fallan al clonar

Al correr `uv run pytest` en raise-commons, es posible que veas errores de collection en 2 tests de raise-pro:

```
ERROR packages/raise-pro/tests/rai_server/test_auth.py - ImportError: cannot import name 'OrgContext'
ERROR packages/raise-pro/tests/rai_server/test_db_models.py - ImportError: cannot import name 'ApiKey'
```

Estos son imports desactualizados en los tests de raise-server (los nombres de las clases cambiaron). **No son un problema de tu setup** — el resto de los 4630+ tests debe pasar. Si ves otros errores, ahí sí es tu instalación.

## Comandos útiles

```bash
# Ver qué tools tienes instaladas globalmente
uv tool list

# Actualizar raise-cli global a la última versión
uv tool upgrade raise-cli

# Desinstalar raise-cli global
uv tool uninstall raise-cli

# Reinstalar limpio (si algo se rompe)
uv tool uninstall raise-cli
uv tool install raise-cli
```
